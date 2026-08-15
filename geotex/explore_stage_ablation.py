"""Stage ablation on v2: locate WHERE high scale damages output.

The paper's core mechanistic claim is "late-stage strong adapter intervention
suppresses texture synthesis." On v2 the symptom is artifact amplification
(SSIM collapse + LapVar rise) rather than flattening. This experiment isolates
the damaging stage on v2 under the CAPPED forward (current eval semantics):

  fixed_low  = 1.25 everywhere
  fixed_high = 2.50 everywhere
  C3         = 1.25 / 2.50 / 1.25  (middle third high)
  early_high = 2.50 only in first 1/3, else 1.25
  mid_high   = 2.50 only in middle 1/3, else 1.25
  late_high  = 2.50 only in last 1/3, else 1.25

If late_high reproduces most of fixed_high's damage -> the "late stage is the
culprit" mechanism survives on v2, only the symptom differs (artifacts not
flattening) -> clean reframe. If early_high is the culprit -> mechanism is
checkpoint-dependent, more disruptive but still interesting.

Usage:
    python geotex/explore_stage_ablation.py \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/explore_contradiction/stage_ablation_v2 \
        --num_objects 6 --num_steps 50
"""
import os
import sys
import json
import argparse
import csv
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from explore_contradiction import (load_model, generate_with_schedule,
                                   compute_probes, make_schedules)


def make_stage_schedules():
    base = make_schedules()

    def stage_high(progress, **kw):
        seg = kw['seg']  # 0=early,1=mid,2=late
        if seg == 0 and progress < 1.0 / 3.0:
            return 2.5
        if seg == 1 and 1.0 / 3.0 <= progress < 2.0 / 3.0:
            return 2.5
        if seg == 2 and progress >= 2.0 / 3.0:
            return 2.5
        return 1.25

    sched = dict(base)
    sched['early_high'] = lambda p, **kw: stage_high(p, seg=0)
    sched['mid_high'] = lambda p, **kw: stage_high(p, seg=1)
    sched['late_high'] = lambda p, **kw: stage_high(p, seg=2)
    return sched


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

    SCHEDULES = make_stage_schedules()
    all_results = {name: [] for name in SCHEDULES}

    print(f"\nStage ablation on {num_objects} objects, checkpoint={args.checkpoint}")
    print(f"Schedules: {list(SCHEDULES.keys())}, steps={args.num_steps}, seed=42")
    print("=" * 80)

    from data_utils import prepare_batch, collate_batch
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

        for sched_name, sched_fn in SCHEDULES.items():
            residual_log = {}
            pred = generate_with_schedule(
                model, batch, device, weight_dtype, geo_feats,
                sched_fn, args.num_steps, init_latents.clone(), residual_log
            )
            m = compute_probes(pred, target_imgs, mask)
            m['object'] = f'obj_{obj_idx:04d}'
            all_results[sched_name].append(m)
        torch.cuda.empty_cache()
        if (obj_idx + 1) % 2 == 0:
            def fmt(n):
                r = all_results[n][-1]
                return f"{r['fg_ssim']:.3f}/{r['fg_lap_var']:.5f}"
            print(f"[{obj_idx+1}/{num_objects}] low:{fmt('fixed_low')} high:{fmt('fixed_high')} "
                  f"early:{fmt('early_high')} mid:{fmt('mid_high')} late:{fmt('late_high')} c3:{fmt('C3_TCAS')}")

    print("\n" + "=" * 90)
    print("STAGE ABLATION SUMMARY")
    print("=" * 90)
    print(f"{'Schedule':<12} {'FG-SSIM':>7} {'PSNR':>6} {'AbsLap':>8} {'LapRatioGT':>10} {'LapCorr':>7} {'MAE':>6}")
    summary_rows = []
    for sched_name in SCHEDULES:
        results = all_results[sched_name]
        lap_vars = [r['fg_lap_var'] for r in results]
        gt_laps = [r['gt_lap_var'] for r in results]
        row = {
            'schedule': sched_name,
            'fg_ssim_mean': float(np.mean([r['fg_ssim'] for r in results])),
            'psnr_mean': float(np.mean([r['psnr'] for r in results])),
            'fg_lap_var_mean': float(np.mean(lap_vars)),
            'gt_lap_var_mean': float(np.mean(gt_laps)),
            'lap_var_ratio_vs_GT': float(np.mean(lap_vars) / (np.mean(gt_laps) + 1e-8)),
            'fg_lap_corr_mean': float(np.nanmean([r['fg_lap_corr'] for r in results])),
            'fg_mae_mean': float(np.mean([r['fg_mae'] for r in results])),
        }
        summary_rows.append(row)
        print(f"{sched_name:<12} {row['fg_ssim_mean']:>7.4f} {row['psnr_mean']:>6.2f} "
              f"{row['fg_lap_var_mean']:>8.5f} {row['lap_var_ratio_vs_GT']:>10.3f} "
              f"{row['fg_lap_corr_mean']:>7.2f} {row['fg_mae_mean']:>6.3f}")

    base_lap = {r['schedule']: r['fg_lap_var_mean'] for r in summary_rows}
    if base_lap.get('fixed_low', 0) > 0:
        print("\nLapVar ratio vs fixed_low (paper-style normalization):")
        for r in summary_rows:
            print(f"  {r['schedule']:<12} {base_lap[r['schedule']] / base_lap['fixed_low']:.3f}")

    out = {'checkpoint': args.checkpoint, 'num_objects': num_objects,
           'num_steps': args.num_steps, 'results': summary_rows}
    with open(os.path.join(args.output_dir, 'stage_ablation_summary.json'), 'w') as f:
        json.dump(out, f, indent=2)
    # Keep the paired observations.  The stage utility is a within-object
    # comparison, so means alone are insufficient for uncertainty estimates.
    per_object_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    metric_names = ('fg_ssim', 'psnr', 'fg_lap_var', 'fg_lap_corr', 'fg_mae')
    fieldnames = ['object', 'schedule', *metric_names]
    with open(per_object_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for schedule, rows in all_results.items():
            for row in rows:
                writer.writerow({
                    'object': row['object'], 'schedule': schedule,
                    **{name: row[name] for name in metric_names},
                })
    print(f"Saved: {per_object_path}")
    print(f"\nSaved: {os.path.join(args.output_dir, 'stage_ablation_summary.json')}")
    print("Done.")


if __name__ == '__main__':
    main()
