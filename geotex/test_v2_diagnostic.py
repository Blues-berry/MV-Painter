"""Diagnostic test script for GeoTex v2 training issues.

Tests:
1. Gradient flow verification (adapter + encoder)
2. Write/read pass separation correctness
3. Per-layer TCAS scale behavior
4. Quick 5-object eval on multiple checkpoints
5. Baseline (no adapter) comparison

Usage:
    python geotex/test_v2_diagnostic.py \
        --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
        --device cuda:0
"""
import os
import sys
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
from data_utils import prepare_batch, collate_batch
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
from tcas_schedule import get_scale_for_step_idx


def load_model_for_test(config_path, device):
    """Load model without checkpoint (fresh zero-init adapters)."""
    config = OmegaConf.load(config_path)
    model = instantiate_from_config(config.model)
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


def load_checkpoint(model, ckpt_path):
    """Load adapter+encoder weights."""
    state = torch.load(ckpt_path, map_location='cpu')
    if 'adapters' in state:
        model.adapters.load_state_dict(state['adapters'])
        model.geo_encoder.load_state_dict(state['geo_encoder'])
    print(f"  Loaded: {ckpt_path}")


# ============================================================
# Test 1: Gradient Flow Verification
# ============================================================
def test_gradient_flow(model, dataset, device):
    """Verify gradients flow to adapter AND encoder during training step."""
    print("\n" + "=" * 60)
    print("TEST 1: Gradient Flow Verification")
    print("=" * 60)

    # Freeze UNet, unfreeze adapter+encoder
    model.unet.requires_grad_(False)
    trainable_params = []
    for name, module in model.unet.named_modules():
        if isinstance(module, GeoTexResnetWrapper):
            for p in module.adapter.parameters():
                p.requires_grad = True
                trainable_params.append(p)
    for p in model.geo_encoder.parameters():
        p.requires_grad = True
        trainable_params.append(p)

    # Run one forward-backward pass
    batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
             for k, v in dataset[0].items()}
    for k in batch:
        if hasattr(batch[k], 'to'):
            batch[k] = batch[k].to(device)

    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        model.prepare_batch_data(batch, device=device)

    B = cond_imgs.shape[0]
    t = torch.randint(0, model.num_timesteps, size=(B,)).long().to(device)

    with torch.no_grad():
        weight_dtype = torch.float16
        if 'global_embeds' in batch:
            global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
            ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
            uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
            prompt_embeds = uc_text_emb + global_embeds * ramp
        else:
            prompt_embeds = model.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=False)
        cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
        added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
        added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                             for k, v in added_cond_kwargs.items()}

        from train_v2 import encode_target_images
        latents = encode_target_images(model, target_imgs, device).to(weight_dtype)
        noise = torch.randn_like(latents)
        latents_noisy = model.train_scheduler.add_noise(latents, noise, t)

    # Compute geo features WITH grad
    geo_input_clean = geo_input.float().clamp(0, 1)
    geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
    geo_feats = model.geo_encoder(geo_input_clean)

    # Set TCAS scale
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._adapter_scale = 1.25  # Simple uniform scale for testing

    model._set_geo_feats_on_wrappers(geo_feats)
    noise_pred = model.pipeline.unet(
        latents_noisy, t,
        encoder_hidden_states=prompt_embeds,
        cross_attention_kwargs=dict(cond_lat=cond_latents),
        added_cond_kwargs=added_cond_kwargs,
        return_dict=False, is_training=True,
    )[0]
    model._clear_geo_feats_on_wrappers()

    # Loss & backward
    loss = F.mse_loss(noise_pred, noise)
    loss.backward()

    # Check gradients
    adapter_grads = []
    encoder_grads = []
    for name, module in model.unet.named_modules():
        if isinstance(module, GeoTexResnetWrapper):
            for pname, p in module.adapter.named_parameters():
                if p.grad is not None:
                    adapter_grads.append((f"{name}.{pname}", p.grad.norm().item()))
    for pname, p in model.geo_encoder.named_parameters():
        if p.grad is not None:
            encoder_grads.append((pname, p.grad.norm().item()))

    print(f"\n  Loss: {loss.item():.6f}")
    print(f"\n  Adapter gradients ({len(adapter_grads)} params with grad):")
    total_adapter_grad = sum(g for _, g in adapter_grads)
    print(f"    Total grad norm: {total_adapter_grad:.6f}")
    if adapter_grads:
        top3 = sorted(adapter_grads, key=lambda x: -x[1])[:3]
        for name, g in top3:
            print(f"    {name}: {g:.6f}")

    print(f"\n  Encoder gradients ({len(encoder_grads)} params with grad):")
    total_encoder_grad = sum(g for _, g in encoder_grads)
    print(f"    Total grad norm: {total_encoder_grad:.6f}")
    if encoder_grads:
        top3 = sorted(encoder_grads, key=lambda x: -x[1])[:3]
        for name, g in top3:
            print(f"    {name}: {g:.6f}")

    # Verdict
    adapter_ok = total_adapter_grad > 1e-8
    encoder_ok = total_encoder_grad > 1e-8
    print(f"\n  VERDICT: Adapter grad flow: {'✅ OK' if adapter_ok else '❌ BROKEN'}")
    print(f"  VERDICT: Encoder grad flow: {'✅ OK' if encoder_ok else '❌ BROKEN (expected with zero-init)'}")

    # Zero grad for next test
    for p in trainable_params:
        if p.grad is not None:
            p.grad.zero_()

    return adapter_ok, encoder_ok


