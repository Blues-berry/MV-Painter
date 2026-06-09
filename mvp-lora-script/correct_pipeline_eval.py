"""
Correct Pipeline End-to-End Evaluation (Memory-Efficient Version)

Two-phase approach to avoid OOM:
  Phase 1: Generate all views with pipeline (no metric models on GPU)
  Phase 2: Compute metrics from saved images (no pipeline on GPU)

Compares Original, Full LoRA, attn2-only LoRA under correct pipeline (ControlNet + depth).
"""
import os
import sys
import csv
import gc
import json
import random
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from safetensors.torch import load_file
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline_utils import (
    load_pipeline, get_bare_unet, reload_base_weights, verify_reference_attention,
    create_combined_grids, run_inference, seed_everything,
    CHECKPOINT_PATH, UNET_CKPT_PATH, TRAIN_DATA, VIEW_FILES, psnr,
)
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only


# ============================================================
# Configuration
# ============================================================
SEED = 42
NUM_INFERENCE_STEPS = 50
RESOLUTION = 512
DEVICE = 'cuda'

# LoRA checkpoints
FULL_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-broken-r4-lr1e4-100-lora-broken-r4-lr1e4-100/lora_checkpoints/lora_step_0000100.safetensors'
ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-250-lora-attn2-only-r4-lr1e5-250/lora_checkpoints/lora_step_0000250.safetensors'

# Test objects
TEST_OBJECTS_FILE = '/4T/CXY/MV-Painter/mvpoutput/paper_assets/test_objects_300.txt'

# Output directory
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/correct_pipeline_eval_300'

# Scales to test
SCALES = [1.0, 0.25]

# Methods — v29 UNet (current setup)
METHODS = {
    'original': {'lora_path': None, 'merge_fn': None, 'rank': None, 'use_v29': True},
    'full_lora': {'lora_path': FULL_LORA_PATH, 'merge_fn': merge_lora_into_unet, 'rank': 4, 'use_v29': True},
    'attn2_only': {'lora_path': ATTN2_LORA_PATH, 'merge_fn': merge_lora_into_unet_attn2_only, 'rank': 4, 'use_v29': True},
}

# Methods — base UNet (matches LoRA training setup)
METHODS_BASE = {
    'base_original': {'lora_path': None, 'merge_fn': None, 'rank': None, 'use_v29': False},
    'base_full_lora': {'lora_path': FULL_LORA_PATH, 'merge_fn': merge_lora_into_unet, 'rank': 4, 'use_v29': False},
    'base_attn2_only': {'lora_path': ATTN2_LORA_PATH, 'merge_fn': merge_lora_into_unet_attn2_only, 'rank': 4, 'use_v29': False},
}

# View order matching infer_multiview.py
VIEW_INDICES = [0, 5, 1, 4, 2, 3]  # 000, 005, 001, 004, 002, 003


# ============================================================
# Utilities
# ============================================================
def ensure_rgb(img):
    if img.mode == 'RGBA':
        # Alpha compositing: RGBA -> RGB with white background
        img_rgb = Image.new('RGB', img.size, (255, 255, 255))
        img_rgb.paste(img, mask=img.split()[3])
        return img_rgb
    return img


