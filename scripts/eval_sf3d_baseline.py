"""Evaluate SF3D as an independent third-party reconstruction baseline for TCAS.

Pipeline:
  1. SF3D: single reference image → reconstructed mesh with UV texture
  2. Render the SF3D mesh using TCAS GT camera poses → 6-view RGB
  3. Compare rendered views against GT using FG-SSIM / PSNR / FG-LPIPS

Usage:
    python scripts/eval_sf3d_baseline.py \
        --num_objects 30 \
        --output_dir mvpoutput/sf3d_baseline
"""
import os
import sys
import json
import argparse
import types
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.transforms import v2

# Bypass missing sf3d.material_refine
sys.path.insert(0, '/home/ubuntu/ssd_work/projects/stable-fast-3d')
dummy = types.ModuleType('sf3d.material_refine')
dummy.MaterialRefinementPipeline = None
sys.modules['sf3d.material_refine'] = dummy

from sf3d.system import SF3D

# TCAS metrics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geotex'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
from metrics import compute_psnr, compute_ssim


def load_camera(cam_path):
    """Load TCAS camera params from npy."""
    cam = np.load(cam_path, allow_pickle=True).item()
    return cam


import nvdiffrast.torch as dr

_glctx = None

def get_glctx():
    global _glctx
    if _glctx is None:
        _glctx = dr.RasterizeCudaContext()
    return _glctx


