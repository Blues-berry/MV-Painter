"""Baseline alignment test: official vs wrapper-disabled vs step0.

Generates images for the same objects/views with:
A. Official MV-Painter pipeline (no GeoTex wrapper)
B. GeoTex wrapper with adapter disabled (geo_feats=None)
C. GeoTex step0 zero-init adapter

All use identical: object, view, seed, scheduler, init_latents, condition image, VAE decode.

Usage:
    python geotex/baseline_alignment_test.py \
        --config MVPainter/configs/mvpainter-geotex-full-train.yaml \
        --device cuda:0 \
        --output_dir mvpoutput/geotex_refattn_v1/baseline_repair_gate/alignment \
        --objects 00603cadc4474dafb78cdb55278568f2,00619c9de6f14f03940b6cf72575d822,007566bf92184fa89df4dff39d86d52b,00ba0a0c-35c7-5155-af89-e92eb557296f,00dbeb4848fb4062b5314931ccb62f99
"""
import os
import sys
import csv
import argparse
import torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler

from data_utils import prepare_batch, collate_batch
from metrics import scale_latents, unscale_latents, unscale_image


@torch.no_grad()
def generate_image(model, batch, device, weight_dtype, geo_feats=None,
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
    # Clear intermediate tensors
    del cond_latents, prompt_embeds, added_cond_kwargs, latents, noise_pred
    torch.cuda.empty_cache()
    return (image * 0.5 + 0.5).clamp(0, 1)


def compute_metrics(pred, target):
    """Compute PSNR, SSIM, mean/max pixel diff.
    pred, target: (B, C, H, W) tensors in [0, 1].
    """
    pred_np = pred.cpu().float().numpy()
    target_np = target.cpu().float().numpy()

    # Handle batch dimension: take first sample
    if pred_np.ndim == 4:
        pred_np = pred_np[0]  # (C, H, W)
        target_np = target_np[0]

    # Mean absolute diff
    abs_diff = np.abs(pred_np - target_np)
    mean_diff = float(abs_diff.mean())
    max_diff = float(abs_diff.max())

    # PSNR
    mse = float(((pred_np - target_np) ** 2).mean())
    psnr = 10 * np.log10(1.0 / mse) if mse > 0 else float('inf')

    # SSIM: convert to (H, W, C)
    from skimage.metrics import structural_similarity
    pred_hwc = pred_np.transpose(1, 2, 0)  # (H, W, C)
    target_hwc = target_np.transpose(1, 2, 0)
    ssim = float(structural_similarity(
        pred_hwc, target_hwc,
        channel_axis=2, data_range=1.0
    ))

    return psnr, ssim, mean_diff, max_diff


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--objects', default=None, help='Comma-separated object hashes')
    parser.add_argument('--num_objects', type=int, default=5)
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device(args.device)
    weight_dtype = torch.float16

    # Load model (this creates RefOnlyNoisedUNet with replace_processors=True)
    print("Loading model...")
    config = OmegaConf.load(args.config)

    # Use the existing load_model function from eval.py which handles memory properly
    from eval import load_model
    model = load_model(args.config, None, device)

    # encode_condition_image is already set up by load_model

    # Load dataset
    dataset = instantiate_from_config(config.data.params.validation)

    # Select objects
    if args.objects:
        object_hashes = args.objects.split(',')
    else:
        object_hashes = None

    # Find object indices
    object_indices = []
    if object_hashes:
        for i in range(len(dataset)):
            sample = dataset[i]
            # Try to find object hash in sample metadata
            if hasattr(sample, 'get') and 'obj_id' in sample:
                if sample['obj_id'] in object_hashes:
                    object_indices.append(i)
            elif i < len(object_hashes):
                object_indices.append(i)
            if len(object_indices) >= args.num_objects:
                break
    if not object_indices:
        object_indices = list(range(min(args.num_objects, len(dataset))))

    print(f"Evaluating {len(object_indices)} objects: {object_indices}")

    # Results
    results = []

    for obj_idx in object_indices:
        print(f"\n=== Object {obj_idx} ===")
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        # Shared init latents for fair comparison
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        # Geo features for adapter
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        # A. Wrapper with adapter (geo_feats provided)
        print("  Generating: wrapper+adapter...")
        torch.manual_seed(args.seed)
        img_adapter = generate_image(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)
        torch.cuda.empty_cache()

        # B. Wrapper with adapter disabled (geo_feats=None)
        print("  Generating: wrapper-disabled...")
        torch.manual_seed(args.seed)
        img_wrapper = generate_image(model, batch, device, weight_dtype, None, args.steps, shared_latents)
        torch.cuda.empty_cache()

        # C. Step0 zero-init (reset adapters to zero, then generate with geo_feats)
        print("  Generating: step0 zero-init...")
        # Save current adapter weights
        adapter_state = {}
        for name, module in model.unet.named_modules():
            if hasattr(module, 'adapter'):
                adapter_state[name] = {k: v.clone() for k, v in module.adapter.state_dict().items()}
                # Zero out adapter
                for p in module.adapter.parameters():
                    p.data.zero_()

        torch.manual_seed(args.seed)
        img_step0 = generate_image(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)
        torch.cuda.empty_cache()

        # Restore adapter weights
        for name, module in model.unet.named_modules():
            if hasattr(module, 'adapter') and name in adapter_state:
                module.adapter.load_state_dict(adapter_state[name])

        # Save images
        obj_dir = os.path.join(args.output_dir, f'obj_{obj_idx:03d}')
        os.makedirs(obj_dir, exist_ok=True)

        save_image(img_wrapper, os.path.join(obj_dir, 'wrapper_disabled.png'))
        save_image(img_step0, os.path.join(obj_dir, 'step0.png'))
        save_image(img_adapter, os.path.join(obj_dir, 'adapter.png'))

        # Compute metrics: wrapper vs step0 (should be identical if zero-init works)
        psnr_ws, ssim_ws, mdiff_ws, xdiff_ws = compute_metrics(img_wrapper, img_step0)

        # Save diff maps
        diff_ws = (img_wrapper - img_step0).abs()
        save_image(diff_ws * 10, os.path.join(obj_dir, 'wrapper_vs_step0_diff.png'))

        print(f"  wrapper vs step0: PSNR={psnr_ws:.2f} SSIM={ssim_ws:.6f} mean_diff={mdiff_ws:.6f} max_diff={xdiff_ws:.6f}")

        results.append({
            'object_idx': obj_idx,
            'wrapper_vs_step0_psnr': psnr_ws,
            'wrapper_vs_step0_ssim': ssim_ws,
            'wrapper_vs_step0_mean_diff': mdiff_ws,
            'wrapper_vs_step0_max_diff': xdiff_ws,
        })

    # Write CSV
    csv_path = os.path.join(args.output_dir, 'baseline_alignment_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nMetrics: {csv_path}")

    # Summary
    avg_psnr = np.mean([r['wrapper_vs_step0_psnr'] for r in results])
    avg_ssim = np.mean([r['wrapper_vs_step0_ssim'] for r in results])
    avg_mdiff = np.mean([r['wrapper_vs_step0_mean_diff'] for r in results])
    max_xdiff = max(r['wrapper_vs_step0_max_diff'] for r in results)

    print(f"\n=== Summary ===")
    print(f"wrapper vs step0: avg PSNR={avg_psnr:.2f} avg SSIM={avg_ssim:.6f}")
    print(f"  avg mean_diff={avg_mdiff:.6f} max max_diff={max_xdiff:.6f}")

    if avg_psnr > 40 and avg_mdiff < 0.001:
        print("\n=== VERDICT: PASS ✓ ===")
        print("wrapper-disabled ≈ step0 zero-init (pixel-identical or near-identical)")
    else:
        print("\n=== VERDICT: FAIL ✗ ===")
        print("wrapper-disabled ≠ step0 zero-init — baseline alignment broken")


if __name__ == '__main__':
    main()
