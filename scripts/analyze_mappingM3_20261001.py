#!/usr/bin/env python
"""M3 mapping-sensitivity analysis (pre-registered in MAPPING_SENSITIVITY_PROTOCOL.md).

Compares the frozen M1 layer-wise rows (existing) against the M3 variant
rows (new) against the SAME unchanged global rows, on the 76-object
MV-Adapter holdout. Benefit-oriented transform identical to
analyze_layerwise_panel_20260930.py (positive favors the LEFT/first
condition; LOWER_BETTER metrics sign-reversed). 10k percentile bootstrap,
seed 20260930.

Labels per (comparison, metric):
  MAPPING_STABLE      same sign and same CI-excludes-zero status in M1 and M3
  MAPPING_ATTENUATED  same sign, CI status differs
  MAPPING_SENSITIVE   sign flip between mappings
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
MV = ROOT / "final/round2/mv_adapter/results"
OUT = ROOT / "final/round2/coordination/core7_same_runner_completion_20261001"

M1 = {
    "L-LLH": MV / "holdout_exact_layer_llh_76/per_object_metrics.csv",
    "L-LHL": MV / "holdout_exact_layer_lhl_76/per_object_metrics.csv",
    "L-FIX": MV / "holdout_exact_layer_fixed_76/per_object_metrics.csv",
}
M3 = {
    "L-LLH": MV / "holdout_exact_mapM3_llh_76/per_object_metrics.csv",
    "L-LHL": MV / "holdout_exact_mapM3_lhl_76/per_object_metrics.csv",
    "L-FIX": MV / "holdout_exact_mapM3_fix_76/per_object_metrics.csv",
}
GLOBAL = {
    "G-FL": MV / "holdout_exact_76/per_object_metrics.csv",
    "G-LLH": MV / "holdout_exact_equal_budget_76/per_object_metrics.csv",
    "G-LHL": MV / "holdout_exact_lhl_shape_transfer_76/per_object_metrics.csv",
}
GLOBAL_LABEL = {"G-FL": "fixed_low", "G-LLH": "LLH", "G-LHL": "LHL"}

COMPARISONS = [
    ("P1", "L-LLH", "G-FL"),
    ("P2", "L-LLH", "G-LLH"),
    ("P4", "L-LHL", "G-LHL"),
]
METRICS = ["psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000", "gt_relative_texture_error"]
LOWER_BETTER = {"fg_lpips", "ciede2000", "gt_relative_texture_error"}
BOOT_SEED = 20260930
BOOT_N = 10_000


def load(path: Path, schedule: str) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}
    out = {}
    with path.open(newline="") as handle:
        for r in csv.DictReader(handle):
            if r["schedule"] == schedule:
                out[r["object"]] = {k: float(v) for k, v in r.items()
                                    if k not in {"object", "geometry_source", "schedule"}}
    return out


def paired_boot(delta: np.ndarray) -> dict:
    rng = np.random.default_rng(BOOT_SEED)
    n = len(delta)
    boot = delta[rng.integers(0, n, size=(BOOT_N, n))].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"n": int(n), "mean_delta": float(delta.mean()),
            "ci95_low": float(lo), "ci95_high": float(hi),
            "ci_excludes_zero": bool(lo > 0 or hi < 0)}


def main() -> None:
    globals_data = {}
    for g in GLOBAL:
        globals_data[g] = load(GLOBAL[g], GLOBAL_LABEL[g])

    results = {}
    rows = []
    for comp_id, left, right in COMPARISONS:
        for mapping, sources in (("M1", M1), ("M3", M3)):
            ldata = load(sources[left], {"L-LLH": "L-LLH", "L-LHL": "L-LHL", "L-FIX": "L-FIX"}[left])
            rdata = globals_data[right]
            common = sorted(set(ldata) & set(rdata))
            for metric in METRICS:
                deltas = np.array([
                    (ldata[o][metric] - rdata[o][metric]) if metric not in LOWER_BETTER
                    else (rdata[o][metric] - ldata[o][metric])
                    for o in common
                ])
                stats = paired_boot(deltas)
                key = f"{comp_id}_{left}_vs_{right}/{metric}"
                results.setdefault(key, {})[mapping] = stats
                rows.append({"comparison": f"{left} - {right}", "mapping": mapping,
                             "metric": metric, "direction": "positive favors left",
                             **stats})

    labels = {}
    for key, per_map in results.items():
        if "M1" not in per_map or "M3" not in per_map:
            labels[key] = "INCOMPLETE (M3 rows missing)"
            continue
        s1 = np.sign(per_map["M1"]["mean_delta"])
        s3 = np.sign(per_map["M3"]["mean_delta"])
        if s1 != s3:
            labels[key] = "MAPPING_SENSITIVE"
        elif per_map["M1"]["ci_excludes_zero"] == per_map["M3"]["ci_excludes_zero"]:
            labels[key] = "MAPPING_STABLE"
        else:
            labels[key] = "MAPPING_ATTENUATED"
        results[key]["label"] = labels[key]

    (OUT / "MAPPING_SENSITIVITY_BOOTSTRAP.json").write_text(json.dumps({
        "protocol": "mv-adapter-mapping-sensitivity-v1",
        "transform": "benefit-oriented: positive favors the left/first condition; lower-is-better metrics sign-reversed",
        "bootstrap": {"seed": BOOT_SEED, "resamples": BOOT_N, "unit": "object"},
        "results": results,
        "labels_summary": {k: sum(1 for v in labels.values() if v == k) for k in set(labels.values())},
    }, indent=2) + "\n")

    with (OUT / "MAPPING_SENSITIVITY_COMPARISONS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    for k, v in labels.items():
        m1 = results[k]["M1"]
        m3 = results[k]["M3"]
        print(f"{k:44s} M1 {m1['mean_delta']:+8.4f} M3 {m3['mean_delta']:+8.4f}  {v}")
    print()
    print("labels summary:", {k: sum(1 for v in labels.values() if v == k) for k in set(labels.values())})


if __name__ == "__main__":
    main()
