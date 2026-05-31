"""
Debug: Analyze why zero LoRA merge != zero-shot.
Check processor state before/after merge.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import save_file, load_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from diffusers import EulerAncestralDiscreteScheduler
from diffusers.models.attention_processor import AttnProcessor2_0


def get_processor_summary(unet, label=""):
    """Get summary of all processors in the UNet."""
    print(f"\n{'='*60}")
    print(f"Processor Summary: {label}")
    print(f"{'='*60}")

    procs = unet.attn_processors
    type_counts = {}
    enabled_counts = {'enabled': 0, 'disabled': 0}

    for name, proc in procs.items():
        proc_type = type(proc).__name__
        type_counts[proc_type] = type_counts.get(proc_type, 0) + 1

        if isinstance(proc, ReferenceOnlyAttnProc):
            if proc.enabled:
                enabled_counts['enabled'] += 1
            else:
                enabled_counts['disabled'] += 1

            chained_type = type(proc.chained_proc).__name__
            key = f"ReferenceOnlyAttnProc({chained_type})"
            type_counts[key] = type_counts.get(key, 0) + 1

    print(f"Total processors: {len(procs)}")
    for k, v in type_counts.items():
        print(f"  {k}: {v}")
    if enabled_counts['enabled'] + enabled_counts['disabled'] > 0:
        print(f"  ReferenceOnlyAttnProc enabled: {enabled_counts['enabled']}")
        print(f"  ReferenceOnlyAttnProc disabled: {enabled_counts['disabled']}")

    return procs


def check_weight_changes(unet_before, unet_after, label=""):
    """Check if any weights changed between before and after."""
    print(f"\n{'='*60}")
    print(f"Weight Changes: {label}")
    print(f"{'='*60}")

    changed = 0
    total = 0
    max_diff = 0

    for (name1, param1), (name2, param2) in zip(
        unet_before.named_parameters(), unet_after.named_parameters()
    ):
        total += 1
        diff = (param1.data - param2.data).abs().max().item()
        if diff > 1e-10:
            changed += 1
            max_diff = max(max_diff, diff)
            if changed <= 5:  # Show first 5 changes
                print(f"  {name1}: max_diff={diff:.6e}")

    print(f"\nTotal parameters: {total}")
    print(f"Changed parameters: {changed}")
    print(f"Max diff: {max_diff:.6e}")

    if changed == 0:
        print("✅ No weights changed - merge is identity!")
    else:
        print("❌ Weights changed - merge is NOT identity!")


def test_merge_identity():
    """Test if merge_lora_into_unet is identity for zero weights."""
    checkpoint_path = '../checkpoints/hf_repo'
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'

    print("Loading pipeline...")
    pipeline = MVPainter_Pipeline.from_pretrained(
        checkpoint_path, torch_dtype=torch.float16, use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Load custom UNet
    if os.path.exists(unet_ckpt_path):
        print(f"Loading custom UNet...")
        ckpt = load_file(unet_ckpt_path)
        unet_state = {k[len('unet.unet.'):]: v for k, v in ckpt.items() if k.startswith('unet.unet.')}
        if unet_state:
            pipeline.unet.load_state_dict(unet_state, strict=False)

    # Get processor summary before any wrapping
    get_processor_summary(pipeline.unet, "After loading (bare UNet)")

    # Check if processors are AttnProcessor2_0
    for name, proc in list(pipeline.unet.attn_processors.items())[:3]:
        print(f"\n  {name}: {type(proc).__name__}")

    # Save weights before wrapping
    weights_before = {n: p.data.clone() for n, p in pipeline.unet.named_parameters()}

    # Now test: what does the pipeline do to processors?
    # The pipeline __call__ method uses RefOnlyNoisedUNet
    # Let's check if the UNet is already wrapped
    print(f"\nUNet type: {type(pipeline.unet).__name__}")

    # Check if it's a RefOnlyNoisedUNet
    if isinstance(pipeline.unet, RefOnlyNoisedUNet):
        print("UNet is already RefOnlyNoisedUNet")
        inner_unet = pipeline.unet.unet
    else:
        print("UNet is NOT RefOnlyNoisedUNet")
        inner_unet = pipeline.unet

    # Check inner UNet processors
    get_processor_summary(inner_unet, "Inner UNet")

    # Now simulate what merge_lora_into_unet does
    print("\n" + "="*60)
    print("Simulating merge_lora_into_unet with zero weights")
    print("="*60)

    # Create zero LoRA state
    # First, get the expected key structure
    from mvpainter.lora_utils import create_lora_processors

    # We need to create the processors to know the key structure
    # But create_lora_processors uses old API...
    # Let's manually create zero weights based on the checkpoint structure

    existing_ckpt = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
    if os.path.exists(existing_ckpt):
        existing_state = load_file(existing_ckpt)
        zero_state = {k: torch.zeros_like(v) for k, v in existing_state.items()}
        zero_path = '/tmp/zero_lora_debug.safetensors'
        save_file(zero_state, zero_path)

        # Now merge
        from mvpainter.lora_utils import merge_lora_into_unet
        merge_lora_into_unet(inner_unet, zero_path, rank=8, alpha=8)

        # Check weights after merge
        weights_after = {n: p.data.clone() for n, p in inner_unet.named_parameters()}
        check_weight_changes_simple(weights_before, weights_after, "After zero merge")

        # Check processors after merge
        get_processor_summary(inner_unet, "After zero merge")

        # Compare specific processor behavior
        print("\n" + "="*60)
        print("Comparing processor behavior")
        print("="*60)

        # Check if ReferenceOnlyAttnProc still works
        for name, proc in inner_unet.attn_processors.items():
            if isinstance(proc, ReferenceOnlyAttnProc):
                print(f"\n{name}:")
                print(f"  enabled: {proc.enabled}")
                print(f"  chained_proc type: {type(proc.chained_proc).__name__}")
                break


def check_weight_changes_simple(weights_before, weights_after, label):
    """Simple weight change check."""
    print(f"\n{label}:")
    changed = 0
    max_diff = 0

    for name in weights_before:
        if name in weights_after:
            diff = (weights_before[name] - weights_after[name]).abs().max().item()
            if diff > 1e-10:
                changed += 1
                max_diff = max(max_diff, diff)

    print(f"  Changed: {changed}/{len(weights_before)}")
    print(f"  Max diff: {max_diff:.6e}")

    if changed == 0:
        print("  ✅ Identity!")
    else:
        print("  ❌ NOT identity!")


if __name__ == '__main__':
    test_merge_identity()
