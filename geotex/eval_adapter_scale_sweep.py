"""Adapter scale sweep: evaluate GeoTex with different adapter correction magnitudes.

Tests multiple adapter scales to find optimal strength without reference drift
or edge artifacts.

Usage:
    python geotex/eval_adapter_scale_sweep.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scales 0.0 0.25 0.5 0.75 1.0 1.25 1.5 \
        --num_objects 20 \
        --output_dir mvpoutput/geotex_refattn_v1/adapter_scale_sweep \
        --device cuda:0
"""
import os
import sys
import json
import csv
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
from eval import load_model, get_lpips, compute_lpips


@torch.no_grad()
def generate_with_scale(model, batch, device, weight_dtype, geo_feats, scale,
                        num_steps=50, init_latents=None):
    """Generate with adapter correction scaled by a factor."""
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

    # Set geo feats with scale
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)
        # Apply scale to all adapters
        for module in model.unet.modules():
            if hasattr(module, 'adapter'):
                module._adapter_scale = scale
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
            # Clear scale
            for module in model.unet.modules():
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents = unscale_latents(latents)
    image = unscale_image(model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0])
    return (image * 0.5 + 0.5).clamp(0, 1)


def main():
    parser = argparse.ArgumentParser(description="Adapter Scale Sweep")
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--scales', type=float, nargs='+', default=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
    parser.add_argument('--num_objects', type=int, default=20)
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16

    if args.output_dir is None:
        args.output_dir = 'mvpoutput/geotex_refattn_v1/adapter_scale_sweep'
    os.makedirs(args.output_dir, exist_ok=True)

    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))

    # Monkey-patch GeoTexResnetWrapper to apply scale
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    original_forward = GeoTexResnetWrapper.forward

    def scaled_forward(self, *args, **kwargs):
        hidden_states = self.resnet(*args, **kwargs)
        if self._current_geo_feats is not None:
            geo_feat = self._current_geo_feats.get(self.geo_feat_key)
            if geo_feat is not None:
                if geo_feat.shape[2:] != hidden_states.shape[2:]:
                    geo_feat = F.interpolate(geo_feat, size=hidden_states.shape[2:],
                                             mode='bilinear', align_corners=False)
                correction = self.adapter.compute_correction(hidden_states, geo_feat)
                self._last_correction = correction
                scale = getattr(self, '_adapter_scale', 1.0)
                hidden_states = hidden_states + correction * scale
        return hidden_states

    GeoTexResnetWrapper.forward = scaled_forward

    print(f"Scale sweep: scales={args.scales}, objects={num_objects}")

    try:
        lpips_fn = get_lpips(device)
    except:
        lpips_fn = None

    results = []

    for obj_idx in range(num_objects):
        from eval import collate_batch, prepare_batch
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for scale in args.scales:
            torch.manual_seed(args.seed)
            image = generate_with_scale(model, batch, device, weight_dtype, geo_feats,
                                        scale, args.steps, shared_latents)

            result = {
                'object_idx': obj_idx,
                'scale': scale,
                'full_psnr': compute_psnr(image, target_imgs).item(),
                'full_ssim': compute_ssim(image, target_imgs).item(),
            }
            if lpips_fn:
                try:
                    result['full_lpips'] = compute_lpips(image, target_imgs, device=device)
                except:
                    result['full_lpips'] = None

            # FG metrics
            fg_mask = mask > 0.5
            if fg_mask.sum() > 0:
                result['fg_psnr'] = compute_psnr(image, target_imgs, mask).item()
                result['fg_ssim'] = compute_ssim(image, target_imgs, mask).item()

            results.append(result)

        # Progress
        obj_results = [r for r in results if r['object_idx'] == obj_idx]
        best = max(obj_results, key=lambda r: r.get('fg_psnr', 0))
        print(f"  Object {obj_idx}: best scale={best['scale']:.2f} fg_PSNR={best.get('fg_psnr', 0):.2f}")

    # Write CSV
    csv_path = os.path.join(args.output_dir, 'scale_sweep_results.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Summary by scale
    summary = {}
    for scale in args.scales:
        scale_results = [r for r in results if r['scale'] == scale]
        summary[str(scale)] = {
            'mean_full_psnr': float(np.mean([r['full_psnr'] for r in scale_results])),
            'mean_full_ssim': float(np.mean([r['full_ssim'] for r in scale_results])),
            'mean_fg_psnr': float(np.mean([r.get('fg_psnr', 0) for r in scale_results])),
            'mean_fg_ssim': float(np.mean([r.get('fg_ssim', 0) for r in scale_results])),
        }
        if lpips_fn:
            lpips_vals = [r['full_lpips'] for r in scale_results if r.get('full_lpips') is not None]
            if lpips_vals:
                summary[str(scale)]['mean_full_lpips'] = float(np.mean(lpips_vals))

    with open(os.path.join(args.output_dir, 'scale_sweep_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary table
    print(f"\n{'='*70}")
    print("SCALE SWEEP SUMMARY")
    print(f"{'='*70}")
    print(f"{'Scale':>6} {'Full PSNR':>10} {'Full SSIM':>10} {'FG PSNR':>10} {'FG SSIM':>10}")
    for scale in args.scales:
        s = summary[str(scale)]
        print(f"{scale:6.2f} {s['mean_full_psnr']:10.2f} {s['mean_full_ssim']:10.4f} "
              f"{s['mean_fg_psnr']:10.2f} {s['mean_fg_ssim']:10.4f}")

    # Restore original forward
    GeoTexResnetWrapper.forward = original_forward

    print(f"\nResults: {args.output_dir}")


if __name__ == '__main__':
    main()
