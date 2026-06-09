"""
Evaluate CLIP similarity for three configurations.
"""
import os
import sys
import csv
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file
from transformers import CLIPModel, CLIPProcessor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler


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


def compute_clip_similarity(img1, img2, clip_model, clip_processor, device='cuda'):
    inputs1 = clip_processor(images=img1, return_tensors="pt").to(device)
    inputs2 = clip_processor(images=img2, return_tensors="pt").to(device)
    with torch.no_grad():
        features1 = clip_model.get_image_features(**inputs1)
        features2 = clip_model.get_image_features(**inputs2)
    features1 = features1 / features1.norm(dim=-1, keepdim=True)
    features2 = features2 / features2.norm(dim=-1, keepdim=True)
    return (features1 * features2).sum(dim=-1).item()


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    crash_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors'
    working_lora_path = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    results = []

    for obj_id in test_objects:
        print(f"\nProcessing: {obj_id[:20]}...")

        gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        if not os.path.exists(gt_path):
            print(f"  Skipping: GT not found")
            continue

        gt_rgba = Image.open(gt_path).convert('RGBA')
        gt_rgb = Image.new('RGB', gt_rgba.size, (255, 255, 255))
        gt_rgb.paste(gt_rgba, mask=gt_rgba.split()[3])

        row = {'obj_id': obj_id}

        # Config A: Original
        print("  A: Original...")
        try:
            p = load_pipeline(checkpoint_path, unet_ckpt_path)
            img = run_inference(p, gt_rgba, seed=42)
            del p; torch.cuda.empty_cache()
            view = extract_first_view(img)
            row['clip_a'] = compute_clip_similarity(gt_rgb, view, clip_model, clip_processor, device)
            print(f"    CLIP={row['clip_a']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_a'] = None

        # Config B: Crashed LoRA
        print("  B: Crashed LoRA...")
        try:
            p = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet(p.unet, crash_lora_path, rank=8, alpha=8)
            img = run_inference(p, gt_rgba, seed=42)
            del p; torch.cuda.empty_cache()
            view = extract_first_view(img)
            row['clip_b'] = compute_clip_similarity(gt_rgb, view, clip_model, clip_processor, device)
            print(f"    CLIP={row['clip_b']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_b'] = None

        # Config C: Working LoRA
        print("  C: Working LoRA...")
        try:
            p = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(p.unet, working_lora_path, rank=4, alpha=1)
            img = run_inference(p, gt_rgba, seed=42)
            del p; torch.cuda.empty_cache()
            view = extract_first_view(img)
            row['clip_c'] = compute_clip_similarity(gt_rgb, view, clip_model, clip_processor, device)
            print(f"    CLIP={row['clip_c']:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
            row['clip_c'] = None

        results.append(row)

    # Save results
    csv_path = os.path.join(output_dir, 'eval_reference_consistency.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['obj_id', 'clip_a', 'clip_b', 'clip_c'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Generate markdown
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avg_a = avg('clip_a')
    avg_b = avg('clip_b')
    avg_c = avg('clip_c')

    md_path = os.path.join(output_dir, 'eval_reference_consistency.md')
    with open(md_path, 'w') as f:
        f.write("# Reference Consistency Evaluation\n\n")
        f.write("**Metric**: CLIP Similarity (vs Ground Truth)\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Crashed)**: attn1+attn2 LoRA, rank=8, 500 steps, lr=5e-4\n")
        f.write("- **C (Working)**: attn2-only LoRA, rank=4, 250 steps, lr=1e-5\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric | Original (A) | Crashed LoRA (B) | Working LoRA (C) |\n")
        f.write("|--------|--------------|------------------|------------------|\n")
        f.write(f"| CLIP Sim ↑ | {avg_a:.4f} | {avg_b:.4f} | {avg_c:.4f} |\n")

        f.write("\n## Per-Object Results\n\n")
        f.write("| Object | CLIP_A | CLIP_B | CLIP_C |\n")
        f.write("|--------|--------|--------|--------|\n")
        for r in results:
            def fmt(key):
                v = r.get(key)
                return f"{v:.4f}" if v is not None else "N/A"
            f.write(f"| {r['obj_id'][:16]}... | {fmt('clip_a')} | {fmt('clip_b')} | {fmt('clip_c')} |\n")

        f.write("\n## Analysis\n\n")
        f.write(f"- **Original CLIP Sim**: {avg_a:.4f}\n")
        f.write(f"- **Crashed LoRA CLIP Sim**: {avg_b:.4f} (diff: {avg_b - avg_a:+.4f})\n")
        f.write(f"- **Working LoRA CLIP Sim**: {avg_c:.4f} (diff: {avg_c - avg_a:+.4f})\n\n")

        if avg_c > avg_b:
            f.write("**Working LoRA preserves reference consistency better than Crashed LoRA.**\n")
        else:
            f.write("**Both LoRA approaches maintain similar reference consistency.**\n")

    print(f"\nReport saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Metric':<15} {'Original':>12} {'Crashed':>12} {'Working':>12}")
    print(f"{'-'*51}")
    print(f"{'CLIP Sim ↑':<15} {avg_a:>12.4f} {avg_b:>12.4f} {avg_c:>12.4f}")


if __name__ == '__main__':
    main()
