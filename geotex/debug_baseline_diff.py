#!/usr/bin/env python3
"""Debug baseline difference between eval.py and eval_scale_inline.py.

Loads model, generates baseline for obj_074 using eval.py's generate_images,
compares with old eval_300obj_clean baseline and new vis_selected baseline.
"""
import os, sys, torch
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from torchvision.utils import save_image
from diffusers import EulerDiscreteScheduler
from eval import load_model, generate_images, collate_batch, prepare_batch

BASE = '/4T/CXY/MV-Painter'
DEVICE = torch.device('cuda:1')
CONFIG = f'{BASE}/mvpoutput/geotex/eval_config_snapshot.yaml'
CHECKPOINT = f'{BASE}/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt'
OBJ_IDX = 74  # obj_074

def main():
    print("Loading model...")
    model = load_model(CONFIG, CHECKPOINT, DEVICE)
    config = OmegaConf.load(CONFIG)
    dataset = instantiate_from_config(config.data.params.validation)

    print(f"Generating baseline for object {OBJ_IDX}...")
    batch = collate_batch(dataset, OBJ_IDX, DEVICE)
    cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
        prepare_batch(batch, model.img_size, DEVICE)

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    torch.manual_seed(42)
    shared_latents = torch.randn(1, 4, latent_h, latent_w, device=DEVICE, dtype=torch.float16)

    # Generate baseline using eval.py's generate_images
    torch.manual_seed(42)
    img_eval_py = generate_images(model, batch, DEVICE, torch.float16, None, 50, shared_latents)

    # Save
    out_dir = f'{BASE}/debug_baseline'
    os.makedirs(out_dir, exist_ok=True)
    save_image(img_eval_py, f'{out_dir}/obj_074_baseline_eval_py.png')
    save_image(target_imgs, f'{out_dir}/obj_074_gt.png')
    save_image(mask, f'{out_dir}/obj_074_mask.png')

    # Compare with old and new baselines
    eval_py = img_eval_py[0].cpu().permute(1, 2, 0).numpy()

    old_path = f'{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations/obj_074_original.png'
    new_path = f'{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/vis_selected/s1p25/visualizations/obj_074_orig.png'

    old = np.array(Image.open(old_path).convert('RGB')).astype(float) / 255.0
    new = np.array(Image.open(new_path).convert('RGB')).astype(float) / 255.0

    eval_py_fg = ~np.all(eval_py > 0.92, axis=2)
    old_fg = ~np.all(old > 0.92, axis=2)
    new_fg = ~np.all(new > 0.92, axis=2)

    print(f"\n=== obj_074 Baseline Comparison ===")
    print(f"eval.py generate_images: mean={eval_py.mean():.3f}, FG_frac={eval_py_fg.mean():.3f}")
    print(f"Old eval_300obj_clean:   mean={old.mean():.3f}, FG_frac={old_fg.mean():.3f}")
    print(f"New vis_selected:        mean={new.mean():.3f}, FG_frac={new_fg.mean():.3f}")
    print(f"\nDiff eval_py vs old: {np.abs(eval_py - old).mean():.4f}")
    print(f"Diff eval_py vs new: {np.abs(eval_py - new).mean():.4f}")
    print(f"Diff old vs new:     {np.abs(old - new).mean():.4f}")

if __name__ == '__main__':
    main()
