#!/usr/bin/env python
"""Generate 6-view 512x768 panels for the 12-object Exact-GLB baking cohort
under layer-wise schedules, for the extended bake handoff.

Protocol: same checkpoint/config/steps/seed semantics as
run_layer_confirmation_276_20260930.py (which see). Panels use nrow=2 so the
slot->crop mapping matches geotex/build_bake_input_handoff.py
(col = slot % 2, row = slot // 2). Reference-augmentation RNG is seeded per
object (random/np/torch) so reruns are deterministic.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import sys
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
from src.utils.train_util import instantiate_from_config

CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
EVAL_LIST = ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
COHORT = ROOT / "final/round2/main_adapter_clean_v2/exact_baking_cohort_manifest.csv"
OUTPUT = Path("/4T/tmp/mvpainter-layer-bake-input-20260930")
STEPS = 50


def stage(progress: float, early: float, middle: float, late: float) -> float:
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def layer_llh(progress: float) -> dict[str, float]:
    return {
        "deep": stage(progress, 1.25, 1.25, 2.50),
        "middle": stage(progress, 1.25, 1.25, 2.50),
        "shallow": stage(progress, 0.50, 0.50, 0.75),
    }


def layer_lhl(progress: float) -> dict[str, float]:
    return {
        "deep": stage(progress, 1.25, 2.50, 1.25),
        "middle": stage(progress, 1.25, 2.50, 1.25),
        "shallow": stage(progress, 0.50, 0.75, 0.50),
    }


SCHEDULES = {"layer_llh": layer_llh, "layer_lhl": layer_lhl}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    cohort_ids = [row["object"] for row in csv.DictReader(COHORT.open())]
    cohort_indices = [int(object_id.split("_")[1]) for object_id in cohort_ids]
    OUTPUT.mkdir(parents=True, exist_ok=True)

    manifest = {
        "protocol": "layer-bake-input-panels-v1",
        "checkpoint_sha256": sha256(CHECKPOINT),
        "eval_list_sha256": sha256(EVAL_LIST),
        "cohort_objects": cohort_ids,
        "cohort_indices": cohort_indices,
        "steps": STEPS,
        "seed": 42,
        "object_seed": "42 + eval_index",
        "panel_layout": "nrow=2 (512x768); slot i -> col i%2, row i//2",
        "schedules": {
            "layer_llh": {"deep": [1.25, 1.25, 2.50], "middle": [1.25, 1.25, 2.50], "shallow": [0.50, 0.50, 0.75]},
            "layer_lhl": {"deep": [1.25, 2.50, 1.25], "middle": [1.25, 2.50, 1.25], "shallow": [0.50, 0.75, 0.50]},
        },
    }
    (OUTPUT / "generation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    device = torch.device("cuda:0")
    dtype = torch.float16
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(EVAL_LIST.resolve())
    dataset = instantiate_from_config(validation)
    if len(dataset) != 300:
        raise RuntimeError(f"expected 300-object eval dataset, got {len(dataset)}")

    for name, schedule_fn in SCHEDULES.items():
        (OUTPUT / name).mkdir(parents=True, exist_ok=True)
        for object_id, idx in zip(cohort_ids, cohort_indices):
            out_path = OUTPUT / name / f"{object_id}.png"
            if out_path.exists():
                continue
            object_seed = 42 + idx
            random.seed(object_seed)
            np.random.seed(object_seed)
            torch.manual_seed(object_seed)
            batch = collate_batch(dataset, idx, device)
            _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
            geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)
            torch.manual_seed(42)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
            torch.manual_seed(42)
            pred = exp.generate_with_schedule(
                model, batch, device, dtype, geo_feats, schedule_fn, STEPS,
                init_latents.clone(), {},
            )
            save_image(pred, out_path, nrow=2)
            print(f"{name} {object_id} saved; fg_psnr={ee.compute_metrics(pred, target, mask, None, None, device)['fg_psnr']:.3f}", flush=True)
            del pred, batch, target, real_depth, geo_input, mask, geo_feats, init_latents
            torch.cuda.empty_cache()
    print("cohort panels complete", flush=True)


if __name__ == "__main__":
    main()
