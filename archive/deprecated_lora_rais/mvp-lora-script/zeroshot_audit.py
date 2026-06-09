"""
Phase 1: Zero-shot audit
Run base pipeline (no LoRA) on clean samples to verify baseline stability.
"""
import os
import sys
import json
import argparse
import numpy as np
import torch
import cv2
from PIL import Image
from torchvision.transforms import v2
from einops import rearrange
from tqdm import tqdm
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler, UNet2DConditionModel


def load_pipeline(checkpoint_path, device='cuda'):
    """Load base pipeline without LoRA."""
    print(f"Loading pipeline from {checkpoint_path} ...")
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Load custom UNet if available
    unet_ckpt_path = os.path.join(os.path.dirname(checkpoint_path), 'v29_25000.safetensors')
    if os.path.exists(unet_ckpt_path) and os.path.getsize(unet_ckpt_path) > 14_000_000_000:
        from safetensors.torch import load_file
        print(f"Loading custom UNet from {unet_ckpt_path} ...")
        ckpt = load_file(unet_ckpt_path)

        # Fix key prefix: v29 checkpoint has 'unet.unet.xxx' but pipeline expects 'xxx'
        unet_state = {}
        for k, v in ckpt.items():
            if k.startswith('unet.unet.'):
                new_key = k[len('unet.unet.'):]
                unet_state[new_key] = v

        if unet_state:
            result = pipeline.unet.load_state_dict(unet_state, strict=False)
            print(f"Loaded {len(unet_state)} keys, missing={len(result.missing_keys)}, unexpected={len(result.unexpected_keys)}")
        else:
            print("WARNING: No unet keys found in checkpoint")
    else:
        print("WARNING: v29 checkpoint not available, using base UNet")

    pipeline = pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)
    return pipeline


def load_sample_data(sample_dir):
    """Load a single sample's data (condition image, normal, depth)."""
    image_dir = os.path.join(sample_dir, 'image')
    normal_dir = os.path.join(sample_dir, 'normal')
    depth_dir = os.path.join(sample_dir, 'depth_png')

    if not os.path.exists(image_dir) or not os.path.exists(normal_dir):
        return None

    # Use view 0 as condition (same as training default)
    cond_path = os.path.join(image_dir, '000.png')
    if not os.path.exists(cond_path):
        return None

    cond_img = cv2.imread(cond_path, cv2.IMREAD_UNCHANGED)
    if cond_img is None:
        return None
    cond_img = cv2.cvtColor(cond_img, cv2.COLOR_BGRA2RGBA)

    # Load target views: [0, 15, 12, 15, 13, 14] -> but we only have 0-16
    # From dataset: target_order = [0,15,12,7,13,14] or reversed
    target_indices = [0, 5, 2, 7, 3, 4]  # Simplified for available views

    target_imgs = []
    normal_imgs = []
    depth_imgs = []

    for idx in target_indices:
        # Load image
        img_path = os.path.join(image_dir, f'{idx:03d}.png')
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            target_imgs.append(img)
        else:
            target_imgs.append(np.zeros_like(cond_img))

        # Load normal
        nrm_path = os.path.join(normal_dir, f'{idx:03d}.png')
        if os.path.exists(nrm_path):
            nrm = cv2.imread(nrm_path, cv2.IMREAD_UNCHANGED)
            nrm = cv2.cvtColor(nrm, cv2.COLOR_BGR2RGB)
            normal_imgs.append(nrm)
        else:
            normal_imgs.append(np.zeros((512, 512, 3), dtype=np.uint16))

        # Load depth
        dep_path = os.path.join(depth_dir, f'{idx:03d}.png')
        if os.path.exists(dep_path):
            dep = cv2.imread(dep_path, cv2.IMREAD_UNCHANGED)
            dep = cv2.cvtColor(dep, cv2.COLOR_BGR2RGB)
            depth_imgs.append(dep)
        else:
            depth_imgs.append(np.ones((512, 512, 3), dtype=np.uint16) * 65535)

    return {
        'cond_img': cond_img,
        'target_imgs': target_imgs,
        'normal_imgs': normal_imgs,
        'depth_imgs': depth_imgs,
    }


def prepare_condition_image(cond_img, img_size=256):
    """Prepare condition image for pipeline (same as inference)."""
    # Convert to PIL
    cond_pil = Image.fromarray(cond_img)
    return cond_pil


