"""
Verify PSNR vs Original for all LoRA checkpoints using the CORRECT pipeline
(ControlNet + depth/normal grids).
"""
import os
import sys
import numpy as np
import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, extract_first_view, verify_zero_lora_identity,
    seed_everything, CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet


def compute_psnr(img1, img2):
    """Compute PSNR between two PIL images."""
    arr1 = np.array(img1).astype(np.float64)
    arr2 = np.array(img2).astype(np.float64)
    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/verification'
    os.makedirs(output_dir, exist_ok=True)

    # Checkpoint paths
    checkpoints = {
        'broken_r4': {
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors',
            'rank': 4, 'alpha': 4, 'type': 'full', 'label': 'Full LoRA r4/lr1e-4/100'
        },
        'crash_r8': {
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors',
            'rank': 8, 'alpha': 8, 'type': 'full', 'label': 'Full LoRA r8/lr5e-4/500'
        },
        'attn2_r4': {
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors',
            'rank': 4, 'alpha': 4, 'type': 'attn2', 'label': 'attn2-only r4/lr1e-5/250'
        },
    }

    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    print("Loading pipeline with ControlNet + depth/normal grids...")
    pipeline = load_pipeline(device='cuda')
    seed_everything(42)

    # Verify zero-LoRA identity
    first_obj_path = os.path.join(TRAIN_DATA, test_objects[0])
    first_normal, first_depth = create_combined_grids(first_obj_path)
    first_cond = Image.open(os.path.join(first_obj_path, 'image/000.png')).convert('RGBA')

    # Skip zero-lora identity check for speed

    results = []

    for obj_id in test_objects:
        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_img = Image.open(os.path.join(obj_path, 'image/000.png')).convert('RGBA')
        normal_grid, depth_grid = create_combined_grids(obj_path)

        if normal_grid is None:
            print(f"Skipping {obj_id}: missing normal/depth")
            continue

        row = {'obj_id': obj_id}

        # Config A: Original
        print(f"\n{obj_id}")
        print("  Config A: Original...")
        reload_base_weights(pipeline)
        verify_reference_attention(pipeline)
        img_a = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        view_a = extract_first_view(img_a)

        # Config B: broken r4 (Full LoRA)
        print("  Config B: Full LoRA r4 (broken)...")
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet(bare_unet, checkpoints['broken_r4']['path'],
                            rank=4, alpha=4)
        verify_reference_attention(pipeline)
        img_b = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        view_b = extract_first_view(img_b)

        # Config C: crash r8 (Full LoRA)
        print("  Config C: Full LoRA r8 (crash)...")
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet(bare_unet, checkpoints['crash_r8']['path'],
                            rank=8, alpha=8)
        verify_reference_attention(pipeline)
        img_c = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        view_c = extract_first_view(img_c)

        # Config D: attn2-only r4
        print("  Config D: attn2-only r4...")
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet_attn2_only(bare_unet, checkpoints['attn2_r4']['path'],
                                        rank=4, alpha=4)
        verify_reference_attention(pipeline)
        img_d = run_inference(pipeline, cond_img, normal_grid, depth_grid, seed=42)
        view_d = extract_first_view(img_d)

        # Compute PSNR vs Original
        row['psnr_broken_r4'] = compute_psnr(view_a, view_b)
        row['psnr_crash_r8'] = compute_psnr(view_a, view_c)
        row['psnr_attn2_r4'] = compute_psnr(view_a, view_d)

        print(f"  PSNR vs Original:")
        print(f"    Full LoRA r4:  {row['psnr_broken_r4']:.2f} dB")
        print(f"    Full LoRA r8:  {row['psnr_crash_r8']:.2f} dB")
        print(f"    attn2-only r4: {row['psnr_attn2_r4']:.2f} dB")

        results.append(row)

    # Save results
    import csv
    csv_path = os.path.join(output_dir, 'psnr_vs_original_verified.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['obj_id', 'psnr_broken_r4', 'psnr_crash_r8', 'psnr_attn2_r4'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY (PSNR vs Original, correct pipeline)")
    print(f"{'='*60}")

    def avg(key):
        vals = [r[key] for r in results]
        return np.mean(vals)

    print(f"Full LoRA r4 (broken):  {avg('psnr_broken_r4'):.2f} dB")
    print(f"Full LoRA r8 (crash):   {avg('psnr_crash_r8'):.2f} dB")
    print(f"attn2-only r4:          {avg('psnr_attn2_r4'):.2f} dB")

    # Save markdown
    md_path = os.path.join(output_dir, 'psnr_vs_original_verified.md')
    with open(md_path, 'w') as f:
        f.write("# PSNR vs Original (Verified, Correct Pipeline)\n\n")
        f.write("**Pipeline**: ControlNet + depth/normal grids\n\n")
        f.write("**GPU**: RTX 5090 32.6GB\n\n")
        f.write("## Summary\n\n")
        f.write("| Method | Checkpoint | PSNR vs Original |\n")
        f.write("|--------|-----------|------------------|\n")
        f.write(f"| Full LoRA (r4, lr=1e-4, 100 steps) | broken-r4 | {avg('psnr_broken_r4'):.2f} dB |\n")
        f.write(f"| Full LoRA (r8, lr=5e-4, 500 steps) | crash-r8 | {avg('psnr_crash_r8'):.2f} dB |\n")
        f.write(f"| attn2-only (r4, lr=1e-5, 250 steps) | attn2-r4 | {avg('psnr_attn2_r4'):.2f} dB |\n")
        f.write("\n## Per-Object\n\n")
        f.write("| Object | Full LoRA r4 | Full LoRA r8 | attn2-only r4 |\n")
        f.write("|--------|-------------|-------------|---------------|\n")
        for r in results:
            f.write(f"| {r['obj_id'][:16]}... | {r['psnr_broken_r4']:.2f} | {r['psnr_crash_r8']:.2f} | {r['psnr_attn2_r4']:.2f} |\n")

    print(f"\nResults saved to {md_path}")


if __name__ == '__main__':
    main()
