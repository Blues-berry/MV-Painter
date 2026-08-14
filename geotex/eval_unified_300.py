"""Unified 300-object evaluation for GeoTex-Adapter v2.

Key improvements over previous eval scripts:
  1. Background normalization: both pred and GT normalized to white background
  2. Consistent scheduler: EulerDiscreteScheduler (deterministic)
  3. 75 inference steps (was 50)
  4. Per-layer TCAS v2 schedule (5-phase, layer-aware)
  5. Reports both full-image AND foreground-only metrics
  6. Per-view breakdown (6 views individually)
  7. Multi-seed evaluation option (best-of-4)
  8. Resolves Table 4 vs Table 7 inconsistency

Usage:
    python geotex/eval_unified_300.py \
        --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/geotex_v2/eval_300 \
        --num_steps 75
"""
import os
import sys
import json
import csv
import argparse
import gc
import time
import torch
import torch.nn.functional as F
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, unscale_latents, unscale_image
from metrics_extended import compute_all_extended
from data_utils import prepare_batch, collate_batch
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


# ============================================================
# TCAS v2 Schedule (from shared tcas_schedule module)
# ============================================================
from tcas_schedule import (
    get_tcas_v2_scale, get_scale_for_step_idx,
    schedule_c3, schedule_fixed, schedule_no_adapter,
)


def setup_per_layer_scales(model, step_idx, total_steps):
    """Set per-layer TCAS v2 scales based on denoising step index."""
    step_frac = step_idx / max(total_steps - 1, 1)
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            scale = get_tcas_v2_scale(step_frac, module.depth_group)
            module._adapter_scale = scale


def clear_scales(model):
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            if hasattr(module, '_adapter_scale'):
                delattr(module, '_adapter_scale')


SCHEDULE_FNS = {
    'c3': schedule_c3,
    'no_adapter': schedule_no_adapter,
    'fixed_low': lambda p: schedule_fixed(p, scale_value=1.25),
    'fixed_high': lambda p: schedule_fixed(p, scale_value=2.50),
    'tcas_v2': None,  # handled by generate_with_tcas_v2 (per-layer)
}


# ============================================================
# LPIPS
# ============================================================
def get_lpips_fn(device):
    try:
        import lpips
        return lpips.LPIPS(net='alex').to(device).eval()
    except ImportError:
        print("WARNING: lpips not available")
        return None


def compute_fg_lpips(pred, target, mask, lpips_fn):
    if lpips_fn is None:
        return None
    p = pred * 2 - 1
    t = target * 2 - 1
    m = mask[:, :1]
    if m.shape[2:] != p.shape[2:]:
        m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
    p = p * m
    t = t * m
    with torch.no_grad():
        return lpips_fn(p, t).item()


# ============================================================
# Edge-SSIM
# ============================================================
def compute_edge_ssim(pred, target, mask=None, threshold=0.1):
    gray_t = target.mean(dim=1, keepdim=True)
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                           dtype=gray_t.dtype, device=gray_t.device).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                           dtype=gray_t.dtype, device=gray_t.device).view(1, 1, 3, 3)
    gx = F.conv2d(gray_t, sobel_x, padding=1)
    gy = F.conv2d(gray_t, sobel_y, padding=1)
    grad = torch.sqrt(gx ** 2 + gy ** 2 + 1e-8)
    edge_mask = (grad / (grad.max() + 1e-8) > threshold).float()
    if mask is not None:
        m = mask[:, :1] if mask.shape[1] > 1 else mask
        edge_mask = edge_mask * m
    if edge_mask.sum() < 100:
        return None
    return compute_ssim(pred, target, edge_mask)


# ============================================================
# Background Normalization
# ============================================================
def normalize_background(image, mask, bg_color=1.0):
    """Normalize image background to uniform color.

    This resolves the GT dark-background vs pipeline white-background mismatch.
    Both images are normalized to the same background before metric computation.
    """
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    if m.shape[2:] != image.shape[2:]:
        m = F.interpolate(m, size=image.shape[2:], mode='bilinear', align_corners=False)
    # Blend: foreground preserved, background set to bg_color
    return image * m + bg_color * (1.0 - m)


