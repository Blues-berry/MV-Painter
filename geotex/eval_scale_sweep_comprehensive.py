"""Comprehensive adapter scale sweep evaluation.

Generates images at different adapter scales and computes:
- Full metrics (PSNR/SSIM/LPIPS)
- Background-normalized metrics (bg-white, bg-black)
- Foreground crop metrics
- Edge metrics
- Mask sensitivity (erode/dilate)

Usage:
    python geotex/eval_scale_sweep_comprehensive.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scales 0.25 0.5 0.75 1.0 1.25 \
        --num_objects 50 \
        --output_dir mvpoutput/geotex_refattn_v1/scale_sweep_50obj \
        --device cuda:1
"""
import os
import sys
import json
import csv
import argparse
import signal
import traceback
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms
from torchvision.transforms import v2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, unscale_latents, unscale_image

# Ignore SIGTERM for batch runner compatibility
signal.signal(signal.SIGTERM, signal.SIG_IGN)


def get_lpips_fn(device):
    try:
        import lpips
        return lpips.LPIPS(net='alex').to(device).eval()
    except:
        return None


def compute_lpips(pred, target, mask=None, lpips_fn=None, device=None):
    if lpips_fn is None:
        return None
    p = pred * 2 - 1
    t = target * 2 - 1
    if mask is not None:
        m = mask[:, :1]
        if m.shape[2:] != p.shape[2:]:
            m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
        p = p * m
        t = t * m
    with torch.no_grad():
        return lpips_fn(p, t).item()


def load_model(config_path, checkpoint_path, device):
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

    # Set geo feats and scale
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)
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
            for module in model.unet.modules():
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents = unscale_latents(latents)
    image = unscale_image(model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0])
    return (image * 0.5 + 0.5).clamp(0, 1)


def normalize_background(image, mask, bg_value=1.0):
    bg = (mask < 0.5).expand_as(image)
    result = image.clone()
    result[bg] = bg_value
    return result


def fg_bbox_crop(image, mask, padding=0.1):
    fg = mask[0, 0] > 0.5
    if fg.sum() == 0:
        return image, mask
    rows = torch.any(fg, dim=1)
    cols = torch.any(fg, dim=0)
    rmin, rmax = torch.where(rows)[0][[0, -1]]
    cmin, cmax = torch.where(cols)[0][[0, -1]]
    H, W = fg.shape
    ph = int((rmax - rmin).item() * padding)
    pw = int((cmax - cmin).item() * padding)
    rmin = max(0, rmin - ph)
    rmax = min(H - 1, rmax + ph)
    cmin = max(0, cmin - pw)
    cmax = min(W - 1, cmax + pw)
    rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
    return image[:, :, rmin:rmax+1, cmin:cmax+1], mask[:, :, rmin:rmax+1, cmin:cmax+1]


def erode_mask(mask, kernel_size):
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    return (F.conv2d(mask, kernel, padding=padding) >= kernel_size * kernel_size).float()


def dilate_mask(mask, kernel_size):
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    return (F.conv2d(mask, kernel, padding=padding) > 0).float()


