"""Generate paper figures from 300-object eval results."""
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
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARNING: matplotlib not available. Install with: pip install matplotlib")


def load_per_object(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def fig_region_bar_chart(data, output_dir):
    """Bar chart: Original vs Adapter for FG/Edge PSNR/SSIM/LPIPS."""
    if not HAS_MPL:
        return

    regions = ['foreground', 'edge']
    metrics = ['psnr', 'ssim', 'lpips']
    labels = ['PSNR (dB)↑', 'SSIM↑', 'LPIPS↓']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for i, (metric, label) in enumerate(zip(metrics, labels)):
        ax = axes[i]
        x = np.arange(len(regions))
        width = 0.35

        orig_means = []
        adapter_means = []
        for region in regions:
            orig_key = f'{region}_orig_{metric}'
            adapter_key = f'{region}_adapter_{metric}'
            orig_vals = [float(r[orig_key]) for r in data if r.get(orig_key) and r[orig_key] != 'None']
            adapter_vals = [float(r[adapter_key]) for r in data if r.get(adapter_key) and r[adapter_key] != 'None']
            orig_means.append(np.mean(orig_vals) if orig_vals else 0)
            adapter_means.append(np.mean(adapter_vals) if adapter_vals else 0)

        bars1 = ax.bar(x - width/2, orig_means, width, label='Original', color='#4C72B0')
        bars2 = ax.bar(x + width/2, adapter_means, width, label='GeoTex', color='#DD8452')

        ax.set_xlabel('Region')
        ax.set_ylabel(label)
        ax.set_title(f'{label.split(" ")[0]} by Region')
        ax.set_xticks(x)
        ax.set_xticklabels(['Foreground', 'Edge'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'main_bar_region_metrics.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def fig_delta_scatter(data, output_dir):
    """Scatter plot: per-object ΔFG PSNR vs ΔFG SSIM."""
    if not HAS_MPL:
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    fg_psnr_orig = [float(r.get('foreground_orig_psnr', 0)) for r in data]
    fg_psnr_adapt = [float(r.get('foreground_adapter_psnr', 0)) for r in data]
    fg_ssim_orig = [float(r.get('foreground_orig_ssim', 0)) for r in data]
    fg_ssim_adapt = [float(r.get('foreground_adapter_ssim', 0)) for r in data]

    delta_psnr = [a - o for a, o in zip(fg_psnr_adapt, fg_psnr_orig)]
    delta_ssim = [a - o for a, o in zip(fg_ssim_adapt, fg_ssim_orig)]

    colors = ['#2ecc71' if dp > 0 and ds > 0 else '#e74c3c' for dp, ds in zip(delta_psnr, delta_ssim)]

    ax.scatter(delta_psnr, delta_ssim, c=colors, alpha=0.6, s=30)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Δ Foreground PSNR (dB)')
    ax.set_ylabel('Δ Foreground SSIM')
    ax.set_title('Per-Object Foreground Improvement (Green=both improved, Red=regression)')

    improved_both = sum(1 for dp, ds in zip(delta_psnr, delta_ssim) if dp > 0 and ds > 0)
    ax.text(0.05, 0.95, f'{improved_both}/{len(data)} improved on both',
            transform=ax.transAxes, fontsize=12, verticalalignment='top')

    plt.tight_layout()
    path = os.path.join(output_dir, 'per_object_delta_scatter.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def fig_lpips_histogram(data, output_dir):
    """Histogram of LPIPS deltas for foreground and edge."""
    if not HAS_MPL:
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for i, region in enumerate(['foreground', 'edge']):
        ax = axes[i]
        orig_key = f'{region}_orig_lpips'
        adapt_key = f'{region}_adapter_lpips'
        deltas = []
        for r in data:
            o = r.get(orig_key)
            a = r.get(adapt_key)
            if o and a and o != 'None' and a != 'None':
                deltas.append(float(a) - float(o))

        ax.hist(deltas, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
        improved = sum(1 for d in deltas if d < 0)
        ax.set_title(f'{region.capitalize()} LPIPS Δ (↓=better, {improved}/{len(deltas)} improved)')
        ax.set_xlabel('Δ LPIPS')
        ax.set_ylabel('Count')

    plt.tight_layout()
    path = os.path.join(output_dir, 'lpips_delta_histogram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def fig_improvement_table(data, output_dir):
    """Improvement rate table as markdown."""
    regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
    metrics = ['psnr', 'ssim', 'lpips']

    lines = ['# Improvement Rate Table\n\n']
    lines.append('| Region | Metric | Improved | Total | Rate |\n')
    lines.append('|--------|--------|----------|-------|------|\n')

    for region in regions:
        for metric in metrics:
            higher = metric != 'lpips'
            orig_key = f'{region}_orig_{metric}'
            adapt_key = f'{region}_adapter_{metric}'
            improved = 0
            total = 0
            for r in data:
                o = r.get(orig_key)
                a = r.get(adapt_key)
                if o and a and o != 'None' and a != 'None':
                    total += 1
                    diff = float(a) - float(o)
                    if (higher and diff > 0) or (not higher and diff < 0):
                        improved += 1
            rate = improved / total * 100 if total > 0 else 0
            lines.append(f'| {region} | {metric.upper()} | {improved} | {total} | {rate:.0f}% |\n')

    path = os.path.join(output_dir, 'improvement_rate_table.md')
    with open(path, 'w') as f:
        f.write(''.join(lines))
    print(f"Saved: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='mvpoutput/geotex/eval_300obj_region')
    parser.add_argument('--output_dir', default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join(args.input_dir, 'paper_figures')
    os.makedirs(args.output_dir, exist_ok=True)

    csv_path = os.path.join(args.input_dir, 'per_object_metrics.csv')
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found")
        return

    data = load_per_object(csv_path)
    print(f"Loaded {len(data)} objects")

    fig_region_bar_chart(data, args.output_dir)
    fig_delta_scatter(data, args.output_dir)
    fig_lpips_histogram(data, args.output_dir)
    fig_improvement_table(data, args.output_dir)

    # Figure captions
    captions = [
        '# Figure Caption Drafts\n',
        '## main_bar_region_metrics.png',
        'Comparison of Original MV-Painter vs GeoTex-Adapter on foreground and edge regions.',
        'GeoTex improves PSNR, SSIM, and LPIPS on both regions.\n',
        '## per_object_delta_scatter.png',
        'Per-object scatter of Δ Foreground PSNR vs Δ Foreground SSIM.',
        'Green dots = objects improved on both metrics. Red = regression on at least one.\n',
        '## lpips_delta_histogram.png',
        'Distribution of LPIPS delta (lower is better) for foreground and edge regions.',
        'Most objects show negative delta (improvement).\n',
        '## improvement_rate_table.md',
        'Tabular improvement rates across all regions and metrics.\n',
    ]
    cap_path = os.path.join(args.output_dir, 'figure_caption_drafts.md')
    with open(cap_path, 'w') as f:
        f.write('\n'.join(captions))
    print(f"Saved: {cap_path}")

    print("\nDone!")


if __name__ == '__main__':
    main()
