"""Compare texture-proxy distance to the per-object GT values."""

import csv
import json
from pathlib import Path

import numpy as np


TMP = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule")
ROOT = Path("/4T/CXY/MV-Painter")
LAYER = TMP / "layer_official_v2_merged/per_object_metrics.csv"
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
STAGE = ROOT / "final/round2/stage_placement_276_20260929"
PAIRS = {
    "fixed_low": BASE / "per_object_fixed_low.csv",
    "c3": BASE / "per_object_c3.csv",
    "fixed_high": BASE / "per_object_fixed_high.csv",
    "fixed_mean": STAGE / "per_object_fixed_mean.csv",
    "c3_lhl": STAGE / "per_object_c3_lhl.csv",
    "llh": STAGE / "per_object_llh.csv",
    "hll": STAGE / "per_object_hll.csv",
}
TEXTURE = {
    "fg_rgb_std": "gt_fg_rgb_std",
    "fg_grad_mag": "gt_fg_grad_mag",
    "fg_lap_var": "gt_fg_lap_var",
    "fg_hf_energy": "gt_fg_hf_energy",
}


def read(path):
    with path.open(newline="") as f:
        return {r["object"]: r for r in csv.DictReader(f)}


def val(row, key):
    return float(row[key])


def boot(delta, seed):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(delta), size=(10000, len(delta)))
    means = delta[idx].mean(1)
    return [float(np.quantile(means, q)) for q in (0.025, 0.975)]


def main():
    layer = read(LAYER)
    result = {}
    objects = sorted(layer)
    for name, path in PAIRS.items():
        other = read(path)
        metrics = {}
        for pred, gt in TEXTURE.items():
            le = np.asarray([abs(val(layer[o], pred) - val(layer[o], gt)) for o in objects])
            be = np.asarray([abs(val(other[o], pred) - val(other[o], gt)) for o in objects])
            delta = le - be
            metrics[pred] = {
                "layer_error_mean": float(le.mean()),
                "baseline_error_mean": float(be.mean()),
                "delta_layer_minus_baseline": float(delta.mean()),
                "delta_ci95": boot(delta, 20260929),
                "layer_better_rate": float((delta < 0).mean()),
            }
        result[name] = metrics
    path = TMP / "layer_official_v2_merged/texture_error_comparisons.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    for name, metrics in result.items():
        print(name)
        for metric, item in metrics.items():
            print(metric, "layer", round(item["layer_error_mean"], 6), "base", round(item["baseline_error_mean"], 6), "delta", round(item["delta_layer_minus_baseline"], 6), "ci", [round(x, 6) for x in item["delta_ci95"]], "better", round(item["layer_better_rate"], 3))


if __name__ == "__main__":
    main()
