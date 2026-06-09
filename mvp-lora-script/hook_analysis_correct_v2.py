"""
Hook Analysis v2: RAIS/RSD under Correct Pipeline (ControlNet + Depth).

Captures reference features from ALL attention layers (attn1 + attn2) for
Original, Full LoRA, attn2-only LoRA, then computes:
- Per-layer RAIS (Reference Attention Integrity Score) = cosine similarity vs Original
- Per-object RAIS (averaged across layers)
- Depth-wise RAIS (shallow/middle/deep)
- RSD (Reference State Drift) = 1 - RAIS

Output:
- per_layer_hook_metrics.csv
- per_object_hook_metrics.csv
- hook_summary.csv
- Layer-wise plot
- Depth-wise bar chart
- report.md
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
    create_combined_grids, seed_everything,
    CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only


# ============================================================
# Configuration
# ============================================================
SEED = 42
NUM_INFERENCE_STEPS = 20  # Fewer steps for hook analysis
DEVICE = 'cuda'

# LoRA checkpoints
FULL_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

# Test objects
TEST_OBJECTS_FILE = '/4T/CXY/MV-Painter/mvpoutput/paper_assets/test_objects_300.txt'

# Output directory
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/hook_analysis_correct_v2_300'

# Methods to compare (excluding original which is the baseline)
METHODS = {
    'full_lora_s1.0': {'lora_path': FULL_LORA_PATH, 'merge_fn': merge_lora_into_unet, 'rank': 4, 'alpha': 4},
    'full_lora_s0.25': {'lora_path': FULL_LORA_PATH, 'merge_fn': merge_lora_into_unet, 'rank': 4, 'alpha': 1},
    'attn2_only_s1.0': {'lora_path': ATTN2_LORA_PATH, 'merge_fn': merge_lora_into_unet_attn2_only, 'rank': 4, 'alpha': 4},
    'attn2_only_s0.25': {'lora_path': ATTN2_LORA_PATH, 'merge_fn': merge_lora_into_unet_attn2_only, 'rank': 4, 'alpha': 1},
}


# ============================================================
# Hook utilities
# ============================================================
def register_hooks_all_layers(pipeline):
    """Register forward hooks on ALL attention modules (attn1 + attn2)."""
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
    """Compute per-token cosine similarity, then average."""
    f1 = feat1.float()
    f2 = feat2.float()

    if f1.dim() == 3:
        f1 = f1.squeeze(0)
        f2 = f2.squeeze(0)

    f1_norm = f1 / (f1.norm(dim=-1, keepdim=True) + 1e-8)
    f2_norm = f2 / (f2.norm(dim=-1, keepdim=True) + 1e-8)

    cos_per_token = (f1_norm * f2_norm).sum(dim=-1)
    return cos_per_token.mean().item()


def get_layer_info(layer_name):
    """Extract layer type and depth from layer name."""
    layer_type = 'attn1' if 'attn1' in layer_name else 'attn2'

    # Parse block index for depth
    # Typical: "unet.down_blocks.1.attentions.0.transformer_blocks.0.attn1"
    parts = layer_name.split('.')

    # Determine depth category based on block structure
    if 'down_blocks' in layer_name:
        # Find the index after 'down_blocks'
        try:
            idx = parts.index('down_blocks')
            block_idx = int(parts[idx + 1]) if idx + 1 < len(parts) else 0
        except (ValueError, IndexError):
            block_idx = 0
        if block_idx <= 1:
            depth = 'shallow'
        elif block_idx <= 2:
            depth = 'middle'
        else:
            depth = 'deep'
    elif 'mid_block' in layer_name:
        depth = 'middle'
    elif 'up_blocks' in layer_name:
        try:
            idx = parts.index('up_blocks')
            block_idx = int(parts[idx + 1]) if idx + 1 < len(parts) else 0
        except (ValueError, IndexError):
            block_idx = 0
        if block_idx <= 1:
            depth = 'deep'
        elif block_idx <= 2:
            depth = 'middle'
        else:
            depth = 'shallow'
    else:
        depth = 'unknown'

    return layer_type, depth


def clear_gpu():
    """Aggressively free GPU memory."""
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()


# ============================================================
# Main analysis
# ============================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)

    # Load test objects
    with open(TEST_OBJECTS_FILE, 'r') as f:
        test_objects = [line.strip() for line in f if line.strip()]
    print(f"Test objects: {len(test_objects)}")

    # CSV files
    per_layer_file = os.path.join(OUTPUT_DIR, 'per_layer_hook_metrics.csv')
    per_object_file = os.path.join(OUTPUT_DIR, 'per_object_hook_metrics.csv')
    summary_file = os.path.join(OUTPUT_DIR, 'hook_summary.csv')

    layer_fields = ['object_id', 'method', 'layer_name', 'layer_type', 'depth', 'rais']
    object_fields = ['object_id', 'method', 'attn1_rais', 'attn2_rais', 'overall_rais',
                     'shallow_rais', 'middle_rais', 'deep_rais', 'rsd']
    summary_fields = ['method', 'N_objects', 'attn1_rais_mean', 'attn1_rais_std',
                      'attn2_rais_mean', 'attn2_rais_std', 'overall_rais_mean', 'overall_rais_std',
                      'shallow_rais_mean', 'middle_rais_mean', 'deep_rais_mean', 'rsd_mean', 'rsd_std']

    layer_csv = open(per_layer_file, 'w', newline='')
    layer_writer = csv.DictWriter(layer_csv, fieldnames=layer_fields)
    layer_writer.writeheader()

    object_csv = open(per_object_file, 'w', newline='')
    object_writer = csv.DictWriter(object_csv, fieldnames=object_fields)
    object_writer.writeheader()

    all_object_results = []

    for obj_idx, obj_id in enumerate(test_objects):
        print(f"\n{'='*60}")
        print(f"Processing object {obj_idx+1}/{len(test_objects)}: {obj_id}")
        print(f"{'='*60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        if not os.path.exists(obj_path):
            print(f"  Skipping: path not found")
            continue

        cond_path = os.path.join(obj_path, 'image', '000.png')
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: could not create grids")
            continue

        # === Run Original ===
        print("  Running Original...")
        pipeline = load_pipeline()
        reload_base_weights(pipeline)
        _, captured_orig = run_inference_and_capture(
            pipeline, cond_img, normal_grid, depth_grid, seed=SEED, num_steps=NUM_INFERENCE_STEPS
        )
        print(f"    Captured {len(captured_orig)} layers")
        del pipeline
        clear_gpu()

        # === Run each LoRA method ===
        for method_name, method_config in METHODS.items():
            print(f"  Running {method_name}...")
            pipeline = load_pipeline()
            reload_base_weights(pipeline)
            bare_unet = get_bare_unet(pipeline)
            method_config['merge_fn'](bare_unet, method_config['lora_path'],
                                       rank=method_config['rank'], alpha=method_config['alpha'])
            _, captured_method = run_inference_and_capture(
                pipeline, cond_img, normal_grid, depth_grid, seed=SEED, num_steps=NUM_INFERENCE_STEPS
            )
            print(f"    Captured {len(captured_method)} layers")
            del pipeline
            clear_gpu()

            # Compute per-layer RAIS
            common_layers = sorted(set(captured_orig.keys()) & set(captured_method.keys()))
            attn1_raises = []
            attn2_raises = []
            depth_raises = {'shallow': [], 'middle': [], 'deep': []}

            for layer_name in common_layers:
                if layer_name not in captured_orig or layer_name not in captured_method:
                    continue

                rais = compute_per_token_cosine(captured_orig[layer_name], captured_method[layer_name])
                layer_type, depth = get_layer_info(layer_name)

                # Write per-layer CSV
                layer_writer.writerow({
                    'object_id': obj_id,
                    'method': method_name,
                    'layer_name': layer_name,
                    'layer_type': layer_type,
                    'depth': depth,
                    'rais': rais,
                })

                if layer_type == 'attn1':
                    attn1_raises.append(rais)
                else:
                    attn2_raises.append(rais)

                if depth in depth_raises:
                    depth_raises[depth].append(rais)

            # Compute per-object aggregates
            attn1_rais = np.mean(attn1_raises) if attn1_raises else float('nan')
            attn2_rais = np.mean(attn2_raises) if attn2_raises else float('nan')
            overall_rais = np.mean(attn1_raises + attn2_raises) if (attn1_raises + attn2_raises) else float('nan')
            shallow_rais = np.mean(depth_raises['shallow']) if depth_raises['shallow'] else float('nan')
            middle_rais = np.mean(depth_raises['middle']) if depth_raises['middle'] else float('nan')
            deep_rais = np.mean(depth_raises['deep']) if depth_raises['deep'] else float('nan')
            rsd = 1.0 - overall_rais if not np.isnan(overall_rais) else float('nan')

            obj_result = {
                'object_id': obj_id,
                'method': method_name,
                'attn1_rais': attn1_rais,
                'attn2_rais': attn2_rais,
                'overall_rais': overall_rais,
                'shallow_rais': shallow_rais,
                'middle_rais': middle_rais,
                'deep_rais': deep_rais,
                'rsd': rsd,
            }
            object_writer.writerow(obj_result)
            all_object_results.append(obj_result)

            print(f"    attn1 RAIS: {attn1_rais:.4f}, attn2 RAIS: {attn2_rais:.4f}, "
                  f"Overall: {overall_rais:.4f}, RSD: {rsd:.4f}")

            # Free captured features
            del captured_method

        # Free original features
        del captured_orig
        clear_gpu()

    # Close CSV files
    layer_csv.close()
    object_csv.close()

    # === Generate summary ===
    print(f"\n{'='*60}")
    print("Generating summary...")
    print(f"{'='*60}")

    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_object_results:
        groups[r['method']].append(r)

    with open(summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()

        for method, records in sorted(groups.items()):
            n = len(records)
            summary = {
                'method': method,
                'N_objects': n,
                'attn1_rais_mean': np.mean([r['attn1_rais'] for r in records]),
                'attn1_rais_std': np.std([r['attn1_rais'] for r in records]),
                'attn2_rais_mean': np.mean([r['attn2_rais'] for r in records]),
                'attn2_rais_std': np.std([r['attn2_rais'] for r in records]),
                'overall_rais_mean': np.mean([r['overall_rais'] for r in records]),
                'overall_rais_std': np.std([r['overall_rais'] for r in records]),
                'shallow_rais_mean': np.mean([r['shallow_rais'] for r in records if not np.isnan(r['shallow_rais'])]),
                'middle_rais_mean': np.mean([r['middle_rais'] for r in records if not np.isnan(r['middle_rais'])]),
                'deep_rais_mean': np.mean([r['deep_rais'] for r in records if not np.isnan(r['deep_rais'])]),
                'rsd_mean': np.mean([r['rsd'] for r in records]),
                'rsd_std': np.std([r['rsd'] for r in records]),
            }
            writer.writerow(summary)

            print(f"\n{method} (N={n}):")
            print(f"  attn1 RAIS: {summary['attn1_rais_mean']:.4f} ± {summary['attn1_rais_std']:.4f}")
            print(f"  attn2 RAIS: {summary['attn2_rais_mean']:.4f} ± {summary['attn2_rais_std']:.4f}")
            print(f"  Overall RAIS: {summary['overall_rais_mean']:.4f} ± {summary['overall_rais_std']:.4f}")
            print(f"  Shallow: {summary['shallow_rais_mean']:.4f}, Middle: {summary['middle_rais_mean']:.4f}, Deep: {summary['deep_rais_mean']:.4f}")
            print(f"  RSD: {summary['rsd_mean']:.4f} ± {summary['rsd_std']:.4f}")

    # === Generate plots ===
    print(f"\n{'='*60}")
    print("Generating plots...")
    print(f"{'='*60}")

    generate_plots(all_object_results, OUTPUT_DIR)

    # === Generate report ===
    print("Generating report...")
    generate_report(all_object_results, OUTPUT_DIR)

    print(f"\n{'='*60}")
    print("Hook analysis complete!")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*60}")


def generate_plots(all_results, output_dir):
    """Generate layer-wise and depth-wise plots."""
    from collections import defaultdict

    # Group by method
    groups = defaultdict(list)
    for r in all_results:
        groups[r['method']].append(r)

    # === Depth-wise bar chart ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    methods = sorted(groups.keys())
    x = np.arange(len(methods))
    width = 0.25

    # attn1 RAIS
    ax = axes[0]
    means = [np.mean([r['attn1_rais'] for r in groups[m]]) for m in methods]
    stds = [np.std([r['attn1_rais'] for r in groups[m]]) for m in methods]
    ax.bar(x, means, width, yerr=stds, capsize=3, color='#FF5722', alpha=0.8)
    ax.set_ylabel('RAIS')
    ax.set_title('attn1 RAIS', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', '\n') for m in methods], fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    # attn2 RAIS
    ax = axes[1]
    means = [np.mean([r['attn2_rais'] for r in groups[m]]) for m in methods]
    stds = [np.std([r['attn2_rais'] for r in groups[m]]) for m in methods]
    ax.bar(x, means, width, yerr=stds, capsize=3, color='#4CAF50', alpha=0.8)
    ax.set_ylabel('RAIS')
    ax.set_title('attn2 RAIS', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', '\n') for m in methods], fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    # Overall RAIS
    ax = axes[2]
    means = [np.mean([r['overall_rais'] for r in groups[m]]) for m in methods]
    stds = [np.std([r['overall_rais'] for r in groups[m]]) for m in methods]
    ax.bar(x, means, width, yerr=stds, capsize=3, color='#2196F3', alpha=0.8)
    ax.set_ylabel('RAIS')
    ax.set_title('Overall RAIS', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', '\n') for m in methods], fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    plt.suptitle('RAIS by Method and Layer Type (Correct Pipeline)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'plots', 'rais_by_method.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # === Depth-wise comparison ===
    fig, ax = plt.subplots(figsize=(10, 6))

    depths = ['shallow', 'middle', 'deep']
    x = np.arange(len(depths))
    width = 0.2

    colors = ['#FF5722', '#FF9800', '#4CAF50', '#8BC34A']
    for i, method in enumerate(methods):
        means = []
        for d in depths:
            vals = [r[f'{d}_rais'] for r in groups[method] if not np.isnan(r.get(f'{d}_rais', float('nan')))]
            means.append(np.mean(vals) if vals else 0)
        ax.bar(x + i * width, means, width, label=method, color=colors[i % len(colors)], alpha=0.8)

    ax.set_ylabel('RAIS')
    ax.set_title('Depth-wise RAIS by Method', fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(depths)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'plots', 'depth_wise_rais.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # === Per-object heatmap for attn1 RAIS ===
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for idx, method in enumerate(methods[:4]):
        ax = axes[idx // 2][idx % 2]
        obj_ids = [r['object_id'][:8] for r in groups[method]]
        attn1_vals = [r['attn1_rais'] for r in groups[method]]
        attn2_vals = [r['attn2_rais'] for r in groups[method]]

        x_pos = np.arange(len(obj_ids))
        ax.bar(x_pos - 0.2, attn1_vals, 0.4, label='attn1', color='#FF5722', alpha=0.8)
        ax.bar(x_pos + 0.2, attn2_vals, 0.4, label='attn2', color='#4CAF50', alpha=0.8)
        ax.set_title(method, fontsize=10, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(obj_ids, rotation=45, fontsize=7)
        ax.set_ylim(0, 1.1)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Per-Object attn1/attn2 RAIS', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'plots', 'per_object_rais.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    print("  Plots saved to plots/")


def generate_report(all_results, output_dir):
    """Generate markdown report."""
    from collections import defaultdict

    groups = defaultdict(list)
    for r in all_results:
        groups[r['method']].append(r)

    report_path = os.path.join(output_dir, 'report.md')
    with open(report_path, 'w') as f:
        f.write("# Hook Analysis v2: RAIS/RSD under Correct Pipeline\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Configuration\n\n")
        f.write(f"- Seed: {SEED}\n")
        f.write(f"- Num inference steps: {NUM_INFERENCE_STEPS}\n")
        f.write(f"- Device: {DEVICE}\n")
        f.write(f"- Full LoRA: `{FULL_LORA_PATH}`\n")
        f.write(f"- attn2-only LoRA: `{ATTN2_LORA_PATH}`\n\n")

        f.write("## Summary\n\n")
        f.write("| Method | N | attn1 RAIS | attn2 RAIS | Overall RAIS | RSD |\n")
        f.write("|--------|---|------------|------------|--------------|-----|\n")

        for method, records in sorted(groups.items()):
            n = len(records)
            attn1 = np.mean([r['attn1_rais'] for r in records])
            attn2 = np.mean([r['attn2_rais'] for r in records])
            overall = np.mean([r['overall_rais'] for r in records])
            rsd = np.mean([r['rsd'] for r in records])
            f.write(f"| {method} | {n} | {attn1:.4f} | {attn2:.4f} | {overall:.4f} | {rsd:.4f} |\n")

        f.write("\n## Depth-wise RAIS\n\n")
        f.write("| Method | Shallow | Middle | Deep |\n")
        f.write("|--------|---------|--------|------|\n")

        for method, records in sorted(groups.items()):
            shallow = np.mean([r['shallow_rais'] for r in records if not np.isnan(r['shallow_rais'])])
            middle = np.mean([r['middle_rais'] for r in records if not np.isnan(r['middle_rais'])])
            deep = np.mean([r['deep_rais'] for r in records if not np.isnan(r['deep_rais'])])
            f.write(f"| {method} | {shallow:.4f} | {middle:.4f} | {deep:.4f} |\n")

        f.write("\n## Key Findings\n\n")

        # Compare full_lora vs attn2_only at s=1.0
        if 'full_lora_s1.0' in groups and 'attn2_only_s1.0' in groups:
            full_attn1 = np.mean([r['attn1_rais'] for r in groups['full_lora_s1.0']])
            attn2_attn1 = np.mean([r['attn1_rais'] for r in groups['attn2_only_s1.0']])
            full_overall = np.mean([r['overall_rais'] for r in groups['full_lora_s1.0']])
            attn2_overall = np.mean([r['overall_rais'] for r in groups['attn2_only_s1.0']])

            f.write(f"### Full LoRA vs attn2-only (scale=1.0)\n\n")
            f.write(f"- Full LoRA attn1 RAIS: {full_attn1:.4f}\n")
            f.write(f"- attn2-only attn1 RAIS: {attn2_attn1:.4f}\n")
            f.write(f"- Delta (attn2-only - Full): {attn2_attn1 - full_attn1:+.4f}\n\n")
            f.write(f"- Full LoRA Overall RAIS: {full_overall:.4f}\n")
            f.write(f"- attn2-only Overall RAIS: {attn2_overall:.4f}\n")
            f.write(f"- Delta: {attn2_overall - full_overall:+.4f}\n\n")

            # Check against expected values
            f.write("### Comparison with Previous Results\n\n")
            f.write("Previous bare-pipeline results:\n")
            f.write("- Full LoRA attn1 RAIS ≈ 0.5578\n")
            f.write("- attn2-only attn1 RAIS ≈ 0.9492\n")
            f.write("- Full LoRA Overall RAIS ≈ 0.7310\n")
            f.write("- attn2-only Overall RAIS ≈ 0.9684\n\n")

            f.write(f"Current correct-pipeline results:\n")
            f.write(f"- Full LoRA attn1 RAIS: {full_attn1:.4f}\n")
            f.write(f"- attn2-only attn1 RAIS: {attn2_attn1:.4f}\n")
            f.write(f"- Full LoRA Overall RAIS: {full_overall:.4f}\n")
            f.write(f"- attn2-only Overall RAIS: {attn2_overall:.4f}\n\n")

    print(f"  Report saved to {report_path}")


if __name__ == '__main__':
    main()
