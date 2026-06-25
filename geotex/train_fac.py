"""FAC (Full Adaptive Correction) fine-tuning script.

Loads a pre-trained GeoTex adapter checkpoint, attaches FAC modules
(LTAG + GSG + FSC), and fine-tunes the combined system.

Strategy:
  - GeoTex adapter weights: loaded from checkpoint, gradients enabled
  - FAC modules: initialized (LTAG warm-started from TCAS), gradients enabled
  - UNet + VAE: frozen
  - Total new params: ~6K (FAC) on top of ~2.2M (adapter+encoder)

Usage:
    python geotex/train_fac.py \
        --config ../MVPainter/configs/mvpainter-geotex-fac-train.yaml \
        --resume /4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/checkpoints/geotex_final.pt \
        --output_dir ../mvpoutput/fac_train \
        --steps 500
"""
import os
import sys
import time
import argparse
import json
import csv
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

from metrics import scale_latents, unscale_latents


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


def main():
    parser = argparse.ArgumentParser(description="FAC Fine-tuning")
    parser.add_argument('--config', required=True, help='Config YAML (with FAC enabled)')
    parser.add_argument('--resume', required=True, help='Pre-trained GeoTex checkpoint to load')
    parser.add_argument('--output_dir', default=None, help='Output directory')
    parser.add_argument('--steps', type=int, default=500, help='Training steps')
    parser.add_argument('--save_every', type=int, default=100, help='Save every N steps')
    parser.add_argument('--lr', type=float, default=5e-5, help='Learning rate')
    parser.add_argument('--device', default='cuda:0', help='Device')
    parser.add_argument('--freeze_adapter', action='store_true',
                        help='Freeze adapter weights, train only FAC modules')
    args = parser.parse_args()

    device = torch.device(args.device)
    config = OmegaConf.load(args.config)

    # Ensure FAC is enabled in config
    model_params = config.model.params
    assert model_params.get('enable_ltag', False) or \
           model_params.get('enable_gsg', False) or \
           model_params.get('enable_fsc', False), \
        "Config must have at least one FAC module enabled (enable_ltag/enable_gsg/enable_fsc)"

    # Output directory
    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'fac_train')
    os.makedirs(args.output_dir, exist_ok=True)
    ckpt_dir = os.path.join(args.output_dir, 'checkpoints')
    os.makedirs(ckpt_dir, exist_ok=True)

    # Instantiate model with FAC
    print(f"Config: {args.config}")
    print(f"FAC: LTAG={model_params.get('enable_ltag')}, "
          f"GSG={model_params.get('enable_gsg')}, "
          f"FSC={model_params.get('enable_fsc')}")
    model = instantiate_from_config(config.model)

    # Load pre-trained adapter weights
    print(f"Loading adapter checkpoint: {args.resume}")
    model.load_geotex_weights(args.resume)

    # Move to device
    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae.to(device).to(dtype=torch.float16)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    if model.correction_controller is not None:
        model.correction_controller.to(device).to(dtype=torch.float32)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')
    model.pipeline.vae.eval()
    model._device = device

    # Freeze UNet
    model.unet.requires_grad_(False)

    # Unfreeze trainable components
    trainable_params = []

    # Adapter weights (optionally frozen)
    if not args.freeze_adapter:
        for name, module in model.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                for p in module.adapter.parameters():
                    p.requires_grad = True
                    trainable_params.append(p)
        for p in model.geo_encoder.parameters():
            p.requires_grad = True
            trainable_params.append(p)
        print("  Adapter + Encoder: trainable")
    else:
        print("  Adapter + Encoder: FROZEN (training FAC only)")

    # FAC controller parameters
    if model.correction_controller is not None:
        for p in model.correction_controller.parameters():
            p.requires_grad = True
            trainable_params.append(p)
        fac_param_count = sum(p.numel() for p in model.correction_controller.parameters())
        print(f"  FAC controller: {fac_param_count} params trainable")

    total_trainable = sum(p.numel() for p in trainable_params)
    print(f"  Total trainable: {total_trainable / 1e6:.4f}M")

    optimizer = torch.optim.AdamW(trainable_params, lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.steps, eta_min=args.lr / 10)

    # Load dataset
    dataset = instantiate_from_config(config.data.params.train)
    print(f"Dataset: {len(dataset)} objects")

    # Training loop
    model.train()
    metrics_log = []
    print(f"\nTraining FAC for {args.steps} steps (lr={args.lr})...")
    print("=" * 70)
    start_time = time.time()

    for step in range(args.steps):
        step_start = time.time()
        idx = step % len(dataset)
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
                 for k, v in dataset[idx].items()}
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)

        B = cond_imgs.shape[0]
        t = torch.randint(0, model.num_timesteps, size=(B,)).long().to(device)

        with torch.no_grad():
            weight_dtype = torch.float16
            model.pipeline.vae = model.pipeline.vae.to(dtype=weight_dtype)

            if 'global_embeds' in batch:
                global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
                ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
                uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
                prompt_embeds = uc_text_emb + global_embeds * ramp
            else:
                prompt_embeds = model.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=False)

            cond_latents = encode_condition_image(model, cond_imgs, device).to(weight_dtype)
            added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
            added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                                 for k, v in added_cond_kwargs.items()}
            latents = encode_target_images(model, target_imgs, device).to(weight_dtype)

            noise = torch.randn_like(latents)
            latents_noisy = model.train_scheduler.add_noise(latents, noise, t)

        # Geometry features
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        # KEY: Set LTAG timestep before forward pass
        if model.correction_controller is not None:
            model.correction_controller.set_timestep(t[0])

        # Set geo features and run forward
        model._set_geo_feats_on_wrappers(geo_feats)

        noise_pred = model.pipeline.unet(
            latents_noisy, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_latents),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False, is_training=True,
        )[0]
        model._clear_geo_feats_on_wrappers()

        # Compute loss
        loss, loss_dict = model.compute_loss(
            noise_pred, noise, target_imgs, mask, weight_dtype,
            depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
        )

        if torch.isnan(loss) or torch.isinf(loss):
            optimizer.zero_grad()
            print(f"  Step {step+1}: NaN/Inf loss, skipping")
            continue

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        step_time = time.time() - step_start

        # FAC-specific monitoring
        fac_info = {}
        if model.correction_controller is not None:
            ctrl = model.correction_controller
            if ctrl.ltag is not None:
                # Sample LTAG scales at different timesteps
                with torch.no_grad():
                    s_early = ctrl.ltag(torch.tensor([100.0], device=device))
                    s_mid = ctrl.ltag(torch.tensor([500.0], device=device))
                    s_late = ctrl.ltag(torch.tensor([900.0], device=device))
                    fac_info['ltag_early_mean'] = s_early.mean().item()
                    fac_info['ltag_mid_mean'] = s_mid.mean().item()
                    fac_info['ltag_late_mean'] = s_late.mean().item()

        # Log
        row = {'step': step + 1, 'loss': loss.item(), 'lr': scheduler.get_last_lr()[0],
               'step_time': step_time}
        for k, v in loss_dict.items():
            row[k.replace('train/', '')] = v.item()
        row.update(fac_info)
        metrics_log.append(row)

        if (step + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (step + 1) / elapsed
            eta = (args.steps - step - 1) / speed
            loss_str = f"loss={loss.item():.4f}"
            ltag_str = ""
            if fac_info:
                ltag_str = f" | LTAG(e/m/l)={fac_info.get('ltag_early_mean', 0):.2f}/{fac_info.get('ltag_mid_mean', 0):.2f}/{fac_info.get('ltag_late_mean', 0):.2f}"
            print(f"Step {step+1}/{args.steps} | {loss_str}{ltag_str} | {speed:.2f} it/s | ETA: {eta:.0f}s")

        if (step + 1) % args.save_every == 0:
            save_path = os.path.join(ckpt_dir, f'geotex_step_{step+1:07d}.pt')
            model.save_geotex_weights(save_path)

    # Final save
    final_path = os.path.join(ckpt_dir, 'geotex_final.pt')
    model.save_geotex_weights(final_path)

    # Write metrics CSV
    csv_path = os.path.join(args.output_dir, 'train_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics_log[0].keys())
        writer.writeheader()
        writer.writerows(metrics_log)

    # Write summary
    total_time = time.time() - start_time
    summary = {
        'config': args.config,
        'resume': args.resume,
        'steps': args.steps,
        'lr': args.lr,
        'total_time_s': total_time,
        'avg_speed': args.steps / total_time,
        'trainable_params': total_trainable,
        'fac_enabled': {
            'ltag': model_params.get('enable_ltag', False),
            'gsg': model_params.get('enable_gsg', False),
            'fsc': model_params.get('enable_fsc', False),
        },
        'final_loss': metrics_log[-1]['loss'] if metrics_log else None,
        'final_ltag_scales': {
            'early': fac_info.get('ltag_early_mean'),
            'mid': fac_info.get('ltag_mid_mean'),
            'late': fac_info.get('ltag_late_mean'),
        } if fac_info else None,
    }
    with open(os.path.join(args.output_dir, 'train_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"FAC training complete: {total_time:.0f}s ({args.steps / total_time:.2f} it/s)")
    print(f"Final loss: {metrics_log[-1]['loss']:.4f}")
    if fac_info:
        print(f"Final LTAG scales (early/mid/late): "
              f"{fac_info.get('ltag_early_mean', 0):.3f} / "
              f"{fac_info.get('ltag_mid_mean', 0):.3f} / "
              f"{fac_info.get('ltag_late_mean', 0):.3f}")
    print(f"Checkpoint: {final_path}")
    print(f"Metrics: {csv_path}")


if __name__ == '__main__':
    main()
