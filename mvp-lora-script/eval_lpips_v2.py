"""
Task A v2: LPIPS + SSIM + PSNR evaluation with truly crashed checkpoint.
Three-way comparison: Original / Crashed LoRA / Working LoRA
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
    except Exception:
        return 0.0


def compute_lpips(img1, img2, loss_fn, device='cuda'):
    t1 = torch.from_numpy(np.array(img1).astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0) * 2 - 1
    t2 = torch.from_numpy(np.array(img2).astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0) * 2 - 1
    if t1.shape != t2.shape:
        t2 = torch.nn.functional.interpolate(t2, size=t1.shape[2:], mode='bilinear', align_corners=False)
    t1, t2 = t1.to(device), t2.to(device)
    with torch.no_grad():
        dist = loss_fn(t1, t2)
    return dist.item()


# ============================================================
# Pipeline helpers
# ============================================================

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


def run_inference(pipeline, image, seed=42, num_steps=50):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(image, num_inference_steps=num_steps, output_type='pil')
    if isinstance(output, list) and len(output) >= 1:
        return output[0]
    return None


def extract_first_view(six_view_img):
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
    crash_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors'
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

    results = []

    for obj_id in test_objects:
        print(f"\n{'='*60}")
        print(f"Processing: {obj_id}")
        print(f"{'='*60}")

        gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(gt_path):
            print(f"  Skipping: GT not found")
            continue

        gt_rgba = Image.open(gt_path).convert('RGBA')
        gt_rgb = Image.new('RGB', gt_rgba.size, (255, 255, 255))
        gt_rgb.paste(gt_rgba, mask=gt_rgba.split()[3])

        cond_img = gt_rgba
        row = {'obj_id': obj_id}

        # --- Config A: Original ---
        print("  Config A: Original...")
        try:
            pipeline_a = load_pipeline(checkpoint_path, unet_ckpt_path)
            img_a_full = run_inference(pipeline_a, cond_img, seed=42)
            del pipeline_a; torch.cuda.empty_cache()

            view_a = extract_first_view(img_a_full)
            row['psnr_a'] = psnr(gt_rgb, view_a)
            row['ssim_a'] = ssim(gt_rgb, view_a)
            row['lpips_a'] = compute_lpips(gt_rgb, view_a, lpips_fn, device)
            print(f"    PSNR={row['psnr_a']:.2f}, LPIPS={row['lpips_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['psnr_a'] = row['ssim_a'] = row['lpips_a'] = None

        # --- Config B: Crashed LoRA (attn1+attn2, 500 steps, lr=5e-4) ---
        print("  Config B: Crashed LoRA...")
        try:
            pipeline_b = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet(pipeline_b.unet, crash_lora_path, rank=8, alpha=8)
            img_b_full = run_inference(pipeline_b, cond_img, seed=42)
            del pipeline_b; torch.cuda.empty_cache()

            view_b = extract_first_view(img_b_full)
            row['psnr_b'] = psnr(gt_rgb, view_b)
            row['ssim_b'] = ssim(gt_rgb, view_b)
            row['lpips_b'] = compute_lpips(gt_rgb, view_b, lpips_fn, device)
            print(f"    PSNR={row['psnr_b']:.2f}, LPIPS={row['lpips_b']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['psnr_b'] = row['ssim_b'] = row['lpips_b'] = None

        # --- Config C: Working LoRA (attn2-only, 250 steps) ---
        print("  Config C: Working LoRA...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, working_lora_path, rank=4, alpha=1)
            img_c_full = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c; torch.cuda.empty_cache()

            view_c = extract_first_view(img_c_full)
            row['psnr_c'] = psnr(gt_rgb, view_c)
            row['ssim_c'] = ssim(gt_rgb, view_c)
            row['lpips_c'] = compute_lpips(gt_rgb, view_c, lpips_fn, device)
            print(f"    PSNR={row['psnr_c']:.2f}, LPIPS={row['lpips_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['psnr_c'] = row['ssim_c'] = row['lpips_c'] = None

        results.append(row)

    # ============================================================
    # Save results
    # ============================================================

    csv_path = os.path.join(output_dir, 'eval_lpips_v2.csv')
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

    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avg_psnr_a, avg_psnr_b, avg_psnr_c = avg('psnr_a'), avg('psnr_b'), avg('psnr_c')
    avg_ssim_a, avg_ssim_b, avg_ssim_c = avg('ssim_a'), avg('ssim_b'), avg('ssim_c')
    avg_lpips_a, avg_lpips_b, avg_lpips_c = avg('lpips_a'), avg('lpips_b'), avg('lpips_c')

    md_path = os.path.join(output_dir, 'eval_lpips_v2.md')
    with open(md_path, 'w') as f:
        f.write("# LPIPS + SSIM + PSNR Evaluation vs Ground Truth (v2)\n\n")
        f.write("**Test set**: 10 objects from clean_objects.txt (last 10)\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Crashed)**: attn1+attn2 LoRA, rank=8, 500 steps, lr=5e-4 (CRASHED)\n")
        f.write("- **C (Working)**: attn2-only LoRA, rank=4, 250 steps, lr=1e-5, scale=0.25\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric   | Original (A) | Crashed LoRA (B) | Working LoRA (C) |\n")
        f.write("|----------|--------------|------------------|------------------|\n")
        f.write(f"| PSNR ↑   | {avg_psnr_a:.2f} dB    | {avg_psnr_b:.2f} dB        | {avg_psnr_c:.2f} dB        |\n")
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

        f.write("\n## Analysis\n\n")
        f.write(f"### Crashed LoRA (B)\n")
        f.write(f"- PSNR: {avg_psnr_b:.2f} dB (vs Original {avg_psnr_a:.2f} dB)\n")
        f.write(f"- LPIPS: {avg_lpips_b:.4f} (vs Original {avg_lpips_a:.4f})\n")
        if avg_psnr_b < 20:
            f.write(f"- **Confirmed catastrophic degradation**: PSNR < 20 dB\n")
        elif avg_psnr_b < 30:
            f.write(f"- **Significant degradation**: PSNR < 30 dB\n")
        else:
            f.write(f"- **Moderate degradation**: PSNR >= 30 dB\n")

        f.write(f"\n### Working LoRA (C)\n")
        f.write(f"- PSNR: {avg_psnr_c:.2f} dB (vs Original {avg_psnr_a:.2f} dB)\n")
        f.write(f"- LPIPS: {avg_lpips_c:.4f} (vs Original {avg_lpips_a:.4f})\n")
        if abs(avg_psnr_c - avg_psnr_a) < 5:
            f.write(f"- **Preserved quality**: PSNR within 5 dB of Original\n")
        else:
            f.write(f"- **Some degradation**: PSNR differs by {abs(avg_psnr_c - avg_psnr_a):.2f} dB\n")

    print(f"Report saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Metric':<10} {'Original':>12} {'Crashed':>12} {'Working':>12}")
    print(f"{'-'*46}")
    print(f"{'PSNR ↑':<10} {avg_psnr_a:>12.2f} {avg_psnr_b:>12.2f} {avg_psnr_c:>12.2f}")
    print(f"{'SSIM ↑':<10} {avg_ssim_a:>12.4f} {avg_ssim_b:>12.4f} {avg_ssim_c:>12.4f}")
    print(f"{'LPIPS ↓':<10} {avg_lpips_a:>12.4f} {avg_lpips_b:>12.4f} {avg_lpips_c:>12.4f}")


if __name__ == '__main__':
    main()
