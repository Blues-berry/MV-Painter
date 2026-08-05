"""GeoTex-Adapter v2 Training Script.

Key improvements over v1:
  1. LR warmup + cosine decay (500 warmup → peak 3e-4 → cosine to 1e-5)
  2. EMA (decay=0.9995) for stable inference weights
  3. Gradient accumulation (effective batch_size=4)
  4. TCAS-aware training: apply scale during training to match inference
  5. Write/read pass separation: adapter only active on read pass
  6. Per-layer scale caps (shallow=0.8, middle=3.5, deep=3.0)
  7. Enhanced loss: higher foreground/edge weights + pixel-space SSIM every N steps
  8. Expanded dataset: 1706 objects (all minus 300 test)

Usage:
    python geotex/train_v2.py \
        --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
        --output_dir mvpoutput/geotex_v2 \
        --steps 10000
"""
import os
import sys
import copy
import math
import time
import argparse
import json
import gc
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from mvpainter.model_unet_geotex import GeoTexResnetWrapper, compute_ssim_loss, compute_edge_mask
from metrics import scale_latents, unscale_latents, unscale_image, compute_psnr, compute_ssim


# ============================================================
# EMA
# ============================================================
class EMA:
    """Exponential Moving Average for model parameters."""

    def __init__(self, parameters, decay=0.9995):
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        for name, p in parameters:
            if p.requires_grad:
                self.shadow[name] = p.data.clone()

    @torch.no_grad()
    def update(self, parameters):
        for name, p in parameters:
            if name in self.shadow:
                self.shadow[name].mul_(self.decay).add_(p.data, alpha=1.0 - self.decay)

    def apply_shadow(self, parameters):
        """Replace model params with EMA values (for eval)."""
        for name, p in parameters:
            if name in self.shadow:
                self.backup[name] = p.data.clone()
                p.data.copy_(self.shadow[name])

    def restore(self, parameters):
        """Restore original model params (after eval)."""
        for name, p in parameters:
            if name in self.backup:
                p.data.copy_(self.backup[name])
        self.backup = {}

    def state_dict(self):
        return {'shadow': self.shadow, 'decay': self.decay}

    def load_state_dict(self, state_dict):
        self.shadow = state_dict['shadow']
        self.decay = state_dict.get('decay', self.decay)


# ============================================================
# LR Schedule
# ============================================================
def get_lr(step, total_steps, warmup_steps, peak_lr, min_lr):
    """Linear warmup + cosine decay schedule."""
    if step < warmup_steps:
        return min_lr + (peak_lr - min_lr) * step / warmup_steps
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return min_lr + 0.5 * (peak_lr - min_lr) * (1 + math.cos(math.pi * progress))


# ============================================================
# TCAS Schedule (5-phase, per-layer)
# ============================================================
# Block depth group → name mapping
BLOCK_DEPTH_MAP = {
    'mid': 'deep',
    'up_0': 'deep',
    'up_1': 'middle',
    'up_2': 'shallow',
}

# 5-phase schedule per layer group
# Phases: [0-15%, 15-35%, 35-65%, 65-85%, 85-100%]
TCAS_V2_SCHEDULES = {
    'deep':    [0.75, 1.50, 2.25, 1.25, 0.50],
    'middle':  [1.00, 2.00, 3.00, 1.75, 0.75],
    'shallow': [0.25, 0.50, 0.75, 0.40, 0.20],
}
PHASE_BOUNDARIES = [0.0, 0.15, 0.35, 0.65, 0.85, 1.0]


def get_tcas_v2_scale(step_frac, layer_group='middle'):
    """5-phase smooth TCAS with per-layer variation.

    Args:
        step_frac: fraction of denoising progress [0, 1] (0=start, 1=end)
        layer_group: 'deep', 'middle', or 'shallow'
    Returns:
        scale value with linear interpolation between phases
    """
    schedule = TCAS_V2_SCHEDULES.get(layer_group, TCAS_V2_SCHEDULES['middle'])

    # Find which phase we're in and interpolate
    for i in range(len(PHASE_BOUNDARIES) - 1):
        if step_frac <= PHASE_BOUNDARIES[i + 1]:
            # Linear interpolation within phase
            phase_start = PHASE_BOUNDARIES[i]
            phase_end = PHASE_BOUNDARIES[i + 1]
            local_frac = (step_frac - phase_start) / (phase_end - phase_start)

            if i < len(schedule) - 1:
                # Interpolate to next phase value for smoothness
                val_curr = schedule[i]
                val_next = schedule[min(i + 1, len(schedule) - 1)]
                return val_curr + (val_next - val_curr) * local_frac * 0.3  # Gentle blend
            return schedule[i]
    return schedule[-1]


