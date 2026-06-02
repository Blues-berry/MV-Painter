"""
CLIP evaluation using CPU (no GPU required).
Uses existing images from three_way_comparison directory.
"""
import os
import sys
import csv
import torch
import numpy as np
from PIL import Image

# Use open_clip which works on CPU
try:
    import open_clip
    USE_OPEN_CLIP = True
    print("Using open_clip")
except ImportError:
    from transformers import CLIPModel, CLIPProcessor
    USE_OPEN_CLIP = False
    print("Using transformers CLIP")


def compute_clip_similarity_openclip(img1, img2, model, preprocess):
    """Compute CLIP similarity using open_clip."""
    t1 = preprocess(img1).unsqueeze(0)
    t2 = preprocess(img2).unsqueeze(0)

    with torch.no_grad():
        f1 = model.encode_image(t1)
        f2 = model.encode_image(t2)

    # Normalize
    f1 = f1 / f1.norm(dim=-1, keepdim=True)
    f2 = f2 / f2.norm(dim=-1, keepdim=True)

    return (f1 * f2).sum(dim=-1).item()


def compute_clip_similarity_transformers(img1, img2, model, processor):
    """Compute CLIP similarity using transformers."""
    inputs1 = processor(images=img1, return_tensors="pt")
    inputs2 = processor(images=img2, return_tensors="pt")

    with torch.no_grad():
        features1 = model.get_image_features(**inputs1)
        features2 = model.get_image_features(**inputs2)

    features1 = features1 / features1.norm(dim=-1, keepdim=True)
    features2 = features2 / features2.norm(dim=-1, keepdim=True)

    return (features1 * features2).sum(dim=-1).item()


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/paper_assets'
    os.makedirs(output_dir, exist_ok=True)

    base_dir = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison'

    # Test objects
    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
        'b23ec9725c48494788d1d88104acbb4a',
        'c630e3959eab49ae87cdad42937e21b2',
    ]

    # Load CLIP model
    print("Loading CLIP model on CPU...")
    if USE_OPEN_CLIP:
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        model.eval()
        compute_fn = lambda i1, i2: compute_clip_similarity_openclip(i1, i2, model, preprocess)
    else:
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        compute_fn = lambda i1, i2: compute_clip_similarity_transformers(i1, i2, clip_model, clip_processor)

    print("CLIP model loaded")

    results = []

    for obj_id in test_objects:
        print(f"\nProcessing: {obj_id[:20]}...")

        gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        orig_path = f'{base_dir}/{obj_id}_original.png'
        broken_path = f'{base_dir}/{obj_id}_broken.png'
        working_path = f'{base_dir}/{obj_id}_attn2only.png'

        if not all(os.path.exists(p) for p in [gt_path, orig_path, broken_path, working_path]):
            print(f"  Skipping: files not found")
            continue

        gt = Image.open(gt_path).convert('RGB')
        orig = Image.open(orig_path).convert('RGB')
        broken = Image.open(broken_path).convert('RGB')
        working = Image.open(working_path).convert('RGB')

        clip_a = compute_fn(gt, orig)
        clip_b = compute_fn(gt, broken)
        clip_c = compute_fn(gt, working)

        print(f"  CLIP Sim: A={clip_a:.4f}, B={clip_b:.4f}, C={clip_c:.4f}")
        results.append({
            'obj_id': obj_id,
            'clip_a': clip_a,
            'clip_b': clip_b,
            'clip_c': clip_c,
        })

    # Save CSV
    csv_path = os.path.join(output_dir, 'eval_reference_consistency.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['obj_id', 'clip_a', 'clip_b', 'clip_c'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Compute averages
    def avg(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return np.mean(vals) if vals else float('nan')

    avg_a = avg('clip_a')
    avg_b = avg('clip_b')
    avg_c = avg('clip_c')

    # Generate markdown report
    md_path = os.path.join(output_dir, 'eval_reference_consistency.md')
    with open(md_path, 'w') as f:
        f.write("# Reference Consistency Evaluation\n\n")
        f.write("**Metric**: CLIP Similarity (vs Ground Truth)\n\n")
        f.write("**Configurations**:\n")
        f.write("- **A (Original)**: Base model, no LoRA\n")
        f.write("- **B (Full LoRA)**: attn1+attn2 LoRA, rank=8, 500 steps, lr=5e-4\n")
        f.write("- **C (attn2-only LoRA)**: attn2-only LoRA, rank=4, 250 steps, lr=1e-5\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Metric | Original (A) | Full LoRA (B) | attn2-only LoRA (C) |\n")
        f.write("|--------|--------------|---------------|---------------------|\n")
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
        f.write(f"- **Full LoRA CLIP Sim**: {avg_b:.4f} (diff: {avg_b - avg_a:+.4f})\n")
        f.write(f"- **attn2-only LoRA CLIP Sim**: {avg_c:.4f} (diff: {avg_c - avg_a:+.4f})\n\n")

        if avg_c > avg_b:
            f.write("**attn2-only LoRA preserves reference consistency better than Full LoRA.**\n")
        else:
            f.write("**Both LoRA approaches maintain similar reference consistency.**\n")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Metric':<15} {'Original':>12} {'Full LoRA':>12} {'attn2-only':>12}")
    print(f"{'-'*51}")
    print(f"{'CLIP Sim ↑':<15} {avg_a:>12.4f} {avg_b:>12.4f} {avg_c:>12.4f}")
    print(f"\nReport saved to {md_path}")


if __name__ == '__main__':
    main()
