#!/usr/bin/env python
"""Robustness-1: strict-276 Core-5 runs under an independent pre-frozen
reference-preprocessing realization, plus the pre-registered R0 global_c3
matrix completion.

Per-object-per-method code path is a verbatim copy of the frozen
scripts/run_layer_confirmation_276_20260930.py (protocol
layer-confirmation-strict276-v1). Only three things are parameterized:

- MVP_SEED_BASE   : reference-realization seed namespace.
                    10042 (default) = Realization-1 (this task).
                    42              = Realization-0 namespace; used ONLY for
                    the pre-registered global_c3 matrix completion and the
                    R0 anchor re-check (never for re-selecting anything).
- MVP_SCHEDULES   : comma list filtered to the frozen Core-5.
- MVP_RUN_DIR     : output directory (rows/CSVs/manifest/progress).

Schedule definitions, stage partition, caps semantics, latent seed (42,
re-seeded before generation because the VAE latent sample consumes torch
RNG), metric path, and the 276-object list are FROZEN and identical to the
official confirmation runs. No re-selection of schedules is permitted; see
final/round2/coordination/main_backbone_robustness1_20260930/PROTOCOL_LOCK.md.
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
RUN_DIR = Path(os.environ.get(
    "MVP_RUN_DIR",
    str(ROOT / "final/round2/coordination/main_backbone_robustness1_20260930/realization1_core5"),
))
SEED_BASE = int(os.environ.get("MVP_SEED_BASE", "10042"))
SCHEDULE_FILTER = os.environ.get("MVP_SCHEDULES", "")
OBJECT_LIMIT = int(os.environ.get("MVP_OBJECT_LIMIT", "0"))  # diagnostics only
STEPS = 50


def stage(progress: float, early: float, middle: float, late: float) -> float:
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def global_fixed_low(progress: float) -> float:
    return 1.25


def global_c3(progress: float) -> float:
    return stage(progress, 1.25, 2.50, 1.25)


def layer_llh(progress: float) -> dict[str, float]:
    return {
        "deep": stage(progress, 1.25, 1.25, 2.50),
        "middle": stage(progress, 1.25, 1.25, 2.50),
        "shallow": stage(progress, 0.50, 0.50, 0.75),
    }


def layer_fixed_mean(progress: float) -> dict[str, float]:
    return {"deep": 1.65, "middle": 1.65, "shallow": 0.58}


def layer_lhl(progress: float) -> dict[str, float]:
    return {
        "deep": stage(progress, 1.25, 2.50, 1.25),
        "middle": stage(progress, 1.25, 2.50, 1.25),
        "shallow": stage(progress, 0.50, 0.75, 0.50),
    }


SCHEDULES = {
    "global_fixed_low": global_fixed_low,
    "global_c3": global_c3,
    "layer_fixed_mean": layer_fixed_mean,
    "layer_lhl": layer_lhl,
    "layer_llh": layer_llh,
}

if SCHEDULE_FILTER:
    wanted = [s.strip() for s in SCHEDULE_FILTER.split(",") if s.strip()]
    unknown = [s for s in wanted if s not in SCHEDULES]
    if unknown:
        raise RuntimeError(f"schedules outside the frozen Core-5: {unknown}")
    SCHEDULES = {k: SCHEDULES[k] for k in wanted}

SCHEDULE_VALUES = {
    "global_fixed_low": 1.25,
    "global_c3": [1.25, 2.50, 1.25],
    "layer_fixed_mean": {"deep": 1.65, "middle": 1.65, "shallow": 0.58},
    "layer_lhl": {
        "deep": [1.25, 2.50, 1.25],
        "middle": [1.25, 2.50, 1.25],
        "shallow": [0.50, 0.75, 0.50],
    },
    "layer_llh": {
        "deep": [1.25, 1.25, 2.50],
        "middle": [1.25, 1.25, 2.50],
        "shallow": [0.50, 0.50, 0.75],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def h_tensor(t: torch.Tensor) -> str:
    return hashlib.sha256(
        t.detach().cpu().contiguous().numpy().tobytes()
    ).hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def write_method_csv(rows, schedule: str) -> None:
    subset = [r for r in rows if r["schedule"] == schedule]
    if not subset:
        return
    fields = list(subset[0])
    temporary = RUN_DIR / f"{schedule}_per_object_metrics.csv.tmp"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(subset)
    temporary.replace(RUN_DIR / f"{schedule}_per_object_metrics.csv")


def write_combined_csv(rows) -> None:
    if not rows:
        return
    fields = list(rows[0])
    temporary = RUN_DIR / "per_object_metrics.csv.tmp"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(RUN_DIR / "per_object_metrics.csv")


def protocol_manifest() -> dict:
    realization = "realization1" if SEED_BASE == 10042 else (
        "realization0_namespace" if SEED_BASE == 42 else f"seed_base_{SEED_BASE}"
    )
    return {
        "protocol": "layer-confirmation-strict276-v1 (verbatim per-object code path)",
        "task": "main-backbone Core-5 Robustness-1 (pre-registered)",
        "realization": realization,
        "reference_seed_policy": (
            f"object_seed = {SEED_BASE} + object_idx for python random / numpy / torch "
            "before collate_batch; torch.manual_seed(42) before initial latent and again "
            "immediately before generation (VAE latent sample consumes torch RNG)"
        ),
        "schedules": sorted(SCHEDULES),
        "schedule_values": {k: SCHEDULE_VALUES[k] for k in sorted(SCHEDULES)},
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "object_list": str(OBJECT_LIST),
        "object_list_sha256": sha256(OBJECT_LIST),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "resolution": [256, 256],
        "steps": STEPS,
        "sampler": "EulerDiscreteScheduler",
        "latent_seed": 42,
        "stage_partition": "step/49; early<1/3, middle<2/3 => 17/16/17",
        "scale_semantics": "effective = min(requested, cap deep 3.0 / middle 3.5 / shallow 0.8)",
        "metric_path": "geotex.eval_exploration.compute_metrics",
        "metrics": ["fg_psnr", "fg_ssim", "fg_lpips", "full_psnr", "full_ssim", "full_lpips", "edge_ssim"],
        "pre_registration": "final/round2/coordination/main_backbone_robustness1_20260930/PROTOCOL_LOCK.md",
        "in_run_integrity": "per object, cond/target/normal/depth/global_embeds/init-latent tensors must hash identically across the 5 methods; abort on any mismatch",
        "runner_script_sha256": sha256(Path(__file__).resolve()),
    }


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RUN_DIR / "protocol_manifest.json"
    if not manifest_path.exists():
        atomic_json(manifest_path, protocol_manifest())

    rows_path = RUN_DIR / "rows.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    completed = {(int(r["object_idx"]), r["schedule"]) for r in rows}
    expected_total = 276 * len(SCHEDULES)
    print(
        f"robustness1 run: seed_base={SEED_BASE} schedules={sorted(SCHEDULES)} "
        f"done={len(completed)}/{expected_total}",
        flush=True,
    )

    device = torch.device(os.environ.get("MVP_DEVICE", "cuda:0"))
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

    object_range = range(len(object_ids)) if OBJECT_LIMIT <= 0 else range(min(OBJECT_LIMIT, len(object_ids)))

    for obj_idx in object_range:
        object_id = object_ids[obj_idx]
        pending = [s for s in sorted(SCHEDULES) if (obj_idx, s) not in completed]
        if not pending:
            continue
        object_seed = SEED_BASE + obj_idx
        reference_hashes = None

        for schedule_name in pending:
            # --- verbatim per-object block from the frozen confirmation runner ---
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
                model, batch, device, dtype, geo_feats, SCHEDULES[schedule_name], STEPS,
                init_latents.clone(), {},
            )
            metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
            # -------------------------------------------------------------------
            # in-run shared-input integrity: the five methods must see identical
            # inputs for the same object; abort the formal run on any mismatch.
            integrity = {
                "cond": h_tensor(batch["cond_imgs"]),
                "target": h_tensor(batch["target_imgs"]),
                "normal": h_tensor(batch["depth_imgs"]),
                "depth": h_tensor(batch["real_depth_imgs"]),
                "global_embeds": h_tensor(batch["global_embeds"]),
                "init_latent": h_tensor(init_latents),
            }
            if reference_hashes is None:
                reference_hashes = integrity
            elif integrity != reference_hashes:
                raise RuntimeError(
                    f"shared-input integrity FAILURE at object_idx={obj_idx} "
                    f"({object_id}) schedule={schedule_name}"
                )

            row = {
                "object": object_id,
                "object_idx": obj_idx,
                "schedule": schedule_name,
                "seed_base": SEED_BASE,
                "elapsed_seconds": time.time() - started,
                **{k: float(v) for k, v in metrics.items()},
            }
            rows.append(row)
            rows.sort(key=lambda item: (int(item["object_idx"]), item["schedule"]))
            atomic_json(rows_path, rows)
            write_method_csv(rows, schedule_name)
            write_combined_csv(rows)
            if obj_idx < 2:
                save_image(pred, RUN_DIR / f"{object_id}_{schedule_name}.png")
            del pred, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
            torch.cuda.empty_cache()
        if obj_idx % 25 == 0:
            done = sum(1 for o in object_range for s in SCHEDULES if (o, s) in
                       {(int(r["object_idx"]), r["schedule"]) for r in rows})
            print(f"[{done}/{expected_total}] {object_id} seed_base={SEED_BASE}", flush=True)

    atomic_json(
        RUN_DIR / "run_manifest.json",
        {**protocol_manifest(), "status": "complete", "row_count": len(rows)},
    )
    print(f"saved {len(rows)} rows (seed_base={SEED_BASE}, schedules={sorted(SCHEDULES)})", flush=True)


if __name__ == "__main__":
    main()
