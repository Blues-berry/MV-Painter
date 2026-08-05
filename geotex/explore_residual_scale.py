"""Residual magnitude spectrum: scale adapter output_proj to bridge v3->v2.

The three checkpoints span a spectrum of trained adapter residual magnitudes:
  refattn_v1 (paper) / v2: large corrections (deep ~0.3/pixel)
  v3_anticollapse:       tiny corrections (deep ~0.006/pixel, ~45x smaller)

Hypothesis H4: the sign/magnitude of high-scale intervention's effect is set by
the trained residual magnitude. Same checkpoint (v2), scale all adapters'
output_proj weights by gamma, and compare fixed_low vs fixed_high:
  gamma small  -> adapter too weak for scale to matter  (v3-like: no-op)
  gamma large  -> high scale triggers artifact amplification (v2-like)
  (uncapped + large gamma would recover the paper's flattening)

This turns the three isolated observations into one continuous law without
retraining.

Usage:
    python geotex/explore_residual_scale.py \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/explore_contradiction/residual_scale_v2 \
        --num_objects 6 --num_steps 50
"""
import os
import sys
import json
import copy
import argparse
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from explore_contradiction import (load_model, generate_with_schedule,
                                   compute_probes, make_schedules)

GAMMAS = [0.1, 0.3, 1.0, 3.0]


def snapshot_output_proj(model):
    """Return deep copies of all adapters' output_proj weight+bias."""
    snap = []
    for mod in model.adapters:
        snap.append((mod.output_proj.weight.data.detach().clone(),
                     mod.output_proj.bias.data.detach().clone()))
    return snap


def apply_gamma(model, snap, gamma):
    """Set every adapter's output_proj weight = snapshot * gamma (absolute, not cumulative).

    Setting from the snapshot guarantees each gamma is independent of previous
    iterations — a mul_() on the current weights would accumulate and make the
    effective gammas wrong (e.g. {0.1, 0.03, 0.03, 0.09}).
    """
    with torch.no_grad():
        for mod, (w, b) in zip(model.adapters, snap):
            mod.output_proj.weight.copy_(w * gamma)
            mod.output_proj.bias.copy_(b * gamma)


def restore_snapshot(model, snap):
    with torch.no_grad():
        for mod, (w, b) in zip(model.adapters, snap):
            mod.output_proj.weight.copy_(w)
            mod.output_proj.bias.copy_(b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_objects', type=int, default=6)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading model...")
    model, config = load_model(args.config, args.checkpoint, device)
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    dataset = instantiate_from_config(OmegaConf.load(args.config).data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    SCHEDULES = make_schedules()

    snap = snapshot_output_proj(model)
    # measure the native (gamma=1) residual magnitude per layer for reference
    all_results = {}  # (gamma, sched) -> list of metrics
    print(f"\nResidual spectrum on {num_objects} objects, checkpoint={args.checkpoint}")
    print(f"Gammas: {GAMMAS}, schedules: fixed_low/fixed_high/C3, steps={args.num_steps}, seed=42")
    print("=" * 80)

    from data_utils import prepare_batch, collate_batch
    try:
        for gamma in GAMMAS:
            apply_gamma(model, snap, gamma)
            print(f"\n--- gamma={gamma} ---")
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

                for sched_name in ['fixed_low', 'fixed_high', 'C3_TCAS']:
                    sched_fn = SCHEDULES[sched_name]
                    pred = generate_with_schedule(
                        model, batch, device, weight_dtype, geo_feats,
                        sched_fn, args.num_steps, init_latents.clone(), {}
                    )
                    m = compute_probes(pred, target_imgs, mask)
                    all_results.setdefault((gamma, sched_name), []).append(m)
                torch.cuda.empty_cache()
            # report this gamma
            def agg(s):
                rs = all_results[(gamma, s)]
                return (np.mean([r['fg_ssim'] for r in rs]),
                        np.mean([r['fg_lap_var'] for r in rs]),
                        np.mean([r['psnr'] for r in rs]))
            row = [f"g={gamma}"]
            for s in ['fixed_low', 'fixed_high', 'C3_TCAS']:
                ss, lv, ps = agg(s)
                row.append(f"{s}: SSIM={ss:.3f} Lap={lv:.5f} PSNR={ps:.2f}")
            print("  ".join(row))
    finally:
        restore_snapshot(model, snap)
        print("\nRestored original adapter weights.")

    # summary table
    print("\n" + "=" * 90)
    print("RESIDUAL MAGNITUDE SPECTRUM SUMMARY")
    print("=" * 90)
    print(f"{'gamma':<6} {'schedule':<11} {'FG-SSIM':>7} {'AbsLap':>8} {'LapRatioGT':>10} {'PSNR':>6}")
    summary_rows = []
    for gamma in GAMMAS:
        for sched_name in ['fixed_low', 'fixed_high', 'C3_TCAS']:
            rs = all_results[(gamma, sched_name)]
            lap = [r['fg_lap_var'] for r in rs]
            gt = np.mean([r['gt_lap_var'] for r in rs])
            row = {
                'gamma': gamma, 'schedule': sched_name,
                'fg_ssim_mean': float(np.mean([r['fg_ssim'] for r in rs])),
                'fg_lap_var_mean': float(np.mean(lap)),
                'lap_var_ratio_vs_GT': float(np.mean(lap) / (gt + 1e-8)),
                'psnr_mean': float(np.mean([r['psnr'] for r in rs])),
            }
            summary_rows.append(row)
            print(f"{gamma:<6.1f} {sched_name:<11} {row['fg_ssim_mean']:>7.4f} "
                  f"{row['fg_lap_var_mean']:>8.5f} {row['lap_var_ratio_vs_GT']:>10.3f} {row['psnr_mean']:>6.2f}")

    out = {'checkpoint': args.checkpoint, 'num_objects': num_objects,
           'num_steps': args.num_steps, 'gammas': GAMMAS, 'results': summary_rows}
    with open(os.path.join(args.output_dir, 'residual_scale_summary.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {os.path.join(args.output_dir, 'residual_scale_summary.json')}")
    print("Done.")


if __name__ == '__main__':
    main()
