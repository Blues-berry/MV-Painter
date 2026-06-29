"""FAC (Full Adaptive Correction) ablation evaluation.

Compares TCAS baseline vs progressive FAC combinations:
  1. TCAS (hand-crafted 3-phase schedule) — baseline
  2. LTAG (Learned Timestep-Adaptive Gating) — replaces TCAS
  3. LTAG + GSG (+ Geometry Spatial Gating)
  4. LTAG + GSG + FSC (Full FAC)

Each variant is evaluated on the same set of objects with fixed seeds.
Outputs a paper-ready ablation table.

Usage:
    python geotex/eval_fac_ablation.py \
        --config configs/geotex_train.yaml \
        --checkpoint /path/to/geotex_checkpoint.pt \
        --fac_checkpoint /path/to/fac_checkpoint.pt
        --num_objects 24 \
        --output_dir mvpoutput/fac_ablation
"""

import os
import sys
import json
import argparse
import csv
from collections import defaultdict

import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image
from metrics_extended import compute_all_extended
from mvpainter.adaptive_correction import AdaptiveCorrectionController
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


# ============================================================
# Model Loading
# ============================================================

def load_model(config_path, checkpoint_path, device):
    """Load base GeoTex model (without FAC)."""
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


def get_num_adapters(model):
    """Count number of adapter wrappers in UNet."""
    count = 0
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            count += 1
    return count


# ============================================================
# FAC Controller Management
# ============================================================

def attach_controller(model, controller, device):
    """Attach a FAC controller to all wrappers."""
    controller = controller.to(device)
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._correction_controller = controller


def detach_controller(model):
    """Remove FAC controller from all wrappers."""
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._correction_controller = None


# ============================================================
# TCAS baseline (hand-crafted schedule)
# ============================================================

def get_tcas_scale(step_idx, total_steps, schedule):
    """TCAS: 3-phase hand-crafted schedule."""
    frac = step_idx / max(total_steps - 1, 1)
    if frac < 0.33:
        return schedule.get('early', 1.25)
    elif frac < 0.66:
        return schedule.get('mid', 2.50)
    else:
        return schedule.get('late', 1.25)


def setup_static_scale(model, scale):
    """Set uniform scale on all adapters."""
    for module in model.unet.modules():
        if hasattr(module, 'adapter') and isinstance(module, GeoTexResnetWrapper):
            module._adapter_scale = scale


def clear_scales(model):
    """Clear all adapter scales."""
    for module in model.unet.modules():
        if hasattr(module, '_adapter_scale'):
            delattr(module, '_adapter_scale')


# ============================================================
# Generation
# ============================================================

