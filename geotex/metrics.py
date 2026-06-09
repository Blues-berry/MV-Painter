"""Shared metrics and loss utilities for GeoTex-Adapter."""
import torch
import torch.nn.functional as F


def compute_psnr(pred, target, mask=None):
    """PSNR in [0,1] range. Returns 100.0 for near-identical images."""
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
    """SSIM with optional foreground mask. Returns value in [0,1]."""
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)
    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))
    if mask is not None:
        mask_d = F.max_pool2d(mask[:, :1], 3, 1, 1)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return 0.0
        return (ssim_map[:, :1] * mask_d)[fg].mean().item()
    return ssim_map.mean().item()


def compute_ssim_loss(pred, target, mask=None):
    """SSIM loss (1 - SSIM) for training."""
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


def compute_edge_mask(depth_or_normal, threshold=0.1):
    """Sobel edge detection on depth or normal map."""
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


def scale_latents(latents):
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def unscale_image(image):
    return image / 0.5 * 0.8
