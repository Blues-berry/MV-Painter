"""
Simplified GeoTex-Adapter training script.
Bypasses DeepSpeed and PyTorch Lightning for faster iteration.
"""
import os
import sys
import time
import argparse
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from einops import rearrange


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/mvpainter-geotex-uponly.yaml')
    parser.add_argument('--steps', type=int, default=500)
    parser.add_argument('--save_every', type=int, default=100)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--img_size', type=int, default=256)
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)

    # Load config
    config = OmegaConf.load(args.config)
    print(f"Config: {args.config}")
    print(f"Steps: {args.steps}, Save every: {args.save_every}")

    # Instantiate model
    print("Instantiating model...")
    model = instantiate_from_config(config.model)
    model.learning_rate = args.lr

    # Move to device (DON'T call pipeline.to('cpu') - it moves VAE back)
    print("Moving model to device...")
    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae.to(device).to(dtype=torch.float16)
    # Re-convert adapters to float32 (UNet.to(float16) converted them too)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')

    # Set VAE to eval mode
    model.pipeline.vae.eval()

    # Set model device for encode_condition_image
    model._device = device

    # Override encode methods to use correct device (model.device returns 'cpu')
    def encode_condition_image_fixed(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors="pt").pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        latents = model.pipeline.vae.encode(image_pt).latent_dist.sample()
        return latents

    def encode_target_images_fixed(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        images = (images - 0.5) / 0.8
        posterior = model.pipeline.vae.encode(images.to(device=device, dtype=dtype)).latent_dist
        latents = posterior.sample() * model.pipeline.vae.config.scaling_factor
        latents = scale_latents(latents)
        return latents

    def scale_latents(latents):
        return (latents - 0.22) * 0.75

    model.encode_condition_image = encode_condition_image_fixed
    model.encode_target_images = encode_target_images_fixed

    # Verify devices
    print(f"UNet device: {next(model.unet.parameters()).device}, dtype: {next(model.unet.parameters()).dtype}")
    print(f"VAE device: {next(model.pipeline.vae.parameters()).device}, dtype: {next(model.pipeline.vae.parameters()).dtype}")
    print(f"Adapter device: {next(model.adapters.parameters()).device}, dtype: {next(model.adapters.parameters()).dtype}")
    print(f"Encoder device: {next(model.geo_encoder.parameters()).device}, dtype: {next(model.geo_encoder.parameters()).dtype}")

    # Freeze UNet, unfreeze adapters
    model.unet.requires_grad_(False)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            for p in module.adapter.parameters():
                p.requires_grad = True
    for p in model.geo_encoder.parameters():
        p.requires_grad = True

    # Count trainable params
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    total_trainable = sum(p.numel() for p in trainable_params)
    print(f"Trainable params: {total_trainable / 1e6:.2f}M")

    # Optimizer
    optimizer = torch.optim.AdamW(trainable_params, lr=args.lr)

    # Load dataset
    print("Loading dataset...")
    dataset = instantiate_from_config(config.data.params.train)
    print(f"Dataset length: {len(dataset)}")

    # Training loop
    model.train()
    save_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex_checkpoints')
    os.makedirs(save_dir, exist_ok=True)

    print(f"\nStarting training for {args.steps} steps...")
    start_time = time.time()

    for step in range(args.steps):
        # Get batch
        idx = step % len(dataset)
        batch = dataset[idx]

        # Collate batch (add batch dim)
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v for k, v in batch.items()}

        # Prepare data (prepare_batch_data handles device placement)
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = model.prepare_batch_data(batch, device=device)

        B = cond_imgs.shape[0]
        t = torch.randint(0, model.num_timesteps, size=(B,)).long().to(device)

        # Get embeddings
        with torch.no_grad():
            weight_dtype = torch.float16

            # Ensure VAE is in correct dtype
            model.pipeline.vae = model.pipeline.vae.to(dtype=weight_dtype)

            if 'global_embeds' in batch:
                global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype)
                global_embeds = global_embeds.view(B, 1, -1)
                ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
                uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
                prompt_embeds = uc_text_emb + global_embeds * ramp
            else:
                prompt_embeds = model.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=False)

            cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
            added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
            added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()}

            latents = model.encode_target_images(target_imgs).to(weight_dtype)

            noise = torch.randn_like(latents)
            latents_noisy = model.train_scheduler.add_noise(latents, noise, t)

        # Forward with adapters
        # Clamp and sanitize geo_input to prevent NaN, cast to float32 for encoder
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        # Set geo_feats on wrapped resnets
        model._set_geo_feats_on_wrappers(geo_feats)

        noise_pred = model.pipeline.unet(
            latents_noisy,
            t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_latents),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=True,
        )[0]

        model._clear_geo_feats_on_wrappers()

        # Compute loss using model's compute_loss (foreground, edge, reg)
        loss, loss_dict = model.compute_loss(
            noise_pred, noise, target_imgs, mask, weight_dtype,
            depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
        )

        # Skip NaN steps
        if torch.isnan(loss) or torch.isinf(loss):
            print(f"Step {step+1}: NaN/Inf loss detected, skipping")
            optimizer.zero_grad()
            continue

        # Backward
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()

        # Logging
        if (step + 1) % 10 == 0:
            elapsed = time.time() - start_time
            steps_per_sec = (step + 1) / elapsed
            eta = (args.steps - step - 1) / steps_per_sec
            loss_parts = " | ".join(f"{k.split('/')[-1]}={v.item():.4f}" for k, v in loss_dict.items() if 'loss' in k)
            print(f"Step {step+1}/{args.steps} | {loss_parts} | "
                  f"Speed: {steps_per_sec:.2f} steps/s | ETA: {eta:.0f}s")

        # Save checkpoint
        if (step + 1) % args.save_every == 0:
            save_path = os.path.join(save_dir, f'geotex_step_{step+1:07d}.pt')
            model.save_geotex_weights(save_path)

    # Final save
    final_path = os.path.join(save_dir, 'geotex_final.pt')
    model.save_geotex_weights(final_path)

    total_time = time.time() - start_time
    print(f"\nTraining complete in {total_time:.0f}s")
    print(f"Average speed: {args.steps / total_time:.2f} steps/s")
    print(f"Checkpoints saved to: {save_dir}")


if __name__ == '__main__':
    main()
