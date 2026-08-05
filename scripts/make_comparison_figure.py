"""Generate a comparison figure: GT / TCAS C3 / no_adapter / SF3D for selected objects.

Produces a grid image showing 4 methods × N objects for the paper.
"""
import os
import sys
import types
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

# Setup SF3D
sys.path.insert(0, '/home/ubuntu/ssd_work/projects/stable-fast-3d')
dummy = types.ModuleType('sf3d.material_refine')
dummy.MaterialRefinementPipeline = None
sys.modules['sf3d.material_refine'] = dummy
from sf3d.system import SF3D

# Import nvdiffrast renderer from eval script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.eval_sf3d_baseline import render_mesh_to_view, load_camera

DATA_ROOT = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
SAMPLES_C3 = '/4T/CXY/MV-Painter/mvpoutput/geotex_v2/eval300v2_c3/samples'
SAMPLES_NOA = '/4T/CXY/MV-Painter/mvpoutput/geotex_v2/eval300v2_no_adapter/samples'


def load_gt_grid(obj, data_root, target_views, size=256):
    """Load GT 6 views and tile into 2x3 grid."""
    imgs = []
    for v in target_views:
        p = os.path.join(data_root, obj, 'image', f'{v:03d}.png')
        im = Image.open(p).convert('RGBA').resize((size, size))
        arr = np.array(im).astype(np.float32) / 255.0
        rgb = arr[..., :3] * arr[..., 3:4] + 1.0 * (1 - arr[..., 3:4])
        imgs.append((rgb * 255).astype(np.uint8))
    return tile_views(imgs, size)


def tile_views(imgs, size=256):
    """Tile 6 views into 2x3 grid."""
    grid = Image.new('RGB', (size * 3, size * 2), 'white')
    for i, arr in enumerate(imgs):
        r, c = divmod(i, 3)
        grid.paste(Image.fromarray(arr), (c * size, r * size))
    return grid


def load_eval_sample(path):
    """Load a pre-saved 6-view grid sample from eval."""
    if os.path.exists(path):
        return Image.open(path).convert('RGB')
    return None


def render_sf3d_views(model, obj, data_root, target_views, size=256, device='cuda:0'):
    """Run SF3D and render 6 views."""
    ref = Image.open(os.path.join(data_root, obj, 'image', '000.png'))
    arr = np.array(ref)
    if arr.shape[-1] == 4 and (arr[..., 3] == 0).all():
        return None

    with torch.no_grad():
        mesh, _ = model.run_image(ref, 512)

    imgs = []
    for v in target_views:
        cam = load_camera(os.path.join(data_root, obj, 'camera', f'{v:03d}.npy'))
        rendered = render_mesh_to_view(mesh, cam, size, device)
        imgs.append((rendered * 255).clip(0, 255).astype(np.uint8))
    return tile_views(imgs, size)


def main():
    # Select representative objects (first few that have all samples available)
    objs_file = os.path.join(DATA_ROOT, 'test_objects_300.txt')
    with open(objs_file) as f:
        all_objs = [l.strip() for l in f if l.strip()]

    # Use objects with best PSNR (available in eval samples, idx 0-19)
    selected = [13, 8, 15, 6, 9]
    target_views = [0, 15, 12, 15, 13, 14]
    size = 128  # smaller per-view for compact figure

    print("Loading SF3D model...")
    model = SF3D.from_pretrained(
        "stabilityai/stable-fast-3d",
        config_name="config.yaml", weight_name="model.safetensors")
    model.to('cuda:0').eval()
    print("SF3D loaded")

    methods = ['GT', 'C3 (TCAS)', 'No adapter', 'SF3D']
    n_obj = len(selected)
    grid_w = size * 3  # each method shows 2x3 grid at this tile size
    grid_h = size * 2

    # Full canvas: methods as columns, objects as rows
    canvas_w = grid_w * len(methods) + 30 * (len(methods) - 1)
    canvas_h = grid_h * n_obj + 30 * n_obj  # +30 for labels
    canvas = Image.new('RGB', (canvas_w, canvas_h + 40), 'white')
    draw = ImageDraw.Draw(canvas)

    # Column headers
    for mi, m in enumerate(methods):
        x = mi * (grid_w + 30) + grid_w // 2
        draw.text((x - 30, 5), m, fill='black')

    for row, oi in enumerate(selected):
        obj = all_objs[oi]
        y_offset = 40 + row * (grid_h + 30)
        print(f"  Object {oi}: {obj[:12]}...")

        # GT
        gt_grid = load_gt_grid(obj, DATA_ROOT, target_views, size)
        canvas.paste(gt_grid, (0, y_offset))

        # C3
        c3_path = os.path.join(SAMPLES_C3, f'obj_{oi:04d}_tcas_v2.png')
        c3_img = load_eval_sample(c3_path)
        if c3_img:
            c3_img = c3_img.resize((grid_w, grid_h))
            canvas.paste(c3_img, (grid_w + 30, y_offset))

        # No adapter
        noa_path = os.path.join(SAMPLES_NOA, f'obj_{oi:04d}_tcas_v2.png')
        noa_img = load_eval_sample(noa_path)
        if noa_img:
            noa_img = noa_img.resize((grid_w, grid_h))
            canvas.paste(noa_img, (2 * (grid_w + 30), y_offset))

        # SF3D
        sf3d_grid = render_sf3d_views(model, obj, DATA_ROOT, target_views, size)
        if sf3d_grid:
            canvas.paste(sf3d_grid, (3 * (grid_w + 30), y_offset))

    out_path = '/4T/CXY/MV-Painter/mvpoutput/comparison_figure.png'
    canvas.save(out_path)
    print(f"Saved: {out_path} ({canvas.size})")


if __name__ == '__main__':
    main()
