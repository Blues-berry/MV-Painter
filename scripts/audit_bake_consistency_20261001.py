#!/usr/bin/env python
"""Baking seam / cross-view consistency audit (final_audit_20261001, Phase 4).

Descriptive consistency metrics for the existing 12-object CPU bake
(`main_adapter_baking/cpu_bake_12{,_layerwise}`), no new baking, no GPU
inference (EGL offscreen rendering only):

1. UV-seam color discontinuity: 3D-adjacent surface points whose UV charts
   disagree (glTF vertex splits) are located; for each seam edge, matching
   parameters t on both chart sides are sampled 2 texels inside their charts
   and compared with CIEDE2000. Baseline: mean CIEDE2000 of adjacent in-chart
   texel pairs, for scale. UV->texel mapping follows the bake's own renderer
   (cpu_texture_bake.render_textured_view: y = (1 - v) * (S - 1)).
2. Cross-view reprojection consistency: the textured mesh is rendered from 8
   fixed orthographic cameras (EGL); world-space position maps are derived
   analytically from depth; for every ordered view pair, corresponding pixels
   (same surface point, depth-consistent) are compared with CIEDE2000.
   A globally consistent UV-convention error cancels in this view-to-view
   difference by construction.

Outputs: bake_consistency_per_asset.csv, bake_consistency_summary.json under
--output-dir. Purely descriptive (12 stratified objects; no inferential claims).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))

BAKE_ROOT = ROOT / "final/round2/main_adapter_baking"
METHODS = {
    "c3": BAKE_ROOT / "cpu_bake_12/c3",
    "fixed_high": BAKE_ROOT / "cpu_bake_12/fixed_high",
    "fixed_low": BAKE_ROOT / "cpu_bake_12/fixed_low",
    "no_adapter": BAKE_ROOT / "cpu_bake_12/no_adapter",
    "global_c3": BAKE_ROOT / "cpu_bake_12_layerwise/global_c3",
    "global_fixed_low": BAKE_ROOT / "cpu_bake_12_layerwise/global_fixed_low",
    "layer_lhl": BAKE_ROOT / "cpu_bake_12_layerwise/layer_lhl",
    "layer_llh": BAKE_ROOT / "cpu_bake_12_layerwise/layer_llh",
}
OBJECTS = ["obj_0013", "obj_0015", "obj_0038", "obj_0048", "obj_0054",
           "obj_0066", "obj_0068", "obj_0078", "obj_0082", "obj_0083",
           "obj_0110", "obj_0111"]

AZIMUTHS = (45.0, 135.0, 225.0, 315.0)
ELEVATIONS = (20.0, -20.0)
RES = 256
XMAG = 0.75
SEAM_SAMPLES = 16
SEAM_OFFSET = 2.0
MAX_SEAM_EDGES = 4000
BASELINE_PAIRS = 4000


def look_at(eye, target, up):
    forward = target - eye
    forward = forward / np.linalg.norm(forward)
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    up2 = np.cross(right, forward)
    pose = np.eye(4)
    pose[:3, 0], pose[:3, 1], pose[:3, 2] = right, up2, -forward
    pose[:3, 3] = eye
    return pose


def camera_poses():
    eye_r = 2.0
    poses = []
    for el in ELEVATIONS:
        for az in AZIMUTHS:
            a, e = np.radians(az), np.radians(el)
            eye = eye_r * np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
            poses.append(look_at(eye, np.zeros(3), np.array([0.0, 0.0, 1.0])))
    return poses


def load_asset(directory, obj, method):
    import trimesh
    stem = f"{obj}_{method}"
    glb_path = directory / obj / f"{stem}_textured.glb"
    texture_path = directory / obj / f"{stem}_texture.png"
    scene = trimesh.load(str(glb_path), process=False)
    meshes = list(scene.geometry.values()) if hasattr(scene, "geometry") else [scene]
    verts, faces, uvs, voff = [], [], [], 0
    for m in meshes:
        if m.visual.uv is None:
            raise RuntimeError(f"{glb_path}: geometry without UVs")
        verts.append(np.asarray(m.vertices, dtype=np.float64))
        faces.append(np.asarray(m.faces, dtype=np.int64) + voff)
        uvs.append(np.asarray(m.visual.uv, dtype=np.float64))
        voff += len(m.vertices)
    vertices = np.concatenate(verts)
    faces = np.concatenate(faces)
    uv = np.concatenate(uvs)
    from PIL import Image
    texture = np.asarray(Image.open(texture_path).convert("RGB"), dtype=np.float32) / 255.0
    return vertices, faces, uv, texture


def canonical_edges(vertices, faces, uv):
    """Canonical 3D edges with their per-occurrence UV assignments."""
    quant = np.round(vertices / 1e-4).astype(np.int64)
    _, canon = np.unique(quant, axis=0, return_inverse=True)
    edge_uvs = {}
    for tri in range(len(faces)):
        a, b, c = faces[tri]
        u = uv[[a, b, c]]
        v = canon[[a, b, c]]
        for i, j in ((0, 1), (1, 2), (2, 0)):
            key = (v[i], v[j]) if v[i] < v[j] else (v[j], v[i])
            ui, uj = (u[i], u[j]) if v[i] < v[j] else (u[j], u[i])
            edge_uvs.setdefault(key, []).append((ui, uj))
    seam = []
    for key, occ in edge_uvs.items():
        if len(occ) < 2:
            continue
        ref = occ[0]
        for other in occ[1:]:
            if np.max(np.abs(ref[0] - other[0])) > 1e-3 or np.max(np.abs(ref[1] - other[1])) > 1e-3:
                seam.append((key, ref, other))
                break
    return seam


def uv_to_texel(points, size):
    x = np.clip(points[..., 0], 0.0, 1.0) * (size - 1)
    y = np.clip(1.0 - points[..., 1], 0.0, 1.0) * (size - 1)
    return np.stack([x, y], axis=-1)


def sample_texel(lab_image, mask, texel):
    x, y = int(round(float(texel[0]))), int(round(float(texel[1])))
    if 0 <= x < mask.shape[1] and 0 <= y < mask.shape[0] and mask[y, x]:
        return lab_image[y, x]
    return None


def seam_metrics(uv, faces, vertices, texture):
    import cv2
    from skimage.color import deltaE_ciede2000, rgb2lab

    size = texture.shape[0]
    lab = rgb2lab(texture)
    occupancy = np.zeros((size, size), dtype=np.uint8)
    tri_uv = uv[faces]
    polys = np.stack([
        np.stack([tri_uv[:, :, 0] * (size - 1), (1.0 - tri_uv[:, :, 1]) * (size - 1)], axis=-1)
    ], axis=1).astype(np.int32)
    cv2.fillPoly(occupancy, [p for p in polys], 1)

    seams = canonical_edges(vertices, faces, uv)
    if len(seams) > MAX_SEAM_EDGES:
        rng = np.random.default_rng(20261001)
        idx = rng.choice(len(seams), MAX_SEAM_EDGES, replace=False)
        seams = [seams[i] for i in idx]

    deltas = []
    total_len = 0.0
    for (key, occ_a, occ_b) in seams:
        (ua_p, ua_q), (ub_p, ub_q) = np.asarray(occ_a), np.asarray(occ_b)
        ts = np.linspace(0.05, 0.95, SEAM_SAMPLES)
        seg_a = np.stack([ua_p + (ua_q - ua_p) * t for t in ts])
        seg_b = np.stack([ub_p + (ub_q - ub_p) * t for t in ts])
        total_len += float(np.linalg.norm(
            uv_to_texel(ua_q[None], size)[0] - uv_to_texel(ua_p[None], size)[0]))
        tex_a = uv_to_texel(seg_a, size)
        tex_b = uv_to_texel(seg_b, size)
        da = tex_a[-1] - tex_a[0]
        na = np.array([-da[1], da[0]])
        norm = np.linalg.norm(na)
        if norm < 1e-6:
            continue
        na = na / norm
        db = tex_b[-1] - tex_b[0]
        nb = np.array([-db[1], db[0]])
        norm = np.linalg.norm(nb)
        if norm < 1e-6:
            continue
        nb = nb / norm
        for sign in (1.0, -1.0):
            la = sample_texel(lab, occupancy, tex_a + sign * SEAM_OFFSET * na)
            lb = sample_texel(lab, occupancy, tex_b + sign * SEAM_OFFSET * nb)
            if la is None or lb is None:
                continue
            deltas.append(float(deltaE_ciede2000(la[None, :], lb[None, :])[0]))

    base = []
    ys, xs = np.nonzero(occupancy)
    if len(xs) > 0:
        rng = np.random.default_rng(20261001)
        pick_x = rng.integers(0, size - 1, BASELINE_PAIRS)
        pick_y = rng.integers(0, size, BASELINE_PAIRS)
        for x, y in zip(pick_x, pick_y):
            if occupancy[y, x] and occupancy[y, x + 1]:
                base.append(float(deltaE_ciede2000(lab[y, x][None, :], lab[y, x + 1][None, :])[0]))
    return {
        "seam_edges_used": len(seams),
        "seam_mean_dE00": float(np.mean(deltas)) if deltas else float("nan"),
        "seam_n_samples": len(deltas),
        "seam_uv_length_texels": total_len,
        "baseline_adjacent_dE00": float(np.mean(base)) if base else float("nan"),
        "seam_over_baseline": float(np.mean(deltas) / np.mean(base)) if deltas and base else float("nan"),
    }


def render_views(vertices, faces, uv, texture):
    os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
    import pyrender
    import trimesh
    from PIL import Image

    tm = trimesh.Trimesh(
        vertices=vertices, faces=faces,
        visual=trimesh.visual.TextureVisuals(uv=uv, image=Image.fromarray(
            (texture * 255).astype(np.uint8))), process=False)
    mesh = pyrender.Mesh.from_trimesh(tm, smooth=False)
    color_maps, depth_maps, poses = [], [], camera_poses()
    renderer = pyrender.OffscreenRenderer(RES, RES)
    scene = pyrender.Scene(bg_color=[1.0, 1.0, 1.0, 1.0], ambient_light=[0.3, 0.3, 0.3])
    scene.add(mesh)
    cam = pyrender.OrthographicCamera(xmag=XMAG, ymag=XMAG)
    cam_node = scene.add(cam, pose=poses[0])
    for pose in poses:
        scene.set_pose(cam_node, pose)
        color, depth = renderer.render(scene)
        color_maps.append(color[..., :3].astype(np.float32) / 255.0)
        depth_maps.append(depth.astype(np.float32))
    renderer.delete()
    return color_maps, depth_maps, poses


def position_map(depth, pose):
    h, w = depth.shape
    xs = (np.arange(w) + 0.5) / w * 2 - 1
    ys = 1 - (np.arange(h) + 0.5) / h * 2
    gx, gy = np.meshgrid(xs, ys)
    cam = np.stack([gx * XMAG, gy * XMAG, -depth], axis=-1)
    return cam @ pose[:3, :3].T + pose[:3, 3]


def crossview_metrics(colors, depths, poses):
    from skimage.color import deltaE_ciede2000, rgb2lab

    labs = [rgb2lab(c) for c in colors]
    world_maps = [position_map(d, p) for d, p in zip(depths, poses)]
    deltas = []
    n = len(colors)
    for i in range(n):
        valid_i = depths[i] > 0
        if not np.any(valid_i):
            continue
        pos_i = world_maps[i][valid_i]
        lab_i = labs[i][valid_i]
        for j in range(n):
            if i == j:
                continue
            ext_inv = np.eye(4)
            ext_inv[:3, :3] = poses[j][:3, :3].T
            ext_inv[:3, 3] = -poses[j][:3, :3].T @ poses[j][:3, 3]
            cam = pos_i @ ext_inv[:3, :3].T + ext_inv[:3, 3]
            z = -cam[:, 2]
            px = np.floor((cam[:, 0] / XMAG + 1) / 2 * RES).astype(int)
            py = np.floor((1 - (cam[:, 1] / XMAG + 1) / 2) * RES).astype(int)
            ok = (px >= 0) & (px < RES) & (py >= 0) & (py < RES) & (z > 0)
            if not np.any(ok):
                continue
            px, py, zc = px[ok], py[ok], z[ok]
            zbuf = depths[j][py, px]
            agree = (zbuf > 0) & (np.abs(zbuf - zc) <= np.maximum(1e-3, 0.02 * zc))
            if not np.any(agree):
                continue
            deltas.append(np.asarray(deltaE_ciede2000(lab_i[ok][agree], labs[j][py[agree], px[agree]])))
    all_d = np.concatenate(deltas) if deltas else np.array([np.nan])
    return {
        "crossview_mean_dE00": float(np.nanmean(all_d)),
        "crossview_p90_dE00": float(np.nanpercentile(all_d, 90)),
        "crossview_n_correspondences": int(all_d.size),
        "crossview_view_pairs": n * (n - 1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--methods", nargs="*", default=list(METHODS))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for method in args.methods:
        directory = METHODS[method]
        for obj in OBJECTS:
            vertices, faces, uv, texture = load_asset(directory, obj, method)
            extent = float(np.max(vertices.max(0) - vertices.min(0)))
            vertices = (vertices - (vertices.max(0) + vertices.min(0)) / 2) / extent
            row = {"object": obj, "method": method, "n_faces": int(len(faces))}
            row.update(seam_metrics(uv, faces, vertices, texture))
            colors, depths, poses = render_views(vertices, faces, uv, texture)
            row.update(crossview_metrics(colors, depths, poses))
            rows.append(row)
            print(f"[{obj}/{method}] seam={row['seam_mean_dE00']:.3f} "
                  f"(x{row['seam_over_baseline']:.2f}) crossview={row['crossview_mean_dE00']:.3f}",
                  flush=True)

    fields = list(rows[0])
    with (args.output_dir / "bake_consistency_per_asset.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for method in args.methods:
        sub = [r for r in rows if r["method"] == method]
        summary[method] = {
            "n": len(sub),
            "seam_mean_dE00_mean": float(np.nanmean([r["seam_mean_dE00"] for r in sub])),
            "seam_over_baseline_mean": float(np.nanmean([r["seam_over_baseline"] for r in sub])),
            "crossview_mean_dE00_mean": float(np.nanmean([r["crossview_mean_dE00"] for r in sub])),
            "crossview_p90_dE00_mean": float(np.nanmean([r["crossview_p90_dE00"] for r in sub])),
        }
    (args.output_dir / "bake_consistency_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
