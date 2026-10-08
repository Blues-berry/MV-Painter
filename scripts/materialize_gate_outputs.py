#!/usr/bin/env python
"""Copy feature-gate predictions into the durable raw RGB comparison set."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
METHODS = ["c3_feature_gate", "linear_feature_gate"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    freeze = json.loads((ARTIFACT / "SAMPLE_FREEZE.json").read_text())
    manifest_path = ARTIFACT / "logs/RAW_RGB_ASSET_SHA256.csv"
    with manifest_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = rows[0].keys()
    existing = {(r["uid"], r["method"]) for r in rows}
    added = []
    for sample in freeze["samples"]:
        for method in METHODS:
            if (sample["uid"], method) in existing:
                continue
            source = ARTIFACT / "runs/feature_ratio_gate/predictions" / method / f"{sample['uid']}.png"
            image = Image.open(source)
            if image.mode != "RGB" or image.size != (512, 768):
                raise RuntimeError(f"expected unmodified 512x768 RGB grid, got {image.mode} {image.size}: {source}")
            target = ARTIFACT / "raw_rgb" / sample["sample_id"] / f"{method}.png"
            shutil.copy2(source, target)
            source_hash, target_hash = sha256(source), sha256(target)
            if source_hash != target_hash:
                raise RuntimeError(f"copy hash mismatch: {source}")
            added.append({
                "sample_id": sample["sample_id"], "uid": sample["uid"], "kind": "prediction",
                "method": method, "source_path": str(source), "source_sha256": source_hash,
                "output_path": str(target), "output_sha256": target_hash,
                "source_action": "feature_ratio_gate_locked_stage2_run; byte-preserved",
            })
    with manifest_path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writerows(added)
    summary_path = ARTIFACT / "logs/RAW_RGB_ASSET_SUMMARY.json"
    summary = json.loads(summary_path.read_text())
    summary["method_count"] = 8
    summary["asset_count"] = len(rows) + len(added)
    summary["prediction_actions"]["stage2_gate"] = (
        "C3 and Generic Linear feature-gate predictions; paired with the locked 26-object inputs"
    )
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"copied {len(added)} gated RGB grids; manifest now has {len(rows) + len(added)} rows")


if __name__ == "__main__":
    main()
