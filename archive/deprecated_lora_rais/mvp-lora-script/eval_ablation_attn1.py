"""
Evaluate attn1-only LoRA ablation checkpoint.
Computes: PSNR vs Original, PSNR vs GT, CLIP Sim, DINO Cos, Reference Feature Cosine Similarity.
Usage: python eval_ablation_attn1.py --lora_path <path_to_lora_weights> --output_dir <output_dir>
"""
import argparse
import os
import sys
import json
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from safetensors.torch import load_file

# Add MVPainter to path
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')

from diffusers import EulerAncestralDiscreteScheduler
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
from mvpainter.lora_utils_attn1 import create_lora_processors_attn1_only
from torchvision.transforms import v2
from einops import rearrange

import clip
from transformers import AutoModel, AutoImageProcessor


def load_pipeline(lora_path=None, device='cuda:0'):
    """Load MV-Painter pipeline, optionally with attn1-only LoRA weights."""
    pipeline = MVPainter_Pipeline.from_pretrained(
        '/4T/CXY/MV-Painter/checkpoints/hf_repo',
        use_safetensors=True,
    ).to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    if lora_path:
        # Create attn1-only LoRA processors
        lora_processors = create_lora_processors_attn1_only(
            pipeline.unet, rank=4, network_alpha=4,
        )
        pipeline.unet.set_attn_processor(lora_processors)

        # Load LoRA weights
        lora_state = load_file(lora_path)
        # Apply weights to processors
        for name, proc in pipeline.unet.attn_processors.items():
            if 'attn1' not in name:
                continue
            from mvpainter.mvpainter_pipeline import ReferenceOnlyAttnProc
            if not isinstance(proc, ReferenceOnlyAttnProc):
                continue
            lora_proc = proc.chained_proc
            prefix = name.replace('.processor', '').replace('.', '_')
            for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
                if hasattr(lora_proc, param_name):
                    lora_layer = getattr(lora_proc, param_name)
                    down_key = f'{prefix}_{param_name}_down'
                    up_key = f'{prefix}_{param_name}_up'
                    if down_key in lora_state and up_key in lora_state:
                        lora_layer.down.weight.data = lora_state[down_key]
                        lora_layer.up.weight.data = lora_state[up_key]

        print(f"Loaded attn1-only LoRA weights from {lora_path}")

    return pipeline


def generate_views(pipeline, cond_image, device='cuda:0'):
    """Generate 6 views from a condition image."""
    if isinstance(cond_image, str):
        cond_image = Image.open(cond_image).convert('RGB')

    output = pipeline(cond_image, num_inference_steps=75, output_type='latent')
    latent = output.images
    image = pipeline.vae.decode(latent / pipeline.vae.config.scaling_factor, return_dict=False)[0]
    image = (image * 0.5 + 0.5).clamp(0, 1)
    return image


def compute_psnr(img1, img2):
    """Compute PSNR between two images (torch tensors, [0,1] range)."""
    mse = torch.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * torch.log10(1.0 / mse).item()


def compute_clip_similarity(images, ref_image, clip_model, clip_preprocess, device):
    """Compute CLIP similarity between generated views and reference image."""
    with torch.no_grad():
        # Process reference image
        if isinstance(ref_image, str):
            ref_pil = Image.open(ref_image).convert('RGB')
        else:
            ref_pil = v2.functional.to_pil_image(ref_image)
        ref_input = clip_preprocess(ref_pil).unsqueeze(0).to(device)
        ref_features = clip_model.encode_image(ref_input)
        ref_features = ref_features / ref_features.norm(dim=-1, keepdim=True)

        # Process generated images
        similarities = []
        for i in range(images.shape[0]):
            gen_pil = v2.functional.to_pil_image(images[i])
            gen_input = clip_preprocess(gen_pil).unsqueeze(0).to(device)
            gen_features = clip_model.encode_image(gen_input)
            gen_features = gen_features / gen_features.norm(dim=-1, keepdim=True)
            sim = (ref_features @ gen_features.T).item()
            similarities.append(sim)

    return np.mean(similarities)


