"""Per-view evaluation: compute metrics for each view separately.

Uses the same generation as main eval (3x2 grid), but extracts individual
views for per-view metric computation. Useful for detecting view-specific
degradation (e.g., back views worse than front views).

Usage:
    python geotex/eval_per_view.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --num_objects 300 \
        --output_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean \
        --device cuda:0
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
from torchvision.utils import save_image

from metrics import compute_psnr, compute_ssim, unscale_latents, unscale_image
from eval import (load_model, generate_images, get_lpips, compute_lpips,
                  collate_batch, prepare_batch)


# 3x2 grid layout: row 0 = [front, front_right], row 1 = [right, back],
#                   row 2 = [left, front_left]
VIEW_NAMES = ['front', 'front_right', 'right', 'back', 'left', 'front_left']


def extract_views(grid_image):
    """Extract 6 individual views from a 3x2 grid image (B, C, 3H, 2W).

    Returns: list of 6 (B, C, H, W) tensors
    """
    B, C, H, W = grid_image.shape
    h = H // 3
    w = W // 2
    views = []
    for row in range(3):
        for col in range(2):
            view = grid_image[:, :, row*h:(row+1)*h, col*w:(col+1)*w]
            views.append(view)
    return views


def main():
    parser = argparse.ArgumentParser(description="Per-view GeoTex Evaluation")
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--num_objects', type=int, default=10)
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--save_vis', action='store_true', default=True)
    parser.add_argument('--vis_count', type=int, default=20)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16

    if args.output_dir is None:
        args.output_dir = 'mvpoutput/geotex_refattn_v1/eval_300obj_clean'

    per_view_dir = os.path.join(args.output_dir, 'per_view')
    os.makedirs(per_view_dir, exist_ok=True)

    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Per-view evaluation: {num_objects} objects × 6 views")

    try:
        lpips_fn = get_lpips(device)
        lpips_available = True
    except:
        lpips_fn = None
        lpips_available = False
        print("WARNING: LPIPS not available")

    all_results = []

    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        torch.manual_seed(args.seed)
        image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)
        torch.manual_seed(args.seed)
        image_orig = generate_images(model, batch, device, weight_dtype, None, args.steps, shared_latents)

        # Extract views
        gt_views = extract_views(target_imgs)
        orig_views = extract_views(image_orig)
        adapter_views = extract_views(image_adapter)

        for v_idx, v_name in enumerate(VIEW_NAMES):
            gt_v = gt_views[v_idx]
            orig_v = orig_views[v_idx]
            adapter_v = adapter_views[v_idx]

            result = {
                'object_idx': obj_idx,
                'view_idx': v_idx,
                'view_name': v_name,
            }

            for label, pred in [('orig', orig_v), ('adapter', adapter_v)]:
                result[f'{label}_psnr'] = compute_psnr(pred, gt_v).item()
                result[f'{label}_ssim'] = compute_ssim(pred, gt_v).item()
                if lpips_fn:
                    try:
                        result[f'{label}_lpips'] = compute_lpips(pred, gt_v, device=device)
                    except:
                        result[f'{label}_lpips'] = None

            result['delta_psnr'] = result['adapter_psnr'] - result['orig_psnr']
            result['delta_ssim'] = result['adapter_ssim'] - result['orig_ssim']
            if lpips_fn and 'adapter_lpips' in result and 'orig_lpips' in result:
                if result['adapter_lpips'] is not None and result['orig_lpips'] is not None:
                    result['delta_lpips'] = result['adapter_lpips'] - result['orig_lpips']

            all_results.append(result)

        # Save per-object view visualization
        if args.save_vis and obj_idx < args.vis_count:
            obj_dir = os.path.join(per_view_dir, f'obj_{obj_idx:03d}')
            os.makedirs(obj_dir, exist_ok=True)
            for v_idx, v_name in enumerate(VIEW_NAMES):
                save_image(gt_views[v_idx], os.path.join(obj_dir, f'{v_name}_gt.png'))
                save_image(orig_views[v_idx], os.path.join(obj_dir, f'{v_name}_orig.png'))
                save_image(adapter_views[v_idx], os.path.join(obj_dir, f'{v_name}_adapter.png'))

        # Progress
        obj_deltas = [r['delta_psnr'] for r in all_results if r['object_idx'] == obj_idx]
        mean_d = np.mean(obj_deltas)
        print(f"  Object {obj_idx}: mean view PSNR delta = {mean_d:+.2f} dB")

    # Write CSV
    csv_path = os.path.join(per_view_dir, 'per_view_metrics.csv')
    fieldnames = list(all_results[0].keys())
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    # Summary by view name
    summary = {}
    for v_name in VIEW_NAMES:
        view_results = [r for r in all_results if r['view_name'] == v_name]
        psnr_vals = [r['delta_psnr'] for r in view_results]
        ssim_vals = [r['delta_ssim'] for r in view_results]
        summary[v_name] = {
            'mean_delta_psnr': float(np.mean(psnr_vals)),
            'std_delta_psnr': float(np.std(psnr_vals)),
            'mean_delta_ssim': float(np.mean(ssim_vals)),
            'positive_psnr': sum(1 for d in psnr_vals if d > 0),
            'total': len(view_results),
        }
        print(f"  {v_name:12s}: PSNR Δ={summary[v_name]['mean_delta_psnr']:+.2f} dB "
              f"[{summary[v_name]['positive_psnr']}/{summary[v_name]['total']}]")

    with open(os.path.join(per_view_dir, 'per_view_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nPer-view results: {per_view_dir}")


if __name__ == '__main__':
    main()
