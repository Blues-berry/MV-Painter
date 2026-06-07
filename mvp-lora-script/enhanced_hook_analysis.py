"""
Enhanced Hook Analysis for RP-LoRA Paper.
Computes:
1. Feature Drift: D_l = ||h_l^LoRA - h_l^Base||_2
2. Attention Entropy: H = -sum(p * log(p)) for attention distributions
3. Cosine Similarity: existing metric

Usage: python enhanced_hook_analysis.py --output_dir <output_dir>
"""
import argparse
import os
import sys
import json
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')

from diffusers import EulerAncestralDiscreteScheduler, UNet2DConditionModel
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.lora_utils import create_lora_processors
from mvpainter.lora_utils_attn2 import create_lora_processors_attn2_only
from torchvision.transforms import v2
from einops import rearrange
from safetensors.torch import load_file


class FeatureHookManager:
    """Manages forward hooks to capture intermediate features."""

    def __init__(self):
        self.hooks = []
        self.features = {}

    def register_hooks(self, unet, prefix=''):
        """Register hooks on all attn1 layers."""
        for name, module in unet.named_modules():
            if 'attn1' in name and 'processor' not in name and 'to_q' not in name and 'to_k' not in name and 'to_v' not in name:
                if hasattr(module, 'forward'):
                    hook_name = f'{prefix}{name}'
                    hook = module.register_forward_hook(self._make_hook(hook_name))
                    self.hooks.append(hook)

    def _make_hook(self, name):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                self.features[name] = output[0].detach().cpu()
            else:
                self.features[name] = output.detach().cpu()
        return hook_fn

    def clear(self):
        self.features = {}

    def remove_hooks(self):
        for hook in self.hooks:
            hook.remove()
        self.hooks = []


def compute_feature_drift(base_features, lora_features):
    """Compute L2 distance between base and LoRA features."""
    drifts = {}
    for name in base_features:
        if name in lora_features:
            base = base_features[name].float()
            lora = lora_features[name].float()
            drift = torch.norm(base - lora, p=2).item()
            drifts[name] = drift
    return drifts


def compute_cosine_similarity(base_features, lora_features):
    """Compute cosine similarity between base and LoRA features."""
    similarities = {}
    for name in base_features:
        if name in lora_features:
            base = base_features[name].float().flatten()
            lora = lora_features[name].float().flatten()
            cos_sim = torch.nn.functional.cosine_similarity(base.unsqueeze(0), lora.unsqueeze(0)).item()
            similarities[name] = cos_sim
    return similarities


def compute_attention_entropy(attention_weights):
    """Compute entropy of attention distribution."""
    if attention_weights is None:
        return None
    # attention_weights: [batch, heads, seq_len, seq_len]
    eps = 1e-10
    entropy = -torch.sum(attention_weights * torch.log(attention_weights + eps), dim=-1)
    return entropy.mean().item()


def load_pipeline_with_lora(lora_type='full', lora_path=None, device='cuda:0'):
    """Load pipeline with different LoRA configurations."""
    pipeline = MVPainter_Pipeline.from_pretrained(
        '/4T/CXY/MV-Painter/checkpoints/hf_repo',
        use_safetensors=True,
    ).to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    if lora_type == 'full':
        processors = create_lora_processors(pipeline.unet, rank=4, network_alpha=4)
        pipeline.unet.set_attn_processor(processors)
        if lora_path:
            lora_state = load_file(lora_path)
            _apply_lora_weights(pipeline.unet, lora_state, 'full')
    elif lora_type == 'attn2':
        processors = create_lora_processors_attn2_only(pipeline.unet, rank=4, network_alpha=4)
        pipeline.unet.set_attn_processor(processors)
        if lora_path:
            lora_state = load_file(lora_path)
            _apply_lora_weights(pipeline.unet, lora_state, 'attn2')
    # 'original' = no LoRA

    return pipeline


def _apply_lora_weights(unet, lora_state, lora_type):
    """Apply LoRA weights to the appropriate processors."""
    for name, proc in unet.attn_processors.items():
        if not isinstance(proc, ReferenceOnlyAttnProc):
            continue
        lora_proc = proc.chained_proc
        if not hasattr(lora_proc, 'to_q_lora'):
            continue

        prefix = name.replace('.processor', '').replace('.', '_')
        for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
            if hasattr(lora_proc, param_name):
                lora_layer = getattr(lora_proc, param_name)
                down_key = f'{prefix}_{param_name}_down'
                up_key = f'{prefix}_{param_name}_up'
                if down_key in lora_state and up_key in lora_state:
                    lora_layer.down.weight.data = lora_state[down_key]
                    lora_layer.up.weight.data = lora_state[up_key]


