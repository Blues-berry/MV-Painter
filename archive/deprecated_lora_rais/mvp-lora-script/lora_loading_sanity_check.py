"""
Phase 5: LoRA Loading Sanity Check
Test if LoRA loading logic is correct by creating zero/tiny LoRA weights.
"""
import os
import sys
import json
import torch
import numpy as np
from PIL import Image
from safetensors.torch import save_file, load_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from mvpainter.lora_utils import create_lora_processors, merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler


def create_zero_lora_from_checkpoint(existing_ckpt_path, rank=8, alpha=8):
    """Create a zero LoRA checkpoint based on an existing checkpoint structure."""
    print("Creating zero LoRA checkpoint from existing structure...")

    # Load existing checkpoint to get structure
    existing = load_file(existing_ckpt_path)

    # Create zero weights with same structure
    lora_state = {}
    for k, v in existing.items():
        lora_state[k] = torch.zeros_like(v)

    return lora_state


def create_tiny_random_lora_from_checkpoint(existing_ckpt_path, rank=8, alpha=8, scale=0.001):
    """Create a tiny random LoRA checkpoint based on an existing checkpoint structure."""
    print(f"Creating tiny random LoRA checkpoint (scale={scale})...")

    # Load existing checkpoint to get structure
    existing = load_file(existing_ckpt_path)

    # Create tiny random weights with same structure
    lora_state = {}
    for k, v in existing.items():
        lora_state[k] = torch.randn_like(v) * scale

    return lora_state


def run_inference(pipeline, sample_image_path, output_path, num_steps=50):
    """Run inference and save output."""
    print(f"Running inference...")

    # Load sample image with alpha channel (RGBA)
    sample_image = Image.open(sample_image_path).convert('RGBA')

    # Run inference
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(
            sample_image,
            num_inference_steps=num_steps,
            output_type='pil',
        )

    # Save output
    if isinstance(output, list) and len(output) >= 1:
        output[0].save(output_path)
        print(f"Output saved to {output_path}")
        return output[0]
    else:
        print(f"Unexpected output type: {type(output)}")
        return None


def compare_images(img1_path, img2_path, output_path):
    """Compare two images and compute metrics."""
    from skimage.metrics import peak_signal_noise_ratio, structural_similarity

    img1 = np.array(Image.open(img1_path).convert('RGB'))
    img2 = np.array(Image.open(img2_path).convert('RGB'))

    # Resize if needed
    if img1.shape != img2.shape:
        from PIL import Image as PILImage
        img2_pil = PILImage.open(img2_path).convert('RGB')
        img2_pil = img2_pil.resize((img1.shape[1], img1.shape[0]))
        img2 = np.array(img2_pil)

    # Compute metrics
    psnr = peak_signal_noise_ratio(img1, img2)

    # Use smaller win_size for small images
    min_side = min(img1.shape[0], img1.shape[1])
    win_size = min(7, min_side if min_side % 2 == 1 else min_side - 1)
    if win_size < 3:
        win_size = 3

    try:
        ssim = structural_similarity(img1, img2, multichannel=True, win_size=win_size)
    except Exception as e:
        print(f"SSIM calculation failed: {e}")
        ssim = 0.0

    # Compute difference image
    diff = np.abs(img1.astype(float) - img2.astype(float))
    diff_img = Image.fromarray(diff.astype(np.uint8))
    diff_img.save(output_path)

    return psnr, ssim


