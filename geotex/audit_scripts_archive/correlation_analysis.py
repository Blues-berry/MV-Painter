"""Analyze correlations between object attributes and metric improvements."""

import csv
import math
import os

# ---------------------------------------------------------------------------
# 1. Load CSVs
# ---------------------------------------------------------------------------

BASE = "/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1"
CLEAN_CSV = os.path.join(BASE, "eval_300obj_clean/per_object_metrics_fixed.csv")
SCALE_CSV = os.path.join(BASE, "scale_1p25_300obj/per_object_metrics.csv")
DIFF_CSV  = os.path.join(BASE, "scale_1p25_vs_1p00_per_object_diff.csv")

OUTPUT_MD  = os.path.join(BASE, "correlation_analysis.md")
OUTPUT_PNG = os.path.join(BASE, "correlation_fg_ratio_vs_delta_fg_ssim_diff.png")


def read_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


clean_rows = read_csv(CLEAN_CSV)
scale_rows = read_csv(SCALE_CSV)
diff_rows  = read_csv(DIFF_CSV)

print(f"Clean CSV: {len(clean_rows)} rows")
print(f"Scale CSV: {len(scale_rows)} rows")
print(f"Diff  CSV: {len(diff_rows)} rows")

# ---------------------------------------------------------------------------
# 2. Build lookup: object_idx -> edge_ratio and orig_fg_ssim from clean CSV
# ---------------------------------------------------------------------------

# edge_ratio from the clean (baseline) CSV
edge_ratio_map = {}
orig_fg_ssim_map = {}

for r in clean_rows:
    idx = int(float(r["object_idx"]))
    edge_ratio_map[idx] = float(r["edge_ratio"])
    orig_fg_ssim_map[idx] = float(r["foreground_orig_ssim"])

# ---------------------------------------------------------------------------
# 3. Build unified data rows from the diff CSV
# ---------------------------------------------------------------------------

data = []
for r in diff_rows:
    idx = int(float(r["object_idx"]))
    if idx not in edge_ratio_map:
        continue
    data.append({
        "object_idx": idx,
        "fg_ratio": float(r["fg_ratio"]),
        "edge_ratio": edge_ratio_map[idx],
        "orig_fg_ssim": orig_fg_ssim_map[idx],
        "delta_fg_ssim_diff": float(r["delta_fg_ssim_diff"]),
        "delta_fg_ssim_1p25": float(r["delta_fg_ssim_1p25"]),
        "delta_edge_ssim_1p25": float(r["delta_edge_ssim_1p25"]),
        "delta_full_psnr_1p25": float(r["delta_full_psnr_1p25"]),
    })

print(f"Merged data: {len(data)} rows")

# ---------------------------------------------------------------------------
# 4. Correlation helpers (manual computation with numpy)
# ---------------------------------------------------------------------------

import numpy as np
from scipy import stats


def pearson(x, y):
    """Return (r, p_value) using scipy."""
    r, p = stats.pearsonr(x, y)
    return r, p


def spearman(x, y):
    """Return (rho, p_value) using scipy."""
    rho, p = stats.spearmanr(x, y)
    return rho, p


# ---------------------------------------------------------------------------
# 5. Compute all five correlations
# ---------------------------------------------------------------------------

pairs = [
    ("fg_ratio vs delta_fg_ssim_diff",
     "fg_ratio", "delta_fg_ssim_diff",
     "Does foreground size predict improvement (1p25 vs 1p00)?"),

    ("fg_ratio vs delta_fg_ssim_1p25",
     "fg_ratio", "delta_fg_ssim_1p25",
     "Does foreground size predict absolute FG SSIM at scale 1.25?"),

    ("edge_ratio vs delta_edge_ssim_1p25",
     "edge_ratio", "delta_edge_ssim_1p25",
     "Does edge complexity predict edge SSIM improvement at scale 1.25?"),

    ("fg_ratio vs delta_full_psnr_1p25",
     "fg_ratio", "delta_full_psnr_1p25",
     "Does foreground size predict full-image PSNR at scale 1.25?"),

    ("orig_fg_ssim vs delta_fg_ssim_diff",
     "orig_fg_ssim", "delta_fg_ssim_diff",
     "Do worse-baseline objects improve more (1p25 vs 1p00)?"),
]

