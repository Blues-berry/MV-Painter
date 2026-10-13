"""Temporary official-metric evaluation for the layer-LHL candidate.

This runner is intentionally outside the repository.  It uses the same
checkpoint, clean-v2 holdout, seed, 50 denoising steps, and metric path as the
formal stage-placement evaluation, but replaces the stage-only schedule with
the exploratory layer-and-stage schedule under test.
"""

from __future__ import annotations

import csv
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from src.utils.train_util import instantiate_from_config


CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = Path("/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt")
OBJECT_LIST = Path("/4T/CXY/MV-Painter/final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt")
OUTPUT = Path(os.environ.get(
    "MVP_OUTPUT",
    "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official",
))
START_OBJECT = int(os.environ.get("MVP_START_OBJECT", "0"))
END_OBJECT = int(os.environ.get("MVP_END_OBJECT", "276"))


def stage(progress: float, early: float, middle: float, late: float) -> float:
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def layer_lhl(progress: float) -> dict[str, float]:
    return {
        "deep": stage(progress, 1.25, 2.50, 1.25),
        "middle": stage(progress, 1.25, 2.50, 1.25),
        "shallow": stage(progress, 0.50, 0.75, 0.50),
    }


def save_rows(rows: list[dict[str, object]]) -> None:
    rows_path = OUTPUT / "rows.json"
    temporary = rows_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(rows, indent=2) + "\n")
    temporary.replace(rows_path)


def write_csv(rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    with (OUTPUT / "per_object_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "predictions").mkdir(parents=True, exist_ok=True)
    (OUTPUT / "predictions" / "layer_LHL").mkdir(parents=True, exist_ok=True)
    (OUTPUT / "predictions" / "ground_truth").mkdir(parents=True, exist_ok=True)
    rows_path = OUTPUT / "rows.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    completed = {str(row["object"]) for row in rows}

    device = torch.device("cuda:0")
    dtype = torch.float16
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    dataset = instantiate_from_config(validation)
    lpips_fn = ee.get_lpips_fn(device)
    object_ids = [f"obj_{idx + 24:04d}" for idx in range(len(dataset))]
    if len(object_ids) != 276:
        raise RuntimeError(f"expected 276 objects, got {len(object_ids)}")
    print(f"official layer-LHL: {len(dataset)} objects; already done={len(completed)}", flush=True)

    for obj_idx, object_id in enumerate(object_ids):
        if obj_idx < START_OBJECT or obj_idx >= END_OBJECT:
            continue
        if object_id in completed:
            continue
        object_start = time.time()
        batch = collate_batch(dataset, obj_idx, device)
        _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1)

        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
        # The condition VAE samples inside generate_with_schedule.  Reset the
        # protocol seed immediately before generation so that this stochastic
        # path is deterministic per object and matches the formal runner.
        torch.manual_seed(42)
        residual_log = {}
        pred = exp.generate_with_schedule(
            model, batch, device, dtype, geo_feats, layer_lhl, 50,
            init_latents, residual_log,
        )
        metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
        row = {"object": object_id, "object_idx": obj_idx, "schedule": "layer_LHL", **metrics}
        rows.append(row)
        rows.sort(key=lambda item: int(item["object_idx"]))
        save_rows(rows)
        save_image(pred, OUTPUT / "predictions" / "layer_LHL" / f"{object_id}.png")
        if obj_idx == 0:
            save_image(target, OUTPUT / "predictions" / "ground_truth" / f"{object_id}.png")
        write_csv(rows)
        print(
            f"[{len(rows)}/276] {object_id} full_psnr={metrics['full_psnr']:.4f} "
            f"fg_psnr={metrics['fg_psnr']:.4f} fg_ssim={metrics['fg_ssim']:.4f} "
            f"elapsed={time.time() - object_start:.1f}s",
            flush=True,
        )
        del pred, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
        torch.cuda.empty_cache()

    write_csv(rows)
    print(f"saved {len(rows)} official rows to {OUTPUT}", flush=True)


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    main()
