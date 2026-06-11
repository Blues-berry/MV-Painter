"""Generate comparison visualization grids for best/worst/regression cases.

Usage:
    python geotex/make_comparison_grids.py \
        --eval_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean \
        --analysis_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean/analysis \
        --output_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean/comparison_grids
"""
import os
import sys
import json
import csv
import argparse
import numpy as np

try:
    import torch
    from torchvision.utils import save_image, make_grid
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def load_analysis_results(analysis_dir):
    """Load analysis_results.json."""
    path = os.path.join(analysis_dir, 'analysis_results.json')
    with open(path, 'r') as f:
        return json.load(f)


def make_grid_from_images(image_paths, nrow=3, padding=2):
    """Create a grid from a list of image paths using PIL."""
    images = []
    for p in image_paths:
        if os.path.exists(p):
            img = Image.open(p).convert('RGB')
            images.append(img)
    if not images:
        return None

    # Resize all to same size
    w, h = images[0].size
    images = [img.resize((w, h), Image.BILINEAR) for img in images]

    # Create grid
    n = len(images)
    cols = min(nrow, n)
    rows = (n + cols - 1) // cols

    grid = Image.new('RGB', (cols * w + (cols - 1) * padding,
                              rows * h + (rows - 1) * padding), (255, 255, 255))
    for i, img in enumerate(images):
        r = i // cols
        c = i % cols
        grid.paste(img, (c * (w + padding), r * (h + padding)))

    return grid


def collect_object_images(eval_dir, obj_idx):
    """Collect all images for a given object."""
    vis_dir = os.path.join(eval_dir, 'visualizations')
    prefix = f"obj_{obj_idx:03d}"
    images = {}
    for suffix in ['gt', 'original', 'adapter', 'original_error', 'adapter_error', 'mask', 'edge_mask']:
        path = os.path.join(vis_dir, f'{prefix}_{suffix}.png')
        if os.path.exists(path):
            images[suffix] = path
    return images


def make_case_grid(eval_dir, object_indices, title, output_path, nrow=3):
    """Make a comparison grid for a set of objects."""
    all_grids = []
    for obj_idx in object_indices:
        images = collect_object_images(eval_dir, obj_idx)
        if not images:
            continue
        # Order: GT, Original, Adapter, Original Error, Adapter Error
        order = ['gt', 'original', 'adapter', 'original_error', 'adapter_error']
        paths = [images.get(s) for s in order if s in images]
        if paths:
            grid = make_grid_from_images(paths, nrow=nrow)
            if grid:
                all_grids.append(grid)

    if not all_grids:
        print(f"No images found for {title}")
        return

    # Stack all object grids vertically
    widths = [g.width for g in all_grids]
    max_w = max(widths)
    total_h = sum(g.height for g in all_grids) + (len(all_grids) - 1) * 4

    final = Image.new('RGB', (max_w, total_h), (255, 255, 255))
    y = 0
    for g in all_grids:
        final.paste(g, ((max_w - g.width) // 2, y))
        y += g.height + 4

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.save(output_path)
    print(f"Saved {title}: {output_path} ({len(all_grids)} objects)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval_dir', required=True)
    parser.add_argument('--analysis_dir', default=None)
    parser.add_argument('--output_dir', default=None)
    args = parser.parse_args()

    if args.analysis_dir is None:
        args.analysis_dir = os.path.join(args.eval_dir, 'analysis')
    if args.output_dir is None:
        args.output_dir = os.path.join(args.eval_dir, 'comparison_grids')

    # Load analysis results
    results_path = os.path.join(args.analysis_dir, 'analysis_results.json')
    if not os.path.exists(results_path):
        print(f"ERROR: {results_path} not found. Run analyze_300obj_results.py first.")
        sys.exit(1)

    results = load_analysis_results(args.analysis_dir)

    # Best-20
    best_indices = [idx for idx, _ in results['best_20'][-20:]]
    make_case_grid(args.eval_dir, best_indices, 'Best-20',
                   os.path.join(args.output_dir, 'best_20_grid.png'))

    # Worst-20
    worst_indices = [idx for idx, _ in results['worst_20'][:20]]
    make_case_grid(args.eval_dir, worst_indices, 'Worst-20',
                   os.path.join(args.output_dir, 'worst_20_grid.png'))

    # Regression cases
    reg_indices = [idx for idx, _ in results['regressions'][:20]]
    make_case_grid(args.eval_dir, reg_indices, 'Regression Cases',
                   os.path.join(args.output_dir, 'regression_grid.png'))

    # Representative success cases (middle of best-20)
    if len(best_indices) >= 10:
        mid_start = len(best_indices) // 2 - 5
        success_indices = best_indices[mid_start:mid_start + 10]
        make_case_grid(args.eval_dir, success_indices, 'Representative Success',
                       os.path.join(args.output_dir, 'success_grid.png'))

    print(f"\nGrids saved to {args.output_dir}")


if __name__ == '__main__':
    main()
