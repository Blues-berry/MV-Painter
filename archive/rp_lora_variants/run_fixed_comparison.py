"""
Run zero-shot vs LoRA comparison with the FIXED merge function.
Properly sets up pipeline with ControlNet + ReferenceOnlyAttnProc.
Creates 3x2 grids like the original infer_multiview.py.

Usage:
    CUDA_VISIBLE_DEVICES=1 python run_fixed_comparison.py
"""
import os
import sys
import json
import torch
import numpy as np
import cv2
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler
import random

def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


PIPELINE_PATH = '../checkpoints/hf_repo'
LORA_R4 = 'logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors'
LORA_R8 = 'logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
OUTPUT_DIR = 'fixed_comparison_results'

# View ordering from infer_multiview.py
VIEW_FILES = ['000.png', '005.png', '001.png', '004.png', '002.png', '003.png']


def load_pipeline():
    """Load pipeline with ControlNet (triggers RefOnlyNoisedUNet wrapping)."""
    print('Loading pipeline...')
    pipeline = MVPainter_Pipeline.from_pretrained(PIPELINE_PATH, torch_dtype=torch.float16)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Add ControlNet -- this calls prepare() which wraps UNet in RefOnlyNoisedUNet
    from mvpainter.controlnet import ControlNetModel_Union
    controlnet = ControlNetModel_Union.from_unet(pipeline.unet).to(dtype=torch.float16, device=pipeline.device)
    pipeline.add_controlnet(controlnet, conditioning_scale=1.0)

    # Load custom UNet checkpoint
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(unet_ckpt_path) and os.path.getsize(unet_ckpt_path) > 14_000_000_000:
        bare_unet = pipeline.unet.unet.unet  # DepthControlUNet -> RefOnlyNoisedUNet -> UNet2DConditionModel
        bare_unet.load_state_dict(load_file(unet_ckpt_path), strict=False)
        print('  Loaded custom UNet checkpoint (v29_25000).')

    pipeline = pipeline.to('cuda')
    return pipeline


def get_bare_unet(pipeline):
    """Get the bare UNet2DConditionModel from the pipeline wrapper chain."""
    return pipeline.unet.unet.unet


def get_ref_unet(pipeline):
    """Get the RefOnlyNoisedUNet (has ReferenceOnlyAttnProc processors)."""
    return pipeline.unet.unet


def reload_base_weights(pipeline):
    """Reload base UNet weights to undo any LoRA merge."""
    bare_unet = get_bare_unet(pipeline)
    base_ckpt = os.path.join(PIPELINE_PATH, 'unet', 'diffusion_pytorch_model.safetensors')
    alt_ckpt = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(alt_ckpt) and os.path.getsize(alt_ckpt) > 14_000_000_000:
        base_ckpt = alt_ckpt
    bare_unet.load_state_dict(load_file(base_ckpt), strict=False)
    print('  Reloaded base UNet weights.')


def verify_reference_attention(pipeline):
    """Sanity check: verify ReferenceOnlyAttnProc is intact."""
    ref_unet = get_ref_unet(pipeline)
    ref_count = sum(1 for p in ref_unet.attn_processors.values()
                    if isinstance(p, ReferenceOnlyAttnProc))
    total_count = len(ref_unet.attn_processors)
    print(f'  ReferenceOnlyAttnProc: {ref_count}/{total_count} processors')
    if ref_count == 0:
        print('  *** WARNING: No ReferenceOnlyAttnProc! Reference attention is BROKEN! ***')
        return False
    print('  Reference attention: OK')
    return True


