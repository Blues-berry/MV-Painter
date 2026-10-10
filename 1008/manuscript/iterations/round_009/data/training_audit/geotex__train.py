"""GeoTex-Adapter training script. Clean, config-driven, no hardcoded paths."""
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
from einops import rearrange

from metrics import scale_latents, unscale_latents


def encode_condition_image(model, images, device):
    """Encode condition images to latents."""
    dtype = next(model.pipeline.vae.parameters()).dtype
    image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
    image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors="pt").pixel_values
    image_pt = image_pt.to(device=device, dtype=dtype)
    return model.pipeline.vae.encode(image_pt).latent_dist.sample()


def encode_target_images(model, images, device):
    """Encode target images to latents."""
    dtype = next(model.pipeline.vae.parameters()).dtype
    images = (images - 0.5) / 0.8
    posterior = model.pipeline.vae.encode(images.to(device=device, dtype=dtype)).latent_dist
    latents = posterior.sample() * model.pipeline.vae.config.scaling_factor
    return scale_latents(latents)


def main():
    parser = argparse.ArgumentParser(description="GeoTex-Adapter Training")
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--output_dir', default=None, help='Output directory (default: from config)')
    parser.add_argument('--steps', type=int, default=None, help='Override max steps')
    parser.add_argument('--save_every', type=int, default=100, help='Save checkpoint every N steps')
    parser.add_argument('--lr', type=float, default=None, help='Override learning rate')
    parser.add_argument('--img_size', type=int, default=256, help='Image size')
    parser.add_argument('--device', default='cuda:0', help='Device')
    parser.add_argument('--resume', default=None, help='Resume from checkpoint')
    args = parser.parse_args()

    device = torch.device(args.device)
    config = OmegaConf.load(args.config)

    # Output directory
    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex')
    os.makedirs(args.output_dir, exist_ok=True)
    ckpt_dir = os.path.join(args.output_dir, 'checkpoints')
    os.makedirs(ckpt_dir, exist_ok=True)

    # Instantiate model
    print(f"Config: {args.config}")
    model = instantiate_from_config(config.model)
    if args.lr is not None:
        model.learning_rate = args.lr

    # Move to device
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

    # Resume
    if args.resume:
        model.load_geotex_weights(args.resume)
        print(f"Resumed from {args.resume}")

    # Freeze UNet, unfreeze adapters
    model.unet.requires_grad_(False)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            for p in module.adapter.parameters():
                p.requires_grad = True
    for p in model.geo_encoder.parameters():
        p.requires_grad = True

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    total_trainable = sum(p.numel() for p in trainable_params)
    print(f"Trainable params: {total_trainable / 1e6:.2f}M")

    optimizer = torch.optim.AdamW(trainable_params, lr=args.lr or 1e-4)

    # Load dataset
    dataset = instantiate_from_config(config.data.params.train)
    print(f"Dataset: {len(dataset)} objects")

    # Training loop
    max_steps = args.steps or config.lightning.trainer.params.max_steps
    model.train()

    metrics_log = []
    print(f"\nTraining for {max_steps} steps...")
    start_time = time.time()

    for step in range(max_steps):
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

        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)
        model._set_geo_feats_on_wrappers(geo_feats)

        noise_pred = model.pipeline.unet(
            latents_noisy, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_latents),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False, is_training=True,
        )[0]
        model._clear_geo_feats_on_wrappers()

        loss, loss_dict = model.compute_loss(
            noise_pred, noise, target_imgs, mask, weight_dtype,
            depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
        )

        if torch.isnan(loss) or torch.isinf(loss):
            optimizer.zero_grad()
            continue

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()

        step_time = time.time() - step_start

        # Collect adapter weight norm
        adapter_norm = 0
        for name, module in model.unet.named_modules():
            if hasattr(module, 'adapter'):
                adapter_norm += module.adapter.output_proj.weight.norm().item()

        # Log metrics
        row = {'step': step + 1, 'loss': loss.item(), 'step_time': step_time,
               'adapter_norm': adapter_norm}
        for k, v in loss_dict.items():
            row[k] = v.item()
        metrics_log.append(row)

        if (step + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (step + 1) / elapsed
            eta = (max_steps - step - 1) / speed
            parts = " | ".join(f"{k.split('/')[-1]}={v.item():.4f}" for k, v in loss_dict.items() if 'loss' in k)
            print(f"Step {step+1}/{max_steps} | {parts} | {speed:.2f} steps/s | ETA: {eta:.0f}s")

        if (step + 1) % args.save_every == 0:
            save_path = os.path.join(ckpt_dir, f'geotex_step_{step+1:07d}.pt')
            model.save_geotex_weights(save_path)

    # Final save
    model.save_geotex_weights(os.path.join(ckpt_dir, 'geotex_final.pt'))

    # Write metrics CSV
    csv_path = os.path.join(args.output_dir, 'train_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics_log[0].keys())
        writer.writeheader()
        writer.writerows(metrics_log)

    # Write summary JSON
    total_time = time.time() - start_time
    summary = {
        'config': args.config,
        'max_steps': max_steps,
        'total_time_s': total_time,
        'avg_speed': max_steps / total_time,
        'trainable_params_M': total_trainable / 1e6,
        'final_loss': metrics_log[-1]['loss'],
        'checkpoints': os.listdir(ckpt_dir),
    }
    with open(os.path.join(args.output_dir, 'train_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nDone in {total_time:.0f}s. Metrics: {csv_path}")


if __name__ == '__main__':
    main()
