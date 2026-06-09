"""
GeoTex-Adapter evaluation: direct denoising loop (no pipeline dependency).
Compares Original MV-Painter vs GeoTex-Adapter on test objects.
"""
import os
import sys
import json
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from einops import rearrange
from diffusers import EulerDiscreteScheduler


def scale_latents(latents):
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def unscale_image(image):
    return image / 0.5 * 0.8


def compute_psnr(pred, target, mask=None):
    if mask is not None:
        # Expand mask to match channels: (B,1,H,W) -> (B,C,H,W)
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
        # Use single-channel mask for SSIM
        mask_d = F.max_pool2d(mask[:, :1], 3, 1, 1)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return 0.0
        ssim_fg = (ssim_map[:, :1] * mask_d)[fg].mean().item()
        return ssim_fg
    return ssim_map.mean().item()


@torch.no_grad()
def generate_images(model, batch, device, weight_dtype, geo_feats=None, num_steps=50, init_latents=None):
    """Generate images using direct denoising loop with deterministic scheduler."""
    from torchvision.transforms import v2 as tv2

    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = tv2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]

    # Get prompt embeddings from pre-computed
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
    prompt_embeds = uc_text_emb + global_embeds * ramp

    # Encode condition image
    cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)

    # Get added cond kwargs
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}

    # Use deterministic scheduler (DDIM-style, no random noise added during steps)
    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)

    # Use shared initial latents for fair comparison
    if init_latents is None:
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(B, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
    latents = init_latents * scheduler.init_noise_sigma

    # Set adapters
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for t in scheduler.timesteps:
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t,
                encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False,
                is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        if geo_feats is not None:
            model._clear_geo_feats_on_wrappers()

    # Decode
    latents = unscale_latents(latents)
    image = unscale_image(model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0])
    image = (image * 0.5 + 0.5).clamp(0, 1)
    return image


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', default='/4T/CXY/MV-Painter/mvpoutput/geotex_checkpoints/geotex_step_0000500.pt')
    parser.add_argument('--num_objects', type=int, default=10)
    parser.add_argument('--output_dir', default='/4T/CXY/MV-Painter/mvpoutput/geotex_eval')
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Load model
    config = OmegaConf.load('/4T/CXY/MV-Painter/MVPainter/configs/mvpainter-geotex-uponly.yaml')
    model = instantiate_from_config(config.model)

    # Load checkpoint
    if args.checkpoint:
        print(f"Loading checkpoint: {args.checkpoint}")
        model.load_geotex_weights(args.checkpoint)

    # Move to device
    model.unet.to(device).to(dtype=weight_dtype)
    model.pipeline.vae.to(device).to(dtype=weight_dtype)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')
    model.pipeline.vae.eval()

    # Override encode methods
    from torchvision.transforms import v2 as tv2
    def encode_condition_image(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [tv2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors='pt').pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        return model.pipeline.vae.encode(image_pt).latent_dist.sample()
    model.encode_condition_image = encode_condition_image

    # Load test dataset
    dataset = instantiate_from_config(config.data.params.validation)
    print(f"Test dataset: {len(dataset)} objects")

    results = []
    num_objects = min(args.num_objects, len(dataset))

    for obj_idx in range(num_objects):
        print(f"\n--- Object {obj_idx + 1}/{num_objects} ---")
        batch = dataset[obj_idx]
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v for k, v in batch.items()}
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)

        # Prepare geometry features
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # Generate with shared initial latents for fair comparison
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        # Generate with adapter
        print("  Generating with adapter...")
        image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)

        # Generate without adapter (original) - SAME initial latents
        print("  Generating without adapter...")
        image_orig = generate_images(model, batch, device, weight_dtype, None, args.steps, shared_latents)

        # Compute metrics
        gt = target_imgs
        mask_fg = mask

        obj_result = {'object_idx': obj_idx}
        obj_result['orig_psnr'] = compute_psnr(image_orig, gt, mask_fg)
        obj_result['orig_ssim'] = compute_ssim(image_orig, gt, mask_fg)
        obj_result['adapter_psnr'] = compute_psnr(image_adapter, gt, mask_fg)
        obj_result['adapter_ssim'] = compute_ssim(image_adapter, gt, mask_fg)

        print(f"  Original: PSNR={obj_result['orig_psnr']:.2f}, SSIM={obj_result['orig_ssim']:.4f}")
        print(f"  Adapter:  PSNR={obj_result['adapter_psnr']:.2f}, SSIM={obj_result['adapter_ssim']:.4f}")

        results.append(obj_result)

        # Save visualization for first 3 objects
        if obj_idx < 3:
            vis = torch.cat([gt, image_orig, image_adapter], dim=0)
            save_path = os.path.join(args.output_dir, f'vis_object_{obj_idx:03d}.png')
            save_image(vis, save_path, nrow=3)
            print(f"  Saved: {save_path}")

    # Aggregate
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    for metric in ['psnr', 'ssim']:
        orig_vals = [r[f'orig_{metric}'] for r in results]
        adapter_vals = [r[f'adapter_{metric}'] for r in results]
        print(f"\n{metric.upper()}:")
        print(f"  Original: {np.mean(orig_vals):.4f} ± {np.std(orig_vals):.4f}")
        print(f"  Adapter:  {np.mean(adapter_vals):.4f} ± {np.std(adapter_vals):.4f}")
        diff = np.mean(adapter_vals) - np.mean(orig_vals)
        print(f"  Diff:     {diff:+.4f}")

    # Save results
    results_path = os.path.join(args.output_dir, 'eval_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")


if __name__ == '__main__':
    main()
