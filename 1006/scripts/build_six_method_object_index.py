#!/usr/bin/env python3
"""Build a complete, descriptive per-object metric/rank index for six strategies."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
OUT = ROOT / "1006/figures/strategy_comparison_gallery/fresh_c_final"
METHODS = (
    ("native_gfl", "GFL", DATA / "runs/c3_confirmation/per_object_metrics.csv"),
    ("native_gfh", "GFH", DATA / "runs/c3_confirmation/per_object_metrics.csv"),
    ("no_adapter", "No adapter", DATA / "runs/c3_confirmation/per_object_metrics.csv"),
    ("native_gc3", "C3", DATA / "runs/c3_confirmation/per_object_metrics.csv"),
    ("layer_llh", "LLH", DATA / "runs/revision_era_addendum/per_object_metrics.csv"),
    ("gen_linear", "Generic linear", DATA / "runs/revision_era_addendum/per_object_metrics.csv"),
)
METRICS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")
HIGHER = {"fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_conditions(path: Path) -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            result.setdefault(row["condition"], {})[row["object_uid"]] = row
    return result


def main() -> None:
    for gate_name in ("FRESH_C_INTEGRITY_GATE.json", "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"):
        gate = DATA / gate_name
        if not gate.is_file() or json.loads(gate.read_text()).get("status") != "PASS":
            raise RuntimeError(f"refusing to build six-method index before PASS gate: {gate}")
    uids = [line.strip() for line in (DATA / "fresh_c_objects.txt").read_text().splitlines() if line.strip()]
    tables_by_path: dict[Path, dict[str, dict[str, dict[str, str]]]] = {}
    rows_by_method: dict[str, dict[str, dict[str, str]]] = {}
    labels = {}
    for condition, label, path in METHODS:
        if path not in tables_by_path:
            tables_by_path[path] = read_conditions(path)
        table = tables_by_path[path]
        if condition not in table or set(table[condition]) != set(uids):
            raise RuntimeError(f"condition/UID coverage mismatch for {condition}")
        rows_by_method[condition] = table[condition]
        labels[condition] = label

    result_rows: list[dict[str, Any]] = []
    # Ranks are computed independently within each object and metric, never across metrics.
    for object_index, uid in enumerate(uids):
        metric_ranks: dict[str, dict[str, int]] = {}
        for metric in METRICS:
            ordered = sorted(
                (condition for condition, _, _ in METHODS),
                key=lambda condition: (
                    -float(rows_by_method[condition][uid][metric]) if metric in HIGHER
                    else float(rows_by_method[condition][uid][metric]),
                    condition,
                ),
            )
            metric_ranks[metric] = {condition: rank for rank, condition in enumerate(ordered, start=1)}
        for condition, label, _ in METHODS:
            row: dict[str, Any] = {
                "object_index": object_index,
                "object_uid": uid,
                "cohort": "FROZEN_FRESH_C_300",
                "cohort_n": len(uids),
                "condition": condition,
                "method_label": label,
                "rank_scope": "descriptive rank among six methods within this UID and metric; no significance or cross-metric score",
            }
            for metric in METRICS:
                row[metric] = float(rows_by_method[condition][uid][metric])
                row[f"rank_{metric}"] = metric_ranks[metric][condition]
            result_rows.append(row)

    out_path = OUT / "six_method_complete_object_index.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(result_rows)
    report = {
        "status": "PASS",
        "cohort": "FROZEN_FRESH_C_300",
        "n_objects": len(uids),
        "methods": [condition for condition, _, _ in METHODS],
        "rows": len(result_rows),
        "metrics": list(METRICS),
        "ranking_rule": "per-object, per-metric ranking across six method outputs; PSNR/SSIM higher is better, LPIPS lower is better; metrics are not combined",
        "input_csv_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in tables_by_path},
        "output_csv": str(out_path.relative_to(ROOT)),
        "output_sha256": sha256(out_path),
    }
    (OUT / "six_method_complete_object_index.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
