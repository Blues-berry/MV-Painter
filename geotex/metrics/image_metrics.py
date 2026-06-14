"""
Consolidated image quality metrics: PSNR, SSIM, LPIPS.

Single authoritative implementation replacing duplicates in:
- geotex/metrics.py (compute_psnr, compute_ssim)
- geotex/eval.py (compute_lpips)
- geotex/eval_scale_sweep_v2.py (compute_lpips)
- geotex/eval_scale_inline.py (compute_lpips)
- geotex/audit_bg_crop.py (compute_lpips_safe)
"""
import torch
import torch.nn.functional as F

_lpips_fn = None


def compute_psnr(pred, target, mask=None):
    """PSNR in [0,1] range. Returns 100.0 for near-identical images.

    Args:
        pred: Predicted image tensor [B, C, H, W] in [0, 1]
        target: Target image tensor [B, C, H, W] in [0, 1]
        mask: Optional foreground mask [B, 1, H, W] or [B, C, H, W]

    Returns:
        PSNR value (float). Returns 0.0 for empty mask.
    """
    if mask is not None:
        if mask.shape[1] == 1 and pred.shape[1] > 1:
            mask = mask.expand_as(pred)
        fg = mask > 0.5
        if fg.sum() == 0:
            return 0.0
        mse = ((pred[fg] - target[fg]) ** 2).mean()
    else:
        mse = ((pred - target) ** 2).mean()
    if mse < 1e-10:
        return 100.0
    return 10 * torch.log10(1.0 / mse).item()


def compute_ssim(pred, target, mask=None):
    """SSIM with optional foreground mask. Returns value in [0,1].

    Uses 3x3 window with standard SSIM constants (C1=0.01^2, C2=0.03^2).
    SSIM map is clamped to [0,1] before averaging.

    Args:
        pred: Predicted image tensor [B, C, H, W] in [0, 1]
        target: Target image tensor [B, C, H, W] in [0, 1]
        mask: Optional foreground mask [B, 1, H, W]

    Returns:
        SSIM value (float). Returns 0.0 for empty mask.
    """
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)
    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))
    ssim_map = ssim_map.clamp(0, 1)
    if mask is not None:
        mask_d = F.max_pool2d(mask[:, :1], 3, 1, 1)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return 0.0
        return (ssim_map[:, :1] * mask_d)[fg].mean().item()
    return ssim_map.mean().item()


def compute_ssim_loss(pred, target, mask=None):
    """SSIM loss (1 - SSIM) for training.

    Args:
        pred: Predicted image tensor [B, C, H, W]
        target: Target image tensor [B, C, H, W]
        mask: Optional foreground mask [B, 1, H, W]

    Returns:
        SSIM loss tensor (not detached).
    """
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)
    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))
    if mask is not None:
        mask_d = F.max_pool2d(mask, 3, 1, 1)
        mask_d = mask_d.expand_as(ssim_map)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return torch.tensor(0.0, device=pred.device)
        return 1.0 - (ssim_map * mask_d)[fg].mean()
    return 1.0 - ssim_map.mean()


def get_lpips_fn(device):
    """Get or create LPIPS model (singleton pattern).

    Args:
        device: Device to load model on.

    Returns:
        LPIPS model or None if lpips not installed.
    """
    global _lpips_fn
    if _lpips_fn is None:
        try:
            import lpips
            _lpips_fn = lpips.LPIPS(net='alex').to(device).eval()
        except ImportError:
            return None
    return _lpips_fn


def compute_lpips(pred, target, mask=None, lpips_fn=None, device=None):
    """Compute LPIPS distance. Input range [0,1], internally converted to [-1,1].

    Args:
        pred: Predicted image tensor [B, C, H, W] in [0, 1]
        target: Target image tensor [B, C, H, W] in [0, 1]
        mask: Optional foreground mask [B, 1, H, W]
        lpips_fn: Pre-loaded LPIPS model (optional, will create if None)
        device: Device for LPIPS model (used only if lpips_fn is None)

    Returns:
        LPIPS value (float) or None if LPIPS not available.
    """
    if lpips_fn is None:
        if device is None:
            device = pred.device
        lpips_fn = get_lpips_fn(device)
    if lpips_fn is None:
        return None
    # LPIPS expects [-1, 1]
    p = pred * 2 - 1
    t = target * 2 - 1
    if mask is not None:
        m = mask[:, :1]
        if m.shape[2:] != p.shape[2:]:
            m = F.interpolate(m, size=p.shape[2:], mode='bilinear', align_corners=False)
        p = p * m
        t = t * m
    with torch.no_grad():
        return lpips_fn(p, t).item()


# ──────────────────────────────────────────────────────────────────────
# Latent / image scaling utilities (from original metrics.py)
# ──────────────────────────────────────────────────────────────────────

def scale_latents(latents):
    """Scale latents for training: (latents - 0.22) * 0.75."""
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    """Unscale latents after inference: latents / 0.75 + 0.22."""
    return latents / 0.75 + 0.22


def unscale_image(image):
    """Unscale decoded image: image / 0.5 * 0.8."""
    return image / 0.5 * 0.8
