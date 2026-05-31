"""
Task 5: Training steps comparison figure.
Compare 100/250/500 steps checkpoints on representative objects.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from diffusers import EulerAncestralDiscreteScheduler


def load_pipeline(checkpoint_path, unet_ckpt_path, device='cuda'):
    """Load base pipeline."""
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
    """Run inference with fixed seed."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')
    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def psnr(img1, img2):
    """Compute PSNR."""
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0**2 / mse)


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput'
    os.makedirs(output_dir, exist_ok=True)

    # Representative test objects
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

    # Generate images for each object and step
    all_images = {}  # {obj_id: {step: (image, psnr_vs_orig)}}

    for obj_id in test_objects:
        print(f"\nProcessing: {obj_id}")
        cond_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(cond_path):
            print(f"  Skipping: not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')
        all_images[obj_id] = {}

        # Get original (step 0)
        print("  Running original (step 0)...")
        pipeline = load_pipeline(checkpoint_path, unet_ckpt_path)
        img_orig = run_inference(pipeline, cond_img, seed=42)
        del pipeline
        torch.cuda.empty_cache()
        all_images[obj_id][0] = (img_orig, float('inf'))

        # Get LoRA results for each step
        for steps, lora_path in checkpoints.items():
            if steps == 0:
                continue
            if not os.path.exists(lora_path):
                print(f"  Step {steps}: checkpoint not found")
                continue

            print(f"  Running step {steps}...")
            pipeline = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline.unet, lora_path, rank=4, alpha=1)
            img = run_inference(pipeline, cond_img, seed=42)
            del pipeline
            torch.cuda.empty_cache()

            p = psnr(img_orig, img) if img_orig and img else None
            all_images[obj_id][steps] = (img, p)
            print(f"    PSNR vs original: {p:.2f} dB" if p else "    PSNR: N/A")

    # Create comparison figure
    print("\nCreating comparison figure...")

    # Layout: rows = objects, cols = steps (0, 100, 250, 500)
    steps_list = [0, 100, 250, 500]
    cell_size = (256, 256)
    label_height = 30

    n_rows = len(all_images)
    n_cols = len(steps_list)

    fig_width = cell_size[0] * n_cols + 100  # Extra space for row labels
    fig_height = (cell_size[1] + label_height) * n_rows + 60  # Extra for header

    fig = Image.new('RGB', (fig_width, fig_height), (255, 255, 255))
    draw = ImageDraw.Draw(fig)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        font = ImageFont.load_default()
        font_small = font

    # Header
    for j, step in enumerate(steps_list):
        x = 100 + cell_size[0] * j + 10
        label = f"Original" if step == 0 else f"{step} steps"
        draw.text((x, 10), label, fill=(0, 0, 0), font=font)

    # Rows
    for i, (obj_id, step_data) in enumerate(all_images.items()):
        y_base = 40 + i * (cell_size[1] + label_height)

        # Row label
        draw.text((5, y_base + cell_size[1] // 2), obj_id[:12], fill=(100, 100, 100), font=font_small)

        for j, step in enumerate(steps_list):
            x = 100 + cell_size[0] * j

            if step in step_data:
                img, p = step_data[step]
                if img:
                    img_resized = img.resize(cell_size)
                    fig.paste(img_resized, (x, y_base))

                # PSNR label
                if p is not None and p != float('inf'):
                    draw.text((x + 5, y_base + cell_size[1] + 5), f"PSNR: {p:.1f}", fill=(0, 100, 0), font=font_small)
                elif p == float('inf'):
                    draw.text((x + 5, y_base + cell_size[1] + 5), "Original", fill=(0, 0, 200), font=font_small)

    save_path = os.path.join(output_dir, 'steps_comparison.png')
    fig.save(save_path, dpi=(150, 150))
    print(f"Saved to {save_path}")


if __name__ == '__main__':
    main()
