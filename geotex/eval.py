"""GeoTex-Adapter evaluation with full region metrics and LPIPS.

Fair comparison: same seed, scheduler, init latents.
Region metrics: full / foreground / background / edge / non-edge-fg.
"""
import os
import sys
import json
import csv
import argparse
import warnings
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler, EulerAncestralDiscreteScheduler

from metrics import (compute_psnr, compute_ssim, compute_edge_mask,
                     unscale_latents, unscale_image)
from data_utils import prepare_batch, collate_batch


# ---------------------------------------------------------------------------
# LPIPS wrapper (loaded once, lazily)
# ---------------------------------------------------------------------------
_lpips_fn = None

def get_lpips(device):
    global _lpips_fn
    if _lpips_fn is None:
        import lpips
        _lpips_fn = lpips.LPIPS(net='alex').to(device).eval()
    return _lpips_fn

def compute_lpips(pred, target, mask=None, device=None):
    """LPIPS in [0,1] range. Lower is better."""
    if device is None:
        device = pred.device
    lpips_fn = get_lpips(device)
    # LPIPS expects [-1, 1]
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


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------
@torch.no_grad()
def generate_images(model, batch, device, weight_dtype, geo_feats=None,
                    num_steps=50, init_latents=None):
    """Generate with deterministic scheduler and shared init latents."""
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

    # NOTE: EulerDiscrete (not EulerAncestral) matches the training setup.
    # The model was trained with this scheduler configuration.
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


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Region metrics
# ---------------------------------------------------------------------------
def compute_region_metrics(pred, target, mask, edge_mask, region_name, device):
    """Compute PSNR, SSIM, LPIPS for a specific region."""
    fg = mask > 0.5
    bg = mask <= 0.5
    edge = edge_mask > 0.5
    non_edge_fg = fg & ~edge

    if region_name == 'full':
        region_mask = None
    elif region_name == 'foreground':
        region_mask = mask
    elif region_name == 'background':
        # Invert mask for background
        bg_mask = 1.0 - mask
        region_mask = bg_mask
    elif region_name == 'edge':
        region_mask = edge_mask
    elif region_name == 'non_edge_fg':
        nmask = (non_edge_fg.float())
        if nmask.sum() == 0:
            return {'psnr': 0.0, 'ssim': 0.0, 'lpips': 1.0, 'pixel_count': 0}
        region_mask = nmask
    else:
        raise ValueError(f"Unknown region: {region_name}")

    result = {
        'psnr': compute_psnr(pred, target, region_mask),
        'ssim': compute_ssim(pred, target, region_mask),
    }

    try:
        result['lpips'] = compute_lpips(pred, target, region_mask, device)
    except Exception as e:
        result['lpips'] = None

    if region_name == 'full':
        result['pixel_count'] = pred.numel() // pred.shape[1]
    else:
        result['pixel_count'] = int((region_mask > 0.5).sum().item()) if region_mask is not None else 0

    return result


