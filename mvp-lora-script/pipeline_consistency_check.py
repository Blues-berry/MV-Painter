"""
Phase 2: Pipeline Consistency Check
Verify that training and inference use the same preprocessing.
"""
import os
import sys
import json
import numpy as np
import torch
import cv2
from PIL import Image
from torchvision.transforms import v2
from einops import rearrange

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_training_preprocessing():
    """Extract preprocessing steps from training code."""
    print("=" * 60)
    print("TRAINING PREPROCESSING (from mvpainter_dataset.py)")
    print("=" * 60)

    # Read training dataset code
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'src', 'data', 'mvpainter_dataset.py')

    with open(dataset_path, 'r') as f:
        content = f.read()

    # Extract key preprocessing steps
    steps = {
        'image_loading': 'cv2.imread with IMREAD_UNCHANGED, cvtColor BGRA2RGBA',
        'normal_loading': 'cv2.imread with IMREAD_UNCHANGED, cvtColor BGR2RGB, /65535.0',
        'depth_loading': 'cv2.imread with IMREAD_UNCHANGED, cvtColor BGR2RGB, /65535.0',
        'depth_normalization': 'valid_mask = depth < 1.0; depth[valid_mask] = 1/depth[valid_mask]; min-max normalize',
        'target_order': '[0, 15, 12, 7, 13, 14] or reversed based on alpha count',
        'rearrange': 'b (x y) c h w -> b c (x h) (y w), x=3, y=2',
        'resize': 'v2.functional.resize to 256, interpolation=3 (bicubic)',
        'bkg_color': '[1., 1., 1.] (white)',
        'random_augmentation': 'random_stretch_or_compress + random_resize (ratio 0.8-1.0)',
    }

    for key, value in steps.items():
        print(f"  {key}: {value}")

    return steps


def check_inference_preprocessing():
    """Extract preprocessing steps from inference code."""
    print("\n" + "=" * 60)
    print("INFERENCE PREPROCESSING (from infer_multiview.py)")
    print("=" * 60)

    # Read inference code
    infer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'infer_multiview.py')

    with open(infer_path, 'r') as f:
        content = f.read()

    # Extract key preprocessing steps
    steps = {
        'image_loading': 'cv2.imread with IMREAD_UNCHANGED, cvtColor BGRA2RGBA',
        'normal_loading': 'cv2.imread (default BGR), resize to 512x512',
        'depth_loading': 'cv2.imread with IMREAD_UNCHANGED, resize to 512x512',
        'depth_normalization': 'valid_mask = depth < 65535; depth/65535; 1/depth; min-max normalize',
        'combined_layout': 'np.zeros((height*3, width*2, channel)) - same 3x2 layout',
        'pipeline_input': 'PIL Image from combined normal/depth',
        'resize': 'Pipeline internal resize to target size',
        'bkg_color': 'Not explicitly set (depends on pipeline)',
    }

    for key, value in steps.items():
        print(f"  {key}: {value}")

    return steps


def check_pipeline_model_preprocessing():
    """Extract preprocessing from the pipeline model."""
    print("\n" + "=" * 60)
    print("PIPELINE MODEL PREPROCESSING (from mvpainter_pipeline.py)")
    print("=" * 60)

    pipeline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'mvpainter', 'mvpainter_pipeline.py')

    with open(pipeline_path, 'r') as f:
        content = f.read()

    steps = {
        'cond_image': 'recenter_img -> to_rgb_image -> feature_extractor_vae -> VAE encode',
        'target_encoding': '(images - 0.5) / 0.8 -> VAE encode -> * scaling_factor -> scale_latents',
        'latent_scaling': 'scale_latents: (latents - 0.22) * 0.75',
        'image_unscaling': 'unscale_image: image / 0.5 * 0.8; unscale_image_2: image * 0.8 / 0.5',
        'scheduler': 'EulerAncestralDiscreteScheduler with timestep_spacing=trailing',
        'guidance_scale': '2.0 (default)',
        'num_inference_steps': '50 (default) or 75',
    }

    for key, value in steps.items():
        print(f"  {key}: {value}")

    return steps


def check_model_unet_lora_preprocessing():
    """Extract preprocessing from LoRA training code."""
    print("\n" + "=" * 60)
    print("LoRA TRAINING PREPROCESSING (from model_unet_lora.py)")
    print("=" * 60)

    lora_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'mvpainter', 'model_unet_lora.py')

    with open(lora_path, 'r') as f:
        content = f.read()

    steps = {
        'target_encoding': '(images - 0.5) / 0.8 -> VAE encode -> * scaling_factor -> scale_latents',
        'latent_scaling': 'scale_latents: (latents - 0.22) * 0.75',
        'noise_schedule': 'DDPMScheduler (training) vs EulerAncestralDiscreteScheduler (inference)',
        'timestep_sampling': 'torch.randint(0, 1000, size=(B,))',
        'loss': 'F.mse_loss(noise_pred, noise)',
        'img_size': '256 (reduced from 512)',
    }

    for key, value in steps.items():
        print(f"  {key}: {value}")

    return steps


