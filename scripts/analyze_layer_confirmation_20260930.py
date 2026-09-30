#!/usr/bin/env python
"""Analyze the strict-276 same-runner confirmation set (layer_llh, layer_fixed_mean, layer_lhl).

Paired object-level 95% percentile bootstrap (10,000 resamples, seed 20260930),
object win rates, and the seven pre-save metrics. Also compares the same-runner
layer-LHL replica against the archived official record (rank correlation only;
absolute values are not pooled across runners).
"""

from __future__ import annotations

import csv
import json
import random
import statistics
import sys
from pathlib import Path

OUT = Path("/4T/tmp/mvpainter-layer-confirmation-20260930")
ARCHIVED_LHL = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/per_object_metrics.csv")
METRICS = ["full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim"]
BETTER = {  # direction
    "full_psnr": +1, "full_ssim": +1, "full_lpips": -1,
    "fg_psnr": +1, "fg_ssim": +1, "fg_lpips": -1, "edge_ssim": +1,
}
BOOT_SEED = 20260930
BOOT_N = 10000


def load_schedule(name: str) -> dict[tuple, dict]:
    rows = json.loads((OUT / f"{name}_rows.json").read_text())
    return {(int(r["object_idx"])): r for r in rows}


def paired(a: dict, b: dict, metric: str) -> dict:
    keys = sorted(set(a) & set(b))
    sign = BETTER[metric]
    diffs = [sign * (a[k][metric] - b[k][metric]) for k in keys]
    rng = random.Random(BOOT_SEED)
    n = len(diffs)
    boots = sorted(sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(BOOT_N))
    wins = sum(1 for d in diffs if d > 0)
    return {
        "metric": metric,
        "mean_diff": sum(diffs) / n,
        "ci95": [boots[250], boots[9750]],
        "win_rate": f"{wins}/{n}",
        "n": n,
    }


def main() -> None:
    schedules = {name: load_schedule(name) for name in ("layer_llh", "layer_fixed_mean", "layer_lhl")}
    summary = {"protocol": "layer-confirmation-strict276-v1", "n_objects": {k: len(v) for k, v in schedules.items()}}

    means = {}
    for name, rows in schedules.items():
        means[name] = {m: statistics.mean(r[m] for r in rows.values()) for m in METRICS}
    summary["means"] = means

    comparisons = {}
    for a, b in (("layer_llh", "layer_lhl"), ("layer_fixed_mean", "layer_lhl"), ("layer_llh", "layer_fixed_mean")):
        comparisons[f"{a}_minus_{b}"] = {m: paired(schedules[a], schedules[b], m) for m in METRICS}
    summary["paired_comparisons"] = comparisons

    # Cross-runner check: same-runner LHL replica vs archived official record (rank correlation on fg_lpips/fg_psnr).
    archived = {}
    with ARCHIVED_LHL.open() as handle:
        for row in csv.DictReader(handle):
            archived[int(row["object_idx"])] = row  # both CSVs index 0..275 (object = obj_{idx+24:04d})
    common = sorted(set(archived) & set(schedules["layer_lhl"]))
    rep = [float(schedules["layer_lhl"][k]["fg_psnr"]) for k in common]
    arc = [float(archived[k]["fg_psnr"]) for k in common]
    mean_rep, mean_arc = statistics.mean(rep), statistics.mean(arc)
    cov = sum((x - mean_rep) * (y - mean_arc) for x, y in zip(rep, arc))
    var_rep = sum((x - mean_rep) ** 2 for x in rep)
    var_arc = sum((y - mean_arc) ** 2 for y in arc)
    summary["cross_runner_lhl_check"] = {
        "note": "archived official record used unseeded Python RNG (reference augmentation differs per process); rank-level agreement only",
        "n_common": len(common),
        "pearson_fg_psnr": cov / (var_rep ** 0.5 * var_arc ** 0.5),
        "mean_fg_psnr_replica": mean_rep,
        "mean_fg_psnr_archived": mean_arc,
    }

    (OUT / "confirmation_analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["means"], indent=1))
    for name, comps in comparisons.items():
        print(f"\n== {name} ==")
        for m in ("fg_lpips", "fg_psnr", "full_psnr", "edge_ssim"):
            c = comps[m]
            print(f"  {m}: {c['mean_diff']:+.5f} CI[{c['ci95'][0]:+.5f},{c['ci95'][1]:+.5f}] wins {c['win_rate']}")
    print("\ncross-runner LHL check:", json.dumps(summary["cross_runner_lhl_check"], indent=1))


if __name__ == "__main__":
    main()
