#!/usr/bin/env python3
"""Offline texture-fidelity extension for validation-v3 prediction panels.

Mirrors scripts/audit_strict276_texture_20261001.py Part B conventions exactly:
  * masks + GT grids rebuilt on CPU through the exact runner dataset path
    (collate_batch -> prepare_batch, alpha branch, unique6)
  * masked CIEDE2000 with erosion_radius=1 (geotex.round2_texture)
  * variation_diagnostics -> symmetric log errors vs GT
  * PNG reload of predictions/<condition>/<uid>.png (3x2 view grid, 256px)

No generation, no GPU. Writes <run_dir>/texture_extension_per_object.csv with
columns <condition>:ciede2000, <condition>:logerr_{laplacian_variance,
rgb_std,gradient_magnitude}, plus <condition>:hf_logerr (symmetric log error
of GT-relative HF energy) when computable.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

CONFIG = ROOT / "final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/clean_holdout.yaml"


def build_masks_and_gt(config: Path, object_list: Path, data_root: Path,
                       cache_dir: Path | None = None):
    """Masks + GT grids via the exact runner dataset path.

    data_root MUST point at the tree containing the cohort's object dirs
    (the dataset silently substitutes random objects when a dir is missing —
    a wrong root spins forever). Results are cached as .npz per object so
    later campaigns reuse them byte-identically.
    """
    import contextlib
    import io
    import torch  # local import: heavy
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from data_utils import collate_batch, prepare_batch

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
    masks, gts = {}, {}
    missing_cache = []
    n = sum(1 for l in object_list.open() if l.strip())
    for idx in range(n):
        cpath = cache_dir / f"{idx:04d}.npz" if cache_dir is not None else None
        if cpath is not None and cpath.exists():
            z = np.load(cpath)
            masks[idx], gts[idx] = z["mask"], z["gt"]
            continue
        missing_cache.append(idx)
    if not missing_cache:
        print(f"  mask/gt cache hit for all {n} objects", flush=True)
        return masks, gts

    config = OmegaConf.load(config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(object_list.resolve())
    validation.params.root_dir_list = [str(data_root.resolve())]
    dataset = instantiate_from_config(validation)
    for idx in missing_cache:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):  # dataset prints per item
            batch = collate_batch(dataset, idx, device="cpu")
            _, target, _, _, _, mask = prepare_batch(batch, 256, "cpu")
        masks[idx] = mask[0, 0].numpy().astype(np.float32)
        gts[idx] = target[0].permute(1, 2, 0).numpy().astype(np.float32)
        if cache_dir is not None:
            np.savez_compressed(cache_dir / f"{idx:04d}.npz",
                                mask=masks[idx], gt=gts[idx])
        if (idx + 1) % 50 == 0:
            print(f"  mask/gt rebuild {idx + 1}/{n}", flush=True)
    return masks, gts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--object-list", required=True)
    ap.add_argument("--conditions", required=True, help="comma list")
    ap.add_argument("--data-root", default="/4T/CXY/MV-Painter/data/fresh_confirm_v3_renders")
    ap.add_argument("--mask-cache", default=None,
                    help="dir for per-object mask/GT npz cache (strongly recommended)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from geotex.round2_texture import (
        masked_ciede2000,
        texture_stat_errors,
        variation_diagnostics,
    )

    run_dir = Path(args.run_dir)
    uids = [l.strip() for l in Path(args.object_list).open() if l.strip()]
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    cache_dir = Path(args.mask_cache) if args.mask_cache else None
    masks, gt_grids = build_masks_and_gt(CONFIG, Path(args.object_list),
                                         Path(args.data_root), cache_dir)
    assert len(masks) == len(uids), (len(masks), len(uids))

    from PIL import Image

    rows_out = []
    excluded = []
    for idx, uid in enumerate(uids):
        gt = gt_grids[idx]
        mask = masks[idx]
        gt_stats = variation_diagnostics(gt, mask)
        if not all(np.isfinite(v) for v in gt_stats.values()):
            excluded.append(uid)
            rows_out.append({"object_uid": uid, "object_idx": idx})
            continue
        row = {"object_uid": uid, "object_idx": idx}
        for cond in conditions:
            pred_path = run_dir / "predictions" / cond / f"{uid}.png"
            if not pred_path.exists():
                row[f"{cond}:missing"] = 1
                continue
            pred = np.asarray(Image.open(pred_path).convert("RGB")).astype(np.float32) / 255.0
            if pred.shape != gt.shape:
                raise RuntimeError(f"{uid}/{cond}: shape mismatch {pred.shape} vs {gt.shape}")
            row[f"{cond}:ciede2000"] = masked_ciede2000(pred, gt, mask, erosion_radius=1)
            pred_stats = variation_diagnostics(pred, mask)
            errors = texture_stat_errors(pred_stats, gt_stats)["symmetric_log_error"]
            for name, value in errors.items():
                row[f"{cond}:logerr_{name}"] = value
        rows_out.append(row)
        if idx % 50 == 0:
            print(f"  texture extension {idx + 1}/{len(uids)}", flush=True)
    if excluded:
        print(f"excluded (empty eroded foreground): {excluded}")

    fields = ["object_uid", "object_idx"]
    for r in rows_out:
        for k in r:
            if k not in fields:
                fields.append(k)
    out_path = Path(args.out) if args.out else run_dir / "texture_extension_per_object.csv"
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    sys.exit(main())
