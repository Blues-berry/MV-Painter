"""
Style Transfer Experiment: Prove attn2-only LoRA can learn new styles while preserving reference attention.

Experiment Design:
1. Create "style" by applying color transformation to training data
2. Train Full LoRA and attn2-only LoRA on styled data
3. Evaluate:
   - Style learning: Does output match the target style?
   - Reference preservation: Does output still follow the condition image?
   - Multi-view consistency: Are generated views consistent?

This addresses the core criticism: "The method doesn't learn anything"
"""
import os
import sys
import torch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))


def apply_warm_style(img):
    """Apply warm color style (simulate sunset/golden hour effect)."""
    arr = np.array(img).astype(float)

    # Increase red channel, decrease blue channel
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.3, 0, 255)  # Red +30%
    arr[:, :, 2] = arr[:, :, 2] * 0.7  # Blue -30%

    # Add warm tint
    arr[:, :, 0] = np.clip(arr[:, :, 0] + 20, 0, 255)  # Add red tint
    arr[:, :, 1] = np.clip(arr[:, :, 1] + 10, 0, 255)  # Slight green

    return Image.fromarray(arr.astype(np.uint8))


def apply_cool_style(img):
    """Apply cool color style (simulate blue hour/futuristic effect)."""
    arr = np.array(img).astype(float)

    # Decrease red, increase blue
    arr[:, :, 0] = arr[:, :, 0] * 0.7  # Red -30%
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.3, 0, 255)  # Blue +30%

    # Add cool tint
    arr[:, :, 2] = np.clip(arr[:, :, 2] + 20, 0, 255)  # Add blue tint

    return Image.fromarray(arr.astype(np.uint8))


def apply_high_contrast_style(img):
    """Apply high contrast style (dramatic/cinematic look)."""
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)

    return img


def prepare_style_dataset(source_dir, output_dir, style_func, num_objects=20):
    """Prepare styled dataset for training."""
    os.makedirs(output_dir, exist_ok=True)

    # Get list of objects
    objects = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    objects = objects[:num_objects]

    print(f"Preparing styled dataset for {len(objects)} objects...")

    for obj_id in objects:
        src_obj_dir = os.path.join(source_dir, obj_id)
        dst_obj_dir = os.path.join(output_dir, obj_id)

        # Copy structure
        os.makedirs(os.path.join(dst_obj_dir, 'image'), exist_ok=True)
        os.makedirs(os.path.join(dst_obj_dir, 'camera'), exist_ok=True)

        # Copy and style images
        image_dir = os.path.join(src_obj_dir, 'image')
        if os.path.exists(image_dir):
            for img_file in os.listdir(image_dir):
                if img_file.endswith('.png'):
                    src_path = os.path.join(image_dir, img_file)
                    dst_path = os.path.join(dst_obj_dir, 'image', img_file)

                    # Apply style
                    img = Image.open(src_path).convert('RGBA')
                    rgb = img.convert('RGB')
                    styled_rgb = style_func(rgb)

                    # Convert back to RGBA
                    styled_rgba = styled_rgb.convert('RGBA')
                    if img.mode == 'RGBA':
                        styled_rgba.putalpha(img.split()[3])

                    styled_rgba.save(dst_path)

        # Copy camera files
        camera_dir = os.path.join(src_obj_dir, 'camera')
        if os.path.exists(camera_dir):
            for cam_file in os.listdir(camera_dir):
                src_path = os.path.join(camera_dir, cam_file)
                dst_path = os.path.join(dst_obj_dir, 'camera', cam_file)
                import shutil
                shutil.copy2(src_path, dst_path)

    print(f"Styled dataset saved to {output_dir}")