def get_tcas_v2_scale_for_timestep(timestep, num_timesteps=1000, layer_group='middle'):
    """Convert diffusion timestep to TCAS v2 scale.

    Note: In diffusion, high timestep = early denoising (more noise).
    step_frac=0 corresponds to t=T (full noise, start of denoising),
    step_frac=1 corresponds to t=0 (clean image, end of denoising).
    """
    # Normalized: t=1000 → frac=0 (start), t=0 → frac=1 (end)
    step_frac = 1.0 - (timestep / num_timesteps)
    return get_tcas_v2_scale(step_frac, layer_group)


def setup_per_layer_scales(model, timestep, num_timesteps=1000):
    """Set per-layer TCAS v2 scales on all adapter wrappers."""
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            scale = get_tcas_v2_scale_for_timestep(
                timestep, num_timesteps, module.depth_group
            )
            module._adapter_scale = scale


def clear_adapter_scales(model):
    """Remove _adapter_scale from all wrappers."""
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            if hasattr(module, '_adapter_scale'):
                delattr(module, '_adapter_scale')


# ============================================================
# Data helpers
# ============================================================
def encode_condition_image(model, images, device):
    dtype = next(model.pipeline.vae.parameters()).dtype
    image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
    image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors="pt").pixel_values
    image_pt = image_pt.to(device=device, dtype=dtype)
    return model.pipeline.vae.encode(image_pt).latent_dist.sample()


def encode_target_images(model, images, device):
    dtype = next(model.pipeline.vae.parameters()).dtype
    images = (images - 0.5) / 0.8
    posterior = model.pipeline.vae.encode(images.to(device=device, dtype=dtype)).latent_dist
    latents = posterior.sample() * model.pipeline.vae.config.scaling_factor
    return scale_latents(latents)


