"""
Test attn2-only LoRA inference.
Compare zero-shot vs attn2-only LoRA on multiple samples.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
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
    output_dir = '/4T/CXY/MV-Painter/attn2_lora_test'
    os.makedirs(output_dir, exist_ok=True)

    # Test samples
    test_samples = [
        'd6a5427888b8413fbfcb',
        '00603cadc4474dafb78cdb55278568f2',
        '0a34342507704b6bbb5c8f39347249d8',
        '0b98863aaa2b421e85434789da3fb97f',
    ]

    lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-lora-attn2-only-r4-lr1e5/lora_checkpoints/lora_step_0000100.safetensors'

    results = []

    for sample_id in test_samples:
        sample_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{sample_id}/image/000.png'
        if not os.path.exists(sample_path):
            print(f"Skipping {sample_id}: not found")
            continue

        print(f"\n{'='*60}")
        print(f"Testing: {sample_id}")
        print(f"{'='*60}")

        sample_image = Image.open(sample_path).convert('RGBA')

        # Zero-shot
        print("Running zero-shot...")
        p1 = load_pipeline(checkpoint_path, unet_ckpt_path)
        img_zs = run_pipeline(p1, sample_image, seed=42)
        img_zs.save(os.path.join(output_dir, f'{sample_id}_zeroshot.png'))
        del p1
        torch.cuda.empty_cache()

        # attn2-only LoRA
        print("Running attn2-only LoRA...")
        p2 = load_pipeline(checkpoint_path, unet_ckpt_path)
        merge_lora_into_unet_attn2_only(p2.unet, lora_path, rank=4, alpha=4)
        img_lora = run_pipeline(p2, sample_image, seed=42)
        img_lora.save(os.path.join(output_dir, f'{sample_id}_attn2_lora.png'))
        del p2
        torch.cuda.empty_cache()

        # Compare
        p = psnr(img_zs, img_lora)
        print(f"PSNR: {p:.2f} dB")

        results.append({
            'sample': sample_id,
            'psnr': p,
            'status': 'PASS' if p > 25 else 'WARN' if p > 15 else 'FAIL',
        })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Sample':<30} {'PSNR':>10} {'Status':>10}")
    print("-" * 50)
    for r in results:
        print(f"{r['sample'][:30]:<30} {r['psnr']:>10.2f} {r['status']:>10}")

    avg_psnr = np.mean([r['psnr'] for r in results])
    print(f"\nAverage PSNR: {avg_psnr:.2f} dB")

    if avg_psnr > 25:
        print("✅ attn2-only LoRA preserves zero-shot performance!")
    elif avg_psnr > 15:
        print("⚠️ attn2-only LoRA has moderate impact on zero-shot performance")
    else:
        print("❌ attn2-only LoRA significantly impacts zero-shot performance")


if __name__ == '__main__':
    main()
