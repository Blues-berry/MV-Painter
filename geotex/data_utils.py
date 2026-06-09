"""Data loading and batch preparation utilities for GeoTex-Adapter."""
import torch
from torchvision.transforms import v2
from einops import rearrange


def prepare_batch(batch, img_size=256, device=None):
    """Prepare batch data including geometry information.

    Returns: cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask
    """
    if device is None:
        device = next(iter(batch.values())).device if hasattr(next(iter(batch.values())), 'device') else 'cpu'

    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, img_size, interpolation=3, antialias=True).clamp(0, 1)

    target_imgs = batch['target_imgs']
    target_imgs = v2.functional.resize(target_imgs, img_size, interpolation=3, antialias=True).clamp(0, 1)
    target_imgs = rearrange(target_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
    target_imgs = target_imgs.to(device)

    normal_imgs = batch['depth_imgs']
    normal_imgs = v2.functional.resize(normal_imgs, img_size, interpolation=3, antialias=True).clamp(0, 1)
    normal_imgs = rearrange(normal_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
    normal_imgs = normal_imgs.to(device)

    real_depth_imgs = batch['real_depth_imgs']
    real_depth_imgs = v2.functional.resize(real_depth_imgs, img_size, interpolation=3, antialias=True).clamp(0, 1)
    real_depth_imgs = rearrange(real_depth_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
    real_depth_imgs = real_depth_imgs.to(device)

    if 'alpha_masks' in batch:
        alpha_masks = batch['alpha_masks']
        if alpha_masks.dim() == 4:
            alpha_masks = alpha_masks.unsqueeze(2)
        B, N, C, H, W = alpha_masks.shape
        alpha_masks = alpha_masks.reshape(B * N, C, H, W)
        alpha_masks = v2.functional.resize(alpha_masks, img_size, interpolation=3, antialias=True).clamp(0, 1)
        alpha_masks = alpha_masks.reshape(B, N, C, img_size, img_size)
        alpha_masks = rearrange(alpha_masks, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        mask = alpha_masks.to(device)
    else:
        mask = (target_imgs < 0.95).any(dim=1, keepdim=True).float()

    depth_single = real_depth_imgs[:, :1, :, :]
    geo_input = torch.cat([normal_imgs, depth_single, mask], dim=1)

    return cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask


def collate_batch(dataset, idx, device=None):
    """Get a single sample and add batch dimension."""
    batch = dataset[idx]
    batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v for k, v in batch.items()}
    if device is not None:
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)
    return batch