@torch.no_grad()
def generate_with_variant(model, batch, device, weight_dtype, geo_feats,
                          num_steps, init_latents, variant, controller=None,
                          tcas_schedule=None):
    """Generate with a specific ablation variant.

    Args:
        variant: one of 'tcas', 'ltag', 'ltag_gsg', 'full_fac'
        controller: AdaptiveCorrectionController (for LTAG/GSG/FSC variants)
        tcas_schedule: dict for TCAS baseline
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
    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    latents = init_latents * scheduler.init_noise_sigma

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    # Variant-specific setup
    if variant == 'tcas':
        # Hand-crafted schedule, no controller
        detach_controller(model)
    else:
        # Attach FAC controller
        attach_controller(model, controller, device)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            # Always apply TCAS scale (base temporal schedule)
            scale = get_tcas_scale(step_idx, num_steps, tcas_schedule or {})
            setup_static_scale(model, scale)

            if variant != 'tcas' and controller is not None:
                # FAC: additionally set timestep for LTAG (if enabled)
                controller.set_timestep(t)

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        model._clear_geo_feats_on_wrappers()
        clear_scales(model)
        detach_controller(model)

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


# ============================================================
# Metrics
# ============================================================

def compute_metrics(pred, target, mask=None):
    """Compute comprehensive metrics for a single prediction."""
    results = {}
    # Basic metrics
    results['psnr'] = compute_psnr(pred, target)
    results['ssim'] = compute_ssim(pred, target)

    # Foreground metrics
    if mask is not None:
        results['fg_psnr'] = compute_psnr(pred, target, mask)
        results['fg_ssim'] = compute_ssim(pred, target, mask)

    # Extended metrics (texture preservation)
    try:
        ext = compute_all_extended(pred, target, mask)
        results.update(ext)
    except Exception:
        pass

    return results


# ============================================================
# Main Ablation Loop
# ============================================================

VARIANTS = {
    'tcas': 'TCAS (baseline)',
    'ltag': 'LTAG only',
    'ltag_gsg': 'LTAG + GSG',
    'full_fac': 'LTAG + GSG + FSC (Full FAC)',
}


def run_ablation(args):
    device = torch.device(getattr(args, 'device', 'cuda:0'))
    weight_dtype = torch.float16
    num_steps = args.num_steps
    tcas_schedule = {'early': 1.25, 'mid': 2.50, 'late': 1.25}

    # Load model
    print("Loading model...")
    model = load_model(args.config, args.checkpoint, device)
    num_adapters = get_num_adapters(model)
    print(f"Model loaded with {num_adapters} adapters")

    # Create controllers for each variant
    controllers = {}

    # LTAG only
    controllers['ltag'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=False, enable_fsc=False,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )

    # LTAG + GSG
    controllers['ltag_gsg'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=True, enable_fsc=False,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )

    # Full FAC
    controllers['full_fac'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=True, enable_fsc=True,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )

    # Load trained FAC weights if available
    if args.fac_checkpoint and os.path.exists(args.fac_checkpoint):
        print(f"Loading FAC weights from {args.fac_checkpoint}")
        fac_state = torch.load(args.fac_checkpoint, map_location='cpu')
        # FAC weights are stored under 'fac_controller' key in geotex checkpoint
        if 'fac_controller' in fac_state:
            fac_ctrl_state = fac_state['fac_controller']
        else:
            fac_ctrl_state = fac_state  # Assume raw controller state dict
        for key, ctrl in controllers.items():
            try:
                ctrl.load_state_dict(fac_ctrl_state, strict=False)
                print(f"  Loaded FAC weights for {key}")
            except Exception as e:
                print(f"  Could not load FAC weights for {key}: {e}")

    # Load dataset
    print("Loading dataset...")
    config = OmegaConf.load(args.config)
    dataset_config = config.data.params.train
    dataset = instantiate_from_config(dataset_config)
    print(f"Dataset: {len(dataset)} objects")

    # Select objects
    num_objects = min(args.num_objects, len(dataset))
    indices = list(range(0, len(dataset), max(1, len(dataset) // num_objects)))[:num_objects]

    # Output setup
    os.makedirs(args.output_dir, exist_ok=True)
    results_all = defaultdict(list)

    print(f"\nRunning ablation: {num_objects} objects × {len(VARIANTS)} variants")
    print("=" * 70)

    for obj_idx, data_idx in enumerate(indices):
        batch = dataset[data_idx]
        batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        obj_name = batch.get('obj_name', [f'obj_{data_idx}'])[0] if 'obj_name' in batch else f'obj_{data_idx}'
        print(f"\n[{obj_idx+1}/{num_objects}] {obj_name}")

        # Prepare geometry features
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)
        # geo_encoder is float32, so feed it float32 input
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        # Fixed seed for fair comparison
        seed = 42 + data_idx
        torch.manual_seed(seed)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for variant_key, variant_name in VARIANTS.items():
            controller = controllers.get(variant_key)

            pred = generate_with_variant(
                model, batch, device, weight_dtype, geo_feats,
                num_steps, init_latents, variant_key,
                controller=controller, tcas_schedule=tcas_schedule,
            )

            # Compute metrics
            metrics = compute_metrics(pred, target_imgs, mask)
            metrics['variant'] = variant_key
            metrics['object'] = obj_name
            results_all[variant_key].append(metrics)

            # Print inline
            psnr_str = f"PSNR={metrics.get('psnr', 0):.2f}"
            ssim_str = f"SSIM={metrics.get('ssim', 0):.4f}"
            print(f"  {variant_name:30s}: {psnr_str}, {ssim_str}")

            # Save sample images (first 4 objects only)
            if obj_idx < 4:
                variant_dir = os.path.join(args.output_dir, 'samples', variant_key)
                os.makedirs(variant_dir, exist_ok=True)
                save_image(pred, os.path.join(variant_dir, f'{obj_name}.png'))

    # ============================================================
    # Summary Table
    # ============================================================
    print("\n" + "=" * 70)
    print("ABLATION SUMMARY")
    print("=" * 70)

    summary_rows = []
    header = ['Variant', 'PSNR↑', 'SSIM↑', 'FG_PSNR↑', 'FG_SSIM↑']
    print(f"{'Variant':30s} {'PSNR↑':>8s} {'SSIM↑':>8s} {'FG_PSNR↑':>10s} {'FG_SSIM↑':>10s}")
    print("-" * 70)

    for variant_key, variant_name in VARIANTS.items():
        metrics_list = results_all[variant_key]
        if not metrics_list:
            continue
        avg = {}
        for key in ['psnr', 'ssim', 'fg_psnr', 'fg_ssim']:
            vals = [m[key] for m in metrics_list if key in m and m[key] is not None]
            avg[key] = np.mean(vals) if vals else 0.0

        row = {
            'variant': variant_name,
            'psnr': avg['psnr'],
            'ssim': avg['ssim'],
            'fg_psnr': avg['fg_psnr'],
            'fg_ssim': avg['fg_ssim'],
        }
        summary_rows.append(row)
        print(f"{variant_name:30s} {avg['psnr']:8.2f} {avg['ssim']:8.4f} {avg['fg_psnr']:10.2f} {avg['fg_ssim']:10.4f}")

    # Save results
    results_path = os.path.join(args.output_dir, 'fac_ablation_results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'config': vars(args),
            'per_object': {k: v for k, v in results_all.items()},
            'summary': summary_rows,
        }, f, indent=2, default=str)
    print(f"\nResults saved to {results_path}")

    # CSV for easy import to LaTeX
    csv_path = os.path.join(args.output_dir, 'fac_ablation_table.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['variant', 'psnr', 'ssim', 'fg_psnr', 'fg_ssim'])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"CSV table saved to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description='FAC Ablation Study')
    parser.add_argument('--config', type=str, required=True, help='Training config YAML')
    parser.add_argument('--checkpoint', type=str, required=True, help='GeoTex adapter checkpoint')
    parser.add_argument('--fac_checkpoint', type=str, default=None, help='Trained FAC controller checkpoint (geotex .pt with fac_controller key)')
    parser.add_argument('--num_objects', type=int, default=24, help='Number of test objects')
    parser.add_argument('--num_steps', type=int, default=50, help='Denoising steps')
    parser.add_argument('--output_dir', type=str, default='mvpoutput/fac_ablation', help='Output directory')
    parser.add_argument('--device', type=str, default='cuda:0', help='Device')
    args = parser.parse_args()
    run_ablation(args)


if __name__ == '__main__':
    main()
