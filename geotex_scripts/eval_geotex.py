"""
GeoTex-Adapter evaluation script.
Compares: Original MV-Painter vs GeoTex-Adapter (up-only, mid+up)
Metrics: Foreground PSNR/SSIM/LPIPS, Edge PSNR/LPIPS, CLIP/DINO similarity
"""
import os
import sys
import json
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from PIL import Image
from torchvision import transforms
from torchvision.transforms import v2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config


def compute_psnr(pred, target, mask=None):
    """Compute PSNR, optionally on foreground only."""
    if mask is not None:
        pred = pred * mask
        target = target * mask
        # Only compute on foreground pixels
        fg = mask > 0.5
        if fg.sum() == 0:
            return 0.0
        mse = ((pred[fg] - target[fg]) ** 2).mean()
    else:
        mse = ((pred - target) ** 2).mean()
    if mse == 0:
        return float('inf')
    return 10 * torch.log10(1.0 / mse).item()


def compute_ssim(pred, target, mask=None):
    """Compute SSIM (simplified version)."""
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2

    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)

    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2

    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))

    if mask is not None:
        mask_dilated = F.max_pool2d(mask, 3, 1, 1)
        ssim_map = ssim_map * mask_dilated
        fg = mask_dilated > 0.5
        if fg.sum() == 0:
            return 0.0
        return ssim_map[fg].mean().item()

    return ssim_map.mean().item()


def compute_lpips(pred, target, lpips_model, mask=None):
    """Compute LPIPS distance."""
    if mask is not None:
        pred = pred * mask + (1 - mask)  # background to white
        target = target * mask + (1 - mask)
    with torch.no_grad():
        dist = lpips_model(pred, target)
    return dist.item()


def compute_clip_similarity(image, condition_image, clip_model, clip_processor):
    """Compute CLIP similarity between generated and condition images."""
    from PIL import Image as PILImage
    import torchvision.transforms as T

    # Convert tensors to PIL
    to_pil = T.ToPILImage()
    img_pil = to_pil(image.squeeze(0).clamp(0, 1))
    cond_pil = to_pil(condition_image.squeeze(0).clamp(0, 1))

    # Process images
    inputs = clip_processor(images=[img_pil, cond_pil], return_tensors="pt", padding=True)
    inputs = {k: v.to(clip_model.device) for k, v in inputs.items()}

    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)
        similarity = (features[0:1] @ features[1:2].T).item()

    return similarity


