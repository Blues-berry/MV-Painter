"""Residual-Normalized adaptive schedule, via fixed per-wrapper scale conversion.

Motivation (find.md R11): a fixed scale is ineffective because the trained
adapter residual magnitude differs enormously across checkpoints (v3 shallow
~0.06 vs v2 ~0.5), so the same scale produces unpredictable intervention
strength — no-op on weak adapters, artifact amplification on strong ones.

Idea (training-free, no forward monkey-patch): measure each wrapper's mean raw
correction norm (calibrated from a fixed_low pass, raw = scaled/eff_scale),
then express "intervention strength" as a TARGET NORM per (stage, depth) and
convert to a per-wrapper scale each step:

    scale(depth, stage) = target_norm(depth, stage) / ref_raw_norm(depth)

Because scale is per-wrapper, it is applied through the model's normal
`_adapter_scale` path (capped by LAYER_MAX_SCALES) — zero memory overhead.

  norm_flat: target = ref_norm(depth)          (constant, which becomes scale=1.0)
  norm_c3:   target = ref_norm(depth)*k(stage)  k=[0.6, 1.4, 0.6]  low-high-low

The claim to verify: normalizing to a reference intervention strength makes the
schedule adapter-invariant — on weak adapters (v3) it restores effective
correction (no longer no-op), on strong adapters (v2) it avoids over-intervention
(no artifact amplification) while keeping the temporal structure.

Usage:
    python geotex/explore_norm_schedule.py \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/explore_contradiction/norm_schedule_v2 \
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

STAGE_BOUNDS = {'early': (0.0, 1.0 / 3.0), 'mid': (1.0 / 3.0, 2.0 / 3.0),
                'late': (2.0 / 3.0, 1.0)}
# per-depth, per-stage multiplier on the reference norm target.
# deep/middle (geometry layers) get stronger correction; shallow (texture) stays weak.
NORM_K = {
    'norm_flat': {'deep': {'early': 1.0, 'mid': 1.0, 'late': 1.0},
                  'middle': {'early': 1.0, 'mid': 1.0, 'late': 1.0},
                  'shallow': {'early': 1.0, 'mid': 1.0, 'late': 1.0}},
    'norm_c3': {'deep': {'early': 0.6, 'mid': 1.4, 'late': 0.6},
                'middle': {'early': 0.6, 'mid': 1.4, 'late': 0.6},
                'shallow': {'early': 0.4, 'mid': 0.8, 'late': 0.4}},
}


def stage_of(progress):
    for st, (lo, hi) in STAGE_BOUNDS.items():
        if lo <= progress < hi:
            return st
    return 'late'


def calibrate_raw_norms(model, batch, device, weight_dtype, geo_feats,
                        init_latents, num_steps):
    """Run fixed_low once; return (per-(stage,depth) mean raw L2 norm, pred).

    residual_log records scaled correction stats; raw_norm = l2 / eff_scale
    (eff_scale is the applied min(_adapter_scale, _max_scale), so this inverts
    the cap correctly). The pred is the fixed_low baseline (reused).
    """
    sched_fn = make_schedules()['fixed_low']
    residual_log = {}
    pred = generate_with_schedule(model, batch, device, weight_dtype, geo_feats,
                                  sched_fn, num_steps, init_latents.clone(), residual_log)
    agg = {}
    for step_idx, entries in residual_log.items():
        st = stage_of(step_idx / max(num_steps - 1, 1))
        for ai, e in entries.items():
            depth = e['depth']
            raw_l2 = e['l2'] / (e['eff_scale'] + 1e-8)
            agg.setdefault(st, {}).setdefault(depth, []).append(raw_l2)
    ref = {}
    for st in agg:
        ref[st] = {d: float(np.mean(v)) for d, v in agg[st].items()}
    return ref, pred, summarize_intervention(residual_log, num_steps)


def make_norm_schedules(raw_norms, k, abs_targets=None):
    """Return schedule fn: progress -> {depth_group: scale}.

    scale(d, st) = target(d, st) / raw_norm(d)

    - abs_targets is None (default): target = raw_norm * k  ->  scale = k
      (relative normalization; only rescales the fixed_low profile, does NOT
      change intervention strength, hence cannot revive a no-op adapter).
    - abs_targets given (absolute normalization): target = abs_targets * k,
      with abs_targets taken from a REFERENCE checkpoint's calibrated raw norm.
      Then scale = abs_targets*k / raw_norm -> the applied intervention strength
      (scale * raw_norm) equals abs_targets*k regardless of this checkpoint's
      own residual magnitude — the training-free cross-adapter normalization.
    """
    def make(k_depth):
        def sched(progress, **kw):
            st = stage_of(progress)
            out = {}
            for d in raw_norms[st]:
                base = abs_targets[st].get(d, 1.0) if abs_targets else raw_norms[st][d]
                out[d] = base * k_depth[d][st] / (raw_norms[st][d] + 1e-8)
            return out
        return sched
    return {name: make(k) for name, k in NORM_K.items() if k is not None}


def summarize_intervention(residual_log, num_steps):
    """Return stage/depth means needed to audit normalization claims."""
    rows = []
    for step_idx, entries in residual_log.items():
        stage = stage_of(step_idx / max(num_steps - 1, 1))
        for entry in entries.values():
            raw_l2 = entry['l2'] / (entry['eff_scale'] + 1e-8)
            rows.append({
                'stage': stage,
                'depth': entry['depth'],
                'raw_l2': raw_l2,
                'requested_scale': entry['scale'],
                'effective_scale': entry['eff_scale'],
                'applied_l2': entry['l2'],
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_objects', type=int, default=6)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--target_json', type=str, default=None,
                        help='Path to a norm_schedule_summary.json from a reference '
                             'checkpoint; its ref_norms become the ABSOLUTE target for '
                             'cross-checkpoint normalization. If None, uses the '
                             'checkpoint\'s own fixed_low raw norms (relative only).')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading model...")
    model, config = load_model(args.config, args.checkpoint, device)
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from data_utils import prepare_batch, collate_batch
    dataset = instantiate_from_config(OmegaConf.load(args.config).data.params.validation)
    num_objects = min(args.num_objects, len(dataset))

    # ---- schedules ----
    SCHEDULES = make_schedules()
    # fixed_low_weak: uniform scale 1.0 — same intervention strength as norm_flat's
    # deep/middle (scale 1.0) but WITHOUT any normalization profile. This is the
    # control that distinguishes "normalization profile matters" from
    # "merely weaker intervention helps" (code-reviewer concern).
    SCHEDULES['fixed_low_weak'] = lambda p, **kw: 1.0
    schedules_to_run = ['fixed_low', 'fixed_low_weak', 'fixed_high', 'C3_TCAS',
                        'norm_flat', 'norm_c3']

    all_results = {s: [] for s in schedules_to_run}
    intervention_rows = []
    # absolute targets from a reference checkpoint (cross-checkpoint normalization)
    abs_targets = None
    if args.target_json:
        ref = json.load(open(args.target_json))
        abs_targets = ref['ref_norms']
        print(f"Using ABSOLUTE targets from {args.target_json}")
    print(f"\nNormalized schedule on {num_objects} objects, checkpoint={args.checkpoint}")
    print(f"Schedules: {schedules_to_run}, steps={args.num_steps}, seed=42")
    print("=" * 80)

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

        # calibrate ref norms for THIS object via fixed_low (also its baseline)
        ref_norms, pred_fl, fixed_low_intervention = calibrate_raw_norms(
            model, batch, device, weight_dtype, geo_feats, init_latents, args.num_steps)
        m_fl = compute_probes(pred_fl, target_imgs, mask)
        m_fl['object'] = f'obj_{obj_idx:04d}'
        all_results['fixed_low'].append(m_fl)
        for row in fixed_low_intervention:
            row.update({'object': f'obj_{obj_idx:04d}', 'schedule': 'fixed_low'})
            intervention_rows.append(row)
        if obj_idx == 0:
            print("  obj0 ref raw L2 norm by (stage, depth):")
            for st in ref_norms:
                print(f"    {st}: {json.dumps({k: round(v, 4) for k, v in ref_norms[st].items()})}")
        del pred_fl, m_fl

        norm_scheds = make_norm_schedules(ref_norms, NORM_K, abs_targets)
        for sched_name in schedules_to_run:
            if sched_name == 'fixed_low':
                continue
            sched_fn = SCHEDULES[sched_name] if sched_name in SCHEDULES else norm_scheds[sched_name]
            torch.manual_seed(42)  # align RNG so all schedules share cond latent/ref noise
            residual_log = {}
            pred = generate_with_schedule(
                model, batch, device, weight_dtype, geo_feats,
                sched_fn, args.num_steps, init_latents.clone(), residual_log)
            m = compute_probes(pred, target_imgs, mask)
            m['object'] = f'obj_{obj_idx:04d}'
            all_results[sched_name].append(m)
            for row in summarize_intervention(residual_log, args.num_steps):
                row.update({'object': f'obj_{obj_idx:04d}', 'schedule': sched_name})
                intervention_rows.append(row)
            del pred, m
            torch.cuda.empty_cache()
        if (obj_idx + 1) % 2 == 0:
            def fmt(n):
                r = all_results[n][-1]
                return f"{r['fg_ssim']:.3f}/{r['fg_lap_var']:.5f}"
            print(f"[{obj_idx+1}/{num_objects}] " + " ".join(
                f"{s}:{fmt(s)}" for s in schedules_to_run))

    # ---- report ----
    print("\n" + "=" * 100)
    print("NORMALIZED SCHEDULE SUMMARY")
    print("=" * 100)
    print(f"{'Schedule':<12} {'FG-SSIM':>7} {'PSNR':>6} {'AbsLap':>8} {'LapRatioGT':>10} {'LapCorr':>7}")
    summary = []
    for sched_name in schedules_to_run:
        rs = all_results[sched_name]
        lap = [r['fg_lap_var'] for r in rs]
        gt = np.mean([r['gt_lap_var'] for r in rs])
        row = {
            'schedule': sched_name,
            'fg_ssim_mean': float(np.mean([r['fg_ssim'] for r in rs])),
            'psnr_mean': float(np.mean([r['psnr'] for r in rs])),
            'fg_lap_var_mean': float(np.mean(lap)),
            'gt_lap_var_mean': float(gt),
            'lap_var_ratio_vs_GT': float(np.mean(lap) / (gt + 1e-8)),
            'fg_lap_corr_mean': float(np.nanmean([r['fg_lap_corr'] for r in rs])),
        }
        summary.append(row)
        print(f"{sched_name:<12} {row['fg_ssim_mean']:>7.4f} {row['psnr_mean']:>6.2f} "
              f"{row['fg_lap_var_mean']:>8.5f} {row['lap_var_ratio_vs_GT']:>10.3f} "
              f"{row['fg_lap_corr_mean']:>7.2f}")

    out = {'checkpoint': args.checkpoint, 'num_objects': num_objects,
           'num_steps': args.num_steps, 'ref_norms': ref_norms, 'results': summary}
    with open(os.path.join(args.output_dir, 'norm_schedule_summary.json'), 'w') as f:
        json.dump(out, f, indent=2)
    metrics_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    metric_fields = ['object', 'schedule', 'fg_ssim', 'psnr', 'fg_lap_var',
                     'fg_lap_corr', 'fg_mae']
    with open(metrics_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        for schedule, rows in all_results.items():
            for row in rows:
                writer.writerow({'object': row.get('object', ''),
                                 'schedule': schedule,
                                 **{k: row[k] for k in metric_fields[2:]}})
    intervention_path = os.path.join(args.output_dir, 'intervention_stats.csv')
    intervention_fields = ['object', 'schedule', 'stage', 'depth', 'raw_l2',
                           'requested_scale', 'effective_scale', 'applied_l2']
    with open(intervention_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=intervention_fields)
        writer.writeheader()
        writer.writerows(intervention_rows)
    print(f"\nSaved: {os.path.join(args.output_dir, 'norm_schedule_summary.json')}")
    print(f"Saved: {metrics_path}")
    print(f"Saved: {intervention_path}")
    print("Done.")


if __name__ == '__main__':
    main()
