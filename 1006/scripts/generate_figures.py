#!/usr/bin/env python3
"""Generate the figures and machine-readable summary tables in this evidence bundle.

The script reads only included, audited summary JSONs in 1006/data and uses object
means or paired bootstrap summaries as recorded by their source audits.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DERIVED = ROOT / "data" / "derived"
FIG.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10})


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def paired_summary(path: str, metric: str):
    test = load(path)["tests"][metric]
    return float(test["mean_delta"]), float(test["ci95"][0]), float(test["ci95"][1]), float(test["favorable_rate"])


def write_csv(path: Path, fields, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# Figure 1: exact requested profiles used in the three registered B contrasts.
profiles = {
    "LLH": {"deep": [1.25, 1.25, 2.50], "middle": [1.25, 1.25, 2.50], "shallow": [0.50, 0.50, 0.75]},
    "HLL": {"deep": [2.50, 1.25, 1.25], "middle": [2.50, 1.25, 1.25], "shallow": [0.75, 0.50, 0.50]},
    "LFM-exact": {"deep": [1.675, 1.675, 1.675], "middle": [1.675, 1.675, 1.675], "shallow": [0.585, 0.585, 0.585]},
    "LLL": {"deep": [1.25, 1.25, 1.25], "middle": [1.25, 1.25, 1.25], "shallow": [0.50, 0.50, 0.50]},
}
caps = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
fig, axs = plt.subplots(3, 1, figsize=(7.4, 5.8), sharex=True, constrained_layout=True)
colors = {"LLH": "#4477AA", "HLL": "#EE6677", "LFM-exact": "#228833", "LLL": "#777777"}
xb = np.array([0, 17, 33, 50])
for ax, layer in zip(axs, ["deep", "middle", "shallow"]):
    for name, prof in profiles.items():
        vals = prof[layer]
        ax.step(xb, [*vals, vals[-1]], where="post", lw=1.8, color=colors[name], label=name)
    ax.axhline(caps[layer], color="#555555", ls="--", lw=0.8)
    ax.text(49.4, caps[layer] + 0.035, f"cap {caps[layer]:g}", ha="right", va="bottom", fontsize=7, color="#555555")
    ax.set_ylabel(f"{layer.capitalize()}\nrequested scale")
    ax.grid(axis="y", alpha=0.2)
axs[-1].set_xticks([0, 17, 33, 50], ["0", "17", "33", "50"])
axs[-1].set_xlabel("Denoising step (early / middle / late windows: 17 / 16 / 17 steps)")
axs[0].legend(ncol=4, frameon=False, loc="upper left")
fig.suptitle("FRESH_CONFIRM_B profiles and per-layer implementation caps", y=1.02)
fig.text(0.5, -0.01, "Requested scale is not realized residual dose; LLH, HLL and LFM-exact share per-layer requested means.", ha="center", fontsize=8)
fig.savefig(FIG / "b_profiles.pdf", bbox_inches="tight")
fig.savefig(FIG / "b_profiles.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Figure 2 / source table: registered B contrasts plus explicitly exploratory HLL-LLL.
base = "data/fresh_b/"
contrasts = [
    ("LLH − LFM-exact", "paired_layer_llh_minus_lfm_exact.json", "registered B1"),
    ("LLH − HLL", "paired_layer_llh_minus_layer_hll.json", "registered B2"),
    ("LLH − LLL", "paired_layer_llh_minus_a3_baseline.json", "registered B2"),
    ("HLL − LLL", "paired_layer_hll_minus_a3_baseline_exploratory.json", "exploratory"),
]
b_rows = []
for label, file, status in contrasts:
    for metric in ["fg_psnr", "fg_lpips"]:
        mean, lo, hi, fav = paired_summary(base + file, metric)
        b_rows.append({"contrast": label, "status": status, "metric": metric, "mean_delta": mean, "ci95_low": lo, "ci95_high": hi, "favorable_rate_first_method": fav})
write_csv(DERIVED / "b_primary_contrasts.csv", list(b_rows[0]), b_rows)
fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.3), constrained_layout=True)
labels = [c[0] for c in contrasts]
for ax, metric, title, margin in [
    (axs[0], "fg_psnr", "FG-PSNR change (dB)", 0.5),
    (axs[1], "fg_lpips", "FG-LPIPS change", 0.01),
]:
    yy = np.arange(len(labels))[::-1]
    for y, (label, file, status) in zip(yy, contrasts):
        mean, lo, hi, fav = paired_summary(base + file, metric)
        color = "#4477AA" if status != "exploratory" else "#999999"
        ax.errorbar(mean, y, xerr=[[mean-lo], [hi-mean]], fmt="o", color=color, capsize=3, ms=5, lw=1.4)
    ax.axvline(0, color="#222222", lw=0.9)
    ax.set_yticks(yy, labels)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.2)
    if metric == "fg_psnr":
        ax.axvspan(-margin, margin, color="#999999", alpha=0.10, zorder=0)
        ax.text(0, -0.62, "registered ±0.5 dB practical margin", ha="center", va="top", fontsize=7, color="#555555")
    else:
        ax.axvspan(-margin, margin, color="#999999", alpha=0.10, zorder=0)
        ax.text(0, -0.62, "registered ±0.01 practical margin", ha="center", va="top", fontsize=7, color="#555555")
    ax.set_xlabel("First condition − second condition")
fig.suptitle("Paired object-bootstrap estimates in FRESH_CONFIRM_B (N=150)")
fig.savefig(FIG / "b_primary_contrasts.pdf", bbox_inches="tight")
fig.savefig(FIG / "b_primary_contrasts.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Figure 3 / table: fixed-cohort E1, with seed means and 3-seed average object CI.
e1 = load("evidence/audits/next_stage_20261006/MULTISEED_ANALYSIS.json")
e1_rows = []
fig, axs = plt.subplots(1, 2, figsize=(8.3, 3.7), constrained_layout=True)
for ax, metric, title in [(axs[0], "fg_psnr", "FG-PSNR (dB)"), (axs[1], "fg_lpips", "FG-LPIPS")]:
    c = next(q for q in e1["metrics"][metric]["contrasts"] if q["contrast"] == "layer_llh-lfm_exact")
    seed_means = [float(c["mean_delta_by_generation_seed"][str(s)]) for s in [42, 43, 44]]
    avg = float(c["mean_delta"]); lo, hi = map(float, c["ci95_object_bootstrap"])
    xs = np.arange(4)
    ax.scatter(xs[:3], seed_means, color="#4477AA", s=36, zorder=3)
    ax.errorbar(xs[3], avg, yerr=[[avg-lo], [hi-avg]], fmt="D", color="#CC6677", capsize=4, ms=6, zorder=4)
    ax.axhline(0, color="#222222", lw=0.8)
    ax.set_xticks(xs, ["42", "43", "44", "avg. + CI"])
    ax.set_title(title)
    ax.set_xlabel("Fixed generation seed / averaged estimate")
    ax.grid(axis="y", alpha=0.2)
    e1_rows.append({"metric": metric, "contrast": c["contrast"], "mean_delta": avg, "ci95_low": lo, "ci95_high": hi,
                    "favorable_object_fraction": c["favorable_object_fraction"], "seed42_mean": seed_means[0], "seed43_mean": seed_means[1],
                    "seed44_mean": seed_means[2], "effect_over_median_seed_range": c["absolute_mean_effect_over_median_seed_range"]})
fig.suptitle("E1 realization sensitivity on the reused 48-object subset")
fig.savefig(FIG / "e1_seed_sensitivity.pdf", bbox_inches="tight")
fig.savefig(FIG / "e1_seed_sensitivity.png", dpi=220, bbox_inches="tight")
plt.close(fig)
write_csv(DERIVED / "e1_seed_sensitivity.csv", list(e1_rows[0]), e1_rows)

# Figure 4 / table: E2 fixed 2x2 factors, moving deep and middle together.
e2 = load("evidence/audits/next_stage_20261006/STATIC_FACTORIAL_ANALYSIS.json")
e2_rows = []
fig, axs = plt.subplots(1, 2, figsize=(8.5, 4.0), constrained_layout=True)
for ax, metric, title in [(axs[0], "fg_psnr", "FG-PSNR (dB)"), (axs[1], "fg_lpips", "FG-LPIPS")]:
    effects = e2["metrics"][metric]["factor_effects"]
    order = ["deep_middle", "shallow", "interaction"]
    yy = np.arange(3)[::-1]
    for y, factor in zip(yy, order):
        x = next(v for v in effects if v["factor"] == factor)
        lo, hi = map(float, x["ci95_object_bootstrap"])
        ax.errorbar(float(x["mean"]), y, xerr=[[float(x["mean"])-lo], [hi-float(x["mean"])]], fmt="o", capsize=3, color="#4477AA", lw=1.4)
        e2_rows.append({"metric": metric, "factor": factor, "mean": x["mean"], "ci95_low": lo, "ci95_high": hi,
                        "favorable_object_fraction": x["favorable_object_fraction"], "holm_p": x["p_holm_three_factors"]})
    ax.axvline(0, color="#222222", lw=0.8)
    ax.set_yticks(yy, ["deep + middle", "shallow", "factor interaction"])
    ax.set_title(title)
    ax.set_xlabel("Factor effect (negative LPIPS / positive PSNR favor stronger factor)")
    ax.grid(axis="x", alpha=0.2)
fig.suptitle("E2 static 2×2 sensitivity; 48 reused objects, three fixed seeds")
fig.savefig(FIG / "e2_static_factors.pdf", bbox_inches="tight")
fig.savefig(FIG / "e2_static_factors.png", dpi=220, bbox_inches="tight")
plt.close(fig)
write_csv(DERIVED / "e2_static_factors.csv", list(e2_rows[0]), e2_rows)

# Figure 5 / table: native glTF base-color unseen-view endpoint differences.
glb = load("data/glb_native/GLB_NATIVE_EGL_ANALYSIS.json")
comp = glb["layer_llh_minus_comparator_object_bootstrap"]["contrasts"]
items = [("FG-PSNR (dB)", "masked_psnr", "layer_llh_minus_native_gfl"),
         ("FG-LPIPS", "fg_lpips", "layer_llh_minus_native_gfl"),
         ("CIEDE2000", "ciede2000", "layer_llh_minus_native_gfl")]
glb_rows=[]
for label, metric, contrast in items:
    v=comp[metric][contrast]["N20"]
    glb_rows.append({"endpoint": label, "mean_delta_llh_minus_gfl": v["mean_delta"], "ci95_low": v["object_bootstrap_ci95"][0],
                     "ci95_high": v["object_bootstrap_ci95"][1], "n_objects": v["n_objects"]})
write_csv(DERIVED / "glb_native_llh_minus_gfl.csv", list(glb_rows[0]), glb_rows)
fig, axs = plt.subplots(1, 3, figsize=(8.2, 2.7), constrained_layout=True)
for ax, (label, metric, contrast), row in zip(axs, items, glb_rows):
    m=float(row["mean_delta_llh_minus_gfl"]); lo=float(row["ci95_low"]); hi=float(row["ci95_high"])
    ax.errorbar(m, 0, xerr=[[m-lo],[hi-m]], fmt="o", capsize=4, color="#4477AA", lw=1.5)
    ax.axvline(0, color="#222222", lw=0.8)
    ax.set_yticks([]); ax.set_title(label); ax.set_xlabel("LLH − GFL")
    ax.grid(axis="x", alpha=0.2)
fig.suptitle("Stored GLB base-color renders: mixed N=20 endpoint differences")
fig.savefig(FIG / "glb_native_endpoints.pdf", bbox_inches="tight")
fig.savefig(FIG / "glb_native_endpoints.png", dpi=220, bbox_inches="tight")
plt.close(fig)

print("Generated figures and derived tables under 1006/.")
