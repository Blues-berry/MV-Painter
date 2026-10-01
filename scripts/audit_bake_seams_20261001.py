#!/usr/bin/env python
"""P3: UV-seam color-discontinuity audit over the existing CPU bakes.

For every textured GLB (8 conditions x 12 objects) this script measures, in
TEXTURE SPACE, the color discontinuity across UV-chart seams:

- seam edge   = a shared 3D edge whose two adjacent triangles assign
                different UV positions (chart boundary);
- seam gap    = CIEDE2000 between the texture colors sampled at the two
                chart-side locations of the SAME 3D edge midpoint;
- control     = CIEDE2000 between two samples of the SAME chart 2px apart
                across interior-edge midpoints (local texture gradient).

Rationale for cross-view consistency: the bakes are unlit albedo textures
on a fixed mesh rendered from unseen viewpoints; with no per-view shading
or stochasticity, cross-view color agreement on shared surface points is
determined by texture-space continuity (UV seams) and coverage. The seam
gaps therefore quantify the cross-view inconsistency mechanism directly.
Coverage / inpainted fractions are aggregated from the coverage PNGs.

CPU-only; no rendering, no GPU.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter
from skimage.color import deltaE_ciede2000, rgb2lab

import trimesh

ROOT = Path("/4T/CXY/MV-Painter")
BAKE_DIRS = {
    "no_adapter": ROOT / "final/round2/main_adapter_baking/cpu_bake_12/no_adapter",
    "fixed_low": ROOT / "final/round2/main_adapter_baking/cpu_bake_12/fixed_low",
    "fixed_high": ROOT / "final/round2/main_adapter_baking/cpu_bake_12/fixed_high",
    "c3": ROOT / "final/round2/main_adapter_baking/cpu_bake_12/c3",
    "global_fixed_low": ROOT / "final/round2/main_adapter_baking/cpu_bake_12_layerwise/global_fixed_low",
    "global_c3": ROOT / "final/round2/main_adapter_baking/cpu_bake_12_layerwise/global_c3",
    "layer_lhl": ROOT / "final/round2/main_adapter_baking/cpu_bake_12_layerwise/layer_lhl",
    "layer_llh": ROOT / "final/round2/main_adapter_baking/cpu_bake_12_layerwise/layer_llh",
}
OUT = ROOT / "final/round2/coordination/BAKE_SEAM_AUDIT_20261001"
UV_EPS = 1e-4
POS_DECIMALS = 5


def make_sampler(tex: np.ndarray):
    """3x3-mean texture sampler via uniform_filter; coords clamped in-bounds."""
    h, w = tex.shape[:2]
    rgb = tex[:, :, :3].astype(np.float64) / 255.0
    smooth = np.stack([uniform_filter(rgb[:, :, c], size=3, mode="nearest") for c in range(3)], axis=2)

    def sample(u, v):
        u = np.asarray(u, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        x = np.clip(np.round(u * (w - 1)).astype(int), 0, w - 1)
        y = np.clip(np.round((1.0 - v) * (h - 1)).astype(int), 0, h - 1)
        return smooth[y, x]

    return sample, w


def delta_e_batch(c1: np.ndarray, c2: np.ndarray) -> np.ndarray:
    lab1 = rgb2lab(np.clip(c1, 0, 1).reshape(-1, 1, 3))
    lab2 = rgb2lab(np.clip(c2, 0, 1).reshape(-1, 1, 3))
    return deltaE_ciede2000(lab1, lab2).reshape(-1)


def audit_glb(glb: Path) -> dict:
    mesh = trimesh.load(str(glb), force="mesh", process=False)
    uv = np.asarray(mesh.visual.uv, dtype=np.float64)
    faces = np.asarray(mesh.faces)
    mat = mesh.visual.material
    tex_img = getattr(mat, "baseColorTexture", None)
    if tex_img is None and hasattr(mat, "image"):
        tex_img = mat.image
    if tex_img is None:
        raise RuntimeError(f"no base-color texture in {glb}")
    tex = np.asarray(tex_img.convert("RGB"))
    sample, tex_w = make_sampler(tex)
    verts = np.asarray(mesh.vertices)

    # position-keyed vertex ids (charts may split vertices in the GLB)
    pk = np.round(verts, decimals=POS_DECIMALS)
    _, pid = np.unique(pk, axis=0, return_inverse=True)
    pid = pid.reshape(-1)

    # three corners per face -> three directed edges, normalized order
    f_pid = pid[faces]                # (F,3)
    f_uv = uv[faces]                  # (F,3,2)
    a = f_pid[:, [0, 1, 2]]
    b = f_pid[:, [1, 2, 0]]
    ua = f_uv[:, [0, 1, 2]]
    ub = f_uv[:, [1, 2, 0]]
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    u_lo = np.where((a <= b)[:, :, None], ua, ub)
    u_hi = np.where((a <= b)[:, :, None], ub, ua)

    key = lo.astype(np.int64) * (int(pid.max()) + 1) + hi.astype(np.int64)
    keys_flat = key.reshape(-1)
    order = np.argsort(keys_flat, kind="stable")
    keys = keys_flat[order]
    u_lo_f = u_lo.reshape(-1, 2)[order]
    u_hi_f = u_hi.reshape(-1, 2)[order]
    uniq, starts, counts = np.unique(keys, return_index=True, return_counts=True)

    seam_m1, seam_m2, ctrl_mid, ctrl_perp = [], [], [], []
    n_boundary = int((counts == 1).sum())
    n_interior_single = 0
    for k_idx in range(len(uniq)):
        s, c = starts[k_idx], counts[k_idx]
        if c == 1:
            continue
        m1 = (u_lo_f[s] + u_hi_f[s]) / 2.0
        # distinct uv-pairs among occurrences (global row indices)
        distinct = [s]
        for j in range(s + 1, s + c):
            if not any(np.abs(u_lo_f[j] - u_lo_f[d]).max() < UV_EPS
                       and np.abs(u_hi_f[j] - u_hi_f[d]).max() < UV_EPS for d in distinct):
                distinct.append(j)
        if len(distinct) > 1:
            m2 = (u_lo_f[distinct[1]] + u_hi_f[distinct[1]]) / 2.0
            seam_m1.append(m1)
            seam_m2.append(m2)
        else:
            n_interior_single += 1
            if n_interior_single % 7 == 0:  # fixed subsample of interior edges
                e_dir = u_hi_f[s] - u_lo_f[s]
                perp = np.array([-e_dir[1], e_dir[0]])
                n = np.linalg.norm(perp)
                if n > 0:
                    ctrl_mid.append(m1)
                    ctrl_perp.append(perp / n)

    if not seam_m1:
        return {"glb": str(glb), "n_seam_edges": 0, "n_boundary_edges": n_boundary,
                "note": "no UV seams detected"}

    seam_m1 = np.asarray(seam_m1)
    seam_m2 = np.asarray(seam_m2)
    seam_uv_dist = np.linalg.norm(seam_m1 - seam_m2, axis=1)

    c1 = sample(seam_m1[:, 0], seam_m1[:, 1])
    c2 = sample(seam_m2[:, 0], seam_m2[:, 1])
    seam_de = delta_e_batch(c1, c2)

    if ctrl_mid:
        cm = np.asarray(ctrl_mid)
        cp = np.asarray(ctrl_perp) * (2.0 / tex_w)  # fixed 2px offset
        k1 = sample(cm[:, 0] + cp[:, 0], cm[:, 1] + cp[:, 1])
        k2 = sample(cm[:, 0] - cp[:, 0], cm[:, 1] - cp[:, 1])
        ctrl_de = delta_e_batch(k1, k2)
        ctrl_mean = float(ctrl_de.mean())
        ratio = float(seam_de.mean() / ctrl_mean) if ctrl_mean > 0 else None
    else:
        ctrl_mean, ratio = None, None

    return {
        "glb": str(glb),
        "n_unique_edges": int(len(uniq)),
        "n_boundary_edges": n_boundary,
        "n_interior_edges": n_interior_single,
        "n_seam_edges": int(len(seam_de)),
        "seam_uv_dist_median": float(np.median(seam_uv_dist)),
        "seam_dE00_mean": float(seam_de.mean()),
        "seam_dE00_median": float(np.median(seam_de)),
        "seam_dE00_p90": float(np.percentile(seam_de, 90)),
        "seam_dE00_frac_gt5": float((seam_de > 5).mean()),
        "seam_dE00_frac_gt10": float((seam_de > 10).mean()),
        "control_dE00_mean_2px": ctrl_mean,
        "seam_to_control_ratio": ratio,
    }


def coverage_stats(cond_dir: Path, obj: str, glb_name: str) -> dict:
    method = glb_name.replace(f"{obj}_", "").replace("_textured.glb", "")
    out = {}
    for tag, name in (("baked_coverage_frac", f"{obj}_{method}_coverage.png"),
                      ("inpainted_coverage_frac", f"{obj}_{method}_inpainted_coverage.png")):
        p = cond_dir / obj / name
        if p.exists():
            arr = np.asarray(Image.open(p).convert("L"), dtype=np.float64) / 255.0
            out[tag] = float(arr.mean())
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for cond, d in sorted(BAKE_DIRS.items()):
        if not d.exists():
            print(f"skip missing {cond}: {d}")
            continue
        for obj_dir in sorted(d.iterdir()):
            if not obj_dir.is_dir():
                continue
            obj = obj_dir.name
            glbs = sorted(obj_dir.glob("*_textured.glb"))
            if not glbs:
                continue
            print(f"auditing {cond}/{obj} ...", flush=True)
            res = audit_glb(glbs[0])
            res.update({"condition": cond, "object": obj})
            res.update(coverage_stats(d, obj, glbs[0].name))
            rows.append(res)

    fields = sorted({k for r in rows for k in r})
    with (OUT / "SEAM_AUDIT_PER_OBJECT.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    agg = {}
    for cond in sorted({r["condition"] for r in rows}):
        sub = [r for r in rows if r["condition"] == cond and r.get("n_seam_edges", 0)]
        if not sub:
            continue
        ctrl = [r["control_dE00_mean_2px"] for r in sub if r.get("control_dE00_mean_2px") is not None]
        rat = [r["seam_to_control_ratio"] for r in sub if r.get("seam_to_control_ratio") is not None]
        agg[cond] = {
            "n_objects": len(sub),
            "seam_dE00_mean_of_means": float(np.mean([r["seam_dE00_mean"] for r in sub])),
            "seam_dE00_median": float(np.median([r["seam_dE00_median"] for r in sub])),
            "seam_dE00_p90_mean": float(np.mean([r["seam_dE00_p90"] for r in sub])),
            "seam_dE00_frac_gt5_mean": float(np.mean([r["seam_dE00_frac_gt5"] for r in sub])),
            "seam_dE00_frac_gt10_mean": float(np.mean([r["seam_dE00_frac_gt10"] for r in sub])),
            "control_dE00_mean_2px": float(np.mean(ctrl)) if ctrl else None,
            "seam_to_control_ratio_mean": float(np.mean(rat)) if rat else None,
            "baked_coverage_frac_mean": float(np.mean([r["baked_coverage_frac"] for r in sub if "baked_coverage_frac" in r])),
        }
    (OUT / "SEAM_AUDIT_AGGREGATES.json").write_text(json.dumps(agg, indent=2) + "\n")
    print(json.dumps(agg, indent=2))


if __name__ == "__main__":
    main()