def compute_dino_similarity(images, ref_image, dino_model, dino_processor, device):
    """Compute DINO cosine similarity between generated views and reference image."""
    with torch.no_grad():
        # Process reference image
        if isinstance(ref_image, str):
            ref_pil = Image.open(ref_image).convert('RGB')
        else:
            ref_pil = v2.functional.to_pil_image(ref_image)
        ref_input = dino_processor(ref_pil, return_tensors='pt').to(device)
        ref_features = dino_model(**ref_input).last_hidden_state[:, 0, :]
        ref_features = ref_features / ref_features.norm(dim=-1, keepdim=True)

        # Process generated images
        similarities = []
        for i in range(images.shape[0]):
            gen_pil = v2.functional.to_pil_image(images[i])
            gen_input = dino_processor(gen_pil, return_tensors='pt').to(device)
            gen_features = dino_model(**gen_input).last_hidden_state[:, 0, :]
            gen_features = gen_features / gen_features.norm(dim=-1, keepdim=True)
            sim = (ref_features @ gen_features.T).item()
            similarities.append(sim)

    return np.mean(similarities)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lora_path', type=str, required=True, help='Path to attn1-only LoRA weights')
    parser.add_argument('--output_dir', type=str, default='/4T/CXY/MV-Painter/mvpoutput/ablation_attn1')
    parser.add_argument('--test_dir', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--test_meta', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full/test_meta.json')
    parser.add_argument('--num_objects', type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = 'cuda:0'

    # Load models
    print("Loading models...")
    pipeline_orig = load_pipeline(lora_path=None, device=device)
    pipeline_attn1 = load_pipeline(lora_path=args.lora_path, device=device)

    # Load CLIP
    clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)

    # Load DINO
    dino_model = AutoModel.from_pretrained('facebook/dino-vits8').to(device)
    dino_processor = AutoImageProcessor.from_pretrained('facebook/dino-vits8')

    # Load test objects
    with open(args.test_meta, 'r') as f:
        test_meta = json.load(f)

    test_objects = list(test_meta.keys())[:args.num_objects]
    print(f"Evaluating on {len(test_objects)} objects")

    results = {
        'psnr_vs_orig': [],
        'psnr_vs_gt': [],
        'clip_sim': [],
        'dino_cos': [],
    }

    for obj_name in tqdm(test_objects, desc="Evaluating"):
        obj_dir = os.path.join(args.test_dir, obj_name)
        cond_image_path = os.path.join(obj_dir, 'cond_image.png')

        if not os.path.exists(cond_image_path):
            print(f"Skipping {obj_name}: no condition image")
            continue

        # Generate views with original model
        orig_views = generate_views(pipeline_orig, cond_image_path, device)

        # Generate views with attn1-only LoRA
        attn1_views = generate_views(pipeline_attn1, cond_image_path, device)

        # Load GT images
        gt_images = []
        for i in range(6):
            gt_path = os.path.join(obj_dir, f'view_{i:02d}.png')
            if os.path.exists(gt_path):
                gt_pil = Image.open(gt_path).convert('RGB')
                gt_tensor = v2.functional.to_tensor(gt_pil).unsqueeze(0)
                gt_images.append(gt_tensor)
        gt_images = torch.cat(gt_images, dim=0).to(device)

        # Compute metrics
        psnr_orig = compute_psnr(attn1_views, orig_views)
        psnr_gt = compute_psnr(attn1_views, gt_images)
        clip_sim = compute_clip_similarity(attn1_views, cond_image_path, clip_model, clip_preprocess, device)
        dino_cos = compute_dino_similarity(attn1_views, cond_image_path, dino_model, dino_processor, device)

        results['psnr_vs_orig'].append(psnr_orig)
        results['psnr_vs_gt'].append(psnr_gt)
        results['clip_sim'].append(clip_sim)
        results['dino_cos'].append(dino_cos)

    # Compute averages
    avg_results = {k: np.mean(v) for k, v in results.items()}
    std_results = {k: np.std(v) for k, v in results.items()}

    print("\n=== Ablation Results: Attn1-only LoRA ===")
    print(f"PSNR vs Original: {avg_results['psnr_vs_orig']:.2f} ± {std_results['psnr_vs_orig']:.2f}")
    print(f"PSNR vs GT:       {avg_results['psnr_vs_gt']:.2f} ± {std_results['psnr_vs_gt']:.2f}")
    print(f"CLIP Similarity:  {avg_results['clip_sim']:.4f} ± {std_results['clip_sim']:.4f}")
    print(f"DINO Cosine:      {avg_results['dino_cos']:.4f} ± {std_results['dino_cos']:.4f}")

    # Save results
    report = {
        'method': 'attn1-only LoRA',
        'lora_path': args.lora_path,
        'num_objects': len(test_objects),
        'avg_results': {k: float(v) for k, v in avg_results.items()},
        'std_results': {k: float(v) for k, v in std_results.items()},
        'per_object_results': {k: [float(x) for x in v] for k, v in results.items()},
    }

    with open(os.path.join(args.output_dir, 'attn1_ablation_results.json'), 'w') as f:
        json.dump(report, f, indent=2)

    # Save markdown report
    with open(os.path.join(args.output_dir, 'attn1_ablation_report.md'), 'w') as f:
        f.write("# Attn1-only LoRA Ablation Results\n\n")
        f.write(f"**LoRA Path**: {args.lora_path}\n")
        f.write(f"**Num Objects**: {len(test_objects)}\n\n")
        f.write("## Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| PSNR vs Original | {avg_results['psnr_vs_orig']:.2f} ± {std_results['psnr_vs_orig']:.2f} dB |\n")
        f.write(f"| PSNR vs GT | {avg_results['psnr_vs_gt']:.2f} ± {std_results['psnr_vs_gt']:.2f} dB |\n")
        f.write(f"| CLIP Similarity | {avg_results['clip_sim']:.4f} ± {std_results['clip_sim']:.4f} |\n")
        f.write(f"| DINO Cosine | {avg_results['dino_cos']:.4f} ± {std_results['dino_cos']:.4f} |\n")
        f.write("\n## Comparison Table\n\n")
        f.write("| Method | PSNR vs Orig | PSNR vs GT | CLIP Sim | DINO Cos |\n")
        f.write("|--------|-------------|-----------|----------|----------|\n")
        f.write(f"| Original | ∞ | 34.49 | 0.7200 | 0.9204 |\n")
        f.write(f"| Full LoRA | 14.99 | 33.20 | 0.7062 | 0.9242 |\n")
        f.write(f"| RP-LoRA (attn2-only) | 48.29 | 34.48 | 0.7242 | 0.9216 |\n")
        f.write(f"| Attn1-only | {avg_results['psnr_vs_orig']:.2f} | {avg_results['psnr_vs_gt']:.2f} | {avg_results['clip_sim']:.4f} | {avg_results['dino_cos']:.4f} |\n")

    print(f"\nResults saved to {args.output_dir}")


if __name__ == '__main__':
    main()
