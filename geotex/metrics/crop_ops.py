"""
Consolidated crop and background operations.

Single authoritative implementation replacing duplicates in:
- geotex/eval_scale_sweep_v2.py (fg_bbox_crop, normalize_background)
- geotex/eval_scale_inline.py (fg_crop, normalize_bg)
"""
import torch


def fg_bbox_crop(image, mask, padding=0.1):
    """Crop image to foreground bounding box with padding.

    Args:
        image: Image tensor [B, C, H, W]
        mask: Foreground mask tensor [B, 1, H, W]
        padding: Fraction of bbox size to add as padding (default: 0.1)

    Returns:
        Tuple of (cropped_image, cropped_mask). Returns original if no foreground.
    """
    fg = mask[0, 0] > 0.5
    if fg.sum() == 0:
        return image, mask
    rows = torch.any(fg, dim=1)
    cols = torch.any(fg, dim=0)
    rmin, rmax = torch.where(rows)[0][[0, -1]]
    cmin, cmax = torch.where(cols)[0][[0, -1]]
    H, W = fg.shape
    ph = int((rmax - rmin).item() * padding)
    pw = int((cmax - cmin).item() * padding)
    rmin, rmax = max(0, rmin - ph), min(H - 1, rmax + ph)
    cmin, cmax = max(0, cmin - pw), min(W - 1, cmax + pw)
    rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
    return image[:, :, rmin:rmax + 1, cmin:cmax + 1], mask[:, :, rmin:rmax + 1, cmin:cmax + 1]


def normalize_background(image, mask, bg_value=1.0):
    """Set background pixels to a constant value.

    Args:
        image: Image tensor [B, C, H, W]
        mask: Foreground mask tensor [B, 1, H, W]
        bg_value: Value to set background pixels to (default: 1.0 = white)

    Returns:
        Image tensor with background normalized.
    """
    bg = (mask < 0.5).expand_as(image)
    result = image.clone()
    result[bg] = bg_value
    return result
