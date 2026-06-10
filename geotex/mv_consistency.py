"""Multi-view consistency metrics for GeoTex-Adapter.

Computes view-to-view consistency without re-generating images.
Uses color statistics (no external model required).
"""
import os
import sys
import json
import csv
import argparse
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2

from metrics import unscale_latents, unscale_image
from eval import load_model, generate_images
from data_utils import prepare_batch, collate_batch


def split_views(image, n_views=6, layout='3x2'):
    """Split a composite image into individual views.

    The composite image is (B, C, 3H, 2W) with layout:
    [view0 view1 view2]
    [view3 view4 view5]
    """
    B, C, H, W = image.shape
    view_h = H // 3
    view_w = W // 2
    views = []
    for row in range(3):
        for col in range(2):
            v = image[:, :, row*view_h:(row+1)*view_h, col*view_w:(col+1)*view_w]
            views.append(v)
    return views


def color_consistency(views, mask=None):
    """Compute color consistency across views.

    For each view, compute foreground RGB mean.
    Then compute variance across views.
    Lower variance = more consistent.
    """
    means = []
    for v in views:
        if mask is not None:
            m = mask > 0.5
            if m.sum() > 0:
                fg_mean = v[m.expand_as(v)].mean().item()
            else:
                fg_mean = v.mean().item()
        else:
            fg_mean = v.mean().item()
        means.append(fg_mean)

    return {
        'mean': np.mean(means),
        'std': np.std(means),
        'variance': np.var(means),
        'per_view': means,
    }


def color_stats_consistency(views, mask=None):
    """Compute per-view foreground RGB mean and std, then consistency."""
    all_means = []
    all_stds = []
    for v in views:
        if mask is not None:
            m = (mask > 0.5)
            if m.sum() > 0:
                fg = v[m.expand_as(v)]
            else:
                fg = v.flatten()
        else:
            fg = v.flatten()
        all_means.append(fg.mean().item())
        all_stds.append(fg.std().item())

    return {
        'mean_of_means': np.mean(all_means),
        'std_of_means': np.std(all_means),
        'mean_of_stds': np.mean(all_stds),
        'std_of_stds': np.std(all_stds),
        'per_view_mean': all_means,
        'per_view_std': all_stds,
    }


@torch.no_grad()
def generate_views(model, batch, device, weight_dtype, geo_feats=None, num_steps=50, seed=42):
    """Generate 6-view composite image."""
    torch.manual_seed(seed)
    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
    torch.manual_seed(seed)
    return generate_images(model, batch, device, weight_dtype, geo_feats, num_steps, init_latents)


def main():
    parser = argparse.ArgumentParser(description="Multi-view consistency evaluation")
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--num_objects', type=int, default=50)
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16

    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex', 'mv_consistency')
    os.makedirs(args.output_dir, exist_ok=True)

    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Computing MV consistency for {num_objects} objects")

    results = []
    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # Generate with adapter
        image_adapter = generate_views(model, batch, device, weight_dtype, geo_feats, args.steps, args.seed)
        # Generate without adapter
        image_orig = generate_views(model, batch, device, weight_dtype, None, args.steps, args.seed)

        # Split into views
        views_orig = split_views(image_orig)
        views_adapter = split_views(image_adapter)
        views_mask = split_views(mask)

        # Compute color consistency for each
        orig_color = color_stats_consistency(views_orig, views_mask[0])
        adapter_color = color_stats_consistency(views_adapter, views_mask[0])

        obj_result = {
            'object_idx': obj_idx,
            'orig_std_of_means': orig_color['std_of_means'],
            'adapter_std_of_means': adapter_color['std_of_means'],
            'orig_mean_of_stds': orig_color['mean_of_stds'],
            'adapter_mean_of_stds': adapter_color['mean_of_stds'],
        }

        # Per-channel consistency
        for ch, name in enumerate(['R', 'G', 'B']):
            orig_ch_means = [v[0, ch].mean().item() for v in views_orig]
            adapter_ch_means = [v[0, ch].mean().item() for v in views_adapter]
            obj_result[f'orig_{name}_std'] = np.std(orig_ch_means)
            obj_result[f'adapter_{name}_std'] = np.std(adapter_ch_means)

        results.append(obj_result)

        delta = adapter_color['std_of_means'] - orig_color['std_of_means']
        print(f"  Object {obj_idx}: color_std {orig_color['std_of_means']:.4f}→{adapter_color['std_of_means']:.4f} ({delta:+.4f})")

    # Write CSV
    csv_path = os.path.join(args.output_dir, 'mv_consistency_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Summary
    summary = {}
    for key in ['orig_std_of_means', 'adapter_std_of_means', 'orig_mean_of_stds', 'adapter_mean_of_stds']:
        vals = [float(r[key]) for r in results]
        summary[key] = {'mean': float(np.mean(vals)), 'std': float(np.std(vals))}

    summary['consistency_improved'] = sum(
        1 for r in results if r['adapter_std_of_means'] < r['orig_std_of_means']
    )
    summary['total'] = len(results)

    json_path = os.path.join(args.output_dir, 'mv_consistency_summary.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Report
    improved = summary['consistency_improved']
    total = summary['total']
    report = f"""# Multi-View Consistency Report

## Color Consistency (std of per-view foreground RGB mean across 6 views)
- Original: {summary['orig_std_of_means']['mean']:.4f} ± {summary['orig_std_of_means']['std']:.4f}
- Adapter:  {summary['adapter_std_of_means']['mean']:.4f} ± {summary['adapter_std_of_means']['std']:.4f}
- Improved: {improved}/{total} objects have lower color variance with adapter

## Verdict
{"✓ Consistency improved" if improved > total // 2 else "⚠ Consistency not improved"}
"""
    report_path = os.path.join(args.output_dir, 'mv_consistency_report.md')
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nResults: {json_path}")
    print(f"Report: {report_path}")
    print(f"Consistency improved: {improved}/{total}")


if __name__ == '__main__':
    main()
