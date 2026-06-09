"""
Test merge identity at pipeline level.
Compare zero-shot output with zero LoRA output using fixed seed.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import save_file, load_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from diffusers import EulerAncestralDiscreteScheduler


def run_pipeline_inference(pipeline, image, seed=42, num_steps=50):
    """Run pipeline inference with fixed seed."""
    # Set seed for reproducibility
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)

    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(
            image,
            num_inference_steps=num_steps,
            output_type='pil',
        )

    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def compare_images_psnr(img1, img2):
    """Compute PSNR between two PIL images."""
    arr1 = np.array(img1).astype(float)
    arr2 = np.array(img2).astype(float)

    if arr1.shape != arr2.shape:
        img2 = img2.resize(img1.size)
        arr2 = np.array(img2).astype(float)

    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float('inf')
    psnr = 10 * np.log10(255.0 ** 2 / mse)
    return psnr


def load_pipeline_base(checkpoint_path, unet_ckpt_path, device='cuda'):
    """Load base pipeline."""
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

    pipeline = pipeline.to(device)
    return pipeline


def main():
    checkpoint_path = '../checkpoints/hf_repo'
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/merge_identity_test'
    os.makedirs(output_dir, exist_ok=True)

    # Sample image
    sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcb/image/000.png'
    if not os.path.exists(sample_image_path):
        sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/00603cadc4474dafb78cdb55278568f2/image/000.png'

    sample_image = Image.open(sample_image_path).convert('RGBA')

    # Test 1: Zero-shot (baseline)
    print("="*60)
    print("TEST 1: Zero-shot (baseline)")
    print("="*60)

    pipeline1 = load_pipeline_base(checkpoint_path, unet_ckpt_path)
    img1 = run_pipeline_inference(pipeline1, sample_image, seed=42)
    img1.save(os.path.join(output_dir, 'zeroshot.png'))
    print(f"Saved zeroshot.png")

    # Test 2: Zero LoRA via merge
    print("\n" + "="*60)
    print("TEST 2: Zero LoRA via merge")
    print("="*60)

    pipeline2 = load_pipeline_base(checkpoint_path, unet_ckpt_path)

    # Create zero LoRA
    existing_ckpt = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
    existing_state = load_file(existing_ckpt)
    zero_state = {k: torch.zeros_like(v) for k, v in existing_state.items()}
    zero_path = '/tmp/zero_lora_test.safetensors'
    save_file(zero_state, zero_path)

    # Merge zero LoRA
    from mvpainter.lora_utils import merge_lora_into_unet
    merge_lora_into_unet(pipeline2.unet, zero_path, rank=8, alpha=8)

    img2 = run_pipeline_inference(pipeline2, sample_image, seed=42)
    img2.save(os.path.join(output_dir, 'zero_lora_merged.png'))
    print(f"Saved zero_lora_merged.png")

    # Compare
    psnr = compare_images_psnr(img1, img2)
    print(f"\nPSNR (zero-shot vs zero LoRA merged): {psnr:.2f} dB")

    if psnr > 40:
        print("✅ PASS: Merge is identity!")
    else:
        print("❌ FAIL: Merge is NOT identity!")

    # Test 3: Check if the issue is in RefOnlyNoisedUNet wrapping
    print("\n" + "="*60)
    print("TEST 3: Direct UNet comparison (no RefOnlyNoisedUNet)")
    print("="*60)

    # Load base UNet without RefOnlyNoisedUNet
    pipeline3 = load_pipeline_base(checkpoint_path, unet_ckpt_path)
    unet_before = pipeline3.unet.state_dict()

    # Merge zero LoRA
    merge_lora_into_unet(pipeline3.unet, zero_path, rank=8, alpha=8)
    unet_after = pipeline3.unet.state_dict()

    # Compare weights
    weight_diff = 0
    for k in unet_before:
        if k in unet_after:
            diff = (unet_before[k] - unet_after[k]).abs().max().item()
            weight_diff = max(weight_diff, diff)

    print(f"Max weight diff after merge: {weight_diff:.6e}")

    if weight_diff < 1e-10:
        print("✅ Weights unchanged - merge is identity at weight level")
    else:
        print("❌ Weights changed - merge is NOT identity at weight level")

    # Test 4: Check processor state
    print("\n" + "="*60)
    print("TEST 4: Processor state comparison")
    print("="*60)

    pipeline4 = load_pipeline_base(checkpoint_path, unet_ckpt_path)

    # Get processors before merge
    procs_before = {name: type(proc).__name__ for name, proc in pipeline4.unet.attn_processors.items()}

    # Merge
    merge_lora_into_unet(pipeline4.unet, zero_path, rank=8, alpha=8)

    # Get processors after merge
    procs_after = {name: type(proc).__name__ for name, proc in pipeline4.unet.attn_processors.items()}

    # Compare
    changed_procs = 0
    for name in procs_before:
        if name in procs_after:
            if procs_before[name] != procs_after[name]:
                changed_procs += 1
                if changed_procs <= 3:
                    print(f"  {name}: {procs_before[name]} -> {procs_after[name]}")

    print(f"\nChanged processors: {changed_procs}/{len(procs_before)}")

    if changed_procs == 0:
        print("✅ Processors unchanged")
    else:
        print("❌ Processors changed!")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"PSNR (zero-shot vs zero LoRA): {psnr:.2f} dB")
    print(f"Weight diff: {weight_diff:.6e}")
    print(f"Changed processors: {changed_procs}")

    if psnr > 40 and weight_diff < 1e-10 and changed_procs == 0:
        print("\n✅ MERGE IS IDENTITY - Bug must be elsewhere")
    else:
        print("\n❌ MERGE IS NOT IDENTITY - Bug is in merge function")


if __name__ == '__main__':
    main()
