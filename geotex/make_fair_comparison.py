#!/usr/bin/env python3
"""Generate fair 50-object comparison between v1 and v2a."""
import csv
import json
from pathlib import Path

BASE = Path("/4T/CXY/MV-Painter/mvpoutput")

def load_csv(path):
    with open(path) as f:
        return {int(float(r['object_idx'])): r for r in csv.DictReader(f)}

def sf(v):
    try: return float(v)
    except: return None

# Load all datasets
v1_s10 = load_csv(BASE / "geotex_refattn_v1/scale_sweep_50obj/scale_1p00/per_object_metrics.csv")
v1_s125 = load_csv(BASE / "geotex_refattn_v1/scale_sweep_50obj/scale_1p25/per_object_metrics.csv")
v2a_s250_s10 = load_csv(BASE / "geotex_refattn_v2/v2a_continue_control/eval_step250_scale1p0/per_object_metrics.csv")
v2a_s250_s125 = load_csv(BASE / "geotex_refattn_v2/v2a_continue_control/eval_step250_scale1p25/per_object_metrics.csv")
v2a_s500_s10 = load_csv(BASE / "geotex_refattn_v2/v2a_continue_control/eval_step500_scale1p0/per_object_metrics.csv")
v2a_s500_s125 = load_csv(BASE / "geotex_refattn_v2/v2a_continue_control/eval_step500_scale1p25/per_object_metrics.csv")

datasets = {
    'v1_s10': v1_s10, 'v1_s125': v1_s125,
    'v2a_s250_s10': v2a_s250_s10, 'v2a_s250_s125': v2a_s250_s125,
    'v2a_s500_s10': v2a_s500_s10, 'v2a_s500_s125': v2a_s500_s125,
}

# Key metrics (all use delta_ prefix in sweep/inline CSVs)
metrics = [
    'delta_full_psnr', 'delta_full_ssim', 'delta_full_lpips',
    'delta_fg_psnr', 'delta_fg_ssim', 'delta_fg_lpips',
    'delta_crop_psnr', 'delta_crop_ssim', 'delta_crop_lpips',
    'delta_edge_ssim', 'delta_nef_ssim',
]

# Compute per-dataset stats
stats = {}
for name, data in datasets.items():
    stats[name] = {}
    for m in metrics:
        vals = [sf(data[i].get(m)) for i in range(50) if i in data]
        vals = [v for v in vals if v is not None]
        if vals:
            positive = sum(1 for v in vals if v > 0)
            stats[name][m] = {
                'mean': sum(vals) / len(vals),
                'min': min(vals),
                'max': max(vals),
                'positive': positive,
                'total': len(vals),
            }

# Write CSV
csv_rows = []
for i in range(50):
    row = {'object_idx': i}
    for name, data in datasets.items():
        if i in data:
            for m in metrics:
                row[f'{name}_{m}'] = sf(data[i].get(m))
    csv_rows.append(row)

csv_path = BASE / "geotex_refattn_v2/v2a_continue_control/fair_50obj_comparison.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
    writer.writeheader()
    writer.writerows(csv_rows)

