#!/usr/bin/env python3
"""Recompute texture metrics for 300-object evaluation.

This script re-runs inference for s=1.25 and s=2.50 on the same 300 objects
used in C3_300obj, using the same seed, checkpoint, and steps.

Key difference from eval_exploration.py:
  - Does NOT save visualizations (except first 5 objects for sanity check)
  - Computes texture metrics (rgb_std, grad_mag, lap_var, etc.) via metrics_extended
  - Outputs per_object_metrics.csv with texture columns

Usage:
    cd /4T/CXY/MV-Painter
    python geotex/eval_texture_300obj.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scale 1.25 \
        --output_dir mvpoutput/geotex_refattn_v1/paper_readiness_audit/cadgraphics_fullpaper_patch_v1/01_texture_closure_300/s125_texture_reeval \
        --num_objects 300 \
        --device cuda:0

    python geotex/eval_texture_300obj.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scale 2.50 \
        --output_dir mvpoutput/geotex_refattn_v1/paper_readiness_audit/cadgraphics_fullpaper_patch_v1/01_texture_closure_300/s250_texture_reeval \
        --num_objects 300 \
        --device cuda:1
"""

import os
import sys
import json
import csv
import gc
import hashlib
import argparse
import time
from datetime import timedelta

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from omegaconf import OmegaConf

sys.path.insert(0, '/4T/CXY/MV-Painter')
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')
sys.path.insert(0, '/4T/CXY/MV-Painter/geotex')

os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.utils import save_image as tv_save_image
from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image
from metrics_extended import compute_all_extended
from eval_exploration import (
    load_model, generate, compute_metrics, setup_layer_scales,
    normalize_bg, fg_crop, get_lpips_fn
)
from eval import collate_batch, prepare_batch


