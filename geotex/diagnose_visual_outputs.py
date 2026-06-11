"""Visual output diagnosis for GeoTex-RefAttn.

Traces image paths, computes statistics, verifies sources, checks baseline alignment.
Run after eval to validate that the pipeline produces correct outputs.

Usage:
    python geotex/diagnose_visual_outputs.py \
        --gt_dir /path/to/gt \
        --original_dir /path/to/original \
        --geotex_dir /path/to/geotex \
        --mask_dir /path/to/mask \
        --output_dir mvpoutput/geotex_refattn_v1/visual_diagnosis \
        --objects obj_000,obj_001,obj_002
"""
import os
import sys
import json
import csv
import argparse
import numpy as np
import torch
from PIL import Image
from pathlib import Path


def load_image(path):
    """Load image as float32 numpy array in [0, 1]."""
    img = Image.open(path).convert('RGB')
    return np.array(img).astype(np.float32) / 255.0


def load_mask(path):
    """Load mask as float32 numpy array in [0, 1]."""
    img = Image.open(path).convert('L')
    return np.array(img).astype(np.float32) / 255.0


def compute_image_stats(img, name="image"):
    """Compute comprehensive image statistics."""
    if img.ndim == 2:
        img = img[:, :, np.newaxis]

    h, w, c = img.shape
    total_pixels = h * w

    stats = {
        'name': name,
        'shape': f'{h}x{w}x{c}',
        'dtype': str(img.dtype),
        'min': float(img.min()),
        'max': float(img.max()),
        'mean': float(img.mean()),
        'std': float(img.std()),
    }

    # Per-channel stats
    for ch in range(min(c, 3)):
        ch_name = ['R', 'G', 'B'][ch]
        stats[f'{ch_name}_mean'] = float(img[:, :, ch].mean())
        stats[f'{ch_name}_std'] = float(img[:, :, ch].std())

    # Background/foreground ratios (assuming white bg)
    white_mask = (img[:, :, 0] > 0.95) & (img[:, :, 1] > 0.95) & (img[:, :, 2] > 0.95)
    stats['white_bg_ratio'] = float(white_mask.sum() / total_pixels)
    stats['fg_ratio'] = float(1.0 - white_mask.sum() / total_pixels)

    # Unique colors (sampled)
    flat = (img * 255).astype(np.uint8).reshape(-1, c)
    if len(flat) > 10000:
        indices = np.random.choice(len(flat), 10000, replace=False)
        flat = flat[indices]
    stats['unique_colors_sampled'] = int(len(np.unique(flat, axis=0)))

    return stats


def verify_image_source(img_path, expected_dir, label):
    """Verify image comes from expected directory."""
    img_path = os.path.realpath(img_path)
    expected_dir = os.path.realpath(expected_dir)
    if not img_path.startswith(expected_dir):
        return f"WARNING: {label} path {img_path} not under expected {expected_dir}"
    return None


def check_baseline_alignment(original_imgs, geotex_imgs, threshold=0.001):
    """Check if Original and GeoTex are from same eval run.

    At step 0 with zero-init adapter, GeoTex should be identical to Original.
    """
    diffs = []
    for orig, gtx in zip(original_imgs, geotex_imgs):
        diff = np.abs(orig - gtx).mean()
        diffs.append(diff)

    avg_diff = np.mean(diffs)
    if avg_diff > threshold:
        return f"WARNING: Original vs GeoTex avg diff={avg_diff:.6f} > {threshold}. May be from different runs."
    return None


