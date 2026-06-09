"""
Task A: LPIPS + SSIM + PSNR evaluation against Ground Truth.
Three-way comparison: Original / Broken LoRA / Working LoRA
"""
import os
import sys
import csv
import torch
import lpips
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler


# ============================================================
# Metric functions
# ============================================================

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
    return 10 * np.log10(255.0 ** 2 / mse)


def ssim(img1, img2):
    """Compute SSIM between two PIL images."""
    from skimage.metrics import structural_similarity
    a1 = np.array(img1).astype(np.float64)
    a2 = np.array(img2).astype(np.float64)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size)
        a2 = np.array(img2).astype(np.float64)
    try:
        win_size = min(7, min(a1.shape[0], a1.shape[1]))
        if win_size % 2 == 0:
            win_size -= 1
        if win_size < 3:
            return 0.0
        return structural_similarity(a1, a2, channel_axis=2, win_size=win_size, data_range=255.0)
    except Exception as e:
        print(f"    SSIM error: {e}")
        return 0.0


def compute_lpips(img1, img2, loss_fn, device='cuda'):
    """Compute LPIPS between two PIL images. Lower is better."""
    # Convert PIL to tensors: [0, 1] -> [-1, 1]
    t1 = torch.from_numpy(np.array(img1).astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0) * 2 - 1
    t2 = torch.from_numpy(np.array(img2).astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0) * 2 - 1

    # Resize if needed
    if t1.shape != t2.shape:
        t2 = torch.nn.functional.interpolate(t2, size=t1.shape[2:], mode='bilinear', align_corners=False)

    t1 = t1.to(device)
    t2 = t2.to(device)

    with torch.no_grad():
        dist = loss_fn(t1, t2)

    return dist.item()


# ============================================================
# Pipeline helpers
# ============================================================

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


def extract_first_view(six_view_img):
    """Extract the first view (top-left) from 6-view grid."""
    arr = np.array(six_view_img)
    h, w = arr.shape[0] // 3, arr.shape[1] // 2
    return Image.fromarray(arr[:h, :w])


# ============================================================
# Main
# ============================================================

