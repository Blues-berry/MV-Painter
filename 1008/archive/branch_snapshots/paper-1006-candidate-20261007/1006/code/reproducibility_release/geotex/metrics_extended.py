"""Extended metrics for GeoTex exploration: texture flattening detection + shape analysis.

All functions expect tensors in [0,1] range, shape (B, C, H, W).
Returns float values (scalar per batch element averaged).
"""
import torch
import torch.nn.functional as F
import numpy as np


def fg_rgb_std(pred, mask):
    """RGB standard deviation inside foreground. Higher = more texture."""
    if mask.shape[1] == 1:
        mask = mask.expand_as(pred)
    fg = mask > 0.5
    if fg.sum() == 0:
        return 0.0
    # Per-pixel RGB std, averaged over FG
    pixel_std = pred.std(dim=1, keepdim=True)  # (B, 1, H, W)
    return pixel_std[fg[:, :1]].mean().item()


def fg_gradient_magnitude(pred, mask):
    """Mean gradient magnitude inside FG. Higher = more detail."""
    gray = pred.mean(dim=1, keepdim=True)  # (B, 1, H, W)
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    gx = F.conv2d(gray, sobel_x, padding=1)
    gy = F.conv2d(gray, sobel_y, padding=1)
    grad = torch.sqrt(gx**2 + gy**2 + 1e-8)
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    fg = m > 0.5
    if fg.sum() == 0:
        return 0.0
    return grad[fg].mean().item()


def fg_laplacian_variance(pred, mask):
    """Variance of Laplacian inside FG. Higher = sharper (more texture)."""
    gray = pred.mean(dim=1, keepdim=True)
    lap_kernel = torch.tensor([[0, 1, 0], [1, -4, 1], [0, 1, 0]],
                              dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    lap = F.conv2d(gray, lap_kernel, padding=1)
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    fg = m > 0.5
    if fg.sum() == 0:
        return 0.0
    return lap[fg].var().item()


def fg_color_entropy(pred, mask, bins=64):
    """Color entropy inside FG. Higher = more diverse colors."""
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    fg = m > 0.5
    if fg.sum() == 0:
        return 0.0
    # Get FG pixels (convert to float32 for histc)
    fg_pixels = pred.float().permute(0, 2, 3, 1)[m.squeeze(1) > 0.5]  # (N, 3)
    if fg_pixels.shape[0] < 10:
        return 0.0
    # Histogram per channel
    entropy = 0.0
    for c in range(fg_pixels.shape[1]):
        hist = torch.histc(fg_pixels[:, c], bins=bins, min=0, max=1)
        hist = hist / (hist.sum() + 1e-8)
        hist = hist[hist > 0]
        entropy += -(hist * torch.log2(hist + 1e-8)).sum().item()
    return entropy / fg_pixels.shape[1]  # average across channels


def fg_hf_energy(pred, mask):
    """High-frequency energy ratio inside FG. Higher = more fine detail.

    Uses full-image FFT with mask weighting for robustness.
    """
    gray = pred.mean(dim=1, keepdim=True)  # (B, 1, H, W)
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    fg = m > 0.5
    if fg.sum() == 0:
        return 0.0
    # Apply mask to focus on FG
    masked = gray * m
    fft = torch.fft.fft2(masked)
    fft_shift = torch.fft.fftshift(fft)
    magnitude = torch.abs(fft_shift)
    H, W = magnitude.shape[2], magnitude.shape[3]
    # High-freq = outside center quarter
    cy, cx = H // 2, W // 2
    qh, qw = max(H // 4, 1), max(W // 4, 1)
    total = magnitude.sum()
    low = magnitude[:, :, max(cy-qh,0):cy+qh, max(cx-qw,0):cx+qw].sum()
    hf = total - low
    return (hf / (total + 1e-8)).item()


def edge_fscore(pred, target, mask=None, threshold=0.1):
    """Edge F-score: precision/recall of Sobel edges."""
    def to_gray(img):
        return img.mean(dim=1, keepdim=True)

    def get_edges(img):
        gray = to_gray(img)
        sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                               dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
        sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                               dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
        gx = F.conv2d(gray, sobel_x, padding=1)
        gy = F.conv2d(gray, sobel_y, padding=1)
        grad = torch.sqrt(gx**2 + gy**2 + 1e-8)
        grad = grad / (grad.max() + 1e-8)
        return (grad > threshold).float()

    pred_edges = get_edges(pred)
    gt_edges = get_edges(target)

    if mask is not None:
        m = mask[:, :1] if mask.shape[1] > 1 else mask
        pred_edges = pred_edges * m
        gt_edges = gt_edges * m

    tp = (pred_edges * gt_edges).sum()
    fp = (pred_edges * (1 - gt_edges)).sum()
    fn = ((1 - pred_edges) * gt_edges).sum()

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    fscore = 2 * precision * recall / (precision + recall + 1e-8)
    return fscore.item()


def fg_mask_correlation(pred, mask):
    """Correlation between pred brightness and GT mask. Higher = better FG/BG separation."""
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    pred_gray = pred.mean(dim=1, keepdim=True)
    fg = m > 0.5
    bg = m <= 0.5
    if fg.sum() < 1 or bg.sum() < 1:
        return 0.0
    fg_mean = pred_gray[fg].mean()
    bg_mean = pred_gray[bg].mean()
    # Contrast: FG should be darker (non-white) than BG (white)
    # Positive = FG darker than BG (good for our white-bg setup)
    return (bg_mean - fg_mean).item()


def fg_brightness_std(pred, mask):
    """Std of FG brightness. Higher = more texture variation."""
    m = mask[:, :1] if mask.shape[1] > 1 else mask
    pred_gray = pred.mean(dim=1, keepdim=True)
    fg = m > 0.5
    if fg.sum() < 10:
        return 0.0
    return pred_gray[fg].std().item()


def compute_all_extended(pred, target, mask, edge_mask=None):
    """Compute all extended metrics for a single (pred, target, mask) triple.

    Returns dict with all metric values.
    """
    r = {}

    # Shape metrics
    r['fg_mask_corr'] = fg_mask_correlation(pred, mask)
    r['edge_fscore'] = edge_fscore(pred, target, mask)

    # Texture metrics
    r['fg_rgb_std'] = fg_rgb_std(pred, mask)
    r['fg_grad_mag'] = fg_gradient_magnitude(pred, mask)
    r['fg_lap_var'] = fg_laplacian_variance(pred, mask)
    r['fg_color_entropy'] = fg_color_entropy(pred, mask)
    r['fg_hf_energy'] = fg_hf_energy(pred, mask)
    r['fg_brightness_std'] = fg_brightness_std(pred, mask)

    # Also compute GT texture metrics for reference
    r['gt_fg_rgb_std'] = fg_rgb_std(target, mask)
    r['gt_fg_grad_mag'] = fg_gradient_magnitude(target, mask)
    r['gt_fg_lap_var'] = fg_laplacian_variance(target, mask)
    r['gt_fg_hf_energy'] = fg_hf_energy(target, mask)

    return r