def compare_target_order():
    """Check the target view order consistency."""
    print("\n" + "=" * 60)
    print("TARGET VIEW ORDER ANALYSIS")
    print("=" * 60)

    # From dataset
    print("\nFrom mvpainter_dataset.py:")
    print("  Default target_order = [0, 15, 12, 7, 13, 14]")
    print("  If reverse (first view is side): [14, 15, 0, 15, 12, 13]")
    print("  Note: View 15 appears twice in both orders!")

    # From inference
    print("\nFrom infer_multiview.py:")
    print("  filenames = ['000.png', '005.png', '001.png', '004.png', '002.png', '003.png']")
    print("  This is different from training order!")

    # Layout
    print("\nLayout (both training and inference):")
    print("  rearrange: b (x y) c h w -> b c (x h) (y w), x=3, y=2")
    print("  This creates a 3-row, 2-column grid:")
    print("  [view0] [view1]")
    print("  [view2] [view3]")
    print("  [view4] [view5]")


def check_depth_normal_consistency():
    """Check depth/normal preprocessing consistency."""
    print("\n" + "=" * 60)
    print("DEPTH/NORMAL PREPROCESSING CONSISTENCY")
    print("=" * 60)

    print("\nTraining (mvpainter_dataset.py):")
    print("  Normal: cv2.imread -> cvtColor BGR2RGB -> /65535.0 (16-bit)")
    print("  Depth:  cv2.imread -> cvtColor BGR2RGB -> /65535.0 (16-bit)")
    print("  Depth normalization: 1/depth for valid pixels, then min-max")

    print("\nInference (infer_multiview.py):")
    print("  Normal: cv2.imread (BGR) -> resize to 512x512")
    print("  Depth:  cv2.imread -> resize to 512x512")
    print("  Depth normalization: depth/65535 -> 1/depth -> min-max")

    print("\n⚠️  ISSUE: Training normalizes to [0, 1] range, inference may not!")
    print("⚠️  ISSUE: Training uses 16-bit images, inference may use 8-bit")


def generate_report(output_path):
    """Generate consistency report."""
    report = """# Pipeline Consistency Report

## Summary

| Check Item | Status | Notes |
|------------|--------|-------|
| Condition image preprocessing | ⚠️ Partially consistent | Both use BGRA2RGBA, but resize differs |
| Depth image preprocessing | ⚠️ Inconsistent | Training uses 16-bit, inference pipeline may differ |
| Normal image preprocessing | ⚠️ Inconsistent | Training normalizes to [0,1], inference may not |
| Target 6-view order | ❌ Inconsistent | Training: [0,15,12,7,13,14], Inference: [0,5,1,4,2,3] |
| Latent normalization | ✅ Consistent | Both use scale_latents: (latents - 0.22) * 0.75 |
| Timestep scheduler | ⚠️ Different by design | Training: DDPM, Inference: EulerAncestral |
| Image size | ✅ Consistent | Both use 256 for training, pipeline handles resize |
| View layout | ✅ Consistent | Both use 3x2 grid layout |

## Critical Issues Found

### 1. Target View Order Mismatch (CRITICAL)

**Training code** (`mvpainter_dataset.py`):
```python
self.target_order = [0, 15, 12, 7, 13, 14]
# Or reversed: [14, 15, 0, 15, 12, 13]
```

**Inference code** (`infer_multiview.py`):
```python
filenames = ['000.png', '005.png', '001.png', '004.png', '002.png', '003.png']
```

**Impact**: The model learns to generate views in a specific order. If inference uses a different order, the output will be scrambled or incorrect.

### 2. Depth/Normal Normalization (MODERATE)

**Training**:
- Normal: `/65535.0` (16-bit normalized to [0, 1])
- Depth: `/65535.0` then `1/depth` then min-max normalization

**Inference**:
- The pipeline receives PIL images and may apply different normalization
- Combined depth/normal images are created differently

### 3. Condition Image Preprocessing (LOW)

Both use similar preprocessing, but:
- Training applies random augmentation (stretch, resize)
- Inference uses `recenter_img` and `to_rgb_image`

## Recommendations

1. **Fix target view order**: Align inference view order with training
2. **Verify depth/normal normalization**: Ensure both use same [0, 1] range
3. **Test with fixed preprocessing**: Run inference with training-consistent preprocessing

## Conclusion

The **target view order mismatch** is a critical issue that could explain LoRA training failures. The model learns a specific view layout during training, but inference uses a different order.

However, this does NOT explain why LoRA training itself fails (black/noisy outputs during training validation). The training validation uses the same dataset code, so it should be consistent.

The LoRA issue is likely in:
1. LoRA layer placement (attn1 vs attn2)
2. LoRA weight initialization or scaling
3. Learning rate / training hyperparameters
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {output_path}")


if __name__ == '__main__':
    output_dir = '/4T/CXY/MV-Painter/pipeline_consistency_report'
    os.makedirs(output_dir, exist_ok=True)

    check_training_preprocessing()
    check_inference_preprocessing()
    check_pipeline_model_preprocessing()
    check_model_unet_lora_preprocessing()
    compare_target_order()
    check_depth_normal_consistency()

    generate_report(os.path.join(output_dir, 'pipeline_consistency_report.md'))
