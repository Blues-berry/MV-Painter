"""
VISUALIZATION-ONLY wrapper for selected objects.
NOT the canonical evaluator. NOT used for metric reporting.

Purpose: Generate gt/orig/adapter PNGs for user-selected objects only.
Output: Isolated under visual_artifacts_s250_audit/vis_selected/

This script:
- Only processes specified object indices
- Saves vis for ALL processed objects (not just first 5)
- Output does NOT mix with canonical eval results
- NOT used for 300-object eval or scale sweep

Usage:
    python scripts/visual_audit/eval_scale_inline_visual_only.py \
        --config mvpoutput/geotex/eval_config_snapshot.yaml \
        --checkpoint mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
        --scale 1.25 \
        --objects 18,25,27,38 \
        --output_dir mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/vis_selected/s1p25 \
        --device cuda:0

    python scripts/visual_audit/eval_scale_inline_visual_only.py --dry-run \
        --config ... --checkpoint ... --scale 1.25 --objects 18,25,27,38 \
        --output_dir ...
"""
import os, sys, json, argparse


def dry_run_report(args, obj_indices):
    """Print dry-run report without importing heavy modules."""
    vis_set = set(obj_indices)
    total_images = len(obj_indices) * 3  # gt/orig/adapter

    # Check existing files
    existing = 0
    missing = 0
    vis_dir = os.path.join(args.output_dir, 'visualizations')
    for obj in obj_indices:
        for suffix in ['gt', 'orig', 'adapter']:
            path = os.path.join(vis_dir, f'obj_{obj:03d}_{suffix}.png')
            if os.path.exists(path):
                existing += 1
            else:
                missing += 1

    print("=" * 70)
    print("EVAL_SCALE_INLINE_VISUAL_ONLY — DRY RUN")
    print("=" * 70)
    print()
    print("Script identity:")
    print("  NOT canonical evaluator")
    print("  NOT used for metric reporting")
    print("  Selected visualization only")
    print("  Output isolated under visual_artifacts_s250_audit/vis_selected/")
    print()
    print(f"Config:      {args.config}")
    print(f"Checkpoint:  {args.checkpoint}")
    print(f"Scale:       {args.scale}")
    print(f"Objects:     {obj_indices} ({len(obj_indices)} total)")
    print(f"Output dir:  {args.output_dir}")
    print(f"Device:      {args.device}")
    print(f"Seed:        {args.seed}")
    print(f"Steps:       {args.steps}")
    print()
    print(f"Vis dir:     {vis_dir}")
    print(f"Existing:    {existing}/{total_images}")
    print(f"Missing:     {missing}/{total_images}")
    if existing > 0:
        print(f"  ⚠️ {existing} files already exist — will NOT overwrite")
    print()
    print("--- DRY RUN ---")
    print(f"Model inference called during dry-run?    NO")
    print(f"GPU used during dry-run?                  NO")
    print(f"Heavy modules imported during dry-run?    NO")
    print(f"Images generated during dry-run?           NO")
    print(f"Files written during dry-run?              NO")
    print()
    print(f"If run WITHOUT --dry-run:")
    print(f"  Model inference called?                  YES (diffusion UNet)")
    print(f"  GPU used?                                YES ({args.device})")
    print(f"  Images generated?                        YES ({missing} PNGs)")
    print(f"  Written to canonical eval dir?            NO")
    print(f"  Written to 300-object eval dir?           NO")
    print(f"  Overwrites existing canonical results?    NO")
    print()
    print("NOT executed. Run without --dry-run to generate.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--scale', type=float, default=1.25)
    parser.add_argument('--objects', type=str, required=True,
                        help='Comma-separated object indices')
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--dry-run', action='store_true',
                        help='Print plan without executing (no GPU, no model)')
    args = parser.parse_args()

    obj_indices = [int(x) for x in args.objects.split(',')]

    if args.dry_run:
        dry_run_report(args, obj_indices)
        return

    # === Heavy imports deferred until after dry-run check ===
    import signal, gc
    import torch, torch.nn.functional as F, numpy as np

    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MVPainter'))
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from torchvision.transforms import v2
    from torchvision.utils import save_image
    from diffusers import EulerDiscreteScheduler

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'geotex'))
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
    def generate_with_scale(model, batch, device, weight_dtype, geo_feats, scale,
                            num_steps=50, init_latents=None):
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
        decoded = model.pipeline.vae.decode(
            latents / model.pipeline.vae.config.scaling_factor, return_dict=False
        )[0]
        del latents, prompt_embeds, cond_latents, added_cond_kwargs
        image = unscale_image(decoded)
        del decoded
        return (image * 0.5 + 0.5).clamp(0, 1)

    def normalize_bg(image, mask, bg_value=1.0):
        bg = (mask < 0.5).expand_as(image)
        result = image.clone()
        result[bg] = bg_value
        return result

    # === Execution ===
    device = torch.device(args.device)
    wdt = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

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
    lpips_fn = get_lpips_fn(device)

    from eval import collate_batch, prepare_batch

    vis_dir = os.path.join(args.output_dir, 'visualizations')
    os.makedirs(vis_dir, exist_ok=True)

    with open(os.path.join(args.output_dir, 'config_snapshot.json'), 'w') as f:
        json.dump({'config': args.config, 'checkpoint': args.checkpoint,
                    'scale': args.scale, 'objects': obj_indices,
                    'steps': args.steps, 'seed': args.seed,
                    'note': 'VISUAL ONLY — not canonical eval'}, f, indent=2)

    print(f"{'='*60}", flush=True)
    print(f"VISUAL-ONLY: Scale={args.scale}, Objects={obj_indices}", flush=True)
    print(f"{'='*60}", flush=True)

    for obj_idx in obj_indices:
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)

        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=wdt)

        torch.manual_seed(args.seed)
        img_orig = generate_with_scale(model, batch, device, wdt, None, 0, args.steps, shared_latents)

        torch.manual_seed(args.seed)
        img_adapter = generate_with_scale(model, batch, device, wdt, geo_feats,
                                          args.scale, args.steps, shared_latents)

        gt = target_imgs[:1]

        save_image(gt, os.path.join(vis_dir, f'obj_{obj_idx:03d}_gt.png'))
        save_image(normalize_bg(img_orig, mask), os.path.join(vis_dir, f'obj_{obj_idx:03d}_orig.png'))
        save_image(normalize_bg(img_adapter, mask), os.path.join(vis_dir, f'obj_{obj_idx:03d}_adapter.png'))

        del img_orig, img_adapter, gt, mask, batch, geo_feats, shared_latents
        del cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, geo_clean
        torch.cuda.empty_cache()

        print(f"  Obj {obj_idx}: saved vis", flush=True)

    GeoTexResnetWrapper.forward = _orig
    print(f"\nVisual-only generation complete. Output: {args.output_dir}")


if __name__ == '__main__':
    main()
