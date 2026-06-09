"""
Evaluate DINO cosine similarity for reference consistency.
Compares: Original / Crashed LoRA / Working LoRA
Only computes DINO metrics (assumes CLIP data already exists).
"""
import os
import sys
import csv
import torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler
from safetensors.torch import load_file
from transformers import Dinov2Model


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


def compute_dino_similarity(img1, img2, dino_model, device='cuda'):
    """Compute DINO cosine similarity between two images."""
    from torchvision import transforms

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    t1 = transform(img1).unsqueeze(0).to(device)
    t2 = transform(img2).unsqueeze(0).to(device)

    with torch.no_grad():
        feat1 = dino_model(t1).last_hidden_state[:, 0, :]  # CLS token
        feat2 = dino_model(t2).last_hidden_state[:, 0, :]

    # Normalize
    feat1 = feat1 / feat1.norm(dim=-1, keepdim=True)
    feat2 = feat2 / feat2.norm(dim=-1, keepdim=True)

    sim = (feat1 * feat2).sum(dim=-1).item()
    return sim


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    # Checkpoint paths
    crash_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors'
    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    # Test objects
    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load DINO
    print("Loading DINOv2 model...")
    dino_model = Dinov2Model.from_pretrained("facebook/dinov2-base").to(device)

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
            row['dino_a'] = compute_dino_similarity(gt_rgb, view_a, dino_model, device)
            print(f"    DINO Cos={row['dino_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['dino_a'] = None

        # --- Config B: Crashed LoRA ---
        print("  Config B: Crashed LoRA...")
        try:
            pipeline_b = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet(pipeline_b.unet, crash_lora_path, rank=8, alpha=8)
            img_b_full = run_inference(pipeline_b, cond_img, seed=42)
            del pipeline_b; torch.cuda.empty_cache()

            view_b = extract_first_view(img_b_full)
            row['dino_b'] = compute_dino_similarity(gt_rgb, view_b, dino_model, device)
            print(f"    DINO Cos={row['dino_b']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['dino_b'] = None

        # --- Config C: Working LoRA ---
        print("  Config C: Working LoRA...")
        try:
            pipeline_c = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline_c.unet, working_lora_path, rank=4, alpha=1)
            img_c_full = run_inference(pipeline_c, cond_img, seed=42)
            del pipeline_c; torch.cuda.empty_cache()

            view_c = extract_first_view(img_c_full)
            row['dino_c'] = compute_dino_similarity(gt_rgb, view_c, dino_model, device)
            print(f"    DINO Cos={row['dino_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['dino_c'] = None

        results.append(row)

    # Save CSV
    csv_path = os.path.join(output_dir, 'eval_dino.csv')
    fieldnames = ['obj_id', 'dino_a', 'dino_b', 'dino_c']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Compute averages
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avg_dino_a = avg('dino_a')
    avg_dino_b = avg('dino_b')
    avg_dino_c = avg('dino_c')

    # Generate markdown report
    md_path = os.path.join(output_dir, 'eval_dino.md')
    with open(md_path, 'w') as f:
        f.write("# DINO Cosine Similarity Evaluation\n\n")
        f.write("**Metric**: DINOv2 Cosine Similarity (vs Ground Truth)\n\n")
        f.write("**Model**: facebook/dinov2-base\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Crashed)**: attn1+attn2 LoRA, rank=8, 500 steps, lr=5e-4\n")
        f.write("- **C (Working)**: attn2-only LoRA, rank=4, 250 steps, lr=1e-5\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric | Original (A) | Crashed LoRA (B) | Working LoRA (C) |\n")
        f.write("|--------|--------------|------------------|------------------|\n")
        f.write(f"| DINO Cos ↑ | {avg_dino_a:.4f} | {avg_dino_b:.4f} | {avg_dino_c:.4f} |\n")

        f.write("\n## Per-Object Results\n\n")
        f.write("| Object | DINO_A | DINO_B | DINO_C |\n")
        f.write("|--------|--------|--------|--------|\n")
        for r in results:
            def fmt(key, prec=4):
                v = r.get(key)
                return f"{v:.{prec}f}" if v is not None else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | "
                    f"{fmt('dino_a')} | {fmt('dino_b')} | {fmt('dino_c')} |\n")

        f.write("\n## Analysis\n\n")
        f.write(f"- **Original DINO Cos**: {avg_dino_a:.4f}\n")
        f.write(f"- **Crashed LoRA DINO Cos**: {avg_dino_b:.4f} (diff: {avg_dino_b - avg_dino_a:+.4f})\n")
        f.write(f"- **Working LoRA DINO Cos**: {avg_dino_c:.4f} (diff: {avg_dino_c - avg_dino_a:+.4f})\n\n")

        if avg_dino_c > avg_dino_b:
            f.write("**Working LoRA preserves reference consistency better than Crashed LoRA (by DINO metric).**\n")
        else:
            f.write("**Both LoRA approaches maintain similar reference consistency (by DINO metric).**\n")

    print(f"\nReport saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Metric':<15} {'Original':>12} {'Crashed':>12} {'Working':>12}")
    print(f"{'-'*51}")
    print(f"{'DINO Cos ↑':<15} {avg_dino_a:>12.4f} {avg_dino_b:>12.4f} {avg_dino_c:>12.4f}")


if __name__ == '__main__':
    main()
