"""Mask sensitivity analysis: erode/dilate mask and recompute metrics.

Tests whether FG SSIM degradation is from mask boundary artifacts.

Usage:
    python geotex/audit_mask_sensitivity.py \
        --eval_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean \
        --device cuda:0
"""
import os
import sys
import csv
import json
import argparse
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
from metrics import compute_psnr, compute_ssim


def load_image(path, size=None):
    img = Image.open(path).convert('RGB')
    if size:
        img = img.resize((size, size), Image.BILINEAR)
    return transforms.ToTensor()(img).unsqueeze(0)


def load_mask(path, size=None):
    img = Image.open(path).convert('L')
    if size:
        img = img.resize((size, size), Image.BILINEAR)
    return transforms.ToTensor()(img).unsqueeze(0)


def erode_mask(mask, kernel_size):
    """Erode mask by kernel_size pixels."""
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    eroded = F.conv2d(mask, kernel, padding=padding)
    return (eroded >= kernel_size * kernel_size).float()


def dilate_mask(mask, kernel_size):
    """Dilate mask by kernel_size pixels."""
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    dilated = F.conv2d(mask, kernel, padding=padding)
    return (dilated > 0).float()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval_dir', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--num_objects', type=int, default=300)
    args = parser.parse_args()

    device = torch.device(args.device)
    vis_dir = os.path.join(args.eval_dir, 'visualizations')
    out_dir = os.path.join(args.eval_dir, 'mask_sensitivity')
    os.makedirs(out_dir, exist_ok=True)

    # Erosion/dilation sizes
    sizes = [0, 3, 5, 10]

    results = []
    num = min(args.num_objects, 300)

    for obj_idx in range(num):
        prefix = f"obj_{obj_idx:03d}"
        gt_path = os.path.join(vis_dir, f'{prefix}_gt.png')
        orig_path = os.path.join(vis_dir, f'{prefix}_original.png')
        adapter_path = os.path.join(vis_dir, f'{prefix}_adapter.png')
        mask_path = os.path.join(vis_dir, f'{prefix}_mask.png')
        edge_path = os.path.join(vis_dir, f'{prefix}_edge_mask.png')

        if not all(os.path.exists(p) for p in [gt_path, orig_path, adapter_path, mask_path]):
            continue

        gt = load_image(gt_path).to(device)
        orig = load_image(orig_path).to(device)
        adapter = load_image(adapter_path).to(device)
        mask = load_mask(mask_path).to(device)
        edge_mask = load_mask(edge_path).to(device)

        # Ensure sizes match
        H, W = gt.shape[2], gt.shape[3]
        for t in [orig, adapter, mask, edge_mask]:
            if t.shape[2:] != (H, W):
                t = F.interpolate(t, size=(H, W), mode='bilinear', align_corners=False)

        r = {'object_idx': obj_idx}

        for size in sizes:
            suffix = f'e{size}' if size > 0 else 'base'
            if size > 0:
                m_eroded = erode_mask(mask, size * 2 + 1)
            else:
                m_eroded = mask

            # FG metrics with eroded mask
            fg_psnr_orig = compute_psnr(orig, gt, m_eroded)
            fg_psnr_adapter = compute_psnr(adapter, gt, m_eroded)
            fg_ssim_orig = compute_ssim(orig, gt, m_eroded)
            fg_ssim_adapter = compute_ssim(adapter, gt, m_eroded)

            r[f'fg_psnr_orig_{suffix}'] = fg_psnr_orig
            r[f'fg_psnr_adapter_{suffix}'] = fg_psnr_adapter
            r[f'fg_ssim_orig_{suffix}'] = fg_ssim_orig
            r[f'fg_ssim_adapter_{suffix}'] = fg_ssim_adapter
            r[f'fg_psnr_delta_{suffix}'] = fg_psnr_adapter - fg_psnr_orig
            r[f'fg_ssim_delta_{suffix}'] = fg_ssim_adapter - fg_ssim_orig

            # Edge metrics with eroded mask + edge mask
            combined = m_eroded * edge_mask
            edge_ssim_orig = compute_ssim(orig, gt, combined)
            edge_ssim_adapter = compute_ssim(adapter, gt, combined)
            r[f'edge_ssim_orig_{suffix}'] = edge_ssim_orig
            r[f'edge_ssim_adapter_{suffix}'] = edge_ssim_adapter
            r[f'edge_ssim_delta_{suffix}'] = edge_ssim_adapter - edge_ssim_orig

            # Non-edge FG
            non_edge_fg = m_eroded * (1 - edge_mask)
            nef_ssim_orig = compute_ssim(orig, gt, non_edge_fg)
            nef_ssim_adapter = compute_ssim(adapter, gt, non_edge_fg)
            r[f'nef_ssim_orig_{suffix}'] = nef_ssim_orig
            r[f'nef_ssim_adapter_{suffix}'] = nef_ssim_adapter
            r[f'nef_ssim_delta_{suffix}'] = nef_ssim_adapter - nef_ssim_orig

            # Mask area ratio
            r[f'fg_area_{suffix}'] = float(m_eroded.sum() / m_eroded.numel())

        results.append(r)

        if obj_idx % 50 == 0:
            print(f"  Object {obj_idx}: fg_ssim_delta base={r['fg_ssim_delta_base']:+.4f} e5={r['fg_ssim_delta_e5']:+.4f}")

    # Save CSV
    fieldnames = list(results[0].keys())
    with open(os.path.join(out_dir, 'mask_sensitivity_metrics.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    summary = {}
    for suffix in ['base', 'e3', 'e5', 'e10']:
        for metric in ['fg_psnr_delta', 'fg_ssim_delta', 'edge_ssim_delta', 'nef_ssim_delta']:
            key = f'{metric}_{suffix}'
            vals = [r[key] for r in results if key in r and r[key] is not None]
            if vals:
                arr = np.array(vals)
                pos = int(np.sum(arr > 0))
                summary[key] = {
                    'mean': float(arr.mean()),
                    'std': float(arr.std()),
                    'positive': pos,
                    'total': len(arr),
                }
        # Area ratio
        area_key = f'fg_area_{suffix}'
        area_vals = [r[area_key] for r in results if area_key in r]
        if area_vals:
            summary[area_key] = {'mean': float(np.mean(area_vals))}

    with open(os.path.join(out_dir, 'mask_sensitivity_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print(f"\n{'='*80}")
    print(f"MASK SENSITIVITY ANALYSIS ({len(results)} objects)")
    print(f"{'='*80}")
    print(f"\n{'Mask':>8} {'FG PSNR Δ':>12} {'FG SSIM Δ':>12} {'Edge SSIM Δ':>13} {'NEF SSIM Δ':>12} {'FG Area':>10}")
    print(f"{'':>8} {'':>12} {'':>12} {'':>13} {'':>12} {'':>10}")
    for suffix in ['base', 'e3', 'e5', 'e10']:
        label = 'original' if suffix == 'base' else f'erode-{suffix[1:]}'
        fp = summary.get(f'fg_psnr_delta_{suffix}', {})
        fs = summary.get(f'fg_ssim_delta_{suffix}', {})
        es = summary.get(f'edge_ssim_delta_{suffix}', {})
        ns = summary.get(f'nef_ssim_delta_{suffix}', {})
        fa = summary.get(f'fg_area_{suffix}', {})
        print(f"{label:>8} {fp.get('mean',0):+12.4f} [{fp.get('positive',0)}/{fp.get('total',0)}]"
              f" {fs.get('mean',0):+12.4f} [{fs.get('positive',0)}/{fs.get('total',0)}]"
              f" {es.get('mean',0):+13.4f} [{es.get('positive',0)}/{es.get('total',0)}]"
              f" {ns.get('mean',0):+12.4f} [{ns.get('positive',0)}/{ns.get('total',0)}]"
              f" {fa.get('mean',0):10.4f}")

    print(f"\nOutputs: {out_dir}")


if __name__ == '__main__':
    main()
