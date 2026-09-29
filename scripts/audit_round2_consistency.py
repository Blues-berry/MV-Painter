#!/usr/bin/env python3
"""Read-only protocol audit for the round-2 evidence package.

This deliberately audits source/manifests rather than rerunning the model.  It
reports what is proven by the frozen artifacts and flags control dimensions
that require a new deterministic pilot.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def check(label: str, ok: bool, detail: str) -> dict[str, object]:
    return {"label": label, "status": "PASS" if ok else "CHECK", "detail": detail}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root

    manifest = root / "final/round2/clean_dataset_v2/dataset_manifest.json"
    freeze = root / "final/round2/main_adapter_clean_v2/clean_v2_freeze_manifest.json"
    holdout = root / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
    csv_path = root / "final/round2/main_adapter_clean_v2/main_adapter_clean_v2_strict276.csv"
    main_eval = root / "geotex/round2_main_eval.py"
    stage_eval = root / "geotex/stage_placement_eval.py"

    m = json.loads(manifest.read_text())
    f = json.loads(freeze.read_text())
    ids = read_ids(holdout)
    csv_rows = list(csv.DictReader(csv_path.open(newline="")))
    main_src = main_eval.read_text()
    stage_src = stage_eval.read_text()

    results = [
        check("strict UID count", len(ids) == 276 and len(set(ids)) == 276, f"count={len(ids)}, unique={len(set(ids))}"),
        check("strict UID hash", sha256(holdout) == m["strict_holdout_sha256"], f"actual={sha256(holdout)}"),
        check("dataset view mode", m.get("target_view_mode") == "unique6", f"mode={m.get('target_view_mode')}, views={m.get('target_views')}"),
        check("CSV summary rows", {r["condition"] for r in csv_rows} >= {"no_adapter", "fixed_low", "fixed_high", "c3"}, f"conditions={[r['condition'] for r in csv_rows]}"),
        check("formal main entrypoint declares unique6", 'target_view_mode = "unique6"' in main_src or 'target_view_mode="unique6"' in main_src, "source-level check"),
        check("formal stage entrypoint declares unique6", 'target_view_mode": "unique6"' in stage_src or 'target_view_mode = "unique6"' in stage_src, "source-level check"),
        check("shared initial latent is represented", "shared_initial_latent" in (root / "final/round2/main_adapter_clean_v2/float_png_trace_12_controlled_20260929/float_png_serialization_manifest.json").read_text(), "controlled trace manifest"),
        check("float32 metric policy", "float32" in (root / "final/round2/main_adapter_clean_v2/float_png_trace_12_controlled_20260929/FIXED_GT_SSIM_DECOMPOSITION.md").read_text(), "fixed-GT decomposition record"),
        check("Python RNG control", bool(re.search(r"random\.seed", main_src)), "formal entrypoint source scan; absent means rerun must fix it"),
        check("NumPy RNG control", bool(re.search(r"np\.random\.seed|numpy\.random\.seed", main_src)), "formal entrypoint source scan; absent means rerun must fix it"),
        check("checkpoint identity", f["checkpoint"]["sha256"] == "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0", "clean-v2 freeze manifest"),
    ]
    payload = {
        "protocol": "round2-consistency-audit-v1",
        "status": "read_only",
        "manifest": str(manifest),
        "freeze_manifest": str(freeze),
        "checks": results,
        "interpretation": "PASS means the saved protocol/artifact is explicit; CHECK requires either source review or a deterministic rerun before a new claim.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Round-2 consistency audit")
        for item in results:
            print(f"[{item['status']}] {item['label']}: {item['detail']}")
        print("\nInterpretation: PASS means explicit saved evidence; CHECK requires a deterministic rerun or source review.")


if __name__ == "__main__":
    main()
