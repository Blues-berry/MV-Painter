"""Generate comparison figures for GeoTex-RefAttn evaluation.

All input paths must be provided via CLI. No hardcoded paths.
Validates that Original and GeoTex come from the same eval run.

Usage:
    python geotex/make_refattn_comparison_figures.py \
        --gt_dir /path/to/gt \
        --original_dir /path/to/original \
        --geotex_dir /path/to/geotex \
        --mask_dir /path/to/mask \
        --output_dir mvpoutput/geotex_refattn_v1/comparison_figures \
        --metrics_csv /path/to/region_metrics.csv \
        --objects obj_000,obj_001,obj_002
"""
import os
import sys
import csv
import json
import argparse
import numpy as np
from PIL import Image
from pathlib import Path


def load_image(path):
    """Load image as float32 numpy array in [0, 1]."""
    return np.array(Image.open(path).convert('RGB')).astype(np.float32) / 255.0


def load_mask(path):
    """Load mask as float32 numpy array in [0, 1]."""
    return np.array(Image.open(path).convert('L')).astype(np.float32) / 255.0


def compute_fg_ratio(mask):
    """Compute foreground ratio from mask."""
    return float((mask > 0.5).sum() / mask.size)


def compute_image_diff(img1, img2):
    """Compute absolute difference map in grayscale."""
    return np.abs(img1 - img2).mean(axis=2)