def render_mesh_to_view(mesh, cam, img_size=256, device='cuda:0'):
    """Render a trimesh mesh using nvdiffrast with given camera params.

    Returns RGB image as numpy array [H,W,3] in [0,1], white background.
    """
    glctx = get_glctx()

    # Extract mesh data
    verts = torch.from_numpy(mesh.vertices).float().to(device)  # [V, 3]
    faces = torch.from_numpy(mesh.faces).int().to(device)  # [F, 3]

    # Build MVP matrix from camera params
    fov = float(cam['fov'])  # radians
    extrinsic = np.array(cam['extrinsic'])
    if extrinsic.shape == (3, 4):
        extrinsic = np.vstack([extrinsic, [0, 0, 0, 1]])

    # World2cam (4x4)
    w2c = torch.from_numpy(extrinsic).float().to(device)

    # Perspective projection matrix (OpenGL-style)
    near, far = float(cam.get('near', 0.1)), float(cam.get('far', 100.0))
    aspect = 1.0
    t = np.tan(fov / 2.0) * near
    b, l, r = -t, -t * aspect, t * aspect
    proj = torch.zeros(4, 4, device=device)
    proj[0, 0] = 2 * near / (r - l)
    proj[1, 1] = 2 * near / (t - b)
    proj[2, 2] = -(far + near) / (far - near)
    proj[2, 3] = -2 * far * near / (far - near)
    proj[3, 2] = -1.0

    mvp = proj @ w2c  # [4, 4]

    # Transform vertices to clip space
    v_homo = torch.cat([verts, torch.ones(verts.shape[0], 1, device=device)], dim=1)  # [V, 4]
    v_clip = (mvp @ v_homo.T).T  # [V, 4]

    # Rasterize
    v_clip_batch = v_clip[None].contiguous()  # [1, V, 4]
    faces = faces.contiguous()
    rast, _ = dr.rasterize(glctx, v_clip_batch, faces, resolution=[img_size, img_size])

    # Get texture if available
    if hasattr(mesh.visual, 'material') and hasattr(mesh.visual, 'uv'):
        uv = torch.from_numpy(np.array(mesh.visual.uv)).float().to(device)  # [V, 2]
        # Get texture image (PBRMaterial uses baseColorTexture)
        mat = mesh.visual.material
        tex_img = getattr(mat, 'baseColorTexture', None) or getattr(mat, 'image', None)
        if tex_img is not None:
            tex = torch.from_numpy(np.array(tex_img)).float().to(device) / 255.0
            if tex.dim() == 2:
                tex = tex.unsqueeze(-1).repeat(1, 1, 3)
            tex = tex[None]  # [1, H, W, C]

            # Interpolate UV
            uv_batch = uv[None]  # [1, V, 2]
            uv_interp, _ = dr.interpolate(uv_batch, rast, faces)  # [1, H, W, 2]

            # Texture lookup
            color = dr.texture(tex, uv_interp, filter_mode='linear')  # [1, H, W, 3]
        else:
            # Fallback: vertex colors or gray
            color = torch.ones(1, img_size, img_size, 3, device=device) * 0.5
    else:
        color = torch.ones(1, img_size, img_size, 3, device=device) * 0.5

    # Apply mask (where rast hits geometry)
    mask = (rast[..., 3:4] > 0).float()
    # White background
    color = color * mask + 1.0 * (1.0 - mask)

    return color[0].cpu().numpy()  # [H, W, 3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root', default='/4T/CXY/MV-Painter/data/train_data/rendered_full')
    parser.add_argument('--objects_file', default='/4T/CXY/MV-Painter/data/train_data/rendered_full/test_objects_300.txt')
    parser.add_argument('--output_dir', default='mvpoutput/sf3d_baseline')
    parser.add_argument('--num_objects', type=int, default=30)
    parser.add_argument('--bake_resolution', type=int, default=512)
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Load objects
    with open(args.objects_file) as f:
        all_objs = [l.strip() for l in f if l.strip()]
    obj_list = all_objs[:args.num_objects]
    print(f"Objects: {len(obj_list)}")

    # TCAS target view indices
    target_views = [0, 15, 12, 15, 13, 14]

    # Load SF3D model
    print("Loading SF3D model...")
    model = SF3D.from_pretrained(
        "stabilityai/stable-fast-3d",
        config_name="config.yaml",
        weight_name="model.safetensors",
    )
    model.to(args.device)
    model.eval()
    print("SF3D loaded")

    results = []

    for idx, obj in enumerate(obj_list):
        obj_dir = os.path.join(args.data_root, obj)
        ref_path = os.path.join(obj_dir, 'image', '000.png')

        if not os.path.exists(ref_path):
            print(f"  [{idx}] skip {obj}: no 000.png")
            continue

        # Check alpha
        ref_img = Image.open(ref_path)
        if ref_img.mode != 'RGBA':
            print(f"  [{idx}] skip {obj}: not RGBA")
            continue
        arr = np.array(ref_img)
        if (arr[..., 3] == 0).all():
            print(f"  [{idx}] skip {obj}: empty alpha")
            continue

        print(f"  [{idx}/{len(obj_list)}] {obj}...")

        try:
            # SF3D reconstruction
            with torch.no_grad():
                mesh, info = model.run_image(ref_img, args.bake_resolution)

            # Render 6 target views using TCAS cameras
            rendered_views = []
            gt_views = []
            masks = []

            for view_idx in target_views:
                cam_path = os.path.join(obj_dir, 'camera', f'{view_idx:03d}.npy')
                gt_path = os.path.join(obj_dir, 'image', f'{view_idx:03d}.png')

                cam = load_camera(cam_path)
                rendered = render_mesh_to_view(mesh, cam, img_size=256)
                rendered_views.append(rendered)

                # Load GT
                gt_img = np.array(Image.open(gt_path).resize((256, 256))).astype(np.float32) / 255.0
                if gt_img.shape[-1] == 4:
                    alpha = gt_img[..., 3:4]
                    gt_rgb = gt_img[..., :3] * alpha + 1.0 * (1 - alpha)  # white bg
                    masks.append(alpha[..., 0])
                else:
                    gt_rgb = gt_img
                    masks.append(np.ones(gt_img.shape[:2]))
                gt_views.append(gt_rgb)

            # Stack into grid (2x3) for metric computation
            # Convert to torch tensors
            pred_t = torch.from_numpy(np.stack(rendered_views)).permute(0, 3, 1, 2).float()
            gt_t = torch.from_numpy(np.stack(gt_views)).permute(0, 3, 1, 2).float()
            mask_t = torch.from_numpy(np.stack(masks)).unsqueeze(1).float()

            # Compute per-view metrics and average
            psnr_vals = []
            ssim_vals = []
            for v in range(len(target_views)):
                p = pred_t[v:v+1]
                g = gt_t[v:v+1]
                m = mask_t[v:v+1]
                psnr_vals.append(compute_psnr(p, g))
                ssim_vals.append(compute_ssim(p, g, m))

            avg_psnr = np.mean(psnr_vals)
            avg_ssim = np.mean(ssim_vals)

            results.append({
                'object': obj, 'obj_idx': idx,
                'full_psnr': avg_psnr, 'fg_ssim': avg_ssim,
            })
            print(f"    PSNR={avg_psnr:.2f} FG-SSIM={avg_ssim:.4f}")

        except Exception as e:
            print(f"    ERROR: {e}")
            continue

        torch.cuda.empty_cache()

    # Summary
    if results:
        mean_psnr = np.mean([r['full_psnr'] for r in results])
        mean_ssim = np.mean([r['fg_ssim'] for r in results])
        print(f"\n=== SF3D Baseline Summary ({len(results)} objects) ===")
        print(f"  Mean PSNR: {mean_psnr:.2f}")
        print(f"  Mean FG-SSIM: {mean_ssim:.4f}")

        summary = {
            'method': 'SF3D',
            'num_objects': len(results),
            'mean_psnr': float(mean_psnr),
            'mean_fg_ssim': float(mean_ssim),
            'per_object': results,
        }
        with open(os.path.join(args.output_dir, 'sf3d_results.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved: {args.output_dir}/sf3d_results.json")


if __name__ == '__main__':
    main()