def load_test_objects():
    with open(TEST_OBJECTS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def load_condition_image(obj_path):
    cond_path = os.path.join(obj_path, 'image', '000.png')
    return Image.open(cond_path).convert('RGBA')


def load_gt_views(obj_path, view_indices):
    gt_views = []
    for idx in view_indices:
        gt_path = os.path.join(obj_path, 'image', f'{idx:03d}.png')
        if os.path.exists(gt_path):
            # Alpha compositing: RGBA -> RGB with white background
            img = Image.open(gt_path).convert('RGBA')
            img_rgb = Image.new('RGB', img.size, (255, 255, 255))
            img_rgb.paste(img, mask=img.split()[3])
            gt_views.append(img_rgb)
        else:
            gt_views.append(None)
    return gt_views


def extract_views_from_grid(grid_image):
    arr = np.array(grid_image)
    h, w = arr.shape[0] // 3, arr.shape[1] // 2
    views = []
    for row in range(3):
        for col in range(2):
            y = row * h
            x = col * w
            view = arr[y:y+h, x:x+w]
            views.append(Image.fromarray(view))
    return views


def generate_views_for_method(pipeline, cond_img, normal_grid, depth_grid, method_config, scale):
    use_v29 = method_config.get('use_v29', True)
    reload_base_weights(pipeline, use_v29=use_v29)
    verify_reference_attention(pipeline)

    if method_config['lora_path'] is not None:
        bare_unet = get_bare_unet(pipeline)
        alpha = int(method_config['rank'] * scale)
        method_config['merge_fn'](bare_unet, method_config['lora_path'],
                                   rank=method_config['rank'], alpha=alpha)
        verify_reference_attention(pipeline)

    grid_image = run_inference(pipeline, cond_img, normal_grid, depth_grid,
                                seed=SEED, num_steps=NUM_INFERENCE_STEPS)
    if grid_image is None:
        return None
    return extract_views_from_grid(grid_image)


def compute_ssim(img1, img2):
    from skimage.metrics import structural_similarity
    img1 = ensure_rgb(img1)
    img2 = ensure_rgb(img2)
    a1 = np.array(img1).astype(np.float64)
    a2 = np.array(img2).astype(np.float64)
    if a1.shape != a2.shape:
        img2 = img2.resize(img1.size, Image.BILINEAR)
        a2 = np.array(img2).astype(np.float64)
    if len(a1.shape) == 3:
        ssim_vals = []
        for c in range(a1.shape[2]):
            ssim_val = structural_similarity(a1[:, :, c], a2[:, :, c], data_range=255)
            ssim_vals.append(ssim_val)
        return np.mean(ssim_vals)
    else:
        return structural_similarity(a1, a2, data_range=255)


def create_qualitative_grid(cond_img, views_dict, obj_id):
    fig, axes = plt.subplots(4, 7, figsize=(28, 16))
    axes[0, 0].imshow(cond_img.convert('RGB'))
    axes[0, 0].set_title('Condition', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    for j in range(1, 7):
        axes[0, j].axis('off')

    method_names = ['original', 'full_lora', 'attn2_only']
    method_labels = ['Original', 'Full LoRA', 'attn2-only LoRA']

    for row, (method, label) in enumerate(zip(method_names, method_labels), 1):
        axes[row, 0].text(0.5, 0.5, label, transform=axes[row, 0].transAxes,
                          fontsize=12, fontweight='bold', ha='center', va='center')
        axes[row, 0].axis('off')
        if method in views_dict:
            for j, view in enumerate(views_dict[method]):
                axes[row, j+1].imshow(view.convert('RGB'))
                axes[row, j+1].set_title(f'View {j}', fontsize=10)
                axes[row, j+1].axis('off')
        else:
            for j in range(1, 7):
                axes[row, j].axis('off')

    plt.suptitle(f'Object: {obj_id}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


def create_qualitative_grid_v2(cond_img, views_dict, obj_id):
    """Create a comprehensive comparison grid: v29 UNet vs base UNet, with and without LoRA."""
    fig, axes = plt.subplots(7, 7, figsize=(28, 32))

    # Row 0: Condition
    axes[0, 0].imshow(cond_img.convert('RGB'))
    axes[0, 0].set_title('Condition', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    for j in range(1, 7):
        axes[0, j].axis('off')

    # Row 1: Section header for v29 UNet
    axes[1, 0].text(0.5, 0.5, 'v29 UNet\n(fine-tuned)', transform=axes[1, 0].transAxes,
                    fontsize=11, fontweight='bold', ha='center', va='center', color='blue')
    axes[1, 0].axis('off')
    for j in range(1, 7):
        axes[1, j].axis('off')

    # Rows 2-4: v29 UNet methods
    v29_methods = [('original', 'Original (v29)'), ('full_lora', 'Full LoRA (v29)'), ('attn2_only', 'attn2-only (v29)')]
    for row, (method, label) in enumerate(v29_methods, 2):
        axes[row, 0].text(0.5, 0.5, label, transform=axes[row, 0].transAxes,
                          fontsize=10, fontweight='bold', ha='center', va='center')
        axes[row, 0].axis('off')
        if method in views_dict:
            for j, view in enumerate(views_dict[method]):
                axes[row, j+1].imshow(view.convert('RGB'))
                axes[row, j+1].set_title(f'View {j}', fontsize=10)
                axes[row, j+1].axis('off')
        else:
            for j in range(1, 7):
                axes[row, j].axis('off')

    # Row 4: Section header for base UNet
    axes[4, 0].text(0.5, 0.5, 'Base UNet\n(pretrained)', transform=axes[4, 0].transAxes,
                    fontsize=11, fontweight='bold', ha='center', va='center', color='green')
    axes[4, 0].axis('off')
    for j in range(1, 7):
        axes[4, j].axis('off')

    # Rows 5-7: base UNet methods
    base_methods = [('base_original', 'Original (base)'), ('base_full_lora', 'Full LoRA (base)'), ('base_attn2_only', 'attn2-only (base)')]
    for row, (method, label) in enumerate(base_methods, 5):
        axes[row, 0].text(0.5, 0.5, label, transform=axes[row, 0].transAxes,
                          fontsize=10, fontweight='bold', ha='center', va='center')
        axes[row, 0].axis('off')
        if method in views_dict:
            for j, view in enumerate(views_dict[method]):
                axes[row, j+1].imshow(view.convert('RGB'))
                axes[row, j+1].set_title(f'View {j}', fontsize=10)
                axes[row, j+1].axis('off')
        else:
            for j in range(1, 7):
                axes[row, j].axis('off')

    plt.suptitle(f'Object: {obj_id} — v29 vs Base UNet Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


# ============================================================
# Phase 1: Generate all views
# ============================================================
def phase1_generate(test_objects):
    """Generate all views and save to disk. Pipeline on GPU, no metric models.

    Generates views for both v29 UNet and base UNet setups.
    """
    print("\n" + "=" * 60)
    print("PHASE 1: Generating views")
    print("=" * 60)

    # Load pipeline with v29 UNet (can switch to base via reload_base_weights)
    pipeline = load_pipeline(use_v29=True)
    views_dir = os.path.join(OUTPUT_DIR, 'generated_views')

    # All methods to generate (v29 + base)
    all_methods = {}
    all_methods.update(METHODS)
    all_methods.update(METHODS_BASE)

    # Build expected method directory names for resume check
    expected_methods = []
    for method_name, method_config in all_methods.items():
        if method_config['lora_path'] is None:
            expected_methods.append(method_name)
        else:
            for scale in SCALES:
                expected_methods.append(f'{method_name}_s{scale}')

    for obj_idx, obj_id in enumerate(test_objects):
        print(f"\n{'='*60}")
        print(f"Object {obj_idx+1}/{len(test_objects)}: {obj_id}")
        print(f"{'='*60}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        if not os.path.exists(obj_path):
            print(f"  Skipping: path not found")
            continue

        # Resume check: skip if all methods already generated
        obj_view_dir = os.path.join(views_dir, obj_id)
        if os.path.exists(obj_view_dir):
            all_done = True
            for m in expected_methods:
                m_dir = os.path.join(obj_view_dir, m)
                if not os.path.exists(m_dir) or len(os.listdir(m_dir)) < 6:
                    all_done = False
                    break
            if all_done:
                print(f"  Skipping: already complete")
                continue

        cond_img = load_condition_image(obj_path)
        normal_grid, depth_grid = create_combined_grids(obj_path)
        if normal_grid is None:
            print(f"  Skipping: could not create grids")
            continue

        # Save condition image for Phase 2
        obj_view_dir = os.path.join(views_dir, obj_id)
        os.makedirs(obj_view_dir, exist_ok=True)
        cond_img.convert('RGB').save(os.path.join(obj_view_dir, 'condition.png'))

        # Generate all methods (v29 and base)
        for method_name, method_config in all_methods.items():
            if method_config['lora_path'] is None:
                # Original (no LoRA)
                print(f"  Generating {method_name}...")
                views = generate_views_for_method(
                    pipeline, cond_img, normal_grid, depth_grid,
                    method_config, 0.0
                )
                if views is not None:
                    view_dir = os.path.join(obj_view_dir, method_name)
                    os.makedirs(view_dir, exist_ok=True)
                    for v_idx, view in enumerate(views):
                        view.save(os.path.join(view_dir, f'view_{v_idx:02d}.png'))
                    print(f"    Saved 6 views")
            else:
                # LoRA methods
                for scale in SCALES:
                    print(f"  Generating {method_name} (scale={scale})...")
                    views = generate_views_for_method(
                        pipeline, cond_img, normal_grid, depth_grid,
                        method_config, scale
                    )
                    if views is not None:
                        view_dir = os.path.join(obj_view_dir, f'{method_name}_s{scale}')
                        os.makedirs(view_dir, exist_ok=True)
                        for v_idx, view in enumerate(views):
                            view.save(os.path.join(view_dir, f'view_{v_idx:02d}.png'))
                        print(f"    Saved 6 views")

        gc.collect()
        torch.cuda.empty_cache()

    # Free pipeline
    del pipeline
    gc.collect()
    torch.cuda.empty_cache()
    print("\nPhase 1 complete. Pipeline unloaded.")


# ============================================================
# Phase 2: Compute metrics from saved images
# ============================================================
class MetricComputer:
    def __init__(self, device='cuda'):
        self.device = device
        self._load_models()

    def _load_models(self):
        print("Loading metric models...")
        import lpips
        self.lpips_fn = lpips.LPIPS(net='alex').to(self.device).eval()

        import open_clip
        self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', pretrained='laion2b_s34b_b79k', device=self.device
        )
        self.clip_model.eval()
        self.clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')

        self.dino_model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14', pretrained=True)
        self.dino_model = self.dino_model.to(self.device).eval()

        from torchvision import transforms
        self.dino_transform = transforms.Compose([
            transforms.Resize(224, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.CenterCrop(224),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        print("Metric models loaded.")

    @torch.no_grad()
    def compute_lpips(self, img1, img2):
        img1, img2 = ensure_rgb(img1), ensure_rgb(img2)
        def pil_to_tensor(img):
            arr = np.array(img).astype(np.float32) / 127.5 - 1.0
            return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
        t1 = pil_to_tensor(img1).to(self.device)
        t2 = pil_to_tensor(img2).to(self.device)
        if t1.shape != t2.shape:
            img2 = img2.resize(img1.size, Image.BILINEAR)
            t2 = pil_to_tensor(img2).to(self.device)
        return self.lpips_fn(t1, t2).item()

    @torch.no_grad()
    def compute_clip_similarity(self, img1, img2):
        def preprocess(img):
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return self.clip_preprocess(img).unsqueeze(0)
        t1 = preprocess(img1).to(self.device)
        t2 = preprocess(img2).to(self.device)
        f1 = self.clip_model.encode_image(t1)
        f2 = self.clip_model.encode_image(t2)
        f1 = f1 / f1.norm(dim=-1, keepdim=True)
        f2 = f2 / f2.norm(dim=-1, keepdim=True)
        return (f1 @ f2.T).item()

    @torch.no_grad()
    def compute_dino_similarity(self, img1, img2):
        def preprocess(img):
            if img.mode != 'RGB':
                img = img.convert('RGB')
            arr = np.array(img).astype(np.float32) / 255.0
            t = torch.from_numpy(arr).permute(2, 0, 1)
            return self.dino_transform(t).unsqueeze(0)
        t1 = preprocess(img1).to(self.device)
        t2 = preprocess(img2).to(self.device)
        f1 = self.dino_model(t1)
        f2 = self.dino_model(t2)
        f1 = f1 / f1.norm(dim=-1, keepdim=True)
        f2 = f2 / f2.norm(dim=-1, keepdim=True)
        return (f1 @ f2.T).item()

    def compute_multiview_consistency(self, view_images):
        n = len(view_images)
        clip_sims, dino_sims = [], []
        for i, j in combinations(range(n), 2):
            clip_sims.append(self.compute_clip_similarity(view_images[i], view_images[j]))
            dino_sims.append(self.compute_dino_similarity(view_images[i], view_images[j]))
        return {
            'mv_clip_consistency': np.mean(clip_sims),
            'mv_dino_consistency': np.mean(dino_sims),
        }


def phase2_compute_metrics(test_objects):
    """Compute all metrics from saved images. Metric models on GPU, no pipeline."""
    print("\n" + "=" * 60)
    print("PHASE 2: Computing metrics")
    print("=" * 60)

    mc = MetricComputer(device=DEVICE)
    views_dir = os.path.join(OUTPUT_DIR, 'generated_views')

    # CSV setup
    per_view_file = os.path.join(OUTPUT_DIR, 'per_view_metrics.csv')
    per_object_file = os.path.join(OUTPUT_DIR, 'per_object_metrics.csv')

    view_fields = [
        'object_id', 'view_id', 'method', 'scale',
        'psnr_gt', 'ssim_gt', 'lpips_gt', 'psnr_original',
        'clip_condition', 'dino_condition'
    ]
    object_fields = [
        'object_id', 'method', 'scale',
        'mean_psnr_gt', 'mean_ssim_gt', 'mean_lpips_gt',
        'mean_psnr_original', 'mean_clip_condition', 'mean_dino_condition',
        'mv_clip_consistency', 'mv_dino_consistency',
        'std_clip_condition', 'std_dino_condition'
    ]

    view_csv = open(per_view_file, 'w', newline='')
    view_writer = csv.DictWriter(view_csv, fieldnames=view_fields)
    view_writer.writeheader()

    object_csv = open(per_object_file, 'w', newline='')
    object_writer = csv.DictWriter(object_csv, fieldnames=object_fields)
    object_writer.writeheader()

    all_results = []

    # Build task list: (obj_id, method, scale)
    tasks = []
    for obj_id in test_objects:
        obj_view_dir = os.path.join(views_dir, obj_id)
        if not os.path.exists(obj_view_dir):
            continue
        # v29 UNet methods
        if os.path.exists(os.path.join(obj_view_dir, 'original')):
            tasks.append((obj_id, 'original', 0.0))
        for method_name in ['full_lora', 'attn2_only']:
            for scale in SCALES:
                dirname = f'{method_name}_s{scale}'
                if os.path.exists(os.path.join(obj_view_dir, dirname)):
                    tasks.append((obj_id, method_name, scale))
        # Base UNet methods
        if os.path.exists(os.path.join(obj_view_dir, 'base_original')):
            tasks.append((obj_id, 'base_original', 0.0))
        for method_name in ['base_full_lora', 'base_attn2_only']:
            for scale in SCALES:
                dirname = f'{method_name}_s{scale}'
                if os.path.exists(os.path.join(obj_view_dir, dirname)):
                    tasks.append((obj_id, method_name, scale))

    print(f"Total tasks: {len(tasks)}")

    for task_idx, (obj_id, method, scale) in enumerate(tasks):
        print(f"\n[{task_idx+1}/{len(tasks)}] {obj_id} / {method} / scale={scale}")

        obj_path = os.path.join(TRAIN_DATA, obj_id)
        obj_view_dir = os.path.join(views_dir, obj_id)

        # Load GT views
        gt_views = load_gt_views(obj_path, VIEW_INDICES)

        # Load condition
        cond_img = Image.open(os.path.join(obj_view_dir, 'condition.png')).convert('RGB')

        # Load generated views
        if method in ('original', 'base_original'):
            gen_dir = os.path.join(obj_view_dir, method)
        else:
            gen_dir = os.path.join(obj_view_dir, f'{method}_s{scale}')

        gen_views = []
        for v_idx in range(6):
            v_path = os.path.join(gen_dir, f'view_{v_idx:02d}.png')
            if os.path.exists(v_path):
                gen_views.append(Image.open(v_path).convert('RGB'))
            else:
                gen_views.append(None)

        # Load original views for psnr_original comparison
        # Use base_original for base methods, original for v29 methods
        orig_views = None
        if method not in ('original', 'base_original'):
            if method.startswith('base_'):
                orig_dir = os.path.join(obj_view_dir, 'base_original')
            else:
                orig_dir = os.path.join(obj_view_dir, 'original')
            if os.path.exists(orig_dir):
                orig_views = []
                for v_idx in range(6):
                    v_path = os.path.join(orig_dir, f'view_{v_idx:02d}.png')
                    if os.path.exists(v_path):
                        orig_views.append(Image.open(v_path).convert('RGB'))
                    else:
                        orig_views.append(None)

        # Compute per-view metrics
        view_metrics_list = []
        for v_idx, gen_view in enumerate(gen_views):
            if gen_view is None:
                continue
            gt_view = gt_views[v_idx] if v_idx < len(gt_views) else None

            metrics = {
                'object_id': obj_id,
                'view_id': v_idx,
                'method': method,
                'scale': scale,
            }

            # PSNR/SSIM/LPIPS vs GT
            if gt_view is not None:
                metrics['psnr_gt'] = psnr(gen_view, gt_view)
                metrics['ssim_gt'] = compute_ssim(gen_view, gt_view)
                metrics['lpips_gt'] = mc.compute_lpips(gen_view, gt_view)
            else:
                metrics['psnr_gt'] = float('nan')
                metrics['ssim_gt'] = float('nan')
                metrics['lpips_gt'] = float('nan')

            # PSNR vs Original
            if orig_views is not None and orig_views[v_idx] is not None:
                metrics['psnr_original'] = psnr(gen_view, orig_views[v_idx])
            elif method == 'original':
                metrics['psnr_original'] = 0.0
            else:
                metrics['psnr_original'] = float('nan')

            # CLIP/DINO vs condition
            metrics['clip_condition'] = mc.compute_clip_similarity(gen_view, cond_img)
            metrics['dino_condition'] = mc.compute_dino_similarity(gen_view, cond_img)

            view_writer.writerow(metrics)
            view_metrics_list.append(metrics)

            print(f"  View {v_idx}: PSNR={metrics['psnr_gt']:.2f}, "
                  f"SSIM={metrics['ssim_gt']:.4f}, "
                  f"PSNR_orig={metrics['psnr_original']:.2f}, "
                  f"CLIP={metrics['clip_condition']:.4f}")

        # Multi-view consistency
        valid_views = [v for v in gen_views if v is not None]
        if len(valid_views) >= 2:
            mv_metrics = mc.compute_multiview_consistency(valid_views)
        else:
            mv_metrics = {'mv_clip_consistency': 0.0, 'mv_dino_consistency': 0.0}

        # Per-object aggregates
        if view_metrics_list:
            obj_metric = {
                'object_id': obj_id,
                'method': method,
                'scale': scale,
                'mean_psnr_gt': np.nanmean([m['psnr_gt'] for m in view_metrics_list]),
                'mean_ssim_gt': np.nanmean([m['ssim_gt'] for m in view_metrics_list]),
                'mean_lpips_gt': np.nanmean([m['lpips_gt'] for m in view_metrics_list]),
                'mean_psnr_original': np.nanmean([m['psnr_original'] for m in view_metrics_list]),
                'mean_clip_condition': np.nanmean([m['clip_condition'] for m in view_metrics_list]),
                'mean_dino_condition': np.nanmean([m['dino_condition'] for m in view_metrics_list]),
                'mv_clip_consistency': mv_metrics['mv_clip_consistency'],
                'mv_dino_consistency': mv_metrics['mv_dino_consistency'],
                'std_clip_condition': np.nanstd([m['clip_condition'] for m in view_metrics_list]),
                'std_dino_condition': np.nanstd([m['dino_condition'] for m in view_metrics_list]),
            }
            object_writer.writerow(obj_metric)
            all_results.append(obj_metric)

    view_csv.close()
    object_csv.close()
    return all_results


# ============================================================
# Phase 3: Generate qualitative grids and report
# ============================================================
def phase3_grids_and_report(test_objects, all_results):
    """Generate qualitative comparison grids and final report."""
    print("\n" + "=" * 60)
    print("PHASE 3: Qualitative grids and report")
    print("=" * 60)

    views_dir = os.path.join(OUTPUT_DIR, 'generated_views')
    grid_dir = os.path.join(OUTPUT_DIR, 'qualitative_grids')
    os.makedirs(grid_dir, exist_ok=True)

    for obj_id in test_objects:
        obj_view_dir = os.path.join(views_dir, obj_id)
        if not os.path.exists(obj_view_dir):
            continue

        # Load condition
        cond_path = os.path.join(obj_view_dir, 'condition.png')
        if not os.path.exists(cond_path):
            continue
        cond_img = Image.open(cond_path).convert('RGB')

        # Load views for each method (scale=1.0 for LoRA)
        views_dict = {}
        for method in ['original', 'full_lora', 'attn2_only',
                       'base_original', 'base_full_lora', 'base_attn2_only']:
            if method in ('original', 'base_original'):
                gen_dir = os.path.join(obj_view_dir, method)
            else:
                gen_dir = os.path.join(obj_view_dir, f'{method}_s1.0')

            if os.path.exists(gen_dir):
                views = []
                for v_idx in range(6):
                    v_path = os.path.join(gen_dir, f'view_{v_idx:02d}.png')
                    if os.path.exists(v_path):
                        views.append(Image.open(v_path).convert('RGB'))
                if views:
                    views_dict[method] = views

        if views_dict:
            fig = create_qualitative_grid_v2(cond_img, views_dict, obj_id)
            fig.savefig(os.path.join(grid_dir, f'{obj_id}.png'),
                       dpi=150, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved grid for {obj_id}")

    # Generate summary CSV
    summary_file = os.path.join(OUTPUT_DIR, 'summary_metrics.csv')
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_results:
        key = (r['method'], r['scale'])
        groups[key].append(r)

    summary_fields = [
        'method', 'scale', 'N_objects', 'N_views',
        'mean_psnr_gt', 'std_psnr_gt',
        'mean_ssim_gt', 'std_ssim_gt',
        'mean_lpips_gt', 'std_lpips_gt',
        'mean_psnr_original', 'std_psnr_original',
        'mean_clip_condition', 'std_clip_condition',
        'mean_dino_condition', 'std_dino_condition',
        'mean_mv_clip', 'std_mv_clip',
        'mean_mv_dino', 'std_mv_dino',
    ]

    with open(summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        for (method, scale), records in sorted(groups.items()):
            n = len(records)
            summary = {
                'method': method,
                'scale': scale,
                'N_objects': n,
                'N_views': n * 6,
            }
            for metric in ['mean_psnr_gt', 'mean_ssim_gt', 'mean_lpips_gt',
                          'mean_psnr_original', 'mean_clip_condition', 'mean_dino_condition',
                          'mv_clip_consistency', 'mv_dino_consistency']:
                values = [r[metric] for r in records]
                short = metric.replace('mean_', '').replace('_consistency', '')
                summary[f'mean_{short}'] = np.nanmean(values)
                summary[f'std_{short}'] = np.nanstd(values)
            writer.writerow(summary)

    # Generate report
    generate_report(all_results, groups)
    print("Phase 3 complete.")


def generate_report(all_results, groups):
    report_path = os.path.join(OUTPUT_DIR, 'report.md')
    with open(report_path, 'w') as f:
        f.write("# Correct Pipeline End-to-End Evaluation Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Configuration\n\n")
        f.write(f"- Seed: {SEED}\n")
        f.write(f"- Num inference steps: {NUM_INFERENCE_STEPS}\n")
        f.write(f"- Resolution: {RESOLUTION}\n")
        f.write(f"- Device: {DEVICE}\n")
        f.write(f"- Full LoRA checkpoint: `{FULL_LORA_PATH}`\n")
        f.write(f"- attn2-only LoRA checkpoint: `{ATTN2_LORA_PATH}`\n")
        f.write(f"- UNet checkpoint: `{UNET_CKPT_PATH}`\n")
        f.write(f"- Test objects file: `{TEST_OBJECTS_FILE}`\n\n")

        f.write("## Methods\n\n")
        f.write("| Method | Description |\n")
        f.write("|--------|-------------|\n")
        f.write("| original | No LoRA, base model with custom UNet checkpoint |\n")
        f.write("| full_lora | LoRA on all attention layers (attn1 + attn2) |\n")
        f.write("| attn2_only | LoRA on cross-attention only (attn2) |\n\n")

        f.write("## Summary Results\n\n")
        f.write("| Method | Scale | N | PSNR↑ | SSIM↑ | LPIPS↓ | PSNR vs Orig | CLIP cond | DINO cond | MV CLIP | MV DINO |\n")
        f.write("|--------|-------|---|-------|-------|--------|--------------|-----------|-----------|---------|--------|\n")

        for (method, scale), records in sorted(groups.items()):
            n = len(records)
            psnr_vals = [r['mean_psnr_gt'] for r in records]
            ssim_vals = [r['mean_ssim_gt'] for r in records]
            lpips_vals = [r['mean_lpips_gt'] for r in records]
            psnr_orig_vals = [r['mean_psnr_original'] for r in records]
            clip_vals = [r['mean_clip_condition'] for r in records]
            dino_vals = [r['mean_dino_condition'] for r in records]
            mv_clip_vals = [r['mv_clip_consistency'] for r in records]
            mv_dino_vals = [r['mv_dino_consistency'] for r in records]

            f.write(f"| {method} | {scale:.2f} | {n} | "
                   f"{np.nanmean(psnr_vals):.2f}±{np.nanstd(psnr_vals):.2f} | "
                   f"{np.nanmean(ssim_vals):.4f}±{np.nanstd(ssim_vals):.4f} | "
                   f"{np.nanmean(lpips_vals):.4f}±{np.nanstd(lpips_vals):.4f} | "
                   f"{np.nanmean(psnr_orig_vals):.2f} | "
                   f"{np.nanmean(clip_vals):.4f}±{np.nanstd(clip_vals):.4f} | "
                   f"{np.nanmean(dino_vals):.4f}±{np.nanstd(dino_vals):.4f} | "
                   f"{np.nanmean(mv_clip_vals):.4f} | "
                   f"{np.nanmean(mv_dino_vals):.4f} |\n")

        f.write("\n## Key Findings\n\n")
        f.write("*(Analysis to be added after reviewing results)*\n")

    print(f"Report saved to {report_path}")


# ============================================================
# Main
# ============================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'qualitative_grids'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'generated_views'), exist_ok=True)

    test_objects = load_test_objects()
    print(f"Test objects: {len(test_objects)}")

    # Check if views already generated
    views_dir = os.path.join(OUTPUT_DIR, 'generated_views')
    existing = [d for d in os.listdir(views_dir) if os.path.isdir(os.path.join(views_dir, d))] if os.path.exists(views_dir) else []

    if len(existing) >= len(test_objects):
        print(f"Found {len(existing)} existing object views. Skipping Phase 1.")
    else:
        phase1_generate(test_objects)

    # Phase 2: Compute metrics
    all_results = phase2_compute_metrics(test_objects)

    # Phase 3: Grids and report
    phase3_grids_and_report(test_objects, all_results)

    print(f"\n{'='*60}")
    print("Evaluation complete!")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
