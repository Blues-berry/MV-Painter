"""
Consolidated region metric computation.

Single authoritative implementation replacing duplicates in:
- geotex/eval_scale_sweep_v2.py (compute_metrics)
- geotex/eval_scale_inline.py (metrics)
"""
from .image_metrics import compute_psnr, compute_ssim, compute_lpips
from .mask_ops import morph_mask
from .crop_ops import fg_bbox_crop, normalize_background


def compute_all_metrics(pred, target, mask, edge_mask, lpips_fn=None, device=None):
    """Compute all region metrics for a single image pair.

    Computes PSNR, SSIM, LPIPS for multiple regions:
    - full: No mask
    - fg: Foreground (mask > 0.5)
    - bg: Background (1 - mask)
    - edge: Edge regions (edge_mask)
    - nef: Non-edge foreground (mask * (1 - edge_mask))
    - bgwhite: Background normalized to white
    - crop: Foreground bounding box crop
    - fg_e3/e5/e10: Eroded foreground masks
    - fg_d3/d5/d10: Dilated foreground masks

    Args:
        pred: Predicted image [B, C, H, W] in [0, 1]
        target: Target image [B, C, H, W] in [0, 1]
        mask: Foreground mask [B, 1, H, W]
        edge_mask: Edge mask [B, 1, H, W]
        lpips_fn: Pre-loaded LPIPS model (optional)
        device: Device for LPIPS (optional)

    Returns:
        Dict with keys like 'full_psnr', 'fg_ssim', 'edge_lpips', etc.
    """
    r = {}

    # Full image
    r['full_psnr'] = compute_psnr(pred, target)
    r['full_ssim'] = compute_ssim(pred, target)
    r['full_lpips'] = compute_lpips(pred, target, lpips_fn=lpips_fn, device=device)

    # Foreground
    r['fg_psnr'] = compute_psnr(pred, target, mask)
    r['fg_ssim'] = compute_ssim(pred, target, mask)
    r['fg_lpips'] = compute_lpips(pred, target, mask, lpips_fn=lpips_fn, device=device)

    # Background
    bg_mask = 1.0 - mask
    r['bg_psnr'] = compute_psnr(pred, target, bg_mask)

    # Edge
    r['edge_psnr'] = compute_psnr(pred, target, edge_mask)
    r['edge_ssim'] = compute_ssim(pred, target, edge_mask)

    # Non-edge foreground
    nef = mask * (1 - edge_mask)
    r['nef_ssim'] = compute_ssim(pred, target, nef)

    # BG-normalized (white background)
    pred_w = normalize_background(pred, mask, 1.0)
    target_w = normalize_background(target, mask, 1.0)
    r['bgwhite_psnr'] = compute_psnr(pred_w, target_w)
    r['bgwhite_ssim'] = compute_ssim(pred_w, target_w)
    r['bgwhite_lpips'] = compute_lpips(pred_w, target_w, lpips_fn=lpips_fn, device=device)

    # Crop
    pred_crop, _ = fg_bbox_crop(pred, mask, 0.1)
    target_crop, _ = fg_bbox_crop(target, mask, 0.1)
    r['crop_psnr'] = compute_psnr(pred_crop, target_crop)
    r['crop_ssim'] = compute_ssim(pred_crop, target_crop)
    r['crop_lpips'] = compute_lpips(pred_crop, target_crop, lpips_fn=lpips_fn, device=device)
    r['crop_area'] = float(pred_crop.numel() / pred.numel())

    # Mask sensitivity: erosion
    for s in [3, 5, 10]:
        m = morph_mask(mask, s * 2 + 1, 'erode')
        r[f'fg_psnr_e{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_e{s}'] = compute_ssim(pred, target, m)

    # Mask sensitivity: dilation
    for s in [3, 5, 10]:
        m = morph_mask(mask, s * 2 + 1, 'dilate')
        r[f'fg_psnr_d{s}'] = compute_psnr(pred, target, m)
        r[f'fg_ssim_d{s}'] = compute_ssim(pred, target, m)

    return r
