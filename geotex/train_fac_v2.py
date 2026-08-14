"""FAC (Full Adaptive Correction) training on v2 base weights.

Trains only the AdaptiveCorrectionController (LTAG/GSG/FSC) on top of the
frozen v2 GeoTex-Adapter + geo encoder. The base adapter/encoder weights are
loaded from the v2 EMA checkpoint and kept frozen; this matches the paper's
claim that "FAC keeps the base model, VAE, and original GeoTex-Adapter frozen,
adding LTAG timestep gating, GSG spatial gating, and FSC frequency-selective
correction on top of TCAS."

Key difference from train_v2.py:
  - trainable = controller params ONLY (LTAG/GSG/FSC, ~6K params)
  - No _adapter_scale is set on wrappers: LTAG provides the temporal scale,
    so the static TCAS _adapter_scale is intentionally left unset (see the
    comment in GeoTexResnetWrapper.forward).
  - model.correction_controller.set_timestep(t[0]) is called each micro-step.

Three variants (--enable_ltag/--enable_gsg/--enable_fsc):
  - LTAG only:          --enable_ltag
  - LTAG + GSG:         --enable_ltag --enable_gsg
  - Full FAC:           --enable_ltag --enable_gsg --enable_fsc

Usage:
    python geotex/train_fac_v2.py \
        --base_checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/fac_v2/ltag \
        --enable_ltag --steps 500 --device cuda:0
"""
import os
import sys
import math
import time
import argparse
import json
import gc
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))

import torch
import torch.nn as nn
import torch.nn.functional as F

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from diffusers import EulerDiscreteScheduler
from train_v2 import (EMA, get_lr, encode_condition_image, encode_target_images,
                      compute_enhanced_loss)
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


def build_eval_timesteps(model, num_eval_steps=50):
    """The exact Euler timesteps used by the FAC evaluation protocol.

    eval_fac_v2.py converts the base EulerAncestral scheduler to
    EulerDiscreteScheduler and runs num_steps=50. We reproduce that grid here so
    LTAG is trained on the same timesteps it is evaluated on (the previous run
    sampled t ~ U[0, 1000), giving ~0.5 gradient samples per timestep and
    preventing the MLP from ever learning a temporal profile).
    """
    sched = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    sched.set_timesteps(num_eval_steps, device='cpu')
    return sched.timesteps  # float tensor, decreasing