def create_training_config(style_name, styled_data_dir, lora_type, rank=4, steps=250):
    """Create training configuration for style transfer."""
    config = {
        'model': {
            'base_learning_rate': 1e-5,
            'target': 'mvpainter.model_unet_lora_attn2.MVDiffusionLoRAAttn2' if lora_type == 'attn2' else 'mvpainter.model_unet_lora.MVDiffusionLoRA',
            'params': {
                'drop_cond_prob': 0.1,
                'stable_diffusion_config': {
                    'pretrained_model_name_or_path': '../checkpoints/hf_repo'
                },
                'lora_rank': rank,
                'lora_alpha': rank,
            }
        },
        'data': {
            'target': 'src.data.mvpainter_dataset.DataModuleFromConfig',
            'params': {
                'batch_size': 1,
                'num_workers': 0,
                'train': {
                    'target': 'src.data.mvpainter_dataset.MVPainterData',
                    'params': {
                        'root_dir_list': [styled_data_dir],
                        'meta_fname': 'train_meta.json',
                        'clean_list': 'clean_objects.txt'
                    }
                }
            }
        },
        'lightning': {
            'trainer': {
                'max_epochs': -1,
                'max_steps': steps,
                'gradient_clip_val': 1.0,
            }
        }
    }

    return config


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Style Transfer Experiment')
    parser.add_argument('--source_dir', type=str,
                        default='/4T/CXY/MV-Painter/data/train_data/rendered_full',
                        help='Source data directory')
    parser.add_argument('--output_dir', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/style_transfer',
                        help='Output directory')
    parser.add_argument('--num_objects', type=int, default=20,
                        help='Number of objects for training')
    parser.add_argument('--style', type=str, default='warm',
                        choices=['warm', 'cool', 'contrast'],
                        help='Style to apply')

    args = parser.parse_args()

    # Select style function
    style_funcs = {
        'warm': apply_warm_style,
        'cool': apply_cool_style,
        'contrast': apply_high_contrast_style,
    }
    style_func = style_funcs[args.style]

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Prepare styled dataset
    styled_data_dir = os.path.join(args.output_dir, f'styled_{args.style}')
    prepare_style_dataset(args.source_dir, styled_data_dir, style_func, args.num_objects)

    # Generate training configs
    configs_dir = os.path.join(args.output_dir, 'configs')
    os.makedirs(configs_dir, exist_ok=True)

    # Full LoRA config
    full_config = create_training_config(args.style, styled_data_dir, 'full', rank=4, steps=250)
    full_config_path = os.path.join(configs_dir, f'style_{args.style}_full_lora.yaml')
    with open(full_config_path, 'w') as f:
        import yaml
        yaml.dump(full_config, f, default_flow_style=False)

    # attn2-only LoRA config
    attn2_config = create_training_config(args.style, styled_data_dir, 'attn2', rank=4, steps=250)
    attn2_config_path = os.path.join(configs_dir, f'style_{args.style}_attn2_lora.yaml')
    with open(attn2_config_path, 'w') as f:
        import yaml
        yaml.dump(attn2_config, f, default_flow_style=False)

    # Generate training script
    train_script = f"""#!/bin/bash
# Style Transfer Training Script
# Style: {args.style}

echo "=== Style Transfer Experiment ==="
echo "Style: {args.style}"
echo "Data: {styled_data_dir}"
echo ""

# Train Full LoRA
echo "Training Full LoRA..."
cd /4T/CXY/MV-Painter/MVPainter
python train.py --base {full_config_path} -t --gpus 0,

# Train attn2-only LoRA
echo "Training attn2-only LoRA..."
python train.py --base {attn2_config_path} -t --gpus 0,

echo "Training complete!"
"""

    train_script_path = os.path.join(args.output_dir, f'train_{args.style}.sh')
    with open(train_script_path, 'w') as f:
        f.write(train_script)
    os.chmod(train_script_path, 0o755)

    # Generate evaluation script
    eval_script = f"""#!/bin/bash
# Style Transfer Evaluation Script

echo "=== Evaluating Style Transfer ==="

python mvp-lora-script/eval_style_transfer.py \\
    --style {args.style} \\
    --styled_data {styled_data_dir} \\
    --output_dir {args.output_dir}/eval_{args.style}
"""

    eval_script_path = os.path.join(args.output_dir, f'eval_{args.style}.sh')
    with open(eval_script_path, 'w') as f:
        f.write(eval_script)
    os.chmod(eval_script_path, 0o755)

    # Print summary
    print(f"\\n{'='*60}")
    print("STYLE TRANSFER EXPERIMENT SETUP")
    print(f"{'='*60}")
    print(f"Style: {args.style}")
    print(f"Training objects: {args.num_objects}")
    print(f"Styled data: {styled_data_dir}")
    print(f"\\nConfigs generated:")
    print(f"  Full LoRA: {full_config_path}")
    print(f"  attn2-only: {attn2_config_path}")
    print(f"\\nScripts generated:")
    print(f"  Training: {train_script_path}")
    print(f"  Evaluation: {eval_script_path}")
    print(f"\\nNext steps:")
    print(f"  1. Run training: bash {train_script_path}")
    print(f"  2. Run evaluation: bash {eval_script_path}")
    print(f"  3. Compare results")


if __name__ == '__main__':
    main()
