"""FAC 300-object controlled ablation evaluation.

Evaluates TCAS vs LTAG vs LTAG+GSG vs Full FAC on 300 test objects with:
- Full metric suite (PSNR, SSIM, FG-PSNR, FG-SSIM, Edge-SSIM, FG-LPIPS,
  RGB Std ratio, Gradient ratio, Lap Var loss)
- Paired t-test (Full FAC vs TCAS)
- Win rates
- Per-object CSV
- Paper-ready comparison figure with zoom-in

Checkpoint: FAC v3 (geotex_final.pt with trained LTAG+GSG+FSC)
Test list: test_objects_300.txt (same as paper Table 3)
"""
import os, sys, json, csv, argparse, gc, time
import torch
import torch.nn.functional as F
import numpy as np
from scipy import stats
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from einops import rearrange

from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image
from metrics_extended import compute_all_extended
from mvpainter.adaptive_correction import AdaptiveCorrectionController
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


# ============================================================
# LPIPS
# ============================================================
def get_lpips_fn(device):
    try:
        import lpips
        return lpips.LPIPS(net='alex').to(device).eval()
    except ImportError:
        print("WARNING: lpips not available, FG-LPIPS will be None")
        return None

def compute_fg_lpips(pred, target, mask, lpips_fn):
    if lpips_fn is None:
        return None
    p = pred * 2 - 1
    t = target * 2 - 1
    m = mask[:, :1]
    if m.shape[2:] != p.shape[2:]:
        m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
    p = p * m
    t = t * m
    with torch.no_grad():
        return lpips_fn(p, t).item()


