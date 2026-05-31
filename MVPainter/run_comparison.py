"""Run inference comparison: zero-shot vs LoRA on test samples."""
import os
import sys
import torch
import numpy as np
from PIL import Image
from torchvision.transforms import v2

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler

def run_inference(pipeline, input_image_path, depth_image_path, output_path, num_steps=50):
    """Run multi-view generation on a single input image."""
    from pytorch_lightning import seed_everything
    seed_everything(42)

    input_image = Image.open(input_image_path).convert('RGBA')
    depth_image = Image.open(depth_image_path)

    output = pipeline(
        input_image,
        depth_image=depth_image,
        num_inference_steps=num_steps,
    )

    # Save the 6-view output
    output[0].save(os.path.join(output_path, 'result_6view.png'))
    output[1].save(os.path.join(output_path, 'result_cond.png'))
    print(f'  Saved to {output_path}')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipeline_path', default='../checkpoints/hf_repo')
    parser.add_argument('--lora_r8', default='logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors')
    parser.add_argument('--lora_r4', default='logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors')
    parser.add_argument('--output_dir', default='comparison_results')
    parser.add_argument('--num_samples', type=int, default=4)
    parser.add_argument('--num_steps', type=int, default=50)
    args = parser.parse_args()

    # Get test samples
    with open('/4T/CXY/MV-Painter/data/train_data/rendered_full/clean_objects.txt') as f:
        all_objects = [l.strip() for l in f.readlines() if l.strip()]
    test_objects = all_objects[-args.num_samples:]
    print(f'Test samples: {len(test_objects)}')

    os.makedirs(args.output_dir, exist_ok=True)

    # Load pipeline once
    print('Loading pipeline...')
    pipeline = MVPainter_Pipeline.from_pretrained(
        args.pipeline_path, torch_dtype=torch.float16,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    pipeline = pipeline.to('cuda')

    for obj in test_objects:
        obj_path = os.path.join('/4T/CXY/MV-Painter/data/train_data/rendered_full', obj)
        img_path = os.path.join(obj_path, 'image', '000.png')
        depth_path = os.path.join(obj_path, 'depth_png', '000.png')

        if not os.path.exists(img_path) or not os.path.exists(depth_path):
            print(f'Skipping {obj}: missing files')
            continue

        print(f'\n=== {obj} ===')

        def load_base_unet():
            """Reload the base UNet weights (unwrapped)."""
            from safetensors.torch import load_file
            base_ckpt = os.path.join(args.pipeline_path, 'unet', 'diffusion_pytorch_model.safetensors')
            if os.path.exists(base_ckpt):
                # Access inner UNet (unwrap RefOnlyNoisedUNet)
                inner_unet = pipeline.unet.unet if hasattr(pipeline.unet, 'unet') else pipeline.unet
                inner_unet.load_state_dict(load_file(base_ckpt), strict=False)

        # 1. Zero-shot
        out_dir = os.path.join(args.output_dir, f'{obj}_zeroshot')
        os.makedirs(out_dir, exist_ok=True)
        if not os.path.exists(os.path.join(out_dir, 'result_6view.png')):
            load_base_unet()
            print('  Running zero-shot...')
            run_inference(pipeline, img_path, depth_path, out_dir, args.num_steps)

        # 2. LoRA rank=8
        if os.path.exists(args.lora_r8):
            out_dir = os.path.join(args.output_dir, f'{obj}_lora_r8')
            os.makedirs(out_dir, exist_ok=True)
            if not os.path.exists(os.path.join(out_dir, 'result_6view.png')):
                load_base_unet()
                inner_unet = pipeline.unet.unet if hasattr(pipeline.unet, 'unet') else pipeline.unet
                print('  Merging LoRA rank=8...')
                merge_lora_into_unet(inner_unet, args.lora_r8, rank=8, alpha=8)
                print('  Running LoRA-r8 inference...')
                run_inference(pipeline, img_path, depth_path, out_dir, args.num_steps)

        # 3. LoRA rank=4
        if os.path.exists(args.lora_r4):
            out_dir = os.path.join(args.output_dir, f'{obj}_lora_r4')
            os.makedirs(out_dir, exist_ok=True)
            if not os.path.exists(os.path.join(out_dir, 'result_6view.png')):
                load_base_unet()
                inner_unet = pipeline.unet.unet if hasattr(pipeline.unet, 'unet') else pipeline.unet
                print('  Merging LoRA rank=4...')
                merge_lora_into_unet(inner_unet, args.lora_r4, rank=4, alpha=4)
                print('  Running LoRA-r4 inference...')
                run_inference(pipeline, img_path, depth_path, out_dir, args.num_steps)

    print(f'\nDone! Results in {args.output_dir}/')


if __name__ == '__main__':
    main()
