"""
Three-way comparison (Original / Full LoRA / attn2-only LoRA)
Generates paper-quality comparison figures.

FIXED version:
- Uses ControlNet + depth grids (matching correct inference pipeline)
- Consistent scale across all configs
- Zero-LoRA identity verification step
- Both scale=1.0 and scale=0.25 groups
"""
import os
import sys
import json
import torch
import numpy as np
import cv2
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.controlnet import ControlNetModel_Union
from diffusers import EulerAncestralDiscreteScheduler
from diffusers.models.attention_processor import AttnProcessor2_0
import random


# --- Constants ---
CHECKPOINT_PATH = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
UNET_CKPT_PATH = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison_fixed'

BROKEN_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

VIEW_FILES = ['000.png', '005.png', '001.png', '004.png', '002.png', '003.png']

TEST_OBJECTS = [
    'd6a5427888b8413fbfcbcaad14353af8',
    'aa82baf218104070a932dee9a1db61ce',
    'e3f35d4cfbb14410bf96a4ffa28235a1',
    'b23ec9725c48494788d1d88104acbb4a',
    'c630e3959eab49ae87cdad42937e21b2',
    'a2b2645701c94fa49e65661806219c6b',
    'bfdb7491cbe04dfd84a1f60bbac3f77e',
    'c9e54b0c51a8424e8f05b774d42c7f80',
    'f0ef4adc17ee4929b40e894c608061ea',
    'f63daf968be34047bc513feb756b5828',
]


def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_pipeline():
    """Load pipeline with ControlNet + RefOnlyNoisedUNet (matching correct inference path)."""
    print('Loading pipeline with ControlNet...')
    pipeline = MVPainter_Pipeline.from_pretrained(
        CHECKPOINT_PATH, torch_dtype=torch.float16, use_safetensors=True,
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
    if os.path.exists(UNET_CKPT_PATH) and os.path.getsize(UNET_CKPT_PATH) > 14_000_000_000:
        bare_unet = pipeline.unet.unet.unet  # DepthControlUNet -> RefOnlyNoisedUNet -> UNet2DConditionModel
        bare_unet.load_state_dict(load_file(UNET_CKPT_PATH), strict=False)
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
    base_ckpt = os.path.join(CHECKPOINT_PATH, 'unet', 'diffusion_pytorch_model.safetensors')
    if os.path.exists(UNET_CKPT_PATH) and os.path.getsize(UNET_CKPT_PATH) > 14_000_000_000:
        base_ckpt = UNET_CKPT_PATH
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
    """Run inference with ControlNet + depth grids."""
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


def verify_zero_lora_identity(pipeline, input_image, normal_grid, depth_grid):
    """Verify that merging zero LoRA weights produces identical output to zero-shot.

    This catches eval toolchain bugs: if PSNR != inf after merging zero weights,
    the merge/load pipeline has a bug.
    """
    print('  [Zero-LoRA Identity Check]')
    reload_base_weights(pipeline)
    verify_reference_attention(pipeline)

    # Run zero-shot
    img_zeroshot = run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42)

    # Create zero LoRA state from existing checkpoint
    if os.path.exists(ATTN2_LORA_PATH):
        existing_state = load_file(ATTN2_LORA_PATH)
        zero_state = {k: torch.zeros_like(v) for k, v in existing_state.items()}
        zero_path = '/tmp/zero_lora_identity_check.safetensors'
        from safetensors.torch import save_file
        save_file(zero_state, zero_path)

        # Reload base, merge zero LoRA, run again
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet_attn2_only(bare_unet, zero_path, rank=4, alpha=4)
        verify_reference_attention(pipeline)
        img_zero_lora = run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42)

        psnr_val = psnr(img_zeroshot, img_zero_lora)
        if psnr_val < 100:  # Should be inf (or very high due to float precision)
            print(f'  *** FAIL: Zero-LoRA PSNR = {psnr_val:.2f} dB (expected inf) ***')
            print(f'  *** This indicates a bug in the merge/load pipeline! ***')
            return False
        else:
            print(f'  PASS: Zero-LoRA PSNR = {psnr_val:.2f} dB (identity confirmed)')
            return True

    # Also test full LoRA zero merge
    if os.path.exists(BROKEN_LORA_PATH):
        existing_state = load_file(BROKEN_LORA_PATH)
        zero_state = {k: torch.zeros_like(v) for k, v in existing_state.items()}
        zero_path = '/tmp/zero_lora_full_identity_check.safetensors'
        from safetensors.torch import save_file
        save_file(zero_state, zero_path)

        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet(bare_unet, zero_path, rank=4, alpha=4)
        verify_reference_attention(pipeline)
        img_zero_full = run_inference(pipeline, input_image, normal_grid, depth_grid, seed=42)

        psnr_val = psnr(img_zeroshot, img_zero_full)
        if psnr_val < 100:
            print(f'  *** FAIL: Zero-FullLoRA PSNR = {psnr_val:.2f} dB (expected inf) ***')
            return False
        else:
            print(f'  PASS: Zero-FullLoRA PSNR = {psnr_val:.2f} dB (identity confirmed)')

    return True


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


