"""GeoTex-Adapter audit: step0 sanity, data leakage, fairness, PSNR range."""
import os
import sys
import json
import argparse
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2

from metrics import compute_psnr, compute_ssim
from eval import load_model, generate_images


def check_step0(config_path, device, num_objects=3, num_steps=50):
    """Verify zero-init adapters produce identical output to original."""
    print("=" * 60)
    print("STEP 0 SANITY CHECK")
    print("=" * 60)

    model = load_model(config_path, checkpoint_path=None, device=device)
    config = OmegaConf.load(config_path)
    dataset = instantiate_from_config(config.data.params.validation)

    # Verify zero-init
    issues = []
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            w_max = module.adapter.output_proj.weight.abs().max().item()
            if w_max > 1e-8:
                issues.append(f"{name}: w_max={w_max:.2e}")
    print(f"  Zero-init: {'✓ PASS' if not issues else '✗ FAIL: ' + str(issues)}")

    # Generate and compare
    results = []
    for obj_idx in range(min(num_objects, len(dataset))):
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
                 for k, v in dataset[obj_idx].items()}
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        cond_imgs = batch['cond_imgs'].to(device)
        cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
        B = cond_imgs.shape[0]

        global_embeds = batch['global_embeds'].to(device, dtype=torch.float16).view(B, 1, -1)
        ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(torch.float16)
        uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=torch.float16)
        prompt_embeds = uc_text_emb + global_embeds * ramp
        cond_latents = model.encode_condition_image(cond_imgs).to(torch.float16)
        added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
        added_cond_kwargs = {k: v.to(device, dtype=torch.float16) if isinstance(v, torch.Tensor) else v
                             for k, v in added_cond_kwargs.items()}

        # Prepare geo
        cond_imgs_t, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            model.prepare_batch_data(batch, device=device)
        geo_clean = geo_input.float().clamp(0, 1)
        geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)

        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(42)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)

        torch.manual_seed(42)
        image_orig = generate_images(model, batch, device, torch.float16, None, num_steps, shared_latents)
        torch.manual_seed(42)
        image_zero = generate_images(model, batch, device, torch.float16, geo_feats, num_steps, shared_latents)

        max_diff = (image_orig - image_zero).abs().max().item()
        passed = max_diff < 1e-4
        print(f"  Object {obj_idx}: max_diff={max_diff:.2e} {'✓' if passed else '✗'}")
        results.append({'object_idx': obj_idx, 'max_diff': max_diff, 'passed': passed})

    all_passed = all(r['passed'] for r in results) and not issues
    print(f"\n  Overall: {'✓ PASS' if all_passed else '✗ FAIL'}")
    return {'step0': {'passed': all_passed, 'details': results}}


def check_data_leakage(config_path):
    """Check for train/test overlap."""
    print("=" * 60)
    print("DATA LEAKAGE AUDIT")
    print("=" * 60)

    config = OmegaConf.load(config_path)
    data_cfg = config.data.params

    # Load object lists
    train_list_file = os.path.join(
        data_cfg.train.params.root_dir_list[0],
        data_cfg.train.params.object_list_file
    )
    test_list_file = os.path.join(
        data_cfg.validation.params.root_dir_list[0],
        data_cfg.validation.params.object_list_file
    )

    with open(train_list_file) as f:
        train_objects = set(line.strip() for line in f if line.strip())
    with open(test_list_file) as f:
        test_objects = set(line.strip() for line in f if line.strip())

    overlap = train_objects & test_objects
    print(f"  Train: {len(train_objects)} objects from {train_list_file}")
    print(f"  Test:  {len(test_objects)} objects from {test_list_file}")
    print(f"  Overlap: {len(overlap)} {'✓ PASS' if len(overlap) == 0 else '✗ FAIL'}")

    if overlap:
        print(f"  Leaked objects: {list(overlap)[:10]}...")

    return {'leakage': {
        'passed': len(overlap) == 0,
        'train_count': len(train_objects),
        'test_count': len(test_objects),
        'overlap_count': len(overlap),
        'overlap_objects': list(overlap),
    }}


def check_psnr_range(config_path, device, num_objects=3):
    """Verify PSNR formula and image ranges."""
    print("=" * 60)
    print("PSNR RANGE CHECK")
    print("=" * 60)

    # Test 1: identical images → inf
    img = torch.rand(1, 3, 64, 64)
    psnr_same = compute_psnr(img, img)
    print(f"  Identical images: PSNR={psnr_same:.1f} {'✓' if psnr_same > 99 else '✗'}")

    # Test 2: known noise → expected PSNR
    noise = torch.randn_like(img) * 0.1
    img_noisy = (img + noise).clamp(0, 1)
    mse = ((img - img_noisy) ** 2).mean()
    expected_psnr = 10 * torch.log10(1.0 / mse).item()
    actual_psnr = compute_psnr(img_noisy, img)
    print(f"  Noisy images: PSNR={actual_psnr:.2f}, expected={expected_psnr:.2f} "
          f"{'✓' if abs(actual_psnr - expected_psnr) < 0.1 else '✗'}")

    # Test 3: check actual image ranges from eval
    model = load_model(config_path, checkpoint_path=None, device=device)
    config = OmegaConf.load(config_path)
    dataset = instantiate_from_config(config.data.params.validation)

    batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v
             for k, v in dataset[0].items()}
    for k in batch:
        if hasattr(batch[k], 'to'):
            batch[k] = batch[k].to(device)

    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        model.prepare_batch_data(batch, device=device)

    print(f"\n  Target images: shape={target_imgs.shape}, range=[{target_imgs.min():.3f}, {target_imgs.max():.3f}], "
          f"mean={target_imgs.mean():.3f}")
    print(f"  Mask: shape={mask.shape}, range=[{mask.min():.3f}, {mask.max():.3f}], "
          f"fg_ratio={mask.mean():.3f}")

    return {'psnr_range': {
        'identical_psnr': psnr_same,
        'noisy_psnr_match': abs(actual_psnr - expected_psnr) < 0.1,
        'target_range': [target_imgs.min().item(), target_imgs.max().item()],
        'mask_fg_ratio': mask.mean().item(),
    }}


def main():
    parser = argparse.ArgumentParser(description="GeoTex-Adapter Audit")
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--check', choices=['step0', 'leakage', 'psnr_range', 'all'], default='all')
    parser.add_argument('--output_dir', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--num_objects', type=int, default=3)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex', 'audit')
    os.makedirs(args.output_dir, exist_ok=True)

    results = {}
    if args.check in ('step0', 'all'):
        results.update(check_step0(args.config, args.device, args.num_objects))
    if args.check in ('leakage', 'all'):
        results.update(check_data_leakage(args.config))
    if args.check in ('psnr_range', 'all'):
        results.update(check_psnr_range(args.config, args.device, args.num_objects))

    # Save results
    json_path = os.path.join(args.output_dir, 'audit_results.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {json_path}")

    # Overall verdict
    all_passed = all(v.get('passed', True) for v in results.values() if isinstance(v, dict))
    print(f"\n{'='*60}")
    print(f"OVERALL: {'✓ ALL CHECKS PASSED' if all_passed else '✗ SOME CHECKS FAILED'}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
