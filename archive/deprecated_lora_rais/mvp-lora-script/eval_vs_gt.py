"""
Evaluate against Ground Truth.
Compute PSNR/SSIM of Original vs LoRA against GT rendered images.

FIXED: Uses ControlNet + depth grids (matching correct inference pipeline).
"""
import os
import sys
import torch
import numpy as np
import csv
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, extract_first_view, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA, psnr,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only


def ssim(img1, img2):
    """Compute SSIM between two PIL images."""
    from skimage.metrics import structural_similarity
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    try:
        win_size = min(7, min(a1.shape[0], a1.shape[1]))
        if win_size % 2 == 0:
            win_size -= 1
        if win_size < 3:
            return 0.0
        return structural_similarity(a1, a2, multichannel=True, win_size=win_size)
    except Exception:
        return 0.0


def load_ground_truth(obj_id, view_idx=0):
    """Load ground truth image for a specific object and view."""
    gt_path = os.path.join(TRAIN_DATA, obj_id, 'image', f'{view_idx:03d}.png')
    if os.path.exists(gt_path):
        img = Image.open(gt_path).convert('RGBA')
        img_rgb = Image.new('RGB', img.size, (255, 255, 255))
        img_rgb.paste(img, mask=img.split()[3])
        return img_rgb
    return None


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/eval_vs_gt_fixed'
    os.makedirs(output_dir, exist_ok=True)

    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    attn2_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

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
        print(f"Evaluating: {obj_id}")
        print(f"{'=' * 60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_path = os.path.join(obj_path, 'image', '000.png')
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')
        gt_view0 = load_ground_truth(obj_id, view_idx=0)
        if gt_view0 is None:
            print(f"  Skipping: GT not found")
            continue

        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: missing normal/depth views")
            continue

        # Config A: Original
        print("  Running Original...")
        try:
            reload_base_weights(pipeline)
            verify_reference_attention(pipeline)
            img_a = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_a = extract_first_view(img_a)
        except Exception as e:
            print(f"  Error: {e}")
            view_a = None

        # Config C: attn2-only LoRA (scale=1.0)
        print("  Running attn2-only LoRA (scale=1.0)...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, attn2_lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            img_c = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_c = extract_first_view(img_c)
        except Exception as e:
            print(f"  Error: {e}")
            view_c = None

        # Config D: attn2-only LoRA (scale=0.25)
        print("  Running attn2-only LoRA (scale=0.25)...")
        try:
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, attn2_lora_path, rank=4, alpha=1)
            verify_reference_attention(pipeline)
            img_d = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
            view_d = extract_first_view(img_d)
        except Exception as e:
            print(f"  Error: {e}")
            view_d = None

        # Compute metrics vs GT
        psnr_orig = psnr(gt_view0, view_a) if view_a else None
        psnr_lora_s1 = psnr(gt_view0, view_c) if view_c else None
        psnr_lora_s025 = psnr(gt_view0, view_d) if view_d else None
        ssim_orig = ssim(gt_view0, view_a) if view_a else None
        ssim_lora_s1 = ssim(gt_view0, view_c) if view_c else None
        ssim_lora_s025 = ssim(gt_view0, view_d) if view_d else None

        print(f"  PSNR Original vs GT: {psnr_orig:.2f} dB" if psnr_orig else "  PSNR Original: N/A")
        print(f"  PSNR attn2(s=1.0) vs GT: {psnr_lora_s1:.2f} dB" if psnr_lora_s1 else "  PSNR attn2(s=1.0): N/A")
        print(f"  PSNR attn2(s=0.25) vs GT: {psnr_lora_s025:.2f} dB" if psnr_lora_s025 else "  PSNR attn2(s=0.25): N/A")

        results.append({
            'obj_id': obj_id,
            'psnr_orig': psnr_orig,
            'psnr_lora_s1': psnr_lora_s1,
            'psnr_lora_s025': psnr_lora_s025,
            'ssim_orig': ssim_orig,
            'ssim_lora_s1': ssim_lora_s1,
            'ssim_lora_s025': ssim_lora_s025,
        })

    # Save results
    csv_path = os.path.join(output_dir, 'results.csv')
    fieldnames = ['obj_id', 'psnr_orig', 'psnr_lora_s1', 'psnr_lora_s025',
                  'ssim_orig', 'ssim_lora_s1', 'ssim_lora_s025']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Generate markdown report
    md_path = os.path.join(output_dir, 'results.md')
    with open(md_path, 'w') as f:
        f.write("# Evaluation vs Ground Truth\n\n")
        f.write("**Pipeline**: ControlNet + depth/normal grids (correct inference path)\n\n")
        f.write("| Object | PSNR_Orig | PSNR_attn2(s=1.0) | PSNR_attn2(s=0.25) | SSIM_Orig | SSIM_attn2(s=1.0) | SSIM_attn2(s=0.25) |\n")
        f.write("|--------|-----------|-------------------|--------------------|-----------|--------------------|--------------------|\n")
        for r in results:
            def fmt(key, prec=2):
                v = r.get(key)
                return f"{v:.{prec}f}" if v is not None else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | "
                    f"{fmt('psnr_orig')} | {fmt('psnr_lora_s1')} | {fmt('psnr_lora_s025')} | "
                    f"{fmt('ssim_orig', 4)} | {fmt('ssim_lora_s1', 4)} | {fmt('ssim_lora_s025', 4)} |\n")

        # Compute averages
        def avg(key):
            vals = [r[key] for r in results if r.get(key) is not None]
            return np.mean(vals) if vals else float('nan')

        f.write(f"\n## Averages\n\n")
        f.write(f"| Metric | Original | attn2-only (s=1.0) | attn2-only (s=0.25) |\n")
        f.write(f"|--------|----------|--------------------|--------------------|\n")
        f.write(f"| PSNR | {avg('psnr_orig'):.2f} dB | {avg('psnr_lora_s1'):.2f} dB | {avg('psnr_lora_s025'):.2f} dB |\n")
        f.write(f"| SSIM | {avg('ssim_orig'):.4f} | {avg('ssim_lora_s1'):.4f} | {avg('ssim_lora_s025'):.4f} |\n")

    print(f"\nResults saved to {output_dir}")


if __name__ == '__main__':
    main()