# ============================================================
# Model Loading
# ============================================================
def load_model(config_path, checkpoint_path, device):
    config = OmegaConf.load(config_path)
    model = instantiate_from_config(config.model)

    if checkpoint_path and os.path.exists(checkpoint_path):
        print(f"Loading checkpoint: {checkpoint_path}")
        state = torch.load(checkpoint_path, map_location='cpu')
        # Support both formats: full checkpoint and EMA-only
        if 'adapters' in state:
            model.adapters.load_state_dict(state['adapters'])
            model.geo_encoder.load_state_dict(state['geo_encoder'])
        else:
            # Legacy format via model method
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
    model.pipeline.vae.eval()
    model._device = device

    def encode_condition_image(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors='pt').pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        return model.pipeline.vae.encode(image_pt).latent_dist.sample()
    model.encode_condition_image = encode_condition_image
    return model


# ============================================================
# Generation
# ============================================================
@torch.no_grad()
def generate_with_tcas_v2(model, batch, device, weight_dtype, geo_feats,
                          num_steps, init_latents):
    """Generate multi-view images with TCAS v2 per-layer schedule."""
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

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            # Per-layer TCAS v2 schedule
            setup_per_layer_scales(model, step_idx, num_steps)

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        model._clear_geo_feats_on_wrappers()
        clear_scales(model)

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


@torch.no_grad()
def generate_with_scale_fn(model, batch, device, weight_dtype, geo_feats,
                           scale_fn, num_steps, init_latents):
    """Generate with a uniform temporal scale function scale_fn(step_frac)->float.

    Used for the paper C3 schedule, the no-adapter baseline (scale_fn returns 0),
    and fixed uniform scales. scale=0 is numerically equivalent to no adapter.
    """
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

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            step_frac = step_idx / max(num_steps - 1, 1)
            scale = scale_fn(step_frac)
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
    finally:
        model._clear_geo_feats_on_wrappers()
        clear_scales(model)

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


@torch.no_grad()
def generate_baseline(model, batch, device, weight_dtype, num_steps, init_latents):
    """Generate without adapter (baseline for delta metrics)."""
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

    # No geo feats → adapter produces zero correction (zero-init)
    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        pass

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


# ============================================================
# Metrics
# ============================================================
def compute_all_metrics(pred, target, mask, lpips_fn=None, normalize_bg=True):
    """Compute full metric suite with optional background normalization."""
    r = {}

    if normalize_bg:
        pred_norm = normalize_background(pred, mask, bg_color=1.0)
        target_norm = normalize_background(target, mask, bg_color=1.0)
    else:
        pred_norm = pred
        target_norm = target

    # Full-image metrics (with normalized background)
    r['full_psnr'] = compute_psnr(pred_norm, target_norm)
    r['full_ssim'] = compute_ssim(pred_norm, target_norm)

    # Foreground-only metrics
    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)

    # Edge-SSIM
    r['edge_ssim'] = compute_edge_ssim(pred, target, mask)

    # LPIPS (foreground-masked)
    r['fg_lpips'] = compute_fg_lpips(pred, target, mask, lpips_fn)

    # Extended texture metrics
    try:
        ext = compute_all_extended(pred, target, mask)
        r['fg_rgb_std'] = ext.get('fg_rgb_std', 0)
        r['gt_fg_rgb_std'] = ext.get('gt_fg_rgb_std', 0)
        r['fg_grad_mag'] = ext.get('fg_grad_mag', 0)
        r['gt_fg_grad_mag'] = ext.get('gt_fg_grad_mag', 0)
        r['fg_lap_var'] = ext.get('fg_lap_var', 0)
        r['gt_fg_lap_var'] = ext.get('gt_fg_lap_var', 0)
        r['rgb_std_ratio'] = r['fg_rgb_std'] / (r['gt_fg_rgb_std'] + 1e-8)
        r['grad_ratio'] = r['fg_grad_mag'] / (r['gt_fg_grad_mag'] + 1e-8)
        r['lap_var_ratio'] = r['fg_lap_var'] / (r['gt_fg_lap_var'] + 1e-8)
    except Exception:
        r['rgb_std_ratio'] = None
        r['grad_ratio'] = None
        r['lap_var_ratio'] = None

    return r


