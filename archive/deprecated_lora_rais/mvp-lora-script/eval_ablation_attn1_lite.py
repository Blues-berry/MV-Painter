"""
Evaluate attn1-only LoRA ablation - lightweight version.
Loads one pipeline at a time to save GPU memory.
"""
import argparse
import os
import sys
import json
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from safetensors.torch import load_file

sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')

from diffusers import EulerAncestralDiscreteScheduler
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, ReferenceOnlyAttnProc
from mvpainter.lora_utils_attn1 import create_lora_processors_attn1_only
from torchvision.transforms import v2

import clip
from transformers import AutoModel, AutoImageProcessor


def load_pipeline_and_generate(checkpoint_path, test_objects, test_dir, device='cuda:0'):
    """Load pipeline and generate views for all test objects."""
    print(f"Loading pipeline from {checkpoint_path}...")
    pipeline = MVPainter_Pipeline.from_pretrained(checkpoint_path, use_safetensors=True).to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    results = {}

    for obj_name in tqdm(test_objects, desc="Generating"):
        obj_dir = os.path.join(test_dir, obj_name)
        cond_image_path = os.path.join(obj_dir, 'image', '000.png')
        if not os.path.exists(cond_image_path):
            continue

        cond_image = Image.open(cond_image_path).convert('RGBA')
        with torch.no_grad():
            output = pipeline(cond_image, num_inference_steps=75, output_type='latent')
            latent = output.images
            image = pipeline.vae.decode(latent / pipeline.vae.config.scaling_factor, return_dict=False)[0]
            image = (image * 0.5 + 0.5).clamp(0, 1)
        results[obj_name] = image.cpu()

    del pipeline
    torch.cuda.empty_cache()
    return results