def create_comparison_figure(cond_img, img_a, img_b, img_c, obj_id, save_path, scale_label):
    """Create a 1-row, 4-column comparison figure."""
    from PIL import ImageDraw, ImageFont

    target_size = (512, 512)
    cond_resized = cond_img.resize(target_size)
    img_a_resized = img_a.resize(target_size) if img_a else Image.new('RGB', target_size, (128, 128, 128))
    img_b_resized = img_b.resize(target_size) if img_b else Image.new('RGB', target_size, (128, 128, 128))
    img_c_resized = img_c.resize(target_size) if img_c else Image.new('RGB', target_size, (128, 128, 128))

    fig_width = target_size[0] * 4
    fig_height = target_size[1] + 40
    fig = Image.new('RGB', (fig_width, fig_height), (255, 255, 255))

    fig.paste(cond_resized, (0, 40))
    fig.paste(img_a_resized, (target_size[0], 40))
    fig.paste(img_b_resized, (target_size[0] * 2, 40))
    fig.paste(img_c_resized, (target_size[0] * 3, 40))

    draw = ImageDraw.Draw(fig)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    labels = [
        "Condition",
        "A: Original",
        f"B: Full LoRA ({scale_label})",
        f"C: attn2-only ({scale_label})",
    ]
    for i, label in enumerate(labels):
        x = target_size[0] * i + 10
        draw.text((x, 10), label, fill=(0, 0, 0), font=font)

    draw.text((10, fig_height - 25), f"Object: {obj_id}", fill=(100, 100, 100), font=font)
    fig.save(save_path)
    return fig