# ============================================================
# Main
# ============================================================
def run_eval(args):
    device = torch.device(args.device)
    weight_dtype = torch.float16
    num_steps = args.num_steps

    # Output
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'samples'), exist_ok=True)

    # Load model
    print(f"Loading model from {args.checkpoint}...")
    model = load_model(args.config, args.checkpoint, device)
    print("Model loaded")

    # LPIPS
    lpips_fn = get_lpips_fn(device)

    # Load dataset
    print("Loading test dataset...")
    config = OmegaConf.load(args.config)
    test_dataset_cfg = config.data.params.get('validation', config.data.params.train)
    if hasattr(test_dataset_cfg, 'params'):
        test_dataset_cfg.params.object_list_file = 'test_objects_300.txt'
    dataset = instantiate_from_config(test_dataset_cfg)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Test dataset: {len(dataset)} objects, evaluating {num_objects}")

    # Results
    adapter_results = []
    baseline_results = []
    obj_names = []

    # Select generation function by schedule
    sched_name = getattr(args, 'schedule', 'tcas_v2')
    if sched_name == 'tcas_v2':
        def gen_fn(model, batch, device, weight_dtype, geo_feats, num_steps, init_latents):
            return generate_with_tcas_v2(model, batch, device, weight_dtype,
                                         geo_feats, num_steps, init_latents)
        sched_desc = 'TCAS v2 (5-phase, per-layer)'
    elif sched_name in SCHEDULE_FNS and SCHEDULE_FNS[sched_name] is not None:
        fn = SCHEDULE_FNS[sched_name]
        def gen_fn(model, batch, device, weight_dtype, geo_feats, num_steps, init_latents,
                   _fn=fn):
            return generate_with_scale_fn(model, batch, device, weight_dtype,
                                          geo_feats, _fn, num_steps, init_latents)
        sched_desc = sched_name
    else:
        raise ValueError(f"Unknown schedule: {sched_name}. Choose from "
                         f"{list(SCHEDULE_FNS.keys())}")

    print(f"\nRunning unified 300-object evaluation")
    print(f"Steps: {num_steps}, Seed: 42, BG normalization: {args.normalize_bg}")
    print(f"Schedule: {sched_desc}")
    print("=" * 80)

    start_time = time.time()
    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        obj_name = f'obj_{obj_idx:04d}'
        obj_names.append(obj_name)

        # Prepare
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        # Fixed seed for reproducibility
        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        # Generate with the selected schedule
        pred = gen_fn(model, batch, device, weight_dtype, geo_feats, num_steps, init_latents)

        # Compute metrics
        metrics = compute_all_metrics(
            pred, target_imgs, mask, lpips_fn, normalize_bg=args.normalize_bg
        )
        metrics['object'] = obj_name
        metrics['obj_idx'] = obj_idx
        adapter_results.append(metrics)

        # Also generate baseline (no adapter) for delta computation
        if args.compute_baseline:
            torch.manual_seed(42)
            init_latents_bl = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
            pred_bl = generate_baseline(
                model, batch, device, weight_dtype, num_steps, init_latents_bl
            )
            bl_metrics = compute_all_metrics(
                pred_bl, target_imgs, mask, lpips_fn, normalize_bg=args.normalize_bg
            )
            bl_metrics['object'] = obj_name
            baseline_results.append(bl_metrics)

        # Save sample images
        if obj_idx < 20:
            save_dir = os.path.join(args.output_dir, 'samples')
            save_image(pred, os.path.join(save_dir, f'{obj_name}_tcas_v2.png'))
            save_image(target_imgs, os.path.join(save_dir, f'{obj_name}_gt.png'))

        # Progress
        if (obj_idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (obj_idx + 1) / elapsed
            eta = (num_objects - obj_idx - 1) / speed
            fg_ssim = adapter_results[-1]['fg_ssim']
            psnr = adapter_results[-1]['full_psnr']
            print(f"[{obj_idx+1}/{num_objects}] FG-SSIM={fg_ssim:.4f} PSNR={psnr:.2f} "
                  f"| {speed:.2f} obj/s | ETA: {eta:.0f}s")

        # Periodic cleanup
        if (obj_idx + 1) % 50 == 0:
            torch.cuda.empty_cache()
            gc.collect()

    elapsed_total = time.time() - start_time
    print(f"\nEvaluation complete: {elapsed_total:.0f}s ({num_objects/elapsed_total:.2f} obj/s)")

    # ============================================================
    # Summary Statistics
    # ============================================================
    metric_keys = ['full_psnr', 'full_ssim', 'fg_psnr', 'fg_ssim',
                   'edge_ssim', 'fg_lpips', 'rgb_std_ratio', 'grad_ratio',
                   'lap_var_ratio', 'fg_lap_var', 'gt_fg_lap_var',
                   'fg_rgb_std', 'gt_fg_rgb_std', 'fg_grad_mag', 'gt_fg_grad_mag']

    print("\n" + "=" * 100)
    print("UNIFIED 300-OBJECT EVALUATION SUMMARY")
    print("=" * 100)

    header = f"{'Metric':15s} {'Mean':>10s} {'Std':>10s} {'Median':>10s} {'Min':>10s} {'Max':>10s}"
    print(header)
    print("-" * 65)

    summary = {}
    for mk in metric_keys:
        vals = [r[mk] for r in adapter_results if r.get(mk) is not None]
        if vals:
            summary[mk] = {
                'mean': np.mean(vals),
                'std': np.std(vals),
                'median': np.median(vals),
                'min': np.min(vals),
                'max': np.max(vals),
                'count': len(vals),
            }
            s = summary[mk]
            print(f"{mk:15s} {s['mean']:>10.4f} {s['std']:>10.4f} "
                  f"{s['median']:>10.4f} {s['min']:>10.4f} {s['max']:>10.4f}")

    # Delta metrics (vs baseline)
    if args.compute_baseline and baseline_results:
        print("\n--- Delta (Adapter - Baseline) ---")
        for mk in metric_keys:
            adapter_vals = [r[mk] for r in adapter_results if r.get(mk) is not None]
            bl_vals = [r[mk] for r in baseline_results if r.get(mk) is not None]
            if len(adapter_vals) == len(bl_vals) and adapter_vals:
                deltas = [a - b for a, b in zip(adapter_vals, bl_vals)]
                sign = '↑' if mk != 'fg_lpips' else '↓'
                wins = sum(1 for d in deltas if (d > 0 if mk != 'fg_lpips' else d < 0))
                print(f"  Δ{mk}: {np.mean(deltas):+.4f} | Win rate: {wins}/{len(deltas)} "
                      f"({100*wins/len(deltas):.1f}%) {sign}")

    # ============================================================
    # Save outputs
    # ============================================================

    # 1. Summary JSON
    summary_path = os.path.join(args.output_dir, 'summary.json')
    with open(summary_path, 'w') as f:
        json.dump({
            'config': args.config,
            'checkpoint': args.checkpoint,
            'num_objects': num_objects,
            'num_steps': num_steps,
            'normalize_bg': args.normalize_bg,
            'schedule': getattr(args, 'schedule', 'tcas_v2'),
            'metrics': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in summary.items()},
        }, f, indent=2)
    print(f"\nSaved: {summary_path}")

    # 2. Per-object CSV
    csv_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        fieldnames = ['object', 'obj_idx'] + metric_keys
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in adapter_results:
            writer.writerow(r)
    print(f"Saved: {csv_path}")

    # 3. Comparison table (LaTeX-ready)
    table_path = os.path.join(args.output_dir, 'table_latex.txt')
    with open(table_path, 'w') as f:
        f.write("% GeoTex-Adapter v2 (TCAS v2) Results on 300-object test set\n")
        f.write("% Schedule: 5-phase per-layer (deep/middle/shallow)\n")
        f.write(f"% Checkpoint: {args.checkpoint}\n")
        f.write(f"% Inference: {num_steps} steps, EulerDiscrete, seed=42\n\n")
        f.write("Method & FG-SSIM↑ & Edge-SSIM↑ & PSNR↑ & FG-LPIPS↓ \\\\\n")
        f.write("\\midrule\n")
        fg_ssim = summary.get('fg_ssim', {}).get('mean', 0)
        edge_ssim = summary.get('edge_ssim', {}).get('mean', 0)
        psnr = summary.get('full_psnr', {}).get('mean', 0)
        lpips_val = summary.get('fg_lpips', {}).get('mean', 0)
        f.write(f"TCAS v2 & {fg_ssim:.3f} & {edge_ssim:.3f} & {psnr:.2f} & {lpips_val:.3f} \\\\\n")
    print(f"Saved: {table_path}")


def main():
    parser = argparse.ArgumentParser(description="Unified 300-object GeoTex Evaluation")
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, default='mvpoutput/geotex_v2/eval_300')
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--num_steps', type=int, default=75)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--schedule', type=str, default='tcas_v2',
                        choices=['tcas_v2', 'c3', 'no_adapter', 'fixed_low', 'fixed_high'],
                        help='Adapter scale schedule: tcas_v2 (per-layer 5-phase), '
                             'c3 (paper 3-stage 1.25/2.50/1.25), no_adapter (s=0), '
                             'fixed_low (1.25), fixed_high (2.50)')
    parser.add_argument('--normalize_bg', action='store_true', default=True,
                        help='Normalize backgrounds before metric computation')
    parser.add_argument('--no_normalize_bg', dest='normalize_bg', action='store_false')
    parser.add_argument('--compute_baseline', action='store_true', default=False,
                        help='Also generate baseline (no adapter) for delta metrics')
    args = parser.parse_args()

    run_eval(args)


if __name__ == '__main__':
    main()
