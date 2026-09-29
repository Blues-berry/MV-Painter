"""Compare raw-PNG recheck metrics with the original float-eval CSVs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "final/round2/main_adapter_clean_v2/raw_metric_audit/raw_metric_recheck_300.csv"
EVAL = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
OUT = ROOT / "final/round2/main_adapter_clean_v2/raw_metric_audit"
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
METRICS = ("full_psnr", "fg_psnr", "full_ssim", "fg_ssim", "edge_ssim", "full_lpips", "fg_lpips")
THRESHOLDS = {"full_psnr": 0.05, "fg_psnr": 0.05, "full_ssim": 0.01, "fg_ssim": 0.01, "edge_ssim": 0.01, "full_lpips": 1e-7, "fg_lpips": 1e-7}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def main() -> None:
    raw = read(RAW)
    all_rows = []
    summary = {"provenance": {"raw": "recomputed_from_raw_png_rgba_and_depth", "lpips": "REUSED_ORIGINAL_EVAL"}, "methods": {}}
    for method in METHODS:
        original_rows = read(EVAL / f"per_object_{method}.csv")
        original = {r["object"]: r for r in original_rows}
        for rr in [r for r in raw if r["method"] == method]:
            obj, uid = rr["object"], rr.get("uid", "")
            if obj not in original:
                continue
            row = {"object": obj, "uid": uid, "method": method}
            for metric in METRICS:
                row[f"raw_{metric}"] = float(rr[metric])
                row[f"original_{metric}"] = float(original[obj][metric])
                row[f"delta_{metric}"] = float(rr[metric]) - float(original[obj][metric])
            all_rows.append(row)
        method_rows = [r for r in all_rows if r["method"] == method]
        summary["methods"][method] = {}
        for metric in METRICS:
            values = np.asarray([r[f"delta_{metric}"] for r in method_rows])
            summary["methods"][method][metric] = {
                "mean_delta": float(values.mean()),
                "mean_abs_delta": float(np.abs(values).mean()),
                "p95_abs_delta": float(np.quantile(np.abs(values), 0.95)),
                "max_abs_delta": float(np.abs(values).max()),
                "threshold": THRESHOLDS[metric],
                "anomaly_objects": [r["object"] for r in method_rows if abs(r[f"delta_{metric}"]) > THRESHOLDS[metric]],
            }
    fields = list(all_rows[0])
    with (OUT / "raw_vs_historical_comparison.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(all_rows)
    (OUT / "raw_vs_historical_error_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({m: {k: v["mean_abs_delta"] for k, v in x.items()} for m, x in summary["methods"].items()}, indent=2))


if __name__ == "__main__":
    main()
