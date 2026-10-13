"""Explore the fixed_high vs C3 LapVar contradiction from objective facts.

Motivation (from find.md planning):
  - Paper's 300-obj texture table (base adapter): s=2.50 LapVar < s=1.25 (flattening).
  - Newer 24-obj / 300-obj evals on geotex_v2 checkpoint: s=2.50 LapVar >> s=1.25 (amplification).
  - Question: is fixed_high's higher absolute LapVar on the v2/v3 checkpoint
    *artifact amplification* (high-freq noise / wrong edges / ringing) or
    *real texture recovery*? And how do per-layer adapter residual norms differ
    between v2 (no anticollapse) and v3 (shallow cap 0.1 + output_proj clamp)?

This script runs the SAME object list on a chosen checkpoint and simultaneously
outputs, for each schedule (no_adapter / fixed_low / fixed_high / C3_TCAS):
  1. per-layer adapter residual norms over denoising steps (deep/middle/shallow)
  2. absolute FG LapVar + GT LapVar (+ ratios both vs GT and vs s=1.25)
  3. FG-SSIM / PSNR / RGB Std / Grad Mag
  4. objective artifact-vs-detail probes:
       - FG pearson corr between |lap(pred)| and |lap(GT)|  (high = real detail)
       - excess-HF fraction & mean excess where |lap(pred)| > |lap(GT)|
       - |pred-GT| masked error, |lap(pred)| heatmaps saved as PNGs
  5. saves high-freq / error / prediction / GT / mask PNGs for the first objects

Usage:
    python geotex/explore_contradiction.py \
        --checkpoint mvpoutput/geotex_v3_anticollapse/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/explore_contradiction/v3 \
        --num_objects 8 --num_steps 50
"""
import os
import sys
import json
import math
import argparse
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, unscale_latents, unscale_image
from metrics_extended import (fg_laplacian_variance, fg_rgb_std,
                              fg_gradient_magnitude, fg_hf_energy)
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
from data_utils import prepare_batch, collate_batch

LAP_KERNEL = torch.tensor([[0, 1, 0], [1, -4, 1], [0, 1, 0]],
                          dtype=torch.float32).view(1, 1, 3, 3)


# ============================================================
# Schedules (reuse eval_schedule_comparison semantics)
# ============================================================

def schedule_fixed(progress, **kw):
    return kw['scale_value']


def schedule_c3(progress, **kw):
    if progress < 1.0 / 3.0:
        return kw['s_low']
    elif progress < 2.0 / 3.0:
        return kw['s_high']
    return kw['s_low']


def schedule_no_adapter(progress, **kw):
    return 0.0


def make_schedules():
    return {
        'no_adapter': lambda p, **kw: schedule_no_adapter(p, **kw),
        'fixed_low': lambda p, **kw: schedule_fixed(p, **kw, scale_value=1.25),
        'fixed_high': lambda p, **kw: schedule_fixed(p, **kw, scale_value=2.50),
        'C3_TCAS': lambda p, **kw: schedule_c3(p, **kw, s_low=1.25, s_high=2.50),
    }


# ============================================================
# Model loading (same as eval_schedule_comparison)
# ============================================================

def load_model(config_path, checkpoint_path, device):
    config = OmegaConf.load(config_path)
    model = instantiate_from_config(config.model)

    if checkpoint_path and os.path.exists(checkpoint_path):
        print(f"Loading checkpoint: {checkpoint_path}")
        state = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        if 'adapters' in state:
            model.adapters.load_state_dict(state['adapters'])
            model.geo_encoder.load_state_dict(state['geo_encoder'])
        else:
            model.load_geotex_weights(checkpoint_path)

    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae.to(device).to(dtype=torch.float16)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')
    model.unet.eval()
    model.pipeline.vae.eval()
    model._device = device

    def encode_condition_image(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors='pt').pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        return model.pipeline.vae.encode(image_pt).latent_dist.sample()
    model.encode_condition_image = encode_condition_image
    return model, config


# ============================================================
# Generation with residual logging
# ============================================================