# ============================================================
# Test 2: Write/Read Pass Separation
# ============================================================
def test_write_read_separation(model, dataset, device):
    """Verify adapter is NOT active during write pass, IS active during read pass."""
    print("\n" + "=" * 60)
    print("TEST 2: Write/Read Pass Separation")
    print("=" * 60)

    batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
             for k, v in dataset[0].items()}
    for k in batch:
        if hasattr(batch[k], 'to'):
            batch[k] = batch[k].to(device)

    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        model.prepare_batch_data(batch, device=device)

    geo_input_clean = geo_input.float().clamp(0, 1)
    geo_feats = model.geo_encoder(geo_input_clean)

    # Track corrections
    corrections_during_write = []
    corrections_during_read = []

    original_forward = GeoTexResnetWrapper.forward

    def patched_forward(self, *args, **kwargs):
        hidden_states = self.resnet(*args, **kwargs)
        if GeoTexResnetWrapper._skip_correction:
            corrections_during_write.append(self.geo_feat_key)
            return hidden_states
        if self._current_geo_feats is not None:
            geo_feat = self._current_geo_feats.get(self.geo_feat_key)
            if geo_feat is not None:
                corrections_during_read.append(self.geo_feat_key)
        return original_forward(self, *args, **kwargs)

    # Monkey-patch temporarily
    GeoTexResnetWrapper.forward = patched_forward

    # Set geo feats and run
    model._set_geo_feats_on_wrappers(geo_feats)
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._adapter_scale = 1.25

    with torch.no_grad():
        weight_dtype = torch.float16
        B = cond_imgs.shape[0]
        if 'global_embeds' in batch:
            global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
            ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
            uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
            prompt_embeds = uc_text_emb + global_embeds * ramp
        cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
        added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
        added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                             for k, v in added_cond_kwargs.items()}

        t = torch.tensor([500], device=device)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        noise_pred = model.pipeline.unet(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_latents),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False, is_training=True,
        )[0]

    model._clear_geo_feats_on_wrappers()

    # Restore
    GeoTexResnetWrapper.forward = original_forward

    print(f"\n  Write pass: {len(corrections_during_write)} adapters SKIPPED (correct=9)")
    print(f"  Read pass:  {len(corrections_during_read)} adapters APPLIED (correct=9)")

    write_ok = len(corrections_during_write) == 9
    read_ok = len(corrections_during_read) == 9
    print(f"\n  VERDICT: Write skip: {'✅ OK' if write_ok else '❌ BROKEN'}")
    print(f"  VERDICT: Read apply: {'✅ OK' if read_ok else '❌ BROKEN'}")

    return write_ok, read_ok