def compute_all_metrics(pred, target, mask, edge_mask, lpips_fn, device):
    """Compute full set of metrics for one image pair."""
    r = {}

    # Full metrics
    r['full_psnr'] = compute_psnr(pred, target)
    r['full_ssim'] = compute_ssim(pred, target)
    r['full_lpips'] = compute_lpips(pred, target, lpips_fn=lpips_fn, device=device)

    # Foreground (original mask)
    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)
    r['fg_lpips'] = compute_lpips(pred, target, mask, lpips_fn=lpips_fn, device=device)

    # Background
    bg_mask = 1.0 - mask
    r['bg_psnr'] = compute_psnr(pred, target, bg_mask)
    r['bg_ssim'] = compute_ssim(pred, target, bg_mask)
    r['bg_lpips'] = compute_lpips(pred, target, bg_mask, lpips_fn=lpips_fn, device=device)

    # Edge
    r['edge_psnr'] = compute_psnr(pred, target, edge_mask)
    r['edge_ssim'] = compute_ssim(pred, target, edge_mask)
    r['edge_lpips'] = compute_lpips(pred, target, edge_mask, lpips_fn=lpips_fn, device=device)

    # Non-edge FG
    nef = mask * (1 - edge_mask)
    r['nef_psnr'] = compute_psnr(pred, target, nef)
    r['nef_ssim'] = compute_ssim(pred, target, nef)

    # BG-normalized (white)
    pred_w = normalize_background(pred, mask, 1.0)
    target_w = normalize_background(target, mask, 1.0)
    r['bgwhite_psnr'] = compute_psnr(pred_w, target_w)
    r['bgwhite_ssim'] = compute_ssim(pred_w, target_w)
    r['bgwhite_lpips'] = compute_lpips(pred_w, target_w, lpips_fn=lpips_fn, device=device)

    # BG-normalized (black)
    pred_b = normalize_background(pred, mask, 0.0)
    target_b = normalize_background(target, mask, 0.0)
    r['bgblack_psnr'] = compute_psnr(pred_b, target_b)
    r['bgblack_ssim'] = compute_ssim(pred_b, target_b)

    # FG crop
    pred_crop, mask_crop = fg_bbox_crop(pred, mask, padding=0.1)
    target_crop, _ = fg_bbox_crop(target, mask, padding=0.1)
    r['crop_psnr'] = compute_psnr(pred_crop, target_crop)
    r['crop_ssim'] = compute_ssim(pred_crop, target_crop)
    r['crop_lpips'] = compute_lpips(pred_crop, target_crop, lpips_fn=lpips_fn, device=device)
    r['crop_area_ratio'] = float(pred_crop.numel() / pred.numel())

    # Mask sensitivity: erode
    for size in [3, 5, 10]:
        m_eroded = erode_mask(mask, size * 2 + 1)
        r[f'fg_psnr_e{size}'] = compute_psnr(pred, target, m_eroded)
        r[f'fg_ssim_e{size}'] = compute_ssim(pred, target, m_eroded)

    # Mask sensitivity: dilate
    for size in [3, 5, 10]:
        m_dilated = dilate_mask(mask, size * 2 + 1)
        r[f'fg_psnr_d{size}'] = compute_psnr(pred, target, m_dilated)
        r[f'fg_ssim_d{size}'] = compute_ssim(pred, target, m_dilated)

    return r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--scales', type=float, nargs='+', default=[0.25, 0.5, 0.75, 1.0, 1.25])
    parser.add_argument('--num_objects', type=int, default=50)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--device', default='cuda:1')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Monkey-patch GeoTexResnetWrapper for scale support
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _original_forward = GeoTexResnetWrapper.forward

    def scaled_forward(self, *f_args, **f_kwargs):
        hidden_states = self.resnet(*f_args, **f_kwargs)
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

    print(f"Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Scale sweep: {len(args.scales)} scales × {num_objects} objects", flush=True)

    lpips_fn = get_lpips_fn(device)

    # Save config snapshot
    snapshot = {
        'config': args.config,
        'checkpoint': args.checkpoint,
        'scales': args.scales,
        'num_objects': num_objects,
        'steps': args.steps,
        'seed': args.seed,
        'device': args.device,
    }
    with open(os.path.join(args.output_dir, 'config_snapshot.json'), 'w') as f:
        json.dump(snapshot, f, indent=2)

    from eval import collate_batch, prepare_batch

    all_results = {}

    for scale in args.scales:
        scale_dir = os.path.join(args.output_dir, f'scale_{scale:.2f}'.replace('.', 'p'))
        os.makedirs(scale_dir, exist_ok=True)
        os.makedirs(os.path.join(scale_dir, 'visualizations'), exist_ok=True)

        print(f"\n{'='*60}", flush=True)
        print(f"Scale = {scale}", flush=True)
        print(f"{'='*60}", flush=True)

        scale_results = []

        for obj_idx in range(num_objects):
            batch = collate_batch(dataset, obj_idx, device)
            cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
                prepare_batch(batch, model.img_size, device)

            geo_clean = geo_input.float().clamp(0, 1)
            geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)

            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            torch.manual_seed(args.seed)
            shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

            # Generate with scale
            torch.manual_seed(args.seed)
            image_scaled = generate_with_scale(model, batch, device, weight_dtype, geo_feats,
                                               scale, args.steps, shared_latents)

            # Generate baseline (no adapter)
            torch.manual_seed(args.seed)
            image_orig = generate_with_scale(model, batch, device, weight_dtype, None,
                                             0, args.steps, shared_latents)

            gt = target_imgs

            # Edge mask
            edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
            from metrics import compute_edge_mask
            edge_mask = compute_edge_mask(edge_source, threshold=0.1)
            if edge_mask.shape[2:] != gt.shape[2:]:
                edge_mask = F.interpolate(edge_mask, size=gt.shape[2:], mode='bilinear', align_corners=False)

            # Compute metrics for adapter output
            adapter_metrics = compute_all_metrics(image_scaled, gt, mask, edge_mask, lpips_fn, device)
            orig_metrics = compute_all_metrics(image_orig, gt, mask, edge_mask, lpips_fn, device)

            # Build result row
            r = {'object_idx': obj_idx, 'scale': scale, 'fg_ratio': float((mask > 0.5).sum().item() / mask.numel())}
            for k, v in adapter_metrics.items():
                r[f'adapter_{k}'] = v
            for k, v in orig_metrics.items():
                r[f'orig_{k}'] = v
            # Deltas
            for k in adapter_metrics:
                if adapter_metrics[k] is not None and orig_metrics[k] is not None:
                    r[f'delta_{k}'] = adapter_metrics[k] - orig_metrics[k]

            scale_results.append(r)

            if obj_idx % 10 == 0:
                print(f"  Object {obj_idx}: crop_psnr={r.get('delta_crop_psnr',0):+.2f} "
                      f"crop_ssim={r.get('delta_crop_ssim',0):+.4f} "
                      f"edge_ssim={r.get('delta_edge_ssim',0):+.4f}", flush=True)

            # Save visualization for first 5 objects
            if obj_idx < 5:
                vis_dir = os.path.join(scale_dir, 'visualizations')
                from torchvision.utils import save_image
                prefix = f"obj_{obj_idx:03d}"
                save_image(gt, os.path.join(vis_dir, f'{prefix}_gt.png'))
                save_image(image_orig, os.path.join(vis_dir, f'{prefix}_orig.png'))
                save_image(image_scaled, os.path.join(vis_dir, f'{prefix}_adapter.png'))

        # Save per-object CSV
        fieldnames = list(scale_results[0].keys())
        with open(os.path.join(scale_dir, 'per_object_metrics.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(scale_results)

        # Compute summary
        summary = {'scale': scale, 'num_objects': len(scale_results)}
        for col in fieldnames:
            if col in ('object_idx', 'scale', 'fg_ratio'):
                continue
            vals = [r[col] for r in scale_results if r.get(col) is not None]
            if vals:
                arr = np.array(vals)
                pos = int(np.sum(arr > 0)) if 'delta' in col else None
                summary[col] = {
                    'mean': float(arr.mean()),
                    'std': float(arr.std()),
                    'positive': pos,
                    'total': len(arr),
                }

        with open(os.path.join(scale_dir, 'summary_metrics.json'), 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        all_results[scale] = summary

        # Print key metrics
        print(f"\n  Scale {scale} Summary:", flush=True)
        for metric in ['delta_full_psnr', 'delta_crop_psnr', 'delta_crop_ssim',
                       'delta_fg_ssim', 'delta_edge_ssim', 'delta_crop_lpips']:
            if metric in summary:
                s = summary[metric]
                print(f"    {metric}: {s['mean']:+.4f} [{s['positive']}/{s['total']}]", flush=True)

    # Restore original forward
    GeoTexResnetWrapper.forward = _original_forward

    # Save overall summary
    with open(os.path.join(args.output_dir, 'all_scales_summary.json'), 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'='*60}", flush=True)
    print("Scale sweep complete. Run analyze_scale_sweep.py for comparison.", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == '__main__':
    main()