@torch.no_grad()
def generate_with_schedule(model, batch, device, weight_dtype, geo_feats,
                           schedule_fn, num_steps, init_latents, residual_log):
    """Generate multi-view images; residual_log[step_idx] gets per-wrapper stats."""
    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
    prompt_embeds = uc_text_emb + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}

    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)
    latents = init_latents * scheduler.init_noise_sigma
    sigmas = scheduler.sigmas.cpu().numpy()
    sigma_max = float(sigmas[0]) if len(sigmas) else 1.0

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    log_snr_min = -2.0 * math.log10(max(sigma_max, 1e-6))
    log_snr_max = -2.0 * math.log10(max(float(sigmas[-2]) if len(sigmas) > 1 else 0.05, 1e-6))
    log_snr_span = max(log_snr_max - log_snr_min, 1e-6)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            progress = step_idx / max(num_steps - 1, 1)
            sigma = float(sigmas[step_idx]) if step_idx < len(sigmas) else float(sigmas[-1])
            scale = schedule_fn(progress)
            if isinstance(scale, dict):
                # per-layer-group schedule
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        module._adapter_scale = scale.get(module.depth_group, 1.0)
            else:
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        module._adapter_scale = scale

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]

            # Log per-wrapper scaled residual norms for this step
            entry = {}
            for module in model.unet.modules():
                if isinstance(module, GeoTexResnetWrapper):
                    c = module._last_correction
                    if c is not None:
                        cf = c.detach().float()
                        entry[module.adapter_idx] = {
                            'depth': module.depth_group,
                            'l2': float(cf.norm()),
                            'mean_abs': float(cf.abs().mean()),
                            'max_abs': float(cf.abs().max()),
                            'h': cf.shape[2],
                            'w': cf.shape[3],
                            'scale': float(getattr(module, '_adapter_scale', 0.0)),
                            'eff_scale': float(min(getattr(module, '_adapter_scale', 0.0),
                                                   module._max_scale)),
                        }
            residual_log[step_idx] = entry
    finally:
        model._clear_geo_feats_on_wrappers()
        for module in model.unet.modules():
            if isinstance(module, GeoTexResnetWrapper):
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


# ============================================================
# Metrics + artifact-vs-detail probes
# ============================================================

def normalize_background(image, mask, bg_color=1.0):
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    if m.shape[2:] != image.shape[2:]:
        m = F.interpolate(m, size=image.shape[2:], mode='bilinear', align_corners=False)
    return image * m + bg_color * (1.0 - m)


def lap_maps(pred, target, mask):
    """Return |lap(pred)|, |lap(target)|, FG mask tensor on pred grid (N,1,H,W)."""
    gray_p = pred.mean(dim=1, keepdim=True).float()
    gray_t = target.mean(dim=1, keepdim=True).float()
    lap_p = F.conv2d(gray_p, LAP_KERNEL.to(pred.device), padding=1)
    lap_t = F.conv2d(gray_t, LAP_KERNEL.to(pred.device), padding=1)
    m = mask[:, :1].float()
    if m.shape[2:] != pred.shape[2:]:
        m = F.interpolate(m, size=pred.shape[2:], mode='bilinear', align_corners=False)
    return lap_p.abs(), lap_t.abs(), (m > 0.5)


def pearson_fg(a, b, fg):
    """Pearson correlation between a,b over FG pixels (a,b float, fg bool (N,1,H,W))."""
    a_f, b_f = a[fg], b[fg]
    if a_f.numel() < 10:
        return float('nan')
    if a_f.std() < 1e-9 or b_f.std() < 1e-9:
        return float('nan')
    return float(torch.corrcoef(torch.stack([a_f.flatten(), b_f.flatten()]))[0, 1].item())