def check_fg_metric_validity(full_psnr, fg_psnr):
    """Check if foreground metric is just copying full metric."""
    if abs(full_psnr - fg_psnr) < 0.01:
        return "WARNING: foreground metric may be invalid (identical to full)"
    return None


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------
def save_object_visualizations(gt, orig, adapter, mask, edge_mask, output_dir, obj_idx):
    """Save per-object visualization bundle."""
    vis_dir = os.path.join(output_dir, 'visualizations')
    os.makedirs(vis_dir, exist_ok=True)
    prefix = f"obj_{obj_idx:03d}"

    # GT / Original / Adapter
    save_image(gt, os.path.join(vis_dir, f'{prefix}_gt.png'))
    save_image(orig, os.path.join(vis_dir, f'{prefix}_original.png'))
    save_image(adapter, os.path.join(vis_dir, f'{prefix}_adapter.png'))

    # Error maps
    err_orig = (orig - gt).abs()
    err_adapter = (adapter - gt).abs()
    save_image(err_orig * 5, os.path.join(vis_dir, f'{prefix}_original_error.png'))
    save_image(err_adapter * 5, os.path.join(vis_dir, f'{prefix}_adapter_error.png'))

    # Masks
    mask_vis = mask.expand_as(gt)
    edge_vis = edge_mask.expand_as(gt)
    save_image(mask_vis, os.path.join(vis_dir, f'{prefix}_mask.png'))
    save_image(edge_vis, os.path.join(vis_dir, f'{prefix}_edge_mask.png'))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="GeoTex-Adapter Evaluation")
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--checkpoint', default=None, help='Adapter checkpoint')
    parser.add_argument('--num_objects', type=int, default=10)
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--save_vis', action='store_true', default=True)
    parser.add_argument('--vis_count', type=int, default=5, help='Number of objects to visualize')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16

    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex', 'eval')
    os.makedirs(args.output_dir, exist_ok=True)

    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Evaluating {num_objects} objects")

    # Check LPIPS availability
    lpips_available = True
    try:
        get_lpips(device)
    except Exception as e:
        warnings.warn(f"LPIPS not available: {e}. Install with: pip install lpips")
        lpips_available = False

    results = []
    warnings_list = []

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

        torch.manual_seed(args.seed)
        image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)
        torch.manual_seed(args.seed)
        image_orig = generate_images(model, batch, device, weight_dtype, None, args.steps, shared_latents)

        gt = target_imgs

        # Compute edge mask from depth/normal
        edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        # Resize edge mask to match image size
        if edge_mask.shape[2:] != gt.shape[2:]:
            edge_mask = F.interpolate(edge_mask, size=gt.shape[2:], mode='bilinear', align_corners=False)

        # Region ratios
        fg_mask = mask > 0.5
        total_pixels = fg_mask.numel()
        fg_ratio = fg_mask.sum().item() / total_pixels
        bg_ratio = 1.0 - fg_ratio
        edge_ratio = (edge_mask > 0.5).sum().item() / total_pixels
        non_edge_fg_ratio = (fg_mask & ~(edge_mask > 0.5)).sum().item() / total_pixels

        # Compute metrics for all regions
        obj_result = {
            'object_idx': obj_idx,
            'fg_ratio': fg_ratio,
            'bg_ratio': bg_ratio,
            'edge_ratio': edge_ratio,
            'non_edge_fg_ratio': non_edge_fg_ratio,
        }

        for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
            orig_m = compute_region_metrics(image_orig, gt, mask, edge_mask, region, device)
            adapter_m = compute_region_metrics(image_adapter, gt, mask, edge_mask, region, device)

            for metric_name in ['psnr', 'ssim', 'lpips']:
                obj_result[f'{region}_orig_{metric_name}'] = orig_m[metric_name]
                obj_result[f'{region}_adapter_{metric_name}'] = adapter_m[metric_name]

        # Check foreground validity
        fg_warning = check_fg_metric_validity(
            obj_result['full_orig_psnr'], obj_result['foreground_orig_psnr'])
        if fg_warning:
            warnings_list.append(f"Object {obj_idx}: {fg_warning}")

        results.append(obj_result)

        # Print summary
        fpsnr_d = obj_result['foreground_adapter_psnr'] - obj_result['foreground_orig_psnr']
        fssim_d = obj_result['foreground_adapter_ssim'] - obj_result['foreground_orig_ssim']
        epsnr_d = obj_result['edge_adapter_psnr'] - obj_result['edge_orig_psnr']
        essim_d = obj_result['edge_adapter_ssim'] - obj_result['edge_orig_ssim']
        print(f"  Object {obj_idx}: fg_PSNR {fpsnr_d:+.2f} fg_SSIM {fssim_d:+.4f} "
              f"edge_PSNR {epsnr_d:+.2f} edge_SSIM {essim_d:+.4f} fg_ratio={fg_ratio:.3f}")

        # Save visualizations
        if args.save_vis and obj_idx < args.vis_count:
            save_object_visualizations(gt, image_orig, image_adapter, mask, edge_mask,
                                       args.output_dir, obj_idx)

    # --- Write outputs ---

    # 1. per_object_metrics.csv
    fieldnames = list(results[0].keys())
    csv_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # 2. region_metrics.csv (flattened)
    region_csv_path = os.path.join(args.output_dir, 'region_metrics.csv')
    region_rows = []
    for r in results:
        row = {'object_idx': r['object_idx'], 'fg_ratio': r['fg_ratio']}
        for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
            for metric in ['psnr', 'ssim', 'lpips']:
                row[f'{region}_orig_{metric}'] = r[f'{region}_orig_{metric}']
                row[f'{region}_adapter_{metric}'] = r[f'{region}_adapter_{metric}']
                row[f'{region}_diff_{metric}'] = r[f'{region}_adapter_{metric}'] - r[f'{region}_orig_{metric}'] if r[f'{region}_adapter_{metric}'] is not None and r[f'{region}_orig_{metric}'] is not None else None
        region_rows.append(row)
    with open(region_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=region_rows[0].keys())
        writer.writeheader()
        writer.writerows(region_rows)

    # 3. summary_metrics.json
    summary = {
        'config': args.config,
        'checkpoint': args.checkpoint,
        'num_objects': num_objects,
        'lpips_available': lpips_available,
    }
    for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
        for metric in ['psnr', 'ssim', 'lpips']:
            key = f'{region}_{metric}'
            orig_vals = [r[f'{region}_orig_{metric}'] for r in results if r[f'{region}_orig_{metric}'] is not None]
            adapter_vals = [r[f'{region}_adapter_{metric}'] for r in results if r[f'{region}_adapter_{metric}'] is not None]
            if orig_vals and adapter_vals:
                summary[key] = {
                    'orig_mean': float(np.mean(orig_vals)),
                    'orig_std': float(np.std(orig_vals)),
                    'adapter_mean': float(np.mean(adapter_vals)),
                    'adapter_std': float(np.std(adapter_vals)),
                    'diff': float(np.mean(adapter_vals) - np.mean(orig_vals)),
                    'improved': sum(1 for o, a in zip(orig_vals, adapter_vals) if (a > o if metric != 'lpips' else a < o)),
                    'total': len(orig_vals),
                }

    # Region ratios
    summary['region_ratios'] = {
        'fg_ratio': float(np.mean([r['fg_ratio'] for r in results])),
        'bg_ratio': float(np.mean([r['bg_ratio'] for r in results])),
        'edge_ratio': float(np.mean([r['edge_ratio'] for r in results])),
        'non_edge_fg_ratio': float(np.mean([r['non_edge_fg_ratio'] for r in results])),
    }

    json_path = os.path.join(args.output_dir, 'summary_metrics.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    # 4. region_summary.json
    region_summary = {}
    for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
        region_summary[region] = {}
        for metric in ['psnr', 'ssim', 'lpips']:
            key = f'{region}_{metric}'
            if key in summary:
                region_summary[region][metric] = summary[key]
    region_summary['warnings'] = warnings_list
    region_summary['lpips_available'] = lpips_available

    region_json_path = os.path.join(args.output_dir, 'region_summary.json')
    with open(region_json_path, 'w') as f:
        json.dump(region_summary, f, indent=2, default=str)

    # Print summary
    print(f"\n{'='*70}")
    print(f"RESULTS ({num_objects} objects)")
    print(f"{'='*70}")
    for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
        print(f"\n  {region.upper()}:")
        for metric in ['psnr', 'ssim', 'lpips']:
            key = f'{region}_{metric}'
            if key in summary:
                s = summary[key]
                better = '↑' if metric != 'lpips' else '↓'
                print(f"    {metric.upper()}: {s['orig_mean']:.4f} → {s['adapter_mean']:.4f} "
                      f"({s['diff']:+.4f} {better}) [{s['improved']}/{s['total']}]")

    print(f"\n  Region ratios: fg={summary['region_ratios']['fg_ratio']:.3f} "
          f"bg={summary['region_ratios']['bg_ratio']:.3f} "
          f"edge={summary['region_ratios']['edge_ratio']:.3f}")

    if warnings_list:
        print(f"\n  WARNINGS:")
        for w in warnings_list:
            print(f"    ⚠ {w}")

    if not lpips_available:
        print(f"\n  ⚠ LPIPS NOT AVAILABLE — install with: pip install lpips")

    print(f"\nOutputs: {args.output_dir}")


if __name__ == '__main__':
    main()
