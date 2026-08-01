"""Quick evaluation script for GeoTex v2 checkpoints.

Loads a checkpoint, runs inference on N test objects, computes metrics,
and saves a comparison grid with correct GT/C3 alignment.

Usage:
    python geotex/eval_v2_quick.py \
        --checkpoint mvpoutput/geotex_v2_quick/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/geotex_v2_eval \
        --num_objects 8
"""
import os
import sys
import json
import argparse
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image, make_grid
from diffusers import EulerDiscreteScheduler
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def unscale_image(image):
    return image / 0.5 * 0.8


def compute_psnr(pred, target, mask=None):
    if mask is not None:
        if mask.shape[1] == 1 and pred.shape[1] > 1:
            mask = mask.expand_as(pred)
        fg = mask > 0.5
        if fg.sum() == 0:
            return 0.0
        mse = ((pred[fg] - target[fg]) ** 2).mean()
    else:
        mse = ((pred - target) ** 2).mean()
    if mse == 0:
        return float('inf')
    return 10 * torch.log10(1.0 / mse).item()


def compute_ssim(pred, target, mask=None):
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)
    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))
    if mask is not None:
        mask_d = F.max_pool2d(mask[:, :1], 3, 1, 1)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return 0.0
        return (ssim_map[:, :1] * mask_d)[fg].mean().item()
    return ssim_map.mean().item()


def load_model(config_path, device):
    """Load model with proper setup."""
    config = OmegaConf.load(config_path)
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

    def encode_condition_image(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors='pt').pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        return model.pipeline.vae.encode(image_pt).latent_dist.sample()
    model.encode_condition_image = encode_condition_image

    return model, config


def load_checkpoint(model, ckpt_path):
    """Load adapter+encoder weights from checkpoint."""
    state = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    if 'adapters' in state:
        model.adapters.load_state_dict(state['adapters'])
        model.geo_encoder.load_state_dict(state['geo_encoder'])
    else:
        # Might be full state dict
        model.adapters.load_state_dict(state)
    print(f"Loaded checkpoint: {ckpt_path}")