def boundary_band(mask, k=3):
    """Thin band along the FG silhouette: dilated FG & ~eroded FG. Bool (N,1,H,W)."""
    m = mask[:, :1].float()
    kd = k
    dil = F.max_pool2d(m, kd, stride=1, padding=kd // 2)
    ero = -F.max_pool2d(-m, kd, stride=1, padding=kd // 2)
    return (dil > 0.5) & ~(ero > 0.5)


def compute_probes(pred, target, mask):
    """Absolute metrics + artifact-vs-detail probes."""
    pred_norm = normalize_background(pred, mask, bg_color=1.0)
    target_norm = normalize_background(target, mask, bg_color=1.0)

    r = {}
    r['fg_ssim'] = float(compute_ssim(pred, target, mask))
    r['psnr'] = float(compute_psnr(pred_norm, target_norm))
    r['fg_lap_var'] = float(fg_laplacian_variance(pred, mask))
    r['gt_lap_var'] = float(fg_laplacian_variance(target, mask))
    r['fg_rgb_std'] = float(fg_rgb_std(pred, mask))
    r['gt_rgb_std'] = float(fg_rgb_std(target, mask))
    r['fg_grad_mag'] = float(fg_gradient_magnitude(pred, mask))
    r['gt_grad_mag'] = float(fg_gradient_magnitude(target, mask))
    r['hf_energy'] = float(fg_hf_energy(pred, mask))
    r['gt_hf_energy'] = float(fg_hf_energy(target, mask))

    # artifact vs detail probes
    lap_p, lap_t, fg = lap_maps(pred, target, mask)
    r['fg_lap_corr'] = pearson_fg(lap_p, lap_t, fg)          # high -> real detail
    # excess HF: pred lap clearly above GT lap
    excess = (lap_p - lap_t) * fg.float()
    r['excess_hf_mean'] = float(excess.clamp(min=0).mean())  # mean of max(0, |lapP|-|lapT|)
    over = (lap_p > lap_t + 1e-4) & fg
    r['excess_hf_frac'] = float(over.float().mean())          # frac of all pixels
    # error magnitude in FG
    err = (pred - target).abs()
    r['fg_mae'] = float((err * fg.float()).sum() / (fg.float().sum() + 1e-8))
    r['gt_lap_map_sum'] = float(lap_t[fg].sum())
    r['pred_lap_map_sum'] = float(lap_p[fg].sum())
    # edge-band (silhouette) concentration of high-frequency response.
    # Ringing / boundary artifacts concentrate |lap| right on the silhouette band.
    band = boundary_band(mask)
    lp_fg = lap_p[fg]; lp_band = lap_p[band]
    lt_fg = lap_t[fg]; lt_band = lap_t[band]
    r['pred_hf_boundary_frac'] = float(lp_band.sum() / (lp_fg.sum() + 1e-8))
    r['gt_hf_boundary_frac'] = float(lt_band.sum() / (lt_fg.sum() + 1e-8))
    return r


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_objects', type=int, default=8)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--save_maps', type=int, default=3, help='save PNG maps for first N objects')
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading model...")
    model, config = load_model(args.config, args.checkpoint, device)
    print("Model loaded.")

    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))

    SCHEDULES = make_schedules()
    all_results = {name: [] for name in SCHEDULES}
    all_residuals = {name: [] for name in SCHEDULES}  # per object per step

    print(f"\nExploring contradiction on {num_objects} objects, checkpoint={args.checkpoint}")
    print(f"Schedules: {list(SCHEDULES.keys())}, steps={args.num_steps}, seed=42")
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

        for sched_name, sched_fn in SCHEDULES.items():
            residual_log = {}
            pred = generate_with_schedule(
                model, batch, device, weight_dtype, geo_feats,
                sched_fn, args.num_steps, init_latents.clone(), residual_log
            )
            m = compute_probes(pred, target_imgs, mask)
            m['object'] = f'obj_{obj_idx:04d}'
            all_results[sched_name].append(m)
            all_residuals[sched_name].append(residual_log)

            # Save maps for first few objects
            if obj_idx < args.save_maps:
                save_dir = os.path.join(args.output_dir, 'maps')
                os.makedirs(save_dir, exist_ok=True)
                tag = f'obj{obj_idx:02d}_{sched_name}'
                save_image(pred, os.path.join(save_dir, f'{tag}_pred.png'))
                save_image(target_imgs, os.path.join(save_dir, f'{tag}_gt.png'))
                save_image(mask[:, :1] if mask.shape[1] > 1 else mask,
                           os.path.join(save_dir, f'{tag}_mask.png'))
                lap_p, lap_t, fg = lap_maps(pred, target_imgs, mask)
                # heatmaps normalized independently for visibility
                def normmap(x):
                    xm = x * fg.float()
                    return (xm - xm.min()) / (xm.max() - xm.min() + 1e-8)
                save_image(normmap(lap_p), os.path.join(save_dir, f'{tag}_lappred.png'))
                save_image(normmap(lap_t), os.path.join(save_dir, f'{tag}_lapgt.png'))
                save_image(normmap((lap_p - lap_t)), os.path.join(save_dir, f'{tag}_lapdiff.png'))
                err = (pred - target_imgs).abs()
                save_image(normmap(err), os.path.join(save_dir, f'{tag}_err.png'))

        # Progress
        if (obj_idx + 1) % 2 == 0:
            def fmt(name):
                r = all_results[name][-1]
                return f"SSIM={r['fg_ssim']:.4f} Lap={r['fg_lap_var']:.5f} corr={r['fg_lap_corr']:.2f}"
            print(f"[{obj_idx+1}/{num_objects}] low:{fmt('fixed_low')} | high:{fmt('fixed_high')} | c3:{fmt('C3_TCAS')}")
        torch.cuda.empty_cache()

    # ============================================================
    # Aggregation
    # ============================================================
    print("\n" + "=" * 100)
    print("CONTRADICTION EXPLORATION SUMMARY")
    print("=" * 100)

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
            'lap_var_ratio_vs_GT_ratioofmeans': float(np.mean(lap_vars) / (np.mean(gt_laps) + 1e-8)),
            'lap_var_ratio_vs_GT_meanofratios': float(np.mean([r['fg_lap_var'] / (r['gt_lap_var'] + 1e-8) for r in results])),
            'fg_rgb_std_mean': float(np.mean([r['fg_rgb_std'] for r in results])),
            'gt_rgb_std_mean': float(np.mean([r['gt_rgb_std'] for r in results])),
            'fg_grad_mag_mean': float(np.mean([r['fg_grad_mag'] for r in results])),
            'hf_energy_mean': float(np.mean([r['hf_energy'] for r in results])),
            # artifact probes
            'fg_lap_corr_mean': float(np.nanmean([r['fg_lap_corr'] for r in results])),
            'excess_hf_mean': float(np.mean([r['excess_hf_mean'] for r in results])),
            'excess_hf_frac_mean': float(np.mean([r['excess_hf_frac'] for r in results])),
            'fg_mae_mean': float(np.mean([r['fg_mae'] for r in results])),
            'pred_hf_boundary_frac_mean': float(np.mean([r['pred_hf_boundary_frac'] for r in results])),
            'gt_hf_boundary_frac_mean': float(np.mean([r['gt_hf_boundary_frac'] for r in results])),
        }
        summary_rows.append(row)

    hdr = (f"{'Schedule':<12} {'FG-SSIM':>7} {'PSNR':>6} {'AbsLap':>8} {'LapRatioGT':>10} "
           f"{'LapCorr':>7} {'BndHF':>6} {'MAE':>6}")
    print(hdr)
    print("-" * 95)
    for r in summary_rows:
        print(f"{r['schedule']:<12} {r['fg_ssim_mean']:>7.4f} {r['psnr_mean']:>6.2f} "
              f"{r['fg_lap_var_mean']:>8.5f} {r['lap_var_ratio_vs_GT_meanofratios']:>10.3f} "
              f"{r['fg_lap_corr_mean']:>7.2f} {r['pred_hf_boundary_frac_mean']:>6.3f} {r['fg_mae_mean']:>6.4f}")

    # Per-stage residual norms (early/mid/late thirds), aggregated over wrappers by depth
    print("\nPer-layer adapter residual norm (mean scaled-correction |.| across steps):")
    print(f"{'Schedule':<12} {'layer':<8} {'early':>8} {'mid':>8} {'late':>8} {'max_abs':>9}")
    residual_agg = {}
    for sched_name in SCHEDULES:
        residual_agg[sched_name] = {}
        for obj_res in all_residuals[sched_name]:
            for step_idx, entries in obj_res.items():
                stage = ('early' if step_idx < args.num_steps / 3
                         else ('mid' if step_idx < 2 * args.num_steps / 3 else 'late'))
                for ai, e in entries.items():
                    key = e['depth']
                    d = residual_agg[sched_name].setdefault(key, {'early': [], 'mid': [], 'late': [], 'max': []})
                    d[stage].append(e['mean_abs'])
                    d['max'].append(e['max_abs'])
        for depth in ['deep', 'middle', 'shallow']:
            d = residual_agg[sched_name].get(depth)
            if d:
                print(f"{sched_name:<12} {depth:<8} "
                      f"{np.mean(d['early']):>8.5f} {np.mean(d['mid']):>8.5f} "
                      f"{np.mean(d['late']):>8.5f} {np.max(d['max']):>9.5f}")

    # ratio vs s=1.25 (paper style)
    base_lap = {r['schedule']: r['fg_lap_var_mean'] for r in summary_rows}
    if 'fixed_low' in base_lap and base_lap['fixed_low'] > 0:
        print("\nLapVar ratio vs s=1.25 (paper-style normalization):")
        for r in summary_rows:
            print(f"  {r['schedule']:<12} {base_lap[r['schedule']] / base_lap['fixed_low']:.3f}")

    out = {
        'checkpoint': args.checkpoint,
        'num_objects': num_objects,
        'num_steps': args.num_steps,
        'results': summary_rows,
        'residual_agg': {s: {d: {k: (float(np.mean(v)) if k != 'max' else float(np.max(v)))
                                  for k, v in layers.items()}
                             for d, layers in residual_agg[s].items()} for s in SCHEDULES},
    }
    with open(os.path.join(args.output_dir, 'explore_summary.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {os.path.join(args.output_dir, 'explore_summary.json')}")
    print("Done.")


if __name__ == '__main__':
    main()
