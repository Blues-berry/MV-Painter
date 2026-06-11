"""Background normalization and foreground crop evaluation.

Loads GT/Original/Adapter images from visualizations, applies background
normalization and fg crop, recomputes metrics.

Usage:
    python geotex/audit_bg_crop.py \
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
from torchvision.transforms import v2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
from metrics import compute_psnr, compute_ssim


def load_image_as_tensor(path, size=None):
    """Load image as (1, C, H, W) tensor in [0, 1]."""
    img = Image.open(path).convert('RGB')
    if size:
        img = img.resize((size, size), Image.BILINEAR)
    t = transforms.ToTensor()(img).unsqueeze(0)
    return t


def load_mask_as_tensor(path, size=None):
    """Load mask image as (1, 1, H, W) tensor in [0, 1]."""
    img = Image.open(path).convert('L')
    if size:
        img = img.resize((size, size), Image.BILINEAR)
    t = transforms.ToTensor()(img).unsqueeze(0)
    return t


def normalize_background(image, mask, bg_value=1.0):
    """Set background to constant value. image: (1,C,H,W), mask: (1,1,H,W)."""
    bg = (mask < 0.5).expand_as(image)
    result = image.clone()
    result[bg] = bg_value
    return result


def fg_bbox_crop(image, mask, padding=0.1):
    """Crop to foreground bounding box with padding. Returns cropped image and mask."""
    fg = mask[0, 0] > 0.5
    if fg.sum() == 0:
        return image, mask
    rows = torch.any(fg, dim=1)
    cols = torch.any(fg, dim=0)
    rmin, rmax = torch.where(rows)[0][[0, -1]]
    cmin, cmax = torch.where(cols)[0][[0, -1]]
    H, W = fg.shape
    # Add padding
    ph = int((rmax - rmin).item() * padding)
    pw = int((cmax - cmin).item() * padding)
    rmin = max(0, rmin - ph)
    rmax = min(H - 1, rmax + ph)
    cmin = max(0, cmin - pw)
    cmax = min(W - 1, cmax + pw)
    # Crop
    rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
    cropped_img = image[:, :, rmin:rmax+1, cmin:cmax+1]
    cropped_mask = mask[:, :, rmin:rmax+1, cmin:cmax+1]
    return cropped_img, cropped_mask


def compute_lpips_safe(pred, target, device):
    """Compute LPIPS safely."""
    try:
        import lpips
        lpips_fn = lpips.LPIPS(net='alex').to(device).eval()
        p = pred * 2 - 1
        t = target * 2 - 1
        with torch.no_grad():
            return lpips_fn(p, t).item()
    except:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval_dir', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--num_objects', type=int, default=300)
    args = parser.parse_args()

    device = torch.device(args.device)
    vis_dir = os.path.join(args.eval_dir, 'visualizations')
    out_dir = os.path.join(args.eval_dir, 'bg_crop_audit')
    os.makedirs(out_dir, exist_ok=True)

    results = []
    num = min(args.num_objects, 300)

    for obj_idx in range(num):
        prefix = f"obj_{obj_idx:03d}"
        gt_path = os.path.join(vis_dir, f'{prefix}_gt.png')
        orig_path = os.path.join(vis_dir, f'{prefix}_original.png')
        adapter_path = os.path.join(vis_dir, f'{prefix}_adapter.png')
        mask_path = os.path.join(vis_dir, f'{prefix}_mask.png')

        if not all(os.path.exists(p) for p in [gt_path, orig_path, adapter_path, mask_path]):
            print(f"  Object {obj_idx}: missing files, skipping")
            continue

        gt = load_image_as_tensor(gt_path).to(device)
        orig = load_image_as_tensor(orig_path).to(device)
        adapter = load_image_as_tensor(adapter_path).to(device)
        mask = load_mask_as_tensor(mask_path).to(device)

        # Ensure all same size
        H, W = gt.shape[2], gt.shape[3]
        if orig.shape[2:] != gt.shape[2:]:
            orig = F.interpolate(orig, size=(H, W), mode='bilinear', align_corners=False)
        if adapter.shape[2:] != gt.shape[2:]:
            adapter = F.interpolate(adapter, size=(H, W), mode='bilinear', align_corners=False)
        if mask.shape[2:] != gt.shape[2:]:
            mask = F.interpolate(mask, size=(H, W), mode='bilinear', align_corners=False)

        r = {'object_idx': obj_idx}

        # A) Original metrics (as-is)
        r['orig_full_psnr'] = compute_psnr(orig, gt)
        r['orig_full_ssim'] = compute_ssim(orig, gt)
        r['adapter_full_psnr'] = compute_psnr(adapter, gt)
        r['adapter_full_ssim'] = compute_ssim(adapter, gt)

        # B) Background set to white
        gt_white = normalize_background(gt, mask, 1.0)
        orig_white = normalize_background(orig, mask, 1.0)
        adapter_white = normalize_background(adapter, mask, 1.0)
        r['orig_bgwhite_psnr'] = compute_psnr(orig_white, gt_white)
        r['orig_bgwhite_ssim'] = compute_ssim(orig_white, gt_white)
        r['adapter_bgwhite_psnr'] = compute_psnr(adapter_white, gt_white)
        r['adapter_bgwhite_ssim'] = compute_ssim(adapter_white, gt_white)

        # C) Background set to black
        gt_black = normalize_background(gt, mask, 0.0)
        orig_black = normalize_background(orig, mask, 0.0)
        adapter_black = normalize_background(adapter, mask, 0.0)
        r['orig_bgblack_psnr'] = compute_psnr(orig_black, gt_black)
        r['orig_bgblack_ssim'] = compute_ssim(orig_black, gt_black)
        r['adapter_bgblack_psnr'] = compute_psnr(adapter_black, gt_black)
        r['adapter_bgblack_ssim'] = compute_ssim(adapter_black, gt_black)

        # D) Foreground bbox crop
        gt_crop, mask_crop = fg_bbox_crop(gt, mask, padding=0.1)
        orig_crop, _ = fg_bbox_crop(orig, mask, padding=0.1)
        adapter_crop, _ = fg_bbox_crop(adapter, mask, padding=0.1)
        r['crop_area_ratio'] = float(gt_crop.numel() / gt.numel())
        r['orig_crop_psnr'] = compute_psnr(orig_crop, gt_crop)
        r['orig_crop_ssim'] = compute_ssim(orig_crop, gt_crop)
        r['adapter_crop_psnr'] = compute_psnr(adapter_crop, gt_crop)
        r['adapter_crop_ssim'] = compute_ssim(adapter_crop, gt_crop)

        # Deltas
        r['delta_full_psnr'] = r['adapter_full_psnr'] - r['orig_full_psnr']
        r['delta_full_ssim'] = r['adapter_full_ssim'] - r['orig_full_ssim']
        r['delta_bgwhite_psnr'] = r['adapter_bgwhite_psnr'] - r['orig_bgwhite_psnr']
        r['delta_bgwhite_ssim'] = r['adapter_bgwhite_ssim'] - r['orig_bgwhite_ssim']
        r['delta_bgblack_psnr'] = r['adapter_bgblack_psnr'] - r['orig_bgblack_psnr']
        r['delta_bgblack_ssim'] = r['adapter_bgblack_ssim'] - r['orig_bgblack_ssim']
        r['delta_crop_psnr'] = r['adapter_crop_psnr'] - r['orig_crop_psnr']
        r['delta_crop_ssim'] = r['adapter_crop_ssim'] - r['orig_crop_ssim']

        results.append(r)

        if obj_idx % 20 == 0:
            print(f"  Object {obj_idx}: delta_full_psnr={r['delta_full_psnr']:+.2f} "
                  f"delta_crop_psnr={r['delta_crop_psnr']:+.2f} "
                  f"delta_crop_ssim={r['delta_crop_ssim']:+.4f}")

    # Save CSV
    fieldnames = list(results[0].keys())
    csv_path = os.path.join(out_dir, 'bg_crop_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    summary = {}
    for key in ['delta_full_psnr', 'delta_full_ssim', 'delta_bgwhite_psnr', 'delta_bgwhite_ssim',
                'delta_bgblack_psnr', 'delta_bgblack_ssim', 'delta_crop_psnr', 'delta_crop_ssim']:
        vals = [r[key] for r in results if r[key] is not None]
        if vals:
            arr = np.array(vals)
            pos = np.sum(arr > 0) if 'ssim' in key else np.sum(arr > 0)
            summary[key] = {
                'mean': float(arr.mean()),
                'std': float(arr.std()),
                'median': float(np.median(arr)),
                'positive': int(pos),
                'total': len(arr),
            }

    with open(os.path.join(out_dir, 'bg_crop_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print(f"\n{'='*80}")
    print(f"BACKGROUND NORMALIZATION & CROP AUDIT ({len(results)} objects)")
    print(f"{'='*80}")
    for key, s in summary.items():
        print(f"  {key:25s}: mean={s['mean']:+.4f} [{s['positive']}/{s['total']} positive]")

    # Correlation: crop_area_ratio vs delta_crop_psnr
    if results:
        areas = [r['crop_area_ratio'] for r in results]
        deltas = [r['delta_crop_psnr'] for r in results]
        corr = np.corrcoef(areas, deltas)[0, 1]
        print(f"\n  Correlation (crop_area_ratio, delta_crop_psnr): {corr:.4f}")

    print(f"\nOutputs: {out_dir}")


if __name__ == '__main__':
    main()