@torch.no_grad()
def generate_single(model, batch, device, geo_feats=None, num_steps=50, seed=42,
                    use_tcas=True):
    """Generate images for a single object with optional TCAS."""
    weight_dtype = torch.float16
    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]

    # Prompt embeddings
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
    prompt_embeds = uc_text_emb + global_embeds * ramp

    # Encode condition
    cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)

    # Added cond kwargs
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}

    # Scheduler
    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)

    # Initial latents (deterministic)
    torch.manual_seed(seed)
    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    latents = torch.randn(B, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
    latents = latents * scheduler.init_noise_sigma

    # Set geo feats if provided
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            # Per-layer TCAS schedule
            if use_tcas and geo_feats is not None:
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        # Simple linear TCAS: scale peaks at mid-timesteps
                        progress = step_idx / num_steps
                        if module.depth_group == 'deep':
                            scale = 1.25 if progress < 0.7 else 0.8
                        elif module.depth_group == 'middle':
                            scale = 1.5 if 0.2 < progress < 0.8 else 0.8
                        else:  # shallow
                            scale = 0.6  # Always conservative for shallow
                        module._adapter_scale = scale

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t,
                encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        if geo_feats is not None:
            model._clear_geo_feats_on_wrappers()
        # Clear adapter scales
        for module in model.unet.modules():
            if isinstance(module, GeoTexResnetWrapper):
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    # Decode
    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = (unscale_image(decoded) * 0.5 + 0.5).clamp(0, 1)
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', required=True, help='Path to checkpoint (EMA preferred)')
    parser.add_argument('--output_dir', default='mvpoutput/geotex_v2_eval')
    parser.add_argument('--num_objects', type=int, default=8)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--no_tcas', action='store_true', help='Disable TCAS schedule (uniform scale)')
    args = parser.parse_args()

    device = torch.device(args.device)
    os.makedirs(args.output_dir, exist_ok=True)

    # Load model
    print("Loading model...")
    model, config = load_model(args.config, device)

    # Load checkpoint
    load_checkpoint(model, args.checkpoint)

    # Load test dataset
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Test dataset: {len(dataset)} objects, evaluating {num_objects}")

    results = []
    gt_images = []
    c3_images = []
    orig_images = []

    for obj_idx in range(num_objects):
        print(f"\n[{obj_idx+1}/{num_objects}] Object {obj_idx}")

        # Load batch - SAME object for both GT and generation
        sample = dataset[obj_idx]
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
                 for k, v in sample.items()}
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        # Get GT and geometry
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)

        # Prepare geometry features
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # Generate with adapter (C3 = GeoTex condition 3-channel geo)
        image_c3 = generate_single(
            model, batch, device, geo_feats=geo_feats,
            num_steps=args.num_steps, seed=args.seed,
            use_tcas=not args.no_tcas
        )

        # Generate without adapter (original MV-Painter)
        image_orig = generate_single(
            model, batch, device, geo_feats=None,
            num_steps=args.num_steps, seed=args.seed,
            use_tcas=False
        )

        # Metrics
        psnr_c3 = compute_psnr(image_c3, target_imgs, mask)
        ssim_c3 = compute_ssim(image_c3, target_imgs, mask)
        psnr_orig = compute_psnr(image_orig, target_imgs, mask)
        ssim_orig = compute_ssim(image_orig, target_imgs, mask)

        print(f"  Original: PSNR={psnr_orig:.2f} SSIM={ssim_orig:.4f}")
        print(f"  GeoTex:   PSNR={psnr_c3:.2f} SSIM={ssim_c3:.4f}")
        print(f"  Δ PSNR={psnr_c3-psnr_orig:+.2f}  Δ SSIM={ssim_c3-ssim_orig:+.4f}")

        results.append({
            'obj_idx': obj_idx,
            'orig_psnr': psnr_orig, 'orig_ssim': ssim_orig,
            'c3_psnr': psnr_c3, 'c3_ssim': ssim_c3,
        })

        # Save individual pairs (correct alignment: same obj_idx for GT and C3)
        save_image(target_imgs, os.path.join(args.output_dir, f'obj_{obj_idx:04d}_gt.png'))
        save_image(image_c3, os.path.join(args.output_dir, f'obj_{obj_idx:04d}_c3.png'))
        save_image(image_orig, os.path.join(args.output_dir, f'obj_{obj_idx:04d}_orig.png'))

        gt_images.append(target_imgs[0])
        c3_images.append(image_c3[0])
        orig_images.append(image_orig[0])

    # Make comparison grid: rows = [GT, Original, GeoTex], cols = objects
    print("\nMaking comparison grid...")
    all_rows = []
    for row_imgs in [gt_images, orig_images, c3_images]:
        row = torch.stack(row_imgs, dim=0)  # (N, C, H, W)
        all_rows.append(row)
    grid_tensor = torch.cat(all_rows, dim=0)  # (3*N, C, H, W)
    grid = make_grid(grid_tensor, nrow=num_objects, padding=2, pad_value=1.0)
    save_image(grid, os.path.join(args.output_dir, 'comparison_grid.png'))

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Objects: {num_objects}, Steps: {args.num_steps}, TCAS: {not args.no_tcas}")
    print()

    orig_psnr = np.mean([r['orig_psnr'] for r in results])
    orig_ssim = np.mean([r['orig_ssim'] for r in results])
    c3_psnr = np.mean([r['c3_psnr'] for r in results])
    c3_ssim = np.mean([r['c3_ssim'] for r in results])

    print(f"{'Method':<12} {'PSNR':>8} {'FG-SSIM':>8}")
    print(f"{'-'*30}")
    print(f"{'Original':<12} {orig_psnr:>8.2f} {orig_ssim:>8.4f}")
    print(f"{'GeoTex':<12} {c3_psnr:>8.2f} {c3_ssim:>8.4f}")
    print(f"{'Δ (C3-Orig)':<12} {c3_psnr-orig_psnr:>+8.2f} {c3_ssim-orig_ssim:>+8.4f}")

    # Save results
    summary = {
        'checkpoint': args.checkpoint,
        'num_objects': num_objects,
        'num_steps': args.num_steps,
        'use_tcas': not args.no_tcas,
        'orig_psnr_mean': orig_psnr,
        'orig_ssim_mean': orig_ssim,
        'c3_psnr_mean': c3_psnr,
        'c3_ssim_mean': c3_ssim,
        'per_object': results,
    }
    with open(os.path.join(args.output_dir, 'eval_results.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to: {args.output_dir}/eval_results.json")
    print(f"Grid saved to: {args.output_dir}/comparison_grid.png")


if __name__ == '__main__':
    main()
