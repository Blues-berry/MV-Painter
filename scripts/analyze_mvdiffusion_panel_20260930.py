#!/usr/bin/env python3
"""Phase D panel consolidation + paired bootstrap for the MVDiffusion backbone.

Panel (75-object holdout, one base = sd21_depth_compat): R0 (official
unmodified) + G-FL, G-LHL, G-LLH, L-FIX, L-LLH, L-LHL. Comparisons per the
task (10,000 object-level paired bootstrap, seed 20260928):
  L-LLH vs G-FL; L-LLH vs G-LLH; L-LLH vs L-FIX; L-LHL vs G-LHL; G-LLH vs G-LHL.
Deltas direction-adjusted so positive favors the left condition. Metrics with
NaN objects (e.g. obj_0029 texture/CIEDE2000 on near-empty GT masks) drop the
object for that metric only.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

METRICS = ["interop_psnr", "interop_fg_ssim", "interop_edge_ssim",
           "interop_fg_lpips", "interop_ciede2000",
           "interop_gt_relative_texture_error"]
LOWER_BETTER = {"interop_fg_lpips", "interop_ciede2000",
                "interop_gt_relative_texture_error"}
LABELS = ["R0", "G-FL", "G-LHL", "G-LLH", "L-FIX", "L-LLH", "L-LHL"]
COMPARISONS = {
    "P1_L-LLH_vs_G-FL": ("L-LLH", "G-FL"),
    "P2_L-LLH_vs_G-LLH": ("L-LLH", "G-LLH"),
    "P3_L-LLH_vs_L-FIX": ("L-LLH", "L-FIX"),
    "P4_L-LHL_vs_G-LHL": ("L-LHL", "G-LHL"),
    "P5_G-LLH_vs_G-LHL": ("G-LLH", "G-LHL"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path,
                        default=Path("final/round2/mvdiffusion/results"))
    parser.add_argument("--seed", type=int, default=20260928)
    parser.add_argument("--resamples", type=int, default=10000)
    args = parser.parse_args()

    root = args.results_root
    sources = {
        "R0": root / "holdout_exact_75_50steps/per_object_metrics_ext.csv",
        "G-FL": root / "panel_G-FL_75/per_object_metrics_ext.csv",
        "G-LHL": root / "panel_G-LHL_75/per_object_metrics_ext.csv",
        "G-LLH": root / "panel_G-LLH_75/per_object_metrics_ext.csv",
        "L-FIX": root / "panel_L-FIX_75/per_object_metrics_ext.csv",
        "L-LLH": root / "panel_L-LLH_75/per_object_metrics_ext.csv",
        "L-LHL": root / "panel_L-LHL_75/per_object_metrics_ext.csv",
    }
    panel: dict[str, dict[str, dict[str, float]]] = {}
    for label, path in sources.items():
        rows = list(csv.DictReader(path.open(newline="")))
        assert len(rows) == 75, f"{label}: expected 75 rows, got {len(rows)}"
        panel[label] = {
            r["object"]: {m: float(r[m]) for m in METRICS} for r in rows
        }
    objects = sorted(panel["R0"].keys())
    for label in LABELS:
        assert set(panel[label]) == set(objects), f"{label}: object set mismatch"

    panel_path = root / "MVDIFFUSION_STANDARD_PANEL_RESULTS.csv"
    with panel_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["object", "condition", *METRICS])
        for obj in objects:
            for label in LABELS:
                writer.writerow([obj, label, *[panel[label][obj][m] for m in METRICS]])

    results = {
        "protocol": "mvdiffusion-scheduled-alpha-paired-bootstrap-v1",
        "unit": "object", "resamples": args.resamples, "seed": args.seed,
        "confidence": 0.95, "base": "sd21_depth_compat (unchanged deployment base)",
        "comparisons": {},
    }
    for comp_name, (left, right) in COMPARISONS.items():
        comp = {"left": left, "right": right, "metrics": {}}
        for metric in METRICS:
            pairs = [
                (panel[left][o][metric], panel[right][o][metric])
                for o in objects
                if np.isfinite(panel[left][o][metric]) and np.isfinite(panel[right][o][metric])
            ]
            a = np.array([p[0] for p in pairs])
            b = np.array([p[1] for p in pairs])
            delta = (a - b) if metric not in LOWER_BETTER else (b - a)
            n = len(delta)
            rng = np.random.default_rng(args.seed)
            idx = rng.integers(0, n, size=(args.resamples, n))
            boot = delta[idx].mean(axis=1)
            lo, hi = np.percentile(boot, [2.5, 97.5])
            comp["metrics"][metric] = {
                "paired_mean_delta": float(delta.mean()),
                "paired_median_delta": float(np.median(delta)),
                "ci95_low": float(lo),
                "ci95_high": float(hi),
                "ci_excludes_zero": bool(lo > 0 or hi < 0),
                "win_rate": float((delta > 0).mean()),
                "n_objects": int(n),
                "direction": "positive_favors_left",
            }
        results["comparisons"][comp_name] = comp

    json_path = root / "MVDIFFUSION_PAIRED_BOOTSTRAP.json"
    json_path.write_text(json.dumps(results, indent=2) + "\n")

    lines = []
    for comp_name, comp in results["comparisons"].items():
        for metric, s in comp["metrics"].items():
            lines.append(
                f"| {comp_name} | {metric} | {s['paired_mean_delta']:.6f} "
                f"| {s['paired_median_delta']:.6f} "
                f"| [{s['ci95_low']:.6f}, {s['ci95_high']:.6f}] "
                f"| {s['win_rate']:.3f} | {s['n_objects']} | {s['ci_excludes_zero']} |"
            )
    header = ("| comparison | metric | mean delta | median | CI95 | win rate | n | CI excl. 0 |\n"
              "|---|---|---:|---:|---|---:|---:|---|\n")
    (root / "MVDIFFUSION_PAIRED_BOOTSTRAP_SUMMARY.md").write_text(header + "\n".join(lines) + "\n")
    print("panel:", panel_path)
    print("bootstrap:", json_path)
    print(header + "\n".join(lines))


if __name__ == "__main__":
    main()