def main():
    output_dir = '/4T/CXY/MV-Painter/lora_loading_sanity_check'
    os.makedirs(output_dir, exist_ok=True)

    # Load pipeline
    print("Loading pipeline...")
    checkpoint_path = '../checkpoints/hf_repo'
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Load custom UNet
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(unet_ckpt_path):
        from safetensors.torch import load_file
        print(f"Loading custom UNet from {unet_ckpt_path} ...")
        ckpt = load_file(unet_ckpt_path)
        unet_state = {}
        for k, v in ckpt.items():
            if k.startswith('unet.unet.'):
                new_key = k[len('unet.unet.'):]
                unet_state[new_key] = v
        if unet_state:
            pipeline.unet.load_state_dict(unet_state, strict=False)

    pipeline = pipeline.to('cuda')

    # Sample image for testing
    sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcb/image/000.png'
    if not os.path.exists(sample_image_path):
        # Try another sample
        sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/00603cadc4474dafb78cdb55278568f2/image/000.png'

    if not os.path.exists(sample_image_path):
        print("ERROR: No sample image found")
        return

    # Test 1: Zero-shot (no LoRA)
    print("\n" + "="*60)
    print("TEST 1: Zero-shot (no LoRA)")
    print("="*60)
    zeroshot_path = os.path.join(output_dir, 'zeroshot.png')
    run_inference(pipeline, sample_image_path, zeroshot_path)

    # Find existing LoRA checkpoint to use as template
    existing_ckpt_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'

    if not os.path.exists(existing_ckpt_path):
        print(f"ERROR: No existing LoRA checkpoint found at {existing_ckpt_path}")
        return

    # Test 2: Zero LoRA (all weights zero)
    print("\n" + "="*60)
    print("TEST 2: Zero LoRA (scale=1.0)")
    print("="*60)

    # Create zero LoRA
    zero_lora_state = create_zero_lora_from_checkpoint(existing_ckpt_path, rank=8, alpha=8)
    zero_lora_path = os.path.join(output_dir, 'zero_lora.safetensors')
    save_file(zero_lora_state, zero_lora_path)
    print(f"Zero LoRA saved to {zero_lora_path}")

    # Reload pipeline and merge zero LoRA
    pipeline2 = MVPainter_Pipeline.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipeline2.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline2.scheduler.config, timestep_spacing='trailing',
    )
    if unet_state:
        pipeline2.unet.load_state_dict(unet_state, strict=False)
    pipeline2 = pipeline2.to('cuda')

    merge_lora_into_unet(pipeline2.unet, zero_lora_path, rank=8, alpha=8)
    zero_lora_output_path = os.path.join(output_dir, 'zero_lora_output.png')
    run_inference(pipeline2, sample_image_path, zero_lora_output_path)

    # Compare
    diff_path = os.path.join(output_dir, 'diff_zeroshot_vs_zero_lora.png')
    psnr, ssim = compare_images(zeroshot_path, zero_lora_output_path, diff_path)
    print(f"\nComparison: Zero-shot vs Zero LoRA")
    print(f"  PSNR: {psnr:.2f} dB (>30 is good)")
    print(f"  SSIM: {ssim:.4f} (>0.9 is good)")

    # Test 3: Tiny random LoRA with different scales
    for scale in [0.001, 0.01, 0.1]:
        print("\n" + "="*60)
        print(f"TEST 3: Tiny random LoRA (scale={scale})")
        print("="*60)

        # Create tiny random LoRA
        tiny_lora_state = create_tiny_random_lora_from_checkpoint(existing_ckpt_path, rank=8, alpha=8, scale=scale)
        tiny_lora_path = os.path.join(output_dir, f'tiny_random_lora_scale{scale}.safetensors')
        save_file(tiny_lora_state, tiny_lora_path)
        print(f"Tiny random LoRA saved to {tiny_lora_path}")

        # Reload pipeline and merge tiny LoRA
        pipeline3 = MVPainter_Pipeline.from_pretrained(
            checkpoint_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        pipeline3.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline3.scheduler.config, timestep_spacing='trailing',
        )
        if unet_state:
            pipeline3.unet.load_state_dict(unet_state, strict=False)
        pipeline3 = pipeline3.to('cuda')

        merge_lora_into_unet(pipeline3.unet, tiny_lora_path, rank=8, alpha=8)
        tiny_lora_output_path = os.path.join(output_dir, f'tiny_random_lora_scale{scale}_output.png')
        run_inference(pipeline3, sample_image_path, tiny_lora_output_path)

        # Compare
        diff_path = os.path.join(output_dir, f'diff_zeroshot_vs_tiny_lora_scale{scale}.png')
        psnr, ssim = compare_images(zeroshot_path, tiny_lora_output_path, diff_path)
        print(f"\nComparison: Zero-shot vs Tiny LoRA (scale={scale})")
        print(f"  PSNR: {psnr:.2f} dB (>30 is good)")
        print(f"  SSIM: {ssim:.4f} (>0.9 is good)")

    # Generate report
    generate_report(output_dir)


def generate_report(output_dir):
    """Generate sanity check report."""
    report = """# LoRA Loading Sanity Check Report

## Test Overview

This test verifies that the LoRA loading and merging logic is correct by testing with:
1. Zero-shot (no LoRA) - baseline
2. Zero LoRA (all weights zero) - should be identical to zero-shot
3. Tiny random LoRA (various scales) - should be close to zero-shot

## Expected Results

| Test | Expected PSNR | Expected SSIM | Interpretation |
|------|---------------|---------------|----------------|
| Zero LoRA | >40 dB | >0.99 | Should be identical to zero-shot |
| Tiny LoRA (0.001) | >35 dB | >0.98 | Should be very close to zero-shot |
| Tiny LoRA (0.01) | >25 dB | >0.90 | Should be similar to zero-shot |
| Tiny LoRA (0.1) | >15 dB | >0.70 | May show visible differences |

## Actual Results

Check the output images in the sanity check directory:
- `zeroshot.png` - Baseline (no LoRA)
- `zero_lora_output.png` - With zero LoRA
- `tiny_random_lora_scale*_output.png` - With tiny random LoRA

## Diagnosis

### If Zero LoRA ≈ Zero-shot (PSNR > 40 dB)
✅ LoRA loading and merging logic is correct. The issue is in the training process.

### If Zero LoRA ≠ Zero-shot (PSNR < 30 dB)
❌ LoRA loading or merging logic has a bug. Check:
1. Key mapping in merge_lora_into_unet
2. Weight scaling (alpha/rank)
3. Processor replacement logic

### If Tiny LoRA (0.001) causes black/noisy output
❌ LoRA injection is fundamentally broken. Check:
1. LoRA is applied to wrong layers
2. LoRA disrupts reference attention
3. Scaling is incorrect

## Conclusion

Based on the results:
- If Zero LoRA works: The training process is the issue
- If Zero LoRA fails: The loading logic is the issue
- If Tiny LoRA causes problems: The LoRA placement is the issue

## Recommendations

1. If loading logic is correct (Zero LoRA works):
   - Focus on training hyperparameters
   - Try attn2-only LoRA
   - Reduce learning rate

2. If loading logic is broken:
   - Fix merge_lora_into_unet
   - Check key naming conventions
   - Verify scaling computation

3. If LoRA placement is the issue:
   - Only apply LoRA to attn2
   - Preserve reference attention mechanism
"""

    report_path = os.path.join(output_dir, 'lora_loading_sanity_report.md')
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {report_path}")


if __name__ == '__main__':
    main()