def main():
    parser = argparse.ArgumentParser(description="Recompute texture metrics for 300-obj set")
    parser.add_argument('--config', required=True, help='Model config YAML')
    parser.add_argument('--checkpoint', required=True, help='GeoTex adapter checkpoint')
    parser.add_argument('--scale', type=float, required=True, help='Uniform adapter scale (e.g. 1.25 or 2.50)')
    parser.add_argument('--output_dir', required=True, help='Output directory for metrics')
    parser.add_argument('--num_objects', type=int, default=300, help='Number of objects to evaluate')
    parser.add_argument('--device', type=str, default='cuda:0', help='GPU device')
    parser.add_argument('--steps', type=int, default=50, help='Denoising steps')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--save_vis_first_n', type=int, default=5,
                        help='Save visualizations for first N objects (sanity check)')
    parser.add_argument('--resume_from', type=int, default=0,
                        help='Resume from this object index (for interrupted runs)')
    args = parser.parse_args()

    device = torch.device(args.device)
    wdt = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Vis dir (only for sanity check)
    vis_dir = os.path.join(args.output_dir, 'visualizations')
    if args.save_vis_first_n > 0:
        os.makedirs(vis_dir, exist_ok=True)

    print(f"{'='*60}")
    print(f"Texture Metrics Recomputation")
    print(f"Scale: {args.scale}")
    print(f"Objects: {args.num_objects}")
    print(f"Device: {args.device}")
    print(f"Output: {args.output_dir}")
    print(f"{'='*60}")
    print(flush=True)

    # Monkey-patch for scale control
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig_forward = GeoTexResnetWrapper.forward

    def scaled_forward(self, *a, **kw):
        hs = self.resnet(*a, **kw)
        if self._current_geo_feats is not None:
            gf = self._current_geo_feats.get(self.geo_feat_key)
            if gf is not None:
                if gf.shape[2:] != hs.shape[2:]:
                    gf = F.interpolate(gf, size=hs.shape[2:], mode='bilinear', align_corners=False)
                c = self.adapter.compute_correction(hs, gf)
                self._last_correction = c
                hs = hs + c * getattr(self, '_adapter_scale', 1.0)
        return hs

    GeoTexResnetWrapper.forward = scaled_forward

    # Load model
    print("Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config_obj = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config_obj.data.params.validation)
    lpips_fn = get_lpips_fn(device)

    # Object list: first N objects (same as C3_300obj)
    num = min(args.num_objects, len(dataset))
    object_indices = list(range(num))
    print(f"Evaluating {num} objects (indices 0-{num-1})")

    # Save config snapshot
    config_snapshot = {
        'config': args.config,
        'checkpoint': args.checkpoint,
        'scale': args.scale,
        'num_objects': num,
        'steps': args.steps,
        'seed': args.seed,
        'script': 'geotex/eval_texture_300obj.py',
        'purpose': 'Texture metrics recomputation for paper readiness audit',
        'save_vis_first_n': args.save_vis_first_n,
    }
    with open(os.path.join(args.output_dir, 'config_snapshot.json'), 'w') as f:
        json.dump(config_snapshot, f, indent=2)

    # Results storage
    results = []
    partial_csv = os.path.join(args.output_dir, 'per_object_metrics_partial.csv')

    # Resume support
    if args.resume_from > 0 and os.path.exists(partial_csv):
        with open(partial_csv) as f:
            reader = csv.DictReader(f)
            results = [row for row in reader]
            # Convert numeric strings back to appropriate types
            for r in results:
                for k, v in r.items():
                    try:
                        r[k] = float(v)
                    except (ValueError, TypeError):
                        pass
        print(f"Resumed: loaded {len(results)} existing results")

    start_time = time.time()
    start_idx = args.resume_from

    for i, obj_idx in enumerate(object_indices):
        if i < start_idx:
            continue

        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # Set uniform scale
        setup_layer_scales(model, scale=args.scale)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=wdt)

        # Generate baseline (no adapter)
        torch.manual_seed(args.seed)
        img_orig = generate(model, batch, device, wdt, None, 0, args.steps, shared_latents)

        # Generate adapter output
        torch.manual_seed(args.seed)
        img_adapter = generate(model, batch, device, wdt, geo_feats, args.scale, args.steps,
                               shared_latents)

        gt = target_imgs
        edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        if edge_mask.shape[2:] != gt.shape[2:]:
            edge_mask = F.interpolate(edge_mask, size=gt.shape[2:], mode='bilinear', align_corners=False)

        # Compute full metrics (standard + texture)
        adapter_m = compute_metrics(img_adapter, gt, mask, edge_mask, lpips_fn, device)
        orig_m = compute_metrics(img_orig, gt, mask, edge_mask, lpips_fn, device)

        # Build result row
        r = {
            'object_idx': obj_idx,
            'scale': args.scale,
            'fg_ratio': float((mask > 0.5).sum().item() / mask.numel()),
        }
        for k, v in adapter_m.items():
            r[f'adapter_{k}'] = v
        for k, v in orig_m.items():
            r[f'orig_{k}'] = v
        for k in adapter_m:
            if adapter_m[k] is not None and orig_m[k] is not None:
                r[f'delta_{k}'] = adapter_m[k] - orig_m[k]

        results.append(r)

        # Save visualization (first N only)
        if i < args.save_vis_first_n:
            tv_save_image(gt, os.path.join(vis_dir, f'obj_{obj_idx:03d}_gt.png'))
            tv_save_image(img_orig, os.path.join(vis_dir, f'obj_{obj_idx:03d}_orig.png'))
            tv_save_image(img_adapter, os.path.join(vis_dir, f'obj_{obj_idx:03d}_adapter.png'))

        # Free memory
        del img_orig, img_adapter, gt, mask, edge_mask, batch, geo_feats, shared_latents
        del cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, geo_clean
        del adapter_m, orig_m, edge_source
        gc.collect()
        torch.cuda.empty_cache()

        # Progress
        elapsed = time.time() - start_time
        rate = (i - start_idx + 1) / elapsed
        remaining = (num - i - 1) / rate if rate > 0 else 0

        if i % 10 == 0 or i == num - 1:
            d_fs = r.get('delta_fg_ssim', 0)
            d_lv = r.get('delta_fg_lap_var', 0)
            d_rs = r.get('delta_fg_rgb_std', 0)
            print(f"  [{i+1:3d}/{num}] obj_{obj_idx:03d}: "
                  f"ΔFG-SSIM={d_fs:+.4f} ΔLapVar={d_lv:+.6f} ΔRGB-Std={d_rs:+.6f} "
                  f"[{timedelta(seconds=int(remaining))} remaining]", flush=True)

        # Periodic save (every 50 objects)
        if (i + 1) % 50 == 0:
            _save_csv(results, partial_csv)
            print(f"  → Saved partial results ({len(results)} objects)", flush=True)

    # Final save
    final_csv = os.path.join(args.output_dir, 'per_object_metrics.csv')
    _save_csv(results, final_csv)

    # Summary
    _save_summary(results, args.output_dir)

    # Restore
    GeoTexResnetWrapper.forward = _orig_forward

    elapsed_total = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE. {len(results)} objects evaluated in {timedelta(seconds=int(elapsed_total))}")
    print(f"Output: {args.output_dir}")
    print(f"{'='*60}")


def _save_csv(results, path):
    """Save results list to CSV."""
    if not results:
        return
    keys = list(results[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


def _save_summary(results, output_dir):
    """Compute and save summary statistics."""
    if not results:
        return

    summary = {}
    # Get all numeric keys
    numeric_keys = [k for k in results[0].keys()
                    if isinstance(results[0][k], (int, float)) and k != 'object_idx']

    for key in numeric_keys:
        values = [r[key] for r in results if r.get(key) is not None and not np.isnan(r.get(key, float('nan')))]
        if values:
            summary[key] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'median': float(np.median(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'total': len(values),
            }

    with open(os.path.join(output_dir, 'summary_metrics.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved: {os.path.join(output_dir, 'summary_metrics.json')}")


if __name__ == '__main__':
    main()
