"""
LoRA Diagnostics Script for MV-Painter
=======================================
Runs 5 experiments to diagnose why LoRA fine-tuning produces degraded outputs.

Usage:
    python lora_diagnostics.py \
        --pipeline_path ../checkpoints/hf_repo \
        --lora_r4 logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors \
        --lora_r8 logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors \
        --output_dir lora_diag_results
"""

import os
import sys
import json
import argparse
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from mvpainter.lora_utils import merge_lora_into_unet, load_lora_weights, create_lora_processors
from diffusers import EulerAncestralDiscreteScheduler


def load_pipeline(pipeline_path):
    """Load pipeline with ControlNet, return (pipeline, bare_unet_ref)."""
    print('Loading pipeline...')
    pipeline = MVPainter_Pipeline.from_pretrained(
        pipeline_path, torch_dtype=torch.float16,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    # Load custom UNet checkpoint
    unet_ckpt_path = os.path.join(pipeline_path, 'unet', 'diffusion_pytorch_model.safetensors')
    alt_path = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(alt_path) and os.path.getsize(alt_path) > 14_000_000_000:
        unet_ckpt_path = alt_path
    if os.path.exists(unet_ckpt_path):
        ckpt = load_file(unet_ckpt_path)
        missing, unexpected = pipeline.unet.load_state_dict(ckpt, strict=False)
        if missing:
            print(f'  WARNING: {len(missing)} missing keys when loading UNet')
            for k in missing[:5]:
                print(f'    {k}')
        if unexpected:
            print(f'  WARNING: {len(unexpected)} unexpected keys when loading UNet')
            for k in unexpected[:5]:
                print(f'    {k}')

    from mvpainter.controlnet import ControlNetModel_Union
    controlnet = ControlNetModel_Union.from_unet(pipeline.unet).to(dtype=torch.float16, device=pipeline.device)
    pipeline.add_controlnet(controlnet, conditioning_scale=1.0)
    pipeline = pipeline.to('cuda')

    # Get reference to the bare UNet (inside RefOnlyNoisedUNet inside DepthControlUNet)
    bare_unet = pipeline.unet.unet.unet if hasattr(pipeline.unet, 'unet') else pipeline.unet
    return pipeline, bare_unet


def reload_base_weights(pipeline, bare_unet, pipeline_path):
    """Reload base UNet weights to undo any LoRA merge."""
    base_ckpt = os.path.join(pipeline_path, 'unet', 'diffusion_pytorch_model.safetensors')
    alt_path = '../checkpoints/v29_25000.safetensors'
    if os.path.exists(alt_path) and os.path.getsize(alt_path) > 14_000_000_000:
        base_ckpt = alt_path
    if os.path.exists(base_ckpt):
        bare_unet.load_state_dict(load_file(base_ckpt), strict=False)
        print('  Reloaded base UNet weights.')


def run_single_inference(pipeline, input_image_path, depth_image_path, output_path, seed=42):
    """Run inference and save result. Returns output image path."""
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    os.makedirs(output_path, exist_ok=True)

    input_image = Image.open(input_image_path).convert('RGBA')
    depth_image = Image.open(depth_image_path)

    output = pipeline(
        input_image,
        depth_image=depth_image,
        num_inference_steps=50,
    )
    result_path = os.path.join(output_path, 'result_6view.png')
    output[0].save(result_path)
    return result_path


# ===========================================================================
# Experiment 1: LoRA Weight Analysis
# ===========================================================================
def experiment_weight_analysis(lora_path, label):
    """Analyze LoRA weight magnitudes and health."""
    print(f'\n{"="*60}')
    print(f'EXPERIMENT: Weight Analysis — {label}')
    print(f'{"="*60}')

    if not os.path.exists(lora_path):
        print(f'  SKIP: {lora_path} not found')
        return None

    state = load_file(lora_path)
    print(f'  Total tensors: {len(state)}')

    # Compute per-layer statistics
    layer_stats = {}
    for key in sorted(state.keys()):
        w = state[key].float()
        layer_stats[key] = {
            'shape': list(w.shape),
            'mean': w.mean().item(),
            'std': w.std().item(),
            'abs_max': w.abs().max().item(),
            'abs_mean': w.abs().mean().item(),
            'norm': w.norm().item(),
            'numel': w.numel(),
        }

    # Compute up@down delta norms for each attention layer
    delta_stats = {}
    prefixes = set()
    for k in state:
        if k.endswith('_down'):
            prefixes.add(k.rsplit('_down', 1)[0])

    for prefix in sorted(prefixes):
        down_key = f'{prefix}_down'
        up_key = f'{prefix}_up'
        if down_key in state and up_key in state:
            down_w = state[down_key].float()
            up_w = state[up_key].float()
            delta = up_w @ down_w  # [out_dim, in_dim]
            delta_stats[prefix] = {
                'delta_norm': delta.norm().item(),
                'delta_abs_mean': delta.abs().mean().item(),
                'delta_abs_max': delta.abs().max().item(),
                'down_norm': down_w.norm().item(),
                'up_norm': up_w.norm().item(),
            }

    # Summary
    all_abs_max = [s['abs_max'] for s in layer_stats.values()]
    all_norms = [s['norm'] for s in layer_stats.values()]
    all_delta_norms = [s['delta_norm'] for s in delta_stats.values()]

    print(f'\n  --- Layer weight summary ---')
    print(f'  Weight abs_max  — min: {min(all_abs_max):.6f}, max: {max(all_abs_max):.6f}, mean: {np.mean(all_abs_max):.6f}')
    print(f'  Weight norms    — min: {min(all_norms):.4f}, max: {max(all_norms):.4f}, mean: {np.mean(all_norms):.4f}')
    print(f'  Delta (up@down) norms — min: {min(all_delta_norms):.6f}, max: {max(all_delta_norms):.6f}, mean: {np.mean(all_delta_norms):.6f}')

    # Check for degenerate weights
    warnings = []
    if max(all_abs_max) < 1e-6:
        warnings.append('CRITICAL: All LoRA weights near zero — training may have collapsed')
    if max(all_abs_max) > 10.0:
        warnings.append(f'WARNING: Some LoRA weights very large (max={max(all_abs_max):.4f}) — may destabilize generation')
    if np.std(all_norms) / (np.mean(all_norms) + 1e-8) > 5.0:
        warnings.append('WARNING: Highly variable layer norms — some layers dominating')

    if warnings:
        print(f'\n  *** WARNINGS ***')
        for w in warnings:
            print(f'  {w}')
    else:
        print(f'\n  Weights look reasonable (no degenerate patterns detected).')

    # Show top-5 largest delta layers
    top5 = sorted(delta_stats.items(), key=lambda x: x[1]['delta_norm'], reverse=True)[:5]
    print(f'\n  Top-5 layers by delta norm:')
    for name, st in top5:
        print(f'    {name}: delta_norm={st["delta_norm"]:.6f}, down_norm={st["down_norm"]:.4f}, up_norm={st["up_norm"]:.4f}')

    return {
        'layer_stats': layer_stats,
        'delta_stats': delta_stats,
        'warnings': warnings,
    }


# ===========================================================================
# Experiment 2: LoRA Scale Sweep
# ===========================================================================
def experiment_scale_sweep(pipeline, bare_unet, pipeline_path, lora_path, label,
                           test_img, test_depth, output_dir, scales=None):
    """Run inference with different LoRA scales."""
    print(f'\n{"="*60}')
    print(f'EXPERIMENT: Scale Sweep — {label}')
    print(f'{"="*60}')

    if not os.path.exists(lora_path):
        print(f'  SKIP: {lora_path} not found')
        return

    if scales is None:
        scales = [0.0, 0.1, 0.25, 0.5, 1.0]

    for scale in scales:
        print(f'\n  --- scale={scale} ---')
        reload_base_weights(pipeline, bare_unet, pipeline_path)

        # Merge with custom scale
        lora_state = load_file(lora_path)

        # Read config to get rank/alpha
        config_path = lora_path.replace('.safetensors', '_config.json')
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
            rank = cfg.get('rank', 8)
            alpha = cfg.get('alpha', rank)
        else:
            # Infer from filename
            rank = 4 if 'rank4' in lora_path.lower() or 'r4' in lora_path.lower() else 8
            alpha = rank

        effective_scale = (alpha / rank) * scale  # Override the global scale

        # Manual merge with custom scale
        from diffusers.models.attention_processor import AttnProcessor2_0
        for proc_name, _ in bare_unet.attn_processors.items():
            prefix = proc_name.replace('.processor', '').replace('.', '_')
            attn_module_name = proc_name.replace('.processor', '')
            attn_module = dict(bare_unet.named_modules())[attn_module_name]

            for proj_name in ['to_q', 'to_k', 'to_v']:
                down_key = f'{prefix}_{proj_name}_lora_down'
                up_key = f'{prefix}_{proj_name}_lora_up'
                if down_key in lora_state and up_key in lora_state:
                    proj_layer = getattr(attn_module, proj_name)
                    delta = (lora_state[up_key] @ lora_state[down_key]) * effective_scale
                    proj_layer.weight.data += delta.to(device=proj_layer.weight.device, dtype=proj_layer.weight.dtype)

            down_key = f'{prefix}_to_out_lora_down'
            up_key = f'{prefix}_to_out_lora_up'
            if down_key in lora_state and up_key in lora_state:
                delta = (lora_state[up_key] @ lora_state[down_key]) * effective_scale
                attn_module.to_out[0].weight.data += delta.to(
                    device=attn_module.to_out[0].weight.device,
                    dtype=attn_module.to_out[0].weight.dtype,
                )

        out_dir = os.path.join(output_dir, f'{label}_scale{scale}')
        run_single_inference(pipeline, test_img, test_depth, out_dir)
        print(f'  Saved to {out_dir}')


# ===========================================================================
# Experiment 3: Merge vs Processor-based Inference
# ===========================================================================
def experiment_merge_vs_processor(pipeline, bare_unet, pipeline_path, lora_path, label,
                                  test_img, test_depth, output_dir):
    """Compare merge-then-infer vs processor-based inference."""
    print(f'\n{"="*60}')
    print(f'EXPERIMENT: Merge vs Processor — {label}')
    print(f'{"="*60}')

    if not os.path.exists(lora_path):
        print(f'  SKIP: {lora_path} not found')
        return

    config_path = lora_path.replace('.safetensors', '_config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg.get('rank', 8)
        alpha = cfg.get('alpha', rank)
    else:
        rank = 4 if 'rank4' in lora_path.lower() or 'r4' in lora_path.lower() else 8
        alpha = rank

    # Method A: merge-then-infer
    print('\n  --- Method A: merge_lora_into_unet ---')
    reload_base_weights(pipeline, bare_unet, pipeline_path)
    merge_lora_into_unet(bare_unet, lora_path, rank=rank, alpha=alpha)
    out_dir = os.path.join(output_dir, f'{label}_merge')
    run_single_inference(pipeline, test_img, test_depth, out_dir)
    print(f'  Saved to {out_dir}')

    # Method B: processor-based (no merge)
    print('\n  --- Method B: processor-based (set_attn_processor) ---')
    reload_base_weights(pipeline, bare_unet, pipeline_path)
    load_lora_weights(bare_unet, lora_path, rank=rank, alpha=alpha)
    out_dir = os.path.join(output_dir, f'{label}_processor')
    run_single_inference(pipeline, test_img, test_depth, out_dir)
    print(f'  Saved to {out_dir}')


# ===========================================================================
# Experiment 4: Training Set vs Test Set
# ===========================================================================
def experiment_train_vs_test(pipeline, bare_unet, pipeline_path, lora_path, label,
                             output_dir, train_data_dir, num_train=3, num_test=3):
    """Run inference on training samples vs test samples."""
    print(f'\n{"="*60}')
    print(f'EXPERIMENT: Train vs Test Samples — {label}')
    print(f'{"="*60}')

    if not os.path.exists(lora_path):
        print(f'  SKIP: {lora_path} not found')
        return

    # Load training object list
    clean_list_path = os.path.join(train_data_dir, 'clean_objects.txt')
    if not os.path.exists(clean_list_path):
        print(f'  SKIP: {clean_list_path} not found')
        return

    with open(clean_list_path) as f:
        all_objects = [l.strip() for l in f.readlines() if l.strip()]

    # Use first N as "train" (likely seen), last N as "test" (likely unseen)
    train_objects = all_objects[:num_train]
    test_objects = all_objects[-num_test:]

    # Merge LoRA
    config_path = lora_path.replace('.safetensors', '_config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg.get('rank', 8)
        alpha = cfg.get('alpha', rank)
    else:
        rank = 4 if 'rank4' in lora_path.lower() or 'r4' in lora_path.lower() else 8
        alpha = rank

    reload_base_weights(pipeline, bare_unet, pipeline_path)
    merge_lora_into_unet(bare_unet, lora_path, rank=rank, alpha=alpha)

    def run_on_objects(objects, split_name):
        for i, obj in enumerate(objects):
            obj_path = os.path.join(train_data_dir, obj)
            img_path = os.path.join(obj_path, 'image', '000.png')
            depth_path = os.path.join(obj_path, 'depth_png', '000.png')
            if not os.path.exists(img_path) or not os.path.exists(depth_path):
                print(f'  Skipping {obj}: missing files')
                continue
            out_dir = os.path.join(output_dir, f'{label}_{split_name}_{i}_{obj}')
            run_single_inference(pipeline, img_path, depth_path, out_dir)
            print(f'  [{split_name}] {obj} -> {out_dir}')

    print(f'\n  --- Training samples (first {num_train}) ---')
    run_on_objects(train_objects, 'train')

    print(f'\n  --- Test samples (last {num_test}) ---')
    run_on_objects(test_objects, 'test')

    # Also run zero-shot on same test samples for comparison
    print(f'\n  --- Zero-shot baseline on test samples ---')
    reload_base_weights(pipeline, bare_unet, pipeline_path)
    run_on_objects(test_objects, 'zeroshot')


# ===========================================================================
# Experiment 5: Delta magnitude relative to base weights
# ===========================================================================
def experiment_delta_magnitude(pipeline, bare_unet, lora_path, label):
    """Check delta_norm / weight_norm ratio for each layer."""
    print(f'\n{"="*60}')
    print(f'EXPERIMENT: Delta Magnitude — {label}')
    print(f'{"="*60}')

    if not os.path.exists(lora_path):
        print(f'  SKIP: {lora_path} not found')
        return

    lora_state = load_file(lora_path)

    config_path = lora_path.replace('.safetensors', '_config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        rank = cfg.get('rank', 8)
        alpha = cfg.get('alpha', rank)
    else:
        rank = 4 if 'rank4' in lora_path.lower() or 'r4' in lora_path.lower() else 8
        alpha = rank

    scale = alpha / rank

    ratios = {}
    for proc_name, _ in bare_unet.attn_processors.items():
        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(bare_unet.named_modules())[attn_module_name]

        for proj_name in ['to_q', 'to_k', 'to_v', 'to_out']:
            if proj_name == 'to_out':
                base_weight = attn_module.to_out[0].weight.data.float()
                down_key = f'{prefix}_to_out_lora_down'
                up_key = f'{prefix}_to_out_lora_up'
            else:
                base_weight = getattr(attn_module, proj_name).weight.data.float()
                down_key = f'{prefix}_{proj_name}_lora_down'
                up_key = f'{prefix}_{proj_name}_lora_up'

            if down_key in lora_state and up_key in lora_state:
                delta = (lora_state[up_key].float() @ lora_state[down_key].float()) * scale
                base_norm = base_weight.norm().item()
                delta_norm = delta.norm().item()
                ratio = delta_norm / (base_norm + 1e-8)
                layer_name = f'{prefix}.{proj_name}'
                ratios[layer_name] = ratio

    if not ratios:
        print('  No LoRA layers found.')
        return

    all_ratios = list(ratios.values())
    print(f'  delta_norm / weight_norm ratio:')
    print(f'    min:    {min(all_ratios):.6f}')
    print(f'    max:    {max(all_ratios):.6f}')
    print(f'    mean:   {np.mean(all_ratios):.6f}')
    print(f'    median: {np.median(all_ratios):.6f}')

    # Show distribution
    thresholds = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
    for t in thresholds:
        count = sum(1 for r in all_ratios if r > t)
        print(f'    layers with ratio > {t}: {count}/{len(all_ratios)}')

    # Top-10 largest ratios
    top10 = sorted(ratios.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f'\n  Top-10 layers by delta/weight ratio:')
    for name, ratio in top10:
        print(f'    {name}: {ratio:.6f}')

    if max(all_ratios) > 1.0:
        print(f'\n  *** WARNING: Some LoRA deltas exceed base weight magnitude! ***')
        print(f'  This strongly suggests the LoRA is corrupting the model.')
    elif max(all_ratios) > 0.1:
        print(f'\n  *** WARNING: Some LoRA deltas are >10% of base weights. ***')
        print(f'  Consider using a lower inference scale.')


# ===========================================================================
# Main
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(description='LoRA Diagnostics for MV-Painter')
    parser.add_argument('--pipeline_path', default='../checkpoints/hf_repo')
    parser.add_argument('--lora_r4', default='logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors')
    parser.add_argument('--lora_r8', default='logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors')
    parser.add_argument('--output_dir', default='lora_diag_results')
    parser.add_argument('--train_data_dir', default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--experiment', type=int, default=0,
                        help='Run specific experiment (1-5), 0=all')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # === Experiment 1 & 5 (no GPU needed for weight analysis) ===
    if args.experiment in (0, 1, 5):
        for label, path in [('r4', args.lora_r4), ('r8', args.lora_r8)]:
            if args.experiment in (0, 1):
                experiment_weight_analysis(path, label)

    # === GPU experiments (2, 3, 4) ===
    if args.experiment in (0, 2, 3, 4, 5):
        pipeline, bare_unet = load_pipeline(args.pipeline_path)

        # Pick a test sample
        clean_list_path = os.path.join(args.train_data_dir, 'clean_objects.txt')
        if os.path.exists(clean_list_path):
            with open(clean_list_path) as f:
                all_objects = [l.strip() for l in f.readlines() if l.strip()]
            test_obj = all_objects[-1]  # Last object as test
            test_img = os.path.join(args.train_data_dir, test_obj, 'image', '000.png')
            test_depth = os.path.join(args.train_data_dir, test_obj, 'depth_png', '000.png')
        else:
            print(f'WARNING: {clean_list_path} not found, skipping inference experiments')
            test_img = test_depth = None

        if test_img and os.path.exists(test_img):
            for label, lora_path in [('r4', args.lora_r4), ('r8', args.lora_r8)]:
                if not os.path.exists(lora_path):
                    print(f'\nSKIP {label}: {lora_path} not found')
                    continue

                if args.experiment in (0, 2):
                    experiment_scale_sweep(
                        pipeline, bare_unet, args.pipeline_path,
                        lora_path, label, test_img, test_depth,
                        args.output_dir,
                    )

                if args.experiment in (0, 3):
                    experiment_merge_vs_processor(
                        pipeline, bare_unet, args.pipeline_path,
                        lora_path, label, test_img, test_depth,
                        args.output_dir,
                    )

                if args.experiment in (0, 4):
                    experiment_train_vs_test(
                        pipeline, bare_unet, args.pipeline_path,
                        lora_path, label, args.output_dir,
                        args.train_data_dir,
                    )

                if args.experiment in (0, 5):
                    experiment_delta_magnitude(pipeline, bare_unet, lora_path, label)

    print(f'\n{"="*60}')
    print(f'DONE. Results in {args.output_dir}/')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
