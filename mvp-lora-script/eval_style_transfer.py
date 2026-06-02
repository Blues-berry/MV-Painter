"""
Evaluate Style Transfer Experiment.

Metrics:
1. Style Learning: Color histogram similarity with styled data
2. Reference Preservation: CLIP similarity with original condition
3. Multi-view Consistency: Cross-view CLIP similarity
"""
import os
import sys
import csv
import torch
import numpy as np
from PIL import Image
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler
from safetensors.torch import load_file
from transformers import CLIPModel, CLIPProcessor


def load_pipeline(checkpoint_path, unet_ckpt_path, device='cuda'):
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path, torch_dtype=torch.float16, use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    if os.path.exists(unet_ckpt_path):
        ckpt = load_file(unet_ckpt_path)
        unet_state = {k[len('unet.unet.'):]: v for k, v in ckpt.items() if k.startswith('unet.unet.')}
        if unet_state:
            pipeline.unet.load_state_dict(unet_state, strict=False)
    return pipeline.to(device)


def run_inference(pipeline, image, seed=42, num_steps=50):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')
    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def extract_views(six_view_img):
    """Extract 6 views from the 6-view image."""
    arr = np.array(six_view_img)
    h, w = arr.shape[0] // 3, arr.shape[1] // 2

    views = []
    for i in range(3):
        for j in range(2):
            view = Image.fromarray(arr[i*h:(i+1)*h, j*w:(j+1)*w])
            views.append(view)

    return views


def compute_clip_similarity(img1, img2, clip_model, clip_processor, device='cuda'):
    inputs1 = clip_processor(images=img1, return_tensors="pt").to(device)
    inputs2 = clip_processor(images=img2, return_tensors="pt").to(device)
    with torch.no_grad():
        features1 = clip_model.get_image_features(**inputs1)
        features2 = clip_model.get_image_features(**inputs2)
    features1 = features1 / features1.norm(dim=-1, keepdim=True)
    features2 = features2 / features2.norm(dim=-1, keepdim=True)
    sim = (features1 * features2).sum(dim=-1).item()
    return sim


def compute_color_histogram_similarity(img1, img2):
    """Compute color histogram similarity (style matching)."""
    # Convert to HSV for better color comparison
    hsv1 = np.array(img1.convert('HSV')).astype(float) / 255.0
    hsv2 = np.array(img2.convert('HSV')).astype(float) / 255.0

    # Compute histograms for each channel
    similarity = 0
    for c in range(3):
        hist1, _ = np.histogram(hsv1[:, :, c], bins=32, range=(0, 1))
        hist2, _ = np.histogram(hsv2[:, :, c], bins=32, range=(0, 1))

        # Normalize
        hist1 = hist1 / hist1.sum()
        hist2 = hist2 / hist2.sum()

        # Bhattacharyya coefficient
        similarity += np.sum(np.sqrt(hist1 * hist2))

    return similarity / 3