def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    # Checkpoint paths
    broken_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    # Test objects (all 10 from test split)
    test_objects_file = '/4T/CXY/MV-Painter/MVPainter/datalist/test_objects.txt'
    with open(test_objects_file) as f:
        test_objects = [line.strip() for line in f if line.strip()]

    print(f"Test objects: {len(test_objects)}")

    # Initialize LPIPS
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    lpips_fn = lpips.LPIPS(net='alex').to(device)
    print(f"LPIPS initialized on {device}")

    # Results storage
    results = []

    for obj_id in test_objects:
        print(f"\n{'='*60}")
        print(f"Processing: {obj_id}")
        print(f"{'='*60}")

        # Load GT image (view 0)
        gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(gt_path):
            print(f"  Skipping: GT not found")
            continue

        gt_rgba = Image.open(gt_path).convert('RGBA')
        gt_rgb = Image.new('RGB', gt_rgba.size, (255, 255, 255))
        gt_rgb.paste(gt_rgba, mask=gt_rgba.split()[3])

        # Load condition image
        cond_img = gt_rgba  # RGBA for pipeline input

        row = {'obj_id': obj_id}

        # --- Config A: Original ---
        print("  Config A: Original...")
        try:
            pipeline_a = load_pipeline(checkpoint_path, unet_ckpt_path)
            img_a_full = run_inference(pipeline_a, cond_img, seed=42)
            del pipeline_a
            torch.cuda.empty_cache()

            view_a = extract_first_view(img_a_full)
            row['psnr_a'] = psnr(gt_rgb, view_a)
            row['ssim_a'] = ssim(gt_rgb, view_a)
            row['lpips_a'] = compute_lpips(gt_rgb, view_a, lpips_fn, device)
            print(f"    PSNR={row['psnr_a']:.2f}, SSIM={row['ssim_a']:.4f}, LPIPS={row['lpips_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['psnr_a'] = row['ssim_a'] = row['lpips_a'] = None

        # --- Config B: Broken LoRA (attn1+attn2) ---
        print("  Config B: Broken LoRA (attn1+attn2)...")
        if os.path.exists(broken_lora_path):
            try:
                pipeline_b = load_pipeline(checkpoint_path, unet_ckpt_path)
                merge_lora_into_unet(pipeline_b.unet, broken_lora_path, rank=4, alpha=4)
                img_b_full = run_inference(pipeline_b, cond_img, seed=42)
                del pipeline_b
                torch.cuda.empty_cache()

                view_b = extract_first_view(img_b_full)
                row['psnr_b'] = psnr(gt_rgb, view_b)
                row['ssim_b'] = ssim(gt_rgb, view_b)
                row['lpips_b'] = compute_lpips(gt_rgb, view_b, lpips_fn, device)
                print(f"    PSNR={row['psnr_b']:.2f}, SSIM={row['ssim_b']:.4f}, LPIPS={row['lpips_b']:.4f}")
            except Exception as e:
                print(f"    Error: {e}")
                row['psnr_b'] = row['ssim_b'] = row['lpips_b'] = None
        else:
            print(f"    Skipping: checkpoint not found")
            row['psnr_b'] = row['ssim_b'] = row['lpips_b'] = None

        # --- Config C: Working LoRA (attn2-only, scale=0.25) ---
        print("  Config C: Working LoRA (attn2-only)...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, working_lora_path, rank=4, alpha=1)
            img_c_full = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c
            torch.cuda.empty_cache()

            view_c = extract_first_view(img_c_full)
            row['psnr_c'] = psnr(gt_rgb, view_c)
            row['ssim_c'] = ssim(gt_rgb, view_c)
            row['lpips_c'] = compute_lpips(gt_rgb, view_c, lpips_fn, device)
            print(f"    PSNR={row['psnr_c']:.2f}, SSIM={row['ssim_c']:.4f}, LPIPS={row['lpips_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['psnr_c'] = row['ssim_c'] = row['lpips_c'] = None

        results.append(row)

    # ============================================================
    # Save results
    # ============================================================

    # CSV
    csv_path = os.path.join(output_dir, 'eval_lpips.csv')
    fieldnames = ['obj_id',
                  'psnr_a', 'ssim_a', 'lpips_a',
                  'psnr_b', 'ssim_b', 'lpips_b',
                  'psnr_c', 'ssim_c', 'lpips_c']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"\nCSV saved to {csv_path}")

    # Compute averages
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avg_psnr_a = avg('psnr_a')
    avg_psnr_b = avg('psnr_b')
    avg_psnr_c = avg('psnr_c')
    avg_ssim_a = avg('ssim_a')
    avg_ssim_b = avg('ssim_b')
    avg_ssim_c = avg('ssim_c')
    avg_lpips_a = avg('lpips_a')
    avg_lpips_b = avg('lpips_b')
    avg_lpips_c = avg('lpips_c')

    # Markdown report
    md_path = os.path.join(output_dir, 'eval_lpips.md')
    with open(md_path, 'w') as f:
        f.write("# LPIPS + SSIM + PSNR Evaluation vs Ground Truth\n\n")
        f.write("**Test set**: 10 objects from clean_objects.txt (last 10)\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Broken)**: attn1+attn2 LoRA, rank=4, 100 steps, lr=1e-4\n")
        f.write("- **C (Working)**: attn2-only LoRA, rank=4, 250 steps, lr=1e-5, scale=0.25\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric   | Original (A) | Broken LoRA (B) | Working LoRA (C) |\n")
        f.write("|----------|--------------|-----------------|------------------|\n")
        f.write(f"| PSNR ↑   | {avg_psnr_a:.2f} dB    | {avg_psnr_b:.2f} dB       | {avg_psnr_c:.2f} dB        |\n")
        f.write(f"| SSIM ↑   | {avg_ssim_a:.4f}      | {avg_ssim_b:.4f}        | {avg_ssim_c:.4f}         |\n")
        f.write(f"| LPIPS ↓  | {avg_lpips_a:.4f}       | {avg_lpips_b:.4f}        | {avg_lpips_c:.4f}         |\n")

        f.write("\n## Per-Object Results\n\n")
        f.write("| Object | PSNR_A | PSNR_B | PSNR_C | SSIM_A | SSIM_B | SSIM_C | LPIPS_A | LPIPS_B | LPIPS_C |\n")
        f.write("|--------|--------|--------|--------|--------|--------|--------|---------|---------|--------|\n")
        for r in results:
            def fmt(key, prec=2):
                v = r.get(key)
                return f"{v:.{prec}f}" if v is not None else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | "
                    f"{fmt('psnr_a')} | {fmt('psnr_b')} | {fmt('psnr_c')} | "
                    f"{fmt('ssim_a', 4)} | {fmt('ssim_b', 4)} | {fmt('ssim_c', 4)} | "
                    f"{fmt('lpips_a', 4)} | {fmt('lpips_b', 4)} | {fmt('lpips_c', 4)} |\n")

        f.write("\n## Interpretation\n\n")
        f.write("- **PSNR**: Higher is better. Measures pixel-level similarity.\n")
        f.write("- **SSIM**: Higher is better (max 1.0). Measures structural similarity.\n")
        f.write("- **LPIPS**: Lower is better (min 0.0). Measures perceptual similarity.\n\n")

        # Analysis
        f.write("## Analysis\n\n")
        if avg_lpips_b > avg_lpips_a * 1.5:
            f.write(f"✅ **Broken LoRA LPIPS is significantly worse** ({avg_lpips_b:.4f} vs {avg_lpips_a:.4f}), ")
            f.write(f"confirming perceptual degradation from attn1+attn2 LoRA.\n\n")
        else:
            f.write(f"⚠️ **Broken LoRA LPIPS difference is small** ({avg_lpips_b:.4f} vs {avg_lpips_a:.4f}). ")
            f.write(f"100 steps may not be enough to show perceptual degradation.\n\n")

        if abs(avg_lpips_c - avg_lpips_a) < 0.05:
            f.write(f"✅ **Working LoRA LPIPS is close to Original** ({avg_lpips_c:.4f} vs {avg_lpips_a:.4f}), ")
            f.write(f"confirming attn2-only LoRA preserves perceptual quality.\n\n")
        else:
            f.write(f"⚠️ **Working LoRA LPIPS differs from Original** ({avg_lpips_c:.4f} vs {avg_lpips_a:.4f}). ")
            f.write(f"May need scale adjustment.\n")

    print(f"Report saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Metric':<10} {'Original':>12} {'Broken':>12} {'Working':>12}")
    print(f"{'-'*46}")
    print(f"{'PSNR ↑':<10} {avg_psnr_a:>12.2f} {avg_psnr_b:>12.2f} {avg_psnr_c:>12.2f}")
    print(f"{'SSIM ↑':<10} {avg_ssim_a:>12.4f} {avg_ssim_b:>12.4f} {avg_ssim_c:>12.4f}")
    print(f"{'LPIPS ↓':<10} {avg_lpips_a:>12.4f} {avg_lpips_b:>12.4f} {avg_lpips_c:>12.4f}")


if __name__ == '__main__':
    main()
