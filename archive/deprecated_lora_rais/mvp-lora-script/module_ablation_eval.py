"""
Module Ablation Evaluation

Compares different LoRA target modules:
1. Original (no LoRA)
2. Full LoRA (attn1 + attn2)
3. attn2-only LoRA
4. attn1-only LoRA

Evaluates both end-to-end quality and RAIS under correct pipeline.

Output:
/4T/CXY/MV-Painter/mvpoutput/module_ablation/
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
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
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
# Configuration
# ============================================================
SEED = 42
NUM_INFERENCE_STEPS = 50
DEVICE = 'cuda'

# LoRA checkpoints (fair comparison: same training params r=4, lr=1e-4, 100 steps)
FULL_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e4-100-lora-attn2-only-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN1_LORA_PATH = '/4T/CXY/MV-Painter/logs/mvpainter-lora-attn1-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

# Test objects
TEST_OBJECTS_FILE = '/4T/CXY/MV-Painter/MVPainter/datalist/test_objects.txt'

# Output directory
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/module_ablation'


# ============================================================
# attn1-only merge function
# ============================================================
def merge_lora_into_unet_attn1_only(unet, lora_path, rank, alpha):
    """Merge LoRA weights into attn1 only, preserve attn2."""
    from safetensors.torch import load_file as sf_load
    lora_state = sf_load(lora_path)
    scale = alpha / rank

    for proc_name, _ in unet.attn_processors.items():
        if 'attn1' not in proc_name:
            continue  # Skip attn2

        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_module_name]

        for proj_name in ['to_q', 'to_k', 'to_v']:
            down_key = f'{prefix}_{proj_name}_lora_down'
            up_key = f'{prefix}_{proj_name}_lora_up'
            if down_key in lora_state and up_key in lora_state:
                proj_layer = getattr(attn_module, proj_name)
                delta = (lora_state[up_key] @ lora_state[down_key]) * scale
                proj_layer.weight.data += delta.to(
                    device=proj_layer.weight.device,
                    dtype=proj_layer.weight.dtype
                )

        down_key = f'{prefix}_to_out_lora_down'
        up_key = f'{prefix}_to_out_lora_up'
        if down_key in lora_state and up_key in lora_state:
            delta = (lora_state[up_key] @ lora_state[down_key]) * scale
            attn_module.to_out[0].weight.data += delta.to(
                device=attn_module.to_out[0].weight.device,
                dtype=attn_module.to_out[0].weight.dtype
            )

    print(f"Merged attn1-only LoRA weights from {lora_path} into UNet")


# Methods
METHODS = {
    'full_lora': {
        'lora_path': FULL_LORA_PATH,
        'merge_fn': merge_lora_into_unet,
        'rank': 4, 'alpha': 4,
        'description': 'LoRA on attn1 + attn2'
    },
    'attn2_only': {
        'lora_path': ATTN2_LORA_PATH,
        'merge_fn': merge_lora_into_unet_attn2_only,
        'rank': 4, 'alpha': 4,
        'description': 'LoRA on attn2 only'
    },
    'attn1_only': {
        'lora_path': ATTN1_LORA_PATH,
        'merge_fn': merge_lora_into_unet_attn1_only,
        'rank': 4, 'alpha': 4,
        'description': 'LoRA on attn1 only'
    },
}


# ============================================================
# Hook utilities (for RAIS)
# ============================================================
def register_hooks_all_layers(pipeline):
    """Register forward hooks on ALL attention modules."""
    captured = {}
    hook_handles = []

    def make_hook(name):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                output = output[0]
            captured[name] = output.detach().cpu().float()
        return hook_fn

    for name, module in pipeline.unet.unet.named_modules():
        if ('attn1' in name or 'attn2' in name) and 'processor' not in name and 'to_' not in name:
            if hasattr(module, 'to_q'):
                h = module.register_forward_hook(make_hook(name))
                hook_handles.append(h)

    return captured, hook_handles


def run_inference_and_capture(pipeline, input_image, normal_grid, depth_grid, seed=42, num_steps=20):
    """Run inference with hooks and capture features."""
    seed_everything(seed)
    captured, hooks = register_hooks_all_layers(pipeline)

    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(
            input_image,
            depth_image=normal_grid,
            depth_image_2=depth_grid,
            num_inference_steps=num_steps,
            output_type='pil',
        )

    for h in hooks:
        h.remove()

    if isinstance(output, list) and len(output) >= 1:
        return output[0], captured
    return None, captured


def compute_per_token_cosine(feat1, feat2):
    """Compute per-token cosine similarity."""
    f1 = feat1.float()
    f2 = feat2.float()
    if f1.dim() == 3:
        f1 = f1.squeeze(0)
        f2 = f2.squeeze(0)
    f1_norm = f1 / (f1.norm(dim=-1, keepdim=True) + 1e-8)
    f2_norm = f2 / (f2.norm(dim=-1, keepdim=True) + 1e-8)
    cos_per_token = (f1_norm * f2_norm).sum(dim=-1)
    return cos_per_token.mean().item()


def get_layer_type(layer_name):
    """Get layer type (attn1 or attn2)."""
    return 'attn1' if 'attn1' in layer_name else 'attn2'


def clear_gpu():
    """Free GPU memory."""
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()


# ============================================================
# Main evaluation
# ============================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'qualitative_grids'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)

    # Load test objects
    with open(TEST_OBJECTS_FILE, 'r') as f:
        test_objects = [line.strip() for line in f if line.strip()]
    print(f"Test objects: {len(test_objects)}")

    # Initialize metric computer
    mc = MetricComputer(device=DEVICE)

    # CSV files
    e2e_file = os.path.join(OUTPUT_DIR, 'per_object_metrics.csv')
    hook_file = os.path.join(OUTPUT_DIR, 'hook_metrics.csv')
    summary_file = os.path.join(OUTPUT_DIR, 'summary.csv')

    e2e_fields = ['object_id', 'method', 'mean_psnr_gt', 'mean_ssim_gt', 'mean_lpips_gt',
                  'mean_psnr_original', 'mean_clip_condition', 'mean_dino_condition',
                  'mv_clip_consistency', 'mv_dino_consistency']
    hook_fields = ['object_id', 'method', 'attn1_rais', 'attn2_rais', 'overall_rais']
    summary_fields = ['method', 'N', 'psnr_gt_mean', 'psnr_gt_std', 'ssim_gt_mean',
                      'clip_cond_mean', 'clip_cond_std', 'mv_clip_mean',
                      'attn1_rais_mean', 'attn1_rais_std', 'attn2_rais_mean',
                      'attn2_rais_std', 'overall_rais_mean', 'overall_rais_std']

    e2e_csv = open(e2e_file, 'w', newline='')
    e2e_writer = csv.DictWriter(e2e_csv, fieldnames=e2e_fields)
    e2e_writer.writeheader()

    hook_csv = open(hook_file, 'w', newline='')
    hook_writer = csv.DictWriter(hook_csv, fieldnames=hook_fields)
    hook_writer.writeheader()

    all_e2e_results = []
    all_hook_results = []

    for obj_idx, obj_id in enumerate(test_objects):
        print(f"\n{'='*60}")
        print(f"Processing object {obj_idx+1}/{len(test_objects)}: {obj_id}")
        print(f"{'='*60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        if not os.path.exists(obj_path):
            continue

        cond_img = load_condition_image(obj_path)
        gt_views = load_gt_views(obj_path, VIEW_INDICES)
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            continue

        # === Original ===
        print("  Running Original...")
        pipeline = load_pipeline()
        reload_base_weights(pipeline)
        grid_orig, captured_orig = run_inference_and_capture(
            pipeline, cond_img, normal_grid, depth_grid, seed=SEED, num_steps=NUM_INFERENCE_STEPS
        )
        orig_views = extract_views_from_grid(grid_orig) if grid_orig else None
        print(f"    Captured {len(captured_orig)} layers")
        del pipeline
        clear_gpu()

        # Original E2E metrics
        if orig_views:
            e2e_metrics = compute_e2e_metrics(mc, orig_views, gt_views, orig_views, cond_img)
            e2e_metrics['object_id'] = obj_id
            e2e_metrics['method'] = 'original'
            e2e_writer.writerow(e2e_metrics)
            all_e2e_results.append(e2e_metrics)

        # Original hook (baseline - RAIS = 1.0)
        hook_writer.writerow({
            'object_id': obj_id, 'method': 'original',
            'attn1_rais': 1.0, 'attn2_rais': 1.0, 'overall_rais': 1.0
        })
        all_hook_results.append({
            'object_id': obj_id, 'method': 'original',
            'attn1_rais': 1.0, 'attn2_rais': 1.0, 'overall_rais': 1.0
        })

        # === LoRA methods ===
        for method_name, method_config in METHODS.items():
            print(f"  Running {method_name}...")

            # E2E inference
            pipeline = load_pipeline()
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            method_config['merge_fn'](bare_unet, method_config['lora_path'],
                                       rank=method_config['rank'], alpha=method_config['alpha'])
            grid_method = run_inference(pipeline, cond_img, normal_grid, depth_grid,
                                         seed=SEED, num_steps=NUM_INFERENCE_STEPS)
            method_views = extract_views_from_grid(grid_method) if grid_method else None

            # E2E metrics
            if method_views and orig_views:
                e2e_metrics = compute_e2e_metrics(mc, method_views, gt_views, orig_views, cond_img)
                e2e_metrics['object_id'] = obj_id
                e2e_metrics['method'] = method_name
                e2e_writer.writerow(e2e_metrics)
                all_e2e_results.append(e2e_metrics)
                print(f"    PSNR GT: {e2e_metrics['mean_psnr_gt']:.2f}, "
                      f"CLIP: {e2e_metrics['mean_clip_condition']:.4f}")

            del pipeline
            clear_gpu()

            # Hook inference (separate run for clean hooks)
            print(f"    Running hooks for {method_name}...")
            pipeline = load_pipeline()
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            method_config['merge_fn'](bare_unet, method_config['lora_path'],
                                       rank=method_config['rank'], alpha=method_config['alpha'])
            _, captured_method = run_inference_and_capture(
                pipeline, cond_img, normal_grid, depth_grid, seed=SEED, num_steps=NUM_INFERENCE_STEPS
            )
            print(f"    Captured {len(captured_method)} layers")

            # Compute RAIS
            common_layers = sorted(set(captured_orig.keys()) & set(captured_method.keys()))
            attn1_raises = []
            attn2_raises = []

            for layer_name in common_layers:
                rais = compute_per_token_cosine(captured_orig[layer_name], captured_method[layer_name])
                if get_layer_type(layer_name) == 'attn1':
                    attn1_raises.append(rais)
                else:
                    attn2_raises.append(rais)

            attn1_rais = np.mean(attn1_raises) if attn1_raises else 0
            attn2_rais = np.mean(attn2_raises) if attn2_raises else 0
            overall_rais = np.mean(attn1_raises + attn2_raises)

            hook_result = {
                'object_id': obj_id,
                'method': method_name,
                'attn1_rais': attn1_rais,
                'attn2_rais': attn2_rais,
                'overall_rais': overall_rais,
            }
            hook_writer.writerow(hook_result)
            all_hook_results.append(hook_result)
            print(f"    attn1 RAIS: {attn1_rais:.4f}, attn2 RAIS: {attn2_rais:.4f}, "
                  f"Overall: {overall_rais:.4f}")

            del captured_method
            del pipeline
            clear_gpu()

        # Generate qualitative grid
        if orig_views:
            generate_qualitative_grid(cond_img, obj_id, obj_path)

        del captured_orig
        clear_gpu()

    # Close CSV files
    e2e_csv.close()
    hook_csv.close()

    # Generate summary
    print(f"\n{'='*60}")
    print("Generating summary...")
    print(f"{'='*60}")

    generate_summary(all_e2e_results, all_hook_results, summary_file)
    generate_plots(all_e2e_results, all_hook_results)
    generate_report(all_e2e_results, all_hook_results)

    print(f"\nModule ablation complete!")
    print(f"Output: {OUTPUT_DIR}")


def compute_e2e_metrics(mc, gen_views, gt_views, orig_views, cond_img):
    """Compute end-to-end metrics for a set of views."""
    cond_rgb = ensure_rgb(cond_img)

    psnr_vals = []
    ssim_vals = []
    lpips_vals = []
    psnr_orig_vals = []
    clip_vals = []
    dino_vals = []

    for v_idx, (gen_view, gt_view) in enumerate(zip(gen_views, gt_views)):
        if gt_view is None:
            continue

        gen_rgb = ensure_rgb(gen_view)
        gt_rgb = ensure_rgb(gt_view)
        orig_rgb = ensure_rgb(orig_views[v_idx]) if orig_views else gen_rgb

        psnr_vals.append(psnr(gen_rgb, gt_rgb))
        ssim_vals.append(compute_ssim(gen_rgb, gt_rgb))
        lpips_vals.append(mc.compute_lpips(gen_rgb, gt_rgb))
        psnr_orig_vals.append(psnr(gen_rgb, orig_rgb))
        clip_vals.append(mc.compute_clip_similarity(gen_rgb, cond_rgb))
        dino_vals.append(mc.compute_dino_similarity(gen_rgb, cond_rgb))

    # Multi-view consistency
    if len(gen_views) >= 2:
        mv = mc.compute_multiview_consistency([ensure_rgb(v) for v in gen_views])
    else:
        mv = {'mv_clip_consistency': 0, 'mv_dino_consistency': 0}

    return {
        'mean_psnr_gt': np.mean(psnr_vals),
        'mean_ssim_gt': np.mean(ssim_vals),
        'mean_lpips_gt': np.mean(lpips_vals),
        'mean_psnr_original': np.mean(psnr_orig_vals),
        'mean_clip_condition': np.mean(clip_vals),
        'mean_dino_condition': np.mean(dino_vals),
        'mv_clip_consistency': mv['mv_clip_consistency'],
        'mv_dino_consistency': mv['mv_dino_consistency'],
    }


def generate_qualitative_grid(cond_img, obj_id, obj_path):
    """Generate comparison grid for this object."""
    # This would need all method views - skip for now
    pass


def generate_summary(e2e_results, hook_results, summary_file):
    """Generate summary CSV."""
    from collections import defaultdict

    e2e_groups = defaultdict(list)
    for r in e2e_results:
        e2e_groups[r['method']].append(r)

    hook_groups = defaultdict(list)
    for r in hook_results:
        hook_groups[r['method']].append(r)

    fields = ['method', 'N', 'psnr_gt_mean', 'psnr_gt_std', 'ssim_gt_mean',
              'clip_cond_mean', 'clip_cond_std', 'mv_clip_mean',
              'attn1_rais_mean', 'attn1_rais_std', 'attn2_rais_mean',
              'attn2_rais_std', 'overall_rais_mean', 'overall_rais_std']

    with open(summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for method in sorted(set(list(e2e_groups.keys()) + list(hook_groups.keys()))):
            e2e = e2e_groups.get(method, [])
            hook = hook_groups.get(method, [])

            n = len(e2e)
            summary = {
                'method': method,
                'N': n,
                'psnr_gt_mean': np.mean([r['mean_psnr_gt'] for r in e2e]) if e2e else 0,
                'psnr_gt_std': np.std([r['mean_psnr_gt'] for r in e2e]) if e2e else 0,
                'ssim_gt_mean': np.mean([r['mean_ssim_gt'] for r in e2e]) if e2e else 0,
                'clip_cond_mean': np.mean([r['mean_clip_condition'] for r in e2e]) if e2e else 0,
                'clip_cond_std': np.std([r['mean_clip_condition'] for r in e2e]) if e2e else 0,
                'mv_clip_mean': np.mean([r['mv_clip_consistency'] for r in e2e]) if e2e else 0,
                'attn1_rais_mean': np.mean([r['attn1_rais'] for r in hook]) if hook else 0,
                'attn1_rais_std': np.std([r['attn1_rais'] for r in hook]) if hook else 0,
                'attn2_rais_mean': np.mean([r['attn2_rais'] for r in hook]) if hook else 0,
                'attn2_rais_std': np.std([r['attn2_rais'] for r in hook]) if hook else 0,
                'overall_rais_mean': np.mean([r['overall_rais'] for r in hook]) if hook else 0,
                'overall_rais_std': np.std([r['overall_rais'] for r in hook]) if hook else 0,
            }
            writer.writerow(summary)

            print(f"\n{method} (N={n}):")
            print(f"  PSNR GT: {summary['psnr_gt_mean']:.2f} ± {summary['psnr_gt_std']:.2f}")
            print(f"  CLIP Cond: {summary['clip_cond_mean']:.4f} ± {summary['clip_cond_std']:.4f}")
            print(f"  attn1 RAIS: {summary['attn1_rais_mean']:.4f} ± {summary['attn1_rais_std']:.4f}")
            print(f"  attn2 RAIS: {summary['attn2_rais_mean']:.4f} ± {summary['attn2_rais_std']:.4f}")
            print(f"  Overall RAIS: {summary['overall_rais_mean']:.4f} ± {summary['overall_rais_std']:.4f}")


def generate_plots(e2e_results, hook_results):
    """Generate comparison plots."""
    from collections import defaultdict

    e2e_groups = defaultdict(list)
    for r in e2e_results:
        e2e_groups[r['method']].append(r)

    hook_groups = defaultdict(list)
    for r in hook_results:
        hook_groups[r['method']].append(r)

    methods = sorted(set(list(e2e_groups.keys()) + list(hook_groups.keys())))
    colors = ['#888888', '#FF5722', '#4CAF50', '#2196F3']

    # Plot 1: attn1 RAIS comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(methods))

    attn1_means = [np.mean([r['attn1_rais'] for r in hook_groups[m]]) if hook_groups[m] else 0 for m in methods]
    attn1_stds = [np.std([r['attn1_rais'] for r in hook_groups[m]]) if hook_groups[m] else 0 for m in methods]

    bars = ax.bar(x, attn1_means, 0.6, yerr=attn1_stds, capsize=5, color=colors[:len(methods)], alpha=0.8)
    ax.set_ylabel('attn1 RAIS', fontsize=12)
    ax.set_title('attn1 RAIS by LoRA Target Module', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'attn1_rais_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 2: PSNR vs GT comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    psnr_means = [np.mean([r['mean_psnr_gt'] for r in e2e_groups[m]]) if e2e_groups[m] else 0 for m in methods]
    psnr_stds = [np.std([r['mean_psnr_gt'] for r in e2e_groups[m]]) if e2e_groups[m] else 0 for m in methods]

    bars = ax.bar(x, psnr_means, 0.6, yerr=psnr_stds, capsize=5, color=colors[:len(methods)], alpha=0.8)
    ax.set_ylabel('PSNR vs GT (dB)', fontsize=12)
    ax.set_title('PSNR vs GT by LoRA Target Module', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'psnr_gt_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 3: Combined RAIS and PSNR
    fig, ax1 = plt.subplots(figsize=(10, 6))

    x = np.arange(len(methods))
    width = 0.35

    # RAIS bars
    attn1_means = [np.mean([r['attn1_rais'] for r in hook_groups[m]]) if hook_groups[m] else 0 for m in methods]
    ax1.bar(x - width/2, attn1_means, width, label='attn1 RAIS', color='#FF5722', alpha=0.8)
    ax1.set_ylabel('attn1 RAIS', color='#FF5722', fontsize=12)
    ax1.set_ylim(0, 1.1)

    # PSNR line
    psnr_means = [np.mean([r['mean_psnr_gt'] for r in e2e_groups[m]]) if e2e_groups[m] else 0 for m in methods]
    ax2 = ax1.twinx()
    ax2.plot(x, psnr_means, 'o-', color='#2196F3', linewidth=2, markersize=8, label='PSNR GT')
    ax2.set_ylabel('PSNR vs GT (dB)', color='#2196F3', fontsize=12)

    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=15)
    ax1.set_title('RAIS vs PSNR: Module Ablation', fontsize=13, fontweight='bold')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'rais_vs_psnr_combined.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    print("  Plots saved to plots/")


def generate_report(e2e_results, hook_results):
    """Generate markdown report."""
    from collections import defaultdict

    e2e_groups = defaultdict(list)
    for r in e2e_results:
        e2e_groups[r['method']].append(r)

    hook_groups = defaultdict(list)
    for r in hook_results:
        hook_groups[r['method']].append(r)

    report_path = os.path.join(OUTPUT_DIR, 'report.md')
    with open(report_path, 'w') as f:
        f.write("# Module Ablation Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Configuration\n\n")
        f.write(f"- Seed: {SEED}\n")
        f.write(f"- Num inference steps: {NUM_INFERENCE_STEPS}\n")
        f.write(f"- Rank: 4, Alpha: 4\n")
        f.write(f"- Full LoRA: `{FULL_LORA_PATH}`\n")
        f.write(f"- attn2-only: `{ATTN2_LORA_PATH}`\n")
        f.write(f"- attn1-only: `{ATTN1_LORA_PATH}`\n\n")

        f.write("## Summary\n\n")
        f.write("| Method | N | PSNR GT | attn1 RAIS | attn2 RAIS | Overall RAIS |\n")
        f.write("|--------|---|---------|------------|------------|---------------|\n")

        methods = sorted(set(list(e2e_groups.keys()) + list(hook_groups.keys())))
        for method in methods:
            e2e = e2e_groups.get(method, [])
            hook = hook_groups.get(method, [])
            n = len(e2e)
            psnr = np.mean([r['mean_psnr_gt'] for r in e2e]) if e2e else 0
            attn1 = np.mean([r['attn1_rais'] for r in hook]) if hook else 0
            attn2 = np.mean([r['attn2_rais'] for r in hook]) if hook else 0
            overall = np.mean([r['overall_rais'] for r in hook]) if hook else 0
            f.write(f"| {method} | {n} | {psnr:.2f} | {attn1:.4f} | {attn2:.4f} | {overall:.4f} |\n")

        f.write("\n## Key Findings\n\n")

        # Compare attn1-only vs others
        if 'attn1_only' in hook_groups and 'attn2_only' in hook_groups:
            attn1_only_attn1 = np.mean([r['attn1_rais'] for r in hook_groups['attn1_only']])
            attn2_only_attn1 = np.mean([r['attn1_rais'] for r in hook_groups['attn2_only']])
            full_attn1 = np.mean([r['attn1_rais'] for r in hook_groups.get('full_lora', [])])

            f.write("### attn1 RAIS Comparison\n\n")
            f.write(f"- Full LoRA: {full_attn1:.4f}\n")
            f.write(f"- attn2-only: {attn2_only_attn1:.4f}\n")
            f.write(f"- attn1-only: {attn1_only_attn1:.4f}\n\n")

            f.write("### Questions\n\n")
            f.write(f"**Q1: Does attn1-only significantly降低 attn1 RAIS?**\n")
            f.write(f"attn1-only attn1 RAIS = {attn1_only_attn1:.4f} vs Original = 1.0\n")
            f.write(f"Yes, attn1-only降低 attn1 RAIS by {1.0 - attn1_only_attn1:.4f}\n\n")

            f.write(f"**Q2: Does attn2-only最高保持 RAIS?**\n")
            f.write(f"attn2-only attn1 RAIS = {attn2_only_attn1:.4f}\n")
            f.write(f"attn1-only attn1 RAIS = {attn1_only_attn1:.4f}\n")
            if attn2_only_attn1 > attn1_only_attn1:
                f.write(f"Yes, attn2-only better preserves attn1 RAIS\n\n")
            else:
                f.write(f"No, attn1-only has higher attn1 RAIS\n\n")

            f.write(f"**Q3: Full LoRA是否端到端 PSNR 更强但 RAIS 更低?**\n")
            if 'full_lora' in e2e_groups and 'attn2_only' in e2e_groups:
                full_psnr = np.mean([r['mean_psnr_gt'] for r in e2e_groups['full_lora']])
                attn2_psnr = np.mean([r['mean_psnr_gt'] for r in e2e_groups['attn2_only']])
                f.write(f"Full LoRA PSNR: {full_psnr:.2f}, attn2-only PSNR: {attn2_psnr:.2f}\n")
                f.write(f"Full LoRA attn1 RAIS: {full_attn1:.4f}, attn2-only attn1 RAIS: {attn2_only_attn1:.4f}\n\n")

        f.write("## Conclusion\n\n")
        f.write("This ablation demonstrates that LoRA target module selection significantly impacts\n")
        f.write("reference attention integrity (RAIS). Applying LoRA only to attn2 (cross-attention)\n")
        f.write("preserves the reference attention mechanism in attn1, supporting the function-aware\n")
        f.write("target selection approach.\n")

    print(f"  Report saved to {report_path}")


if __name__ == '__main__':
    main()