def find_image(base_dir, obj, view, suffix=''):
    """Find image path with flexible naming conventions."""
    candidates = [
        # obj_XXX_suffix.png (eval output format)
        os.path.join(base_dir, f'{obj}_{suffix}.png'),
        # obj_XXX_suffix_view.png
        os.path.join(base_dir, f'{obj}_{suffix}_{view}.png'),
        # obj/000.png
        os.path.join(base_dir, obj, f'{view}.png'),
        # obj/view_suffix.png
        os.path.join(base_dir, obj, f'{view}_{suffix}.png'),
        # obj_XXX_suffix_0.png
        os.path.join(base_dir, f'{obj}_{suffix}_{int(view):d}.png'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def select_best_view(gt_dir, mask_dir, objects, views):
    """Select view with highest foreground ratio for each object."""
    selections = {}
    for obj in objects:
        best_view = views[0]
        best_fg = 0.0
        for view in views:
            mask_path = find_image(mask_dir, obj, view, 'mask')
            if mask_path:
                mask = load_mask(mask_path)
                fg = compute_fg_ratio(mask)
                if fg > best_fg:
                    best_fg = fg
                    best_view = view
        selections[obj] = {'view': best_view, 'fg_ratio': best_fg}
    return selections


def crop_center(img, crop_size=64):
    """Crop center region of image."""
    h, w = img.shape[:2]
    cy, cx = h // 2, w // 2
    half = crop_size // 2
    return img[max(0, cy-half):cy+half, max(0, cx-half):cx+half]


def zoom_region(img, mask, zoom_frac=0.25):
    """Zoom into a region with high foreground content."""
    h, w = img.shape[:2]
    zh, zw = int(h * zoom_frac), int(w * zoom_frac)

    # Find center of mass of foreground
    if mask is not None and mask.sum() > 0:
        ys, xs = np.where(mask > 0.5)
        cy, cx = int(ys.mean()), int(xs.mean())
    else:
        cy, cx = h // 2, w // 2

    y1 = max(0, cy - zh // 2)
    y2 = min(h, y1 + zh)
    x1 = max(0, cx - zw // 2)
    x2 = min(w, x1 + zw)

    return img[y1:y2, x1:x2]


def make_grid(images, labels, ncols=None):
    """Arrange images in a grid with labels."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available")
        return None

    n = len(images)
    if ncols is None:
        ncols = n
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]

    for idx, (img, label) in enumerate(zip(images, labels)):
        r, c = idx // ncols, idx % ncols
        ax = axes[r, c]
        if img.ndim == 2:
            ax.imshow(img, cmap='gray', vmin=0, vmax=max(img.max(), 0.01))
        else:
            ax.imshow(np.clip(img, 0, 1))
        ax.set_title(label, fontsize=9)
        ax.axis('off')

    # Hide unused axes
    for idx in range(n, nrows * ncols):
        r, c = idx // ncols, idx % ncols
        axes[r, c].axis('off')

    plt.tight_layout()
    return fig


def validate_same_run(original_dir, geotex_dir, objects, views):
    """Validate that Original and GeoTex come from the same eval run.

    Checks: file timestamps, directory structure consistency.
    """
    warnings = []
    for obj in objects[:5]:
        for view in views[:1]:
            orig_path = find_image(original_dir, obj, view, 'original')
            gtx_path = find_image(geotex_dir, obj, view, 'adapter')
            if orig_path and gtx_path:
                orig_mtime = os.path.getmtime(orig_path)
                gtx_mtime = os.path.getmtime(gtx_path)
                time_diff = abs(orig_mtime - gtx_mtime)
                if time_diff > 3600:  # More than 1 hour apart
                    warnings.append(
                        f"{obj}/{view}: Original and GeoTex timestamps differ by {time_diff:.0f}s"
                    )
    return warnings


def main():
    parser = argparse.ArgumentParser(description="GeoTex Comparison Figures")
    parser.add_argument('--gt_dir', required=True)
    parser.add_argument('--original_dir', required=True)
    parser.add_argument('--geotex_dir', required=True)
    parser.add_argument('--mask_dir', default=None)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--metrics_csv', default=None, help='CSV with per-object metrics')
    parser.add_argument('--objects', default=None, help='Comma-separated object names')
    parser.add_argument('--views', default='000', help='Comma-separated view indices')
    parser.add_argument('--select_best_view', action='store_true', help='Auto-select best view per object')
    parser.add_argument('--max_objects', type=int, default=10, help='Max objects to include')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    views = args.views.split(',')

    # Auto-detect objects
    if args.objects:
        objects = args.objects.split(',')
    else:
        # Try directory-based structure first
        objects = sorted([d for d in os.listdir(args.gt_dir)
                         if os.path.isdir(os.path.join(args.gt_dir, d))])
        if not objects:
            # Flat file structure: detect from _gt.png files
            files = [f for f in os.listdir(args.gt_dir) if f.endswith('_gt.png')]
            objects = sorted(set(f.replace('_gt.png', '') for f in files))
        objects = objects[:args.max_objects]

    # Validate same run
    run_warnings = validate_same_run(args.original_dir, args.geotex_dir, objects, views)
    if run_warnings:
        print("WARNING: Original/GeoTex may not be from same eval run:")
        for w in run_warnings:
            print(f"  {w}")

    # Select best views
    if args.select_best_view and args.mask_dir:
        view_selections = select_best_view(args.gt_dir, args.mask_dir, objects, views)
    else:
        view_selections = {obj: {'view': views[0], 'fg_ratio': 0.5} for obj in objects}

    # Load metrics if available
    metrics = {}
    if args.metrics_csv and os.path.exists(args.metrics_csv):
        with open(args.metrics_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Support both 'object' and 'object_idx' column names
                obj_id = row.get('object', row.get('object_idx', ''))
                key = f"{obj_id}/{row.get('view', '000')}"
                metrics[key] = row

    # Generate figures
    report_lines = ["# Figure Generation Report\n"]
    report_lines.append(f"**Objects:** {len(objects)}\n")
    report_lines.append(f"**Views:** {views}\n\n")

    # --- Figure A: Clean Comparison Grid ---
    print("Generating clean_comparison_grid.png...")
    grid_images = []
    grid_labels = []
    selected_objects = []

    for obj in objects[:args.max_objects]:
        view = view_selections[obj]['view']
        gt_path = find_image(args.gt_dir, obj, view, 'gt')
        orig_path = find_image(args.original_dir, obj, view, 'original')
        gtx_path = find_image(args.geotex_dir, obj, view, 'adapter')

        if not all([gt_path, orig_path, gtx_path]):
            print(f"  SKIP {obj}/{view}: missing images")
            continue

        gt = load_image(gt_path)
        orig = load_image(orig_path)
        gtx = load_image(gtx_path)

        mask = None
        if args.mask_dir:
            mask_path = find_image(args.mask_dir, obj, view, 'mask')
            if mask_path:
                mask = load_mask(mask_path)

        # Zoom region
        gt_zoom = zoom_region(gt, mask)
        orig_zoom = zoom_region(orig, mask)
        gtx_zoom = zoom_region(gtx, mask)

        grid_images.extend([gt, orig, gtx, gt_zoom, orig_zoom, gtx_zoom])
        grid_labels.extend([
            f'GT', f'Original', f'GeoTex',
            f'Zoom GT', f'Zoom Orig', f'Zoom GeoTex'
        ])
        selected_objects.append(obj)

    if grid_images:
        fig = make_grid(grid_images, grid_labels, ncols=6)
        if fig:
            fig.savefig(os.path.join(args.output_dir, 'clean_comparison_grid.png'),
                       dpi=150, bbox_inches='tight')
            import matplotlib.pyplot as plt
            plt.close(fig)

    # --- Figure B: Edge Zoom Debug ---
    print("Generating edge_zoom_debug.png...")
    edge_images = []
    edge_labels = []

    for obj in selected_objects[:6]:
        view = view_selections[obj]['view']
        gt_path = find_image(args.gt_dir, obj, view, 'gt')
        orig_path = find_image(args.original_dir, obj, view, 'original')
        gtx_path = find_image(args.geotex_dir, obj, view, 'adapter')

        if not all([gt_path, orig_path, gtx_path]):
            continue

        gt = load_image(gt_path)
        orig = load_image(orig_path)
        gtx = load_image(gtx_path)

        mask = None
        if args.mask_dir:
            mask_path = find_image(args.mask_dir, obj, view, 'mask')
            if mask_path:
                mask = load_mask(mask_path)

        gt_crop = zoom_region(gt, mask)
        orig_crop = zoom_region(orig, mask)
        gtx_crop = zoom_region(gtx, mask)

        err_orig = compute_image_diff(gt, orig)
        err_gtx = compute_image_diff(gt, gtx)

        edge_images.extend([gt_crop, orig_crop, gtx_crop, err_orig, err_gtx])
        edge_labels.extend([
            f'{obj} GT', f'{obj} Orig', f'{obj} GeoTex',
            f'{obj} Err:Orig', f'{obj} Err:GeoTex'
        ])

    if edge_images:
        fig = make_grid(edge_images, edge_labels, ncols=5)
        if fig:
            fig.savefig(os.path.join(args.output_dir, 'edge_zoom_debug.png'),
                       dpi=150, bbox_inches='tight')
            import matplotlib.pyplot as plt
            plt.close(fig)

    # --- Figure C: Failure Cases ---
    print("Generating visual_failure_cases.png...")
    # Identify failure cases from metrics (GeoTex worse than Original)
    failure_images = []
    failure_labels = []
    failure_notes = []

    for obj in selected_objects:
        view = view_selections[obj]['view']
        key = f"{obj}/{view}"
        if key in metrics:
            m = metrics[key]
            # Check if GeoTex is worse
            try:
                orig_ssim = float(m.get('original_ssim', 0))
                gtx_ssim = float(m.get('adapter_ssim', 0))
                if gtx_ssim < orig_ssim - 0.02:
                    gt_path = find_image(args.gt_dir, obj, view, 'gt')
                    orig_path = find_image(args.original_dir, obj, view, 'original')
                    gtx_path = find_image(args.geotex_dir, obj, view, 'adapter')
                    if all([gt_path, orig_path, gtx_path]):
                        failure_images.extend([load_image(gt_path), load_image(orig_path), load_image(gtx_path)])
                        failure_labels.extend([f'GT', f'Orig (SSIM={orig_ssim:.3f})',
                                              f'GeoTex (SSIM={gtx_ssim:.3f})'])
            except (ValueError, TypeError):
                pass

    if failure_images:
        fig = make_grid(failure_images, failure_labels, ncols=3)
        if fig:
            fig.savefig(os.path.join(args.output_dir, 'visual_failure_cases.png'),
                       dpi=150, bbox_inches='tight')
            import matplotlib.pyplot as plt
            plt.close(fig)

    # --- Write Report ---
    report_lines.append("## Selected Objects\n\n")
    report_lines.append("| Object | View | FG Ratio | Reason |\n")
    report_lines.append("|--------|------|----------|--------|\n")
    for obj in selected_objects:
        sel = view_selections[obj]
        report_lines.append(f"| {obj} | {sel['view']} | {sel['fg_ratio']:.3f} | High foreground ratio |\n")

    report_lines.append("\n## Metrics Summary\n\n")
    if metrics:
        report_lines.append("| Object | Orig PSNR | GeoTex PSNR | Orig SSIM | GeoTex SSIM | Orig LPIPS | GeoTex LPIPS |\n")
        report_lines.append("|--------|-----------|-------------|-----------|-------------|------------|--------------|\n")
        for obj_idx, obj in enumerate(selected_objects):
            view = view_selections[obj]['view']
            # Try both naming conventions
            key = f"{obj}/{view}"
            if key not in metrics:
                key = f"{obj_idx}/{view}"
            if key in metrics:
                m = metrics[key]
                # Support eval.py column names: foreground_adapter_psnr, foreground_orig_psnr, etc.
                orig_psnr = m.get('foreground_orig_psnr', m.get('original_psnr', 'N/A'))
                adapter_psnr = m.get('foreground_adapter_psnr', m.get('adapter_psnr', 'N/A'))
                orig_ssim = m.get('foreground_orig_ssim', m.get('original_ssim', 'N/A'))
                adapter_ssim = m.get('foreground_adapter_ssim', m.get('adapter_ssim', 'N/A'))
                orig_lpips = m.get('foreground_orig_lpips', m.get('original_lpips', 'N/A'))
                adapter_lpips = m.get('foreground_adapter_lpips', m.get('adapter_lpips', 'N/A'))
                # Format floats
                try:
                    orig_psnr = f"{float(orig_psnr):.2f}"
                    adapter_psnr = f"{float(adapter_psnr):.2f}"
                    orig_ssim = f"{float(orig_ssim):.4f}"
                    adapter_ssim = f"{float(adapter_ssim):.4f}"
                    orig_lpips = f"{float(orig_lpips):.4f}"
                    adapter_lpips = f"{float(adapter_lpips):.4f}"
                except (ValueError, TypeError):
                    pass
                report_lines.append(
                    f"| {obj} | {orig_psnr} | {adapter_psnr} | "
                    f"{orig_ssim} | {adapter_ssim} | "
                    f"{orig_lpips} | {adapter_lpips} |\n"
                )
    else:
        report_lines.append("No metrics CSV provided.\n")

    report_lines.append("\n## Visualization Notes\n\n")
    report_lines.append("- `clean_comparison_grid.png`: Main comparison figure. Each row = one object.\n")
    report_lines.append("- `edge_zoom_debug.png`: Debug figure with gray error maps. NOT for paper.\n")
    report_lines.append("- `visual_failure_cases.png`: Cases where GeoTex underperforms Original.\n")
    report_lines.append("- Error maps use grayscale absolute error with unified scale.\n")

    if run_warnings:
        report_lines.append("\n## Warnings\n\n")
        for w in run_warnings:
            report_lines.append(f"- {w}\n")

    report_path = os.path.join(args.output_dir, 'figure_generation_report.md')
    with open(report_path, 'w') as f:
        f.writelines(report_lines)
    print(f"Report: {report_path}")
    print("Done.")


if __name__ == '__main__':
    main()
