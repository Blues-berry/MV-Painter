"""Probe sensitivity of the C3 window and peak scale on the v2 checkpoint.

Each candidate keeps the low scale fixed and applies the high scale only on a
single denoising interval.  This isolates the two reviewer concerns that the
chosen 1/3, 2/3 boundaries and 2.50 peak may be hand-tuned.

Example:
    python geotex/sweep_c3_sensitivity.py --num_objects 4 \
        --output_dir mvpoutput/revision_c3_sensitivity_smoke
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))

from omegaconf import OmegaConf  # noqa: F401  (keeps environment check explicit)
from torchvision.utils import save_image
from src.utils.train_util import instantiate_from_config
from eval_schedule_comparison import (
    load_model, generate_with_schedule, compute_metrics,
    prepare_batch, collate_batch,
)


def parse_windows(value):
    windows = []
    for item in value.split(','):
        start, end = (float(x) for x in item.split(':'))
        if not 0.0 <= start < end <= 1.0:
            raise ValueError(f'invalid window {item}; require 0 <= start < end <= 1')
        windows.append((start, end))
    return windows


def main():
    parser = argparse.ArgumentParser(description='C3 boundary/peak sensitivity probe')
    parser.add_argument('--config', default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', default='mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt')
    parser.add_argument('--output_dir', default='mvpoutput/revision_c3_sensitivity')
    parser.add_argument('--num_objects', type=int, default=24)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--low', type=float, default=1.25)
    parser.add_argument('--highs', default='2.00,2.25,2.50,2.75,3.00')
    parser.add_argument('--windows', default='0.25:0.75,0.333333:0.666667,0.4:0.6')
    args = parser.parse_args()

    highs = [float(x) for x in args.highs.split(',')]
    windows = parse_windows(args.windows)
    candidates = [
        (f'w{start:.3f}_{end:.3f}_h{high:.2f}'.replace('.', 'p'), start, end, high)
        for start, end in windows for high in highs
    ]
    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device(args.device)
    dtype = torch.float16
    model, config = load_model(args.config, args.checkpoint, device)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    results = {name: [] for name, _, _, _ in candidates}

    print(f'Candidates={len(candidates)}, objects={num_objects}, steps={args.num_steps}')
    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        _, target, _, _, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_input = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input)
        torch.manual_seed(42)
        latent_shape = (1, 4, model.img_size * 3 // 8, model.img_size * 2 // 8)
        init_latents = torch.randn(*latent_shape, device=device, dtype=dtype)

        for name, start, end, high in candidates:
            def schedule(progress, **_kw):
                return high if start <= progress < end else args.low

            pred = generate_with_schedule(model, batch, device, dtype, geo_feats,
                                          schedule, args.num_steps, init_latents.clone())
            row = compute_metrics(pred, target, mask)
            row['object'] = f'obj_{obj_idx:04d}'
            results[name].append(row)
            if obj_idx < 2:
                save_dir = os.path.join(args.output_dir, 'samples')
                os.makedirs(save_dir, exist_ok=True)
                save_image(pred, os.path.join(save_dir, f'obj{obj_idx:02d}_{name}.png'))
        print(f'[{obj_idx + 1}/{num_objects}] done')
        torch.cuda.empty_cache()

    summary = []
    csv_rows = []
    for name, start, end, high in candidates:
        rows = results[name]
        mean = lambda key: float(np.mean([r[key] for r in rows]))
        summary.append({
            'schedule': name, 'start': start, 'end': end, 'low': args.low, 'high': high,
            'fg_ssim': mean('fg_ssim'), 'psnr': mean('psnr'),
            'lap_var_ratio': float(np.mean([r['lap_var'] / (r['gt_lap_var'] + 1e-8) for r in rows])),
            'rgb_std_ratio': float(np.mean([r['rgb_std'] / (r['gt_rgb_std'] + 1e-8) for r in rows])),
        })
        for r in rows:
            csv_rows.append({k: r[k] for k in ('object', 'fg_ssim', 'psnr', 'lap_var', 'rgb_std', 'grad_mag')})
    summary.sort(key=lambda r: r['psnr'], reverse=True)
    with open(os.path.join(args.output_dir, 'summary.json'), 'w') as f:
        json.dump({'checkpoint': args.checkpoint, 'num_objects': num_objects,
                   'num_steps': args.num_steps, 'low': args.low,
                   'results': summary}, f, indent=2)
    with open(os.path.join(args.output_dir, 'per_object_metrics.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    for row in summary[:10]:
        print(f"{row['schedule']:24s} SSIM={row['fg_ssim']:.4f} PSNR={row['psnr']:.2f} "
              f"Lap={row['lap_var_ratio']:.3f} RGB={row['rgb_std_ratio']:.3f}")


if __name__ == '__main__':
    main()