results = []
for label, xkey, ykey, description in pairs:
    x = np.array([d[xkey] for d in data])
    y = np.array([d[ykey] for d in data])

    # Filter out NaN/Inf
    mask = np.isfinite(x) & np.isfinite(y)
    x_clean, y_clean = x[mask], y[mask]
    n = len(x_clean)

    r, p_r = pearson(x_clean, y_clean)
    rho, p_rho = spearman(x_clean, y_clean)

    results.append({
        "label": label,
        "description": description,
        "xkey": xkey,
        "ykey": ykey,
        "n": n,
        "pearson_r": r,
        "pearson_p": p_r,
        "spearman_rho": rho,
        "spearman_p": p_rho,
    })

# Print to console
for res in results:
    print(f"\n{res['label']}")
    print(f"  n={res['n']}, Pearson r={res['pearson_r']:.4f} (p={res['pearson_p']:.4e}), "
          f"Spearman rho={res['spearman_rho']:.4f} (p={res['spearman_p']:.4e})")

# ---------------------------------------------------------------------------
# 6. Scatter plot: fg_ratio vs delta_fg_ssim_diff
# ---------------------------------------------------------------------------

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

x_plot = np.array([d["fg_ratio"] for d in data])
y_plot = np.array([d["delta_fg_ssim_diff"] for d in data])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(x_plot, y_plot, alpha=0.4, s=15, edgecolors="none")

# Regression line
mask = np.isfinite(x_plot) & np.isfinite(y_plot)
slope, intercept = np.polyfit(x_plot[mask], y_plot[mask], 1)
x_line = np.linspace(x_plot[mask].min(), x_plot[mask].max(), 100)
ax.plot(x_line, slope * x_line + intercept, "r-", linewidth=2,
        label=f"y = {slope:.3f}x + {intercept:.4f}")

