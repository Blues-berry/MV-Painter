#!/usr/bin/env python3
"""Debug vis_selected baseline generation using the same logic as eval_scale_inline_visual_only.py."""
import os, sys, torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import unscale_latents, unscale_image
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

BASE = '/4T/CXY/MV-Painter'
DEVICE = torch.device('cuda:1')
CONFIG = f'{BASE}/mvpoutput/geotex/eval_config_snapshot.yaml'
CHECKPOINT = f'{BASE}/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt'
OBJ_IDX = 74

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
def generate_with_scale(model, batch, device, weight_dtype, geo_feats, scale, num_steps=50, init_latents=None):
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
    decoded = model.pipeline.vae.decode(latents / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
    del latents, prompt_embeds, cond_latents, added_cond_kwargs
    image = unscale_image(decoded)
    del decoded
    return (image * 0.5 + 0.5).clamp(0, 1)

def normalize_bg(image, mask, bg_value=1.0):
    bg = (mask < 0.5).expand_as(image)
    result = image.clone()
    result[bg] = bg_value
    return result

def main():
    # Patch forward (like eval_scale_inline_visual_only.py)
    _orig = GeoTexResnetWrapper.forward
    def scaled(self, *a, **kw):
        hs = self.resnet(*a, **kw)
        if self._current_geo_feats is not None:
            gf = self._current_geo_feats.get(self.geo_feat_key)
            if gf is not None:
                if gf.shape[2:] != hs.shape[2:]:
                    gf = torch.nn.functional.interpolate(gf, size=hs.shape[2:], mode='bilinear', align_corners=False)
                c = self.adapter.compute_correction(hs, gf)
                self._last_correction = c
                hs = hs + c * getattr(self, '_adapter_scale', 1.0)
        return hs
    GeoTexResnetWrapper.forward = scaled

    print("Loading model...")
    model = load_model(CONFIG, CHECKPOINT, DEVICE)
    config = OmegaConf.load(CONFIG)
    dataset = instantiate_from_config(config.data.params.validation)

    from eval import collate_batch, prepare_batch

    print(f"Generating baseline for object {OBJ_IDX}...")
    batch = collate_batch(dataset, OBJ_IDX, DEVICE)
    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        prepare_batch(batch, model.img_size, DEVICE)

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    torch.manual_seed(42)
    shared_latents = torch.randn(1, 4, latent_h, latent_w, device=DEVICE, dtype=torch.float16)

    torch.manual_seed(42)
    img_orig = generate_with_scale(model, batch, DEVICE, torch.float16, None, 0, 50, shared_latents)

    # Save raw and normalized
    out_dir = f'{BASE}/debug_baseline'
    os.makedirs(out_dir, exist_ok=True)
    save_image(img_orig, f'{out_dir}/obj_074_vis_selected_raw.png')
    save_image(normalize_bg(img_orig, mask), f'{out_dir}/obj_074_vis_selected_normalized.png')

    # Compare
    raw = img_orig[0].cpu().permute(1, 2, 0).numpy()
    normalized = normalize_bg(img_orig, mask)[0].cpu().permute(1, 2, 0).numpy()

    raw_fg = ~np.all(raw > 0.92, axis=2)
    norm_fg = ~np.all(normalized > 0.92, axis=2)

    print(f"\n=== vis_selected script output (obj_{OBJ_IDX:03d}) ===")
    print(f"Raw baseline:        mean={raw.mean():.3f}, FG_frac={raw_fg.mean():.3f}")
    print(f"Normalized baseline: mean={normalized.mean():.3f}, FG_frac={norm_fg.mean():.3f}")

    # Compare with old eval
    old_path = f'{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations/obj_{OBJ_IDX:03d}_original.png'
    old = np.array(Image.open(old_path).convert('RGB')).astype(float) / 255.0
    old_fg = ~np.all(old > 0.92, axis=2)
    print(f"Old eval baseline:   mean={old.mean():.3f}, FG_frac={old_fg.mean():.3f}")

    # Compare with vis_selected saved file
    vis_path = f'{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/vis_selected/s1p25/visualizations/obj_{OBJ_IDX:03d}_orig.png'
    vis = np.array(Image.open(vis_path).convert('RGB')).astype(float) / 255.0
    vis_fg = ~np.all(vis > 0.92, axis=2)
    print(f"Saved vis_selected:  mean={vis.mean():.3f}, FG_frac={vis_fg.mean():.3f}")

    print(f"\nDiff raw vs old:     {np.abs(raw - old).mean():.4f}")
    print(f"Diff norm vs old:    {np.abs(normalized - old).mean():.4f}")
    print(f"Diff raw vs saved:   {np.abs(raw - vis).mean():.4f}")
    print(f"Diff norm vs saved:  {np.abs(normalized - vis).mean():.4f}")

    GeoTexResnetWrapper.forward = _orig

if __name__ == '__main__':
    main()
