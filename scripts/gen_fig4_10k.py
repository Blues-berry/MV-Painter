"""
用10k步checkpoint重跑100个物体的 s=1.25 / s=2.50 / C3。
"""
import os, sys, gc
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geotex'))

from omegaconf import OmegaConf
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import unscale_latents, unscale_image

OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/paper_figures_final/fig4_10k'
CONFIG = '/4T/CXY/MV-Painter/mvpoutput/geotex/eval_config_snapshot.yaml'
CHECKPOINT = '/4T/CXY/MV-Painter/mvpoutput/geotex_10k/checkpoints/geotex_step_0010000.pt'
DEVICE = 'cuda:0'
NUM_STEPS = 50
SEED = 42

# 同样的100个物体
CANDIDATE_OBJECTS = [226, 271, 131, 112, 178, 284, 97, 208, 75, 37, 50, 90, 62, 203, 47, 44, 10, 5, 34, 19,
                     298,69,55,71,28,100,267,108,210,86,16,31,125,9,180,252,245,221,88,84,198,42,104,223,35,
                     101,275,76,61,188,58,240,257,94,17,33,89,102,80,20,52,92,103,95,49,14,23,70,168,197,149,
                     238,279,107,81,30,261,234,24,21,247,51,217,121,29,282,22,145,230,255,4,93,53,74,202,65,
                     46,184,3,293]


def load_model(config_path, checkpoint_path, device):
    from src.utils.train_util import instantiate_from_config
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
def generate(model, batch, device, geo_feats, scale, num_steps, init_latents):
    wdt = torch.float16
    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]
    global_embeds = batch['global_embeds'].to(device, dtype=wdt).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(wdt)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=wdt)
    prompt_embeds = uc_text_emb + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs).to(wdt)
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=wdt) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}
    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)
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
    image = unscale_image(decoded)
    del latents, decoded, prompt_embeds, cond_latents, added_cond_kwargs, cond_imgs, global_embeds
    return (image * 0.5 + 0.5).clamp(0, 1)


@torch.no_grad()
def generate_c3(model, batch, device, geo_feats, num_steps, init_latents):
    """C3 schedule: early=1.25, mid=2.50, late=1.25"""
    wdt = torch.float16
    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]
    global_embeds = batch['global_embeds'].to(device, dtype=wdt).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(wdt)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=wdt)
    prompt_embeds = uc_text_emb + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs).to(wdt)
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=wdt) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}
    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)
    latents = init_latents * scheduler.init_noise_sigma
    
    total_steps = len(scheduler.timesteps)
    # C3 boundaries: early [0, 0.33), mid [0.33, 0.67), late [0.67, 1.0]
    early_end = int(total_steps * 0.33)
    mid_end = int(total_steps * 0.67)
    
    model._set_geo_feats_on_wrappers(geo_feats)
    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            # Set scale based on timestep phase
            if step_idx < early_end:
                scale = 1.25
            elif step_idx < mid_end:
                scale = 2.50
            else:
                scale = 1.25
            
            for module in model.unet.modules():
                if hasattr(module, 'adapter'):
                    module._adapter_scale = scale
            
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
            del latent_input, noise_pred
    finally:
        model._clear_geo_feats_on_wrappers()
        for module in model.unet.modules():
            if hasattr(module, '_adapter_scale'):
                delattr(module, '_adapter_scale')
    
    latents = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(latents / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
    image = unscale_image(decoded)
    del latents, decoded, prompt_embeds, cond_latents, added_cond_kwargs, cond_imgs, global_embeds
    return (image * 0.5 + 0.5).clamp(0, 1)


def main():
    device = torch.device(DEVICE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig_forward = GeoTexResnetWrapper.forward
    def scaled_forward(self, *a, **kw):
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
    GeoTexResnetWrapper.forward = scaled_forward

    print(f"Loading model with 10k checkpoint: {CHECKPOINT}", flush=True)
    model = load_model(CONFIG, CHECKPOINT, device)
    config = OmegaConf.load(CONFIG)
    from src.utils.train_util import instantiate_from_config
    dataset = instantiate_from_config(config.data.params.validation)
    print(f"Dataset: {len(dataset)} objects", flush=True)

    from eval import collate_batch, prepare_batch

    # 跳过已存在的
    todo = []
    for obj_idx in CANDIDATE_OBJECTS:
        s125 = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_s1.25.png')
        if os.path.exists(s125):
            continue
        todo.append(obj_idx)
    
    print(f"Need to generate: {len(todo)} objects (3 conditions each)", flush=True)

    for i, obj_idx in enumerate(todo):
        print(f"[{i+1}/{len(todo)}] obj {obj_idx}", end=' ', flush=True)
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(SEED)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)

        # GT
        gt_path = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_gt.png')
        if not os.path.exists(gt_path):
            save_image(target_imgs, gt_path)

        # s=1.25
        torch.manual_seed(SEED)
        img = generate(model, batch, device, geo_feats, 1.25, NUM_STEPS, shared_latents.clone())
        save_image(img, os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_s1.25.png'))
        del img

        # s=2.50
        torch.manual_seed(SEED)
        img = generate(model, batch, device, geo_feats, 2.50, NUM_STEPS, shared_latents.clone())
        save_image(img, os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_s2.50.png'))
        del img

        # C3
        torch.manual_seed(SEED)
        img = generate_c3(model, batch, device, geo_feats, NUM_STEPS, shared_latents.clone())
        save_image(img, os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_C3.png'))
        del img

        del batch, cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask
        del geo_clean, geo_feats, shared_latents
        gc.collect()
        torch.cuda.empty_cache()
        print("done", flush=True)

    GeoTexResnetWrapper.forward = _orig_forward
    print(f"\nAll done! Results in {OUTPUT_DIR}", flush=True)


if __name__ == '__main__':
    main()
