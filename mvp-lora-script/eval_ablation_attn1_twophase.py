"""
Evaluate attn1-only LoRA ablation - two-phase approach to avoid OOM.
Phase 1: Generate images with Original model, save to disk.
Phase 2: Generate images with attn1-only LoRA, save to disk.
Phase 3: Compute metrics on CPU from saved images.
"""
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


def generate_and_save(checkpoint_path, lora_path, output_dir, test_objects, test_dir, device='cuda:0', label='original'):
    """Generate views and save to disk."""
    print(f"\n=== Generating with {label} ===")
    pipeline = MVPainter_Pipeline.from_pretrained(checkpoint_path, use_safetensors=True).to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    if lora_path:
        print(f"Loading attn1-only LoRA from {lora_path}...")
        lora_processors = create_lora_processors_attn1_only(pipeline.unet, rank=4, network_alpha=4)
        pipeline.unet.set_attn_processor(lora_processors)
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

    save_dir = os.path.join(output_dir, label)
    os.makedirs(save_dir, exist_ok=True)

    for obj_name in tqdm(test_objects, desc=f"Generating ({label})"):
        obj_dir = os.path.join(test_dir, obj_name)
        cond_image_path = os.path.join(obj_dir, 'image', '000.png')
        if not os.path.exists(cond_image_path):
            continue

        obj_save_dir = os.path.join(save_dir, obj_name)
        os.makedirs(obj_save_dir, exist_ok=True)

        # Skip if already generated
        if os.path.exists(os.path.join(obj_save_dir, 'view_005.png')):
            continue

        cond_image = Image.open(cond_image_path).convert('RGBA')
        with torch.no_grad():
            output = pipeline(cond_image, num_inference_steps=75, output_type='latent')
            latent = output.images
            image = pipeline.vae.decode(latent / pipeline.vae.config.scaling_factor, return_dict=False)[0]
            image = (image * 0.5 + 0.5).clamp(0, 1)

        # Save each view
        for i in range(image.shape[0]):
            from torchvision.transforms import functional as TF
            img_pil = TF.to_pil_image(image[i].cpu())
            img_pil.save(os.path.join(obj_save_dir, f'view_{i:02d}.png'))

    del pipeline
    torch.cuda.empty_cache()
    print(f"Saved {label} results to {save_dir}")


def compute_metrics_from_saved(output_dir, test_objects, test_dir, device='cuda:0'):
    """Compute metrics from saved images."""
    import clip
    from transformers import AutoModel, AutoImageProcessor
    from torchvision.transforms import v2

    print("\n=== Computing metrics ===")

    # Load CLIP
    clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)

    orig_dir = os.path.join(output_dir, 'original')
    attn1_dir = os.path.join(output_dir, 'attn1_only')

    psnr_vs_orig_list = []
    psnr_vs_gt_list = []
    clip_sim_list = []

    for obj_name in tqdm(test_objects, desc="Computing metrics"):
        orig_obj_dir = os.path.join(orig_dir, obj_name)
        attn1_obj_dir = os.path.join(attn1_dir, obj_name)

        if not os.path.exists(orig_obj_dir) or not os.path.exists(attn1_obj_dir):
            continue

        # Load generated views
        orig_views = []
        attn1_views = []
        for i in range(6):
            orig_path = os.path.join(orig_obj_dir, f'view_{i:02d}.png')
            attn1_path = os.path.join(attn1_obj_dir, f'view_{i:02d}.png')
            if os.path.exists(orig_path) and os.path.exists(attn1_path):
                orig_pil = Image.open(orig_path).convert('RGB')
                attn1_pil = Image.open(attn1_path).convert('RGB')
                orig_views.append(v2.functional.to_tensor(orig_pil).unsqueeze(0))
                attn1_views.append(v2.functional.to_tensor(attn1_pil).unsqueeze(0))

        if not orig_views:
            continue

        orig_views = torch.cat(orig_views, dim=0)
        attn1_views = torch.cat(attn1_views, dim=0)

        # PSNR vs Original
        mse = torch.mean((attn1_views - orig_views) ** 2).item()
        psnr_orig = 10 * np.log10(1.0 / max(mse, 1e-10))
        psnr_vs_orig_list.append(psnr_orig)

        # PSNR vs GT
        gt_images = []
        obj_dir = os.path.join(test_dir, obj_name)
        for i in range(6):
            gt_path = os.path.join(obj_dir, 'image', f'{i:03d}.png')
            if os.path.exists(gt_path):
                gt_pil = Image.open(gt_path).convert('RGB')
                gt_tensor = v2.functional.to_tensor(gt_pil).unsqueeze(0)
                gt_images.append(gt_tensor)
        if gt_images:
            gt_images = torch.cat(gt_images, dim=0)
            mse_gt = torch.mean((attn1_views - gt_images[:attn1_views.shape[0]]) ** 2).item()
            psnr_gt = 10 * np.log10(1.0 / max(mse_gt, 1e-10))
            psnr_vs_gt_list.append(psnr_gt)

        # CLIP Similarity (condition image vs generated views)
        cond_image_path = os.path.join(test_dir, obj_name, 'image', '000.png')
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
    print(f"{'Attn1-only':<20} {psnr_orig_mean:>11.2f}±{psnr_orig_std:.2f} {psnr_gt_mean:>11.2f}±{psnr_gt_std:.2f} {clip_mean:>9.4f}±{clip_std:.4f}")

    # Save results
    report = {
        'method': 'attn1-only LoRA',
        'num_objects': len(psnr_vs_orig_list),
        'psnr_vs_orig': {'mean': float(psnr_orig_mean), 'std': float(psnr_orig_std)},
        'psnr_vs_gt': {'mean': float(psnr_gt_mean), 'std': float(psnr_gt_std)},
        'clip_sim': {'mean': float(clip_mean), 'std': float(clip_std)},
    }

    with open(os.path.join(output_dir, 'attn1_ablation_results.json'), 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nResults saved to {output_dir}/attn1_ablation_results.json")
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--lora_path', type=str, default='/4T/CXY/MV-Painter/logs/mvpainter-lora-attn1-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors')
    parser.add_argument('--output_dir', type=str, default='/4T/CXY/MV-Painter/mvpoutput/ablation_attn1')
    parser.add_argument('--checkpoint_path', type=str, default='/4T/CXY/MV-Painter/checkpoints/hf_repo')
    parser.add_argument('--test_dir', type=str, default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--num_objects', type=int, default=5)
    parser.add_argument('--phase', type=str, default='all', choices=['generate_orig', 'generate_attn1', 'compute', 'all'])
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = 'cuda:0'

    # Load test objects
    all_objects = sorted(os.listdir(args.test_dir))
    valid_objects = [o for o in all_objects if os.path.exists(os.path.join(args.test_dir, o, 'image', '000.png'))]
    test_objects = valid_objects[:args.num_objects]
    print(f"Evaluating on {len(test_objects)} objects: {test_objects}")

    # Save test objects list
    with open(os.path.join(args.output_dir, 'test_objects.json'), 'w') as f:
        json.dump(test_objects, f)

    if args.phase in ['generate_orig', 'all']:
        generate_and_save(args.checkpoint_path, None, args.output_dir, test_objects, args.test_dir, device, 'original')

    if args.phase in ['generate_attn1', 'all']:
        generate_and_save(args.checkpoint_path, args.lora_path, args.output_dir, test_objects, args.test_dir, device, 'attn1_only')

    if args.phase in ['compute', 'all']:
        compute_metrics_from_saved(args.output_dir, test_objects, args.test_dir, device)


if __name__ == '__main__':
    main()
