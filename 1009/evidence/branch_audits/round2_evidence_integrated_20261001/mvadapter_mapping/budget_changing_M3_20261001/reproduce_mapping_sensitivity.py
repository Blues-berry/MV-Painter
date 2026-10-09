#!/usr/bin/env python
"""M3 mapping-sensitivity reanalysis.

Compares the frozen M1 layer-wise rows (existing) against the M3 variant
rows (new) against the SAME unchanged global rows, on the 76-object
MV-Adapter holdout. Benefit-oriented transform identical to
analyze_layerwise_panel_20260930.py (positive favors the LEFT/first
condition; LOWER_BETTER metrics sign-reversed). 10k percentile bootstrap,
seed 20260930. The source protocol calls M3 pre-registered, but its protocol
and result files first appear in the same Git commit; treat the test as
retrospective because chronology is not independently verifiable.

Labels per (comparison, metric):
  MAPPING_STABLE      same sign and same CI-excludes-zero status in M1 and M3
  MAPPING_ATTENUATED  same sign, CI status differs
  MAPPING_SENSITIVE   sign flip between mappings
"""

from __future__ import annotations

import csv
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_INPUTS = HERE.parent / "shared_inputs"

M1 = {
    "L-LLH": "M1_L-LLH_76_per_object_metrics.csv",
    "L-LHL": "M1_L-LHL_76_per_object_metrics.csv",
    "L-FIX": "M1_L-FIX_76_per_object_metrics.csv",
}
M3 = {
    "L-LLH": "M3_L-LLH_76_per_object_metrics.csv",
    "L-LHL": "M3_L-LHL_76_per_object_metrics.csv",
    "L-FIX": "M3_L-FIX_76_per_object_metrics.csv",
}
GLOBAL = {
    "G-FL": "G-FL_76_per_object_metrics.csv",
    "G-LLH": "G-LLH_76_per_object_metrics.csv",
    "G-LHL": "G-LHL_76_per_object_metrics.csv",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    inputs = args.inputs.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    globals_data = {}
    for g in GLOBAL:
        globals_data[g] = load(inputs / GLOBAL[g], GLOBAL_LABEL[g])

    results = {}
    rows = []
    for comp_id, left, right in COMPARISONS:
        for mapping, sources in (("M1", M1), ("M3", M3)):
            ldata = load(inputs / sources[left], {"L-LLH": "L-LLH", "L-LHL": "L-LHL", "L-FIX": "L-FIX"}[left])
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

    (output_dir / "MAPPING_SENSITIVITY_BOOTSTRAP.json").write_text(json.dumps({
        "protocol": "mv-adapter-mapping-sensitivity-v1",
        "transform": "benefit-oriented: positive favors the left/first condition; lower-is-better metrics sign-reversed",
        "bootstrap": {"seed": BOOT_SEED, "resamples": BOOT_N, "unit": "object"},
        "results": results,
        "labels_summary": {
            k: sum(1 for v in labels.values() if v == k)
            for k in ("MAPPING_SENSITIVE", "MAPPING_STABLE", "MAPPING_ATTENUATED")
            if k in labels.values()
        },
    }, indent=2) + "\n")

    with (output_dir / "MAPPING_SENSITIVITY_COMPARISONS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    for k, v in labels.items():
        m1 = results[k]["M1"]
        m3 = results[k]["M3"]
        print(f"{k:44s} M1 {m1['mean_delta']:+8.4f} M3 {m3['mean_delta']:+8.4f}  {v}")
    print()
    print("labels summary:", {
        k: sum(1 for v in labels.values() if v == k)
        for k in ("MAPPING_SENSITIVE", "MAPPING_STABLE", "MAPPING_ATTENUATED")
        if k in labels.values()
    })


if __name__ == "__main__":
    main()