def load_pipeline_with_lora_and_generate(checkpoint_path, lora_path, test_objects, test_dir, device='cuda:0'):
    """Load pipeline with attn1-only LoRA and generate views."""
    print(f"Loading pipeline with attn1-only LoRA...")
    pipeline = MVPainter_Pipeline.from_pretrained(checkpoint_path, use_safetensors=True).to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Set up attn1-only LoRA processors
    lora_processors = create_lora_processors_attn1_only(pipeline.unet, rank=4, network_alpha=4)
    pipeline.unet.set_attn_processor(lora_processors)

    # Load LoRA weights
    lora_state = load_file(lora_path)
    for name, proc in pipeline.unet.attn_processors.items():
        if not isinstance(proc, ReferenceOnlyAttnProc):
            continue
        if 'attn1' not in name:
            continue
        lora_proc = proc.chained_proc
        prefix = name.replace('.processor', '').replace('.', '_')
        for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
            if hasattr(lora_proc, param_name):
                lora_layer = getattr(lora_proc, param_name)
                down_key = f'{prefix}_{param_name}_down'
                up_key = f'{prefix}_{param_name}_up'
                if down_key in lora_state and up_key in lora_state:
                    lora_layer.down.weight.data = lora_state[down_key].to(lora_layer.down.weight.device)
                    lora_layer.up.weight.data = lora_state[up_key].to(lora_layer.up.weight.device)

    results = {}
    for obj_name in tqdm(test_objects, desc="Generating (attn1)"):
        obj_dir = os.path.join(test_dir, obj_name)
        cond_image_path = os.path.join(obj_dir, 'image', '000.png')
        if not os.path.exists(cond_image_path):
            continue

        cond_image = Image.open(cond_image_path).convert('RGBA')
        with torch.no_grad():
            output = pipeline(cond_image, num_inference_steps=75, output_type='latent')
            latent = output.images
            image = pipeline.vae.decode(latent / pipeline.vae.config.scaling_factor, return_dict=False)[0]
            image = (image * 0.5 + 0.5).clamp(0, 1)
        results[obj_name] = image.cpu()

    del pipeline
    torch.cuda.empty_cache()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lora_path', type=str, default='/4T/CXY/MV-Painter/logs/mvpainter-lora-attn1-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors')
    parser.add_argument('--output_dir', type=str, default='/4T/CXY/MV-Painter/mvpoutput/ablation_attn1')
    parser.add_argument('--checkpoint_path', type=str, default='/4T/CXY/MV-Painter/checkpoints/hf_repo')
    parser.add_argument('--test_dir', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--test_meta', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full/test_meta.json')
    parser.add_argument('--num_objects', type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = 'cuda:0'

    # Load test objects from directory listing
    all_objects = sorted(os.listdir(args.test_dir))
    # Filter to only directories with image/000.png (condition image)
    valid_objects = [o for o in all_objects if os.path.exists(os.path.join(args.test_dir, o, 'image', '000.png'))]
    test_objects = valid_objects[:args.num_objects]
    print(f"Evaluating on {len(test_objects)} objects: {test_objects}")

    # Phase 1: Generate with Original model
    print("\n=== Phase 1: Original model ===")
    orig_results = load_pipeline_and_generate(args.checkpoint_path, test_objects, args.test_dir, device)

    # Phase 2: Generate with attn1-only LoRA
    print("\n=== Phase 2: Attn1-only LoRA model ===")
    attn1_results = load_pipeline_with_lora_and_generate(args.checkpoint_path, args.lora_path, test_objects, args.test_dir, device)

    # Phase 3: Compute metrics
    print("\n=== Phase 3: Computing metrics ===")

    # Load CLIP
    clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)

    psnr_vs_orig_list = []
    psnr_vs_gt_list = []
    clip_sim_list = []

    for obj_name in test_objects:
        if obj_name not in orig_results or obj_name not in attn1_results:
            continue

        orig_views = orig_results[obj_name]
        attn1_views = attn1_results[obj_name]

        # PSNR vs Original
        mse = torch.mean((attn1_views - orig_views) ** 2).item()
        psnr_orig = 10 * np.log10(1.0 / max(mse, 1e-10))
        psnr_vs_orig_list.append(psnr_orig)

        # PSNR vs GT
        gt_images = []
        obj_dir = os.path.join(args.test_dir, obj_name)
        for i in range(6):
            gt_path = os.path.join(obj_dir, 'image', f'{i:03d}.png')
            if os.path.exists(gt_path):
                gt_pil = Image.open(gt_path).convert('RGB')
                gt_tensor = v2.functional.to_tensor(gt_pil).unsqueeze(0)
                gt_images.append(gt_tensor)
        if gt_images:
            gt_images = torch.cat(gt_images, dim=0)
            mse_gt = torch.mean((attn1_views - gt_images) ** 2).item()
            psnr_gt = 10 * np.log10(1.0 / max(mse_gt, 1e-10))
            psnr_vs_gt_list.append(psnr_gt)

        # CLIP Similarity
        cond_image_path = os.path.join(args.test_dir, obj_name, 'cond_image.png')
        with torch.no_grad():
            ref_pil = Image.open(cond_image_path).convert('RGB')
            ref_input = clip_preprocess(ref_pil).unsqueeze(0).to(device)
            ref_features = clip_model.encode_image(ref_input)
            ref_features = ref_features / ref_features.norm(dim=-1, keepdim=True)

            sims = []
            for i in range(attn1_views.shape[0]):
                gen_pil = v2.functional.to_pil_image(attn1_views[i])
                gen_input = clip_preprocess(gen_pil).unsqueeze(0).to(device)
                gen_features = clip_model.encode_image(gen_input)
                gen_features = gen_features / gen_features.norm(dim=-1, keepdim=True)
                sim = (ref_features @ gen_features.T).item()
                sims.append(sim)
            clip_sim_list.append(np.mean(sims))

    # Compute stats
    psnr_orig_mean = np.mean(psnr_vs_orig_list)
    psnr_orig_std = np.std(psnr_vs_orig_list)
    psnr_gt_mean = np.mean(psnr_vs_gt_list) if psnr_vs_gt_list else 0
    psnr_gt_std = np.std(psnr_vs_gt_list) if psnr_vs_gt_list else 0
    clip_mean = np.mean(clip_sim_list)
    clip_std = np.std(clip_sim_list)

    print("\n=== Ablation Results: Attn1-only LoRA ===")
    print(f"PSNR vs Original: {psnr_orig_mean:.2f} ± {psnr_orig_std:.2f}")
    print(f"PSNR vs GT:       {psnr_gt_mean:.2f} ± {psnr_gt_std:.2f}")
    print(f"CLIP Similarity:  {clip_mean:.4f} ± {clip_std:.4f}")

    # Comparison table
    print("\n=== Comparison Table ===")
    print(f"{'Method':<20} {'PSNR vs Orig':>12} {'PSNR vs GT':>12} {'CLIP Sim':>10}")
    print("-" * 58)
    print(f"{'Original':<20} {'∞':>12} {'36.12±3.22':>12} {'0.9770±0.0128':>10}")
    print(f"{'Full LoRA':<20} {'14.99':>12} {'34.02±3.60':>12} {'0.9766±0.0141':>10}")
    print(f"{'RP-LoRA (attn2)':<20} {'48.29':>12} {'36.12±3.21':>12} {'0.9772±0.0125':>10}")
    print(f"{'Attn1-only':<20} {psnr_orig_mean:>11.2f} {psnr_gt_mean:>11.2f}±{psnr_gt_std:.2f} {clip_mean:>9.4f}±{clip_std:.4f}")

    # Save results
    report = {
        'method': 'attn1-only LoRA',
        'lora_path': args.lora_path,
        'num_objects': len(test_objects),
        'psnr_vs_orig': {'mean': float(psnr_orig_mean), 'std': float(psnr_orig_std)},
        'psnr_vs_gt': {'mean': float(psnr_gt_mean), 'std': float(psnr_gt_std)},
        'clip_sim': {'mean': float(clip_mean), 'std': float(clip_std)},
    }

    with open(os.path.join(args.output_dir, 'attn1_ablation_results.json'), 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nResults saved to {args.output_dir}/attn1_ablation_results.json")


if __name__ == '__main__':
    main()