def run_three_way_for_scale(pipeline, scale, scale_label, test_objects, output_dir):
    """Run three-way comparison for a given scale value.

    Args:
        pipeline: Loaded pipeline with ControlNet
        scale: LoRA scale (alpha/rank)
        scale_label: Label for output files (e.g., "s1.0" or "s0.25")
        test_objects: List of object IDs
        output_dir: Base output directory
    """
    scale_dir = os.path.join(output_dir, f'scale_{scale_label}')
    os.makedirs(scale_dir, exist_ok=True)

    results = []

    for obj_id in test_objects:
        print(f'\n  [{scale_label}] Processing: {obj_id}')
        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_path = os.path.join(obj_path, 'image', '000.png')

        if not os.path.exists(cond_path):
            print(f'    Skipping: condition image not found')
            continue

        cond_img = Image.open(cond_path).convert('RGBA')
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f'    Skipping: missing normal/depth views')
            continue

        # --- Config A: Original (no LoRA) ---
        print('    Config A (Original)...')
        reload_base_weights(pipeline)
        verify_reference_attention(pipeline)
        img_a = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)

        # --- Config B: Full LoRA (attn1+attn2) ---
        print('    Config B (Full LoRA)...')
        if os.path.exists(BROKEN_LORA_PATH):
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            rank_b = 4
            alpha_b = int(rank_b * scale)  # alpha = rank * scale
            merge_lora_into_unet(bare_unet, BROKEN_LORA_PATH, rank=rank_b, alpha=alpha_b)
            verify_reference_attention(pipeline)
            img_b = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        else:
            print(f'    Full LoRA checkpoint not found: {BROKEN_LORA_PATH}')
            img_b = None

        # --- Config C: attn2-only LoRA ---
        print('    Config C (attn2-only LoRA)...')
        if os.path.exists(ATTN2_LORA_PATH):
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            rank_c = 4
            alpha_c = int(rank_c * scale)  # alpha = rank * scale
            merge_lora_into_unet_attn2_only(bare_unet, ATTN2_LORA_PATH, rank=rank_c, alpha=alpha_c)
            verify_reference_attention(pipeline)
            img_c = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        else:
            print(f'    attn2-only checkpoint not found: {ATTN2_LORA_PATH}')
            img_c = None

        # Save individual images
        if img_a:
            img_a.save(os.path.join(scale_dir, f'{obj_id}_original.png'))
        if img_b:
            img_b.save(os.path.join(scale_dir, f'{obj_id}_full_lora.png'))
        if img_c:
            img_c.save(os.path.join(scale_dir, f'{obj_id}_attn2only.png'))

        # Compute PSNR
        psnr_ab = psnr(img_a, img_b) if img_a and img_b else None
        psnr_ac = psnr(img_a, img_c) if img_a and img_c else None

        psnr_ab_str = f'{psnr_ab:.2f} dB' if psnr_ab is not None else 'N/A'
        psnr_ac_str = f'{psnr_ac:.2f} dB' if psnr_ac is not None else 'N/A'
        print(f'    PSNR(A vs B) = {psnr_ab_str}, PSNR(A vs C) = {psnr_ac_str}')

        # Create comparison figure
        fig_path = os.path.join(scale_dir, f'{obj_id}_comparison.png')
        create_comparison_figure(cond_img, img_a, img_b, img_c, obj_id, fig_path, scale_label)

        results.append({
            'obj_id': obj_id,
            'psnr_ab': psnr_ab,
            'psnr_ac': psnr_ac,
        })

    # Print summary
    print(f'\n  [{"=" * 40}]')
    print(f'  SUMMARY (scale={scale})')
    print(f'  [{"=" * 40}]')
    for r in results:
        ab = f'{r["psnr_ab"]:.2f}' if r['psnr_ab'] is not None else 'N/A'
        ac = f'{r["psnr_ac"]:.2f}' if r['psnr_ac'] is not None else 'N/A'
        print(f'  {r["obj_id"][:20]:20s}  PSNR(A vs B)={ab:>8}  PSNR(A vs C)={ac:>8}')

    # Compute averages
    valid_ab = [r['psnr_ab'] for r in results if r['psnr_ab'] is not None]
    valid_ac = [r['psnr_ac'] for r in results if r['psnr_ac'] is not None]
    if valid_ab:
        print(f'  Avg PSNR(A vs B) = {np.mean(valid_ab):.2f} dB')
    if valid_ac:
        print(f'  Avg PSNR(A vs C) = {np.mean(valid_ac):.2f} dB')

    # Save results JSON
    results_path = os.path.join(scale_dir, 'results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'scale': scale,
            'scale_label': scale_label,
            'results': results,
            'avg_psnr_ab': float(np.mean(valid_ab)) if valid_ab else None,
            'avg_psnr_ac': float(np.mean(valid_ac)) if valid_ac else None,
        }, f, indent=2)
    print(f'\n  Results saved to {results_path}')

    return results


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print('=' * 60)
    print('Three-Way Comparison (Fixed: ControlNet + Consistent Scale)')
    print('=' * 60)

    # Load pipeline once
    pipeline = load_pipeline()

    # --- Step 1: Zero-LoRA Identity Verification ---
    print('\n' + '=' * 60)
    print('STEP 1: Zero-LoRA Identity Verification')
    print('=' * 60)

    first_obj = TEST_OBJECTS[0]
    first_obj_path = os.path.join(TRAIN_DATA, first_obj)
    first_cond = Image.open(os.path.join(first_obj_path, 'image', '000.png')).convert('RGBA')
    first_normal, first_depth = create_combined_grids(first_obj_path)

    if first_normal is not None:
        identity_ok = verify_zero_lora_identity(pipeline, first_cond, first_normal, first_depth)
        if not identity_ok:
            print('\n*** ABORTING: Zero-LoRA identity check failed! ***')
            print('*** Fix the merge/load pipeline before running comparisons. ***')
            return
    else:
        print('  WARNING: Could not run identity check (missing depth/normal files)')

    # --- Step 2: Run comparisons at both scales ---
    SCALES = [
        (1.0, '1.0'),
        (0.25, '0.25'),
    ]

    all_summaries = {}
    for scale, scale_label in SCALES:
        print(f'\n{"=" * 60}')
        print(f'STEP 2: Three-Way Comparison (scale={scale})')
        print(f'{"=" * 60}')

        results = run_three_way_for_scale(
            pipeline, scale, scale_label, TEST_OBJECTS, OUTPUT_DIR
        )
        all_summaries[scale_label] = results

    # --- Step 3: Cross-scale summary ---
    print(f'\n{"=" * 60}')
    print('CROSS-SCALE SUMMARY')
    print(f'{"=" * 60}')
    print(f'{"Object":<25} {"s=1.0 (B)":>12} {"s=1.0 (C)":>12} {"s=0.25 (B)":>12} {"s=0.25 (C)":>12}')
    print('-' * 75)

    for i, obj_id in enumerate(TEST_OBJECTS):
        row = f'{obj_id[:24]:<25}'
        for sl in ['1.0', '0.25']:
            r_list = all_summaries.get(sl, [])
            r = next((x for x in r_list if x['obj_id'] == obj_id), None)
            ab = f'{r["psnr_ab"]:.1f}' if r and r['psnr_ab'] is not None else 'N/A'
            ac = f'{r["psnr_ac"]:.1f}' if r and r['psnr_ac'] is not None else 'N/A'
            row += f' {ab:>12} {ac:>12}'
        print(row)

    print(f'\nOutput saved to {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