def create_combined_grids(obj_path):
    """Create 3x2 combined grids for normal and depth, matching infer_multiview.py."""
    normal_dir = os.path.join(obj_path, 'normal')
    depth_dir = os.path.join(obj_path, 'depth_png')

    # Load and resize 6 views
    normal_views = []
    depth_views = []
    for fname in VIEW_FILES:
        n_path = os.path.join(normal_dir, fname)
        d_path = os.path.join(depth_dir, fname)
        if not os.path.exists(n_path) or not os.path.exists(d_path):
            return None, None

        n_img = cv2.resize(cv2.imread(n_path), (512, 512))
        d_img = cv2.resize(cv2.imread(d_path, cv2.IMREAD_UNCHANGED), (512, 512))
        normal_views.append(n_img)
        depth_views.append(d_img)

    h, w, c = normal_views[0].shape

    # Create combined normal grid (3x2)
    combined_normal = np.zeros((h * 3, w * 2, c), dtype=np.uint8)
    combined_depth = np.ones((h * 3, w * 2), dtype=np.uint16) * 65535

    for idx, (nv, dv) in enumerate(zip(normal_views, depth_views)):
        x_off = (idx % 2) * w
        y_off = (idx // 2) * h
        combined_normal[y_off:y_off+h, x_off:x_off+w] = nv
        combined_depth[y_off:y_off+h, x_off:x_off+w] = dv

    # Normalize depth (same as infer_multiview.py)
    valid_mask = combined_depth < 65535
    depth_f = combined_depth.astype(np.float32) / 65535.0
    depth_f[valid_mask] = 1.0 / depth_f[valid_mask]
    if valid_mask.any():
        min_d = np.min(depth_f[valid_mask])
        max_d = np.max(depth_f[valid_mask])
        depth_f[valid_mask] = (depth_f[valid_mask] - min_d) / (max_d - min_d + 1e-8)
    combined_depth_rgb = np.repeat(depth_f[:, :, np.newaxis], 3, axis=2)

    normal_pil = Image.fromarray(combined_normal[:, :, ::-1])  # BGR -> RGB
    depth_pil = Image.fromarray((combined_depth_rgb * 255).astype(np.uint8))

    return normal_pil, depth_pil


def run_inference(pipeline, obj_path, output_dir, seed=42):
    """Run inference with proper 3x2 grid inputs."""
    seed_everything(seed)
    os.makedirs(output_dir, exist_ok=True)

    # Get input image (first view)
    img_path = os.path.join(obj_path, 'image', VIEW_FILES[0])
    input_image = Image.open(img_path).convert('RGBA')

    # Create 3x2 grids
    normal_grid, depth_grid = create_combined_grids(obj_path)
    if normal_grid is None:
        print('  SKIP: missing view files')
        return None

    output = pipeline(input_image, depth_image=normal_grid, depth_image_2=depth_grid,
                      num_inference_steps=50)
    result_path = os.path.join(output_dir, 'result_6view.png')
    output[0].save(result_path)
    return result_path


def manual_merge_with_scale(pipeline, lora_path, rank, alpha, override_scale=None):
    """Merge LoRA with optional scale override. Preserves ReferenceOnlyAttnProc."""
    bare_unet = get_bare_unet(pipeline)
    lora_state = load_file(lora_path)
    scale = (alpha / rank) if override_scale is None else override_scale

    for proc_name, _ in bare_unet.attn_processors.items():
        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(bare_unet.named_modules())[attn_module_name]

        for proj_name in ['to_q', 'to_k', 'to_v']:
            down_key = f'{prefix}_{proj_name}_lora_down'
            up_key = f'{prefix}_{proj_name}_lora_up'
            if down_key in lora_state and up_key in lora_state:
                proj_layer = getattr(attn_module, proj_name)
                delta = (lora_state[up_key] @ lora_state[down_key]) * scale
                proj_layer.weight.data += delta.to(device=proj_layer.weight.device, dtype=proj_layer.weight.dtype)

        down_key = f'{prefix}_to_out_lora_down'
        up_key = f'{prefix}_to_out_lora_up'
        if down_key in lora_state and up_key in lora_state:
            delta = (lora_state[up_key] @ lora_state[down_key]) * scale
            attn_module.to_out[0].weight.data += delta.to(
                device=attn_module.to_out[0].weight.device,
                dtype=attn_module.to_out[0].weight.dtype,
            )

    # Preserve ReferenceOnlyAttnProc wrappers on the RefOnlyNoisedUNet
    ref_unet = get_ref_unet(pipeline)
    from diffusers.models.attention_processor import AttnProcessor2_0
    new_procs = {}
    for proc_name, proc in ref_unet.attn_processors.items():
        if isinstance(proc, ReferenceOnlyAttnProc):
            proc.chained_proc = AttnProcessor2_0()
            new_procs[proc_name] = proc
        else:
            new_procs[proc_name] = AttnProcessor2_0()
    ref_unet.set_attn_processor(new_procs)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get test samples
    with open(os.path.join(TRAIN_DATA, 'clean_objects.txt')) as f:
        all_objects = [l.strip() for l in f.readlines() if l.strip()]
    test_objects = all_objects[-4:]  # Last 4
    print(f'Test samples: {test_objects}')

    pipeline = load_pipeline()
    bare_unet = get_bare_unet(pipeline)

    for obj in test_objects:
        obj_path = os.path.join(TRAIN_DATA, obj)
        img_path = os.path.join(obj_path, 'image', VIEW_FILES[0])
        if not os.path.exists(img_path):
            print(f'Skipping {obj}: missing files')
            continue

        print(f'\n{"="*60}')
        print(f'Sample: {obj}')
        print(f'{"="*60}')

        # 1. Zero-shot
        print('\n--- Zero-shot ---')
        reload_base_weights(pipeline)
        verify_reference_attention(pipeline)
        out_dir = os.path.join(OUTPUT_DIR, f'{obj}_zeroshot')
        run_inference(pipeline, obj_path, out_dir)
        print(f'  Saved to {out_dir}')

        # 2. LoRA-r4 (fixed merge, scale=1.0)
        if os.path.exists(LORA_R4):
            print('\n--- LoRA-r4 (scale=1.0, fixed merge) ---')
            reload_base_weights(pipeline)
            merge_lora_into_unet(bare_unet, LORA_R4, rank=4, alpha=4)
            verify_reference_attention(pipeline)
            out_dir = os.path.join(OUTPUT_DIR, f'{obj}_lora_r4')
            run_inference(pipeline, obj_path, out_dir)
            print(f'  Saved to {out_dir}')

        # 3. LoRA-r8 (fixed merge, scale=1.0)
        if os.path.exists(LORA_R8):
            print('\n--- LoRA-r8 (scale=1.0, fixed merge) ---')
            reload_base_weights(pipeline)
            merge_lora_into_unet(bare_unet, LORA_R8, rank=8, alpha=8)
            verify_reference_attention(pipeline)
            out_dir = os.path.join(OUTPUT_DIR, f'{obj}_lora_r8')
            run_inference(pipeline, obj_path, out_dir)
            print(f'  Saved to {out_dir}')

    # Scale sweep on first sample
    print(f'\n{"="*60}')
    print('SCALE SWEEP on first test sample')
    print(f'{"="*60}')
    obj = test_objects[0]
    obj_path = os.path.join(TRAIN_DATA, obj)

    for label, lora_path in [('r4', LORA_R4), ('r8', LORA_R8)]:
        if not os.path.exists(lora_path):
            continue
        config_path = lora_path.replace('.safetensors', '_config.json')
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg['rank']
        alpha = cfg['alpha']

        for scale in [0.0, 0.1, 0.25, 0.5, 1.0]:
            print(f'\n--- {label} scale={scale} ---')
            reload_base_weights(pipeline)
            if scale > 0:
                manual_merge_with_scale(pipeline, lora_path, rank, alpha, override_scale=scale)
            verify_reference_attention(pipeline)
            out_dir = os.path.join(OUTPUT_DIR, f'sweep_{obj}_{label}_s{scale}')
            run_inference(pipeline, obj_path, out_dir)
            print(f'  Saved to {out_dir}')

    print(f'\n{"="*60}')
    print(f'DONE! Results in {OUTPUT_DIR}/')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
