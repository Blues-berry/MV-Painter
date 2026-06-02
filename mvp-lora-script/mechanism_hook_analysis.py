"""
Mechanism Hook Analysis: Capture reference features from attn1 layers
and compare across Original / Full LoRA / attn2-only LoRA.
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
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler


def load_pipeline(checkpoint_path, unet_ckpt_path, device='cuda'):
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path, torch_dtype=torch.float16, use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    if os.path.exists(unet_ckpt_path):
        ckpt = load_file(unet_ckpt_path)
        unet_state = {k[len('unet.unet.'):]: v for k, v in ckpt.items() if k.startswith('unet.unet.')}
        if unet_state:
            pipeline.unet.load_state_dict(unet_state, strict=False)
    return pipeline.to(device)


def register_hooks(pipeline):
    """Register forward hooks on attn1 layers to capture reference features."""
    captured = {}

    def make_hook(name):
        def hook_fn(module, input, output):
            # output is the hidden states after attention
            if isinstance(output, tuple):
                output = output[0]
            captured[name] = output.detach().cpu()
        return hook_fn

    hooks = []
    for name, module in pipeline.unet.named_modules():
        if 'attn1' in name and 'processor' not in name and 'to_' not in name:
            # Register hook on the attention module itself
            if hasattr(module, 'to_q'):
                h = module.register_forward_hook(make_hook(name))
                hooks.append(h)

    return captured, hooks


def compute_cosine_similarity(feat1, feat2):
    """Compute cosine similarity between two feature tensors."""
    f1 = feat1.flatten().float()
    f2 = feat2.flatten().float()
    return (torch.dot(f1, f2) / (f1.norm() * f2.norm() + 1e-8)).item()


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/output/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    crash_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r8-lr5e4-500-lora-broken-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors'
    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcbcaad14353af8/image/000.png'
    sample_image = Image.open(sample_image_path).convert('RGBA')

    device = 'cuda'

    # --- Run Original ---
    print("Running Original...")
    pipeline_orig = load_pipeline(checkpoint_path, unet_ckpt_path, device)
    captured_orig, hooks_orig = register_hooks(pipeline_orig)
    torch.manual_seed(42); np.random.seed(42)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        _ = pipeline_orig(sample_image, num_inference_steps=30, output_type='pil')
    for h in hooks_orig:
        h.remove()
    del pipeline_orig; torch.cuda.empty_cache()
    print(f"  Captured {len(captured_orig)} layers")

    # --- Run Full LoRA ---
    print("Running Full LoRA...")
    pipeline_full = load_pipeline(checkpoint_path, unet_ckpt_path, device)
    merge_lora_into_unet(pipeline_full.unet, crash_lora_path, rank=8, alpha=8)
    captured_full, hooks_full = register_hooks(pipeline_full)
    torch.manual_seed(42); np.random.seed(42)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        _ = pipeline_full(sample_image, num_inference_steps=30, output_type='pil')
    for h in hooks_full:
        h.remove()
    del pipeline_full; torch.cuda.empty_cache()
    print(f"  Captured {len(captured_full)} layers")

    # --- Run attn2-only LoRA ---
    print("Running attn2-only LoRA...")
    pipeline_attn2 = load_pipeline(checkpoint_path, unet_ckpt_path, device)
    merge_lora_into_unet_attn2_only(pipeline_attn2.unet, working_lora_path, rank=4, alpha=1)
    captured_attn2, hooks_attn2 = register_hooks(pipeline_attn2)
    torch.manual_seed(42); np.random.seed(42)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        _ = pipeline_attn2(sample_image, num_inference_steps=30, output_type='pil')
    for h in hooks_attn2:
        h.remove()
    del pipeline_attn2; torch.cuda.empty_cache()
    print(f"  Captured {len(captured_attn2)} layers")

    # --- Compute cosine similarities ---
    print("\nComputing cosine similarities...")
    common_layers = sorted(set(captured_orig.keys()) & set(captured_full.keys()) & set(captured_attn2.keys()))
    print(f"Common layers: {len(common_layers)}")

    layers = []
    sim_full = []
    sim_attn2 = []

    for layer_name in common_layers:
        orig_feat = captured_orig[layer_name]
        full_feat = captured_full[layer_name]
        attn2_feat = captured_attn2[layer_name]

        s_full = compute_cosine_similarity(orig_feat, full_feat)
        s_attn2 = compute_cosine_similarity(orig_feat, attn2_feat)

        layers.append(layer_name.split('.')[-2] + '.' + layer_name.split('.')[-1])
        sim_full.append(s_full)
        sim_attn2.append(s_attn2)

    # --- Plot ---
    print("Generating plot...")
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(layers))
    ax.plot(x, sim_full, 'o-', color='#FF5722', linewidth=2, markersize=4, label='Full LoRA (attn1+attn2)')
    ax.plot(x, sim_attn2, 's-', color='#4CAF50', linewidth=2, markersize=4, label='attn2-only LoRA')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Perfect match')

    ax.set_xlabel('Layer Index', fontsize=12)
    ax.set_ylabel('Cosine Similarity to Original Reference Features', fontsize=12)
    ax.set_title('Reference Feature Preservation: Full LoRA vs attn2-only LoRA', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)

    # Add annotations
    avg_full = np.mean(sim_full)
    avg_attn2 = np.mean(sim_attn2)
    ax.annotate(f'Avg: {avg_full:.3f}', xy=(len(layers)//2, avg_full),
                xytext=(len(layers)//2, avg_full - 0.15),
                arrowprops=dict(arrowstyle='->', color='#FF5722'),
                fontsize=10, color='#FF5722')
    ax.annotate(f'Avg: {avg_attn2:.3f}', xy=(len(layers)//2, avg_attn2),
                xytext=(len(layers)//2, avg_attn2 + 0.08),
                arrowprops=dict(arrowstyle='->', color='#4CAF50'),
                fontsize=10, color='#4CAF50')

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'mechanism_hook_analysis.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved to {save_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Full LoRA avg cosine similarity:    {avg_full:.4f}")
    print(f"attn2-only avg cosine similarity:   {avg_attn2:.4f}")
    print(f"Difference:                         {avg_attn2 - avg_full:+.4f}")

    if avg_attn2 > avg_full + 0.1:
        print("\n✅ attn2-only LoRA preserves reference features much better than Full LoRA")
    elif avg_attn2 > avg_full:
        print("\n⚠️ attn2-only LoRA preserves reference features better than Full LoRA")
    else:
        print("\n❌ Both approaches show similar reference feature degradation")


if __name__ == '__main__':
    main()