def extract_attention_features(pipeline, cond_image, hook_manager, device='cuda:0'):
    """Extract features from attention layers during inference."""
    hook_manager.clear()

    if isinstance(cond_image, str):
        cond_image = Image.open(cond_image).convert('RGB')

    # Run inference to capture features
    with torch.no_grad():
        output = pipeline(cond_image, num_inference_steps=25, output_type='latent')

    return hook_manager.features


def plot_feature_drift(drifts_full, drifts_attn2, output_path):
    """Plot feature drift across layers."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    # Extract layer indices
    layers_full = sorted(drifts_full.keys(), key=lambda x: int(x.split('.')[-1]) if x.split('.')[-1].isdigit() else 0)
    layers_attn2 = sorted(drifts_attn2.keys(), key=lambda x: int(x.split('.')[-1]) if x.split('.')[-1].isdigit() else 0)

    # Use numeric indices
    indices_full = list(range(len(layers_full)))
    indices_attn2 = list(range(len(layers_attn2)))

    values_full = [drifts_full[l] for l in layers_full]
    values_attn2 = [drifts_attn2[l] for l in layers_attn2]

    ax.plot(indices_full, values_full, 'r-o', label='Full LoRA', markersize=4, linewidth=2)
    ax.plot(indices_attn2, values_attn2, 'b-s', label='RP-LoRA (attn2-only)', markersize=4, linewidth=2)

    ax.set_xlabel('Layer Depth', fontsize=14)
    ax.set_ylabel('Feature Drift (L2 Norm)', fontsize=14)
    ax.set_title('Feature Drift Across Self-Attention Layers', fontsize=16)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved feature drift plot to {output_path}")


def plot_cosine_similarity(sims_full, sims_attn2, output_path):
    """Plot cosine similarity across layers."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    layers_full = sorted(sims_full.keys(), key=lambda x: int(x.split('.')[-1]) if x.split('.')[-1].isdigit() else 0)
    layers_attn2 = sorted(sims_attn2.keys(), key=lambda x: int(x.split('.')[-1]) if x.split('.')[-1].isdigit() else 0)

    indices_full = list(range(len(layers_full)))
    indices_attn2 = list(range(len(layers_attn2)))

    values_full = [sims_full[l] for l in layers_full]
    values_attn2 = [sims_attn2[l] for l in layers_attn2]

    ax.plot(indices_full, values_full, 'r-o', label='Full LoRA', markersize=4, linewidth=2)
    ax.plot(indices_attn2, values_attn2, 'b-s', label='RP-LoRA (attn2-only)', markersize=4, linewidth=2)

    ax.set_xlabel('Layer Depth', fontsize=14)
    ax.set_ylabel('Cosine Similarity', fontsize=14)
    ax.set_title('Reference Feature Cosine Similarity Across Layers', fontsize=16)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved cosine similarity plot to {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full_lora_path', type=str, default=None)
    parser.add_argument('--attn2_lora_path', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default='/4T/CXY/MV-Painter/mvpoutput/enhanced_hook_analysis')
    parser.add_argument('--cond_image', type=str, default=None)
    parser.add_argument('--num_samples', type=int, default=5)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = 'cuda:0'

    # Default condition image
    if args.cond_image is None:
        test_dir = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
        test_objects = os.listdir(test_dir)[:args.num_samples]
        cond_images = []
        for obj in test_objects:
            img_path = os.path.join(test_dir, obj, 'cond_image.png')
            if os.path.exists(img_path):
                cond_images.append(img_path)
    else:
        cond_images = [args.cond_image]

    print(f"Analyzing {len(cond_images)} condition images")

    # Load pipelines
    print("Loading Original pipeline...")
    pipeline_orig = load_pipeline_with_lora('original', device=device)

    print("Loading Full LoRA pipeline...")
    pipeline_full = load_pipeline_with_lora('full', args.full_lora_path, device)

    print("Loading RP-LoRA pipeline...")
    pipeline_attn2 = load_pipeline_with_lora('attn2', args.attn2_lora_path, device)

    # Initialize hook managers
    hooks_full = FeatureHookManager()
    hooks_attn2 = FeatureHookManager()

    # Register hooks
    hooks_full.register_hooks(pipeline_full.unet, prefix='full_')
    hooks_attn2.register_hooks(pipeline_attn2.unet, prefix='attn2_')

    # Collect features across samples
    all_drifts_full = {}
    all_drifts_attn2 = {}
    all_sims_full = {}
    all_sims_attn2 = {}

    for img_path in tqdm(cond_images, desc="Processing"):
        # Extract features from original (reference)
        hooks_orig = FeatureHookManager()
        hooks_orig.register_hooks(pipeline_orig.unet, prefix='orig_')
        orig_features = extract_attention_features(pipeline_orig, img_path, hooks_orig, device)
        hooks_orig.remove_hooks()

        # Extract features from Full LoRA
        full_features = extract_attention_features(pipeline_full, img_path, hooks_full, device)

        # Extract features from RP-LoRA
        attn2_features = extract_attention_features(pipeline_attn2, img_path, hooks_attn2, device)

        # Compute drifts
        drifts_full = compute_feature_drift(orig_features, full_features)
        drifts_attn2 = compute_feature_drift(orig_features, attn2_features)

        # Compute similarities
        sims_full = compute_cosine_similarity(orig_features, full_features)
        sims_attn2 = compute_cosine_similarity(orig_features, attn2_features)

        # Accumulate
        for k, v in drifts_full.items():
            all_drifts_full.setdefault(k, []).append(v)
        for k, v in drifts_attn2.items():
            all_drifts_attn2.setdefault(k, []).append(v)
        for k, v in sims_full.items():
            all_sims_full.setdefault(k, []).append(v)
        for k, v in sims_attn2.items():
            all_sims_attn2.setdefault(k, []).append(v)

    # Average across samples
    avg_drifts_full = {k: np.mean(v) for k, v in all_drifts_full.items()}
    avg_drifts_attn2 = {k: np.mean(v) for k, v in all_drifts_attn2.items()}
    avg_sims_full = {k: np.mean(v) for k, v in all_sims_full.items()}
    avg_sims_attn2 = {k: np.mean(v) for k, v in all_sims_attn2.items()}

    # Generate plots
    plot_feature_drift(avg_drifts_full, avg_drifts_attn2,
                       os.path.join(args.output_dir, 'feature_drift.png'))
    plot_cosine_similarity(avg_sims_full, avg_sims_attn2,
                           os.path.join(args.output_dir, 'cosine_similarity.png'))

    # Save numerical results
    results = {
        'avg_drift_full': {k: float(v) for k, v in avg_drifts_full.items()},
        'avg_drift_attn2': {k: float(v) for k, v in avg_drifts_attn2.items()},
        'avg_cosine_full': {k: float(v) for k, v in avg_sims_full.items()},
        'avg_cosine_attn2': {k: float(v) for k, v in avg_sims_attn2.items()},
        'summary': {
            'mean_drift_full': float(np.mean(list(avg_drifts_full.values()))) if avg_drifts_full else 0,
            'mean_drift_attn2': float(np.mean(list(avg_drifts_attn2.values()))) if avg_drifts_attn2 else 0,
            'mean_cosine_full': float(np.mean(list(avg_sims_full.values()))) if avg_sims_full else 1,
            'mean_cosine_attn2': float(np.mean(list(avg_sims_attn2.values()))) if avg_sims_attn2 else 1,
        }
    }

    with open(os.path.join(args.output_dir, 'hook_analysis_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # Clean up
    hooks_full.remove_hooks()
    hooks_attn2.remove_hooks()

    print(f"\n=== Enhanced Hook Analysis Summary ===")
    print(f"Mean Feature Drift (Full LoRA): {results['summary']['mean_drift_full']:.4f}")
    print(f"Mean Feature Drift (RP-LoRA):   {results['summary']['mean_drift_attn2']:.4f}")
    print(f"Mean Cosine Sim (Full LoRA):    {results['summary']['mean_cosine_full']:.4f}")
    print(f"Mean Cosine Sim (RP-LoRA):      {results['summary']['mean_cosine_attn2']:.4f}")
    print(f"\nResults saved to {args.output_dir}")


if __name__ == '__main__':
    main()
