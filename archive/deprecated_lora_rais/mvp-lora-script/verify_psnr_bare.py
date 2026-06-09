"""
Verify PSNR vs Original for all LoRA checkpoints.
Reloads full pipeline per config to avoid state issues.
"""
import os, sys, gc, csv
import numpy as np
import torch
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MVPainter'))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from diffusers import EulerAncestralDiscreteScheduler
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
from mvpainter.lora_utils import merge_lora_into_unet

CHECKPOINT_PATH = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
UNET_CKPT_PATH = '/4T/CXY/MV-Painter/checkpoints/v29_25000.safetensors'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'

def load_pipeline():
    pipeline = MVPainter_Pipeline.from_pretrained(CHECKPOINT_PATH, torch_dtype=torch.float16)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing')
    unet_state = load_file(UNET_CKPT_PATH)
    pipeline.unet.load_state_dict(unet_state, strict=False)
    pipeline = pipeline.to('cuda')
    return pipeline

def run_and_extract(pipeline, image, seed=42):
    generator = torch.Generator(device='cuda').manual_seed(seed)
    with torch.no_grad():
        output = pipeline(image, num_inference_steps=50, generator=generator, output_type='pil')
    img = output.images[0] if hasattr(output, 'images') else (output[0] if isinstance(output, list) else output)
    arr = np.array(img)
    h, w = arr.shape[:2]
    return Image.fromarray(arr[:h//2, :w//3])

def compute_psnr(img1, img2):
    a1 = np.array(img1).astype(np.float64)
    a2 = np.array(img2).astype(np.float64)
    mse = np.mean((a1 - a2) ** 2)
    return float('inf') if mse == 0 else 10 * np.log10(255.0**2 / mse)

def main():
    out = '/4T/CXY/MV-Painter/mvpoutput/verification'
    os.makedirs(out, exist_ok=True)

    tests = ['d6a5427888b8413fbfcbcaad14353af8', 'aa82baf218104070a932dee9a1db61ce',
             'e3f35d4cfbb14410bf96a4ffa28235a1', 'b23ec9725c48494788d1d88104acbb4a',
             'c630e3959eab49ae87cdad42937e21b2']

    ckpts = [
        ('broken_r4', '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors',
         4, 4, 'full', 'Full LoRA r4'),
        ('crash_r8', '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors',
         8, 8, 'full', 'Full LoRA r8'),
        ('attn2_r4', '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors',
         4, 4, 'attn2', 'attn2-only r4'),
    ]

    results = []
    for obj_id in tests:
        cond_img = Image.open(os.path.join(TRAIN_DATA, obj_id, 'image/000.png')).convert('RGBA')
        row = {'obj_id': obj_id}
        print(f"\n{obj_id}")

        for name, path, rank, alpha, ltype, label in ckpts:
            print(f"  {label}...", end=' ', flush=True)
            torch.cuda.empty_cache()
            gc.collect()
            pipeline = load_pipeline()
            if ltype == 'full':
                merge_lora_into_unet(pipeline.unet, path, rank=rank, alpha=alpha)
            else:
                merge_lora_into_unet_attn2_only(pipeline.unet, path, rank=rank, alpha=alpha)
            view_lora = run_and_extract(pipeline, cond_img)
            del pipeline
            torch.cuda.empty_cache()
            gc.collect()

            # Reload original for comparison
            pipeline_orig = load_pipeline()
            view_orig = run_and_extract(pipeline_orig, cond_img)
            del pipeline_orig
            torch.cuda.empty_cache()
            gc.collect()

            psnr = compute_psnr(view_orig, view_lora)
            row[f'psnr_{name}'] = psnr
            print(f"{psnr:.2f} dB")
        results.append(row)

    # Summary
    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    def avg(k): return np.mean([r[k] for r in results])
    for name, _, _, _, _, label in ckpts:
        print(f"{label}: {avg(f'psnr_{name}'):.2f} dB")

    # Save
    md_path = os.path.join(out, 'psnr_vs_original_verified.md')
    with open(md_path, 'w') as f:
        f.write("# PSNR vs Original (Verified)\n\n")
        f.write("| Method | PSNR vs Original |\n|--------|------------------|\n")
        for name, _, _, _, _, label in ckpts:
            f.write(f"| {label} | {avg(f'psnr_{name}'):.2f} dB |\n")
    print(f"\nSaved to {md_path}")

if __name__ == '__main__':
    main()
