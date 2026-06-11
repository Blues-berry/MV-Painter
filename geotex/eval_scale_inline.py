"""Inline scale eval: generate baseline + adapter per object, compute metrics, free memory.

No baseline caching. Each object: generate baseline → generate adapter → compute metrics → free.

Usage:
    python geotex/eval_scale_inline.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scale 1.25 \
        --num_objects 300 \
        --output_dir mvpoutput/geotex_refattn_v1/scale_1p25_300obj \
        --device cuda:1
"""
import os, sys, json, csv, argparse, signal, gc
import torch, torch.nn.functional as F, numpy as np

signal.signal(signal.SIGTERM, signal.SIG_IGN)
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image


def get_lpips_fn(device):
    try:
        import lpips
        return lpips.LPIPS(net='alex').to(device).eval()
    except:
        return None


def compute_lpips(pred, target, mask=None, lpips_fn=None, device=None):
    if lpips_fn is None:
        return None
    p, t = pred * 2 - 1, target * 2 - 1
    if mask is not None:
        m = mask[:, :1]
        if m.shape[2:] != p.shape[2:]:
            m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
        p, t = p * m, t * m
    with torch.no_grad():
        return lpips_fn(p, t).item()


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
def generate(model, batch, device, weight_dtype, geo_feats, scale, num_steps, init_latents):
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
    if init_latents is None:
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
    del latents, prompt_embeds, cond_latents, added_cond_kwargs, cond_imgs, global_embeds
    image = unscale_image(decoded)
    del decoded
    return (image * 0.5 + 0.5).clamp(0, 1)


def normalize_bg(image, mask, val=1.0):
    bg = (mask < 0.5).expand_as(image)
    r = image.clone()
    r[bg] = val
    return r


def fg_crop(image, mask, pad=0.1):
    fg = mask[0, 0] > 0.5
    if fg.sum() == 0:
        return image, mask
    rows = torch.any(fg, dim=1)
    cols = torch.any(fg, dim=0)
    rmin, rmax = torch.where(rows)[0][[0, -1]]
    cmin, cmax = torch.where(cols)[0][[0, -1]]
    H, W = fg.shape
    ph, pw = int((rmax - rmin).item() * pad), int((cmax - cmin).item() * pad)
    rmin, rmax = max(0, rmin - ph), min(H - 1, rmax + ph)
    cmin, cmax = max(0, cmin - pw), min(W - 1, cmax + pw)
    rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
    return image[:, :, rmin:rmax+1, cmin:cmax+1], mask[:, :, rmin:rmax+1, cmin:cmax+1]


def morph(mask, ks, op='erode'):
    if ks <= 0:
        return mask
    p = ks // 2
    k = torch.ones(1, 1, ks, ks, device=mask.device)
    c = F.conv2d(mask, k, padding=p)
    return (c >= ks * ks).float() if op == 'erode' else (c > 0).float()


