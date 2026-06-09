"""Visualization utilities for GeoTex-Adapter evaluation."""
import os
import torch
from torchvision.utils import save_image


def save_comparison(gt, orig, adapter, output_dir, prefix="vis", max_images=3):
    """Save GT / Original / Adapter comparison images."""
    os.makedirs(output_dir, exist_ok=True)
    n = min(gt.shape[0], max_images)
    for i in range(n):
        vis = torch.cat([gt[i:i+1], orig[i:i+1], adapter[i:i+1]], dim=0)
        save_image(vis, os.path.join(output_dir, f'{prefix}_{i:03d}.png'), nrow=3)


def save_error_maps(gt, orig, adapter, mask, output_dir, prefix="error", max_images=3):
    """Save error maps: |orig-gt|, |adapter-gt|, adapter-orig diff."""
    os.makedirs(output_dir, exist_ok=True)
    n = min(gt.shape[0], max_images)
    for i in range(n):
        err_orig = (orig[i:i+1] - gt[i:i+1]).abs()
        err_adapter = (adapter[i:i+1] - gt[i:i+1]).abs()
        diff = (adapter[i:i+1] - orig[i:i+1]).abs()
        mask_vis = mask[i:i+1].expand_as(err_orig)
        vis = torch.cat([err_orig * 5, err_adapter * 5, diff * 5, mask_vis], dim=0)
        save_image(vis, os.path.join(output_dir, f'{prefix}_{i:03d}.png'), nrow=4)


def save_region_visualization(gt, orig, adapter, mask, edge_mask, output_dir, idx=0):
    """Save region visualization: GT, orig, adapter, mask, edge mask."""
    os.makedirs(output_dir, exist_ok=True)
    vis = torch.cat([
        gt[0:1], orig[0:1], adapter[0:1],
        mask[0:1].expand_as(gt[0:1]),
        edge_mask[0:1].expand_as(gt[0:1]),
    ], dim=0)
    save_image(vis, os.path.join(output_dir, f'region_{idx:03d}.png'), nrow=5)
