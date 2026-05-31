"""
Task 4: Evaluate against Ground Truth.
Compute PSNR/SSIM of Original vs LoRA against GT rendered images.
"""
import os
import sys
import torch
import numpy as np
import csv
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from diffusers import EulerAncestralDiscreteScheduler


def load_pipeline(checkpoint_path, unet_ckpt_path, device='cuda'):
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
    return pipeline.to(device)


def run_inference(pipeline, image, seed=42, num_steps=50):
    """Run inference with fixed seed."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')
    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def psnr(img1, img2):
    """Compute PSNR between two PIL images."""
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0**2 / mse)


def ssim(img1, img2):
    """Compute SSIM between two PIL images."""
    from skimage.metrics import structural_similarity
    a1 = np.array(img1).astype(float)
    a2 = np.array(img2).astype(float)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(float)
    try:
        win_size = min(7, min(a1.shape[0], a1.shape[1]))
        if win_size % 2 == 0:
            win_size -= 1
        if win_size < 3:
            return 0.0
        return structural_similarity(a1, a2, multichannel=True, win_size=win_size)
    except:
        return 0.0


def load_ground_truth(obj_id, view_idx=0):
    """Load ground truth image for a specific object and view."""
    gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/{view_idx:03d}.png'
    if os.path.exists(gt_path):
        img = Image.open(gt_path).convert('RGBA')
        # Convert to RGB (remove alpha)
        img_rgb = Image.new('RGB', img.size, (255, 255, 255))
        img_rgb.paste(img, mask=img.split()[3])
        return img_rgb
    return None


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/eval_vs_gt'
    os.makedirs(output_dir, exist_ok=True)

    # Test objects
    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    results = []

    for obj_id in test_objects:
        print(f"\n{'='*60}")
        print(f"Evaluating: {obj_id}")
        print(f"{'='*60}")

        cond_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(cond_path):
            print(f"  Skipping: condition image not found")
            continue

        cond_img = Image.open(cond_path).convert('RGBA')

        # Load GT for view 0 (condition view)
        gt_view0 = load_ground_truth(obj_id, view_idx=0)
        if gt_view0 is None:
            print(f"  Skipping: GT not found")
            continue

        # Config A: Original
        print("  Running Original...")
        try:
            pipeline_a = load_pipeline(checkpoint_path, unet_ckpt_path)
            img_a = run_inference(pipeline_a, cond_img, seed=42)
            del pipeline_a
            torch.cuda.empty_cache()

            # Extract first view from 6-view grid (top-left)
            img_a_arr = np.array(img_a)
            h, w = img_a_arr.shape[0] // 3, img_a_arr.shape[1] // 2
            view_a = Image.fromarray(img_a_arr[:h, :w])
        except Exception as e:
            print(f"  Error: {e}")
            view_a = None

        # Config C: Working LoRA
        print("  Running attn2-only LoRA...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, working_lora_path, rank=4, alpha=1)
            img_c = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c
            torch.cuda.empty_cache()

            # Extract first view
            img_c_arr = np.array(img_c)
            h, w = img_c_arr.shape[0] // 3, img_c_arr.shape[1] // 2
            view_c = Image.fromarray(img_c_arr[:h, :w])
        except Exception as e:
            print(f"  Error: {e}")
            view_c = None

        # Compute metrics vs GT
        psnr_orig = psnr(gt_view0, view_a) if view_a else None
        psnr_lora = psnr(gt_view0, view_c) if view_c else None
        ssim_orig = ssim(gt_view0, view_a) if view_a else None
        ssim_lora = ssim(gt_view0, view_c) if view_c else None

        print(f"  PSNR Original vs GT: {psnr_orig:.2f} dB" if psnr_orig else "  PSNR Original: N/A")
        print(f"  PSNR LoRA vs GT: {psnr_lora:.2f} dB" if psnr_lora else "  PSNR LoRA: N/A")
        print(f"  SSIM Original vs GT: {ssim_orig:.4f}" if ssim_orig else "  SSIM Original: N/A")
        print(f"  SSIM LoRA vs GT: {ssim_lora:.4f}" if ssim_lora else "  SSIM LoRA: N/A")

        results.append({
            'obj_id': obj_id,
            'psnr_orig': psnr_orig,
            'psnr_lora': psnr_lora,
            'ssim_orig': ssim_orig,
            'ssim_lora': ssim_lora,
        })

    # Save results
    csv_path = os.path.join(output_dir, 'results.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['obj_id', 'psnr_orig', 'psnr_lora', 'ssim_orig', 'ssim_lora'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Generate markdown report
    md_path = os.path.join(output_dir, 'results.md')
    with open(md_path, 'w') as f:
        f.write("# Evaluation vs Ground Truth\n\n")
        f.write("| Object | PSNR_Original | PSNR_LoRA | SSIM_Original | SSIM_LoRA |\n")
        f.write("|--------|---------------|-----------|----------------|----------|\n")
        for r in results:
            psnr_o = f"{r['psnr_orig']:.2f}" if r['psnr_orig'] else "N/A"
            psnr_l = f"{r['psnr_lora']:.2f}" if r['psnr_lora'] else "N/A"
            ssim_o = f"{r['ssim_orig']:.4f}" if r['ssim_orig'] else "N/A"
            ssim_l = f"{r['ssim_lora']:.4f}" if r['ssim_lora'] else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | {psnr_o} | {psnr_l} | {ssim_o} | {ssim_l} |\n")

        # Compute averages
        psnr_orig_avg = np.mean([r['psnr_orig'] for r in results if r['psnr_orig']])
        psnr_lora_avg = np.mean([r['psnr_lora'] for r in results if r['psnr_lora']])
        ssim_orig_avg = np.mean([r['ssim_orig'] for r in results if r['ssim_orig']])
        ssim_lora_avg = np.mean([r['ssim_lora'] for r in results if r['ssim_lora']])

        f.write(f"\n## Averages\n\n")
        f.write(f"| Metric | Original | LoRA (attn2-only) |\n")
        f.write(f"|--------|----------|--------------------|\n")
        f.write(f"| PSNR | {psnr_orig_avg:.2f} dB | {psnr_lora_avg:.2f} dB |\n")
        f.write(f"| SSIM | {ssim_orig_avg:.4f} | {ssim_lora_avg:.4f} |\n")

    print(f"\nResults saved to {output_dir}")


if __name__ == '__main__':
    main()
