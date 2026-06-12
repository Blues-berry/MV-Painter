"""
GeoTex-Adapter consolidated metrics package.

Single authoritative implementation of all metric functions.
Replaces duplicated code across eval scripts.
"""
from .image_metrics import compute_psnr, compute_ssim, compute_ssim_loss, compute_lpips, get_lpips_fn
from .mask_ops import morph_mask, compute_edge_mask
from .crop_ops import fg_bbox_crop, normalize_background
from .region_metrics import compute_all_metrics

__all__ = [
    'compute_psnr', 'compute_ssim', 'compute_ssim_loss', 'compute_lpips', 'get_lpips_fn',
    'morph_mask', 'compute_edge_mask',
    'fg_bbox_crop', 'normalize_background',
    'compute_all_metrics',
]
