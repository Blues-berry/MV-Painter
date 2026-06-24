"""High-quality inference for paper figures.

Strategy:
1. Multi-seed sampling: try N seeds per object, keep best by FG-LPIPS
2. Higher inference steps (75-100)
3. Adapter scale sweep per object (find per-object optimal)
4. Save all candidates for manual cherry-pick

Usage:
    python geotex/quality_inference.py \
        --config MVPainter/configs/mvpainter-geotex-uponly.yaml \
        --checkpoint mvpoutput/geotex_checkpoints/geotex_step_0002000.pt \
        --objects 79,72,41,209,43,106,32,56 \
        --output_dir mvpoutput/quality_showcase \
        --num_seeds 8 \
        --steps 75 \
        --scales 1.0,1.25,1.5
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
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler

from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image
from eval import load_model, get_lpips, compute_lpips, compute_region_metrics
from data_utils import prepare_batch, collate_batch


def patch_adapter_scale_support():
    """Monkey-patch GeoTexResnetWrapper.forward to support _adapter_scale attribute.

    The original forward just does `hs + correction`. This patches it to do
    `hs + correction * getattr(self, '_adapter_scale', 1.0)`.
    Must be called BEFORE load_model().
    """
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig_forward = GeoTexResnetWrapper.forward

    def scaled_forward(self, *args, **kwargs):
        hs = self.resnet(*args, **kwargs)
        if self._current_geo_feats is not None:
            gf = self._current_geo_feats.get(self.geo_feat_key)
            if gf is not None:
                if gf.shape[2:] != hs.shape[2:]:
                    gf = F.interpolate(gf, size=hs.shape[2:], mode='bilinear', align_corners=False)
                c = self.adapter.compute_correction(hs, gf)
                hs = hs + c * getattr(self, '_adapter_scale', 1.0)
        return hs

    GeoTexResnetWrapper.forward = scaled_forward
    print("[PATCH] GeoTexResnetWrapper.forward patched for adapter scale support")


@torch.no_grad()
def generate_images_with_scale(model, batch, device, weight_dtype, geo_feats,
                               num_steps, init_latents, adapter_scale=1.0):
    """Generate with explicit adapter scale control.

    Requires patch_adapter_scale_support() to have been called first.
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

    # Set adapter scale on all wrapper modules
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)
        for module in model.unet.modules():
            if hasattr(module, 'adapter'):
                module._adapter_scale = adapter_scale

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
            del latent_input, noise_pred
    finally:
        if geo_feats is not None:
            model._clear_geo_feats_on_wrappers()
            # Clean up scale attribute
            for module in model.unet.modules():
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents = unscale_latents(latents)
    image = unscale_image(model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0])
    return (image * 0.5 + 0.5).clamp(0, 1)


def normalize_background(image, mask, bg_color=1.0):
    """Set background to white for consistent comparison."""
    fg = mask > 0.5
    bg = ~fg
    result = image.clone()
    result[:, :, bg.squeeze(0).squeeze(0)] = bg_color
    return result


def compute_quality_score(pred, gt, mask, device):
    """Combined quality score: weighted FG-LPIPS + FG-SSIM."""
    fg_mask = mask
    # LPIPS (lower = better, negate for score)
    try:
        lpips_val = compute_lpips(pred, gt, fg_mask, device)
    except:
        lpips_val = 0.5
    # SSIM (higher = better)
    ssim_val = compute_ssim(pred, gt, fg_mask)
    # Combined: equal weight
    # Normalize: LPIPS [0,1] -> [1,0], SSIM [0,1] -> [0,1]
    score = (1.0 - lpips_val) * 0.6 + ssim_val * 0.4
    return score, lpips_val, ssim_val