def detect_edges(image):
    """Detect edges using Sobel filter."""
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32).view(1, 1, 3, 3)

    if image.device != sobel_x.device:
        sobel_x = sobel_x.to(image.device)
        sobel_y = sobel_y.to(image.device)

    gray = image.mean(dim=1, keepdim=True)
    edges_x = F.conv2d(gray, sobel_x, padding=1)
    edges_y = F.conv2d(gray, sobel_y, padding=1)
    edges = torch.sqrt(edges_x ** 2 + edges_y ** 2)
    return edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/mvpainter-geotex-uponly.yaml')
    parser.add_argument('--checkpoint', default=None, help='Path to GeoTex checkpoint')
    parser.add_argument('--num_objects', type=int, default=10)
    parser.add_argument('--output_dir', default='mvpoutput/geotex_eval')
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)
    os.makedirs(args.output_dir, exist_ok=True)

    # Load config
    config = OmegaConf.load(args.config)

    # Instantiate model
    print("Loading model...")
    model = instantiate_from_config(config.model)

    # Load checkpoint if provided
    if args.checkpoint:
        print(f"Loading checkpoint: {args.checkpoint}")
        model.load_geotex_weights(args.checkpoint)

    # Move to device
    model.pipeline.to('cpu')
    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae = model.pipeline.vae.to(device).to(dtype=torch.float16)
    model.adapters.to(device).to(dtype=torch.float16)
    model.geo_encoder.to(device).to(dtype=torch.float16)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')
    model.pipeline.vae.eval()

    # Load LPIPS model
    try:
        import lpips
        lpips_model = lpips.LPIPS(net='alex').to(device)
    except ImportError:
        print("Warning: lpips not installed, skipping LPIPS metric")
        lpips_model = None

    # Load test dataset
    print("Loading test dataset...")
    test_dataset = instantiate_from_config(config.data.params.validation)
    print(f"Test dataset: {len(test_dataset)} objects")

    # Evaluate
    results = []
    num_objects = min(args.num_objects, len(test_dataset))

    for obj_idx in range(num_objects):
        print(f"\nEvaluating object {obj_idx + 1}/{num_objects}...")
        batch = test_dataset[obj_idx]

        # Add batch dim
        batch = {k: v.unsqueeze(0) if hasattr(v, 'unsqueeze') else v for k, v in batch.items()}

        # Prepare data
        for k in batch:
            if hasattr(batch[k], 'to'):
                batch[k] = batch[k].to(device)

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = model.prepare_batch_data(batch)

        # Generate with adapter
        with torch.no_grad():
            from torchvision.transforms import v2 as tv2
            images_pil = [tv2.functional.to_pil_image(cond_imgs[i]) for i in range(cond_imgs.shape[0])]

            # Generate with adapter (if checkpoint provided)
            if args.checkpoint:
                # Set geo_feats on wrapped resnets
                geo_feats = model.geo_encoder(geo_input.to(torch.float16))
                model._set_geo_feats_on_wrappers(geo_feats)

                latent = model.pipeline(images_pil[0], num_inference_steps=50, output_type='latent').images
                image_adapter = model.unscale_image(model.pipeline.vae.decode(
                    latent / model.pipeline.vae.config.scaling_factor, return_dict=False
                )[0])
                image_adapter = (image_adapter * 0.5 + 0.5).clamp(0, 1)

                model._clear_geo_feats_on_wrappers()
            else:
                image_adapter = None

            # Generate without adapter (original)
            # Temporarily disable adapters by clearing geo_feats
            model._clear_geo_feats_on_wrappers()
            latent_orig = model.pipeline(images_pil[0], num_inference_steps=50, output_type='latent').images
            image_orig = model.unscale_image(model.pipeline.vae.decode(
                latent_orig / model.pipeline.vae.config.scaling_factor, return_dict=False
            )[0])
            image_orig = (image_orig * 0.5 + 0.5).clamp(0, 1)

        # Compute metrics
        gt = target_imgs[0:1]  # (1, C, H, W)

        obj_result = {'object_idx': obj_idx}

        # Original metrics
        obj_result['orig_psnr'] = compute_psnr(image_orig, gt, mask[0:1])
        obj_result['orig_ssim'] = compute_ssim(image_orig, gt, mask[0:1])
        if lpips_model:
            obj_result['orig_lpips'] = compute_lpips(image_orig, gt, lpips_model, mask[0:1])

        # Adapter metrics
        if image_adapter is not None:
            obj_result['adapter_psnr'] = compute_psnr(image_adapter, gt, mask[0:1])
            obj_result['adapter_ssim'] = compute_ssim(image_adapter, gt, mask[0:1])
            if lpips_model:
                obj_result['adapter_lpips'] = compute_lpips(image_adapter, gt, lpips_model, mask[0:1])

            # Edge metrics
            edges_gt = detect_edges(gt)
            edges_adapter = detect_edges(image_adapter)
            edges_orig = detect_edges(image_orig)

            edge_mask = (edges_gt > 0.1).float()
            obj_result['orig_edge_psnr'] = compute_psnr(image_orig, gt, edge_mask)
            obj_result['adapter_edge_psnr'] = compute_psnr(image_adapter, gt, edge_mask)

        results.append(obj_result)

        # Save visualization
        if obj_idx < 3:
            vis_images = [gt, image_orig]
            if image_adapter is not None:
                vis_images.append(image_adapter)
            vis_grid = torch.cat(vis_images, dim=0)
            from torchvision.utils import save_image
            save_path = os.path.join(args.output_dir, f'vis_object_{obj_idx:03d}.png')
            save_image(vis_grid, save_path, nrow=len(vis_images))
            print(f"  Saved visualization: {save_path}")

    # Aggregate results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    metrics = ['psnr', 'ssim', 'lpips', 'edge_psnr']
    for metric in metrics:
        orig_key = f'orig_{metric}'
        adapter_key = f'adapter_{metric}'

        orig_vals = [r[orig_key] for r in results if orig_key in r]
        adapter_vals = [r[adapter_key] for r in results if adapter_key in r]

        if orig_vals:
            print(f"\n{metric.upper()}:")
            print(f"  Original: {np.mean(orig_vals):.4f} ± {np.std(orig_vals):.4f}")
            if adapter_vals:
                print(f"  Adapter:  {np.mean(adapter_vals):.4f} ± {np.std(adapter_vals):.4f}")
                diff = np.mean(adapter_vals) - np.mean(orig_vals)
                print(f"  Diff:     {diff:+.4f}")

    # Save results
    results_path = os.path.join(args.output_dir, 'eval_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")


if __name__ == '__main__':
    main()
