#!/usr/bin/env python
"""Robustness-1 analysis: paired bootstrap + R0-vs-R1 stability (task items 8-9).

Inputs (frozen):
- Realization-0 same-runner rows: /4T/tmp/mvpainter-layer-confirmation-20260930/
  {global_fixed_low, layer_llh, layer_fixed_mean, layer_lhl}_rows.json
- Realization-0 global_c3 completion (pre-registered matrix completion):
  <task>/r0_completion_global_c3/rows.json
- Realization-1 Core-5 rows: <task>/realization1_core5/rows.json

Conventions identical to the frozen analyze_layer_confirmation_20260930.py:
paired object-level 95% percentile bootstrap, 10,000 resamples, seed
20260930 (fresh Random per comparison x metric x realization), object as
sampling unit. The two realizations are never pooled.

Outputs (in <task>/): paired_bootstrap.json, aggregate_metrics.csv,
R0_R1_DIRECTION_STABILITY.csv, R0_R1_STABILITY_SUMMARY.json.
"""

from __future__ import annotations

import csv
import json
import random
import statistics
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
TASK = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
R0_DIR = Path("/4T/tmp/mvpainter-layer-confirmation-20260930")
R0_C3 = TASK / "r0_completion_global_c3/rows.json"
R1_ROWS = TASK / "realization1_core5/rows.json"

METRICS = ["fg_psnr", "fg_ssim", "fg_lpips", "full_psnr", "full_ssim", "full_lpips", "edge_ssim"]
BETTER = {
    "fg_psnr": +1, "fg_ssim": +1, "fg_lpips": -1,
    "full_psnr": +1, "full_ssim": +1, "full_lpips": -1, "edge_ssim": +1,
}
COMPARISONS = [
    ("layer_llh", "global_fixed_low"),   # primary gate
    ("layer_llh", "global_c3"),
    ("layer_llh", "layer_fixed_mean"),
    ("layer_llh", "layer_lhl"),
]
METHODS = ["global_fixed_low", "global_c3", "layer_fixed_mean", "layer_lhl", "layer_llh"]
BOOT_SEED = 20260930
BOOT_N = 10000


def load_rows(path: Path) -> dict[int, dict]:
    rows = json.loads(path.read_text())
    return {int(r["object_idx"]): r for r in rows}


def paired(a: dict[int, dict], b: dict[int, dict], metric: str) -> dict:
    keys = sorted(set(a) & set(b))
    sign = BETTER[metric]
    diffs = [sign * (float(a[k][metric]) - float(b[k][metric])) for k in keys]
    n = len(diffs)
    if n != 276:
        raise RuntimeError(f"expected 276 paired objects, got {n} ({metric})")
    rng = random.Random(BOOT_SEED)
    boots = sorted(sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(BOOT_N))
    wins = sum(1 for d in diffs if d > 0)
    losses = sum(1 for d in diffs if d < 0)
    return {
        "metric": metric,
        "mean_diff": sum(diffs) / n,
        "median_diff": statistics.median(diffs),
        "ci95": [boots[250], boots[9750]],
        "win_rate": f"{wins}/{n}",
        "losses": f"{losses}/{n}",
        "ties": n - wins - losses,
        "n": n,
        "ci_excludes_zero": bool(boots[250] > 0 or boots[9750] < 0),
    }


def classify(r0: dict, r1: dict) -> str:
    same_sign = (r0["mean_diff"] > 0) == (r1["mean_diff"] > 0)
    if not same_sign:
        return "UNSTABLE"
    if r0["ci_excludes_zero"] and r1["ci_excludes_zero"]:
        return "STABLE_STRONG"
    return "STABLE_DIRECTIONAL"


