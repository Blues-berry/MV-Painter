"""
Evaluate reference consistency using CLIP similarity and DINO cosine similarity.
Compares: Original / Full LoRA / attn2-only LoRA

FIXED: Uses ControlNet + depth grids (matching correct inference pipeline).
"""
import os
import sys
import csv
import torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, extract_first_view, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from transformers import CLIPModel, CLIPProcessor, Dinov2Model


def compute_clip_similarity(img1, img2, clip_model, clip_processor, device='cuda'):
    """Compute CLIP similarity between two images."""
    inputs1 = clip_processor(images=img1, return_tensors="pt").to(device)
    inputs2 = clip_processor(images=img2, return_tensors="pt").to(device)

    with torch.no_grad():
        features1 = clip_model.get_image_features(**inputs1)
        features2 = clip_model.get_image_features(**inputs2)

    features1 = features1 / features1.norm(dim=-1, keepdim=True)
    features2 = features2 / features2.norm(dim=-1, keepdim=True)

    sim = (features1 * features2).sum(dim=-1).item()
    return sim


def compute_dino_similarity(img1, img2, dino_model, device='cuda'):
    """Compute DINO cosine similarity between two images."""
    from torchvision import transforms

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    t1 = transform(img1).unsqueeze(0).to(device)
    t2 = transform(img2).unsqueeze(0).to(device)

    with torch.no_grad():
        feat1 = dino_model(t1).last_hidden_state[:, 0, :]  # CLS token
        feat2 = dino_model(t2).last_hidden_state[:, 0, :]

    feat1 = feat1 / feat1.norm(dim=-1, keepdim=True)
    feat2 = feat2 / feat2.norm(dim=-1, keepdim=True)

    sim = (feat1 * feat2).sum(dim=-1).item()
    return sim


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    # Checkpoint paths
    full_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
    attn2_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load CLIP
    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Load DINO
    print("Loading DINOv2 model...")
    dino_model = Dinov2Model.from_pretrained("facebook/dinov2-base").to(device)

    # Load pipeline
    pipeline = load_pipeline()

    # --- Zero-LoRA Identity Verification ---
    print('\n' + '=' * 60)
    print('Zero-LoRA Identity Verification')
    print('=' * 60)
    first_obj = test_objects[0]
    first_obj_path = os.path.join(TRAIN_DATA, first_obj)
    first_cond = Image.open(os.path.join(first_obj_path, 'image', '000.png')).convert('RGBA')
    first_normal, first_depth = create_combined_grids(first_obj_path)

    if first_normal is not None:
        ok = verify_zero_lora_identity(
            pipeline, first_cond, first_normal, first_depth,
            attn2_lora_path, merge_lora_into_unet_attn2_only, rank=4, alpha=4,
        )
        if not ok:
            print('\n*** ABORTING: Zero-LoRA identity check failed! ***')
            return

    results = []

    for obj_id in test_objects:
        print(f"\n{'=' * 60}")
        print(f"Processing: {obj_id}")
        print(f"{'=' * 60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_path = os.path.join(obj_path, 'image', '000.png')
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        gt_rgba = Image.open(cond_path).convert('RGBA')
        gt_rgb = Image.new('RGB', gt_rgba.size, (255, 255, 255))
        gt_rgb.paste(gt_rgba, mask=gt_rgba.split()[3])

        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: missing normal/depth views")
            continue

        cond_img = gt_rgba
        row = {'obj_id': obj_id}

        # --- Config A: Original ---
        print("  Config A: Original...")
        try:
            reload_base_weights(pipeline)
            verify_reference_attention(pipeline)
            img_a_full = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_a = extract_first_view(img_a_full)

            row['clip_a'] = compute_clip_similarity(gt_rgb, view_a, clip_model, clip_processor, device)
            row['dino_a'] = compute_dino_similarity(gt_rgb, view_a, dino_model, device)
            print(f"    CLIP Sim={row['clip_a']:.4f}, DINO Cos={row['dino_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_a'] = row['dino_a'] = None

        # --- Config B: Full LoRA ---
        print("  Config B: Full LoRA...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet(bare_unet, full_lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            img_b_full = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_b = extract_first_view(img_b_full)

            row['clip_b'] = compute_clip_similarity(gt_rgb, view_b, clip_model, clip_processor, device)
            row['dino_b'] = compute_dino_similarity(gt_rgb, view_b, dino_model, device)
            print(f"    CLIP Sim={row['clip_b']:.4f}, DINO Cos={row['dino_b']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_b'] = row['dino_b'] = None

        # --- Config C: attn2-only LoRA (scale=1.0) ---
        print("  Config C: attn2-only LoRA (scale=1.0)...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, attn2_lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            img_c_full = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_c = extract_first_view(img_c_full)

            row['clip_c'] = compute_clip_similarity(gt_rgb, view_c, clip_model, clip_processor, device)
            row['dino_c'] = compute_dino_similarity(gt_rgb, view_c, dino_model, device)
            print(f"    CLIP Sim={row['clip_c']:.4f}, DINO Cos={row['dino_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_c'] = row['dino_c'] = None

        # --- Config D: attn2-only LoRA (scale=0.25) ---
        print("  Config D: attn2-only LoRA (scale=0.25)...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, attn2_lora_path, rank=4, alpha=1)
            verify_reference_attention(pipeline)
            img_d_full = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_d = extract_first_view(img_d_full)

            row['clip_d'] = compute_clip_similarity(gt_rgb, view_d, clip_model, clip_processor, device)
            row['dino_d'] = compute_dino_similarity(gt_rgb, view_d, dino_model, device)
            print(f"    CLIP Sim={row['clip_d']:.4f}, DINO Cos={row['dino_d']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_d'] = row['dino_d'] = None

        results.append(row)

    # Save CSV
    csv_path = os.path.join(output_dir, 'eval_reference_consistency.csv')
    fieldnames = ['obj_id',
                  'clip_a', 'clip_b', 'clip_c', 'clip_d',
                  'dino_a', 'dino_b', 'dino_c', 'dino_d']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Compute averages
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avgs = {k: avg(k) for k in fieldnames if k != 'obj_id'}

    # Generate markdown report
    md_path = os.path.join(output_dir, 'eval_reference_consistency.md')
    with open(md_path, 'w') as f:
        f.write("# Reference Consistency Evaluation\n\n")
        f.write("**Metrics**: CLIP Similarity and DINO Cosine Similarity (vs Ground Truth)\n\n")
        f.write("**Pipeline**: ControlNet + depth/normal grids (correct inference path)\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Full LoRA)**: attn1+attn2 LoRA, rank=4, scale=1.0\n")
        f.write("- **C (attn2-only, s=1.0)**: attn2-only LoRA, rank=4, alpha=4, scale=1.0\n")
        f.write("- **D (attn2-only, s=0.25)**: attn2-only LoRA, rank=4, alpha=1, scale=0.25\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric | Original (A) | Full LoRA (B) | attn2-only s=1.0 (C) | attn2-only s=0.25 (D) |\n")
        f.write("|--------|--------------|---------------|----------------------|-----------------------|\n")
        f.write(f"| CLIP Sim ↑ | {avgs['clip_a']:.4f} | {avgs['clip_b']:.4f} | {avgs['clip_c']:.4f} | {avgs['clip_d']:.4f} |\n")
        f.write(f"| DINO Cos ↑ | {avgs['dino_a']:.4f} | {avgs['dino_b']:.4f} | {avgs['dino_c']:.4f} | {avgs['dino_d']:.4f} |\n")

        f.write("\n## Per-Object Results\n\n")
        f.write("| Object | CLIP_A | CLIP_B | CLIP_C | CLIP_D | DINO_A | DINO_B | DINO_C | DINO_D |\n")
        f.write("|--------|--------|--------|--------|--------|--------|--------|--------|--------|\n")
        for r in results:
            def fmt(key, prec=4):
                v = r.get(key)
                return f"{v:.{prec}f}" if v is not None else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | "
                    f"{fmt('clip_a')} | {fmt('clip_b')} | {fmt('clip_c')} | {fmt('clip_d')} | "
                    f"{fmt('dino_a')} | {fmt('dino_b')} | {fmt('dino_c')} | {fmt('dino_d')} |\n")

    print(f"\nReport saved to {md_path}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"{'Metric':<15} {'Original':>10} {'FullLoRA':>10} {'attn2 s1.0':>12} {'attn2 s0.25':>12}")
    print(f"{'-' * 60}")
    print(f"{'CLIP Sim ↑':<15} {avgs['clip_a']:>10.4f} {avgs['clip_b']:>10.4f} {avgs['clip_c']:>12.4f} {avgs['clip_d']:>12.4f}")
    print(f"{'DINO Cos ↑':<15} {avgs['dino_a']:>10.4f} {avgs['dino_b']:>10.4f} {avgs['dino_c']:>12.4f} {avgs['dino_d']:>12.4f}")


if __name__ == '__main__':
    main()
