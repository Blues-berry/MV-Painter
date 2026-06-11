"""Analyze 300-object eval results: delta distributions, scatter plots, worst/best cases.

Usage:
    python geotex/analyze_300obj_results.py \
        --metrics_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean \
        --output_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean/analysis
"""
import os
import sys
import json
import csv
import argparse
import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARNING: matplotlib not available, skipping plots")


def load_per_object_metrics(csv_path):
    """Load per_object_metrics.csv into list of dicts."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            # Convert numeric fields
            for k, v in row.items():
                try:
                    row[k] = float(v)
                except (ValueError, TypeError):
                    pass
            rows.append(row)
    return rows


def compute_deltas(rows):
    """Compute adapter - original deltas for all metrics."""
    regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
    metrics = ['psnr', 'ssim', 'lpips']
    deltas = []
    for r in rows:
        d = {'object_idx': int(r['object_idx'])}
        for reg in regions:
            for met in metrics:
                orig_key = f'{reg}_orig_{met}'
                adapter_key = f'{reg}_adapter_{met}'
                if orig_key in r and adapter_key in r:
                    o = r[orig_key]
                    a = r[adapter_key]
                    if o is not None and a is not None:
                        d[f'{reg}_delta_{met}'] = a - o
                        d[f'{reg}_orig_{met}'] = o
                        d[f'{reg}_adapter_{met}'] = a
        # Also carry fg_ratio for analysis
        if 'fg_ratio' in r:
            d['fg_ratio'] = r['fg_ratio']
        deltas.append(d)
    return deltas


def print_summary(deltas):
    """Print summary statistics."""
    regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
    metrics = ['psnr', 'ssim', 'lpips']

    print(f"\n{'='*80}")
    print(f"300-OBJECT EVAL SUMMARY ({len(deltas)} objects)")
    print(f"{'='*80}")

    for reg in regions:
        print(f"\n  {reg.upper()}:")
        for met in metrics:
            key = f'{reg}_delta_{met}'
            vals = [d[key] for d in deltas if key in d and d[key] is not None]
            if not vals:
                continue
            arr = np.array(vals)
            improved = np.sum(arr > 0) if met != 'lpips' else np.sum(arr < 0)
            better = '↑' if met != 'lpips' else '↓'
            print(f"    {met.upper():6s}: mean={arr.mean():+.4f} std={arr.std():.4f} "
                  f"median={np.median(arr):+.4f} [{improved}/{len(arr)} {better}]")

    # Go/No-Go check
    print(f"\n{'='*80}")
    print("GO/NO-GO CRITERIA:")
    print(f"{'='*80}")

    fpnr_key = 'full_delta_psnr'
    flpips_key = 'full_delta_lpips'
    fgpnr_key = 'foreground_delta_psnr'
    fgssim_key = 'foreground_delta_ssim'
    essim_key = 'edge_delta_ssim'

    fpnr_vals = [d[fpnr_key] for d in deltas if fpnr_key in d]
    flpips_vals = [d[flpips_key] for d in deltas if flpips_key in d]
    fgpnr_vals = [d[fgpnr_key] for d in deltas if fgpnr_key in d]
    fgssim_vals = [d[fgssim_key] for d in deltas if fgssim_key in d]
    essim_vals = [d[essim_key] for d in deltas if essim_key in d]

    checks = []
    if fpnr_vals:
        mean_fpnr = np.mean(fpnr_vals)
        ok = mean_fpnr >= 1.0
        checks.append(('Full PSNR delta ≥ +1 dB', ok, f'{mean_fpnr:+.2f} dB'))
    if flpips_vals:
        mean_flpips = np.mean(flpips_vals)
        ok = mean_flpips < 0
        checks.append(('LPIPS decrease', ok, f'{mean_flpips:+.4f}'))
    if fgpnr_vals:
        mean_fgpnr = np.mean(fgpnr_vals)
        ok = mean_fgpnr > 0
        checks.append(('FG PSNR positive', ok, f'{mean_fgpnr:+.2f} dB'))
    if fgssim_vals:
        mean_fgssim = np.mean(fgssim_vals)
        ok = mean_fgssim > 0
        checks.append(('FG SSIM positive', ok, f'{mean_fgssim:+.4f}'))
    if essim_vals:
        mean_essim = np.mean(essim_vals)
        ok = mean_essim > 0
        checks.append(('Edge SSIM positive', ok, f'{mean_essim:+.4f}'))

    # Count positive objects
    if fpnr_vals:
        positive_ratio = np.sum(np.array(fpnr_vals) > 0) / len(fpnr_vals)
        ok = positive_ratio >= 0.65
        checks.append(('≥65% objects positive Full PSNR', ok, f'{positive_ratio:.1%}'))

    passed = sum(1 for _, ok, _ in checks if ok)
    for name, ok, val in checks:
        status = '✅' if ok else '❌'
        print(f"  {status} {name}: {val}")
    print(f"\n  Result: {passed}/{len(checks)} passed")
    if passed >= 2:
        print("  → GO: Continue GeoTex experiments")
    else:
        print("  → NO-GO: Debug before proceeding")


def find_worst_best(deltas, n=20):
    """Find worst-N and best-N objects by Full PSNR delta."""
    key = 'full_delta_psnr'
    valid = [(d['object_idx'], d[key]) for d in deltas if key in d and d[key] is not None]
    valid.sort(key=lambda x: x[1])

    worst = valid[:n]
    best = valid[-n:]

    return worst, best


def find_regression_cases(deltas, threshold=-0.5):
    """Find objects where adapter is significantly worse."""
    key = 'full_delta_psnr'
    regressions = [(d['object_idx'], d[key]) for d in deltas
                   if key in d and d[key] is not None and d[key] < threshold]
    regressions.sort(key=lambda x: x[1])
    return regressions


def analyze_by_fg_ratio(deltas):
    """Check if improvement correlates with foreground ratio."""
    fpnr_key = 'full_delta_psnr'
    fg_key = 'fg_ratio'
    pairs = [(d[fg_key], d[fpnr_key]) for d in deltas
             if fg_key in d and fpnr_key in d and d[fg_key] is not None and d[fpnr_key] is not None]
    if not pairs:
        return None
    fg_ratios, fpnr_deltas = zip(*pairs)
    corr = np.corrcoef(fg_ratios, fpnr_deltas)[0, 1]
    return {'correlation': float(corr), 'n': len(pairs)}


def make_plots(deltas, output_dir):
    """Generate analysis plots."""
    if not HAS_MPL:
        print("Skipping plots (matplotlib not available)")
        return

    os.makedirs(output_dir, exist_ok=True)

    # 1. Per-object delta PSNR scatter
    fpnr_vals = [(d['object_idx'], d.get('full_delta_psnr')) for d in deltas
                 if d.get('full_delta_psnr') is not None]
    if fpnr_vals:
        idx, vals = zip(*fpnr_vals)
        fig, ax = plt.subplots(figsize=(12, 5))
        colors = ['green' if v > 0 else 'red' for v in vals]
        ax.scatter(range(len(vals)), vals, c=colors, s=8, alpha=0.6)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        ax.axhline(y=np.mean(vals), color='blue', linestyle='-', linewidth=1, label=f'Mean: {np.mean(vals):+.2f}')
        ax.set_xlabel('Object Index (sorted by delta)')
        ax.set_ylabel('Full PSNR Delta (dB)')
        ax.set_title('Per-Object Full PSNR Delta: GeoTex vs Official')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'delta_psnr_scatter.png'), dpi=150)
        plt.close()

    # 2. Per-object delta LPIPS scatter
    flpips_vals = [(d['object_idx'], d.get('full_delta_lpips')) for d in deltas
                   if d.get('full_delta_lpips') is not None]
    if flpips_vals:
        idx, vals = zip(*flpips_vals)
        fig, ax = plt.subplots(figsize=(12, 5))
        colors = ['green' if v < 0 else 'red' for v in vals]
        ax.scatter(range(len(vals)), vals, c=colors, s=8, alpha=0.6)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        ax.axhline(y=np.mean(vals), color='blue', linestyle='-', linewidth=1, label=f'Mean: {np.mean(vals):+.4f}')
        ax.set_xlabel('Object Index (sorted by delta)')
        ax.set_ylabel('Full LPIPS Delta')
        ax.set_title('Per-Object Full LPIPS Delta: GeoTex vs Official')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'delta_lpips_scatter.png'), dpi=150)
        plt.close()

    # 3. FG delta vs Full delta
    fg_psnr = [d.get('foreground_delta_psnr') for d in deltas]
    full_psnr = [d.get('full_delta_psnr') for d in deltas]
    pairs = [(f, fu) for f, fu in zip(fg_psnr, full_psnr) if f is not None and fu is not None]
    if pairs:
        fg, fu = zip(*pairs)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(fu, fg, s=8, alpha=0.5)
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5)
        lim = max(abs(min(fg + fu)), abs(max(fg + fu))) * 1.1
        ax.plot([-lim, lim], [-lim, lim], 'k--', linewidth=0.5, alpha=0.3)
        ax.set_xlabel('Full PSNR Delta (dB)')
        ax.set_ylabel('FG PSNR Delta (dB)')
        ax.set_title('FG PSNR Delta vs Full PSNR Delta')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'fg_vs_full_delta.png'), dpi=150)
        plt.close()

    # 4. Edge SSIM delta distribution
    essim_vals = [d.get('edge_delta_ssim') for d in deltas if d.get('edge_delta_ssim') is not None]
    if essim_vals:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(essim_vals, bins=50, color='steelblue', edgecolor='black', linewidth=0.3)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
        ax.axvline(x=np.mean(essim_vals), color='blue', linestyle='-', linewidth=1,
                   label=f'Mean: {np.mean(essim_vals):+.4f}')
        ax.set_xlabel('Edge SSIM Delta')
        ax.set_ylabel('Count')
        ax.set_title('Edge SSIM Delta Distribution')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'edge_ssim_distribution.png'), dpi=150)
        plt.close()

    # 5. Full PSNR delta distribution
    fpnr_arr = [v for _, v in fpnr_vals] if fpnr_vals else []
    if fpnr_arr:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(fpnr_arr, bins=50, color='steelblue', edgecolor='black', linewidth=0.3)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
        ax.axvline(x=np.mean(fpnr_arr), color='blue', linestyle='-', linewidth=1,
                   label=f'Mean: {np.mean(fpnr_arr):+.2f}')
        ax.set_xlabel('Full PSNR Delta (dB)')
        ax.set_ylabel('Count')
        ax.set_title('Full PSNR Delta Distribution')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'full_psnr_distribution.png'), dpi=150)
        plt.close()

    # 6. Region comparison bar chart
    regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
    metric = 'psnr'
    means = []
    for reg in regions:
        key = f'{reg}_delta_{metric}'
        vals = [d[key] for d in deltas if key in d and d[key] is not None]
        means.append(np.mean(vals) if vals else 0)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['green' if m > 0 else 'red' for m in means]
    ax.bar(regions, means, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_ylabel(f'{metric.upper()} Delta')
    ax.set_title(f'Region {metric.upper()} Delta Comparison')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'region_{metric}_comparison.png'), dpi=150)
    plt.close()

    print(f"Plots saved to {output_dir}")


def write_analysis_report(deltas, worst, best, regressions, fg_corr, output_dir):
    """Write analysis report markdown."""
    report_path = os.path.join(output_dir, 'performance_analysis.md')
    os.makedirs(output_dir, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("# Performance Analysis: GeoTex RefAttn v1 (300 objects)\n\n")
        f.write(f"**Date:** 2026-06-10\n")
        f.write(f"**Objects:** {len(deltas)}\n\n")

        f.write("## 1. Is GeoTex average improvement or few-object pull-up?\n\n")
        fpnr_vals = [d.get('full_delta_psnr') for d in deltas if d.get('full_delta_psnr') is not None]
        if fpnr_vals:
            arr = np.array(fpnr_vals)
            f.write(f"- Mean delta: {arr.mean():+.2f} dB\n")
            f.write(f"- Median delta: {np.median(arr):+.2f} dB\n")
            f.write(f"- Std: {arr.std():.2f} dB\n")
            f.write(f"- Positive: {np.sum(arr > 0)}/{len(arr)} ({np.sum(arr > 0)/len(arr):.1%})\n")
            f.write(f"- >+1 dB: {np.sum(arr > 1)}/{len(arr)} ({np.sum(arr > 1)/len(arr):.1%})\n")
            f.write(f"- >+3 dB: {np.sum(arr > 3)}/{len(arr)} ({np.sum(arr > 3)/len(arr):.1%})\n")
            f.write(f"- >+5 dB: {np.sum(arr > 5)}/{len(arr)} ({np.sum(arr > 5)/len(arr):.1%})\n")
            f.write(f"- <-1 dB: {np.sum(arr < -1)}/{len(arr)} ({np.sum(arr < -1)/len(arr):.1%})\n")

            if np.median(arr) > 0 and np.sum(arr > 0) / len(arr) > 0.5:
                f.write("\n**Conclusion:** Improvement is broadly distributed, not from few objects.\n")
            elif np.sum(arr > 5) > 0 and np.median(arr) < 1:
                f.write("\n**Conclusion:** Improvement is concentrated in few objects (potential pull-up).\n")
            else:
                f.write("\n**Conclusion:** Mixed pattern — need further analysis.\n")

        f.write("\n## 2. Which region benefits most?\n\n")
        regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
        for metric in ['psnr', 'ssim', 'lpips']:
            f.write(f"\n### {metric.upper()} Delta\n\n")
            f.write("| Region | Mean | Median | Positive |\n")
            f.write("|--------|------|--------|----------|\n")
            for reg in regions:
                key = f'{reg}_delta_{metric}'
                vals = [d[key] for d in deltas if key in d and d[key] is not None]
                if vals:
                    arr = np.array(vals)
                    pos = np.sum(arr > 0) if metric != 'lpips' else np.sum(arr < 0)
                    f.write(f"| {reg} | {arr.mean():+.4f} | {np.median(arr):+.4f} | {pos}/{len(arr)} |\n")

        f.write("\n## 3. Regression cases\n\n")
        f.write(f"Objects with Full PSNR delta < -0.5 dB: {len(regressions)}\n\n")
        if regressions:
            f.write("| Object | Full PSNR Delta |\n")
            f.write("|--------|----------------|\n")
            for obj_idx, delta in regressions[:20]:
                f.write(f"| {obj_idx} | {delta:+.2f} dB |\n")

        f.write("\n## 4. Best / Worst cases\n\n")
        f.write("### Best 10\n\n")
        f.write("| Object | Full PSNR Delta |\n")
        f.write("|--------|----------------|\n")
        for obj_idx, delta in best[-10:]:
            f.write(f"| {obj_idx} | {delta:+.2f} dB |\n")

        f.write("\n### Worst 10\n\n")
        f.write("| Object | Full PSNR Delta |\n")
        f.write("|--------|----------------|\n")
        for obj_idx, delta in worst[:10]:
            f.write(f"| {obj_idx} | {delta:+.2f} dB |\n")

        f.write("\n## 5. FG ratio correlation\n\n")
        if fg_corr:
            f.write(f"- Pearson correlation (fg_ratio, full_psnr_delta): {fg_corr['correlation']:.4f}\n")
            f.write(f"- N: {fg_corr['n']}\n")
            if abs(fg_corr['correlation']) > 0.3:
                f.write("- **Significant correlation** — improvement may depend on foreground ratio\n")
            else:
                f.write("- No strong correlation — improvement is not driven by fg ratio alone\n")

    print(f"Analysis report: {report_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--metrics_dir', required=True)
    parser.add_argument('--output_dir', default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join(args.metrics_dir, 'analysis')

    csv_path = os.path.join(args.metrics_dir, 'per_object_metrics.csv')
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found")
        sys.exit(1)

    rows = load_per_object_metrics(csv_path)
    deltas = compute_deltas(rows)

    print_summary(deltas)

    worst, best = find_worst_best(deltas, n=20)
    regressions = find_regression_cases(deltas, threshold=-0.5)
    fg_corr = analyze_by_fg_ratio(deltas)

    make_plots(deltas, args.output_dir)
    write_analysis_report(deltas, worst, best, regressions, fg_corr, args.output_dir)

    # Save structured results
    results = {
        'num_objects': len(deltas),
        'worst_20': worst,
        'best_20': best,
        'regressions': regressions,
        'fg_ratio_correlation': fg_corr,
    }
    results_path = os.path.join(args.output_dir, 'analysis_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results: {results_path}")


if __name__ == '__main__':
    main()