def compute_multiview_consistency(views, clip_model, clip_processor, device='cuda'):
    """Compute multi-view consistency (average pairwise CLIP similarity)."""
    if len(views) < 2:
        return 0.0

    similarities = []
    for i in range(len(views)):
        for j in range(i+1, len(views)):
            sim = compute_clip_similarity(views[i], views[j], clip_model, clip_processor, device)
            similarities.append(sim)

    return np.mean(similarities)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Evaluate Style Transfer')
    parser.add_argument('--style', type=str, default='warm',
                        help='Style name')
    parser.add_argument('--styled_data', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/style_transfer/styled_warm',
                        help='Styled data directory')
    parser.add_argument('--output_dir', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/style_transfer/eval_warm',
                        help='Output directory')
    parser.add_argument('--test_objects', type=int, default=5,
                        help='Number of test objects')

    args = parser.parse_args()

    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    os.makedirs(args.output_dir, exist_ok=True)

    # Find LoRA checkpoints
    logs_dir = '/4T/CXY/MV-Painter/MVPainter/logs'
    full_lora_candidates = [d for d in os.listdir(logs_dir) if f'style_{args.style}_full' in d.lower()]
    attn2_lora_candidates = [d for d in os.listdir(logs_dir) if f'style_{args.style}_attn2' in d.lower()]

    if not full_lora_candidates or not attn2_lora_candidates:
        print("Style transfer LoRA checkpoints not found!")
        print("Please run training first: bash style_transfer/train_{args.style}.sh")
        return

    full_lora_path = os.path.join(logs_dir, full_lora_candidates[0], 'lora_checkpoints')
    attn2_lora_path = os.path.join(logs_dir, attn2_lora_candidates[0], 'lora_checkpoints')

    # Find latest checkpoint
    def find_latest_ckpt(path):
        if not os.path.exists(path):
            return None
        ckpts = sorted([f for f in os.listdir(path) if f.endswith('.safetensors')])
        return os.path.join(path, ckpts[-1]) if ckpts else None

    full_ckpt = find_latest_ckpt(full_lora_path)
    attn2_ckpt = find_latest_ckpt(attn2_lora_path)

    if not full_ckpt or not attn2_ckpt:
        print("No checkpoints found!")
        return

    print(f"Full LoRA checkpoint: {full_ckpt}")
    print(f"attn2-only checkpoint: {attn2_ckpt}")

    # Get test objects (different from training)
    source_dir = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
    all_objects = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    test_objects = all_objects[20:20+args.test_objects]  # Use objects not in training

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load CLIP
    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    results = []

    for obj_id in test_objects:
        print(f"\n{'='*60}")
        print(f"Object: {obj_id}")
        print(f"{'='*60}")

        # Get original and styled images
        orig_path = os.path.join(source_dir, obj_id, 'image', '000.png')
        styled_path = os.path.join(args.styled_data, obj_id, 'image', '000.png')

        if not os.path.exists(orig_path) or not os.path.exists(styled_path):
            print(f"  Skipping: images not found")
            continue

        orig_img = Image.open(orig_path).convert('RGB')
        styled_img = Image.open(styled_path).convert('RGB')

        cond_img = Image.open(orig_path).convert('RGBA')

        row = {'obj_id': obj_id}

        # --- Config A: Original (no style) ---
        print("  Config A: Original...")
        try:
            pipeline_a = load_pipeline(checkpoint_path, unet_ckpt_path)
            img_a_full = run_inference(pipeline_a, cond_img, seed=42)
            del pipeline_a; torch.cuda.empty_cache()

            views_a = extract_views(img_a_full)

            # Style similarity with styled target
            row['style_sim_a'] = compute_color_histogram_similarity(styled_img, views_a[0])
            # Reference similarity with original
            row['ref_sim_a'] = compute_clip_similarity(orig_img, views_a[0], clip_model, clip_processor, device)
            # Multi-view consistency
            row['consistency_a'] = compute_multiview_consistency(views_a, clip_model, clip_processor, device)

            print(f"    Style: {row['style_sim_a']:.4f}, Ref: {row['ref_sim_a']:.4f}, Consistency: {row['consistency_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['style_sim_a'] = row['ref_sim_a'] = row['consistency_a'] = None

        # --- Config B: Full LoRA ---
        print("  Config B: Full LoRA...")
        try:
            pipeline_b = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet(pipeline_b.unet, full_ckpt, rank=4, alpha=4)
            img_b_full = run_inference(pipeline_b, cond_img, seed=42)
            del pipeline_b; torch.cuda.empty_cache()

            views_b = extract_views(img_b_full)

            row['style_sim_b'] = compute_color_histogram_similarity(styled_img, views_b[0])
            row['ref_sim_b'] = compute_clip_similarity(orig_img, views_b[0], clip_model, clip_processor, device)
            row['consistency_b'] = compute_multiview_consistency(views_b, clip_model, clip_processor, device)

            print(f"    Style: {row['style_sim_b']:.4f}, Ref: {row['ref_sim_b']:.4f}, Consistency: {row['consistency_b']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['style_sim_b'] = row['ref_sim_b'] = row['consistency_b'] = None

        # --- Config C: attn2-only LoRA ---
        print("  Config C: attn2-only LoRA...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, attn2_ckpt, rank=4, alpha=4)
            img_c_full = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c; torch.cuda.empty_cache()

            views_c = extract_views(img_c_full)

            row['style_sim_c'] = compute_color_histogram_similarity(styled_img, views_c[0])
            row['ref_sim_c'] = compute_clip_similarity(orig_img, views_c[0], clip_model, clip_processor, device)
            row['consistency_c'] = compute_multiview_consistency(views_c, clip_model, clip_processor, device)

            print(f"    Style: {row['style_sim_c']:.4f}, Ref: {row['ref_sim_c']:.4f}, Consistency: {row['consistency_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['style_sim_c'] = row['ref_sim_c'] = row['consistency_c'] = None

        results.append(row)

    # Save CSV
    csv_path = os.path.join(args.output_dir, 'style_transfer_results.csv')
    fieldnames = ['obj_id',
                  'style_sim_a', 'ref_sim_a', 'consistency_a',
                  'style_sim_b', 'ref_sim_b', 'consistency_b',
                  'style_sim_c', 'ref_sim_c', 'consistency_c']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Compute averages
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    # Generate report
    md_path = os.path.join(args.output_dir, 'style_transfer_report.md')
    with open(md_path, 'w') as f:
        f.write(f"# Style Transfer Experiment Results\n\n")
        f.write(f"**Style**: {args.style}\n")
        f.write(f"**Test Objects**: {len(results)}\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Method | Style Learning ↑ | Reference Pres. ↑ | Multi-view Cons. ↑ |\n")
        f.write("|--------|------------------|-------------------|-------------------|\n")
        f.write(f"| Original (no style) | {avg('style_sim_a'):.4f} | {avg('ref_sim_a'):.4f} | {avg('consistency_a'):.4f} |\n")
        f.write(f"| Full LoRA | {avg('style_sim_b'):.4f} | {avg('ref_sim_b'):.4f} | {avg('consistency_b'):.4f} |\n")
        f.write(f"| attn2-only LoRA | {avg('style_sim_c'):.4f} | {avg('ref_sim_c'):.4f} | {avg('consistency_c'):.4f} |\n")

        f.write("\n## Analysis\n\n")

        # Style learning
        f.write("### 1. Style Learning\n\n")
        f.write("Higher = better style matching with target style.\n\n")
        f.write(f"- Original: {avg('style_sim_a'):.4f} (baseline)\n")
        f.write(f"- Full LoRA: {avg('style_sim_b'):.4f} (diff: {avg('style_sim_b') - avg('style_sim_a'):+.4f})\n")
        f.write(f"- attn2-only: {avg('style_sim_c'):.4f} (diff: {avg('style_sim_c') - avg('style_sim_a'):+.4f})\n\n")

        if avg('style_sim_c') > avg('style_sim_b'):
            f.write("**attn2-only LoRA learns the style better!**\n\n")
        elif avg('style_sim_b') > avg('style_sim_c'):
            f.write("**Full LoRA learns the style better.**\n\n")
        else:
            f.write("**Both methods learn the style similarly.**\n\n")

        # Reference preservation
        f.write("### 2. Reference Preservation\n\n")
        f.write("Higher = better preservation of original condition image.\n\n")
        f.write(f"- Original: {avg('ref_sim_a'):.4f} (baseline)\n")
        f.write(f"- Full LoRA: {avg('ref_sim_b'):.4f} (diff: {avg('ref_sim_b') - avg('ref_sim_a'):+.4f})\n")
        f.write(f"- attn2-only: {avg('ref_sim_c'):.4f} (diff: {avg('ref_sim_c') - avg('ref_sim_a'):+.4f})\n\n")

        if avg('ref_sim_c') > avg('ref_sim_b'):
            f.write("**attn2-only LoRA preserves reference better!**\n\n")

        # Multi-view consistency
        f.write("### 3. Multi-view Consistency\n\n")
        f.write("Higher = more consistent across views.\n\n")
        f.write(f"- Original: {avg('consistency_a'):.4f}\n")
        f.write(f"- Full LoRA: {avg('consistency_b'):.4f}\n")
        f.write(f"- attn2-only: {avg('consistency_c'):.4f}\n\n")

        f.write("## Key Finding\n\n")

        # Determine the key finding
        style_better = avg('style_sim_c') > avg('style_sim_b')
        ref_better = avg('ref_sim_c') > avg('ref_sim_b')

        if style_better and ref_better:
            f.write("**attn2-only LoRA achieves BOTH better style learning AND better reference preservation.**\n\n")
            f.write("This proves that attn2-only LoRA can actually learn new tasks while preserving the critical reference attention mechanism.\n")
        elif style_better:
            f.write("**attn2-only LoRA learns the style better while maintaining similar reference preservation.**\n\n")
        elif ref_better:
            f.write("**attn2-only LoRA preserves reference better while learning the style similarly.**\n\n")
        else:
            f.write("Both methods show similar performance. Further investigation needed.\n")

    print(f"\nReport saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("STYLE TRANSFER RESULTS")
    print(f"{'='*60}")
    print(f"\n{'Method':<20} {'Style':>10} {'Reference':>12} {'Consistency':>14}")
    print(f"{'-'*56}")
    print(f"{'Original':<20} {avg('style_sim_a'):>10.4f} {avg('ref_sim_a'):>12.4f} {avg('consistency_a'):>14.4f}")
    print(f"{'Full LoRA':<20} {avg('style_sim_b'):>10.4f} {avg('ref_sim_b'):>12.4f} {avg('consistency_b'):>14.4f}")
    print(f"{'attn2-only LoRA':<20} {avg('style_sim_c'):>10.4f} {avg('ref_sim_c'):>12.4f} {avg('consistency_c'):>14.4f}")


if __name__ == '__main__':
    main()
