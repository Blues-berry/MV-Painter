"""
Training steps comparison figure.
Compare 100/250/500 steps checkpoints on representative objects.

FIXED: Uses ControlNet + depth grids (matching correct inference pipeline).
"""
import os
import sys
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA, psnr,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput'
    os.makedirs(output_dir, exist_ok=True)

    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
    ]

    # Checkpoint paths for different steps
    checkpoints = {
        0: None,  # Original (no LoRA)
        100: '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-lora-attn2-only-r4-lr1e5/lora_checkpoints/lora_step_0000100.safetensors',
        250: '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors',
        500: '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-500-lora-attn2-only-r4-lr1e5-500/lora_checkpoints/lora_step_0000500.safetensors',
    }

    # Load pipeline once
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
        # Check with one of the available checkpoints
        for steps, lora_path in checkpoints.items():
            if lora_path and os.path.exists(lora_path):
                ok = verify_zero_lora_identity(
                    pipeline, first_cond, first_normal, first_depth,
                    lora_path, merge_lora_into_unet_attn2_only, rank=4, alpha=4,
                )
                if not ok:
                    print('\n*** ABORTING: Zero-LoRA identity check failed! ***')
                    return
                break

    # Generate images for each object and step
    all_images = {}  # {obj_id: {step: (image, psnr_vs_orig)}}

    for obj_id in test_objects:
        print(f"\nProcessing: {obj_id}")
        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_path = os.path.join(obj_path, 'image', '000.png')
        if not os.path.exists(cond_path):
            print(f"  Skipping: not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: missing normal/depth views")
            continue

        all_images[obj_id] = {}

        # Get original (step 0)
        print("  Running original (step 0)...")
        reload_base_weights(pipeline)
        verify_reference_attention(pipeline)
        img_orig = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        all_images[obj_id][0] = (img_orig, float('inf'))

        # Get LoRA results for each step
        for steps, lora_path in checkpoints.items():
            if steps == 0:
                continue
            if not os.path.exists(lora_path):
                print(f"  Step {steps}: checkpoint not found")
                continue

            print(f"  Running step {steps}...")
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            merge_lora_into_unet_attn2_only(bare_unet, lora_path, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            img = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)

            p = psnr(img_orig, img) if img_orig and img else None
            all_images[obj_id][steps] = (img, p)
            print(f"    PSNR vs original: {p:.2f} dB" if p else "    PSNR: N/A")

    # Create comparison figure
    print("\nCreating comparison figure...")

    steps_list = [0, 100, 250, 500]
    cell_size = (256, 256)
    label_height = 30

    n_rows = len(all_images)
    n_cols = len(steps_list)

    fig_width = cell_size[0] * n_cols + 100
    fig_height = (cell_size[1] + label_height) * n_rows + 60

    fig = Image.new('RGB', (fig_width, fig_height), (255, 255, 255))
    draw = ImageDraw.Draw(fig)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_small = font

    # Header
    for j, step in enumerate(steps_list):
        x = 100 + cell_size[0] * j + 10
        label = "Original" if step == 0 else f"{step} steps"
        draw.text((x, 10), label, fill=(0, 0, 0), font=font)

    # Rows
    for i, (obj_id, step_data) in enumerate(all_images.items()):
        y_base = 40 + i * (cell_size[1] + label_height)

        draw.text((5, y_base + cell_size[1] // 2), obj_id[:12], fill=(100, 100, 100), font=font_small)

        for j, step in enumerate(steps_list):
            x = 100 + cell_size[0] * j

            if step in step_data:
                img, p = step_data[step]
                if img:
                    img_resized = img.resize(cell_size)
                    fig.paste(img_resized, (x, y_base))

                if p is not None and p != float('inf'):
                    draw.text((x + 5, y_base + cell_size[1] + 5), f"PSNR: {p:.1f}", fill=(0, 100, 0), font=font_small)
                elif p == float('inf'):
                    draw.text((x + 5, y_base + cell_size[1] + 5), "Original", fill=(0, 0, 200), font=font_small)

    save_path = os.path.join(output_dir, 'steps_comparison_fixed.png')
    fig.save(save_path, dpi=(150, 150))
    print(f"Saved to {save_path}")


if __name__ == '__main__':
    main()
