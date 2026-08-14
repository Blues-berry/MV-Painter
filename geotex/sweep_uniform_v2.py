"""Uniform adapter-scale sweep on the v2 checkpoint (geotex_v2_ema_final.pt).

Runs uniform scales {1.00, 1.75, 2.25} on the same 24-object probe set / seed-42
protocol as `eval_schedule_comparison.py`, so the points can be merged with the
existing fixed_low (1.25) / fixed_high (2.50) / no_adapter rows of that run to
form a uniform-scale trend on ONE checkpoint. This replaces the design-phase
(50-object, deleted-checkpoint) scale sweep used by an earlier paper draft.

Usage:
    python geotex/sweep_uniform_v2.py \
        --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/revision_scale_sweep_v2 \
        --num_objects 24 --num_steps 50
"""
import os
import sys
import json
import csv
import argparse
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))

from omegaconf import OmegaConf
from torchvision.utils import save_image
from src.utils.train_util import instantiate_from_config

from eval_schedule_comparison import (load_model, generate_with_schedule,
                                      compute_metrics, prepare_batch, collate_batch)

UNIFORM_SCALES = [1.00, 1.75, 2.25]


def main():
    parser = argparse.ArgumentParser(description="Uniform scale sweep on v2 checkpoint")
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, default='mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt')
    parser.add_argument('--output_dir', type=str, default='mvpoutput/revision_scale_sweep_v2')
    parser.add_argument('--num_objects', type=int, default=24)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    model, config = load_model(args.config, args.checkpoint, device)
    print("Model loaded.")

    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Dataset: {len(dataset)} objects, evaluating first {num_objects}")

    all_results = {f'uniform_{s:.2f}'.replace('.', 'p'): [] for s in UNIFORM_SCALES}

    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for s in UNIFORM_SCALES:
            sched_fn = lambda p, **kw: s  # noqa: E731
            pred = generate_with_schedule(
                model, batch, device, weight_dtype, geo_feats,
                sched_fn, args.num_steps, init_latents.clone()
            )
            metrics = compute_metrics(pred, target_imgs, mask)
            metrics['object'] = f'obj_{obj_idx:04d}'
            key = f'uniform_{s:.2f}'.replace('.', 'p')
            all_results[key].append(metrics)

            if obj_idx < 4:
                save_dir = os.path.join(args.output_dir, 'samples')
                os.makedirs(save_dir, exist_ok=True)
                save_image(pred, os.path.join(save_dir, f'obj{obj_idx:02d}_{key}.png'))

        if (obj_idx + 1) % 4 == 0:
            print(f"[{obj_idx+1}/{num_objects}] done")

        torch.cuda.empty_cache()

    # Summary
    summary_rows = []
    csv_rows = []
    for key in all_results:
        results = all_results[key]
        rows = []
        for r in results:
            rows.append({
                'object': r['object'], 'fg_ssim': float(r['fg_ssim']),
                'psnr': float(r['psnr']), 'lap_var': float(r['lap_var']),
                'rgb_std': float(r['rgb_std']), 'grad_mag': float(r['grad_mag']),
            })
        csv_rows.extend(rows)
        mean = lambda f: float(np.mean([r[f] for r in results]))  # noqa: E731
        lap_ratio = float(np.mean([r['lap_var'] / (r['gt_lap_var'] + 1e-8) for r in results]))
        rgb_ratio = float(np.mean([r['rgb_std'] / (r['gt_rgb_std'] + 1e-8) for r in results]))
        summary_rows.append({
            'schedule': key,
            'scale': float(key.replace('uniform_', '').replace('p', '.')),
            'fg_ssim': mean('fg_ssim'),
            'psnr': mean('psnr'),
            'lap_var_ratio': lap_ratio,
            'rgb_std_ratio': rgb_ratio,
        })
        print(f"{key:12s} FG-SSIM={mean('fg_ssim'):.4f} PSNR={mean('psnr'):.2f} "
              f"LapRatio={lap_ratio:.3f} RGBRatio={rgb_ratio:.3f}")

    with open(os.path.join(args.output_dir, 'summary.json'), 'w') as f:
        json.dump({'checkpoint': args.checkpoint, 'num_objects': num_objects,
                   'num_steps': args.num_steps, 'results': summary_rows}, f, indent=2)
    with open(os.path.join(args.output_dir, 'per_object_metrics.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    print(f"Saved: {args.output_dir}/summary.json")


if __name__ == '__main__':
    main()
