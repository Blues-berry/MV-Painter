#!/usr/bin/env python3
"""Per-object diagnostic: v1 scale=1.25 vs v2a scale=1.25 (300 objects)."""
import csv
from pathlib import Path

BASE = Path("/4T/CXY/MV-Painter/mvpoutput")

def load_csv(path):
    with open(path) as f:
        return {int(float(r['object_idx'])): r for r in csv.DictReader(f)}

def sf(v):
    try: return float(v)
    except: return None

# Load datasets
v1 = load_csv(BASE / "geotex_refattn_v1/scale_1p25_300obj/per_object_metrics.csv")
v2a = load_csv(BASE / "geotex_refattn_v2/eval_v2a_step250_scale1p25_300obj/per_object_metrics.csv")

# Build per-object diff
rows = []
for i in range(300):
    if i not in v1 or i not in v2a:
        continue
    r1, r2 = v1[i], v2a[i]

    fg_ssim_1 = sf(r1.get('delta_fg_ssim'))
    fg_ssim_2 = sf(r2.get('delta_fg_ssim'))
    nef_ssim_1 = sf(r1.get('delta_nef_ssim'))
    nef_ssim_2 = sf(r2.get('delta_nef_ssim'))
    fg_lpips_1 = sf(r1.get('delta_fg_lpips'))
    fg_lpips_2 = sf(r2.get('delta_fg_lpips'))
    edge_ssim_1 = sf(r1.get('delta_edge_ssim'))
    edge_ssim_2 = sf(r2.get('delta_edge_ssim'))

    row = {
        'object_idx': i,
        'v1_fg_ssim': fg_ssim_1,
        'v2a_fg_ssim': fg_ssim_2,
        'fg_ssim_diff': (fg_ssim_2 - fg_ssim_1) if fg_ssim_1 is not None and fg_ssim_2 is not None else None,
        'v1_nef_ssim': nef_ssim_1,
        'v2a_nef_ssim': nef_ssim_2,
        'nef_ssim_diff': (nef_ssim_2 - nef_ssim_1) if nef_ssim_1 is not None and nef_ssim_2 is not None else None,
        'v1_fg_lpips': fg_lpips_1,
        'v2a_fg_lpips': fg_lpips_2,
        'fg_lpips_diff': (fg_lpips_2 - fg_lpips_1) if fg_lpips_1 is not None and fg_lpips_2 is not None else None,
        'v1_edge_ssim': edge_ssim_1,
        'v2a_edge_ssim': edge_ssim_2,
        'edge_ssim_diff': (edge_ssim_2 - edge_ssim_1) if edge_ssim_1 is not None and edge_ssim_2 is not None else None,
    }
    rows.append(row)

# Save CSV
csv_path = BASE / "geotex_refattn_v2/v2a_continue_control/v2a_vs_v1_per_object_300obj.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

# Find regressions
fg_regressions = sorted([r for r in rows if r['fg_ssim_diff'] is not None], key=lambda r: r['fg_ssim_diff'])[:20]
nef_regressions = sorted([r for r in rows if r['nef_ssim_diff'] is not None], key=lambda r: r['nef_ssim_diff'])[:20]
lpips_regressions = sorted([r for r in rows if r['fg_lpips_diff'] is not None], key=lambda r: r['fg_lpips_diff'], reverse=True)[:20]

# Write markdown
md_path = BASE / "geotex_refattn_v2/v2a_continue_control/v2a_vs_v1_regression_diagnostic.md"
with open(md_path, 'w') as f:
    f.write("# v2a vs v1 Regression Diagnostic (300 objects, scale=1.25)\n\n")
    f.write("**Date:** 2026-06-12\n")
    f.write("**Comparison:** v1 scale=1.25 vs v2a step250 scale=1.25\n")
    f.write("**Objects:** 0-299 (identical)\n")
    f.write("**Evaluator:** eval_scale_inline.py\n")
    f.write("**Seed:** 42\n\n")

    f.write("## Summary\n\n")
    fg_improved = sum(1 for r in rows if r['fg_ssim_diff'] is not None and r['fg_ssim_diff'] > 0)
    fg_regressed = sum(1 for r in rows if r['fg_ssim_diff'] is not None and r['fg_ssim_diff'] < 0)
    f.write(f"- FG SSIM: {fg_improved} improved, {fg_regressed} regressed\n")

    nef_improved = sum(1 for r in rows if r['nef_ssim_diff'] is not None and r['nef_ssim_diff'] > 0)
    nef_regressed = sum(1 for r in rows if r['nef_ssim_diff'] is not None and r['nef_ssim_diff'] < 0)
    f.write(f"- NEF SSIM: {nef_improved} improved, {nef_regressed} regressed\n")

    lpips_improved = sum(1 for r in rows if r['fg_lpips_diff'] is not None and r['fg_lpips_diff'] < 0)
    lpips_regressed = sum(1 for r in rows if r['fg_lpips_diff'] is not None and r['fg_lpips_diff'] > 0)
    f.write(f"- FG LPIPS: {lpips_improved} improved, {lpips_regressed} regressed\n\n")

    f.write("## Top-20 FG SSIM Regressions\n\n")
    f.write("| Object | v1 FG SSIM | v2a FG SSIM | Diff |\n")
    f.write("|--------|-----------|-------------|------|\n")
    for r in fg_regressions:
        f.write(f"| {r['object_idx']} | {r['v1_fg_ssim']:+.4f} | {r['v2a_fg_ssim']:+.4f} | {r['fg_ssim_diff']:+.4f} |\n")

    f.write("\n## Top-20 NEF SSIM Regressions\n\n")
    f.write("| Object | v1 NEF SSIM | v2a NEF SSIM | Diff |\n")
    f.write("|--------|-------------|--------------|------|\n")
    for r in nef_regressions:
        f.write(f"| {r['object_idx']} | {r['v1_nef_ssim']:+.4f} | {r['v2a_nef_ssim']:+.4f} | {r['nef_ssim_diff']:+.4f} |\n")

    f.write("\n## Top-20 FG LPIPS Regressions (higher = worse)\n\n")
    f.write("| Object | v1 FG LPIPS | v2a FG LPIPS | Diff |\n")
    f.write("|--------|-------------|--------------|------|\n")
    for r in lpips_regressions:
        f.write(f"| {r['object_idx']} | {r['v1_fg_lpips']:+.4f} | {r['v2a_fg_lpips']:+.4f} | {r['fg_lpips_diff']:+.4f} |\n")

    f.write("\n## Visualization List\n\n")
    f.write("Objects to visualize for regression analysis:\n\n")
    f.write("```\n")
    for r in fg_regressions[:10]:
        f.write(f"obj_{r['object_idx']:03d}\n")
    f.write("```\n")

print(f"CSV: {csv_path}")
print(f"MD: {md_path}")
