"""
Shared pipeline utilities for all eval scripts.
Provides correct pipeline setup with ControlNet + depth grids.
"""
import os
import sys
import random
import numpy as np
import torch
import cv2
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.controlnet import ControlNetModel_Union
from diffusers import EulerAncestralDiscreteScheduler


# Default paths
CHECKPOINT_PATH = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
UNET_CKPT_PATH = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'

# View ordering from infer_multiview.py
VIEW_FILES = ['000.png', '005.png', '001.png', '004.png', '002.png', '003.png']


def seed_everything(seed=42):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_state_dict_safe(model, state_dict, strict=False, label=""):
    """Load state dict with warnings for missing/unexpected keys.

    Unlike torch.load_state_dict(strict=False) which silently ignores mismatches,
    this function prints warnings so issues are visible.
    """
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    if missing:
        print(f'  WARNING [{label}]: {len(missing)} missing keys:')
        for k in missing[:5]:
            print(f'    - {k}')
        if len(missing) > 5:
            print(f'    ... and {len(missing) - 5} more')
    if unexpected:
        print(f'  WARNING [{label}]: {len(unexpected)} unexpected keys:')
        for k in unexpected[:5]:
            print(f'    - {k}')
        if len(unexpected) > 5:
            print(f'    ... and {len(unexpected) - 5} more')
    if not missing and not unexpected:
        print(f'  [{label}] State dict loaded perfectly (no mismatches)')
    return missing, unexpected


def load_pipeline(checkpoint_path=CHECKPOINT_PATH, unet_ckpt_path=UNET_CKPT_PATH, device='cuda'):
    """Load pipeline with ControlNet + RefOnlyNoisedUNet (matching correct inference path).

    This is the ONLY correct way to load the pipeline for eval. The wrapper chain is:
    DepthControlUNet (pipeline.unet)
      -> RefOnlyNoisedUNet (pipeline.unet.unet)
        -> UNet2DConditionModel (pipeline.unet.unet.unet)
    """
    print('Loading pipeline with ControlNet...')
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path, torch_dtype=torch.float16, use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Add ControlNet -- this calls prepare() which wraps UNet in RefOnlyNoisedUNet
    controlnet = ControlNetModel_Union.from_unet(pipeline.unet).to(
        dtype=torch.float16, device=pipeline.device
    )
    pipeline.add_controlnet(controlnet, conditioning_scale=1.0)

    # Load custom UNet checkpoint into bare UNet
    if os.path.exists(unet_ckpt_path) and os.path.getsize(unet_ckpt_path) > 14_000_000_000:
        bare_unet = pipeline.unet.unet.unet
        load_state_dict_safe(bare_unet, load_file(unet_ckpt_path), label="UNet checkpoint")
        print('  Loaded custom UNet checkpoint (v29_25000).')

    pipeline = pipeline.to(device)
    return pipeline


def get_bare_unet(pipeline):
    """Get the bare UNet2DConditionModel from the pipeline wrapper chain."""
    return pipeline.unet.unet.unet


def get_ref_unet(pipeline):
    """Get the RefOnlyNoisedUNet (has ReferenceOnlyAttnProc processors)."""
    return pipeline.unet.unet


def reload_base_weights(pipeline, checkpoint_path=CHECKPOINT_PATH, unet_ckpt_path=UNET_CKPT_PATH):
    """Reload base UNet weights to undo any LoRA merge."""
    bare_unet = get_bare_unet(pipeline)
    base_ckpt = os.path.join(checkpoint_path, 'unet', 'diffusion_pytorch_model.safetensors')
    if os.path.exists(unet_ckpt_path) and os.path.getsize(unet_ckpt_path) > 14_000_000_000:
        base_ckpt = unet_ckpt_path
    load_state_dict_safe(bare_unet, load_file(base_ckpt), label="reload_base")
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

    combined_normal = np.zeros((h * 3, w * 2, c), dtype=np.uint8)
    combined_depth = np.ones((h * 3, w * 2), dtype=np.uint16) * 65535

    for idx, (nv, dv) in enumerate(zip(normal_views, depth_views)):
        x_off = (idx % 2) * w
        y_off = (idx // 2) * h
        combined_normal[y_off:y_off + h, x_off:x_off + w] = nv
        combined_depth[y_off:y_off + h, x_off:x_off + w] = dv

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


def run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42, num_steps=50):
    """Run inference with ControlNet + depth grids (the correct way)."""
    seed_everything(seed)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(
            input_image,
            depth_image=normal_grid,
            depth_image_2=depth_grid,
            num_inference_steps=num_steps,
            output_type='pil',
        )
    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


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


def verify_zero_lora_identity(pipeline, input_image, normal_grid, depth_grid,
                               lora_path, merge_fn, rank, alpha):
    """Verify that merging zero LoRA weights produces identical output to zero-shot.

    Returns True if identity check passes (PSNR > 100 dB).
    """
    from safetensors.torch import save_file as sf_save

    print('  [Zero-LoRA Identity Check]')
    reload_base_weights(pipeline)
    verify_reference_attention(pipeline)

    # Run zero-shot
    img_zeroshot = run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42)

    if not os.path.exists(lora_path):
        print('    Skipping: LoRA checkpoint not found')
        return True

    # Create zero LoRA state
    existing_state = load_file(lora_path)
    zero_state = {k: torch.zeros_like(v) for k, v in existing_state.items()}
    zero_path = '/tmp/zero_lora_identity_check.safetensors'
    sf_save(zero_state, zero_path)

    # Reload base, merge zero LoRA, run again
    reload_base_weights(pipeline)
    bare_unet = get_bare_unet(pipeline)
    merge_fn(bare_unet, zero_path, rank=rank, alpha=alpha)
    verify_reference_attention(pipeline)
    img_zero_lora = run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42)

    p = psnr(img_zeroshot, img_zero_lora)
    if p < 100:
        print(f'    *** FAIL: Zero-LoRA PSNR = {p:.2f} dB (expected inf) ***')
        print(f'    *** This indicates a bug in the merge/load pipeline! ***')
        return False
    else:
        print(f'    PASS: Zero-LoRA PSNR = {p:.2f} dB (identity confirmed)')
        return True


def extract_first_view(six_view_img):
    """Extract the first view (top-left) from a 6-view grid image."""
    arr = np.array(six_view_img)
    h, w = arr.shape[0] // 3, arr.shape[1] // 2
    return Image.fromarray(arr[:h, :w])
