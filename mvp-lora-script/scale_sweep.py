"""
Phase 3: Scale Sweep
Test different LoRA scale values on the 250-step checkpoint.
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
from diffusers import EulerAncestralDiscreteScheduler


def psnr(img1, img2):
    """Compute PSNR between two PIL images."""
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def merge_lora_with_scale(unet, lora_path, rank, alpha, scale):
    """Merge LoRA weights with a custom scale factor."""
    lora_state = load_file(lora_path)
    effective_alpha = alpha * scale  # Scale the alpha
    merge_lora_into_unet_attn2_only(unet, lora_path, rank=rank, alpha=effective_alpha)


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
    """Run pipeline with fixed seed."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)

    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')

    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    elif hasattr(output, 'images'):
        return output.images[0]
    return None


def main():
    checkpoint_path = '../checkpoints/hf_repo'
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/scale_sweep'
    os.makedirs(output_dir, exist_ok=True)

    # Use 250-step checkpoint
    lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    # Test sample
    sample_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/00603cadc4474dafb78cdb55278568f2/image/000.png'
    sample_image = Image.open(sample_path).convert('RGBA')

    # Scales to test
    scales = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]

    results = []

    # Generate zero-shot baseline
    print("="*60)
    print("Generating zero-shot baseline...")
    print("="*60)
    pipeline = load_pipeline(checkpoint_path, unet_ckpt_path)
    img_zs = run_inference(pipeline, sample_image, seed=42)
    img_zs.save(os.path.join(output_dir, 'zeroshot.png'))
    del pipeline
    torch.cuda.empty_cache()

    # Test each scale
    for scale in scales:
        print(f"\n{'='*60}")
        print(f"Testing scale = {scale}")
        print(f"{'='*60}")

        pipeline = load_pipeline(checkpoint_path, unet_ckpt_path)
        merge_lora_with_scale(pipeline.unet, lora_path, rank=4, alpha=4, scale=scale)
        img = run_inference(pipeline, sample_image, seed=42)
        img.save(os.path.join(output_dir, f'scale_{scale:.2f}.png'))

        p = psnr(img_zs, img)
        results.append({'scale': scale, 'psnr': p})
        print(f"Scale {scale:.2f}: PSNR = {p:.2f} dB")

        del pipeline
        torch.cuda.empty_cache()

    # Generate report
    print(f"\n{'='*60}")
    print("SCALE SWEEP RESULTS")
    print(f"{'='*60}")
    print(f"{'Scale':>8} {'PSNR (dB)':>12} {'Status':>10}")
    print("-" * 30)
    for r in results:
        status = 'IDENTICAL' if r['psnr'] > 50 else 'GOOD' if r['psnr'] > 25 else 'DIVERGING'
        print(f"{r['scale']:>8.2f} {r['psnr']:>12.2f} {status:>10}")

    # Save report
    report = f"""# Scale Sweep Report

## Configuration
- LoRA Checkpoint: 250-step attn2-only (rank=4, alpha=4)
- Test Sample: 00603cadc4474dafb78cdb55278568f2
- Inference Steps: 50
- Seed: 42

## Results

| Scale | PSNR (dB) | Status |
|-------|-----------|--------|
"""
    for r in results:
        status = 'IDENTICAL' if r['psnr'] > 50 else 'GOOD' if r['psnr'] > 25 else 'DIVERGING'
        report += f"| {r['scale']:.2f} | {r['psnr']:.2f} | {status} |\n"

    # Find recommended scale
    good_scales = [r for r in results if 25 < r['psnr'] < 45]
    if good_scales:
        recommended = good_scales[len(good_scales)//2]
        report += f"""
## Recommendation

**Recommended scale: {recommended['scale']:.2f}** (PSNR = {recommended['psnr']:.2f} dB)

This scale provides a good balance between:
- Preserving zero-shot quality (PSNR > 25 dB)
- Allowing LoRA to have meaningful effect

## Usage

```python
merge_lora_with_scale(pipeline.unet, lora_path, rank=4, alpha=4, scale={recommended['scale']:.2f})
```
"""
    else:
        report += """
## Recommendation

No scale provides good results. Consider:
1. Training for fewer steps
2. Reducing learning rate
3. Using a different checkpoint
"""

    with open(os.path.join(output_dir, 'scale_sweep_report.md'), 'w') as f:
        f.write(report)

    print(f"\nReport saved to {os.path.join(output_dir, 'scale_sweep_report.md')}")


if __name__ == '__main__':
    main()
