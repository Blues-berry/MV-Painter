"""300-object evaluation for FAC controllers trained on v2 base weights.

Matches the eval_300_* protocol (50 Euler steps, seed 42, shared init latents,
normalize_bg=True) so tab:fac rows are directly comparable to tab:300obj.
During generation the FAC controller provides the temporal (LTAG) and spatial
(LTAG+GSG) / frequency (Full FAC) modulation; the static TCAS _adapter_scale
is intentionally NOT set (LTAG replaces it).

Usage:
    python geotex/eval_fac_v2.py \
        --config MVPainter/configs/mvpainter-geotex-fac-train.yaml \
        --checkpoint mvpoutput/fac_v2/ltag/checkpoints/fac_v2_ltag_step_000500.pt \
        --output_dir mvpoutput/fac_v2/ltag/eval_300 \
        --num_objects 300 --num_steps 50
"""
import os
import sys
import json
import csv
import argparse
import gc
import time
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import unscale_latents, unscale_image
from data_utils import prepare_batch, collate_batch
from eval_unified_300 import compute_all_metrics


def set_config_from_variant(config, variant):
    """Enable FAC modules according to the checkpoint's variant string."""
    config.model.params.enable_ltag = 'ltag' in variant
    config.model.params.enable_gsg = 'gsg' in variant
    config.model.params.enable_fsc = 'fsc' in variant


def load_model(config_path, checkpoint_path, device):
    config = OmegaConf.load(config_path)
    st = torch.load(checkpoint_path, map_location='cpu')
    variant = st.get('variant', 'ltag+gsg+fsc')
    set_config_from_variant(config, variant)
    print(f"FAC variant: {variant}")

    model = instantiate_from_config(config.model)

    # Load base + FAC controller weights
    model.adapters.load_state_dict(st['adapters'])
    model.geo_encoder.load_state_dict(st['geo_encoder'])
    if 'fac_controller' in st and model.correction_controller is not None:
        model.correction_controller.load_state_dict(st['fac_controller'])
        print(f"  Loaded FAC controller weights")

    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae.to(device).to(dtype=torch.float16)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    if model.correction_controller is not None:
        model.correction_controller.to(device).to(dtype=torch.float32)
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
def generate_with_fac(model, batch, device, weight_dtype, geo_feats,
                      num_steps, init_latents):
    """Generate with FAC controller (LTAG provides temporal scale)."""
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

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            # FAC: set LTAG timestep; do NOT set _adapter_scale
            if model.correction_controller is not None:
                model.correction_controller.set_timestep(t)
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        model._clear_geo_feats_on_wrappers()

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


def run_eval(args):
    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'samples'), exist_ok=True)

    model = load_model(args.config, args.checkpoint, device)

    test_dataset_cfg = OmegaConf.load(args.config).data.params.validation
    from src.data.mvpainter_dataset import MVPainterData
    dataset = MVPainterData(**test_dataset_cfg.params)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Test dataset: {len(dataset)} objects, evaluating {num_objects}")

    results = []
    print(f"\nRunning FAC 300-object evaluation (steps={args.num_steps}, seed=42)")
    print("=" * 80)
    start_time = time.time()

    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        obj_name = f'obj_{obj_idx:04d}'

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        pred = generate_with_fac(model, batch, device, weight_dtype, geo_feats,
                                 args.num_steps, init_latents)

        m = compute_all_metrics(pred, target_imgs, mask, None, normalize_bg=True)
        m['object'] = obj_name
        m['obj_idx'] = obj_idx
        results.append(m)

        if obj_idx < 20:
            save_image(pred, os.path.join(args.output_dir, 'samples', f'{obj_name}.png'))
            save_image(target_imgs, os.path.join(args.output_dir, 'samples', f'{obj_name}_gt.png'))

        if (obj_idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (obj_idx + 1) / elapsed
            eta = (num_objects - obj_idx - 1) / max(speed, 1e-6)
            print(f"[{obj_idx+1}/{num_objects}] FG-SSIM={m['fg_ssim']:.4f} PSNR={m['full_psnr']:.2f} "
                  f"| {speed:.2f} obj/s | ETA: {eta:.0f}s")

        if (obj_idx + 1) % 50 == 0:
            torch.cuda.empty_cache()
            gc.collect()

    elapsed_total = time.time() - start_time
    print(f"\nEvaluation complete: {elapsed_total:.0f}s ({num_objects/elapsed_total:.2f} obj/s)")

    metric_keys = ['full_psnr', 'full_ssim', 'fg_psnr', 'fg_ssim',
                   'edge_ssim', 'fg_lpips', 'rgb_std_ratio', 'grad_ratio',
                   'lap_var_ratio', 'fg_lap_var', 'gt_fg_lap_var',
                   'fg_rgb_std', 'gt_fg_rgb_std', 'fg_grad_mag', 'gt_fg_grad_mag']

    summary = {}
    for mk in metric_keys:
        vals = [r[mk] for r in results if r.get(mk) is not None]
        if vals:
            summary[mk] = {
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals)),
                'median': float(np.median(vals)),
                'min': float(np.min(vals)),
                'max': float(np.max(vals)),
                'count': int(len(vals)),
            }

    print("\n" + "=" * 100)
    print("FAC 300-OBJECT EVALUATION SUMMARY")
    print("=" * 100)
    for mk in ['full_psnr', 'full_ssim', 'fg_psnr', 'fg_ssim', 'edge_ssim']:
        if mk in summary:
            s = summary[mk]
            print(f"{mk:>12s}: mean={s['mean']:.4f} std={s['std']:.4f}")

    out = {
        'checkpoint': args.checkpoint,
        'num_objects': num_objects,
        'num_steps': args.num_steps,
        'normalize_bg': True,
        'variant': getattr(model, 'correction_controller', None) is not None,
        'metrics': summary,
    }
    with open(os.path.join(args.output_dir, 'summary.json'), 'w') as f:
        json.dump(out, f, indent=2)

    with open(os.path.join(args.output_dir, 'per_object_metrics.csv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['object', 'obj_idx'] + metric_keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, '') for k in ['object', 'obj_idx'] + metric_keys})
    print(f"Saved: {os.path.join(args.output_dir, 'summary.json')}")
    print(f"Saved: {os.path.join(args.output_dir, 'per_object_metrics.csv')}")


def main():
    parser = argparse.ArgumentParser(description="FAC 300-object evaluation")
    parser.add_argument('--config', type=str,
                        default='MVPainter/configs/mvpainter-geotex-fac-train.yaml')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()
    run_eval(args)


if __name__ == '__main__':
    main()
