"""只为A图的目标物体生成 s=2.25"""
import os, sys, gc
import torch
import torch.nn.functional as F

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

# A图物体 + 备选
OBJECTS = [55, 62, 112, 131, 104]

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

def main():
    device = torch.device(DEVICE)
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig = GeoTexResnetWrapper.forward
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

    print("Loading 10k model...", flush=True)
    model = load_model(CONFIG, CHECKPOINT, device)
    config = OmegaConf.load(CONFIG)
    from src.utils.train_util import instantiate_from_config
    dataset = instantiate_from_config(config.data.params.validation)
    from eval import collate_batch, prepare_batch

    for i, obj_idx in enumerate(OBJECTS):
        out_path = os.path.join(OUTPUT_DIR, f'obj_{obj_idx:03d}_s2.25.png')
        if os.path.exists(out_path):
            print(f"[{i+1}/{len(OBJECTS)}] obj {obj_idx} s=2.25 exists, skip", flush=True)
            continue
        print(f"[{i+1}/{len(OBJECTS)}] obj {obj_idx} s=2.25", end=' ', flush=True)
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(SEED)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        torch.manual_seed(SEED)
        img = generate(model, batch, device, geo_feats, 2.25, NUM_STEPS, shared_latents.clone())
        save_image(img, out_path)
        del img, batch, cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask, geo_clean, geo_feats, shared_latents
        gc.collect(); torch.cuda.empty_cache()
        print("done", flush=True)

    GeoTexResnetWrapper.forward = _orig
    print("All s=2.25 done!", flush=True)

if __name__ == '__main__':
    main()