def warmstart_ltag_to_c3(model, eval_ts, fit_steps=200, lr=1e-2):
    """Supervisedly fit LTAG weights to C3's *effective* per-layer schedule.

    C3 on the eval grid: s = 2.50 on the middle third of steps, 1.25 elsewhere,
    further capped per layer (deep 3.0 / middle 3.5 / shallow 0.8) in the
    wrapper. We fit the per-adapter targets AFTER the same cap, so that an
    untrained LTAG reproduces the effective TCAS schedule exactly at every
    layer (e.g. shallow adapters pinned at 0.8, not 1.25/2.50). The ablation
    therefore measures learned refinement of C3 rather than a difference in
    injection limits.
    """
    ltag = model.correction_controller.ltag
    dev = next(ltag.parameters()).device
    n = len(eval_ts)
    n_adapters = ltag.num_adapters
    mid = slice(n // 3, 2 * n // 3)

    # Per-adapter layer cap (from the wrappers' depth groups), so the target
    # schedule matches the effective TCAS scale the eval baseline applies.
    adapter_max = {}
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            adapter_max[module.adapter_idx] = module._max_scale

    targets = torch.full((n, n_adapters), 1.25, device=dev)
    targets[mid, :] = 2.50  # middle third of TIMESTEPS rows, all adapters
    for idx in range(n_adapters):
        cap = adapter_max.get(idx)
        if cap is not None:
            targets[:, idx] = targets[:, idx].clamp(max=cap)
    print(f"  Per-adapter warm-start caps: {[round(adapter_max.get(i, 3.0), 2) for i in range(n_adapters)]}")

    t_vals = eval_ts.float().to(dev)
    opt = torch.optim.Adam(ltag.parameters(), lr=lr)
    last = 0.0
    for _ in range(fit_steps):
        opt.zero_grad()
        pred = ltag(t_vals)  # (n, num_adapters)
        loss = (pred - targets).pow(2).mean()
        loss.backward()
        opt.step()
        last = loss.item()
    print(f"  LTAG warm-started to effective C3 on {n} eval timesteps "
          f"(final fit MSE = {last:.5f})")


def load_base_weights(model, base_checkpoint):
    """Load v2 adapter + geo_encoder weights, then freeze them."""
    st = torch.load(base_checkpoint, map_location='cpu')
    if 'adapters' in st:
        model.adapters.load_state_dict(st['adapters'])
    else:
        raise ValueError(f"base checkpoint has no 'adapters': {list(st.keys())}")
    model.geo_encoder.load_state_dict(st['geo_encoder'])
    # Freeze base components (controller params remain trainable)
    model.adapters.requires_grad_(False)
    model.geo_encoder.requires_grad_(False)
    for name, module in model.unet.named_modules():
        if isinstance(module, GeoTexResnetWrapper):
            module.adapter.requires_grad_(False)
    return st


def main():
    parser = argparse.ArgumentParser(description="FAC controller training on v2 base")
    parser.add_argument('--config', type=str,
                        default='MVPainter/configs/mvpainter-geotex-fac-train.yaml')
    parser.add_argument('--base_checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--steps', type=int, default=2000)
    parser.add_argument('--save_every', type=int, default=500)
    parser.add_argument('--peak_lr', type=float, default=1e-4)
    parser.add_argument('--min_lr', type=float, default=1e-6)
    parser.add_argument('--warmup_steps', type=int, default=100)
    parser.add_argument('--no_warmstart_c3', action='store_true',
                        help='disable supervised LTAG warm-start to the C3 piecewise schedule')
    parser.add_argument('--eval_steps', type=int, default=50,
                        help='number of eval steps whose Euler timesteps are used for t-sampling')
    parser.add_argument('--grad_accum', type=int, default=1)
    parser.add_argument('--grad_clip', type=float, default=1.0)
    parser.add_argument('--ema_decay', type=float, default=0.999)
    parser.add_argument('--fg_weight', type=float, default=0.7)
    parser.add_argument('--edge_weight', type=float, default=0.3)
    parser.add_argument('--ssim_weight', type=float, default=0.2)
    parser.add_argument('--reg_weight', type=float, default=1e-4)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--enable_ltag', action='store_true')
    parser.add_argument('--enable_gsg', action='store_true')
    parser.add_argument('--enable_fsc', action='store_true')
    args = parser.parse_args()

    device = torch.device(args.device)

    config = OmegaConf.load(args.config)
    # Override FAC module flags from CLI
    config.model.params.enable_ltag = args.enable_ltag
    config.model.params.enable_gsg = args.enable_gsg
    config.model.params.enable_fsc = args.enable_fsc
    config.model.params.adapter_reg_weight = args.reg_weight

    variant = []
    if args.enable_ltag:
        variant.append('ltag')
    if args.enable_gsg:
        variant.append('gsg')
    if args.enable_fsc:
        variant.append('fsc')
    variant_str = '+'.join(variant) if variant else 'none'
    print(f"FAC variant: {variant_str}")

    # ============ Model ============
    model = instantiate_from_config(config.model)
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

    # Load + freeze base weights
    load_base_weights(model, args.base_checkpoint)

    # Controller on device, float32
    if model.correction_controller is None:
        raise RuntimeError("correction_controller is None — FAC modules not enabled in config")
    model.correction_controller.to(device).to(dtype=torch.float32)

    print(f"FAC params: {model.correction_controller.param_count()}")

    # Build the eval Euler timestep grid and (optionally) warm-start LTAG to C3
    eval_ts = build_eval_timesteps(model, args.eval_steps).to(device)
    print(f"Eval timestep grid: {len(eval_ts)} steps, "
          f"t range [{eval_ts[-1].item():.1f}, {eval_ts[0].item():.1f}]")
    if args.enable_ltag and not args.no_warmstart_c3:
        warmstart_ltag_to_c3(model, eval_ts)
    elif args.enable_ltag:
        print("  LTAG warm-start to C3 disabled (--no_warmstart_c3)")

    # ============ Optimizer + EMA (controller only) ============
    trainable_params = [p for p in model.correction_controller.parameters() if p.requires_grad]
    trainable_named = [(f"fac.{n}", p) for n, p in model.correction_controller.named_parameters()]
    print(f"Trainable controller params: {sum(p.numel() for p in trainable_params)}")
    optimizer = torch.optim.AdamW(trainable_params, lr=args.peak_lr, weight_decay=1e-5)
    ema = EMA(trainable_named, decay=args.ema_decay)

    # ============ Dataset ============
    dataset = instantiate_from_config(config.data.params.train)
    dataset_len = len(dataset)
    print(f"Dataset: {dataset_len} objects")

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"\nStarting FAC training: {args.steps} steps, lr={args.peak_lr}, variant={variant_str}")
    print("=" * 70)

    model.adapters.train()  # adapter in train mode (BN/affine) but frozen weights
    model.geo_encoder.train()
    model.correction_controller.train()
    optimizer.zero_grad()
    accum_loss = 0.0
    start_time = time.time()
    trainable_params_all = trainable_params

    for step in range(args.steps):
        step_start = time.time()
        lr = get_lr(step, args.steps, args.warmup_steps, args.peak_lr, args.min_lr)
        for pg in optimizer.param_groups:
            pg['lr'] = lr

        step_loss_total = 0.0
        step_loss_dict = {}
        valid_micro_steps = 0

        for accum_idx in range(args.grad_accum):
            micro_step = step * args.grad_accum + accum_idx
            idx = micro_step % dataset_len

            sample = dataset[idx]
            batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
                     for k, v in sample.items()}
            for k in batch:
                if hasattr(batch[k], 'to'):
                    batch[k] = batch[k].to(device)

            cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
                model.prepare_batch_data(batch, device=device)

            B = cond_imgs.shape[0]
            # Sample t from the eval Euler timestep grid: LTAG sees exactly the
            # noise levels it will be evaluated on (avoids the ~0.5 samples per
            # timestep that made the previous run collapse to a flat profile).
            t = eval_ts[torch.randint(0, len(eval_ts), size=(B,))].long()

            with torch.no_grad():
                weight_dtype = torch.float16
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

                latents = encode_target_images(model, target_imgs, device).to(weight_dtype)
                noise = torch.randn_like(latents)
                latents_noisy = model.train_scheduler.add_noise(latents, noise, t)

                geo_input_clean = geo_input.float().clamp(0, 1)
                geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
                geo_feats = model.geo_encoder(geo_input_clean)

            # LTAG provides the temporal scale — do NOT set _adapter_scale.
            model.correction_controller.set_timestep(t[0])
            model._set_geo_feats_on_wrappers(geo_feats)

            noise_pred = model.pipeline.unet(
                latents_noisy, t,
                encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False, is_training=True,
            )[0]
            model._clear_geo_feats_on_wrappers()

            loss, loss_dict = compute_enhanced_loss(
                noise_pred, noise, model,
                target_imgs=target_imgs, mask=mask,
                depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
                foreground_weight=args.fg_weight,
                edge_weight=args.edge_weight,
                ssim_weight=args.ssim_weight,
                reg_weight=args.reg_weight,
                step=step, device=device,
            )

            scaled_loss = loss / args.grad_accum
            if torch.isnan(scaled_loss) or torch.isinf(scaled_loss):
                print(f"  Step {step+1} micro {accum_idx}: NaN/Inf loss, skipping")
                continue

            scaled_loss.backward()
            step_loss_total += loss.item()
            valid_micro_steps += 1
            for k, v in loss_dict.items():
                step_loss_dict[k] = step_loss_dict.get(k, 0) + v / args.grad_accum

        if valid_micro_steps == 0:
            optimizer.zero_grad()
            print(f"  Step {step+1}: all micro-steps NaN, skipping optimizer step")
            continue

        if args.grad_clip > 0:
            grad_norm = torch.nn.utils.clip_grad_norm_(trainable_params_all, args.grad_clip)
        else:
            grad_norm = 0.0

        # Per-module grad norms (before stepping) to verify learning actually happens
        mod_grads = {}
        ctrl = model.correction_controller
        for name, p in ctrl.named_parameters():
            if p.grad is not None:
                g = p.grad.detach().norm()
                m = name.split('.')[0]
                mod_grads[m] = max(mod_grads.get(m, 0.0), float(g))

        optimizer.step()
        optimizer.zero_grad()
        ema.update(trainable_named)

        step_loss_dict['train/lr'] = lr
        step_loss_dict['train/grad_norm'] = grad_norm
        avg_loss = step_loss_total / max(valid_micro_steps, 1)
        accum_loss = 0.99 * accum_loss + 0.01 * avg_loss
        step_elapsed = time.time() - step_start

        if (step + 1) % 20 == 0 or step == args.steps - 1:
            mg = " ".join(f"{k}={v:.1e}" for k, v in sorted(mod_grads.items())) or "no-grad"
            print(f"[{step+1}/{args.steps}] loss={avg_loss:.4f} (ema {accum_loss:.4f}) "
                  f"lr={lr:.2e} grad={grad_norm:.3f} | {mg} | {step_elapsed:.1f}s")

        # Save checkpoint
        if (step + 1) % args.save_every == 0 or step == args.steps - 1:
            ckpt_dir = os.path.join(args.output_dir, 'checkpoints')
            os.makedirs(ckpt_dir, exist_ok=True)
            # EMA-applied controller state
            ema.apply_shadow(trainable_named)
            fac_state = model.correction_controller.state_dict()
            ema.restore(trainable_named)

            save_state = {
                'adapters': model.adapters.state_dict(),
                'geo_encoder': model.geo_encoder.state_dict(),
                'fac_controller': fac_state,
                'step': step + 1,
                'variant': variant_str,
                'config': os.path.basename(args.config),
                'fac_version': 3,  # + per-layer capped warm-start/apply (LTAG@init ≡ effective C3)
                'warmstart_c3': not args.no_warmstart_c3,
                'peak_lr': args.peak_lr,
            }
            ckpt_path = os.path.join(ckpt_dir, f'fac_v2_{variant_str}_step_{step+1:06d}.pt')
            torch.save(save_state, ckpt_path)
            print(f"  → Saved: {ckpt_path}")
            gc.collect()

    print("\nFAC training complete.")
    print(f"Final checkpoint dir: {os.path.join(args.output_dir, 'checkpoints')}")


if __name__ == '__main__':
    main()