def generate_contact_sheet(images, labels, output_path, title=""):
    """Generate a contact sheet with images and labels."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"matplotlib not available, skipping contact sheet: {output_path}")
        return

    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, img, label in zip(axes, images, labels):
        if img.ndim == 2:
            ax.imshow(img, cmap='gray')
        else:
            ax.imshow(img)
        ax.set_title(label, fontsize=10)
        ax.axis('off')

    if title:
        fig.suptitle(title, fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="GeoTex Visual Diagnosis")
    parser.add_argument('--gt_dir', required=True, help='GT images directory')
    parser.add_argument('--original_dir', required=True, help='Original baseline directory')
    parser.add_argument('--geotex_dir', required=True, help='GeoTex output directory')
    parser.add_argument('--mask_dir', default=None, help='Mask directory (optional)')
    parser.add_argument('--normal_dir', default=None, help='Normal map directory (optional)')
    parser.add_argument('--depth_dir', default=None, help='Depth map directory (optional)')
    parser.add_argument('--output_dir', required=True, help='Output directory for diagnosis')
    parser.add_argument('--objects', default=None, help='Comma-separated object names (default: auto-detect)')
    parser.add_argument('--views', default='000', help='Comma-separated view indices')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Auto-detect objects
    if args.objects:
        objects = args.objects.split(',')
    else:
        # Try to detect from gt_dir
        objects = sorted([d for d in os.listdir(args.gt_dir)
                         if os.path.isdir(os.path.join(args.gt_dir, d))])
        if not objects:
            # Maybe flat structure with obj_XXX prefix
            files = [f for f in os.listdir(args.gt_dir) if f.endswith('.png')]
            objects = sorted(set(f.rsplit('_', 1)[0] for f in files))

    views = args.views.split(',')
    print(f"Objects: {objects[:10]}...")
    print(f"Views: {views}")

    # Collect all stats
    all_stats = []
    all_warnings = []
    path_traces = []
    baseline_comparisons = []

    for obj in objects:
        for view in views:
            # Find image paths
            gt_path = find_image(args.gt_dir, obj, view, 'gt')
            orig_path = find_image(args.original_dir, obj, view, 'original')
            gtx_path = find_image(args.geotex_dir, obj, view, 'adapter')

            if gt_path is None or orig_path is None or gtx_path is None:
                print(f"SKIP {obj}/{view}: missing images (gt={gt_path}, orig={orig_path}, gtx={gtx_path})")
                continue

            # Path trace
            trace = {
                'object': obj,
                'view': view,
                'gt_path': gt_path,
                'original_path': orig_path,
                'geotex_path': gtx_path,
            }
            if args.mask_dir:
                mask_path = find_image(args.mask_dir, obj, view, 'mask')
                trace['mask_path'] = mask_path
            path_traces.append(trace)

            # Load images
            gt_img = load_image(gt_path)
            orig_img = load_image(orig_path)
            gtx_img = load_image(gtx_path)

            # Verify sources
            warn = verify_image_source(orig_path, args.original_dir, 'Original')
            if warn:
                all_warnings.append(warn)
            warn = verify_image_source(gtx_path, args.geotex_dir, 'GeoTex')
            if warn:
                all_warnings.append(warn)

            # Image stats
            for img, name in [(gt_img, 'GT'), (orig_img, 'Original'), (gtx_img, 'GeoTex')]:
                stats = compute_image_stats(img, f'{obj}/{view}/{name}')
                stats['object'] = obj
                stats['view'] = view
                all_stats.append(stats)

            # Baseline alignment
            warn = check_baseline_alignment([orig_img], [gtx_img])
            if warn:
                baseline_comparisons.append({'object': obj, 'view': view, 'warning': warn})

            # Generate contact sheet for this object/view
            images = [gt_img, orig_img, gtx_img]
            labels = ['GT', 'Original', 'GeoTex']

            # Add difference maps
            diff_orig = np.abs(gt_img - orig_img).mean(axis=2)
            diff_gtx = np.abs(gt_img - gtx_img).mean(axis=2)
            images.extend([diff_orig, diff_gtx])
            labels.extend(['Error:Orig', 'Error:GeoTex'])

            sheet_path = os.path.join(args.output_dir, f'{obj}_{view}_diagnosis.png')
            generate_contact_sheet(images, labels, sheet_path, title=f'{obj} view {view}')

    # Write outputs
    # 1. Path trace CSV
    csv_path = os.path.join(args.output_dir, 'image_path_trace.csv')
    if path_traces:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=path_traces[0].keys())
            writer.writeheader()
            writer.writerows(path_traces)
        print(f"Saved: {csv_path}")

    # 2. Image stats CSV
    csv_path = os.path.join(args.output_dir, 'image_stats.csv')
    if all_stats:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_stats[0].keys())
            writer.writeheader()
            writer.writerows(all_stats)
        print(f"Saved: {csv_path}")

    # 3. Baseline alignment metrics
    csv_path = os.path.join(args.output_dir, 'baseline_alignment_metrics.csv')
    if baseline_comparisons:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=baseline_comparisons[0].keys())
            writer.writeheader()
            writer.writerows(baseline_comparisons)
        print(f"Saved: {csv_path}")

    # 4. Audit report
    report_path = os.path.join(args.output_dir, 'visual_chain_audit.md')
    with open(report_path, 'w') as f:
        f.write("# Visual Chain Audit Report\n\n")
        f.write(f"**Objects:** {len(objects)}\n")
        f.write(f"**Views:** {views}\n\n")

        if all_warnings:
            f.write("## Warnings\n\n")
            for w in all_warnings:
                f.write(f"- {w}\n")
            f.write("\n")
        else:
            f.write("## Warnings\n\nNone ✓\n\n")

        if baseline_comparisons:
            f.write("## Baseline Alignment Issues\n\n")
            for bc in baseline_comparisons:
                f.write(f"- {bc['object']}/{bc['view']}: {bc['warning']}\n")
            f.write("\n")
        else:
            f.write("## Baseline Alignment\n\nAll checks passed ✓\n\n")

        # Summary stats
        if all_stats:
            f.write("## Image Statistics Summary\n\n")
            f.write("| Image | Mean | Std | FG Ratio | White BG |\n")
            f.write("|-------|------|-----|----------|----------|\n")
            for s in all_stats[:30]:  # First 30
                f.write(f"| {s['name']} | {s['mean']:.4f} | {s['std']:.4f} | {s['fg_ratio']:.4f} | {s['white_bg_ratio']:.4f} |\n")

    print(f"Saved: {report_path}")
    print(f"\nDiagnosis complete. {len(all_stats)} stats collected, {len(all_warnings)} warnings.")


def find_image(base_dir, obj, view, suffix=''):
    """Find image path with flexible naming conventions."""
    # Try: base_dir/obj/view.png
    path = os.path.join(base_dir, obj, f'{view}.png')
    if os.path.exists(path):
        return path

    # Try: base_dir/obj_suffix_view.png
    path = os.path.join(base_dir, f'{obj}_{suffix}_{view}.png')
    if os.path.exists(path):
        return path

    # Try: base_dir/obj_suffix.png (single view)
    path = os.path.join(base_dir, f'{obj}_{suffix}.png')
    if os.path.exists(path):
        return path

    # Try: base_dir/obj/view_suffix.png
    path = os.path.join(base_dir, obj, f'{view}_{suffix}.png')
    if os.path.exists(path):
        return path

    # Try: base_dir/obj_suffix_view.png (no leading zeros)
    path = os.path.join(base_dir, f'{obj}_{suffix}_{int(view):d}.png')
    if os.path.exists(path):
        return path

    return None


if __name__ == '__main__':
    main()
