"""
Fair Module Ablation Evaluation

Compares different LoRA target modules with FAIR training params:
- Full LoRA: r=4, lr=1e-5, 250 steps
- attn2-only: r=4, lr=1e-5, 250 steps

Output:
/4T/CXY/MV-Painter/mvpoutput/module_ablation_fair/
"""
import os
import sys
import gc
import csv
import json
import numpy as np
import torch
from PIL import Image
from safetensors.torch import load_file
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, get_ref_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, seed_everything, psnr,
    CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA, VIEW_FILES,
)
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from correct_pipeline_eval import (
    MetricComputer, extract_views_from_grid, ensure_rgb, compute_ssim,
    load_gt_views, load_condition_image, VIEW_INDICES,
)


# ============================================================
# Configuration - FAIR comparison
# ============================================================
SEED = 42
NUM_INFERENCE_STEPS = 50
DEVICE = 'cuda'

# Fair LoRA checkpoints (r=4, lr=1e-5, 250 steps)
FULL_LORA_FAIR_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-full-r4-lr1e5-250-fair-lora-full-fair-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

# Test objects
TEST_OBJECTS_FILE = '/4T/CXY/MV-Painter/MVPainter/datalist/test_objects.txt'

# Output directory
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/module_ablation_fair'


def load_test_objects():
    with open(TEST_OBJECTS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def compute_rais(original_features, lora_features):
    """Compute Reference Attention Integrity Score."""
    similarities = []
    for key in original_features:
        if key in lora_features:
            orig = original_features[key].float().flatten()
            lora = lora_features[key].float().flatten()
            sim = torch.nn.functional.cosine_similarity(orig.unsqueeze(0), lora.unsqueeze(0)).item()
            similarities.append(sim)
    return np.mean(similarities) if similarities else 0.0


def extract_hook_features(hook_outputs):
    """Extract features from hook outputs."""
    features = {}
    for name, outputs in hook_outputs.items():
        if outputs:
            features[name] = outputs[-1]
    return features


def run_single_eval(pipeline, cond_image, gt_views, depth_grid, normal_grid,
                    method_name, metrics_computer, device):
    """Run inference and compute metrics for a single configuration."""
    seed_everything(SEED)

    # Run inference
    with torch.no_grad():
        output = run_inference(
            pipeline, cond_image,
            normal_grid=normal_grid,
            depth_grid=depth_grid,
            num_steps=NUM_INFERENCE_STEPS,
        )

    # Extract views
    generated_views = extract_views_from_grid(output)

    # Compute metrics
    results = {
        'method': method_name,
        'psnr_gt': [],
        'ssim_gt': [],
        'clip_condition': [],
        'dino_condition': [],
    }

    for i, (gen_view, gt_view) in enumerate(zip(generated_views, gt_views)):
        gen_rgb = ensure_rgb(gen_view)
        gt_rgb = ensure_rgb(gt_view)

        # PSNR vs GT
        results['psnr_gt'].append(psnr(gen_rgb, gt_rgb))
        results['ssim_gt'].append(compute_ssim(gen_rgb, gt_rgb))

        # CLIP and DINO
        clip_sim = metrics_computer.compute_clip_similarity(cond_image, gen_rgb)
        dino_sim = metrics_computer.compute_dino_similarity(cond_image, gen_rgb)
        results['clip_condition'].append(clip_sim)
        results['dino_condition'].append(dino_sim)

    # Average metrics
    return {
        'method': method_name,
        'psnr_gt': np.mean(results['psnr_gt']),
        'ssim_gt': np.mean(results['ssim_gt']),
        'clip_condition': np.mean(results['clip_condition']),
        'dino_condition': np.mean(results['dino_condition']),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)

    print(f"=" * 60)
    print(f"Fair Module Ablation Evaluation")
    print(f"=" * 60)
    print(f"Full LoRA (fair): {FULL_LORA_FAIR_PATH}")
    print(f"attn2-only: {ATTN2_LORA_PATH}")
    print(f"Seed: {SEED}")
    print()

    # Verify checkpoints exist
    for path, name in [(FULL_LORA_FAIR_PATH, "Full LoRA (fair)"), (ATTN2_LORA_PATH, "attn2-only")]:
        if not os.path.exists(path):
            print(f"ERROR: {name} checkpoint not found: {path}")
            return

    # Load test objects
    test_objects = load_test_objects()
    print(f"Test objects: {len(test_objects)}")
    print()

    # Initialize metrics computer
    metrics_computer = MetricComputer(DEVICE)

    # Results storage
    all_results = []

    for obj_idx, obj_id in enumerate(test_objects):
        print(f"\n{'='*60}")
        print(f"Object {obj_idx+1}/{len(test_objects)}: {obj_id}")
        print(f"{'='*60}")

        # Load condition image and GT views
        obj_path = os.path.join(TRAIN_DATA, obj_id)
        cond_image = load_condition_image(obj_path)
        gt_views = load_gt_views(obj_path, VIEW_INDICES)

        if cond_image is None or gt_views is None:
            print(f"  Skipping - failed to load data")
            continue

        # Load depth/normal grids
        obj_dir = os.path.join(TRAIN_DATA, obj_id)
        depth_grid, normal_grid = create_combined_grids(obj_dir)

        if depth_grid is None:
            print(f"  Skipping - failed to create grids")
            continue

        # ========== Original (no LoRA) ==========
        print(f"  Running Original...")
        pipeline = load_pipeline()
        reload_base_weights(pipeline)
        verify_reference_attention(pipeline)

        result_orig = run_single_eval(
            pipeline, cond_image, gt_views, depth_grid, normal_grid,
            'original', metrics_computer, DEVICE
        )
        all_results.append(result_orig)
        print(f"    PSNR GT: {result_orig['psnr_gt']:.2f}")

        del pipeline
        gc.collect()
        torch.cuda.empty_cache()

        # ========== Full LoRA (fair) ==========
        print(f"  Running Full LoRA (fair)...")
        pipeline = load_pipeline()
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet(bare_unet, FULL_LORA_FAIR_PATH, rank=4, alpha=4)
        verify_reference_attention(pipeline)

        result_full = run_single_eval(
            pipeline, cond_image, gt_views, depth_grid, normal_grid,
            'full_lora_fair', metrics_computer, DEVICE
        )
        all_results.append(result_full)
        print(f"    PSNR GT: {result_full['psnr_gt']:.2f}")

        del pipeline
        gc.collect()
        torch.cuda.empty_cache()

        # ========== attn2-only ==========
        print(f"  Running attn2-only...")
        pipeline = load_pipeline()
        reload_base_weights(pipeline)
        bare_unet = get_bare_unet(pipeline)
        merge_lora_into_unet_attn2_only(bare_unet, ATTN2_LORA_PATH, rank=4, alpha=4)
        verify_reference_attention(pipeline)

        result_attn2 = run_single_eval(
            pipeline, cond_image, gt_views, depth_grid, normal_grid,
            'attn2_only', metrics_computer, DEVICE
        )
        all_results.append(result_attn2)
        print(f"    PSNR GT: {result_attn2['psnr_gt']:.2f}")

        del pipeline
        gc.collect()
        torch.cuda.empty_cache()

    # ========== Summary ==========
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")

    # Group by method
    methods = {}
    for r in all_results:
        if r['method'] not in methods:
            methods[r['method']] = []
        methods[r['method']].append(r)

    # Compute averages
    summary = []
    for method, results in methods.items():
        avg = {
            'method': method,
            'n': len(results),
            'psnr_gt': np.mean([r['psnr_gt'] for r in results]),
            'ssim_gt': np.mean([r['ssim_gt'] for r in results]),
            'clip_condition': np.mean([r['clip_condition'] for r in results]),
            'dino_condition': np.mean([r['dino_condition'] for r in results]),
        }
        summary.append(avg)
        print(f"\n{method}:")
        print(f"  N: {avg['n']}")
        print(f"  PSNR GT: {avg['psnr_gt']:.2f}")
        print(f"  SSIM GT: {avg['ssim_gt']:.4f}")
        print(f"  CLIP Cond: {avg['clip_condition']:.4f}")
        print(f"  DINO Cond: {avg['dino_condition']:.4f}")

    # Save results
    csv_path = os.path.join(OUTPUT_DIR, 'summary.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['method', 'n', 'psnr_gt', 'ssim_gt', 'clip_condition', 'dino_condition'])
        writer.writeheader()
        writer.writerows(summary)
    print(f"\nResults saved to {csv_path}")

    # Save per-object results
    per_obj_path = os.path.join(OUTPUT_DIR, 'per_object.csv')
    with open(per_obj_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['method', 'psnr_gt', 'ssim_gt', 'clip_condition', 'dino_condition'])
        writer.writeheader()
        writer.writerows(all_results)
    print(f"Per-object results saved to {per_obj_path}")

    # Generate report
    report_path = os.path.join(OUTPUT_DIR, 'report.md')
    with open(report_path, 'w') as f:
        f.write("# Fair Module Ablation Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Configuration\n\n")
        f.write(f"- Seed: {SEED}\n")
        f.write(f"- Num inference steps: {NUM_INFERENCE_STEPS}\n")
        f.write(f"- Full LoRA (fair): `{FULL_LORA_FAIR_PATH}`\n")
        f.write(f"- attn2-only: `{ATTN2_LORA_PATH}`\n")
        f.write(f"- Training params: r=4, lr=1e-5, 250 steps (both)\n\n")
        f.write("## Summary\n\n")
        f.write("| Method | N | PSNR GT ↑ | SSIM GT ↑ | CLIP Cond ↑ | DINO Cond ↑ |\n")
        f.write("|--------|---|-----------|-----------|-------------|-------------|\n")
        for s in summary:
            f.write(f"| {s['method']} | {s['n']} | {s['psnr_gt']:.2f} | {s['ssim_gt']:.4f} | {s['clip_condition']:.4f} | {s['dino_condition']:.4f} |\n")
        f.write("\n")

        # Comparison
        full_lora = next((s for s in summary if s['method'] == 'full_lora_fair'), None)
        attn2_only = next((s for s in summary if s['method'] == 'attn2_only'), None)
        original = next((s for s in summary if s['method'] == 'original'), None)

        if full_lora and attn2_only and original:
            f.write("## Key Findings\n\n")
            f.write(f"### PSNR GT Comparison\n")
            f.write(f"- Full LoRA (fair): {full_lora['psnr_gt']:.2f}\n")
            f.write(f"- attn2-only: {attn2_only['psnr_gt']:.2f}\n")
            f.write(f"- Original: {original['psnr_gt']:.2f}\n")
            f.write(f"- Delta (Full - attn2): {full_lora['psnr_gt'] - attn2_only['psnr_gt']:.2f}\n\n")

            f.write(f"### CLIP Condition Similarity\n")
            f.write(f"- Full LoRA (fair): {full_lora['clip_condition']:.4f}\n")
            f.write(f"- attn2-only: {attn2_only['clip_condition']:.4f}\n")
            f.write(f"- Delta: {full_lora['clip_condition'] - attn2_only['clip_condition']:.4f}\n\n")

            f.write("## Conclusion\n\n")
            f.write("This experiment uses **fair** training parameters (r=4, lr=1e-5, 250 steps) for both methods.\n")

    print(f"Report saved to {report_path}")

    # Generate comparison plot
    plot_path = os.path.join(OUTPUT_DIR, 'plots', 'comparison.png')
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    methods_order = ['original', 'full_lora_fair', 'attn2_only']
    colors = ['#2ecc71', '#e74c3c', '#3498db']

    for ax, metric, label in zip(axes, ['psnr_gt', 'clip_condition', 'dino_condition'], ['PSNR GT', 'CLIP Condition', 'DINO Condition']):
        values = []
        for m in methods_order:
            s = next((x for x in summary if x['method'] == m), None)
            values.append(s[metric] if s else 0)

        bars = ax.bar(methods_order, values, color=colors)
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.tick_params(axis='x', rotation=45)

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{val:.2f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {plot_path}")

    print(f"\n{'='*60}")
    print(f"Done!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
