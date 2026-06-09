"""GeoTex-Adapter evaluation. Fair comparison: same seed, scheduler, init latents."""
import os
import sys
import json
import csv
import argparse
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from diffusers import EulerDiscreteScheduler

from metrics import compute_psnr, compute_ssim, unscale_latents, unscale_image
from data_utils import prepare_batch, collate_batch
from vis_utils import save_comparison, save_error_maps


@torch.no_grad()
def generate_images(model, batch, device, weight_dtype, geo_feats=None,
                    num_steps=50, init_latents=None):
    """Generate images with deterministic scheduler and shared init latents."""
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

    if init_latents is None:
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(B, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
    latents = init_latents * scheduler.init_noise_sigma

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
                return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        if geo_feats is not None:
            model._clear_geo_feats_on_wrappers()

    latents = unscale_latents(latents)
    image = unscale_image(model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0])
    return (image * 0.5 + 0.5).clamp(0, 1)


def load_model(config_path, checkpoint_path, device):
    """Load model with optional checkpoint."""
    config = OmegaConf.load(config_path)
    model = instantiate_from_config(config.model)
    if checkpoint_path:
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


def main():
    parser = argparse.ArgumentParser(description="GeoTex-Adapter Evaluation")
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--checkpoint', default=None, help='Adapter checkpoint (None = original)')
    parser.add_argument('--num_objects', type=int, default=10)
    parser.add_argument('--object_list', default=None, help='Object list file (overrides num_objects)')
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--save_vis', action='store_true', default=True)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16

    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex', 'eval')
    os.makedirs(args.output_dir, exist_ok=True)

    # Load model
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)

    # Load dataset
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Evaluating {num_objects} objects")

    results = []
    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # Shared init latents for fair comparison
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        # Generate with adapter
        torch.manual_seed(args.seed)
        image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)

        # Generate without adapter (original)
        torch.manual_seed(args.seed)
        image_orig = generate_images(model, batch, device, weight_dtype, None, args.steps, shared_latents)

        # Compute metrics
        gt = target_imgs
        obj_result = {
            'object_idx': obj_idx,
            'orig_psnr': compute_psnr(image_orig, gt, mask),
            'orig_ssim': compute_ssim(image_orig, gt, mask),
            'adapter_psnr': compute_psnr(image_adapter, gt, mask),
            'adapter_ssim': compute_ssim(image_adapter, gt, mask),
            'fg_orig_psnr': compute_psnr(image_orig, gt, mask),
            'fg_adapter_psnr': compute_psnr(image_adapter, gt, mask),
            'fg_orig_ssim': compute_ssim(image_orig, gt, mask),
            'fg_adapter_ssim': compute_ssim(image_adapter, gt, mask),
        }
        results.append(obj_result)

        pd = obj_result['adapter_psnr'] - obj_result['orig_psnr']
        sd = obj_result['adapter_ssim'] - obj_result['orig_ssim']
        print(f"  Object {obj_idx}: PSNR {obj_result['orig_psnr']:.2f}→{obj_result['adapter_psnr']:.2f} ({pd:+.2f}) "
              f"SSIM {obj_result['orig_ssim']:.4f}→{obj_result['adapter_ssim']:.4f} ({sd:+.4f})")

        if args.save_vis and obj_idx < 3:
            save_comparison(gt, image_orig, image_adapter, args.output_dir, f"vis_{obj_idx:03d}", 1)
            save_error_maps(gt, image_orig, image_adapter, mask, args.output_dir, f"err_{obj_idx:03d}", 1)

    # Write per-object CSV
    csv_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Write summary JSON
    summary = {}
    for metric in ['psnr', 'ssim']:
        orig_vals = [r[f'orig_{metric}'] for r in results]
        adapter_vals = [r[f'adapter_{metric}'] for r in results]
        summary[metric] = {
            'orig_mean': float(np.mean(orig_vals)),
            'orig_std': float(np.std(orig_vals)),
            'adapter_mean': float(np.mean(adapter_vals)),
            'adapter_std': float(np.std(adapter_vals)),
            'diff': float(np.mean(adapter_vals) - np.mean(orig_vals)),
            'improved': sum(1 for o, a in zip(orig_vals, adapter_vals) if a > o),
            'total': len(results),
        }
    summary['config'] = args.config
    summary['checkpoint'] = args.checkpoint
    summary['num_objects'] = num_objects

    json_path = os.path.join(args.output_dir, 'summary_metrics.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults: {json_path}")
    for metric in ['psnr', 'ssim']:
        s = summary[metric]
        print(f"  {metric.upper()}: {s['orig_mean']:.4f} → {s['adapter_mean']:.4f} ({s['diff']:+.4f}) [{s['improved']}/{s['total']}]")


if __name__ == '__main__':
    main()
