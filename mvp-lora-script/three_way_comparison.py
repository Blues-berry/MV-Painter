"""
Task 3: Three-way comparison (Original / Broken LoRA / Working LoRA)
Generates paper-quality comparison figures.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
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


def create_comparison_figure(cond_img, img_a, img_b, img_c, labels, obj_id, save_path):
    """Create a 1-row, 3-column comparison figure."""
    from PIL import ImageDraw, ImageFont

    # Resize all images to same size
    target_size = (512, 512)
    cond_resized = cond_img.resize(target_size)
    img_a_resized = img_a.resize(target_size) if img_a else Image.new('RGB', target_size, (128, 128, 128))
    img_b_resized = img_b.resize(target_size) if img_b else Image.new('RGB', target_size, (128, 128, 128))
    img_c_resized = img_c.resize(target_size) if img_c else Image.new('RGB', target_size, (128, 128, 128))

    # Create figure: 1 row, 4 columns (condition + 3 configs)
    fig_width = target_size[0] * 4
    fig_height = target_size[1] + 40  # Extra space for labels
    fig = Image.new('RGB', (fig_width, fig_height), (255, 255, 255))

    # Paste images
    fig.paste(cond_resized, (0, 40))
    fig.paste(img_a_resized, (target_size[0], 40))
    fig.paste(img_b_resized, (target_size[0] * 2, 40))
    fig.paste(img_c_resized, (target_size[0] * 3, 40))

    # Add labels
    draw = ImageDraw.Draw(fig)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()

    labels_with_obj = [f"Condition", f"A: Original", f"B: Broken", f"C: attn2-only"]
    for i, label in enumerate(labels_with_obj):
        x = target_size[0] * i + 10
        draw.text((x, 10), label, fill=(0, 0, 0), font=font)

    # Add object ID
    draw.text((10, fig_height - 25), f"Object: {obj_id}", fill=(100, 100, 100), font=font)

    fig.save(save_path)
    return fig


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison'
    os.makedirs(output_dir, exist_ok=True)

    # Test objects
    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    # Checkpoint paths
    broken_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    all_results = []
    paper_figures = []

    for obj_id in test_objects:
        print(f"\n{'='*60}")
        print(f"Processing: {obj_id}")
        print(f"{'='*60}")

        cond_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')

        # Config A: Original (no LoRA)
        print("  Running Config A (Original)...")
        try:
            pipeline_a = load_pipeline(checkpoint_path, unet_ckpt_path)
            img_a = run_inference(pipeline_a, cond_img, seed=42)
            del pipeline_a
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"  Error Config A: {e}")
            img_a = None

        # Config B: Broken LoRA (attn1+attn2)
        print("  Running Config B (Broken LoRA)...")
        if os.path.exists(broken_lora_path):
            try:
                pipeline_b = load_pipeline(checkpoint_path, unet_ckpt_path)
                merge_lora_into_unet(pipeline_b.unet, broken_lora_path, rank=4, alpha=4)
                img_b = run_inference(pipeline_b, cond_img, seed=42)
                del pipeline_b
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"  Error Config B: {e}")
                img_b = None
        else:
            print(f"  Broken checkpoint not found: {broken_lora_path}")
            img_b = None

        # Config C: Working LoRA (attn2-only, scale=0.25)
        print("  Running Config C (attn2-only LoRA)...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, working_lora_path, rank=4, alpha=1)
            img_c = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"  Error Config C: {e}")
            img_c = None

        # Save individual images
        if img_a:
            img_a.save(os.path.join(output_dir, f'{obj_id}_original.png'))
        if img_b:
            img_b.save(os.path.join(output_dir, f'{obj_id}_broken.png'))
        if img_c:
            img_c.save(os.path.join(output_dir, f'{obj_id}_attn2only.png'))

        # Compute PSNR between configs
        psnr_ab = psnr(img_a, img_b) if img_a and img_b else None
        psnr_ac = psnr(img_a, img_c) if img_a and img_c else None

        print(f"  PSNR (A vs B): {psnr_ab:.2f} dB" if psnr_ab else "  PSNR (A vs B): N/A")
        print(f"  PSNR (A vs C): {psnr_ac:.2f} dB" if psnr_ac else "  PSNR (A vs C): N/A")

        # Create comparison figure
        fig_path = os.path.join(output_dir, f'{obj_id}_comparison.png')
        create_comparison_figure(cond_img, img_a, img_b, img_c, [], obj_id, fig_path)

        all_results.append({
            'obj_id': obj_id,
            'psnr_ab': psnr_ab,
            'psnr_ac': psnr_ac,
        })

        paper_figures.append({
            'obj_id': obj_id,
            'fig_path': fig_path,
        })

    # Create paper main figure (pick top 3)
    print("\n" + "="*60)
    print("Creating paper main figure...")
    print("="*60)

    if len(paper_figures) >= 3:
        selected = paper_figures[:3]
        create_paper_main_figure(selected, output_dir)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in all_results:
        print(f"{r['obj_id'][:20]:20s} PSNR(A vs B)={r['psnr_ab']:.2f if r['psnr_ab'] else 'N/A':>8} PSNR(A vs C)={r['psnr_ac']:.2f if r['psnr_ac'] else 'N/A':>8}")

    print(f"\nOutput saved to {output_dir}")


def create_paper_main_figure(figures, output_dir):
    """Create a tall paper figure with 3 objects stacked vertically."""
    from PIL import Image as PILImage

    images = []
    for fig_info in figures:
        img = PILImage.open(fig_info['fig_path'])
        images.append(img)

    # Stack vertically
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    paper_fig = PILImage.new('RGB', (total_width, total_height), (255, 255, 255))
    y_offset = 0
    for img in images:
        paper_fig.paste(img, (0, y_offset))
        y_offset += img.height

    save_path = os.path.join(output_dir, '..', 'paper_main_figure.png')
    paper_fig.save(save_path, dpi=(150, 150))
    print(f"Paper main figure saved to {save_path}")


if __name__ == '__main__':
    main()
