"""
Scale Sweep: Test different LoRA scale values on the 250-step checkpoint.

FIXED: Uses ControlNet + depth grids (matching correct inference pipeline).
"""
import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA, psnr,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only


def merge_lora_with_scale(bare_unet, lora_path, rank, alpha, scale):
    """Merge LoRA weights with a custom scale factor."""
    effective_alpha = int(alpha * scale)
    merge_lora_into_unet_attn2_only(bare_unet, lora_path, rank=rank, alpha=effective_alpha)


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/scale_sweep_fixed'
    os.makedirs(output_dir, exist_ok=True)

    lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    # Test sample
    sample_obj = '00603cadc4474dafb78cdb55278568f2'
    sample_path = os.path.join(TRAIN_DATA, sample_obj, 'image', '000.png')
    if not os.path.exists(sample_path):
        # Fallback to first test object
        sample_obj = 'd6a5427888b8413fbfcbcaad14353af8'
        sample_path = os.path.join(TRAIN_DATA, sample_obj, 'image', '000.png')

    sample_image = Image.open(sample_path).convert('RGBA')
    obj_path = os.path.join(TRAIN_DATA, sample_obj)
    normal_grid, depth_grid = create_combined_grids(obj_path)

    if normal_grid is None:
        print("ERROR: Could not create depth/normal grids for test sample")
        return

    scales = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]

    # Load pipeline once
    pipeline = load_pipeline()

    # --- Zero-LoRA Identity Verification ---
    print('\n' + '=' * 60)
    print('Zero-LoRA Identity Verification')
    print('=' * 60)
    ok = verify_zero_lora_identity(
        pipeline, sample_image, normal_grid, depth_grid,
        lora_path, merge_lora_into_unet_attn2_only, rank=4, alpha=4,
    )
    if not ok:
        print('\n*** ABORTING: Zero-LoRA identity check failed! ***')
        return

    results = []

    # Generate zero-shot baseline
    print("=" * 60)
    print("Generating zero-shot baseline...")
    print("=" * 60)
    reload_base_weights(pipeline)
    verify_reference_attention(pipeline)
    img_zs = run_inference(pipeline, sample_image, normal_grid, depth_grid, seed=42)
    img_zs.save(os.path.join(output_dir, 'zeroshot.png'))

    # Test each scale
    for scale in scales:
        print(f"\n{'=' * 60}")
        print(f"Testing scale = {scale}")
        print(f"{'=' * 60}")

        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)

        if scale > 0:
            merge_lora_with_scale(bare_unet, lora_path, rank=4, alpha=4, scale=scale)

        verify_reference_attention(pipeline)
        img = run_inference(pipeline, sample_image, normal_grid, depth_grid, seed=42)
        img.save(os.path.join(output_dir, f'scale_{scale:.2f}.png'))

        p = psnr(img_zs, img)
        results.append({'scale': scale, 'psnr': p})
        print(f"Scale {scale:.2f}: PSNR = {p:.2f} dB")

    # Generate report
    print(f"\n{'=' * 60}")
    print("SCALE SWEEP RESULTS")
    print(f"{'=' * 60}")
    print(f"{'Scale':>8} {'PSNR (dB)':>12} {'Status':>10}")
    print("-" * 30)
    for r in results:
        status = 'IDENTICAL' if r['psnr'] > 50 else 'GOOD' if r['psnr'] > 25 else 'DIVERGING'
        print(f"{r['scale']:>8.2f} {r['psnr']:>12.2f} {status:>10}")

    # Save report
    report = f"""# Scale Sweep Report

## Configuration
- LoRA Checkpoint: 250-step attn2-only (rank=4, alpha=4)
- Test Sample: {sample_obj}
- Pipeline: ControlNet + depth/normal grids (correct inference path)
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
        recommended = good_scales[len(good_scales) // 2]
        report += f"""
## Recommendation

**Recommended scale: {recommended['scale']:.2f}** (PSNR = {recommended['psnr']:.2f} dB)

This scale provides a good balance between:
- Preserving zero-shot quality (PSNR > 25 dB)
- Allowing LoRA to have meaningful effect

## Usage

```python
merge_lora_with_scale(pipeline.unet.unet.unet, lora_path, rank=4, alpha=4, scale={recommended['scale']:.2f})
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
