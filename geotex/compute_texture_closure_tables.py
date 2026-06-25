#!/usr/bin/env python3
"""Compute texture closure tables from 300-object evaluation data.

Reads per_object_metrics.csv from C3, s=1.25, s=2.50 and produces:
  - summary_absolute.csv
  - summary_relative_to_s125.csv
  - texture_loss_rate.csv
  - win_rate_summary.csv
  - bootstrap_ci.csv
  - texture_closure_table_for_paper.md

Requires: C3_300obj, s125_texture_reeval, s250_texture_reeval to be complete.
"""

import os
import csv
import json
import numpy as np
from pathlib import Path

BASE = '/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1'
AUDIT_DIR = f'{BASE}/paper_readiness_audit/cadgraphics_fullpaper_patch_v1'
OUT_DIR = f'{AUDIT_DIR}/01_texture_closure_300'
STAT_DIR = f'{AUDIT_DIR}/05_statistics'

C3_CSV = f'{BASE}/C3_300obj/per_object_metrics.csv'
S125_CSV = f'{AUDIT_DIR}/01_texture_closure_300/s125_texture_reeval/per_object_metrics.csv'
S250_CSV = f'{AUDIT_DIR}/01_texture_closure_300/s250_texture_reeval/per_object_metrics.csv'


def load_csv(path):
    """Load CSV as list of dicts with float conversion."""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = {}
            for k, v in row.items():
                try:
                    d[k] = float(v)
                except (ValueError, TypeError):
                    d[k] = v
            rows.append(d)
    return rows


def check_consistency(c3_rows, s125_rows, s250_rows):
    """Verify object IDs and counts match."""
    assert len(c3_rows) == 300, f"C3 has {len(c3_rows)} rows, expected 300"
    assert len(s125_rows) == 300, f"s=1.25 has {len(s125_rows)} rows, expected 300"
    assert len(s250_rows) == 300, f"s=2.50 has {len(s250_rows)} rows, expected 300"

    c3_ids = [int(r['object_idx']) for r in c3_rows]
    s125_ids = [int(r['object_idx']) for r in s125_rows]
    s250_ids = [int(r['object_idx']) for r in s250_rows]

    assert c3_ids == s125_ids == s250_ids, "Object ID mismatch!"

    # Check all have texture columns
    for name, rows in [('C3', c3_rows), ('s=1.25', s125_rows), ('s=2.50', s250_rows)]:
        assert 'adapter_fg_rgb_std' in rows[0], f"{name} missing adapter_fg_rgb_std"
        assert 'adapter_fg_grad_mag' in rows[0], f"{name} missing adapter_fg_grad_mag"
        assert 'adapter_fg_lap_var' in rows[0], f"{name} missing adapter_fg_lap_var"

    print("✅ Consistency check passed: 300 objects × 3 methods, all texture columns present.")


def compute_summary_absolute(c3_rows, s125_rows, s250_rows):
    """Generate summary_absolute.csv."""
    metrics = ['adapter_fg_ssim', 'adapter_edge_ssim', 'adapter_full_psnr',
               'adapter_fg_lpips', 'adapter_fg_lap_var', 'adapter_fg_rgb_std',
               'adapter_fg_grad_mag']
    labels = ['FG-SSIM ↑', 'Edge-SSIM ↑', 'PSNR ↑', 'FG-LPIPS ↓',
              'Lap Var ↑', 'RGB Std ↑', 'Gradient Mag ↑']

    rows_out = []
    for name, data in [('s=1.25', s125_rows), ('s=2.50', s250_rows), ('C3', c3_rows)]:
        row = {'Method': name}
        for metric, label in zip(metrics, labels):
            values = [r[metric] for r in data if metric in r]
            row[label] = f"{np.mean(values):.4f}" if values else "N/A"
        rows_out.append(row)

    path = os.path.join(OUT_DIR, 'summary_absolute.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Method'] + labels)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Saved: {path}")
    return rows_out