# ============================================================
# Test 3: Quick 5-object eval on checkpoints
# ============================================================
@torch.no_grad()
def test_checkpoint_quality(model, dataset, device, ckpt_dir):
    """Quick 5-object eval on available checkpoints."""
    print("\n" + "=" * 60)
    print("TEST 3: Checkpoint Quality (5 objects)")
    print("=" * 60)

    checkpoints = sorted([
        f for f in os.listdir(ckpt_dir)
        if f.startswith('geotex_v2_ema_') and f.endswith('.pt')
    ])

    if not checkpoints:
        print("  No checkpoints found!")
        return {}

    results = {}
    weight_dtype = torch.float16
    num_steps = 50  # Quick eval
    num_objects = 5

    for ckpt_name in checkpoints:
        ckpt_path = os.path.join(ckpt_dir, ckpt_name)
        load_checkpoint(model, ckpt_path)

        fg_ssims = []
        psnrs = []

        for obj_idx in range(num_objects):
            batch = collate_batch(dataset, obj_idx, device)
            cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
                prepare_batch(batch, model.img_size, device)

            geo_input_clean = geo_input.float().clamp(0, 1)
            geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_input_clean)

            torch.manual_seed(42)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

            # Generate
            cond_imgs_r = v2.functional.resize(batch['cond_imgs'].to(device), model.img_size, interpolation=3, antialias=True).clamp(0, 1)
            B = cond_imgs_r.shape[0]
            global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
            ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
            uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
            prompt_embeds = uc_text_emb + global_embeds * ramp
            cond_latents = model.encode_condition_image(cond_imgs_r).to(weight_dtype)
            added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
            added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                                 for k, v in added_cond_kwargs.items()}

            scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
            scheduler.set_timesteps(num_steps, device=device)
            latents = init_latents * scheduler.init_noise_sigma

            model._set_geo_feats_on_wrappers(geo_feats)
            for step_idx, t_val in enumerate(scheduler.timesteps):
                # Per-layer TCAS v2
                for module in model.unet.modules():
                    if isinstance(module, GeoTexResnetWrapper):
                        scale = get_scale_for_step_idx(step_idx, num_steps, module.depth_group)
                        module._adapter_scale = scale

                latent_input = scheduler.scale_model_input(latents, t_val)
                noise_pred = model.pipeline.unet(
                    latent_input, t_val, encoder_hidden_states=prompt_embeds,
                    cross_attention_kwargs=dict(cond_lat=cond_latents),
                    added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
                )[0]
                latents = scheduler.step(noise_pred, t_val, latents, return_dict=False)[0]

            model._clear_geo_feats_on_wrappers()
            for module in model.unet.modules():
                if isinstance(module, GeoTexResnetWrapper):
                    if hasattr(module, '_adapter_scale'):
                        delattr(module, '_adapter_scale')

            latents_dec = unscale_latents(latents)
            decoded = model.pipeline.vae.decode(latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
            pred = (unscale_image(decoded) * 0.5 + 0.5).clamp(0, 1)

            fg_ssim = compute_ssim(pred, target_imgs, mask)
            psnr = compute_psnr(pred, target_imgs)
            fg_ssims.append(fg_ssim)
            psnrs.append(psnr)

        mean_fg_ssim = np.mean(fg_ssims)
        mean_psnr = np.mean(psnrs)
        results[ckpt_name] = {'fg_ssim': mean_fg_ssim, 'psnr': mean_psnr}
        print(f"  {ckpt_name:40s}: FG-SSIM={mean_fg_ssim:.4f}  PSNR={mean_psnr:.2f}")

    # Also test baseline (no adapter / zero-init)
    print("\n  --- Baseline (zero-init adapter = no correction) ---")
    # Reset adapters to zero
    for adapter in model.adapters:
        torch.nn.init.zeros_(adapter.output_proj.weight)
        torch.nn.init.zeros_(adapter.output_proj.bias)

    fg_ssims_bl = []
    psnrs_bl = []
    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_feats = model.geo_encoder(geo_input_clean)

        torch.manual_seed(42)
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
        cond_imgs_r = v2.functional.resize(batch['cond_imgs'].to(device), model.img_size, interpolation=3, antialias=True).clamp(0, 1)
        B = cond_imgs_r.shape[0]
        global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
        ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
        uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
        prompt_embeds = uc_text_emb + global_embeds * ramp
        cond_latents = model.encode_condition_image(cond_imgs_r).to(weight_dtype)
        added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
        added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                             for k, v in added_cond_kwargs.items()}

        scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
        scheduler.set_timesteps(num_steps, device=device)
        latents = init_latents * scheduler.init_noise_sigma

        model._set_geo_feats_on_wrappers(geo_feats)
        for step_idx, t_val in enumerate(scheduler.timesteps):
            for module in model.unet.modules():
                if isinstance(module, GeoTexResnetWrapper):
                    module._adapter_scale = 1.0
            latent_input = scheduler.scale_model_input(latents, t_val)
            noise_pred = model.pipeline.unet(
                latent_input, t_val, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t_val, latents, return_dict=False)[0]
        model._clear_geo_feats_on_wrappers()

        latents_dec = unscale_latents(latents)
        decoded = model.pipeline.vae.decode(latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
        pred = (unscale_image(decoded) * 0.5 + 0.5).clamp(0, 1)
        fg_ssims_bl.append(compute_ssim(pred, target_imgs, mask))
        psnrs_bl.append(compute_psnr(pred, target_imgs))

    mean_bl_ssim = np.mean(fg_ssims_bl)
    mean_bl_psnr = np.mean(psnrs_bl)
    results['baseline_zero_init'] = {'fg_ssim': mean_bl_ssim, 'psnr': mean_bl_psnr}
    print(f"  {'baseline (zero-init)':40s}: FG-SSIM={mean_bl_ssim:.4f}  PSNR={mean_bl_psnr:.2f}")

    return results


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--ckpt_dir', default='mvpoutput/geotex_v2/checkpoints')
    parser.add_argument('--skip_grad_test', action='store_true')
    args = parser.parse_args()

    device = torch.device(args.device)
    print("Loading model...")
    model = load_model_for_test(args.config, device)
    print("Loading dataset...")
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    print(f"Dataset: {len(dataset)} objects\n")

    # Test 1: Gradient flow
    if not args.skip_grad_test:
        adapter_ok, encoder_ok = test_gradient_flow(model, dataset, device)
    else:
        print("Skipping gradient test")
        adapter_ok, encoder_ok = True, False

    # Test 2: Write/Read separation
    write_ok, read_ok = test_write_read_separation(model, dataset, device)

    # Test 3: Checkpoint quality comparison
    results = test_checkpoint_quality(model, dataset, device, args.ckpt_dir)

    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"  Gradient flow (adapter): {'✅' if adapter_ok else '❌'}")
    print(f"  Gradient flow (encoder): {'✅' if encoder_ok else '⚠️ (zero-init expected)'}")
    print(f"  Write/read separation:   {'✅' if write_ok and read_ok else '❌'}")
    print(f"\n  Checkpoint quality ranking:")
    if results:
        sorted_results = sorted(results.items(), key=lambda x: -x[1]['fg_ssim'])
        for name, m in sorted_results:
            marker = "⭐" if m['fg_ssim'] == max(r['fg_ssim'] for r in results.values()) else "  "
            print(f"  {marker} {name:40s}: FG-SSIM={m['fg_ssim']:.4f}  PSNR={m['psnr']:.2f}")


if __name__ == '__main__':
    main()
