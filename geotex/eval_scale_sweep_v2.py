"""Optimized adapter scale sweep: generate baseline once, reuse for all scales.

Usage:
    python geotex/eval_scale_sweep_v2.py \
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
import torch
import torch.nn.functional as F
import numpy as np

signal.signal(signal.SIGTERM, signal.SIG_IGN)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image


def get_lpips_fn(device):
    try:
        import lpips
        return lpips.LPIPS(net='alex').to(device).eval()
    except:
        return None


def compute_lpips(pred, target, mask=None, lpips_fn=None, device=None):
    if lpips_fn is None:
        return None
    p, t = pred * 2 - 1, target * 2 - 1
    if mask is not None:
        m = mask[:, :1]
        if m.shape[2:] != p.shape[2:]:
            m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
        p, t = p * m, t * m
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
        for module in model.unet.modules():
            if hasattr(module, 'adapter'):
                module._adapter_scale = scale
    try:
        for t in scheduler.timesteps:
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
            del latent_input, noise_pred
    finally:
        if geo_feats is not None:
            model._clear_geo_feats_on_wrappers()
            for module in model.unet.modules():
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    del latents, prompt_embeds, cond_latents, added_cond_kwargs
    image = unscale_image(decoded)
    del decoded
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
    ph, pw = int((rmax - rmin).item() * padding), int((cmax - cmin).item() * padding)
    rmin, rmax = max(0, rmin - ph), min(H - 1, rmax + ph)
    cmin, cmax = max(0, cmin - pw), min(W - 1, cmax + pw)
    rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
    return image[:, :, rmin:rmax+1, cmin:cmax+1], mask[:, :, rmin:rmax+1, cmin:cmax+1]


def morph_mask(mask, kernel_size, op='erode'):
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    conv = F.conv2d(mask, kernel, padding=padding)
    if op == 'erode':
        return (conv >= kernel_size * kernel_size).float()
    return (conv > 0).float()


def compute_metrics(pred, target, mask, edge_mask, lpips_fn, device):
    r = {}
    r['full_psnr'] = compute_psnr(pred, target)
    r['full_ssim'] = compute_ssim(pred, target)
    r['full_lpips'] = compute_lpips(pred, target, lpips_fn=lpips_fn, device=device)

    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)
    r['fg_lpips'] = compute_lpips(pred, target, mask, lpips_fn=lpips_fn, device=device)

    bg_mask = 1.0 - mask
    r['bg_psnr'] = compute_psnr(pred, target, bg_mask)

    r['edge_psnr'] = compute_psnr(pred, target, edge_mask)
    r['edge_ssim'] = compute_ssim(pred, target, edge_mask)

    nef = mask * (1 - edge_mask)
    r['nef_ssim'] = compute_ssim(pred, target, nef)

    # BG-normalized
    pred_w = normalize_background(pred, mask, 1.0)
    target_w = normalize_background(target, mask, 1.0)
    r['bgwhite_psnr'] = compute_psnr(pred_w, target_w)
    r['bgwhite_ssim'] = compute_ssim(pred_w, target_w)
    r['bgwhite_lpips'] = compute_lpips(pred_w, target_w, lpips_fn=lpips_fn, device=device)

    # Crop
    pred_crop, _ = fg_bbox_crop(pred, mask, 0.1)
    target_crop, _ = fg_bbox_crop(target, mask, 0.1)
    r['crop_psnr'] = compute_psnr(pred_crop, target_crop)
    r['crop_ssim'] = compute_ssim(pred_crop, target_crop)
    r['crop_lpips'] = compute_lpips(pred_crop, target_crop, lpips_fn=lpips_fn, device=device)
    r['crop_area'] = float(pred_crop.numel() / pred.numel())

    # Mask sensitivity
    for s in [3, 5, 10]:
        m = morph_mask(mask, s * 2 + 1, 'erode')
        r[f'fg_psnr_e{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_e{s}'] = compute_ssim(pred, target, m)
    for s in [3, 5, 10]:
        m = morph_mask(mask, s * 2 + 1, 'dilate')
        r[f'fg_psnr_d{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_d{s}'] = compute_ssim(pred, target, m)

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

    # Patch wrapper for scale
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig_fwd = GeoTexResnetWrapper.forward
    def scaled_fwd(self, *a, **kw):
        hs = self.resnet(*a, **kw)
        if self._current_geo_feats is not None:
            gf = self._current_geo_feats.get(self.geo_feat_key)
            if gf is not None:
                if gf.shape[2:] != hs.shape[2:]:
                    gf = F.interpolate(gf, size=hs.shape[2:], mode='bilinear', align_corners=False)
                c = self.adapter.compute_correction(hs, gf)
                self._last_correction = c
                hs = hs + c * getattr(self, '_adapter_scale', 1.0)
        return hs
    GeoTexResnetWrapper.forward = scaled_fwd

    print(f"Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num = min(args.num_objects, len(dataset))
    lpips_fn = get_lpips_fn(device)

    from eval import collate_batch, prepare_batch

    # Save config
    with open(os.path.join(args.output_dir, 'config_snapshot.json'), 'w') as f:
        json.dump({'config': args.config, 'checkpoint': args.checkpoint,
                    'scales': args.scales, 'num_objects': num,
                    'steps': args.steps, 'seed': args.seed}, f, indent=2)

    # Phase 1: Generate baselines
    print(f"\n{'='*60}", flush=True)
    print(f"Phase 1: Generating baselines for {num} objects", flush=True)
    print(f"{'='*60}", flush=True)

    baselines = []  # list of (image_orig, gt, mask, edge_mask, geo_feats, batch, shared_latents)

    for obj_idx in range(num):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        torch.manual_seed(args.seed)
        image_orig = generate_with_scale(model, batch, device, weight_dtype, None, 0, args.steps, shared_latents)

        edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        if edge_mask.shape[2:] != target_imgs.shape[2:]:
            edge_mask = F.interpolate(edge_mask, size=target_imgs.shape[2:], mode='bilinear', align_corners=False)

        baselines.append({
            'image_orig': image_orig.cpu(),
            'gt': target_imgs.cpu(),
            'mask': mask.cpu(),
            'edge_mask': edge_mask.cpu(),
            'geo_feats': {k: v.cpu() for k, v in geo_feats.items()},
            'batch': {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in batch.items()},
            'shared_latents': shared_latents.cpu(),
        })

        # Free GPU memory
        del image_orig, target_imgs, mask, edge_mask, geo_feats, batch, shared_latents
        del cond_imgs, normal_imgs, real_depth_imgs, geo_input, geo_clean
        torch.cuda.empty_cache()

        if obj_idx % 10 == 0:
            print(f"  Baseline {obj_idx}/{num}", flush=True)

    print(f"Baselines done.", flush=True)

    # Phase 2: Generate adapter images at each scale
    all_scale_results = {}

    for scale in args.scales:
        scale_name = f'scale_{scale:.2f}'.replace('.', 'p')
        scale_dir = os.path.join(args.output_dir, scale_name)
        vis_dir = os.path.join(scale_dir, 'visualizations')
        os.makedirs(vis_dir, exist_ok=True)

        print(f"\n{'='*60}", flush=True)
        print(f"Scale = {scale}", flush=True)
        print(f"{'='*60}", flush=True)

        results = []

        for obj_idx in range(num):
            bl = baselines[obj_idx]
            # Move back to device
            batch = {k: v.to(device) if hasattr(v, 'to') else v for k, v in bl['batch'].items()}
            geo_feats = {k: v.to(device) for k, v in bl['geo_feats'].items()}
            shared_latents = bl['shared_latents'].to(device).to(dtype=weight_dtype)
            gt = bl['gt'].to(device)
            mask = bl['mask'].to(device)
            edge_mask = bl['edge_mask'].to(device)
            image_orig = bl['image_orig'].to(device)

            torch.manual_seed(args.seed)
            image_adapter = generate_with_scale(model, batch, device, weight_dtype, geo_feats,
                                                scale, args.steps, shared_latents)

            # Compute metrics
            adapter_m = compute_metrics(image_adapter, gt, mask, edge_mask, lpips_fn, device)
            orig_m = compute_metrics(image_orig, gt, mask, edge_mask, lpips_fn, device)

            r = {'object_idx': obj_idx, 'scale': scale,
                 'fg_ratio': float((mask > 0.5).sum().item() / mask.numel())}
            for k, v in adapter_m.items():
                r[f'adapter_{k}'] = v
            for k, v in orig_m.items():
                r[f'orig_{k}'] = v
            for k in adapter_m:
                if adapter_m[k] is not None and orig_m[k] is not None:
                    r[f'delta_{k}'] = adapter_m[k] - orig_m[k]

            results.append(r)

            # Free GPU memory
            del image_adapter, image_orig, gt, mask, edge_mask, batch, geo_feats, shared_latents
            del adapter_m, orig_m
            torch.cuda.empty_cache()

            if obj_idx % 10 == 0:
                d_cp = r.get('delta_crop_psnr', 0)
                d_cs = r.get('delta_crop_ssim', 0)
                d_es = r.get('delta_edge_ssim', 0)
                print(f"  Obj {obj_idx}: crop_psnr={d_cp:+.2f} crop_ssim={d_cs:+.4f} edge_ssim={d_es:+.4f}", flush=True)

            # Save vis for first 3
            if obj_idx < 3:
                save_image(gt, os.path.join(vis_dir, f'obj_{obj_idx:03d}_gt.png'))
                save_image(image_orig, os.path.join(vis_dir, f'obj_{obj_idx:03d}_orig.png'))
                save_image(image_adapter, os.path.join(vis_dir, f'obj_{obj_idx:03d}_adapter.png'))

        # Save CSV
        fieldnames = list(results[0].keys())
        with open(os.path.join(scale_dir, 'per_object_metrics.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        # Summary
        summary = {'scale': scale, 'num_objects': len(results)}
        for col in fieldnames:
            if col in ('object_idx', 'scale', 'fg_ratio'):
                continue
            vals = [r[col] for r in results if r.get(col) is not None]
            if vals:
                arr = np.array(vals)
                pos = int(np.sum(arr > 0)) if 'delta' in col else None
                summary[col] = {'mean': float(arr.mean()), 'std': float(arr.std()),
                                'positive': pos, 'total': len(arr)}

        with open(os.path.join(scale_dir, 'summary_metrics.json'), 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        all_scale_results[scale] = summary

        # Print key deltas
        print(f"\n  Scale {scale} Key Deltas:", flush=True)
        for m in ['delta_full_psnr', 'delta_crop_psnr', 'delta_crop_ssim', 'delta_crop_lpips',
                   'delta_fg_psnr', 'delta_fg_ssim', 'delta_edge_ssim', 'delta_bgwhite_psnr']:
            if m in summary:
                s = summary[m]
                print(f"    {m:25s}: {s['mean']:+.4f} [{s['positive']}/{s['total']}]", flush=True)

    # Save overall
    with open(os.path.join(args.output_dir, 'all_scales_summary.json'), 'w') as f:
        json.dump({str(k): v for k, v in all_scale_results.items()}, f, indent=2, default=str)

    GeoTexResnetWrapper.forward = _orig_fwd
    print(f"\nScale sweep complete.", flush=True)


if __name__ == '__main__':
    main()
