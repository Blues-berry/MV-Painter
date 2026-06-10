"""Generate visual comparison figures for paper.

Only generates qualitative visual comparisons — no bar charts, scatter plots, or histograms.
"""
import os
import sys
import json
import csv
import argparse
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from torchvision.utils import save_image
from torchvision.transforms import v2
from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config

from metrics import compute_psnr, compute_ssim, compute_edge_mask
from eval import load_model, generate_images
from data_utils import prepare_batch, collate_batch


def load_per_object(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def select_objects(per_object, n_best=2, n_median=2, n_worst=2, n_failure=2):
    """Select representative objects for comparison."""
    # Sort by FG PSNR delta
    for r in per_object:
        o = float(r.get('foreground_orig_psnr', 0))
        a = float(r.get('foreground_adapter_psnr', 0))
        r['_fg_psnr_delta'] = a - o
        o_s = float(r.get('foreground_orig_ssim', 0))
        a_s = float(r.get('foreground_adapter_ssim', 0))
        r['_fg_ssim_delta'] = a_s - o_s

    sorted_by_psnr = sorted(per_object, key=lambda x: x['_fg_psnr_delta'], reverse=True)
    sorted_by_ssim = sorted(per_object, key=lambda x: x['_fg_ssim_delta'], reverse=True)

    selected = []
    selected_ids = set()

    # Best PSNR
    for r in sorted_by_psnr:
        if r['object_idx'] not in selected_ids and len([s for s in selected if s.get('_type') == 'best_psnr']) < n_best:
            r['_type'] = 'best_psnr'
            selected.append(r)
            selected_ids.add(r['object_idx'])

    # Best SSIM
    for r in sorted_by_ssim:
        if r['object_idx'] not in selected_ids and len([s for s in selected if s.get('_type') == 'best_ssim']) < n_best:
            r['_type'] = 'best_ssim'
            selected.append(r)
            selected_ids.add(r['object_idx'])

    # Median
    mid = len(sorted_by_psnr) // 2
    for r in sorted_by_psnr[mid-2:mid+2]:
        if r['object_idx'] not in selected_ids and len([s for s in selected if s.get('_type') == 'median']) < n_median:
            r['_type'] = 'median'
            selected.append(r)
            selected_ids.add(r['object_idx'])

    # Worst / failure
    for r in sorted_by_psnr[-n_worst-n_failure:]:
        if r['object_idx'] not in selected_ids and len([s for s in selected if s.get('_type') == 'failure']) < n_worst + n_failure:
            r['_type'] = 'failure'
            selected.append(r)
            selected_ids.add(r['object_idx'])

    return selected


@torch.no_grad()
def generate_object_images(model, dataset, obj_idx, device, weight_dtype, num_steps=50, seed=42):
    """Generate GT, Original, GeoTex for one object."""
    batch = collate_batch(dataset, obj_idx, device)
    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        prepare_batch(batch, model.img_size, device)

    geo_clean = geo_input.float().clamp(0, 1)
    geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
    geo_feats = model.geo_encoder(geo_clean)

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    torch.manual_seed(seed)
    shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

    torch.manual_seed(seed)
    image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, num_steps, shared_latents)
    torch.manual_seed(seed)
    image_orig = generate_images(model, batch, device, weight_dtype, None, num_steps, shared_latents)

    # Edge mask
    edge_source = real_depth_imgs.float()
    edge_mask = compute_edge_mask(edge_source, threshold=0.1)
    if edge_mask.shape[2:] != target_imgs.shape[2:]:
        edge_mask = torch.nn.functional.interpolate(edge_mask, size=target_imgs.shape[2:], mode='bilinear', align_corners=False)

    return {
        'gt': target_imgs,
        'orig': image_orig,
        'adapter': image_adapter,
        'mask': mask,
        'edge_mask': edge_mask,
    }


def make_main_comparison(selected_objects, model, dataset, device, weight_dtype, output_dir, num_steps=50):
    """Figure 1: Main qualitative comparison grid."""
    os.makedirs(output_dir, exist_ok=True)

    all_rows = []
    for obj_info in selected_objects:
        obj_idx = int(obj_info['object_idx'])
        imgs = generate_object_images(model, dataset, obj_idx, device, weight_dtype, num_steps)

        gt = imgs['gt']
        orig = imgs['orig']
        adapter = imgs['adapter']

        err_orig = (orig - gt).abs()
        err_adapter = (adapter - gt).abs()

        # Single row: Condition(GT) | GT | Original | GeoTex | Orig Error | GeoTex Error
        row = torch.cat([gt, gt, orig, adapter, err_orig * 5, err_adapter * 5], dim=0)
        all_rows.append(row)

    grid = torch.cat(all_rows, dim=0)
    save_image(grid, os.path.join(output_dir, 'main_qualitative_comparison.png'), nrow=6, padding=2)

    print(f"Saved main_qualitative_comparison.png ({len(selected_objects)} objects × 6 columns)")
    return grid


def make_worst_case_comparison(per_object, model, dataset, device, weight_dtype, output_dir, num_steps=50, n=5):
    """Figure 3: Worst case comparison."""
    os.makedirs(output_dir, exist_ok=True)

    # Find worst cases
    for r in per_object:
        r['_fg_psnr_delta'] = float(r.get('foreground_adapter_psnr', 0)) - float(r.get('foreground_orig_psnr', 0))
        r['_fg_ssim_delta'] = float(r.get('foreground_adapter_ssim', 0)) - float(r.get('foreground_orig_ssim', 0))

    worst_psnr = sorted(per_object, key=lambda x: x['_fg_psnr_delta'])[:n]

    all_rows = []
    for obj_info in worst_psnr:
        obj_idx = int(obj_info['object_idx'])
        imgs = generate_object_images(model, dataset, obj_idx, device, weight_dtype, num_steps)

        gt = imgs['gt']
        orig = imgs['orig']
        adapter = imgs['adapter']
        err_orig = (orig - gt).abs()
        err_adapter = (adapter - gt).abs()

        row = torch.cat([gt, orig, adapter, err_orig * 5, err_adapter * 5], dim=0)
        all_rows.append(row)

    grid = torch.cat(all_rows, dim=0)
    save_image(grid, os.path.join(output_dir, 'worst_case_comparison.png'), nrow=5, padding=2)

    print(f"Saved worst_case_comparison.png ({n} worst cases)")


def main():
    parser = argparse.ArgumentParser(description="Generate visual comparison figures")
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--input_dir', required=True, help='Directory with per_object_metrics.csv')
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--num_objects', type=int, default=8)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join(args.input_dir, 'comparison_figures')
    os.makedirs(args.output_dir, exist_ok=True)

    # Load per-object metrics
    csv_path = os.path.join(args.input_dir, 'per_object_metrics.csv')
    per_object = load_per_object(csv_path)
    print(f"Loaded {len(per_object)} objects")

    # Select representative objects
    selected = select_objects(per_object)
    print(f"Selected {len(selected)} objects: {[s['object_idx'] for s in selected]}")

    # Load model
    device = torch.device(args.device)
    weight_dtype = torch.float16
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)

    # Generate figures
    make_main_comparison(selected, model, dataset, device, weight_dtype, args.output_dir, args.steps)
    make_worst_case_comparison(per_object, model, dataset, device, weight_dtype, args.output_dir, args.steps, n=5)

    print(f"\nAll figures saved to {args.output_dir}")


if __name__ == '__main__':
    main()