# ============================================================
# Enhanced Loss
# ============================================================
def compute_enhanced_loss(noise_pred, noise_gt, model, target_imgs=None, mask=None,
                          depth_imgs=None, normal_imgs=None,
                          foreground_weight=0.7, edge_weight=0.3,
                          ssim_weight=0.2, reg_weight=5e-5,
                          var_weight=0.01,
                          step=0, device='cuda'):
    """Enhanced loss with lightweight anti-collapse.

    Anti-collapse strategy (v3 final):
      - Primary: output_proj weight norm clamping (in training loop, not loss)
      - Secondary: shallow layer scale=0.1 (in forward pass)
      - Tertiary: var_weight=0.01 (gentle variance preservation, not dominant)
      - reg_weight=5e-5 (same as v2_ext, light L2 on corrections)

    Key learning: aggressive loss-based constraints (high reg, ratio penalty)
    create gradient conflicts with noise_loss → training instability → NaN.
    Physical constraints (weight norm clamp, scale caps) are stable.
    """
    loss_dict = {}
    latent_h, latent_w = noise_pred.shape[2], noise_pred.shape[3]
    base_mse = F.mse_loss(noise_pred, noise_gt, reduction='none')

    # Spatial weight map
    spatial_weight = torch.ones_like(base_mse)

    # Foreground boost (0.7 = foreground gets 1.7x weight)
    if mask is not None and foreground_weight > 0:
        mask_latent = F.interpolate(mask, size=(latent_h, latent_w),
                                    mode='bilinear', align_corners=False)
        fg_boost = 1.0 + foreground_weight * mask_latent
        spatial_weight = spatial_weight * fg_boost.expand_as(noise_pred)

    # Edge boost (0.3 = edge regions get 1.3x additional)
    if edge_weight > 0 and (depth_imgs is not None or normal_imgs is not None):
        edge_source = depth_imgs.float() if depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        edge_latent = F.interpolate(edge_mask, size=(latent_h, latent_w),
                                    mode='bilinear', align_corners=False)
        edge_boost = 1.0 + edge_weight * edge_latent
        spatial_weight = spatial_weight * edge_boost.expand_as(noise_pred)

    # Combined noise loss
    noise_loss = (base_mse * spatial_weight).mean()
    loss_dict['train/noise_loss'] = noise_loss.item()
    total_loss = noise_loss

    # Latent-space SSIM loss (lightweight)
    if ssim_weight > 0:
        mask_latent_ssim = None
        if mask is not None:
            mask_latent_ssim = F.interpolate(mask, size=(latent_h, latent_w),
                                            mode='bilinear', align_corners=False)
        ssim_loss = compute_ssim_loss(noise_pred.float(), noise_gt.float(), mask_latent_ssim)
        loss_dict['train/ssim_loss'] = ssim_loss.item()
        total_loss = total_loss + ssim_weight * ssim_loss

    # Adapter residual regularization (L2 on corrections)
    if reg_weight > 0:
        reg_loss = torch.tensor(0.0, device=noise_pred.device)
        count = 0
        for module in model.unet.modules():
            if isinstance(module, GeoTexResnetWrapper) and module._last_correction is not None:
                reg_loss = reg_loss + module._last_correction.pow(2).mean()
                count += 1
        if count > 0:
            reg_loss = reg_loss / count
            loss_dict['train/reg_loss'] = reg_loss.item()
            total_loss = total_loss + reg_weight * reg_loss

    # Note: ratio penalty removed — it caused gradient instability (penalty grew
    # unbounded as adapter strengthened, conflicting with noise loss gradients).
    # Replaced by static scale caps (shallow=0.1) which provide hard limits without
    # gradient conflicts.

    # Variance preservation loss: prevent mode collapse to gray
    if var_weight > 0:
        pred_var = noise_pred.var(dim=[2, 3]).mean()
        gt_var = noise_gt.var(dim=[2, 3]).mean()
        # Only penalize when predicted variance is LESS than GT variance
        var_loss = F.relu(gt_var - pred_var)
        loss_dict['train/var_loss'] = var_loss.item()
        total_loss = total_loss + var_weight * var_loss

    loss_dict['train/total_loss'] = total_loss.item()
    return total_loss, loss_dict


