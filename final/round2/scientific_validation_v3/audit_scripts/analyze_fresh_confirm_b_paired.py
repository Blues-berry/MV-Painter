#!/usr/bin/env python3
"""Analyze one locked paired comparison from FRESH_CONFIRM_B.

Uses the campaign's pre-existing paired bootstrap implementation
(`analyze_v3.paired_bootstrap`) with its frozen 10,000 resamples and seed
20261002. The favorable-object rate is corrected for lower-is-better metrics.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
sys.path.insert(0, str(V3))
import analyze_v3  # noqa: E402


def read_condition(path: Path, condition: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["condition"] == condition:
                uid = row["object_uid"]
                if uid in rows:
                    raise ValueError(f"duplicate object-condition row: {uid}/{condition}")
                rows[uid] = row
    return rows


def summarize(deltas: np.ndarray, metric: str) -> dict:
    result = analyze_v3.paired_bootstrap(deltas)
    favorable = deltas > 0 if metric == "fg_psnr" else deltas < 0
    result["favorable_rate"] = float(np.mean(favorable))
    result["ties_rate"] = float(np.mean(deltas == 0))
    result["favorable_direction"] = "higher" if metric == "fg_psnr" else "lower"
    result["p_method"] = "two-sided paired-bootstrap sign-crossing test; 10,000 draws; minimum reported p=1/10,000"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", required=True, help="Condition A; effect is A minus B")
    parser.add_argument("--b", required=True)
    parser.add_argument("--metrics", default="fg_psnr,fg_lpips")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    table = RUN / "per_object_metrics.csv"
    left, right = read_condition(table, args.a), read_condition(table, args.b)
    if len(left) != 150 or len(right) != 150 or set(left) != set(right):
        raise SystemExit(f"paired coverage failure: {args.a}={len(left)}, {args.b}={len(right)}")

    result = {
        "cohort": "FRESH_CONFIRM_B",
        "n_objects": len(left),
        "contrast": f"{args.a} - {args.b}",
        "delta_convention": "condition A minus condition B",
        "bootstrap_draws": analyze_v3.BOOT_N,
        "bootstrap_seed": analyze_v3.BOOT_SEED,
        "tests": {},
    }
    for metric in args.metrics.split(","):
        if metric not in {"fg_psnr", "fg_lpips"}:
            raise ValueError(f"unsupported metric for this locked contrast: {metric}")
        delta = np.asarray([float(left[uid][metric]) - float(right[uid][metric])
                            for uid in sorted(left)], dtype=np.float64)
        result["tests"][metric] = summarize(delta, metric)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