def prepare_depth_normal(normal_imgs, depth_imgs, img_size=256):
    """Prepare depth/normal maps as combined images (same as training layout)."""
    bkg_color = [1., 1., 1.]

    # Process normal images
    normal_list = []
    for img in normal_imgs:
        img_float = img.astype(np.float32) / 65535.0
        if len(img_float.shape) == 2:
            img_float = np.stack([img_float] * 3, axis=0)
        else:
            img_float = img_float.transpose(2, 0, 1)
        normal_list.append(torch.from_numpy(img_float).float())

    # Process depth images
    depth_list = []
    for img in depth_imgs:
        img_float = img.astype(np.float32) / 65535.0
        if len(img_float.shape) == 2:
            img_float = np.stack([img_float] * 3, axis=0)
        else:
            img_float = img_float.transpose(2, 0, 1)
        depth_list.append(torch.from_numpy(img_float).float())

    # Stack and rearrange: (6, C, H, W) -> (C, 3H, 2W)
    normal_tensor = torch.stack(normal_list, dim=0)
    normal_tensor = rearrange(normal_tensor, '(x y) c h w -> c (x h) (y w)', x=3, y=2)

    depth_tensor = torch.stack(depth_list, dim=0)
    depth_tensor = rearrange(depth_tensor, '(x y) c h w -> c (x h) (y w)', x=3, y=2)

    # Convert to PIL
    normal_pil = Image.fromarray((normal_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8))
    depth_pil = Image.fromarray((depth_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8))

    return normal_pil, depth_pil


def check_image_quality(img_array):
    """Check if an image is black, noisy, or normal."""
    if img_array is None:
        return 'invalid'

    mean_val = np.mean(img_array)
    std_val = np.std(img_array)

    # Check if mostly black
    if mean_val < 5:
        return 'black'

    # Check if mostly white
    if mean_val > 250:
        return 'white'

    # Check if high noise (high std relative to mean)
    if std_val > 100 and mean_val < 50:
        return 'noisy'

    # Check for blue-ish tint (common in failed diffusion)
    if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
        b_mean = np.mean(img_array[:, :, 0])
        r_mean = np.mean(img_array[:, :, 2])
        if b_mean > r_mean * 2 and b_mean > 100:
            return 'blue_noise'

    return 'normal'


def run_zeroshot_audit(pipeline, data_root, clean_list, output_dir, num_samples=20, device='cuda'):
    """Run zero-shot inference on clean samples."""
    os.makedirs(output_dir, exist_ok=True)

    # Load clean list
    clean_path = os.path.join(data_root, clean_list)
    with open(clean_path, 'r') as f:
        all_names = [l.strip() for l in f.readlines() if l.strip()]

    # Sample or use all
    if num_samples and num_samples < len(all_names):
        import random
        random.seed(42)
        names = random.sample(all_names, num_samples)
    else:
        names = all_names

    results = []

    for name in tqdm(names, desc="Zero-shot audit"):
        sample_dir = os.path.join(data_root, name)
        sample_output_dir = os.path.join(output_dir, name)
        os.makedirs(sample_output_dir, exist_ok=True)

        result = {
            'name': name,
            'condition_status': 'unknown',
            'zeroshot_status': 'unknown',
            'depth_status': 'unknown',
            'normal_status': 'unknown',
            'error': None,
        }

        try:
            # Load sample data
            data = load_sample_data(sample_dir)
            if data is None:
                result['condition_status'] = 'load_failed'
                result['error'] = 'Failed to load sample data'
                results.append(result)
                continue

            # Check condition image quality
            cond_status = check_image_quality(data['cond_img'])
            result['condition_status'] = cond_status

            # Save condition image
            cond_pil = Image.fromarray(data['cond_img'])
            cond_pil.save(os.path.join(sample_output_dir, 'condition.png'))

            # Check normal/depth quality
            normal_avg = np.mean([np.mean(n) for n in data['normal_imgs']])
            depth_avg = np.mean([np.mean(d) for d in data['depth_imgs']])
            result['normal_status'] = 'normal' if normal_avg > 100 else 'suspicious'
            result['depth_status'] = 'normal' if depth_avg < 60000 else 'suspicious'

            # Prepare for pipeline
            cond_input = prepare_condition_image(data['cond_img'])

            # Run zero-shot inference
            with torch.no_grad(), torch.amp.autocast('cuda'):
                output = pipeline(
                    cond_input,
                    num_inference_steps=50,
                    output_type='pil',
                )

            # Pipeline returns a list: [6view_image, cond_image]
            if isinstance(output, list) and len(output) >= 1:
                six_view = output[0]
                six_view.save(os.path.join(sample_output_dir, 'zeroshot_6view.png'))

                # Also save condition image from pipeline output
                if len(output) >= 2:
                    output[1].save(os.path.join(sample_output_dir, 'pipeline_cond.png'))

                # Check quality
                six_view_arr = np.array(six_view)
                result['zeroshot_status'] = check_image_quality(six_view_arr)
            elif hasattr(output, 'images') and len(output.images) > 0:
                six_view = output.images[0]
                six_view.save(os.path.join(sample_output_dir, 'zeroshot_6view.png'))
                six_view_arr = np.array(six_view)
                result['zeroshot_status'] = check_image_quality(six_view_arr)
            else:
                result['zeroshot_status'] = 'no_output'
                result['error'] = f'Pipeline returned unexpected output type: {type(output)}'

        except Exception as e:
            result['zeroshot_status'] = 'error'
            result['error'] = str(e)
            traceback.print_exc()

        results.append(result)

        # Clear GPU memory
        torch.cuda.empty_cache()

    return results