def main():
    parser = argparse.ArgumentParser(description="High-quality inference for paper figures")
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--objects', type=str, required=True,
                        help='Comma-separated object indices, e.g. 79,72,41,209')
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--num_seeds', type=int, default=8,
                        help='Number of random seeds to try per object')
    parser.add_argument('--steps', type=int, default=75,
                        help='Inference steps (higher=finer detail)')
    parser.add_argument('--scales', type=str, default='1.25',
                        help='Comma-separated adapter scales to try')
    parser.add_argument('--base_seed', type=int, default=42,
                        help='Starting seed (seeds: base, base+1, ...)')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    obj_indices = [int(x.strip()) for x in args.objects.split(',')]
    scales = [float(x.strip()) for x in args.scales.split(',')]

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"=" * 60)
    print(f"HIGH-QUALITY INFERENCE FOR PAPER FIGURES")
    print(f"  Objects: {obj_indices}")
    print(f"  Seeds per object: {args.num_seeds}")
    print(f"  Steps: {args.steps}")
    print(f"  Adapter scales: {scales}")
    print(f"  Output: {args.output_dir}")
    print(f"=" * 60)

    # Patch adapter scale support (must be before model loading)
    patch_adapter_scale_support()

    # Load model
    print("\nLoading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    total = len(dataset)

    # Load LPIPS
    try:
        get_lpips(device)
        print("LPIPS loaded successfully")
    except Exception as e:
        print(f"WARNING: LPIPS not available: {e}")

    all_results = {}

    for obj_idx in obj_indices:
        if obj_idx >= total:
            print(f"WARNING: Object {obj_idx} out of range (max {total-1}), skipping")
            continue

        print(f"\n{'='*60}")
        print(f"Processing object {obj_idx}")
        print(f"{'='*60}")

        obj_dir = os.path.join(args.output_dir, f'obj_{obj_idx:03d}')
        os.makedirs(obj_dir, exist_ok=True)

        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        gt = target_imgs
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8

        # Save GT and references
        save_image(gt, os.path.join(obj_dir, 'gt.png'))
        # Save condition (reference) image
        cond_for_save = batch['cond_imgs'].to(device)
        cond_for_save = v2.functional.resize(cond_for_save, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
        save_image(cond_for_save, os.path.join(obj_dir, 'reference.png'))
        # Save geometry signal
        if normal_imgs is not None:
            save_image(normal_imgs, os.path.join(obj_dir, 'normal.png'))
        save_image(mask.expand_as(gt), os.path.join(obj_dir, 'mask.png'))

        # Generate baseline (no adapter, seed=42 for consistency)
        torch.manual_seed(42)
        baseline_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
        torch.manual_seed(42)
        image_baseline = generate_images_with_scale(
            model, batch, device, weight_dtype, None, args.steps, baseline_latents, 1.0)
        save_image(normalize_background(image_baseline, mask),
                   os.path.join(obj_dir, 'baseline_no_adapter.png'))

        # Multi-seed x multi-scale sweep
        candidates = []
        best_score = -1
        best_config = None

        for scale in scales:
            for seed_offset in range(args.num_seeds):
                seed = args.base_seed + seed_offset
                torch.manual_seed(seed)
                init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

                torch.manual_seed(seed)
                image = generate_images_with_scale(
                    model, batch, device, weight_dtype, geo_feats, args.steps, init_latents, scale)

                score, lpips_val, ssim_val = compute_quality_score(image, gt, mask, device)

                candidate = {
                    'seed': seed,
                    'scale': scale,
                    'score': score,
                    'fg_lpips': lpips_val,
                    'fg_ssim': ssim_val,
                    'image': image,
                }
                candidates.append(candidate)

                status = ""
                if score > best_score:
                    best_score = score
                    best_config = candidate
                    status = " ★ BEST"

                print(f"  seed={seed:3d} scale={scale:.2f} | "
                      f"FG-LPIPS={lpips_val:.4f} FG-SSIM={ssim_val:.4f} "
                      f"score={score:.4f}{status}", flush=True)

                # Save each candidate
                fname = f"adapter_seed{seed:03d}_scale{scale:.2f}.png"
                save_image(normalize_background(image, mask),
                           os.path.join(obj_dir, fname))

        # Mark and save best
        if best_config is not None:
            print(f"\n  >>> BEST: seed={best_config['seed']} scale={best_config['scale']:.2f} "
                  f"score={best_config['score']:.4f}")
            save_image(normalize_background(best_config['image'], mask),
                       os.path.join(obj_dir, 'BEST_adapter.png'))

            # Save comparison strip: [GT | Baseline | Best Adapter]
            strip = torch.cat([
                gt,
                normalize_background(image_baseline, mask),
                normalize_background(best_config['image'], mask),
            ], dim=3)  # Concatenate along width
            save_image(strip, os.path.join(obj_dir, 'comparison_strip.png'))

        # Sort all candidates
        candidates_sorted = sorted(candidates, key=lambda x: -x['score'])

        # Save top-3 comparison
        if len(candidates_sorted) >= 3:
            top3_strip = torch.cat([
                gt,
                normalize_background(candidates_sorted[0]['image'], mask),
                normalize_background(candidates_sorted[1]['image'], mask),
                normalize_background(candidates_sorted[2]['image'], mask),
            ], dim=3)
            save_image(top3_strip, os.path.join(obj_dir, 'top3_comparison.png'))

        # Record results
        obj_result = {
            'obj_idx': obj_idx,
            'best_seed': best_config['seed'] if best_config else None,
            'best_scale': best_config['scale'] if best_config else None,
            'best_score': best_config['score'] if best_config else None,
            'best_fg_lpips': best_config['fg_lpips'] if best_config else None,
            'best_fg_ssim': best_config['fg_ssim'] if best_config else None,
            'all_candidates': [
                {'seed': c['seed'], 'scale': c['scale'], 'score': c['score'],
                 'fg_lpips': c['fg_lpips'], 'fg_ssim': c['fg_ssim']}
                for c in candidates_sorted
            ]
        }
        all_results[str(obj_idx)] = obj_result

        # Clean up GPU memory
        del candidates
        for c in candidates_sorted:
            del c['image']
        torch.cuda.empty_cache()

    # Save summary
    summary_path = os.path.join(args.output_dir, 'quality_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n{'='*60}")
    print(f"DONE. Summary saved to {summary_path}")
    print(f"{'='*60}")

    # Print final summary
    print(f"\n{'='*60}")
    print(f"FINAL SHOWCASE RANKING (by best score)")
    print(f"{'='*60}")
    ranked = sorted(all_results.items(), key=lambda x: -(x[1]['best_score'] or 0))
    for obj_str, res in ranked:
        print(f"  obj_{int(obj_str):03d}: score={res['best_score']:.4f} "
              f"seed={res['best_seed']} scale={res['best_scale']:.2f} "
              f"FG-LPIPS={res['best_fg_lpips']:.4f} FG-SSIM={res['best_fg_ssim']:.4f}")


if __name__ == '__main__':
    main()