# ============================================================
# Main Training
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="GeoTex-Adapter v2 Training")
    parser.add_argument('--config', required=True, help='Config YAML')
    parser.add_argument('--output_dir', default=None, help='Output directory')
    parser.add_argument('--steps', type=int, default=10000, help='Total training steps')
    parser.add_argument('--warmup_steps', type=int, default=1000, help='LR warmup steps')
    parser.add_argument('--peak_lr', type=float, default=5e-5, help='Peak learning rate')
    parser.add_argument('--min_lr', type=float, default=5e-6, help='Minimum learning rate')
    parser.add_argument('--grad_accum', type=int, default=4, help='Gradient accumulation steps')
    parser.add_argument('--ema_decay', type=float, default=0.9995, help='EMA decay')
    parser.add_argument('--save_every', type=int, default=1000, help='Save checkpoint every N steps')
    parser.add_argument('--eval_every', type=int, default=2000, help='Run quick eval every N steps')
    parser.add_argument('--device', default='cuda:0', help='Device')
    parser.add_argument('--grad_clip', type=float, default=0.5, help='Gradient clipping')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    # Loss weights
    parser.add_argument('--fg_weight', type=float, default=0.7, help='Foreground loss weight')
    parser.add_argument('--edge_weight', type=float, default=0.3, help='Edge loss weight')
    parser.add_argument('--ssim_weight', type=float, default=0.2, help='Latent SSIM weight')
    parser.add_argument('--reg_weight', type=float, default=1e-3, help='Adapter L2 reg weight')
    parser.add_argument('--var_weight', type=float, default=0.05, help='Variance preservation weight')
    parser.add_argument('--train_scale', type=float, default=None,
                        help='Uniform adapter scale during training (overrides per-layer caps). '
                             'If None, uses legacy behavior (shallow=0.1, others=1.0). '
                             'Set to 0.6 for v4 sweetspot training.')
    parser.add_argument('--proj_clamp', type=float, default=1.5,
                        help='Output projection weight norm clamp (0 to disable). '
                             'v3 used 1.5 but never triggered (norms ≈0.4). '
                             'v4 sets 0 (disabled, relying on train_scale for control).')
    args = parser.parse_args()

    # Seed
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device(args.device)
    config = OmegaConf.load(args.config)

    # Output directory
    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex_v2')
    os.makedirs(args.output_dir, exist_ok=True)
    ckpt_dir = os.path.join(args.output_dir, 'checkpoints')
    os.makedirs(ckpt_dir, exist_ok=True)
    log_dir = os.path.join(args.output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Save config
    with open(os.path.join(args.output_dir, 'train_args.json'), 'w') as f:
        json.dump(vars(args), f, indent=2)

    # ============================================================
    # Model Setup
    # ============================================================
    print("=" * 70)
    print("GeoTex-Adapter v2 Training")
    print("=" * 70)
    print(f"Config: {args.config}")
    print(f"Steps: {args.steps}, Warmup: {args.warmup_steps}")
    print(f"LR: {args.min_lr} → {args.peak_lr} → {args.min_lr} (cosine)")
    print(f"Grad accum: {args.grad_accum}, Effective batch: {args.grad_accum}")
    print(f"EMA decay: {args.ema_decay}")
    print(f"Loss: fg={args.fg_weight}, edge={args.edge_weight}, "
          f"ssim={args.ssim_weight}, reg={args.reg_weight}, "
          f"var={args.var_weight}")
    print()

    model = instantiate_from_config(config.model)

    # Move to device with proper dtypes
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

    # Freeze UNet backbone
    model.unet.requires_grad_(False)

    # Unfreeze trainable: adapters + encoder
    trainable_params = []
    trainable_named_params = []
    for name, module in model.unet.named_modules():
        if isinstance(module, GeoTexResnetWrapper):
            for pname, p in module.adapter.named_parameters():
                p.requires_grad = True
                trainable_params.append(p)
                trainable_named_params.append((f"adapter.{name}.{pname}", p))
    for pname, p in model.geo_encoder.named_parameters():
        p.requires_grad = True
        trainable_params.append(p)
        trainable_named_params.append((f"encoder.{pname}", p))

    total_trainable = sum(p.numel() for p in trainable_params)
    print(f"Trainable params: {total_trainable / 1e6:.2f}M")
    print(f"Adapters: {sum(p.numel() for p in model.adapters.parameters()) / 1e6:.2f}M")
    print(f"Encoder: {sum(p.numel() for p in model.geo_encoder.parameters()) / 1e6:.2f}M")

    # ============================================================
    # Optimizer + EMA
    # ============================================================
    optimizer = torch.optim.AdamW(trainable_params, lr=args.peak_lr, weight_decay=1e-5)
    ema = EMA(trainable_named_params, decay=args.ema_decay)

    # ============================================================
    # Dataset
    # ============================================================
    dataset = instantiate_from_config(config.data.params.train)
    dataset_len = len(dataset)
    print(f"Dataset: {dataset_len} objects")
    print()

    # ============================================================
    # Training Loop
    # ============================================================
    print(f"Starting training: {args.steps} steps × {args.grad_accum} accum = "
          f"{args.steps * args.grad_accum} micro-steps")
    print("=" * 70)

    # Only set trainable components to training mode (UNet backbone stays eval)
    model.adapters.train()
    model.geo_encoder.train()
    optimizer.zero_grad()
    accum_loss = 0.0
    log_entries = []
    start_time = time.time()
    best_eval_metric = -1.0

    for step in range(args.steps):
        step_start = time.time()

        # Update learning rate
        lr = get_lr(step, args.steps, args.warmup_steps, args.peak_lr, args.min_lr)
        for pg in optimizer.param_groups:
            pg['lr'] = lr

        # Gradient accumulation loop
        step_loss_total = 0.0
        step_loss_dict = {}
        valid_micro_steps = 0

        for accum_idx in range(args.grad_accum):
            micro_step = step * args.grad_accum + accum_idx
            idx = micro_step % dataset_len

            # Load batch
            sample = dataset[idx]
            batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
                     for k, v in sample.items()}
            for k in batch:
                if hasattr(batch[k], 'to'):
                    batch[k] = batch[k].to(device)

            cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
                model.prepare_batch_data(batch, device=device)

            B = cond_imgs.shape[0]
            t = torch.randint(0, model.num_timesteps, size=(B,)).long().to(device)

            with torch.no_grad():
                weight_dtype = torch.float16

                # Conditioning (with random drop for classifier-free guidance)
                if np.random.rand() > model.drop_cond_prob:
                    if 'global_embeds' in batch:
                        global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
                        ramp = global_embeds.new_tensor(
                            model.pipeline.config.ramping_coefficients
                        ).unsqueeze(-1).to(weight_dtype)
                        uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
                        prompt_embeds = uc_text_emb + global_embeds * ramp
                    else:
                        prompt_embeds = model.pipeline.get_prompt_embeds_train(
                            cond_image=cond_imgs, is_drop=False
                        )
                    cond_latents = encode_condition_image(model, cond_imgs, device).to(weight_dtype)
                    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
                else:
                    if 'global_embeds' in batch:
                        prompt_embeds = torch.zeros((B, 77, 2048), device=device, dtype=weight_dtype)
                    else:
                        prompt_embeds = model.pipeline.get_prompt_embeds_train(
                            cond_image=cond_imgs, is_drop=True
                        )
                    cond_latents = encode_condition_image(
                        model, torch.zeros_like(cond_imgs), device
                    ).to(weight_dtype)
                    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=True)

                added_cond_kwargs = {
                    k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                    for k, v in added_cond_kwargs.items()
                }

                # Encode target to latent
                latents = encode_target_images(model, target_imgs, device).to(weight_dtype)
                noise = torch.randn_like(latents)
                latents_noisy = model.train_scheduler.add_noise(latents, noise, t)

            # Geometry features (requires grad)
            geo_input_clean = geo_input.float().clamp(0, 1)
            geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_input_clean)

            # Apply scale caps during training to control correction magnitude.
            # Legacy (v3): shallow=0.1, others=1.0 (aggressive suppression, led to too-weak adapter)
            # v4 sweetspot: uniform train_scale=0.6 (calibrated from fine gamma scan §8)
            if args.train_scale is not None:
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        module._adapter_scale = args.train_scale
            else:
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        if module.depth_group == 'shallow':
                            module._adapter_scale = 0.1  # Heavily suppress shallow layers
                        else:
                            module._adapter_scale = 1.0  # No amplification for deep/middle

            # Set geo features and run forward
            model._set_geo_feats_on_wrappers(geo_feats)

            noise_pred = model.pipeline.unet(
                latents_noisy, t,
                encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False, is_training=True,
            )[0]

            # Compute loss BEFORE clearing (loss reads _last_correction/_last_hidden)
            loss, loss_dict = compute_enhanced_loss(
                noise_pred, noise, model,
                target_imgs=target_imgs, mask=mask,
                depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
                foreground_weight=args.fg_weight,
                edge_weight=args.edge_weight,
                ssim_weight=args.ssim_weight,
                reg_weight=args.reg_weight,
                var_weight=args.var_weight,
                step=step, device=device,
            )
            # Clear geo feats AFTER loss computation
            model._clear_geo_feats_on_wrappers()

            # Scale loss for gradient accumulation
            scaled_loss = loss / args.grad_accum

            if torch.isnan(scaled_loss) or torch.isinf(scaled_loss):
                print(f"  Step {step+1} micro {accum_idx}: NaN/Inf loss, skipping")
                continue

            scaled_loss.backward()
            step_loss_total += loss.item()
            valid_micro_steps += 1

            # Aggregate loss dict
            for k, v in loss_dict.items():
                step_loss_dict[k] = step_loss_dict.get(k, 0) + v / args.grad_accum

        # Skip optimizer step if no valid micro-steps produced gradients
        if valid_micro_steps == 0:
            optimizer.zero_grad()
            print(f"  Step {step+1}: all micro-steps NaN, skipping optimizer step")
            continue

        # Gradient step
        if args.grad_clip > 0:
            grad_norm = torch.nn.utils.clip_grad_norm_(trainable_params, args.grad_clip)
        else:
            grad_norm = 0.0

        optimizer.step()
        optimizer.zero_grad()

        # Output projection weight norm clamping (prevents correction explosion)
        # v3 used 1.5 (never triggered, norms converge ≈0.4);
        # v4 disables (train_scale=0.6 controls magnitude via gradient scaling).
        if args.proj_clamp > 0:
            with torch.no_grad():
                for adapter in model.adapters:
                    w = adapter.output_proj.weight
                    w_norm = w.norm()
                    if w_norm > args.proj_clamp:
                        w.mul_(args.proj_clamp / w_norm)

        # EMA update
        ema.update(trainable_named_params)

        avg_loss = step_loss_total / args.grad_accum
        step_time = time.time() - step_start

        # Logging
        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - start_time
            eta = elapsed / (step + 1) * (args.steps - step - 1)
            print(f"[{step+1:5d}/{args.steps}] loss={avg_loss:.4f} "
                  f"lr={lr:.2e} gnorm={grad_norm:.3f} "
                  f"| {step_time:.2f}s/step | ETA: {eta/60:.0f}min")

        log_entries.append({
            'step': step + 1,
            'loss': avg_loss,
            'lr': lr,
            'grad_norm': float(grad_norm) if isinstance(grad_norm, torch.Tensor) else grad_norm,
            **step_loss_dict,
        })

        # Save checkpoint
        if (step + 1) % args.save_every == 0:
            ckpt_path = os.path.join(ckpt_dir, f'geotex_v2_step_{step+1:06d}.pt')
            save_state = {
                'step': step + 1,
                'adapters': model.adapters.state_dict(),
                'geo_encoder': model.geo_encoder.state_dict(),
                'optimizer': optimizer.state_dict(),
                'ema': ema.state_dict(),
            }
            torch.save(save_state, ckpt_path)
            print(f"  → Saved checkpoint: {ckpt_path}")

            # Also save EMA-only weights (for inference)
            ema_path = os.path.join(ckpt_dir, f'geotex_v2_ema_step_{step+1:06d}.pt')
            ema.apply_shadow(trainable_named_params)
            ema_state = {
                'adapters': model.adapters.state_dict(),
                'geo_encoder': model.geo_encoder.state_dict(),
            }
            torch.save(ema_state, ema_path)
            ema.restore(trainable_named_params)
            print(f"  → Saved EMA weights: {ema_path}")

        # Periodic GC
        if (step + 1) % 200 == 0:
            torch.cuda.empty_cache()
            gc.collect()

        # Save training log periodically
        if (step + 1) % 100 == 0:
            log_path = os.path.join(log_dir, 'train_log.json')
            with open(log_path, 'w') as f:
                json.dump(log_entries, f)

    # ============================================================
    # Final save
    # ============================================================
    total_time = time.time() - start_time
    print(f"\nTraining complete: {total_time/3600:.1f}h ({total_time/args.steps:.2f}s/step)")

    # Save final checkpoint
    final_path = os.path.join(ckpt_dir, 'geotex_v2_final.pt')
    save_state = {
        'step': args.steps,
        'adapters': model.adapters.state_dict(),
        'geo_encoder': model.geo_encoder.state_dict(),
        'optimizer': optimizer.state_dict(),
        'ema': ema.state_dict(),
    }
    torch.save(save_state, final_path)
    print(f"Final checkpoint: {final_path}")

    # Save final EMA weights
    ema_final_path = os.path.join(ckpt_dir, 'geotex_v2_ema_final.pt')
    ema.apply_shadow(trainable_named_params)
    ema_state = {
        'adapters': model.adapters.state_dict(),
        'geo_encoder': model.geo_encoder.state_dict(),
    }
    torch.save(ema_state, ema_final_path)
    ema.restore(trainable_named_params)
    print(f"Final EMA weights: {ema_final_path}")

    # Save full training log
    log_path = os.path.join(log_dir, 'train_log.json')
    with open(log_path, 'w') as f:
        json.dump(log_entries, f)
    print(f"Training log: {log_path}")


if __name__ == '__main__':
    main()