def generate_report(results, output_path):
    """Generate audit report."""
    stats = {
        'total': len(results),
        'zeroshot_normal': 0,
        'zeroshot_black': 0,
        'zeroshot_noisy': 0,
        'zeroshot_blue_noise': 0,
        'zeroshot_error': 0,
        'condition_abnormal': 0,
        'depth_abnormal': 0,
        'normal_abnormal': 0,
    }

    for r in results:
        if r['zeroshot_status'] == 'normal':
            stats['zeroshot_normal'] += 1
        elif r['zeroshot_status'] == 'black':
            stats['zeroshot_black'] += 1
        elif r['zeroshot_status'] in ['noisy', 'blue_noise']:
            stats['zeroshot_noisy'] += 1
        elif r['zeroshot_status'] in ['error', 'no_output', 'load_failed']:
            stats['zeroshot_error'] += 1

        if r['condition_status'] not in ['normal']:
            stats['condition_abnormal'] += 1
        if r['depth_status'] not in ['normal']:
            stats['depth_abnormal'] += 1
        if r['normal_status'] not in ['normal']:
            stats['normal_abnormal'] += 1

    report = f"""# Zero-shot Audit Report

## Summary Statistics

| Item | Count |
|------|-------|
| Total samples | {stats['total']} |
| Zero-shot normal | {stats['zeroshot_normal']} |
| Zero-shot black | {stats['zeroshot_black']} |
| Zero-shot noisy/fragmented | {stats['zeroshot_noisy']} |
| Zero-shot error | {stats['zeroshot_error']} |
| Condition abnormal | {stats['condition_abnormal']} |
| Depth abnormal | {stats['depth_abnormal']} |
| Normal abnormal | {stats['normal_abnormal']} |

## Per-Sample Results

| Sample | Condition | Zero-shot | Depth | Normal | Error |
|--------|-----------|-----------|-------|--------|-------|
"""

    for r in results:
        error_msg = r.get('error', '') or ''
        if len(error_msg) > 50:
            error_msg = error_msg[:50] + '...'
        report += f"| {r['name'][:20]} | {r['condition_status']} | {r['zeroshot_status']} | {r['depth_status']} | {r['normal_status']} | {error_msg} |\n"

    # Diagnosis
    report += """
## Diagnosis

"""
    if stats['zeroshot_normal'] == stats['total']:
        report += "✅ **All zero-shot outputs are normal.** The base pipeline is stable and can be used for LoRA comparison.\n"
    elif stats['zeroshot_normal'] > stats['total'] * 0.8:
        report += "⚠️ **Most zero-shot outputs are normal**, but some samples have issues. Check the abnormal samples before LoRA training.\n"
    elif stats['zeroshot_black'] > stats['total'] * 0.3:
        report += "❌ **Many zero-shot outputs are black.** This indicates a fundamental issue with the pipeline or data, NOT LoRA-specific.\n"
    elif stats['zeroshot_noisy'] > stats['total'] * 0.3:
        report += "❌ **Many zero-shot outputs are noisy/fragmented.** This suggests the base model or data has issues.\n"
    else:
        report += "⚠️ **Mixed results.** Further investigation needed.\n"

    if stats['condition_abnormal'] > 0:
        report += f"\n⚠️ {stats['condition_abnormal']} samples have abnormal condition images.\n"
    if stats['depth_abnormal'] > 0:
        report += f"\n⚠️ {stats['depth_abnormal']} samples have suspicious depth maps.\n"

    report += """
## Conclusion

"""
    if stats['zeroshot_normal'] >= stats['total'] * 0.8:
        report += "The base pipeline is reliable. LoRA training issues are likely due to:\n"
        report += "1. LoRA layer placement (attn1 vs attn2)\n"
        report += "2. Learning rate / training hyperparameters\n"
        report += "3. LoRA weight initialization or scaling\n"
    else:
        report += "The base pipeline itself has issues. Before debugging LoRA:\n"
        report += "1. Fix the base pipeline instability\n"
        report += "2. Clean the dataset to remove problematic samples\n"
        report += "3. Verify the checkpoint quality\n"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {output_path}")
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, default='../checkpoints/hf_repo')
    parser.add_argument('--data_root', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--clean_list', type=str, default='clean_objects.txt')
    parser.add_argument('--output_dir', type=str, default='../zeroshot_audit')
    parser.add_argument('--num_samples', type=int, default=20)
    parser.add_argument('--device', type=str, default='cuda')
    args = parser.parse_args()

    pipeline = load_pipeline(args.checkpoint, args.device)
    results = run_zeroshot_audit(
        pipeline, args.data_root, args.clean_list,
        args.output_dir, args.num_samples, args.device
    )
    generate_report(results, os.path.join(args.output_dir, 'zeroshot_audit_report.md'))
