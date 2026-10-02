#!/usr/bin/env python3
"""Phase III Experiment D/F visualization-object selection (GT-only).

Protocol rules (Experiments D and F):
  * stratify the FROZEN fresh cohort using GT-only properties BEFORE any
    method outcome is inspected:
      - texture complexity: tercile of mean GT foreground Laplacian variance
        over the six target views (same kernel family as
        geotex/metrics_extended.py fg_laplacian_variance)
      - foreground coverage: tercile of mean alpha coverage over the six
        target views
      - geometry complexity: tercile of log10(GLB face count) as a tertiary
        diversity axis within strata cells
  * select 24 objects deterministically (seed 20261002), 2-3 per 3x3 cell,
    spreading geometry terciles within each cell
  * freeze visualization_24.txt + manifest BEFORE method metrics are read

Inputs: the frozen cohort list and the fresh render tree.
Outputs (this directory): visualization_24.txt, visualization_24_manifest.csv,
stratification_table.csv, stratification_summary.json
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
RENDER_DIR = ROOT / "data/fresh_confirm_v3_renders"
TARGET_VIEWS = [0, 15, 12, 16, 13, 14]
SEED = 20261002
N_SELECT = 24

LAP_KERNEL = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def gt_stats_for(uid: str) -> dict:
    d = Path(RENDER_DIR) / uid
    laps, covs = [], []
    for v in TARGET_VIEWS:
        img = np.asarray(Image.open(d / "image" / f"{v:03d}.png").convert("RGBA"), dtype=np.float32) / 255.0
        alpha = img[:, :, 3]
        mask = alpha > 0.5
        covs.append(float(alpha.mean()))
        gray = img[:, :, :3].mean(axis=2)
        lap = np.abs(_conv2d(gray, LAP_KERNEL))
        laps.append(float(lap[mask].var()) if mask.sum() > 10 else 0.0)
    return {"texture": float(np.mean(laps)), "coverage": float(np.mean(covs))}


def _conv2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    # simple 3x3 convolution with zero padding (matches torch conv semantics)
    ph, pw = 1, 1
    padded = np.pad(img, ((ph, ph), (pw, pw)), mode="constant")
    out = np.zeros_like(img)
    for i in range(3):
        for j in range(3):
            out += kernel[i, j] * padded[i:i + img.shape[0], j:j + img.shape[1]]
    return out


def face_count(uid: str) -> int:
    import trimesh

    base = "/home/ubuntu/.objaverse/hf-objaverse-v1/glbs"
    for shard in sorted(__import__("os").listdir(base)):
        p = Path(base) / shard / f"{uid}.glb"
        if p.exists():
            scene = trimesh.load(str(p), force="scene", process=False)
            n = 0
            for g in scene.geometry.values():
                if hasattr(g, "faces"):
                    n += len(g.faces)
            return n
    return 0


def terciles(values: dict) -> dict:
    keys = sorted(values)
    v = np.array([values[k] for k in keys])
    q1, q2 = np.quantile(v, [1 / 3, 2 / 3])
    return {k: int(np.digitize(values[k], [q1, q2])) for k in keys}  # 0,1,2


def main() -> None:
    cohort_file = Path(sys.argv[1]) if len(sys.argv) > 1 else V3 / "fresh_confirm_300.txt"
    uids = [l.strip() for l in cohort_file.open() if l.strip()]
    print(f"cohort: {cohort_file} ({len(uids)} objects)")

    stats = {}
    for i, uid in enumerate(uids):
        stats[uid] = gt_stats_for(uid)
        stats[uid]["faces"] = face_count(uid)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(uids)}")

    tex_t = terciles({u: s["texture"] for u, s in stats.items()})
    cov_t = terciles({u: s["coverage"] for u, s in stats.items()})
    geo_t = terciles({u: float(np.log10(max(s["faces"], 1))) for u, s in stats.items()})

    cells = {}
    for u in uids:
        cells.setdefault((tex_t[u], cov_t[u]), []).append(u)

    rng = np.random.default_rng(SEED)
    selected = []
    # round-robin across the 9 cells; within a cell, rng-permuted order then
    # spread across geometry terciles (sort by (geo tercile, perm rank))
    cell_keys = sorted(cells)
    iters = {k: 0 for k in cell_keys}
    orders = {k: list(rng.permutation(cells[k])) for k in cell_keys}
    for k in cell_keys:
        orders[k].sort(key=lambda u: (geo_t[u], orders[k].index(u)))
    while len(selected) < N_SELECT:
        progressed = False
        for k in cell_keys:
            if iters[k] < len(orders[k]) and len(selected) < N_SELECT:
                u = orders[k][iters[k]]
                iters[k] += 1
                if u not in selected:
                    selected.append(u)
                    progressed = True
        if not progressed:
            break
    selected.sort()

    # per-view stats table
    with (V3 / "stratification_table.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uid", "gt_texture_lapvar", "gt_coverage", "log10_faces",
                    "texture_tercile", "coverage_tercile", "geometry_tercile"])
        for u in uids:
            w.writerow([u, stats[u]["texture"], stats[u]["coverage"],
                        round(float(np.log10(max(stats[u]["faces"], 1))), 4),
                        tex_t[u], cov_t[u], geo_t[u]])

    with (V3 / "visualization_24.txt").open("w") as f:
        f.write("\n".join(selected) + "\n")

    with (V3 / "visualization_24_manifest.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uid", "gt_texture_lapvar", "gt_coverage", "faces",
                    "texture_tercile", "coverage_tercile", "geometry_tercile"])
        for u in selected:
            w.writerow([u, stats[u]["texture"], stats[u]["coverage"], stats[u]["faces"],
                        tex_t[u], cov_t[u], geo_t[u]])

    summary = {
        "seed": SEED,
        "cohort": str(cohort_file),
        "cohort_sha256": sha256(cohort_file),
        "n_selected": len(selected),
        "target_views": TARGET_VIEWS,
        "cell_counts": {f"tex{k[0]}_cov{k[1]}": len(v) for k, v in sorted(cells.items())},
        "selected_per_cell": {f"tex{k[0]}_cov{k[1]}":
                              sum(1 for u in selected if (tex_t[u], cov_t[u]) == k)
                              for k in cell_keys},
        "rule": "terciles of GT-only texture/coverage; within-cell order spreads "
                "geometry terciles; round-robin across cells; rng seed 20261002; "
                "GT-only, frozen before method metrics were read",
    }
    (V3 / "stratification_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"\nFROZEN -> {V3 / 'visualization_24.txt'}")


if __name__ == "__main__":
    sys.exit(main())