def main() -> None:
    r0 = {}
    for name in ("global_fixed_low", "layer_llh", "layer_fixed_mean", "layer_lhl"):
        r0[name] = load_rows(R0_DIR / f"{name}_rows.json")
    if R0_C3.exists():
        r0["global_c3"] = load_rows(R0_C3)
    else:
        raise RuntimeError(f"missing R0 global_c3 completion rows: {R0_C3}")
    r1_all = json.loads(R1_ROWS.read_text())
    r1 = {}
    for name in METHODS:
        r1[name] = {int(r["object_idx"]): r for r in r1_all if r["schedule"] == name}
    for name in METHODS:
        if len(r1[name]) != 276 or len(r0[name]) != 276:
            raise RuntimeError(f"incomplete rows for {name}: r1={len(r1[name])} r0={len(r0[name])}")

    # paired bootstrap per realization
    paired_out: dict[str, dict] = {}
    for label, rows in (("R0", r0), ("R1", r1)):
        paired_out[label] = {}
        for a, b in COMPARISONS:
            paired_out[label][f"{a}_minus_{b}"] = {
                m: paired(rows[a], rows[b], m) for m in METRICS
            }
    (TASK / "paired_bootstrap.json").write_text(json.dumps(paired_out, indent=2) + "\n")

    # aggregate means
    agg_rows = []
    for label, rows in (("R0", r0), ("R1", r1)):
        for name in METHODS:
            for m in METRICS:
                agg_rows.append({
                    "realization": label, "method": name, "metric": m,
                    "mean": statistics.mean(float(rows[name][k][m]) for k in rows[name]),
                    "n": 276,
                })
    with (TASK / "aggregate_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["realization", "method", "metric", "mean", "n"])
        writer.writeheader()
        writer.writerows(agg_rows)

    # direction stability table
    stab_rows = []
    classifications = {}
    for a, b in COMPARISONS:
        comp = f"{a}_minus_{b}"
        classifications[comp] = {}
        for m in METRICS:
            p0 = paired_out["R0"][comp][m]
            p1 = paired_out["R1"][comp][m]
            label = classify(p0, p1)
            classifications[comp][m] = label
            stab_rows.append({
                "comparison": comp, "metric": m,
                "r0_mean_delta": round(p0["mean_diff"], 6),
                "r0_ci95": f"[{p0['ci95'][0]:.6f},{p0['ci95'][1]:.6f}]",
                "r0_win_rate": p0["win_rate"],
                "r1_mean_delta": round(p1["mean_diff"], 6),
                "r1_ci95": f"[{p1['ci95'][0]:.6f},{p1['ci95'][1]:.6f}]",
                "r1_win_rate": p1["win_rate"],
                "ci_excludes_zero_R0": p0["ci_excludes_zero"],
                "ci_excludes_zero_R1": p1["ci_excludes_zero"],
                "classification": label,
            })
    with (TASK / "R0_R1_DIRECTION_STABILITY.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stab_rows[0]))
        writer.writeheader()
        writer.writerows(stab_rows)

    # ranking sensitivity (means, best -> worst per metric direction)
    def ranking(rows: dict) -> dict:
        out = {}
        for m in METRICS:
            ordered = sorted(METHODS, key=lambda name: -BETTER[m] * statistics.mean(
                float(rows[name][k][m]) for k in rows[name]))
            out[m] = ordered
        return out

    rank_r0, rank_r1 = ranking(r0), ranking(r1)
    summary = {
        "protocol": "main-backbone Core-5 Robustness-1 (PROTOCOL_LOCK.md)",
        "bootstrap": f"{BOOT_N} resamples, seed {BOOT_SEED}, paired percentile CI, object-level",
        "n_objects": 276,
        "realizations": {
            "R0": "object_seed = 42 + idx (frozen official rows + pre-registered global_c3 completion)",
            "R1": "object_seed = 10042 + idx",
        },
        "paired_comparisons": paired_out,
        "classification": classifications,
        "classification_counts": {
            label: sum(1 for comp in classifications.values() for v in comp.values() if v == label)
            for label in ("STABLE_STRONG", "STABLE_DIRECTIONAL", "UNSTABLE")
        },
        "ranking_R0": rank_r0,
        "ranking_R1": rank_r1,
        "ranking_flags": {
            "llh_above_lhl_R0": rank_r0["fg_lpips"][0] == "layer_llh" or "layer_llh" == rank_r0["fg_psnr"][0],
            "llh_vs_lhl_both": {
                m: (rank_r0[m].index("layer_llh") < rank_r0[m].index("layer_lhl"),
                    rank_r1[m].index("layer_llh") < rank_r1[m].index("layer_lhl"))
                for m in METRICS
            },
            "llh_vs_gfl_both": {
                m: (rank_r0[m].index("layer_llh") < rank_r0[m].index("global_fixed_low"),
                    rank_r1[m].index("layer_llh") < rank_r1[m].index("global_fixed_low"))
                for m in METRICS
            },
            "midrank_flips": {
                m: [pair for pair in (("global_fixed_low", "global_c3"), ("global_c3", "layer_fixed_mean"),
                                      ("global_fixed_low", "layer_fixed_mean"), ("layer_fixed_mean", "layer_lhl"))
                    if (rank_r0[m].index(pair[0]) < rank_r0[m].index(pair[1]))
                    != (rank_r1[m].index(pair[0]) < rank_r1[m].index(pair[1]))]
                for m in METRICS
            },
        },
        "primary_gate": {
            "comparison": "layer_llh_minus_global_fixed_low",
            "R0": paired_out["R0"]["layer_llh_minus_global_fixed_low"],
            "R1": paired_out["R1"]["layer_llh_minus_global_fixed_low"],
        },
    }
    (TASK / "R0_R1_STABILITY_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")

    print("classification counts:", summary["classification_counts"])
    print("\n== primary gate: layer_llh - global_fixed_low ==")
    for label in ("R0", "R1"):
        for m in ("fg_psnr", "fg_lpips", "full_psnr", "edge_ssim"):
            c = paired_out[label]["layer_llh_minus_global_fixed_low"][m]
            print(f"  {label} {m}: {c['mean_diff']:+.5f} CI[{c['ci95'][0]:+.5f},{c['ci95'][1]:+.5f}] "
                  f"wins {c['win_rate']} excl0={c['ci_excludes_zero']}")
    print("\nrankings R1 (fg_lpips):", rank_r1["fg_lpips"])


if __name__ == "__main__":
    main()
