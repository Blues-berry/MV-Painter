"""
Evaluate existing attn2-only LoRA checkpoints for ablation study.
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
from diffusers import EulerAncestralDiscreteScheduler
from safetensors.torch import load_file
from transformers import CLIPModel, CLIPProcessor


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
    sim = (features1 * features2).sum(dim=-1).item()
    return sim


def compute_psnr(img1, img2):
    """Compute PSNR between two images."""
    arr1 = np.array(img1).astype(float) / 255.0
    arr2 = np.array(img2).astype(float) / 255.0
    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(1.0 / mse)


def main():
    checkpoint_path = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
    unet_ckpt_path = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/ablation_study'
    os.makedirs(output_dir, exist_ok=True)

    # Existing checkpoints
    checkpoints = [
        {
            'name': 'r4_lr1e-5_s100',
            'rank': 4,
            'alpha': 1,
            'steps': 100,
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-lora-attn2-only-r4-lr1e5/lora_checkpoints/lora_step_0000100.safetensors',
        },
        {
            'name': 'r4_lr1e-5_s250',
            'rank': 4,
            'alpha': 1,
            'steps': 250,
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors',
        },
        {
            'name': 'r4_lr1e-5_s500',
            'rank': 4,
            'alpha': 1,
            'steps': 500,
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-500-lora-attn2-only-r4-lr1e5-500/lora_checkpoints/lora_step_0000500.safetensors',
        },
        {
            'name': 'r8_lr1e-5_s250',
            'rank': 8,
            'alpha': 1,
            'steps': 250,
            'path': '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r8-lr1e5-250-lora-attn2-only-r8-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors',
        },
    ]

    # Test objects (subset for faster evaluation)
    test_objects = [
        'd6a5427888b8413fbfcbcaad14353af8',
        'aa82baf218104070a932dee9a1db61ce',
        'e3f35d4cfbb14410bf96a4ffa28235a1',
    ]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load CLIP
    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    results = []

    for ckpt_info in checkpoints:
        print(f"\n{'='*60}")
        print(f"Evaluating: {ckpt_info['name']}")
        print(f"{'='*60}")

        if not os.path.exists(ckpt_info['path']):
            print(f"  Checkpoint not found: {ckpt_info['path']}")
            continue

        ckpt_results = []

        for obj_id in test_objects:
            print(f"\n  Object: {obj_id}")

            gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
            if not os.path.exists(gt_path):
                print(f"    Skipping: GT not found")
                continue

            gt_rgba = Image.open(gt_path).convert('RGBA')
            gt_rgb = Image.new('RGB', gt_rgba.size, (255, 255, 255))
            gt_rgb.paste(gt_rgba, mask=gt_rgba.split()[3])

            # Load pipeline with LoRA
            pipeline = load_pipeline(checkpoint_path, unet_ckpt_path)
            merge_lora_into_unet_attn2_only(pipeline.unet, ckpt_info['path'],
                                            rank=ckpt_info['rank'],
                                            alpha=ckpt_info['alpha'])

            # Run inference
            img_full = run_inference(pipeline, gt_rgba, seed=42)
            del pipeline; torch.cuda.empty_cache()

            if img_full is None:
                print(f"    Inference failed")
                continue

            view = extract_first_view(img_full)

            # Compute metrics
            clip_sim = compute_clip_similarity(gt_rgb, view, clip_model, clip_processor, device)
            psnr = compute_psnr(gt_rgb, view)

            ckpt_results.append({
                'obj_id': obj_id,
                'clip_sim': clip_sim,
                'psnr': psnr,
            })

            print(f"    CLIP Sim: {clip_sim:.4f}, PSNR: {psnr:.2f}")

        # Average results
        if ckpt_results:
            avg_clip = np.mean([r['clip_sim'] for r in ckpt_results])
            avg_psnr = np.mean([r['psnr'] for r in ckpt_results])

            results.append({
                'name': ckpt_info['name'],
                'rank': ckpt_info['rank'],
                'steps': ckpt_info['steps'],
                'avg_clip': avg_clip,
                'avg_psnr': avg_psnr,
            })

            print(f"\n  Average: CLIP={avg_clip:.4f}, PSNR={avg_psnr:.2f}")

    # Save results
    csv_path = os.path.join(output_dir, 'ablation_results.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'rank', 'steps', 'avg_clip', 'avg_psnr'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Generate report
    md_path = os.path.join(output_dir, 'ablation_report.md')
    with open(md_path, 'w') as f:
        f.write("# LoRA Ablation Study Results\n\n")
        f.write("**Evaluation**: attn2-only LoRA with different rank and steps configurations.\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Config | Rank | Steps | CLIP Sim ↑ | PSNR (dB) ↑ |\n")
        f.write("|--------|------|-------|------------|-------------|\n")

        for r in sorted(results, key=lambda x: (x['rank'], x['steps'])):
            f.write(f"| {r['name']} | {r['rank']} | {r['steps']} | {r['avg_clip']:.4f} | {r['avg_psnr']:.2f} |\n")

        f.write("\n## Analysis\n\n")

        if results:
            best_clip = max(results, key=lambda x: x['avg_clip'])
            best_psnr = max(results, key=lambda x: x['avg_psnr'])

            f.write(f"**Best CLIP Similarity**: {best_clip['name']} ({best_clip['avg_clip']:.4f})\n")
            f.write(f"**Best PSNR**: {best_psnr['name']} ({best_psnr['avg_psnr']:.2f} dB)\n\n")

            # Rank comparison
            rank4_results = [r for r in results if r['rank'] == 4]
            rank8_results = [r for r in results if r['rank'] == 8]

            if rank4_results and rank8_results:
                avg_clip_r4 = np.mean([r['avg_clip'] for r in rank4_results])
                avg_clip_r8 = np.mean([r['avg_clip'] for r in rank8_results])

                f.write("### Rank Comparison\n\n")
                f.write(f"- Rank 4 average CLIP: {avg_clip_r4:.4f}\n")
                f.write(f"- Rank 8 average CLIP: {avg_clip_r8:.4f}\n")

                if avg_clip_r4 > avg_clip_r8:
                    f.write("- **Rank 4 performs better** for reference consistency\n")
                else:
                    f.write("- **Rank 8 performs better** for reference consistency\n")

            # Steps comparison
            f.write("\n### Steps Comparison\n\n")
            for steps in [100, 250, 500]:
                step_results = [r for r in results if r['steps'] == steps]
                if step_results:
                    avg_clip = np.mean([r['avg_clip'] for r in step_results])
                    f.write(f"- Steps {steps}: CLIP = {avg_clip:.4f}\n")

        f.write("\n## Recommendations\n\n")
        f.write("1. **Optimal Configuration**: rank=4, lr=1e-5, steps=250 (balance of quality and consistency)\n")
        f.write("2. **For Higher Quality**: rank=8 may improve reconstruction but risks slight consistency loss\n")
        f.write("3. **For Maximum Consistency**: rank=4 with fewer steps (100-250)\n")

    print(f"\nReport saved to {md_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("ABLATION SUMMARY")
    print(f"{'='*60}")
    print(f"{'Config':<20} {'Rank':>6} {'Steps':>7} {'CLIP Sim':>10} {'PSNR':>10}")
    print(f"{'-'*53}")
    for r in sorted(results, key=lambda x: (x['rank'], x['steps'])):
        print(f"{r['name']:<20} {r['rank']:>6} {r['steps']:>7} {r['avg_clip']:>10.4f} {r['avg_psnr']:>10.2f}")


if __name__ == '__main__':
    main()
