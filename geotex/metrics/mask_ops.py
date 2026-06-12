"""
Consolidated mask operations: morphological ops, edge detection.

Single authoritative implementation replacing duplicates in:
- geotex/metrics.py (compute_edge_mask)
- geotex/eval_scale_sweep_v2.py (morph_mask)
- geotex/eval_scale_inline.py (morph)
- geotex/audit_mask_sensitivity.py (erode_mask, dilate_mask)
"""
import torch
import torch.nn.functional as F


def morph_mask(mask, kernel_size, op='erode'):
    """Apply morphological erosion or dilation to a binary mask.

    Args:
        mask: Binary mask tensor [B, 1, H, W] with values in [0, 1]
        kernel_size: Size of the morphological kernel (must be odd)
        op: 'erode' or 'dilate'

    Returns:
        Processed mask tensor [B, 1, H, W] with values in {0, 1}
    """
    if kernel_size <= 0:
        return mask
    padding = kernel_size // 2
    kernel = torch.ones(1, 1, kernel_size, kernel_size, device=mask.device)
    conv = F.conv2d(mask, kernel, padding=padding)
    if op == 'erode':
        return (conv >= kernel_size * kernel_size).float()
    return (conv > 0).float()


def compute_edge_mask(depth_or_normal, threshold=0.1):
    """Sobel edge detection on depth or normal map.

    Computes gradient magnitude using Sobel operators, normalizes to [0,1],
    then thresholds to produce a binary edge mask.

    Args:
        depth_or_normal: Depth or normal map tensor [B, C, H, W]
            - If C=3, converted to grayscale by averaging
            - If C=1, used directly
        threshold: Edge threshold in [0, 1] (default: 0.1)

    Returns:
        Binary edge mask tensor [B, 1, H, W] with values in {0, 1}
    """
    if depth_or_normal.shape[1] == 3:
        gray = depth_or_normal.mean(dim=1, keepdim=True)
    else:
        gray = depth_or_normal
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    grad_x = F.conv2d(gray, sobel_x, padding=1)
    grad_y = F.conv2d(gray, sobel_y, padding=1)
    grad_mag = torch.sqrt(grad_x ** 2 + grad_y ** 2 + 1e-8)
    grad_mag = grad_mag / (grad_mag.max() + 1e-8)
    return (grad_mag > threshold).float()