def metrics(pred, target, mask, edge, lpips_fn, dev):
    r = {}
    r['full_psnr'] = compute_psnr(pred, target)
    r['full_ssim'] = compute_ssim(pred, target)
    r['full_lpips'] = compute_lpips(pred, target, lpips_fn=lpips_fn, device=dev)
    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)
    r['fg_lpips'] = compute_lpips(pred, target, mask, lpips_fn=lpips_fn, device=dev)
    bg = 1.0 - mask
    r['bg_psnr'] = compute_psnr(pred, target, bg)
    r['edge_psnr'] = compute_psnr(pred, target, edge)
    r['edge_ssim'] = compute_ssim(pred, target, edge)
    nef = mask * (1 - edge)
    r['nef_ssim'] = compute_ssim(pred, target, nef)
    pw = normalize_bg(pred, mask, 1.0)
    tw = normalize_bg(target, mask, 1.0)
    r['bgwhite_psnr'] = compute_psnr(pw, tw)
    r['bgwhite_ssim'] = compute_ssim(pw, tw)
    r['bgwhite_lpips'] = compute_lpips(pw, tw, lpips_fn=lpips_fn, device=dev)
    pc, _ = fg_crop(pred, mask, 0.1)
    tc, _ = fg_crop(target, mask, 0.1)
    r['crop_psnr'] = compute_psnr(pc, tc)
    r['crop_ssim'] = compute_ssim(pc, tc)
    r['crop_lpips'] = compute_lpips(pc, tc, lpips_fn=lpips_fn, device=dev)
    r['crop_area'] = float(pc.numel() / pred.numel())
    for s in [3, 5, 10]:
        m = morph(mask, s * 2 + 1, 'erode')
        r[f'fg_psnr_e{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_e{s}'] = compute_ssim(pred, target, m)
    for s in [3, 5, 10]:
        m = morph(mask, s * 2 + 1, 'dilate')
        r[f'fg_psnr_d{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_d{s}'] = compute_ssim(pred, target, m)
    return r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--scale', type=float, default=1.25)
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--device', default='cuda:1')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    device = torch.device(args.device)
    wdt = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Patch wrapper for scale
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    _orig = GeoTexResnetWrapper.forward
    def scaled(self, *a, **kw):
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
    GeoTexResnetWrapper.forward = scaled

    print(f"Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    num = min(args.num_objects, len(dataset))
    lpips_fn = get_lpips_fn(device)

    from eval import collate_batch, prepare_batch

    # Save config
    with open(os.path.join(args.output_dir, 'config_snapshot.json'), 'w') as f:
        json.dump({'config': args.config, 'checkpoint': args.checkpoint,
                    'scale': args.scale, 'num_objects': num,
                    'steps': args.steps, 'seed': args.seed}, f, indent=2)

    vis_dir = os.path.join(args.output_dir, 'visualizations')
    os.makedirs(vis_dir, exist_ok=True)
    results = []

    print(f"{'='*60}", flush=True)
    print(f"Scale = {args.scale}, Objects = {num}", flush=True)
    print(f"{'='*60}", flush=True)

    for obj_idx in range(num):
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=wdt)

        # Generate baseline (no adapter)
        torch.manual_seed(args.seed)
        img_orig = generate(model, batch, device, wdt, None, 0, args.steps, shared_latents)

        # Generate adapter
        torch.manual_seed(args.seed)
        img_adapter = generate(model, batch, device, wdt, geo_feats, args.scale, args.steps, shared_latents)

        gt = target_imgs
        edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        if edge_mask.shape[2:] != gt.shape[2:]:
            edge_mask = F.interpolate(edge_mask, size=gt.shape[2:], mode='bilinear', align_corners=False)

        # Compute metrics
        adapter_m = metrics(img_adapter, gt, mask, edge_mask, lpips_fn, device)
        orig_m = metrics(img_orig, gt, mask, edge_mask, lpips_fn, device)

        r = {'object_idx': obj_idx, 'scale': args.scale,
             'fg_ratio': float((mask > 0.5).sum().item() / mask.numel())}
        for k, v in adapter_m.items():
            r[f'adapter_{k}'] = v
        for k, v in orig_m.items():
            r[f'orig_{k}'] = v
        for k in adapter_m:
            if adapter_m[k] is not None and orig_m[k] is not None:
                r[f'delta_{k}'] = adapter_m[k] - orig_m[k]
        results.append(r)

        # Save vis for first 5
        if obj_idx < 5:
            save_image(gt, os.path.join(vis_dir, f'obj_{obj_idx:03d}_gt.png'))
            save_image(img_orig, os.path.join(vis_dir, f'obj_{obj_idx:03d}_orig.png'))
            save_image(img_adapter, os.path.join(vis_dir, f'obj_{obj_idx:03d}_adapter.png'))

        # Free everything
        del img_orig, img_adapter, gt, mask, edge_mask, batch, geo_feats, shared_latents
        del cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, geo_clean
        del adapter_m, orig_m, edge_source
        gc.collect()
        torch.cuda.empty_cache()

        if obj_idx % 10 == 0:
            d_cp = r.get('delta_crop_psnr', 0)
            d_cs = r.get('delta_crop_ssim', 0)
            d_es = r.get('delta_edge_ssim', 0)
            d_fs = r.get('delta_fg_ssim', 0)
            mem = torch.cuda.memory_allocated(device) / 1e9
            print(f"  Obj {obj_idx:3d}: crop_psnr={d_cp:+.2f} crop_ssim={d_cs:+.4f} "
                  f"edge_ssim={d_es:+.4f} fg_ssim={d_fs:+.4f} mem={mem:.1f}GB", flush=True)

        # Save partial every 20
        if (obj_idx + 1) % 20 == 0:
            _save(results, args.output_dir)

    _save(results, args.output_dir)
    GeoTexResnetWrapper.forward = _orig
    print(f"\nDone. {len(results)} objects.", flush=True)


def _save(results, out_dir):
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(os.path.join(out_dir, 'per_object_metrics.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    summary = {'num_objects': len(results)}
    for col in fieldnames:
        if col in ('object_idx', 'scale', 'fg_ratio'):
            continue
        vals = [r[col] for r in results if r.get(col) is not None]
        if vals:
            arr = np.array(vals)
            pos = int(np.sum(arr > 0)) if 'delta' in col else None
            summary[col] = {'mean': float(arr.mean()), 'std': float(arr.std()),
                            'positive': pos, 'total': len(arr)}
    with open(os.path.join(out_dir, 'summary_metrics.json'), 'w') as f:
        json.dump(summary, f, indent=2, default=str)


if __name__ == '__main__':
    main()
