"""
Deep diagnostics: verify merge formula, weight shapes, delta magnitude, and compare
merge vs processor-based inference at multiple scales.
"""
import os
import sys
import json
import torch
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LORA_R4 = 'logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors'
LORA_R8 = 'logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
PIPELINE_PATH = '../checkpoints/hf_repo'


def shape_diag():
    """Check LoRA weight shapes and compare to base weights."""
    print("=" * 60)
    print("LoRA Weight Shape Diagnostic")
    print("=" * 60)

    for label, lora_path in [('r4', LORA_R4), ('r8', LORA_R8)]:
        if not os.path.exists(lora_path):
            print(f"\n{label}: SKIP — not found")
            continue

        config_path = lora_path.replace('.safetensors', '_config.json')
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg['rank']
        alpha = cfg['alpha']
        scale = alpha / rank
        print(f"\n{label}: rank={rank}, alpha={alpha}, scale={scale}")

        lora_state = load_file(lora_path)

        # Group by down/up pairs and check shapes
        down_keys = sorted([k for k in lora_state if k.endswith('_down')])
        print(f"  Total LoRA layers: {len(down_keys)}")

        # Check first few
        for dk in down_keys[:5]:
            uk = dk.replace('_down', '_up')
            if uk in lora_state:
                d = lora_state[dk]
                u = lora_state[uk]
                delta = (u @ d) * scale
                print(f"  {dk}:")
                print(f"    down: {list(d.shape)}, up: {list(u.shape)}, delta: {list(delta.shape)}")
                print(f"    down norm={d.norm():.6f}, up norm={u.norm():.6f}, delta norm={delta.norm():.6f}")
                print(f"    delta abs_mean={delta.abs().mean():.8f}, abs_max={delta.abs().max():.8f}")

        # Check ALL delta norms
        all_delta_norms = []
        for dk in down_keys:
            uk = dk.replace('_down', '_up')
            if uk in lora_state:
                delta = (lora_state[uk] @ lora_state[dk]) * scale
                all_delta_norms.append(delta.norm().item())

        print(f"\n  Delta norm stats across all {len(all_delta_norms)} layers:")
        print(f"    min={min(all_delta_norms):.6f}, max={max(all_delta_norms):.6f}, "
              f"mean={sum(all_delta_norms)/len(all_delta_norms):.6f}")
        print(f"    median={sorted(all_delta_norms)[len(all_delta_norms)//2]:.6f}")


def merge_effect_diag():
    """Check how much the merge changes the base weights."""
    print("\n" + "=" * 60)
    print("Merge Effect Diagnostic: compare weights before/after merge")
    print("=" * 60)

    from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
    from diffusers import EulerAncestralDiscreteScheduler
    from mvpainter.lora_utils import merge_lora_into_unet

    print("Loading pipeline...")
    pipeline = MVPainter_Pipeline.from_pretrained(PIPELINE_PATH, torch_dtype=torch.float16)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Get bare UNet
    pipeline.prepare()  # Wrap in RefOnlyNoisedUNet
    bare_unet = pipeline.unet.unet

    # Load custom UNet checkpoint
    unet_ckpt = os.path.join(PIPELINE_PATH, 'unet', 'diffusion_pytorch_model.safetensors')
    alt_ckpt = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(alt_ckpt) and os.path.getsize(alt_ckpt) > 14_000_000_000:
        unet_ckpt = alt_ckpt
    print(f"Loading base UNet from: {unet_ckpt}")
    missing, unexpected = bare_unet.load_state_dict(load_file(unet_ckpt), strict=False)
    print(f"  Loaded: {len(missing)} missing, {len(unexpected)} unexpected keys")
    if missing[:5]:
        print(f"  Sample missing: {missing[:5]}")
    if unexpected[:5]:
        print(f"  Sample unexpected: {unexpected[:5]}")

    for label, lora_path in [('r4', LORA_R4), ('r8', LORA_R8)]:
        if not os.path.exists(lora_path):
            print(f"\n{label}: SKIP")
            continue

        config_path = lora_path.replace('.safetensors', '_config.json')
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg['rank']
        alpha = cfg['alpha']
        scale = alpha / rank

        print(f"\n{label}: rank={rank}, alpha={alpha}, scale={scale}")

        # Save pre-merge weights for some layers
        sample_layers = []
        for name, module in list(bare_unet.named_modules())[:5]:
            if hasattr(module, 'to_q') and hasattr(module.to_q, 'weight'):
                pre_w = module.to_q.weight.data.float().clone()
                sample_layers.append((name, 'to_q', pre_w))
                pre_w = module.to_k.weight.data.float().clone()
                sample_layers.append((name, 'to_k', pre_w))
                if len(sample_layers) >= 6:
                    break

        # Merge
        merge_lora_into_unet(bare_unet, lora_path, rank=rank, alpha=alpha)

        # Check change
        print(f"\n  Weight change after merge:")
        for name, proj, pre_w in sample_layers:
            module = dict(bare_unet.named_modules())[name]
            post_w = getattr(module, proj).weight.data.float()
            diff = (post_w - pre_w)
            print(f"    {name}.{proj}: "
                  f"pre_norm={pre_w.norm():.4f}, "
                  f"post_norm={post_w.norm():.4f}, "
                  f"diff_norm={diff.norm():.6f}, "
                  f"diff_pct={diff.norm()/(pre_w.norm()+1e-8)*100:.4f}%")

        # Check if any weights changed to all zeros or NaN
        print(f"\n  Post-merge weight health check:")
        nan_count = 0
        inf_count = 0
        zero_count = 0
        total_count = 0
        for name, param in bare_unet.named_parameters():
            if 'weight' in name and 'attn' in name:
                total_count += 1
                if torch.isnan(param.data).any():
                    nan_count += 1
                if torch.isinf(param.data).any():
                    inf_count += 1
                if param.data.abs().max() < 1e-10:
                    zero_count += 1
        print(f"    Checked {total_count} weight tensors: "
              f"{nan_count} NaN, {inf_count} Inf, {zero_count} all-zeros")

    print("\nDone!")


if __name__ == '__main__':
    shape_diag()
    merge_effect_diag()
