"""
为 Figure 4 批量生成候选物体的 s=1.25 / s=2.50 推理结果。
C3 结果已经存在（300obj全有），只需要补生成两个均匀 scale 的。
生成完后组合成对比图供选择。
"""
import os, sys, json, gc
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geotex'))

from omegaconf import OmegaConf
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import unscale_latents, unscale_image

# ============================================================
# 候选物体：从300集中选纹理最丰富、且C3效果好的
# ============================================================
CANDIDATE_OBJECTS = [226, 271, 131, 112, 178, 284, 97, 208, 75, 37, 
                     50, 90, 62, 203, 47, 44, 10, 5, 34, 19]

OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/paper_figures_final/fig4_candidates'
CONFIG = '/4T/CXY/MV-Painter/mvpoutput/geotex/eval_config_snapshot.yaml'
CHECKPOINT = '/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt'
C3_VIS_DIR = '/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/C3_300obj/visualizations'
DEVICE = 'cuda:0'
NUM_STEPS = 50
SEED = 42


def load_model(config_path, checkpoint_path, device):
    config = OmegaConf.load(config_path)
    from src.utils.train_util import instantiate_from_config
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


def main():
    device = torch.device(DEVICE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Patch wrapper for scale
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

    print("Loading model...", flush=True)
    model = load_model(CONFIG, CHECKPOINT, device)
    config = OmegaConf.load(CONFIG)
    from src.utils.train_util import instantiate_from_config
    dataset = instantiate_from_config(config.data.params.validation)
    print(f"Dataset loaded: {len(dataset)} objects", flush=True)

    from eval import collate_batch, prepare_batch

    scales = [1.25, 2.50]
    
    for i, obj_idx in enumerate(CANDIDATE_OBJECTS):
        print(f"\n[{i+1}/{len(CANDIDATE_OBJECTS)}] Object {obj_idx}", flush=True)
        
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(SEED)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)

        # Save GT
        gt_path = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_gt.png')
        save_image(target_imgs, gt_path)

        for scale in scales:
            torch.manual_seed(SEED)
            img = generate(model, batch, device, geo_feats, scale, NUM_STEPS, shared_latents.clone())
            out_path = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_s{scale:.2f}.png')
            save_image(img, out_path)
            print(f"  s={scale}: saved", flush=True)
            del img

        # Copy C3 (symlink)
        c3_src = os.path.join(C3_VIS_DIR, f'obj_{obj_idx:03d}_adapter.png')
        c3_dst = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_C3.png')
        if os.path.exists(c3_src) and not os.path.exists(c3_dst):
            os.symlink(c3_src, c3_dst)

        del batch, cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask
        del geo_clean, geo_feats, shared_latents
        gc.collect()
        torch.cuda.empty_cache()

    GeoTexResnetWrapper.forward = _orig_forward
    print(f"\n\nDone! All candidates saved to {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
