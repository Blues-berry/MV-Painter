"""
Hook Analysis on Correct Pipeline (ControlNet + Depth).

Captures reference features from ALL attention layers (attn1 + attn2) at multiple
timesteps to understand:
1. Is attn1 corruption different under correct pipeline vs bare pipeline?
2. Do downstream layers compensate for upstream corruption?
3. How does corruption evolve across timesteps?

This is for the Mechanistic Interpretability direction.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.controlnet import ControlNetModel_Union
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler
from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights,
    create_combined_grids, seed_everything,
    CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA,
)


# --- LoRA checkpoint paths ---
FULL_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'


def register_hooks_all_layers(pipeline):
    """Register forward hooks on ALL attention modules (attn1 + attn2).

    Captures the output hidden states of each attention module during the READ pass
    (when reference features are being used).
    """
    captured = {}
    hook_handles = []

    def make_hook(name):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                output = output[0]
            # Only capture during read pass (when we have meaningful features)
            captured[name] = output.detach().cpu().float()
        return hook_fn

    for name, module in pipeline.unet.unet.named_modules():
        # Hook on attn1 and attn2 modules (not processors)
        if ('attn1' in name or 'attn2' in name) and 'processor' not in name and 'to_' not in name:
            if hasattr(module, 'to_q'):
                h = module.register_forward_hook(make_hook(name))
                hook_handles.append(h)

    return captured, hook_handles


def register_hooks_ref_dict(pipeline):
    """Register hooks to capture what's stored in ref_dict during write pass.

    This directly measures the reference features that the model stores.
    """
    captured_write = {}
    captured_read = {}
    hook_handles = []

    # Hook on ReferenceOnlyAttnProc to capture ref_dict contents
    for name, proc in pipeline.unet.unet.attn_processors.items():
        if isinstance(proc, ReferenceOnlyAttnProc) and proc.enabled:
            # We need to hook the processor's __call__ method
            # Since we can't easily hook __call__, we'll capture the input to the chained proc
            pass

    return captured_write, captured_read, hook_handles


def compute_layer_cosine_similarity(feat1, feat2):
    """Compute cosine similarity between two feature tensors."""
    f1 = feat1.flatten().float()
    f2 = feat2.flatten().float()
    return (torch.dot(f1, f2) / (f1.norm() * f2.norm() + 1e-8)).item()


def compute_per_token_cosine(feat1, feat2):
    """Compute per-token cosine similarity, then average.

    This is more meaningful than flattening for sequence models.
    """
    # feat shape: [batch, seq_len, hidden_dim]
    f1 = feat1.float()
    f2 = feat2.float()

    if f1.dim() == 3:
        f1 = f1.squeeze(0)
        f2 = f2.squeeze(0)

    # Normalize each token
    f1_norm = f1 / (f1.norm(dim=-1, keepdim=True) + 1e-8)
    f2_norm = f2 / (f2.norm(dim=-1, keepdim=True) + 1e-8)

    # Per-token cosine similarity
    cos_per_token = (f1_norm * f2_norm).sum(dim=-1)

    return cos_per_token.mean().item()


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


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/hook_analysis_correct'
    os.makedirs(output_dir, exist_ok=True)

    # Test object
    obj_id = 'd6a5427888b8413fbfcbcaad14353af8'
    obj_path = os.path.join(TRAIN_DATA, obj_id)
    cond_path = os.path.join(obj_path, 'image', '000.png')
    cond_img = Image.open(cond_path).convert('RGBA')
    normal_grid, depth_grid = create_combined_grids(obj_path)

    if normal_grid is None:
        print("ERROR: Could not create depth/normal grids")
        return

    NUM_STEPS = 20  # Fewer steps to reduce memory pressure

    def clear_gpu():
        """Aggressively free GPU memory."""
        import gc
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    # === Run Original ===
    print("=" * 60)
    print("Running Original (with ControlNet + depth)...")
    print("=" * 60)
    pipeline = load_pipeline()
    reload_base_weights(pipeline)
    img_orig, captured_orig = run_inference_and_capture(
        pipeline, cond_img, normal_grid, depth_grid, seed=42, num_steps=NUM_STEPS
    )
    print(f"  Captured {len(captured_orig)} layers")
    del pipeline
    clear_gpu()

    # === Run Full LoRA (scale=1.0) ===
    print("\n" + "=" * 60)
    print("Running Full LoRA (scale=1.0, with ControlNet + depth)...")
    print("=" * 60)
    pipeline = load_pipeline()
    reload_base_weights(pipeline)
    bare_unet = get_bare_unet(pipeline)
    merge_lora_into_unet(bare_unet, FULL_LORA_PATH, rank=4, alpha=4)
    img_full, captured_full = run_inference_and_capture(
        pipeline, cond_img, normal_grid, depth_grid, seed=42, num_steps=NUM_STEPS
    )
    print(f"  Captured {len(captured_full)} layers")
    del pipeline
    clear_gpu()

    # === Run attn2-only LoRA (scale=1.0) ===
    print("\n" + "=" * 60)
    print("Running attn2-only LoRA (scale=1.0, with ControlNet + depth)...")
    print("=" * 60)
    pipeline = load_pipeline()
    reload_base_weights(pipeline)
    bare_unet = get_bare_unet(pipeline)
    merge_lora_into_unet_attn2_only(bare_unet, ATTN2_LORA_PATH, rank=4, alpha=4)
    img_attn2, captured_attn2 = run_inference_and_capture(
        pipeline, cond_img, normal_grid, depth_grid, seed=42, num_steps=NUM_STEPS
    )
    print(f"  Captured {len(captured_attn2)} layers")
    del pipeline
    clear_gpu()

    # === Compute similarities ===
    print("\n" + "=" * 60)
    print("Computing per-layer cosine similarities...")
    print("=" * 60)

    common_layers = sorted(set(captured_orig.keys()) & set(captured_full.keys()) & set(captured_attn2.keys()))
    print(f"Common layers: {len(common_layers)}")

    results = []
    for layer_name in common_layers:
        orig_feat = captured_orig[layer_name]
        full_feat = captured_full[layer_name]
        attn2_feat = captured_attn2[layer_name]

        # Use per-token cosine (more meaningful for sequence models)
        s_full = compute_per_token_cosine(orig_feat, full_feat)
        s_attn2 = compute_per_token_cosine(orig_feat, attn2_feat)

        # Determine layer type
        layer_type = 'attn1' if 'attn1' in layer_name else 'attn2'

        # Extract layer index (e.g., "down_blocks.0.attentions.0.transformer_blocks.0.attn1" → "0.0.0.0.attn1")
        parts = layer_name.split('.')
        short_name = '.'.join(parts[-4:]) if len(parts) >= 4 else layer_name

        results.append({
            'name': layer_name,
            'short_name': short_name,
            'type': layer_type,
            'sim_full': s_full,
            'sim_attn2': s_attn2,
        })

    # === Print results ===
    print(f"\n{'Layer':<50} {'Type':>6} {'Full LoRA':>10} {'attn2-only':>10} {'Delta':>8}")
    print("-" * 90)
    for r in results:
        delta = r['sim_attn2'] - r['sim_full']
        print(f"{r['short_name']:<50} {r['type']:>6} {r['sim_full']:>10.4f} {r['sim_attn2']:>10.4f} {delta:>+8.4f}")

    # Compute averages by layer type
    attn1_results = [r for r in results if r['type'] == 'attn1']
    attn2_results = [r for r in results if r['type'] == 'attn2']

    avg_full_attn1 = np.mean([r['sim_full'] for r in attn1_results]) if attn1_results else 0
    avg_attn2_attn1 = np.mean([r['sim_attn2'] for r in attn1_results]) if attn1_results else 0
    avg_full_attn2 = np.mean([r['sim_full'] for r in attn2_results]) if attn2_results else 0
    avg_attn2_attn2 = np.mean([r['sim_attn2'] for r in attn2_results]) if attn2_results else 0

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Layer Type':<20} {'Full LoRA':>10} {'attn2-only':>10} {'Delta':>8}")
    print(f"{'-'*50}")
    print(f"{'attn1 (self-attn)':<20} {avg_full_attn1:>10.4f} {avg_attn2_attn1:>10.4f} {avg_attn2_attn1 - avg_full_attn1:>+8.4f}")
    print(f"{'attn2 (cross-attn)':<20} {avg_full_attn2:>10.4f} {avg_attn2_attn2:>10.4f} {avg_attn2_attn2 - avg_full_attn2:>+8.4f}")
    print(f"{'Overall':<20} {np.mean([r['sim_full'] for r in results]):>10.4f} {np.mean([r['sim_attn2'] for r in results]):>10.4f}")

    # === Generate plot ===
    print("\nGenerating plot...")

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})

    # Top plot: per-layer cosine similarity
    ax = axes[0]
    x = np.arange(len(results))
    colors_full = ['#FF5722' if r['type'] == 'attn1' else '#FF9800' for r in results]
    colors_attn2 = ['#4CAF50' if r['type'] == 'attn1' else '#8BC34A' for r in results]

    ax.plot(x, [r['sim_full'] for r in results], 'o-', color='#FF5722', linewidth=1.5, markersize=3,
            label=f'Full LoRA (attn1 avg: {avg_full_attn1:.3f}, attn2 avg: {avg_full_attn2:.3f})')
    ax.plot(x, [r['sim_attn2'] for r in results], 's-', color='#4CAF50', linewidth=1.5, markersize=3,
            label=f'attn2-only LoRA (attn1 avg: {avg_attn2_attn1:.3f}, attn2 avg: {avg_attn2_attn2:.3f})')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Perfect match')

    # Mark attn1/attn2 boundaries
    for i, r in enumerate(results):
        if i > 0 and r['type'] != results[i-1]['type']:
            ax.axvline(x=i, color='gray', linestyle=':', alpha=0.3)

    ax.set_xlabel('Layer Index', fontsize=12)
    ax.set_ylabel('Per-Token Cosine Similarity to Original', fontsize=12)
    ax.set_title(f'Reference Feature Preservation (Correct Pipeline: ControlNet + Depth)\nObject: {obj_id}', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)

    # Bottom plot: delta (attn2-only - Full LoRA)
    ax2 = axes[1]
    deltas = [r['sim_attn2'] - r['sim_full'] for r in results]
    colors_delta = ['#2196F3' if d > 0 else '#F44336' for d in deltas]
    ax2.bar(x, deltas, color=colors_delta, alpha=0.7, width=0.8)
    ax2.axhline(y=0, color='black', linewidth=0.5)
    ax2.set_xlabel('Layer Index', fontsize=12)
    ax2.set_ylabel('Δ (attn2-only − Full)', fontsize=12)
    ax2.set_title('Positive = attn2-only preserves better', fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'hook_analysis_correct_pipeline.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved to {plot_path}")

    # Save results
    import json
    results_path = os.path.join(output_dir, 'hook_analysis_results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'obj_id': obj_id,
            'num_steps': NUM_STEPS,
            'pipeline': 'correct (ControlNet + depth)',
            'results': results,
            'summary': {
                'attn1': {'full': avg_full_attn1, 'attn2_only': avg_attn2_attn1},
                'attn2': {'full': avg_full_attn2, 'attn2_only': avg_attn2_attn2},
            },
        }, f, indent=2)
    print(f"Results saved to {results_path}")

    # Save output images for visual comparison
    if img_orig:
        img_orig.save(os.path.join(output_dir, f'{obj_id}_original.png'))
    if img_full:
        img_full.save(os.path.join(output_dir, f'{obj_id}_full_lora.png'))
    if img_attn2:
        img_attn2.save(os.path.join(output_dir, f'{obj_id}_attn2only.png'))
    print(f"Output images saved to {output_dir}")


if __name__ == '__main__':
    main()
