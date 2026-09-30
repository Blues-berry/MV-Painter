#!/usr/bin/env python
"""Strict-276 holdout confirmation runs for pre-registered layer-wise candidates.

Protocol is frozen in
final/round2/coordination/revision_next_20260930/EXPERIMENT_PROTOCOL_LOCK.md
(written before these runs). Same config/checkpoint/object list/seed/metric
path as the layer-LHL official record. Candidates: layer_llh and
layer_fixed_mean. This run is a confirmation surface and must not be used to
re-select schedules.
"""

from __future__ import annotations

import csv
import hashlib
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
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
OUTPUT = Path(os.environ.get(
    "MVP_OUTPUT",
    "/4T/tmp/mvpainter-layer-confirmation-20260930",
))
SCHEDULE_NAME = os.environ.get("MVP_SCHEDULE", "layer_llh")
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


def layer_fixed_mean(progress: float) -> dict[str, float]:
    return {"deep": 1.65, "middle": 1.65, "shallow": 0.58}


SCHEDULES = {"layer_llh": layer_llh, "layer_fixed_mean": layer_fixed_mean}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def write_csv(rows) -> None:
    if not rows:
        return
    fields = list(rows[0])
    temporary = OUTPUT / f"{SCHEDULE_NAME}_per_object_metrics.csv.tmp"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(OUTPUT / f"{SCHEDULE_NAME}_per_object_metrics.csv")


def protocol_manifest() -> dict:
    return {
        "protocol": "layer-confirmation-strict276-v1",
        "status": "confirmation_only; schedule pre-registered on development probes",
        "schedule": SCHEDULE_NAME,
        "schedule_values": {
            "layer_llh": {
                "deep": [1.25, 1.25, 2.50],
                "middle": [1.25, 1.25, 2.50],
                "shallow": [0.50, 0.50, 0.75],
            },
            "layer_fixed_mean": {"deep": 1.65, "middle": 1.65, "shallow": 0.58},
        },
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "object_list": str(OBJECT_LIST),
        "object_list_sha256": sha256(OBJECT_LIST),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "resolution": [256, 256],
        "steps": STEPS,
        "seed": 42,
        "stage_partition": "step/49; early<1/3, middle<2/3 => 17/16/17",
        "scale_semantics": "effective = min(requested, cap deep 3.0 / middle 3.5 / shallow 0.8)",
        "metric_path": "geotex.eval_exploration.compute_metrics",
        "pre_registration": "final/round2/coordination/revision_next_20260930/EXPERIMENT_PROTOCOL_LOCK.md",
        "reference_augmentation_note": "cond image stretch is random per load; paired within run only",
    }


def main() -> None:
    schedule_fn = SCHEDULES[SCHEDULE_NAME]
    (OUTPUT / SCHEDULE_NAME).mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT / f"{SCHEDULE_NAME}_protocol_manifest.json"
    if not manifest_path.exists():
        atomic_json(manifest_path, protocol_manifest())

    rows_path = OUTPUT / f"{SCHEDULE_NAME}_rows.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    completed = {int(row["object_idx"]) for row in rows}

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
    print(
        f"confirmation {SCHEDULE_NAME}: {len(dataset)} objects; done={len(completed)}",
        flush=True,
    )

    for obj_idx, object_id in enumerate(object_ids):
        if obj_idx in completed:
            continue
        object_seed = 42 + obj_idx
        random.seed(object_seed)
        np.random.seed(object_seed)
        torch.manual_seed(object_seed)
        batch = collate_batch(dataset, obj_idx, device)
        _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1)

        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
        torch.manual_seed(42)
        started = time.time()
        pred = exp.generate_with_schedule(
            model, batch, device, dtype, geo_feats, schedule_fn, STEPS,
            init_latents.clone(), {},
        )
        metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
        row = {
            "object": object_id,
            "object_idx": obj_idx,
            "schedule": SCHEDULE_NAME,
            "elapsed_seconds": time.time() - started,
            **{k: float(v) for k, v in metrics.items()},
        }
        rows.append(row)
        rows.sort(key=lambda item: int(item["object_idx"]))
        atomic_json(rows_path, rows)
        write_csv(rows)
        if obj_idx < 2:
            save_image(pred, OUTPUT / SCHEDULE_NAME / f"{object_id}.png")
        if obj_idx % 25 == 0:
            print(f"[{len(rows)}/276] {object_id} fg_lpips={metrics['fg_lpips']:.4f}", flush=True)
        del pred, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
        torch.cuda.empty_cache()

    atomic_json(
        OUTPUT / f"{SCHEDULE_NAME}_run_manifest.json",
        {**protocol_manifest(), "status": "complete", "row_count": len(rows)},
    )
    print(f"saved {len(rows)} rows for {SCHEDULE_NAME}", flush=True)


if __name__ == "__main__":
    main()