# Write markdown
md_path = BASE / "geotex_refattn_v2/v2a_continue_control/fair_50obj_comparison.md"
with open(md_path, 'w') as f:
    f.write("# Fair 50-Object Comparison: v1 vs v2a\n\n")
    f.write("**Date:** 2026-06-12\n")
    f.write("**Objects:** 0-49 (identical across all evaluations)\n")
    f.write("**Evaluator:** eval_scale_inline.py (same code for all)\n")
    f.write("**Seed:** 42 (same for all)\n\n")

    f.write("## Summary Table\n\n")
    f.write("| Metric | v1 s=1.0 | v1 s=1.25 | v2a s250 s=1.0 | v2a s250 s=1.25 | v2a s500 s=1.0 | v2a s500 s=1.25 |\n")
    f.write("|--------|----------|-----------|----------------|-----------------|----------------|-----------------|\n")

    for m in metrics:
        label = m.replace('delta_', '').replace('_', ' ').title()
        vals = []
        for name in ['v1_s10', 'v1_s125', 'v2a_s250_s10', 'v2a_s250_s125', 'v2a_s500_s10', 'v2a_s500_s125']:
            s = stats[name].get(m, {})
            vals.append(s.get('mean', 0))
        f.write(f"| {label} | {vals[0]:+.4f} | {vals[1]:+.4f} | {vals[2]:+.4f} | {vals[3]:+.4f} | {vals[4]:+.4f} | {vals[5]:+.4f} |\n")

    f.write("\n## Positive Object Ratio\n\n")
    f.write("| Metric | v1 s=1.0 | v1 s=1.25 | v2a s250 s=1.0 | v2a s250 s=1.25 | v2a s500 s=1.0 | v2a s500 s=1.25 |\n")
    f.write("|--------|----------|-----------|----------------|-----------------|----------------|-----------------|\n")

    for m in ['delta_fg_ssim', 'delta_edge_ssim', 'delta_crop_ssim']:
        label = m.replace('delta_', '').replace('_', ' ').title()
        vals = []
        for name in ['v1_s10', 'v1_s125', 'v2a_s250_s10', 'v2a_s250_s125', 'v2a_s500_s10', 'v2a_s500_s125']:
            s = stats[name].get(m, {})
            vals.append(f"{s.get('positive', 0)}/{s.get('total', 0)}")
        f.write(f"| {label} | {vals[0]} | {vals[1]} | {vals[2]} | {vals[3]} | {vals[4]} | {vals[5]} |\n")

    f.write("\n## LPIPS Direction Check\n\n")
    f.write("LPIPS: adapter - original. **More negative = better** (lower LPIPS = better quality).\n\n")
    f.write("| Config | Full LPIPS Δ | FG LPIPS Δ | Crop LPIPS Δ |\n")
    f.write("|--------|-------------|------------|-------------|\n")

    for name in ['v1_s10', 'v1_s125', 'v2a_s250_s10', 'v2a_s250_s125', 'v2a_s500_s10', 'v2a_s500_s125']:
        fl = stats[name].get('delta_full_lpips', {}).get('mean', 0)
        fg = stats[name].get('delta_fg_lpips', {}).get('mean', 0)
        cr = stats[name].get('delta_crop_lpips', {}).get('mean', 0)
        f.write(f"| {name} | {fl:+.4f} | {fg:+.4f} | {cr:+.4f} |\n")

    f.write("\n## Key Findings\n\n")

    # Compare v2a s250 s=1.0 vs v1 s=1.25
    v1_fg = stats['v1_s125'].get('delta_fg_ssim', {}).get('mean', 0)
    v2a_fg = stats['v2a_s250_s10'].get('delta_fg_ssim', {}).get('mean', 0)
    f.write(f"### v2a step250 scale=1.0 vs v1 scale=1.25\n")
    f.write(f"- FG SSIM: {v2a_fg:+.4f} vs {v1_fg:+.4f} → {'✅ 接近/超过' if abs(v2a_fg - v1_fg) < 0.01 or v2a_fg > v1_fg else '⚠️ 差距较大'}\n")

    v1_edge = stats['v1_s125'].get('delta_edge_ssim', {}).get('mean', 0)
    v2a_edge = stats['v2a_s250_s10'].get('delta_edge_ssim', {}).get('mean', 0)
    f.write(f"- Edge SSIM: {v2a_edge:+.4f} vs {v1_edge:+.4f} → {'✅ 超过' if v2a_edge >= v1_edge else '⚠️ 下降'}\n")

    f.write(f"\n### v2a step250 scale=1.25 vs v1 scale=1.25\n")
    v2a_125_fg = stats['v2a_s250_s125'].get('delta_fg_ssim', {}).get('mean', 0)
    f.write(f"- FG SSIM: {v2a_125_fg:+.4f} vs {v1_fg:+.4f} → {'✅ 明显超过' if v2a_125_fg > v1_fg + 0.01 else '⚠️ 未明显超过'}\n")

    f.write(f"\n### Over-training Check\n")
    s250_fg = stats['v2a_s250_s10'].get('delta_fg_ssim', {}).get('mean', 0)
    s500_fg = stats['v2a_s500_s10'].get('delta_fg_ssim', {}).get('mean', 0)
    f.write(f"- step250 s=1.0 FG SSIM: {s250_fg:+.4f}\n")
    f.write(f"- step500 s=1.0 FG SSIM: {s500_fg:+.4f}\n")
    f.write(f"- Difference: {s500_fg - s250_fg:+.4f} → {'⚠️ step500 过训练' if s500_fg < s250_fg - 0.01 else '✅ 无明显过训练'}\n")

print(f"CSV: {csv_path}")
print(f"MD: {md_path}")
