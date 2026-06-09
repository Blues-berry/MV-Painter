"""
Test trained LoRA checkpoint with fixed seed.
Compare zero-shot vs trained LoRA to understand the actual issue.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler


def run_pipeline(pipeline, image, seed=42, num_steps=50):
    """Run pipeline with fixed seed."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)

    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')

    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def psnr(img1, img2):
    """Compute PSNR."""
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def load_pipeline(checkpoint_path, unet_ckpt_path, device='cuda'):
    """Load pipeline."""
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


def main():
    checkpoint_path = '../checkpoints/hf_repo'
    unet_ckpt_path = '../checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/trained_lora_test'
    os.makedirs(output_dir, exist_ok=True)

    sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcb/image/000.png'
    if not os.path.exists(sample_image_path):
        sample_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/00603cadc4474dafb78cdb55278568f2/image/000.png'

    sample_image = Image.open(sample_image_path).convert('RGBA')

    # Test 1: Zero-shot baseline
    print("="*60)
    print("TEST 1: Zero-shot baseline")
    print("="*60)
    p1 = load_pipeline(checkpoint_path, unet_ckpt_path)
    img1 = run_pipeline(p1, sample_image, seed=42)
    img1.save(os.path.join(output_dir, 'zeroshot_seed42.png'))
    print("Saved zeroshot_seed42.png")
    del p1
    torch.cuda.empty_cache()

    # Test 2: Zero-shot with same seed (reproducibility check)
    print("\n" + "="*60)
    print("TEST 2: Zero-shot same seed (reproducibility)")
    print("="*60)
    p2 = load_pipeline(checkpoint_path, unet_ckpt_path)
    img2 = run_pipeline(p2, sample_image, seed=42)
    img2.save(os.path.join(output_dir, 'zeroshot_seed42_v2.png'))
    print("Saved zeroshot_seed42_v2.png")

    psnr_12 = psnr(img1, img2)
    print(f"PSNR (run1 vs run2): {psnr_12:.2f} dB")
    if psnr_12 > 40:
        print("✅ Reproducible!")
    else:
        print("⚠️ Not fully reproducible (diffusion sampling variance)")
    del p2
    torch.cuda.empty_cache()

    # Test 3: Trained LoRA (rank 8)
    print("\n" + "="*60)
    print("TEST 3: Trained LoRA (rank 8, step 1000)")
    print("="*60)
    lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'

    p3 = load_pipeline(checkpoint_path, unet_ckpt_path)
    merge_lora_into_unet(p3.unet, lora_path, rank=8, alpha=8)
    img3 = run_pipeline(p3, sample_image, seed=42)
    img3.save(os.path.join(output_dir, 'trained_lora_r8_step1000.png'))
    print("Saved trained_lora_r8_step1000.png")

    psnr_13 = psnr(img1, img3)
    print(f"PSNR (zero-shot vs trained r8): {psnr_13:.2f} dB")
    if psnr_13 > 30:
        print("✅ LoRA output is similar to zero-shot")
    elif psnr_13 > 20:
        print("⚠️ LoRA output has noticeable differences")
    else:
        print("❌ LoRA output is very different from zero-shot")
    del p3
    torch.cuda.empty_cache()

    # Test 4: Trained LoRA (rank 4)
    print("\n" + "="*60)
    print("TEST 4: Trained LoRA (rank 4, step 1000)")
    print("="*60)
    lora_path_4 = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints/lora_step_0001000.safetensors'

    p4 = load_pipeline(checkpoint_path, unet_ckpt_path)
    merge_lora_into_unet(p4.unet, lora_path_4, rank=4, alpha=4)
    img4 = run_pipeline(p4, sample_image, seed=42)
    img4.save(os.path.join(output_dir, 'trained_lora_r4_step1000.png'))
    print("Saved trained_lora_r4_step1000.png")

    psnr_14 = psnr(img1, img4)
    print(f"PSNR (zero-shot vs trained r4): {psnr_14:.2f} dB")
    if psnr_14 > 30:
        print("✅ LoRA output is similar to zero-shot")
    elif psnr_14 > 20:
        print("⚠️ LoRA output has noticeable differences")
    else:
        print("❌ LoRA output is very different from zero-shot")
    del p4
    torch.cuda.empty_cache()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Reproducibility (same seed): {psnr_12:.2f} dB")
    print(f"Trained LoRA r8: {psnr_13:.2f} dB")
    print(f"Trained LoRA r4: {psnr_14:.2f} dB")

    if psnr_13 < 15 or psnr_14 < 15:
        print("\n❌ Trained LoRA produces very different output.")
        print("Possible causes:")
        print("1. LoRA applied to attn1 disrupts reference attention")
        print("2. Training hyperparameters (lr too high)")
        print("3. Training data issues")
    elif psnr_13 < 25 or psnr_14 < 25:
        print("\n⚠️ Trained LoRA has moderate differences.")
        print("May need attn2-only LoRA or lower lr.")
    else:
        print("\n✅ Trained LoRA output is reasonable.")


if __name__ == '__main__':
    main()