# ============================================================
# Edge-SSIM
# ============================================================
def compute_edge_ssim(pred, target, mask=None, threshold=0.1):
    """SSIM computed only on edge regions."""
    gray_t = target.mean(dim=1, keepdim=True)
    sobel_x = torch.tensor([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=gray_t.dtype, device=gray_t.device).view(1,1,3,3)
    sobel_y = torch.tensor([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=gray_t.dtype, device=gray_t.device).view(1,1,3,3)
    gx = F.conv2d(gray_t, sobel_x, padding=1)
    gy = F.conv2d(gray_t, sobel_y, padding=1)
    grad = torch.sqrt(gx**2 + gy**2 + 1e-8)
    edge_mask = (grad / (grad.max() + 1e-8) > threshold).float()
    if mask is not None:
        m = mask[:, :1] if mask.shape[1] > 1 else mask
        edge_mask = edge_mask * m
    if edge_mask.sum() < 100:
        return None
    return compute_ssim(pred, target, edge_mask)


# ============================================================
# Model Loading
# ============================================================
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


def get_num_adapters(model):
    count = 0
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            count += 1
    return count


def attach_controller(model, controller, device):
    controller = controller.to(device)
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._correction_controller = controller

def detach_controller(model):
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._correction_controller = None


# ============================================================
# TCAS schedule
# ============================================================
def get_tcas_scale(step_idx, total_steps, schedule):
    frac = step_idx / max(total_steps - 1, 1)
    if frac < 0.33:
        return schedule.get('early', 1.25)
    elif frac < 0.66:
        return schedule.get('mid', 2.50)
    else:
        return schedule.get('late', 1.25)

def setup_static_scale(model, scale):
    for module in model.unet.modules():
        if isinstance(module, GeoTexResnetWrapper):
            module._adapter_scale = scale

def clear_scales(model):
    for module in model.unet.modules():
        if hasattr(module, '_adapter_scale'):
            delattr(module, '_adapter_scale')


# ============================================================
# Generation
# ============================================================
@torch.no_grad()
def generate_with_variant(model, batch, device, weight_dtype, geo_feats,
                          num_steps, init_latents, variant, controller=None,
                          tcas_schedule=None):
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
    latents = init_latents * scheduler.init_noise_sigma

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    if variant == 'tcas':
        detach_controller(model)
    else:
        attach_controller(model, controller, device)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            if variant == 'tcas':
                scale = get_tcas_scale(step_idx, num_steps, tcas_schedule or {})
                setup_static_scale(model, scale)
            elif controller is not None:
                controller.set_timestep(t)

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        model._clear_geo_feats_on_wrappers()
        clear_scales(model)
        detach_controller(model)

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False)[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


# ============================================================
# Metrics
# ============================================================
def compute_all_metrics(pred, target, mask, lpips_fn=None, device='cuda'):
    """Compute full metric suite."""
    r = {}
    r['psnr'] = compute_psnr(pred, target)
    r['ssim'] = compute_ssim(pred, target)
    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)
    r['edge_ssim'] = compute_edge_ssim(pred, target, mask)
    r['fg_lpips'] = compute_fg_lpips(pred, target, mask, lpips_fn)

    # Extended texture metrics
    try:
        ext = compute_all_extended(pred, target, mask)
        r['fg_rgb_std'] = ext.get('fg_rgb_std', 0)
        r['gt_fg_rgb_std'] = ext.get('gt_fg_rgb_std', 0)
        r['fg_grad_mag'] = ext.get('fg_grad_mag', 0)
        r['gt_fg_grad_mag'] = ext.get('gt_fg_grad_mag', 0)
        r['fg_lap_var'] = ext.get('fg_lap_var', 0)
        r['gt_fg_lap_var'] = ext.get('gt_fg_lap_var', 0)
        # Ratios (closer to 1.0 = closer to GT)
        r['rgb_std_ratio'] = r['fg_rgb_std'] / (r['gt_fg_rgb_std'] + 1e-8)
        r['grad_ratio'] = r['fg_grad_mag'] / (r['gt_fg_grad_mag'] + 1e-8)
        r['lap_var_loss'] = abs(r['fg_lap_var'] - r['gt_fg_lap_var'])
    except Exception as e:
        r['rgb_std_ratio'] = None
        r['grad_ratio'] = None
        r['lap_var_loss'] = None

    return r


# ============================================================
# Main
# ============================================================
VARIANTS = {
    'tcas': 'TCAS (baseline)',
    'ltag': 'LTAG only',
    'ltag_gsg': 'LTAG + GSG',
    'full_fac': 'Full FAC',
}


def run_eval(args):
    device = torch.device(args.device)
    weight_dtype = torch.float16
    num_steps = args.num_steps
    tcas_schedule = {'early': 1.25, 'mid': 2.50, 'late': 1.25}

    # Output
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'samples'), exist_ok=True)

    # Load model
    print(f"Loading model from {args.checkpoint}...")
    model = load_model(args.config, args.checkpoint, device)
    num_adapters = get_num_adapters(model)
    print(f"Model loaded: {num_adapters} adapters")

    # LPIPS
    lpips_fn = get_lpips_fn(device)

    # Create controllers
    controllers = {}
    controllers['ltag'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=False, enable_fsc=False,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )
    controllers['ltag_gsg'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=True, enable_fsc=False,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )
    controllers['full_fac'] = AdaptiveCorrectionController(
        num_adapters=num_adapters, geo_channels=64,
        enable_ltag=True, enable_gsg=True, enable_fsc=True,
        ltag_kwargs={'init_schedule': tcas_schedule},
    )

    # Load FAC weights
    if args.fac_checkpoint and os.path.exists(args.fac_checkpoint):
        print(f"Loading FAC weights from {args.fac_checkpoint}")
        fac_state = torch.load(args.fac_checkpoint, map_location='cpu')
        if 'fac_controller' in fac_state:
            fac_ctrl_state = fac_state['fac_controller']
        else:
            fac_ctrl_state = fac_state
        for key, ctrl in controllers.items():
            try:
                ctrl.load_state_dict(fac_ctrl_state, strict=False)
            except Exception as e:
                print(f"  Warning: could not load FAC for {key}: {e}")
        print("  FAC weights loaded")

    # Load dataset (test split)
    print("Loading test dataset...")
    config = OmegaConf.load(args.config)
    # Override to use test split
    test_dataset_cfg = config.data.params.get('validation', config.data.params.train)
    if hasattr(test_dataset_cfg, 'params'):
        test_dataset_cfg.params.object_list_file = 'test_objects_300.txt'
    dataset = instantiate_from_config(test_dataset_cfg)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Test dataset: {len(dataset)} objects, evaluating {num_objects}")

    # Per-object results
    all_results = defaultdict(list)  # variant -> [dict per obj]
    obj_names = []

    print(f"\nRunning 300-object evaluation: {num_objects} objects × {len(VARIANTS)} variants")
    print(f"Steps: {num_steps}, Seed: 42+idx")
    print("=" * 80)

    start_time = time.time()
    for obj_idx in range(num_objects):
        batch = dataset[obj_idx]
        batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        obj_name = f'obj_{obj_idx:04d}'
        obj_names.append(obj_name)

        # Prepare
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        # Fixed seed
        seed = 42 + obj_idx
        torch.manual_seed(seed)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for variant_key, variant_name in VARIANTS.items():
            controller = controllers.get(variant_key)
            pred = generate_with_variant(
                model, batch, device, weight_dtype, geo_feats,
                num_steps, init_latents, variant_key,
                controller=controller, tcas_schedule=tcas_schedule,
            )

            metrics = compute_all_metrics(pred, target_imgs, mask, lpips_fn, device)
            metrics['variant'] = variant_key
            metrics['object'] = obj_name
            metrics['obj_idx'] = obj_idx
            all_results[variant_key].append(metrics)

            # Save sample images for figure generation (first 20 objects)
            if obj_idx < 20:
                var_dir = os.path.join(args.output_dir, 'samples', variant_key)
                os.makedirs(var_dir, exist_ok=True)
                save_image(pred, os.path.join(var_dir, f'{obj_name}.png'))
                if variant_key == 'tcas':
                    # Also save GT
                    gt_dir = os.path.join(args.output_dir, 'samples', 'gt')
                    os.makedirs(gt_dir, exist_ok=True)
                    save_image(target_imgs, os.path.join(gt_dir, f'{obj_name}.png'))

        # Progress
        if (obj_idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            speed = (obj_idx + 1) / elapsed
            eta = (num_objects - obj_idx - 1) / speed
            tcas_psnr = all_results['tcas'][-1]['psnr']
            fac_psnr = all_results['full_fac'][-1]['psnr']
            print(f"[{obj_idx+1}/{num_objects}] TCAS={tcas_psnr:.2f} FAC={fac_psnr:.2f} "
                  f"| {speed:.2f} obj/s | ETA: {eta:.0f}s")

        # Periodically clear CUDA cache
        if (obj_idx + 1) % 50 == 0:
            torch.cuda.empty_cache()
            gc.collect()

    elapsed_total = time.time() - start_time
    print(f"\nEvaluation complete: {elapsed_total:.0f}s ({num_objects/elapsed_total:.2f} obj/s)")

    # ============================================================
    # Compute Summary Statistics
    # ============================================================
    metric_keys = ['psnr', 'ssim', 'fg_psnr', 'fg_ssim', 'edge_ssim', 'fg_lpips',
                   'rgb_std_ratio', 'grad_ratio', 'lap_var_loss']

    summary = {}
    for variant_key, variant_name in VARIANTS.items():
        ms = all_results[variant_key]
        s = {'variant': variant_name}
        for mk in metric_keys:
            vals = [m[mk] for m in ms if m.get(mk) is not None]
            s[mk] = np.mean(vals) if vals else None
            s[f'{mk}_std'] = np.std(vals) if vals else None
        summary[variant_key] = s

    # ============================================================
    # Paired t-test: Full FAC vs TCAS
    # ============================================================
    ttest_results = {}
    test_metrics = ['psnr', 'fg_psnr', 'fg_ssim', 'fg_lpips', 'edge_ssim']
    for mk in test_metrics:
        tcas_vals = [m[mk] for m in all_results['tcas'] if m.get(mk) is not None]
        fac_vals = [m[mk] for m in all_results['full_fac'] if m.get(mk) is not None]
        if len(tcas_vals) == len(fac_vals) and len(tcas_vals) > 1:
            t_stat, p_value = stats.ttest_rel(fac_vals, tcas_vals)
            ttest_results[mk] = {'t_stat': t_stat, 'p_value': p_value,
                                  'significant': p_value < 0.05}

    # ============================================================
    # Win rates
    # ============================================================
    win_rates = {}
    for mk in ['psnr', 'fg_psnr', 'fg_ssim', 'fg_lpips']:
        tcas_vals = [m[mk] for m in all_results['tcas'] if m.get(mk) is not None]
        fac_vals = [m[mk] for m in all_results['full_fac'] if m.get(mk) is not None]
        if mk == 'fg_lpips':  # lower is better
            wins = sum(1 for f, t in zip(fac_vals, tcas_vals) if f < t)
        else:
            wins = sum(1 for f, t in zip(fac_vals, tcas_vals) if f > t)
        total = len(tcas_vals)
        win_rates[mk] = {'wins': wins, 'total': total, 'rate': wins / max(total, 1)}

    # ============================================================
    # Deltas
    # ============================================================
    deltas = {}
    for mk in metric_keys:
        tcas_val = summary['tcas'].get(mk)
        fac_val = summary['full_fac'].get(mk)
        if tcas_val is not None and fac_val is not None:
            deltas[mk] = fac_val - tcas_val

    # ============================================================
    # Print Summary
    # ============================================================
    print("\n" + "=" * 100)
    print("300-OBJECT FAC ABLATION SUMMARY")
    print("=" * 100)

    header = f"{'Variant':22s}"
    for mk in metric_keys:
        arrow = '↓' if mk in ['fg_lpips', 'lap_var_loss'] else '↑'
        header += f" {mk}{arrow:>12s}"
    print(header)
    print("-" * 100)

    for variant_key in VARIANTS:
        s = summary[variant_key]
        line = f"{s['variant']:22s}"
        for mk in metric_keys:
            v = s.get(mk)
            if v is None:
                line += f" {'N/A':>12s}"
            elif mk in ['psnr', 'fg_psnr']:
                line += f" {v:>12.2f}"
            else:
                line += f" {v:>12.4f}"
        print(line)

    print("\n--- Deltas (Full FAC - TCAS) ---")
    for mk, d in deltas.items():
        print(f"  Δ{mk}: {d:+.4f}")

    print("\n--- Paired t-test (Full FAC vs TCAS) ---")
    for mk, tt in ttest_results.items():
        sig = "***" if tt['p_value'] < 0.001 else "**" if tt['p_value'] < 0.01 else "*" if tt['p_value'] < 0.05 else "ns"
        print(f"  {mk}: t={tt['t_stat']:.3f}, p={tt['p_value']:.4f} {sig}")

    print("\n--- Win Rates (Full FAC beats TCAS) ---")
    for mk, wr in win_rates.items():
        print(f"  {mk}: {wr['wins']}/{wr['total']} ({wr['rate']*100:.1f}%)")

    # ============================================================
    # Save outputs
    # ============================================================

    # 1. Main table CSV
    csv_path = os.path.join(args.output_dir, 'fac_ablation_300_table.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['variant'] + metric_keys)
        writer.writeheader()
        for vk in VARIANTS:
            row = {mk: summary[vk].get(mk) for mk in metric_keys}
            row['variant'] = summary[vk]['variant']
            writer.writerow(row)
    print(f"\nSaved: {csv_path}")

    # 2. Per-object CSV
    per_obj_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    all_per_obj = []
    for vk in VARIANTS:
        all_per_obj.extend(all_results[vk])
    if all_per_obj:
        fieldnames = list(all_per_obj[0].keys())
        with open(per_obj_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_per_obj)
    print(f"Saved: {per_obj_path}")

    # 3. Full JSON
    json_path = os.path.join(args.output_dir, 'fac_ablation_300_results.json')
    json_out = {
        'config': {
            'checkpoint': args.checkpoint,
            'fac_checkpoint': args.fac_checkpoint,
            'num_objects': num_objects,
            'num_steps': num_steps,
            'seed_base': 42,
        },
        'summary': summary,
        'deltas': deltas,
        'ttest': {k: {kk: float(vv) if isinstance(vv, (np.floating, float)) else vv
                      for kk, vv in v.items()} for k, v in ttest_results.items()},
        'win_rates': win_rates,
        'elapsed_s': elapsed_total,
    }
    with open(json_path, 'w') as f:
        json.dump(json_out, f, indent=2, default=str)
    print(f"Saved: {json_path}")

    # 4. Summary markdown
    md_path = os.path.join(args.output_dir, 'fac_ablation_300_summary.md')
    with open(md_path, 'w') as f:
        f.write("# FAC 300-Object Ablation Summary\n\n")
        f.write(f"- Checkpoint: `{args.checkpoint}`\n")
        f.write(f"- FAC weights: `{args.fac_checkpoint}`\n")
        f.write(f"- Objects: {num_objects}, Steps: {num_steps}, Seed: 42+idx\n")
        f.write(f"- Time: {elapsed_total:.0f}s\n\n")

        f.write("## Main Table\n\n")
        f.write(f"| Variant | PSNR↑ | SSIM↑ | FG-PSNR↑ | FG-SSIM↑ | Edge-SSIM↑ | FG-LPIPS↓ | RGB Std Ratio↑ | Grad Ratio↑ | Lap Var Loss↓ |\n")
        f.write(f"|---------|-------|-------|----------|----------|------------|-----------|----------------|-------------|---------------|\n")
        for vk in VARIANTS:
            s = summary[vk]
            f.write(f"| {s['variant']} |")
            for mk in metric_keys:
                v = s.get(mk)
                if v is None:
                    f.write(f" N/A |")
                elif mk in ['psnr', 'fg_psnr']:
                    f.write(f" {v:.2f} |")
                else:
                    f.write(f" {v:.4f} |")
            f.write("\n")

        f.write("\n## Deltas (Full FAC - TCAS)\n\n")
        for mk, d in deltas.items():
            f.write(f"- Δ{mk}: **{d:+.4f}**\n")

        f.write("\n## Statistical Significance (Paired t-test)\n\n")
        f.write("| Metric | t-stat | p-value | Significant |\n")
        f.write("|--------|--------|---------|-------------|\n")
        for mk, tt in ttest_results.items():
            sig = "✓" if tt['significant'] else "✗"
            f.write(f"| {mk} | {tt['t_stat']:.3f} | {tt['p_value']:.4f} | {sig} |\n")

        f.write("\n## Win Rates\n\n")
        for mk, wr in win_rates.items():
            f.write(f"- {mk}: **{wr['wins']}/{wr['total']} ({wr['rate']*100:.1f}%)**\n")

    print(f"Saved: {md_path}")

    # ============================================================
    # Generate comparison figure
    # ============================================================
    print("\nGenerating comparison figure...")
    generate_comparison_figure(all_results, args.output_dir, device)
    print("Done!")


def generate_comparison_figure(all_results, output_dir, device):
    """Generate paper-ready comparison figure with zoom-in.

    Object selection:
    - 2 best (largest FAC-TCAS PSNR delta)
    - 2 median
    - 2 worst (smallest or negative delta)
    """
    from PIL import Image, ImageDraw, ImageFont
    from torchvision.io import read_image

    # Compute per-object deltas
    tcas_results = {m['obj_idx']: m for m in all_results['tcas']}
    fac_results = {m['obj_idx']: m for m in all_results['full_fac']}

    deltas_per_obj = []
    for idx in tcas_results:
        if idx in fac_results and idx < 20:  # only have samples for first 20
            d = fac_results[idx]['fg_psnr'] - tcas_results[idx]['fg_psnr']
            deltas_per_obj.append((idx, d))

    if not deltas_per_obj:
        print("  No samples available for figure")
        return

    deltas_per_obj.sort(key=lambda x: x[1])

    # Select objects
    n = len(deltas_per_obj)
    selected = []
    # 2 worst
    selected.extend(deltas_per_obj[:2])
    # 2 median
    mid = n // 2
    selected.extend(deltas_per_obj[mid-1:mid+1])
    # 2 best
    selected.extend(deltas_per_obj[-2:])

    # Build figure
    samples_dir = os.path.join(output_dir, 'samples')
    rows = []
    crop_size = 180
    zoom_out_size = 300

    for obj_idx, delta in selected:
        obj_name = f'obj_{obj_idx:04d}'
        gt_path = os.path.join(samples_dir, 'gt', f'{obj_name}.png')
        tcas_path = os.path.join(samples_dir, 'tcas', f'{obj_name}.png')
        fac_path = os.path.join(samples_dir, 'full_fac', f'{obj_name}.png')

        if not all(os.path.exists(p) for p in [gt_path, tcas_path, fac_path]):
            continue

        gt = read_image(gt_path).float() / 255.0
        tcas_img = read_image(tcas_path).float() / 255.0
        fac_img = read_image(fac_path).float() / 255.0

        # Ensure same size
        h = min(gt.shape[1], tcas_img.shape[1], fac_img.shape[1])
        w = min(gt.shape[2], tcas_img.shape[2], fac_img.shape[2])
        gt = gt[:, :h, :w]
        tcas_img = tcas_img[:, :h, :w]
        fac_img = fac_img[:, :h, :w]

        # Auto-select zoom region: find region with max difference
        diff = (fac_img - tcas_img).abs().mean(dim=0)  # (H, W)
        # Use average pooling to find densest difference region
        diff_pooled = F.avg_pool2d(diff.unsqueeze(0).unsqueeze(0), crop_size, stride=crop_size//4)
        max_pos = diff_pooled.flatten().argmax().item()
        ph, pw = diff_pooled.shape[2], diff_pooled.shape[3]
        max_y = (max_pos // pw) * (crop_size // 4)
        max_x = (max_pos % pw) * (crop_size // 4)
        # Clamp
        max_y = min(max_y, h - crop_size)
        max_x = min(max_x, w - crop_size)
        max_y = max(0, max_y)
        max_x = max(0, max_x)
        region = (max_y, max_y + crop_size, max_x, max_x + crop_size)

        # Draw rectangle
        def draw_rect(img, r, color=(1,0,0), width=2):
            y1, y2, x1, x2 = r
            out = img.clone()
            for ww in range(width):
                out[0, y1+ww, x1:x2] = color[0]; out[1, y1+ww, x1:x2] = color[1]; out[2, y1+ww, x1:x2] = color[2]
                out[0, y2-1-ww, x1:x2] = color[0]; out[1, y2-1-ww, x1:x2] = color[1]; out[2, y2-1-ww, x1:x2] = color[2]
                out[0, y1:y2, x1+ww] = color[0]; out[1, y1:y2, x1+ww] = color[1]; out[2, y1:y2, x1+ww] = color[2]
                out[0, y1:y2, x2-1-ww] = color[0]; out[1, y1:y2, x2-1-ww] = color[1]; out[2, y1:y2, x2-1-ww] = color[2]
            return out

        def crop_zoom(img, r):
            y1, y2, x1, x2 = r
            crop = img[:, y1:y2, x1:x2]
            return F.interpolate(crop.unsqueeze(0), size=(zoom_out_size, zoom_out_size),
                                mode='bilinear', align_corners=False).squeeze(0)

        def add_border(img, color=(1,0,0), width=3):
            out = img.clone()
            out[0,:width,:]=color[0]; out[1,:width,:]=color[1]; out[2,:width,:]=color[2]
            out[0,-width:,:]=color[0]; out[1,-width:,:]=color[1]; out[2,-width:,:]=color[2]
            out[0,:,:width]=color[0]; out[1,:,:width]=color[1]; out[2,:,:width]=color[2]
            out[0,:,-width:]=color[0]; out[1,:,-width:]=color[1]; out[2,:,-width:]=color[2]
            return out

        # Main with rect
        gt_r = draw_rect(gt, region)
        tcas_r = draw_rect(tcas_img, region)
        fac_r = draw_rect(fac_img, region)

        # Zooms with border
        gt_z = add_border(crop_zoom(gt, region))
        tcas_z = add_border(crop_zoom(tcas_img, region))
        fac_z = add_border(crop_zoom(fac_img, region))

        # Pad zoom to match main height
        main_h = gt_r.shape[1]
        pad_top = (main_h - zoom_out_size) // 2
        pad_bot = main_h - zoom_out_size - pad_top
        gt_z = F.pad(gt_z, (0, 0, pad_top, pad_bot), value=1.0)
        tcas_z = F.pad(tcas_z, (0, 0, pad_top, pad_bot), value=1.0)
        fac_z = F.pad(fac_z, (0, 0, pad_top, pad_bot), value=1.0)

        # Separators
        sep = torch.ones(3, main_h, 4)
        wide_sep = torch.ones(3, main_h, 10)

        # Row: GT | TCAS | FAC || GT_zoom | TCAS_zoom | FAC_zoom
        row = torch.cat([gt_r, sep, tcas_r, sep, fac_r, wide_sep,
                        gt_z, sep, tcas_z, sep, fac_z], dim=2)
        rows.append(row)

    if not rows:
        return

    # Pad rows to same width
    max_w = max(r.shape[2] for r in rows)
    padded_rows = []
    for r in rows:
        if r.shape[2] < max_w:
            r = F.pad(r, (0, max_w - r.shape[2]), value=1.0)
        padded_rows.append(r)

    h_sep = torch.ones(3, 6, max_w)
    final = []
    for i, r in enumerate(padded_rows):
        if i > 0:
            final.append(h_sep)
        final.append(r)
    grid = torch.cat(final, dim=1)

    # Save raw
    raw_path = os.path.join(output_dir, 'comparison_zoom_300_raw.png')
    save_image(grid, raw_path)

    # Add labels with PIL
    img_pil = Image.open(raw_path)
    W, H = img_pil.size
    header_h = 65
    new_img = Image.new('RGB', (W, H + header_h), color=(255, 255, 255))
    new_img.paste(img_pil, (0, header_h))

    draw = ImageDraw.Draw(new_img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
        font_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except:
        font = ImageFont.load_default()
        font_sm = font

    # Column widths
    main_w = gt_r.shape[2]
    zoom_w = zoom_out_size
    sep_px = 4
    wide_px = 10

    # Main labels
    labels_main = ['GT', 'TCAS', 'Full FAC']
    x_mains = [0, main_w + sep_px, 2*(main_w + sep_px)]
    for lbl, x in zip(labels_main, x_mains):
        bbox = draw.textbbox((0,0), lbl, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (main_w - tw)//2, 10), lbl, fill=(0,0,0), font=font)

    # Zoom labels
    zoom_start = 3*(main_w + sep_px) + wide_px - sep_px
    labels_zoom = ['GT zoom', 'TCAS zoom', 'FAC zoom']
    x_zooms = [zoom_start, zoom_start + zoom_w + sep_px, zoom_start + 2*(zoom_w + sep_px)]
    for lbl, x in zip(labels_zoom, x_zooms):
        bbox = draw.textbbox((0,0), lbl, font=font_sm)
        tw = bbox[2] - bbox[0]
        draw.text((x + (zoom_w - tw)//2, 35), lbl, fill=(180,0,0), font=font_sm)

    final_path = os.path.join(output_dir, 'comparison_zoom_300.png')
    new_img.save(final_path, quality=95)
    print(f"  Saved figure: {final_path} ({new_img.size[0]}x{new_img.size[1]})")


def main():
    parser = argparse.ArgumentParser(description='FAC 300-Object Ablation')
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--fac_checkpoint', type=str, default=None)
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--output_dir', type=str, default='mvpoutput/fac_ablation_300_v1')
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()
    run_eval(args)


if __name__ == '__main__':
    main()
