"""
Evaluate attn1-only LoRA using the same approach as eval_reference_consistency.py.
Merges LoRA weights into UNet to avoid loading multiple pipelines.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, extract_first_view,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)
from mvpainter.lora_utils_attn1 import merge_lora_into_unet_attn1_only
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from transformers import CLIPModel, CLIPProcessor, Dinov2Model


def compute_clip_similarity(img1, img2, clip_model, clip_processor, device='cuda'):
    inputs1 = clip_processor(images=img1, return_tensors="pt").to(device)
    inputs2 = clip_processor(images=img2, return_tensors="pt").to(device)
    with torch.no_grad():
        features1 = clip_model.get_image_features(**inputs1)
        features2 = clip_model.get_image_features(**inputs2)
    features1 = features1 / features1.norm(dim=-1, keepdim=True)
    features2 = features2 / features2.norm(dim=-1, keepdim=True)
    return (features1 * features2).sum(dim=-1).item()


def compute_dino_similarity(img1, img2, dino_model, device='cuda'):
    from torchvision import transforms
    transform = transforms.Compose([
        transforms.Resize(224), transforms.CenterCrop(224),
        transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    t1 = transform(img1).unsqueeze(0).to(device)
    t2 = transform(img2).unsqueeze(0).to(device)
    with torch.no_grad():
        feat1 = dino_model(t1).last_hidden_state[:, 0, :]
        feat2 = dino_model(t2).last_hidden_state[:, 0, :]
    feat1 = feat1 / feat1.norm(dim=-1, keepdim=True)
    feat2 = feat2 / feat2.norm(dim=-1, keepdim=True)
    return (feat1 * feat2).sum(dim=-1).item()


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/ablation_attn1'
    os.makedirs(output_dir, exist_ok=True)

    attn1_lora_path = '/4T/CXY/MV-Painter/logs/mvpainter-lora-attn1-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'
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

    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    print("Loading DINOv2 model...")
    dino_model = Dinov2Model.from_pretrained("facebook/dinov2-base").to(device)

    pipeline = load_pipeline()

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

        # --- Config C: Attn1-only LoRA ---
        print("  Config C: Attn1-only LoRA...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn1_only(bare_unet, attn1_lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            img_c_full = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_c = extract_first_view(img_c_full)
            row['clip_c'] = compute_clip_similarity(gt_rgb, view_c, clip_model, clip_processor, device)
            row['dino_c'] = compute_dino_similarity(gt_rgb, view_c, dino_model, device)
            print(f"    CLIP Sim={row['clip_c']:.4f}, DINO Cos={row['dino_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_c'] = row['dino_c'] = None

        # --- Config D: RP-LoRA (attn2-only) ---
        print("  Config D: RP-LoRA (attn2-only)...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, attn2_lora_path, rank=4, alpha=4)
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

    # Print summary
    print("\n" + "=" * 80)
    print("ABLATION RESULTS: Layer Selection")
    print("=" * 80)

    def safe_mean(values):
        valid = [v for v in values if v is not None]
        return np.mean(valid) if valid else 0

    def safe_std(values):
        valid = [v for v in values if v is not None]
        return np.std(valid) if valid else 0

    metrics = {
        'Original (A)': {'clip': [r.get('clip_a') for r in results], 'dino': [r.get('dino_a') for r in results]},
        'Full LoRA (B)': {'clip': [r.get('clip_b') for r in results], 'dino': [r.get('dino_b') for r in results]},
        'Attn1-only (C)': {'clip': [r.get('clip_c') for r in results], 'dino': [r.get('dino_c') for r in results]},
        'RP-LoRA (D)': {'clip': [r.get('clip_d') for r in results], 'dino': [r.get('dino_d') for r in results]},
    }

    print(f"\n{'Method':<20} {'CLIP Sim':>15} {'DINO Cos':>15}")
    print("-" * 55)
    for name, m in metrics.items():
        clip_mean = safe_mean(m['clip'])
        clip_std = safe_std(m['clip'])
        dino_mean = safe_mean(m['dino'])
        dino_std = safe_std(m['dino'])
        print(f"{name:<20} {clip_mean:>7.4f}±{clip_std:.4f} {dino_mean:>7.4f}±{dino_std:.4f}")

    # Save results
    import json
    report = {
        'test_objects': test_objects,
        'results': results,
        'summary': {name: {
            'clip_mean': float(safe_mean(m['clip'])),
            'clip_std': float(safe_std(m['clip'])),
            'dino_mean': float(safe_mean(m['dino'])),
            'dino_std': float(safe_std(m['dino'])),
        } for name, m in metrics.items()},
    }
    with open(os.path.join(output_dir, 'layer_ablation_results.json'), 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nResults saved to {output_dir}/layer_ablation_results.json")


if __name__ == '__main__':
    main()
