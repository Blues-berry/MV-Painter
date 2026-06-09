"""
Evaluate perturbation sensitivity: how robust are different LoRA configurations
to degraded condition images?

Tests: Original / Full LoRA / attn2-only LoRA
Under perturbations: Gaussian noise, occlusion, brightness jitter, background disturb

For each (object, perturbation, intensity, config):
  - Generate with original condition → reference_output
  - Generate with perturbed condition → perturbed_output
  - Compute consistency metric = similarity(reference_output, perturbed_output)

Lower delta = more robust = better reference-conditioned behavior preservation.
"""
import os
import sys
import csv
import json
import torch
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from datetime import datetime
import functools

# Force unbuffered output
print = functools.partial(print, flush=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, extract_first_view, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from transformers import CLIPModel, CLIPProcessor, Dinov2Model


# ============================================================
# Perturbation functions
# ============================================================

def add_gaussian_noise(img, sigma):
    """Add Gaussian noise to PIL image."""
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, sigma, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def random_occlusion(img, ratio):
    """Randomly occlude a rectangular region of the image."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    occlude_w = int(w * np.sqrt(ratio))
    occlude_h = int(h * np.sqrt(ratio))
    x1 = np.random.randint(0, w - occlude_w)
    y1 = np.random.randint(0, h - occlude_h)
    # Fill with mean color
    arr = np.array(img)
    mean_color = tuple(int(c) for c in arr.mean(axis=(0, 1)))
    draw.rectangle([x1, y1, x1 + occlude_w, y1 + occlude_h], fill=mean_color)
    return img


def brightness_jitter(img, factor):
    """Adjust brightness by factor (1.0 = no change)."""
    arr = np.array(img).astype(np.float32)
    arr = np.clip(arr * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def background_disturb(img, intensity):
    """Add random noise to background pixels (white/near-white)."""
    arr = np.array(img).astype(np.float32)
    # Detect background: near-white pixels (R>240, G>240, B>240)
    bg_mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    noise = np.random.normal(0, intensity, arr.shape)
    arr[bg_mask] = np.clip(arr[bg_mask] + noise[bg_mask], 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


PERTURBATIONS = {
    'gaussian_noise': {
        'func': add_gaussian_noise,
        'levels': [10, 25, 50],  # sigma values
        'label': 'Gaussian Noise σ',
    },
    'occlusion': {
        'func': random_occlusion,
        'levels': [0.05, 0.10, 0.20],  # ratio
        'label': 'Occlusion ratio',
    },
    'brightness': {
        'func': brightness_jitter,
        'levels': [0.7, 0.85, 1.15, 1.3],  # factor
        'label': 'Brightness factor',
    },
    'background': {
        'func': background_disturb,
        'levels': [20, 40, 80],  # intensity
        'label': 'Background noise σ',
    },
}


# ============================================================
# Metrics
# ============================================================

def compute_clip_similarity(img1, img2, clip_model, clip_processor, device='cuda'):
    inputs1 = clip_processor(images=img1, return_tensors="pt").to(device)
    inputs2 = clip_processor(images=img2, return_tensors="pt").to(device)
    with torch.no_grad():
        f1 = clip_model.get_image_features(**inputs1)
        f2 = clip_model.get_image_features(**inputs2)
    f1 = f1 / f1.norm(dim=-1, keepdim=True)
    f2 = f2 / f2.norm(dim=-1, keepdim=True)
    return (f1 * f2).sum(dim=-1).item()


def compute_dino_similarity(img1, img2, dino_model, device='cuda'):
    from torchvision import transforms
    transform = transforms.Compose([
        transforms.Resize(224), transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    t1 = transform(img1).unsqueeze(0).to(device)
    t2 = transform(img2).unsqueeze(0).to(device)
    with torch.no_grad():
        feat1 = dino_model(t1).last_hidden_state[:, 0, :]
        feat2 = dino_model(t2).last_hidden_state[:, 0, :]
    feat1 = feat1 / feat1.norm(dim=-1, keepdim=True)
    feat2 = feat2 / feat2.norm(dim=-1, keepdim=True)
    return (feat1 * feat2).sum(dim=-1).item()


def compute_psnr(img1, img2):
    """Compute PSNR between two PIL images."""
    arr1 = np.array(img1).astype(np.float64)
    arr2 = np.array(img2).astype(np.float64)
    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


# ============================================================
# Main evaluation
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-objects', type=int, default=15,
                        help='Number of test objects to evaluate')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output-dir', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/perturbation_sensitivity')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    np.random.seed(args.seed)

    # Load models
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    print("Loading DINOv2 model...")
    dino_model = Dinov2Model.from_pretrained("facebook/dinov2-base").to(device)

    # Load pipeline
    pipeline = load_pipeline()

    # Checkpoint paths
    full_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-full-r4-lr1e5-250-fair-lora-full-fair-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'
    attn2_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    # Select test objects from clean_objects.txt
    clean_path = os.path.join(TRAIN_DATA, 'clean_objects.txt')
    with open(clean_path) as f:
        all_objects = [l.strip() for l in f if l.strip()]

    # Randomly sample
    if len(all_objects) > args.num_objects:
        indices = np.random.choice(len(all_objects), args.num_objects, replace=False)
        test_objects = [all_objects[i] for i in sorted(indices)]
    else:
        test_objects = all_objects

    print(f"\nEvaluating {len(test_objects)} objects")
    print(f"Perturbations: {list(PERTURBATIONS.keys())}")

    # Results storage
    all_results = []

    # Incremental CSV writer - save each result immediately
    csv_path = os.path.join(args.output_dir, 'perturbation_results.csv')

    # Load existing results for resume support
    existing_results = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['obj_id'], row['config'], row['perturbation'], row['level'])
                existing_results.add(key)
                all_results.append(row)
        print(f"  Resuming: {len(existing_results)} results already exist")

    csv_file = open(csv_path, 'a' if existing_results else 'w', newline='')
    csv_fieldnames = ['obj_id', 'config', 'perturbation', 'level', 'clip_consistency', 'dino_consistency', 'psnr_consistency']
    csv_writer = csv.DictWriter(csv_file, fieldnames=csv_fieldnames)
    if not existing_results:
        csv_writer.writeheader()

    for obj_idx, obj_id in enumerate(test_objects):
        print(f"\n{'=' * 60}")
        print(f"[{obj_idx + 1}/{len(test_objects)}] Object: {obj_id}")
        print(f"{'=' * 60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_path = os.path.join(obj_path, 'image', '000.png')
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        cond_rgba = Image.open(cond_path).convert('RGBA')
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: missing normal/depth")
            continue

        # Generate reference outputs (original condition, no perturbation)
        configs = [
            ('original', None, None),
            ('full_lora', full_lora_path, merge_lora_into_unet),
            ('attn2_lora', attn2_lora_path, merge_lora_into_unet_attn2_only),
        ]

        reference_outputs = {}
        for config_name, lora_path, merge_func in configs:
            print(f"  Generating reference: {config_name}...")
            reload_base_weights(pipeline)
            if lora_path is not None:
                bare_unet = get_bare_unet(pipeline)
                merge_func(bare_unet, lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            seed_everything(args.seed)
            output = run_inference(pipeline, cond_rgba, normal_grid, depth_grid, seed=args.seed)
            if output is not None:
                view = extract_first_view(output)
                reference_outputs[config_name] = view
                print(f"    Reference OK")
            else:
                print(f"    Reference FAILED")
                reference_outputs[config_name] = None

        # Test each perturbation
        for perturb_name, perturb_info in PERTURBATIONS.items():
            perturb_func = perturb_info['func']
            levels = perturb_info['levels']

            for level in levels:
                print(f"\n  Perturbation: {perturb_name} (level={level})")

                # Apply perturbation to condition image
                cond_rgb = Image.new('RGB', cond_rgba.size, (255, 255, 255))
                cond_rgb.paste(cond_rgba, mask=cond_rgba.split()[3])
                perturbed_cond_rgb = perturb_func(cond_rgb, level)
                # Convert back to RGBA with original alpha
                perturbed_rgba = perturbed_cond_rgb.convert('RGBA')
                if cond_rgba.mode == 'RGBA':
                    perturbed_rgba.putalpha(cond_rgba.split()[3])

                # Generate with perturbed condition for each config
                for config_name, lora_path, merge_func in configs:
                    # Skip if already computed (resume support)
                    check_key = (obj_id, config_name, perturb_name, str(level))
                    if check_key in existing_results:
                        print(f"    {config_name}: SKIPPED (already computed)")
                        continue

                    reload_base_weights(pipeline)
                    if lora_path is not None:
                        bare_unet = get_bare_unet(pipeline)
                        merge_func(bare_unet, lora_path, rank=4, alpha=4)
                    verify_reference_attention(pipeline)
                    seed_everything(args.seed)
                    output = run_inference(pipeline, perturbed_rgba, normal_grid, depth_grid, seed=args.seed)

                    if output is None:
                        print(f"    {config_name}: inference FAILED")
                        continue

                    perturbed_view = extract_first_view(output)
                    ref_view = reference_outputs.get(config_name)

                    if ref_view is None:
                        print(f"    {config_name}: no reference output")
                        continue

                    # Compute consistency metrics
                    clip_sim = compute_clip_similarity(ref_view, perturbed_view, clip_model, clip_processor, device)
                    dino_sim = compute_dino_similarity(ref_view, perturbed_view, dino_model, device)
                    psnr_val = compute_psnr(ref_view, perturbed_view)

                    row = {
                        'obj_id': obj_id,
                        'config': config_name,
                        'perturbation': perturb_name,
                        'level': level,
                        'clip_consistency': clip_sim,
                        'dino_consistency': dino_sim,
                        'psnr_consistency': psnr_val,
                    }
                    all_results.append(row)
                    csv_writer.writerow(row)
                    csv_file.flush()
                    print(f"    {config_name}: CLIP={clip_sim:.4f} DINO={dino_sim:.4f} PSNR={psnr_val:.1f}")

    # Close CSV
    csv_file.close()
    print(f"\nResults saved to {csv_path} ({len(all_results)} rows)")

    # Generate summary report
    generate_summary(all_results, args.output_dir)


def generate_summary(results, output_dir):
    """Generate summary statistics."""
    if not results:
        print("No results to summarize")
        return

    # Group by (config, perturbation, level)
    from collections import defaultdict
    groups = defaultdict(lambda: {'clip': [], 'dino': [], 'psnr': []})

    for r in results:
        key = (r['config'], r['perturbation'], r['level'])
        groups[key]['clip'].append(r['clip_consistency'])
        groups[key]['dino'].append(r['dino_consistency'])
        groups[key]['psnr'].append(r['psnr_consistency'])

    # Compute averages
    summary = {}
    for (config, perturb, level), metrics in groups.items():
        key = f"{config}_{perturb}_{level}"
        summary[key] = {
            'config': config,
            'perturbation': perturb,
            'level': level,
            'n': len(metrics['clip']),
            'clip_mean': np.mean(metrics['clip']),
            'clip_std': np.std(metrics['clip']),
            'dino_mean': np.mean(metrics['dino']),
            'dino_std': np.std(metrics['dino']),
            'psnr_mean': np.mean(metrics['psnr']),
            'psnr_std': np.std(metrics['psnr']),
        }

    # Save summary JSON
    summary_path = os.path.join(output_dir, 'perturbation_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    # Generate markdown report
    md_path = os.path.join(output_dir, 'perturbation_report.md')
    with open(md_path, 'w') as f:
        f.write("# Perturbation Sensitivity Evaluation\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("**Purpose**: Evaluate robustness of different LoRA configurations to condition image perturbations.\n\n")
        f.write("**Metric**: Consistency between reference output (original condition) and perturbed output.\n")
        f.write("Higher = more robust = less sensitive to perturbation.\n\n")

        f.write("## Summary by Perturbation Type\n\n")

        for perturb_name in PERTURBATIONS:
            f.write(f"### {perturb_name}\n\n")
            f.write("| Config | Level | CLIP Consistency | DINO Consistency | PSNR Consistency |\n")
            f.write("|--------|-------|------------------|------------------|------------------|\n")

            for (config, perturb, level), metrics in sorted(groups.items()):
                if perturb != perturb_name:
                    continue
                f.write(f"| {config} | {level} | "
                        f"{np.mean(metrics['clip']):.4f} ± {np.std(metrics['clip']):.4f} | "
                        f"{np.mean(metrics['dino']):.4f} ± {np.std(metrics['dino']):.4f} | "
                        f"{np.mean(metrics['psnr']):.1f} ± {np.std(metrics['psnr']):.1f} |\n")
            f.write("\n")

        # Delta analysis: attn2-only vs full_lora
        f.write("## Delta Analysis: attn2-only vs Full LoRA\n\n")
        f.write("Positive delta = attn2-only is more robust.\n\n")
        f.write("| Perturbation | Level | ΔCLIP | ΔDINO | ΔPSNR |\n")
        f.write("|-------------|-------|-------|-------|-------|\n")

        for perturb_name in PERTURBATIONS:
            for level in PERTURBATIONS[perturb_name]['levels']:
                key_attn2 = f"attn2_lora_{perturb_name}_{level}"
                key_full = f"full_lora_{perturb_name}_{level}"
                if key_attn2 in summary and key_full in summary:
                    s_attn2 = summary[key_attn2]
                    s_full = summary[key_full]
                    d_clip = s_attn2['clip_mean'] - s_full['clip_mean']
                    d_dino = s_attn2['dino_mean'] - s_full['dino_mean']
                    d_psnr = s_attn2['psnr_mean'] - s_full['psnr_mean']
                    f.write(f"| {perturb_name} | {level} | "
                            f"{d_clip:+.4f} | {d_dino:+.4f} | {d_psnr:+.1f} |\n")

    print(f"Summary saved to {summary_path}")
    print(f"Report saved to {md_path}")


if __name__ == '__main__':
    main()
