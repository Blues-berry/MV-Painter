"""Standard-panel consolidation + paired bootstrap for the MV-Adapter layer-wise task.

Panel (76-object Exact holdout): R0, G-FL, G-LHL, G-LLH, L-FIX, L-LLH, L-LHL.
Comparisons P1-P5 (10,000 object-level paired bootstrap, seed 20260928):
  P1 L-LLH vs G-FL; P2 L-LLH vs G-LLH; P3 L-LLH vs L-FIX;
  P4 L-LHL vs G-LHL; P5 G-LLH vs G-LHL.
Deltas are left-minus-right for higher-better metrics and right-minus-left for
lower-better metrics (LPIPS, CIEDE2000, GT-texture), so positive always favors
the left condition.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

METRICS = ["psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
           "gt_relative_texture_error"]
LOWER_BETTER = {"fg_lpips", "ciede2000", "gt_relative_texture_error"}

SOURCES = {
    "R0":   ("results/holdout_exact_76/per_object_metrics.csv", "no_geometry"),
    "G-FL": ("results/holdout_exact_76/per_object_metrics.csv", "fixed_low"),
    "G-LHL": ("results/holdout_exact_lhl_shape_transfer_76/per_object_metrics.csv", "LHL"),
    "G-LLH": ("results/holdout_exact_equal_budget_76/per_object_metrics.csv", "LLH"),
    "L-FIX": ("results/holdout_exact_layer_fixed_76/per_object_metrics.csv", "L-FIX"),
    "L-LLH": ("results/holdout_exact_layer_llh_76/per_object_metrics.csv", "L-LLH"),
    "L-LHL": ("results/holdout_exact_layer_lhl_76/per_object_metrics.csv", "L-LHL"),
}
COMPARISONS = {
    "P1_L-LLH_vs_G-FL": ("L-LLH", "G-FL"),
    "P2_L-LLH_vs_G-LLH": ("L-LLH", "G-LLH"),
    "P3_L-LLH_vs_L-FIX": ("L-LLH", "L-FIX"),
    "P4_L-LHL_vs_G-LHL": ("L-LHL", "G-LHL"),
    "P5_G-LLH_vs_G-LHL": ("G-LLH", "G-LHL"),
}


def load_condition(path: Path, schedule: str) -> dict[str, dict[str, float]]:
    rows = list(csv.DictReader(path.open(newline="")))
    out = {}
    for row in rows:
        if row["schedule"] != schedule:
            continue
        out[row["object"]] = {m: float(row[m]) for m in METRICS}
    return out


def main() -> None:
    base = Path(__file__).resolve().parent
    panel = {}
    for label, (rel, schedule) in SOURCES.items():
        data = load_condition(base / rel, schedule)
        assert len(data) == 76, f"{label}: expected 76 objects, got {len(data)}"
        panel[label] = data

    objects = sorted(panel["R0"].keys())
    for label in panel:
        assert set(panel[label].keys()) == set(objects), f"{label}: object set mismatch"

    # 1. standard panel CSV
    panel_path = base / "MVADAPTER_STANDARD_PANEL_76.csv"
    with panel_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["object", "condition", *METRICS])
        for obj in objects:
            for label in SOURCES:
                writer.writerow([obj, label, *[panel[label][obj][m] for m in METRICS]])

    # 2. paired bootstrap
    rng_seed = 20260928
    n_boot = 10000
    results = {"protocol": "mvadapter-layerwise-panel-paired-bootstrap-v1",
               "unit": "object", "resamples": n_boot, "seed": rng_seed,
               "confidence": 0.95, "panel_rows": len(objects) * len(SOURCES),
               "comparisons": {}}
    for comp_name, (left, right) in COMPARISONS.items():
        comp = {"left": left, "right": right, "metrics": {}}
        for metric in METRICS:
            a = np.array([panel[left][o][metric] for o in objects])
            b = np.array([panel[right][o][metric] for o in objects])
            delta = (a - b) if metric not in LOWER_BETTER else (b - a)
            n = len(objects)
            rng = np.random.default_rng(rng_seed)
            idx = rng.integers(0, n, size=(n_boot, n))
            boot = delta[idx].mean(axis=1)
            lo, hi = np.percentile(boot, [2.5, 97.5])
            comp["metrics"][metric] = {
                "paired_mean_delta": float(delta.mean()),
                "paired_median_delta": float(np.median(delta)),
                "ci95_low": float(lo),
                "ci95_high": float(hi),
                "ci_excludes_zero": bool(lo > 0 or hi < 0),
                "win_rate": float((delta > 0).mean()),
                "direction": "positive_favors_left",
            }
        results["comparisons"][comp_name] = comp

    json_path = base / "MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json"
    json_path.write_text(json.dumps(results, indent=2) + "\n")

    # 3. summary table for the report
    lines = [
        "| comparison | metric | mean delta | median | CI95 | win rate | CI excl. 0 |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    for comp_name, comp in results["comparisons"].items():
        for metric, s in comp["metrics"].items():
            lines.append(
                f"| {comp_name} | {metric} | {s['paired_mean_delta']:.6f} "
                f"| {s['paired_median_delta']:.6f} "
                f"| [{s['ci95_low']:.6f}, {s['ci95_high']:.6f}] "
                f"| {s['win_rate']:.3f} | {s['ci_excludes_zero']} |"
            )
    Path(base / "MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP_SUMMARY.md").write_text(
        "\n".join(lines) + "\n")
    print("panel:", panel_path)
    print("bootstrap:", json_path)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
