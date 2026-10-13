#!/usr/bin/env python
"""Mapping-sensitivity analysis (final_audit_20261001, Phase 2).

Compares the budget-neutral alternative partition B' = (2,1,1) L-LLH rows
(results/holdout_exact_layer_llh_mapB211_76) against the existing panel rows
(G-FL, G-LLH, L-LLH under the frozen partition C=(1,1,2)) on the 76-object
Exact holdout. Benefit-oriented deltas (positive = left condition better;
LPIPS/ΔE00/GT-texture lower-better), 10k object-level percentile bootstrap,
seed 20260928 (the panel's seed). Frozen in MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL.md §5.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/4T/CXY/MV-Painter")

PANEL = Path("/4T/CXY/MV-Painter/final/round2/mv_adapter")
CONDITIONS = {
    "G-FL": ("results/holdout_exact_76/per_object_metrics.csv", "fixed_low"),
    "G-LLH": ("results/holdout_exact_equal_budget_76/per_object_metrics.csv", "LLH"),
    "L-LLH(C)": ("results/holdout_exact_layer_llh_76/per_object_metrics.csv", "L-LLH"),
    "L-LLH(B')": ("results/holdout_exact_layer_llh_mapB211_76/per_object_metrics.csv", "L-LLH"),
}
LOWER_BETTER = {"fg_lpips", "ciede2000", "gt_relative_texture_error"}
BOOT_SEED = 20260928
BOOT_N = 10000


def load(path, schedule):
    with path.open(newline="") as handle:
        return {r["object"]: {k: float(v) for k, v in r.items()
                              if k not in ("object", "geometry_source", "schedule")}
                for r in csv.DictReader(handle) if r["schedule"] == schedule}


def main() -> None:
    data = {}
    for name, (rel, sched) in CONDITIONS.items():
        with (PANEL / rel).open(newline="") as handle:
            data[name] = {r["object"]: {k: float(v) for k, v in r.items()
                                        if k not in ("object", "geometry_source", "schedule")}
                          for r in csv.DictReader(handle) if r["schedule"] == sched}

    objects = sorted(set(data["L-LLH(B')"]) & set(data["G-FL"]) & set(data["L-LLH(C)"]))
    metrics = [m for m in data["G-FL"][objects[0]]]
    comparisons = []
    for left, right in (("L-LLH(B')", "G-FL"), ("L-LLH(B')", "G-LLH"), ("L-LLH(B')", "L-LLH(C)")):
        for metric in metrics:
            a = np.array([data[left][o][metric] for o in objects])
            b = np.array([data[right][o][metric] for o in objects])
            delta = (a - b) if metric not in LOWER_BETTER else (b - a)
            rng = np.random.default_rng(BOOT_SEED)
            idx = rng.integers(0, len(delta), size=(BOOT_N, len(delta)))
            means = delta[idx].mean(axis=1)
            lo, hi = float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))
            comparisons.append({
                "comparison": f"{left} minus {right}",
                "metric": metric,
                "mean_delta": float(delta.mean()),
                "ci95": [lo, hi],
                "ci_excludes_zero": bool(lo > 0 or hi < 0),
                "win_rate_left": f"{int((delta > 0).sum())}/{len(delta)}",
                "direction": "positive_favors_left",
            })
    out = {"protocol": "MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL",
           "n_objects": len(objects), "bootstrap": {"resamples": BOOT_N, "seed": BOOT_SEED},
           "comparisons": comparisons}
    dest = PANEL / "MVADAPTER_MAPPING_SENSITIVITY_BOOTSTRAP.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for c in comparisons:
        star = "*" if c["ci_excludes_zero"] else " "
        print(f"{c['comparison']:>24} {c['metric']:>26} {c['mean_delta']:+.5f}{star} "
              f"[{c['ci95'][0]:+.5f},{c['ci95'][1]:+.5f}] {c['win_rate_left']}")
    print(f"n_objects={len(objects)} -> {dest}")


if __name__ == "__main__":
    main()