ax.set_xlabel("Foreground Ratio (fg_ratio)", fontsize=12)
ax.set_ylabel("Delta FG SSIM (1p25 - 1p00)", fontsize=12)
ax.set_title("Foreground Ratio vs FG SSIM Improvement (Scale 1.25 vs 1.00)", fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

r_val = results[0]["pearson_r"]
p_val = results[0]["pearson_p"]
ax.text(0.02, 0.98, f"Pearson r = {r_val:.4f}\np = {p_val:.2e}\nn = {results[0]['n']}",
        transform=ax.transAxes, fontsize=11, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150)
print(f"\nScatter plot saved to {OUTPUT_PNG}")

# ---------------------------------------------------------------------------
# 7. Write markdown report
# ---------------------------------------------------------------------------

lines = [
    "# Correlation Analysis: Object Attributes vs Metric Improvements",
    "",
    f"**Data sources:**",
    f"- Clean baseline: `eval_300obj_clean/per_object_metrics_fixed.csv` ({len(clean_rows)} objects)",
    f"- Scale 1.25: `scale_1p25_300obj/per_object_metrics.csv` ({len(scale_rows)} objects)",
    f"- Per-object diff: `scale_1p25_vs_1p00_per_object_diff.csv` ({len(diff_rows)} objects)",
    f"- Merged sample size: **{len(data)} objects**",
    "",
    "---",
    "",
    "## Results Summary",
    "",
    "| # | Correlation | n | Pearson r | p-value | Spearman rho | p-value |",
    "|---|-------------|---|-----------|---------|--------------|---------|",
]

for i, res in enumerate(results, 1):
    lines.append(
        f"| {i} | {res['label']} | {res['n']} "
        f"| {res['pearson_r']:.4f} | {res['pearson_p']:.2e} "
        f"| {res['spearman_rho']:.4f} | {res['spearman_p']:.2e} |"
    )

lines += [
    "",
    "---",
    "",
    "## Detailed Analysis",
    "",
]

for i, res in enumerate(results, 1):
    # Interpret strength
    abs_r = abs(res["pearson_r"])
    if abs_r < 0.1:
        strength = "negligible"
    elif abs_r < 0.3:
        strength = "weak"
    elif abs_r < 0.5:
        strength = "moderate"
    elif abs_r < 0.7:
        strength = "strong"
    else:
        strength = "very strong"

    sig = "significant" if res["pearson_p"] < 0.05 else "not significant"

    lines += [
        f"### {i}. {res['label']}",
        f"**Question:** {res['description']}",
        "",
        f"- **n** = {res['n']}",
        f"- **Pearson r** = {res['pearson_r']:.4f} (p = {res['pearson_p']:.4e}) -- {strength}, {sig} at alpha=0.05",
        f"- **Spearman rho** = {res['spearman_rho']:.4f} (p = {res['spearman_p']:.4e})",
        "",
    ]

lines += [
    "---",
    "",
    "## Interpretation",
    "",
]

# Auto-generate interpretation for key findings
for res in results:
    abs_r = abs(res["pearson_r"])
    sig = res["pearson_p"] < 0.05
    direction = "positive" if res["pearson_r"] > 0 else "negative"

    if sig:
        if "fg_ratio" in res["xkey"] and "delta_fg_ssim_diff" == res["ykey"]:
            lines.append(f"- **{res['label']}**: Statistically significant {direction} correlation (r={res['pearson_r']:.4f}). "
                         f"{'Larger foreground regions tend to show greater SSIM improvement from scale 1.00 to 1.25.' if res['pearson_r'] > 0 else 'Smaller foreground regions tend to show greater SSIM improvement.'}")
        elif "edge_ratio" in res["xkey"]:
            lines.append(f"- **{res['label']}**: Statistically significant {direction} correlation (r={res['pearson_r']:.4f}). "
                         f"{'Objects with more edge area tend to show greater edge SSIM improvement.' if res['pearson_r'] > 0 else 'Objects with less edge area tend to show greater edge SSIM improvement.'}")
        elif "orig_fg_ssim" in res["xkey"]:
            lines.append(f"- **{res['label']}**: Statistically significant {direction} correlation (r={res['pearson_r']:.4f}). "
                         f"{'Objects with higher baseline FG SSIM improve more.' if res['pearson_r'] > 0 else 'Objects with lower baseline FG SSIM (worse quality) tend to improve more, consistent with a regression-to-mean effect.'}")
        else:
            lines.append(f"- **{res['label']}**: Statistically significant {direction} correlation (r={res['pearson_r']:.4f}).")
    else:
        lines.append(f"- **{res['label']}**: No statistically significant correlation (r={res['pearson_r']:.4f}, p={res['pearson_p']:.4e}).")

lines += [
    "",
    "---",
    "",
    f"## Scatter Plot",
    "",
    f"![fg_ratio vs delta_fg_ssim_diff](correlation_fg_ratio_vs_delta_fg_ssim_diff.png)",
    "",
    f"**Figure:** Each point is one object. Red line = linear regression fit.",
]

# Add footnote about methodology
lines += [
    "",
    "---",
    "",
    "## Methodology",
    "",
    "- Pearson r measures linear correlation; Spearman rho measures monotonic correlation (rank-based).",
    "- p-values test H0: no correlation. Significant at alpha=0.05.",
    "- `fg_ratio` = foreground pixel fraction from baseline evaluation.",
    "- `edge_ratio` = edge pixel fraction from baseline evaluation.",
    "- `orig_fg_ssim` = baseline foreground SSIM (scale 1.00, no adapter).",
    "- `delta_fg_ssim_diff` = (FG SSIM at 1.25) - (FG SSIM at 1.00), i.e., improvement from scale change.",
    "- `delta_fg_ssim_1p25` = FG SSIM improvement at scale 1.25 vs GT.",
    "- `delta_edge_ssim_1p25` = edge SSIM improvement at scale 1.25 vs GT.",
    "- `delta_full_psnr_1p25` = full-image PSNR at scale 1.25 vs GT.",
]

with open(OUTPUT_MD, "w") as f:
    f.write("\n".join(lines))

print(f"\nReport saved to {OUTPUT_MD}")
