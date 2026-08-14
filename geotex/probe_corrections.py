"""Probe: measure v2 checkpoint's adapter corrections magnitude.

Loads the v2 EMA checkpoint, runs ONE UNet forward on a real test object,
and reports each wrapper's correction norm vs typical hidden magnitude.
Answers: does the v2 adapter actually produce meaningful corrections,
or is its effect negligible (≈ no_adapter)?
"""
import os, sys, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
import torchvision.transforms.v2 as v2
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
from eval_v2_quick import load_model, load_checkpoint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', default='mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt')
parser.add_argument('--device', default='cuda:1')
parser.add_argument('--scale', type=float, default=1.0, help='adapter scale to apply')
args = parser.parse_args()

device = torch.device(args.device)
model, config = load_model('MVPainter/configs/mvpainter-geotex-v2-train.yaml', device)
load_checkpoint(model, args.checkpoint)

dataset = instantiate_from_config(config.data.params.validation)
print(f"Test dataset: {len(dataset)} objects")

for obj_idx in range(min(3, len(dataset))):
    sample = dataset[obj_idx]
    batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v for k, v in sample.items()}
    for k in batch:
        if hasattr(batch[k], 'to'):
            batch[k] = batch[k].to(device)

    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        model.prepare_batch_data(batch, device=device)

    geo_clean = geo_input.float().clamp(0, 1)
    geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
    with torch.no_grad():
        geo_feats = model.geo_encoder(geo_clean)

    B = cond_imgs.shape[0]
    weight_dtype = torch.float16
    cond_imgs_r = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    prompt_embeds = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype) + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs_r).to(weight_dtype)
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    torch.manual_seed(42)
    latents = torch.randn(B, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
    t = torch.tensor([500], device=device, dtype=torch.long)

    model._set_geo_feats_on_wrappers(geo_feats)
    for m in model.unet.modules():
        if isinstance(m, GeoTexResnetWrapper):
            m._adapter_scale = args.scale

    with torch.no_grad():
        noise_pred = model.pipeline.unet(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_latents),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False, is_training=False,
        )[0]

    print(f"\n=== obj {obj_idx} (scale={args.scale}) — correction magnitudes ===")
    print(f"{'wrapper':<24} {'group':<8} {'corr_norm':>9} {'corr_max':>9} {'corr_mean':>9}")
    total_corr = 0.0
    count = 0
    for name, m in model.unet.named_modules():
        if isinstance(m, GeoTexResnetWrapper):
            c = m._last_correction
            if c is None:
                continue
            cn = c.norm().item()
            cm = c.abs().max().item()
            cmean = c.abs().mean().item()
            total_corr += cn
            count += 1
            print(f"{name:<24} {m.depth_group:<8} {cn:9.4f} {cm:9.4f} {cmean:9.4f}")
    print(f"mean correction norm over {count} wrappers: {total_corr/max(count,1):.4f}")
    # noise_pred magnitude for reference
    print(f"noise_pred: norm={noise_pred.norm().item():.4f} mean_abs={noise_pred.abs().mean().item():.4f}")