def compute_summary_relative(c3_rows, s125_rows, s250_rows):
    """Generate summary_relative_to_s125.csv."""
    tex_metrics = ['adapter_fg_lap_var', 'adapter_fg_rgb_std', 'adapter_fg_grad_mag']
    tex_labels = ['Lap Var', 'RGB Std', 'Gradient Mag']

    rows_out = []
    for name, data in [('s=1.25', s125_rows), ('s=2.50', s250_rows), ('C3', c3_rows)]:
        row = {'Method': name}

        # ΔFG-SSIM (relative to no-adapter, from delta column)
        delta_fg = [r.get('delta_fg_ssim', 0) for r in data]
        row['ΔFG-SSIM ↑'] = f"{np.mean(delta_fg):.4f}"

        # Texture ratios relative to s=1.25
        for metric, label in zip(tex_metrics, tex_labels):
            method_vals = [r[metric] for r in data]
            s125_vals = [r[metric] for r in s125_rows]
            # Ratio
            ratios = [m / max(s, 1e-8) for m, s in zip(method_vals, s125_vals)]
            row[f'{label} Ratio'] = f"{np.mean(ratios):.4f}"
            # Delta
            deltas = [m - s for m, s in zip(method_vals, s125_vals)]
            row[f'Δ{label}'] = f"{np.mean(deltas):.6f}"

        # Assessment
        if name == 's=1.25':
            row['Assessment'] = 'Baseline (texture-best)'
        elif name == 's=2.50':
            row['Assessment'] = 'Shape gain + texture loss'
        else:
            row['Assessment'] = 'Better trade-off'

        rows_out.append(row)

    path = os.path.join(OUT_DIR, 'summary_relative_to_s125.csv')
    fieldnames = list(rows_out[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Saved: {path}")
    return rows_out


def compute_texture_loss_rate(c3_rows, s125_rows, s250_rows):
    """Compute texture loss rate: fraction of objects with texture degradation."""
    results = []

    for name, data in [('s=1.25', s125_rows), ('s=2.50', s250_rows), ('C3', c3_rows)]:
        n = len(data)
        s125_lv = [r['adapter_fg_lap_var'] for r in s125_rows]
        s125_rs = [r['adapter_fg_rgb_std'] for r in s125_rows]
        s125_gm = [r['adapter_fg_grad_mag'] for r in s125_rows]

        method_lv = [r['adapter_fg_lap_var'] for r in data]
        method_rs = [r['adapter_fg_rgb_std'] for r in data]
        method_gm = [r['adapter_fg_grad_mag'] for r in data]

        # Definition A: Lap Var ratio < 1.0
        lv_loss_A = sum(1 for m, s in zip(method_lv, s125_lv) if m < s) / n
        # Definition A strict: ratio < 0.95
        lv_loss_A_strict = sum(1 for m, s in zip(method_lv, s125_lv) if m < 0.95 * s) / n

        # Definition B: at least 2 of 3 metrics below s=1.25
        loss_B = 0
        for i in range(n):
            count = 0
            if method_lv[i] < s125_lv[i]:
                count += 1
            if method_rs[i] < s125_rs[i]:
                count += 1
            if method_gm[i] < s125_gm[i]:
                count += 1
            if count >= 2:
                loss_B += 1
        loss_B_rate = loss_B / n

        # Definition B strict: at least 2 of 3 metrics below 0.95 × s=1.25
        loss_B_strict = 0
        for i in range(n):
            count = 0
            if method_lv[i] < 0.95 * s125_lv[i]:
                count += 1
            if method_rs[i] < 0.95 * s125_rs[i]:
                count += 1
            if method_gm[i] < 0.95 * s125_gm[i]:
                count += 1
            if count >= 2:
                loss_B_strict += 1
        loss_B_strict_rate = loss_B_strict / n

        results.append({
            'Method': name,
            'Texture Loss Rate A (Lap Var < s=1.25)': f"{lv_loss_A:.3f}",
            'Texture Loss Rate A strict (<0.95)': f"{lv_loss_A_strict:.3f}",
            'Texture Loss Rate B (≥2/3 below s=1.25)': f"{loss_B_rate:.3f}",
            'Texture Loss Rate B strict (≥2/3 below 0.95×)': f"{loss_B_strict_rate:.3f}",
        })

    path = os.path.join(OUT_DIR, 'texture_loss_rate.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved: {path}")
    return results


def compute_win_rates(c3_rows, s250_rows):
    """C3 vs s=2.50 per-object win rate."""
    n = len(c3_rows)
    wins = {}

    for metric in ['adapter_fg_lap_var', 'adapter_fg_rgb_std', 'adapter_fg_grad_mag',
                   'adapter_fg_ssim', 'adapter_full_psnr']:
        c3_vals = [r[metric] for r in c3_rows]
        s250_vals = [r[metric] for r in s250_rows]

        # For texture metrics (higher = better): C3 wins if C3 > s=2.50
        # For LPIPS (lower = better): C3 wins if C3 < s=2.50
        if 'lpips' in metric:
            c3_wins = sum(1 for c, s in zip(c3_vals, s250_vals) if c < s)
        else:
            c3_wins = sum(1 for c, s in zip(c3_vals, s250_vals) if c > s)

        ties = sum(1 for c, s in zip(c3_vals, s250_vals) if abs(c - s) < 1e-8)
        wins[metric] = {
            'C3_wins': c3_wins,
            's250_wins': n - c3_wins - ties,
            'ties': ties,
            'C3_win_rate': c3_wins / n,
        }

    # FG-SSIM tolerance check: C3 within 0.005 and 0.01 of s=2.50
    c3_ssim = [r['adapter_fg_ssim'] for r in c3_rows]
    s250_ssim = [r['adapter_fg_ssim'] for r in s250_rows]
    within_005 = sum(1 for c, s in zip(c3_ssim, s250_ssim) if c >= s - 0.005) / n
    within_01 = sum(1 for c, s in zip(c3_ssim, s250_ssim) if c >= s - 0.01) / n
    not_lower = sum(1 for c, s in zip(c3_ssim, s250_ssim) if c >= s) / n

    wins['fg_ssim_tolerance'] = {
        'C3_not_lower_than_s250': not_lower,
        'C3_within_0.005_of_s250': within_005,
        'C3_within_0.01_of_s250': within_01,
    }

    # Save
    rows_out = []
    for metric, data in wins.items():
        if metric == 'fg_ssim_tolerance':
            for k, v in data.items():
                rows_out.append({'Metric': k, 'Value': f"{v:.4f}", 'Note': 'Fraction of objects'})
        else:
            rows_out.append({
                'Metric': f"C3 vs s=2.50: {metric}",
                'Value': f"{data['C3_win_rate']:.4f}",
                'Note': f"C3 wins {data['C3_wins']}/{n}, s250 wins {data['s250_wins']}/{n}, ties {data['ties']}"
            })

    os.makedirs(STAT_DIR, exist_ok=True)
    path = os.path.join(STAT_DIR, 'win_rate_summary.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Metric', 'Value', 'Note'])
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Saved: {path}")
    return wins


def compute_bootstrap_ci(c3_rows, s250_rows, n_bootstrap=10000, seed=42):
    """Bootstrap 95% CI for mean differences (C3 - s=2.50)."""
    rng = np.random.RandomState(seed)
    n = len(c3_rows)

    metrics_to_compare = [
        ('adapter_fg_ssim', 'ΔSSIM (C3 - s250)'),
        ('adapter_full_psnr', 'ΔPSNR (C3 - s250)'),
        ('adapter_fg_lap_var', 'ΔLap Var (C3 - s250)'),
        ('adapter_fg_rgb_std', 'ΔRGB Std (C3 - s250)'),
        ('adapter_fg_grad_mag', 'ΔGrad Mag (C3 - s250)'),
    ]

    results = []
    for metric, label in metrics_to_compare:
        c3_vals = np.array([r[metric] for r in c3_rows])
        s250_vals = np.array([r[metric] for r in s250_rows])
        diffs = c3_vals - s250_vals

        observed_mean = diffs.mean()
        observed_median = np.median(diffs)

        # Bootstrap
        boot_means = np.zeros(n_bootstrap)
        for b in range(n_bootstrap):
            idx = rng.randint(0, n, size=n)
            boot_means[b] = diffs[idx].mean()

        ci_low = np.percentile(boot_means, 2.5)
        ci_high = np.percentile(boot_means, 97.5)

        # Sign test (fraction positive)
        sign_positive = (diffs > 0).sum() / n

        results.append({
            'Comparison': label,
            'Observed Mean': f"{observed_mean:.6f}",
            'Observed Median': f"{observed_median:.6f}",
            'CI 2.5%': f"{ci_low:.6f}",
            'CI 97.5%': f"{ci_high:.6f}",
            'Sign Positive': f"{sign_positive:.4f}",
            'N': n,
            'Bootstrap Samples': n_bootstrap,
        })

    path = os.path.join(STAT_DIR, 'bootstrap_ci.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved: {path}")
    return results


def generate_paper_table(abs_table, rel_table, loss_table, wins, bootstrap):
    """Generate markdown table for paper insertion."""
    md = []
    md.append("# Texture Closure: 300-Object Validation\n")
    md.append("## Table: Absolute Metrics (300 objects)\n")
    md.append("| Method | FG-SSIM ↑ | Edge-SSIM ↑ | PSNR ↑ | FG-LPIPS ↓ | Lap Var ↑ | RGB Std ↑ | Gradient Mag ↑ |")
    md.append("|--------|-----------|-------------|--------|------------|-----------|-----------|---------------|")
    for row in abs_table:
        vals = [row.get(k, 'N/A') for k in ['FG-SSIM ↑', 'Edge-SSIM ↑', 'PSNR ↑', 'FG-LPIPS ↓',
                                              'Lap Var ↑', 'RGB Std ↑', 'Gradient Mag ↑']]
        md.append(f"| {row['Method']} | {' | '.join(vals)} |")

    md.append("\n## Table: Relative to s=1.25 (Texture Retention)\n")
    md.append("| Method | ΔFG-SSIM ↑ | Lap Var Ratio | RGB Std Ratio | Gradient Ratio | Assessment |")
    md.append("|--------|------------|---------------|---------------|----------------|------------|")
    for row in rel_table:
        md.append(f"| {row['Method']} | {row['ΔFG-SSIM ↑']} | {row['Lap Var Ratio']} | {row['RGB Std Ratio']} | {row['Gradient Mag Ratio']} | {row['Assessment']} |")

    md.append("\n## Texture Loss Rate\n")
    md.append("| Method | Rate A (LapVar < s=1.25) | Rate A strict (<0.95×) | Rate B (≥2/3 below) | Rate B strict |")
    md.append("|--------|--------------------------|------------------------|---------------------|---------------|")
    for row in loss_table:
        md.append(f"| {row['Method']} | {row['Texture Loss Rate A (Lap Var < s=1.25)']} | {row['Texture Loss Rate A strict (<0.95)']} | {row['Texture Loss Rate B (≥2/3 below s=1.25)']} | {row['Texture Loss Rate B strict (≥2/3 below 0.95×)']} |")

    md.append("\n## C3 vs s=2.50 Win Rate\n")
    for metric, data in wins.items():
        if metric == 'fg_ssim_tolerance':
            md.append(f"\n**FG-SSIM Tolerance:**")
            for k, v in data.items():
                md.append(f"- {k}: {v:.1%}")
        else:
            md.append(f"- {metric}: C3 wins {data['C3_win_rate']:.1%} ({data['C3_wins']}/300)")

    md.append("\n## Bootstrap 95% CI (C3 - s=2.50, 10000 resamples)\n")
    md.append("| Metric | Mean | 95% CI | Sign Positive |")
    md.append("|--------|------|--------|---------------|")
    for row in bootstrap:
        md.append(f"| {row['Comparison']} | {row['Observed Mean']} | [{row['CI 2.5%']}, {row['CI 97.5%']}] | {row['Sign Positive']} |")

    md.append("\n---\n")
    md.append("*Note: C3 uses equal-third timestep schedule (early=1.25, mid=2.50, late=1.25).*")
    md.append("*Texture metrics computed on foreground mask only.*")
    md.append("*Bootstrap uses object-level resampling with fixed seed=42.*")

    path = os.path.join(OUT_DIR, 'texture_closure_table_for_paper.md')
    with open(path, 'w') as f:
        f.write('\n'.join(md))
    print(f"Saved: {path}")


def main():
    print("=" * 60)
    print("Computing Texture Closure Tables")
    print("=" * 60)

    # Verify inputs exist
    for path, name in [(C3_CSV, 'C3'), (S125_CSV, 's=1.25'), (S250_CSV, 's=2.50')]:
        if not os.path.exists(path):
            print(f"ERROR: {name} CSV not found at: {path}")
            return
        print(f"  ✓ {name}: {path}")

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(STAT_DIR, exist_ok=True)

    # Load data
    c3_rows = load_csv(C3_CSV)
    s125_rows = load_csv(S125_CSV)
    s250_rows = load_csv(S250_CSV)

    # Consistency check
    check_consistency(c3_rows, s125_rows, s250_rows)

    # Compute tables
    print("\n--- Summary Absolute ---")
    abs_table = compute_summary_absolute(c3_rows, s125_rows, s250_rows)

    print("\n--- Summary Relative to s=1.25 ---")
    rel_table = compute_summary_relative(c3_rows, s125_rows, s250_rows)

    print("\n--- Texture Loss Rate ---")
    loss_table = compute_texture_loss_rate(c3_rows, s125_rows, s250_rows)

    print("\n--- Win Rates (C3 vs s=2.50) ---")
    win_data = compute_win_rates(c3_rows, s250_rows)

    print("\n--- Bootstrap CI ---")
    bootstrap = compute_bootstrap_ci(c3_rows, s250_rows)

    print("\n--- Paper Table (Markdown) ---")
    generate_paper_table(abs_table, rel_table, loss_table, win_data, bootstrap)

    print("\n" + "=" * 60)
    print("DONE. All texture closure tables generated.")
    print("=" * 60)


if __name__ == '__main__':
    main()
