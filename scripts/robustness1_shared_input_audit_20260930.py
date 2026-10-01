#!/usr/bin/env python
"""Robustness-1 shared-input preflight audit (R1 seed namespace).

Adapted from scripts/shared_input_determinism_audit_20260930.py (the R0
audit, PASS 2026-09-30). Rebuilds the exact input section of the frozen
strict-276 confirmation runner for 10 fixed strict-276 objects x Core-5
methods and SHA-256 hashes every input artifact — but under the
Realization-1 reference-seed namespace (object_seed = 10042 + obj_idx).

Run twice in separate processes (--tag pass1 / pass2).
ROBUSTNESS1_SHARED_INPUT_AUDIT = PASS iff
  (a) across-method mismatch = 0 within each pass, and
  (b) pass1 vs pass2 mismatch = 0 for every field.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee  # noqa: E402
from data_utils import collate_batch, prepare_batch  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402
from diffusers import EulerDiscreteScheduler  # noqa: E402

CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
OUT_DIR = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
SEED_BASE = int(os.environ.get("MVP_SEED_BASE", "10042"))
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


def layer_fixed_mean(progress: float) -> dict:
    return {"deep": 1.65, "middle": 1.65, "shallow": 0.58}


def layer_lhl(progress: float) -> dict:
    return {
        "deep": stage(progress, 1.25, 2.50, 1.25),
        "middle": stage(progress, 1.25, 2.50, 1.25),
        "shallow": stage(progress, 0.50, 0.75, 0.50),
    }


def layer_llh(progress: float) -> dict:
    return {
        "deep": stage(progress, 1.25, 1.25, 2.50),
        "middle": stage(progress, 1.25, 1.25, 2.50),
        "shallow": stage(progress, 0.50, 0.50, 0.75),
    }


SCHEDULES = {
    "global_fixed_low": global_fixed_low,
    "global_c3": global_c3,
    "layer_fixed_mean": layer_fixed_mean,
    "layer_lhl": layer_lhl,
    "layer_llh": layer_llh,
}


def h_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def h_tensor(t: torch.Tensor) -> str:
    return h_bytes(t.detach().cpu().contiguous().numpy().tobytes())


def h_file(path: Path) -> str:
    return h_bytes(path.read_bytes())


def h_featdict(d: dict) -> str:
    parts = []
    for key in sorted(d.keys(), key=str):
        v = d[key]
        if isinstance(v, torch.Tensor):
            parts.append(f"{key}:{h_tensor(v)}")
        else:
            parts.append(f"{key}:{json.dumps(v, sort_keys=True, default=str)}")
    return h_bytes("|".join(parts).encode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    device = torch.device(os.environ.get("MVP_DEVICE", "cuda:0"))
    dtype = torch.float16

    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    from omegaconf import OmegaConf
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    dataset = instantiate_from_config(validation)
    n = len(dataset)
    if n != 276:
        raise RuntimeError(f"expected 276 objects, got {n}")

    object_ids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    sample = sorted(random.Random(20260930).sample(range(n), 10))

    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(STEPS, device=device)
    sched_record = {
        "timesteps_sha256": h_tensor(scheduler.timesteps.float().cpu()),
        "sigmas_sha256": h_tensor(scheduler.sigmas.float().cpu()),
        "init_noise_sigma": float(scheduler.init_noise_sigma),
        "steps": STEPS,
    }

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    torch.manual_seed(42)
    init_latents_gpu = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
    torch.manual_seed(42)
    init_latents_cpu = torch.randn(1, 4, latent_h, latent_w, dtype=torch.float32)
    latent_record = {"gpu_sha256": h_tensor(init_latents_gpu), "cpu_sha256": h_tensor(init_latents_cpu)}

    rows = []
    for obj_idx in sample:
        object_id = object_ids[obj_idx]
        paths_idx = dataset.paths[obj_idx]
        raw_hashes = {
            "cond_000": h_file(Path(paths_idx) / "image" / "000.png"),
            "cond_014": h_file(Path(paths_idx) / "image" / "014.png"),
            "object_dir": h_bytes(str(paths_idx).encode()),
        }
        for method, schedule_fn in SCHEDULES.items():
            _ = schedule_fn  # schedules are constructed; inputs must not depend on them
            object_seed = SEED_BASE + obj_idx
            random.seed(object_seed)
            np.random.seed(object_seed)
            torch.manual_seed(object_seed)
            batch = collate_batch(dataset, obj_idx, device)
            cond_raw, target, normal, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
            geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)
            with torch.no_grad():
                cond_lat = model.encode_condition_image(cond_raw).to(dtype)

            row = {
                "object": object_id,
                "obj_idx": obj_idx,
                "object_seed": object_seed,
                "method": method,
                "raw_reference": raw_hashes,
                "cond_imgs_raw_sha256": h_tensor(batch["cond_imgs"]),
                "cond_imgs_resized_sha256": h_tensor(cond_raw),
                "cond_lat_sha256": h_tensor(cond_lat),
                "target_imgs_raw_sha256": h_tensor(batch["target_imgs"]),
                "target_grid_sha256": h_tensor(target),
                "normals_raw_sha256": h_tensor(batch["depth_imgs"]),
                "normals_grid_sha256": h_tensor(normal),
                "depth_raw_sha256": h_tensor(batch["real_depth_imgs"]),
                "depth_grid_sha256": h_tensor(real_depth),
                "mask_grid_sha256": h_tensor(mask),
                "geo_clean_sha256": h_tensor(geo_clean),
                "geo_feats_sha256": h_featdict(geo_feats),
                "global_embeds_sha256": h_tensor(batch["global_embeds"]),
                "target_view_mode": "unique6",
            }
            rows.append(row)
            print(f"[{args.tag}] {object_id} {method} done", flush=True)
            del batch, cond_raw, target, normal, real_depth, geo_input, mask, geo_clean, geo_feats, cond_lat
            torch.cuda.empty_cache()

    payload = {
        "audit": "robustness1_shared_input_determinism",
        "tag": args.tag,
        "protocol": "layer-confirmation-strict276-v1 input section, Realization-1 namespace",
        "seed_rule": f"object_seed = {SEED_BASE} + obj_idx (random/np/torch), latent seed 42",
        "config": str(CONFIG),
        "checkpoint_sha256": "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0",
        "object_list_sha256": "a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044",
        "object_sample_indices": sample,
        "schedule_record": sched_record,
        "initial_latent": latent_record,
        "rows": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"ROBUSTNESS1_SHARED_INPUT_AUDIT.{args.tag}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"written {out}", flush=True)


if __name__ == "__main__":
    main()
