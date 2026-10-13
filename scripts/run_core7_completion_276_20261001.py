#!/usr/bin/env python
"""Core-7 same-runner completion: strict-276 no_adapter + global_fixed_high.

Protocol is frozen in final/round2/coordination/
core7_same_runner_completion_20261001/PROTOCOL_LOCK_CORE7_COMPLETION.md
(written before these runs). Per-object-per-method code path is a verbatim
copy of the frozen scripts/run_layer_confirmation_276_20260930.py (protocol
layer-confirmation-strict276-v1), R0 namespace (object_seed = 42 + idx).
Only parameterized: MVP_RUN_DIR, MVP_SCHEDULES (filtered to the frozen
additions + the GFL preflight anchor), MVP_OBJECT_LIMIT / MVP_OBJECT_INDICES
(preflight only), MVP_DEVICE. Confirmation surface only; no re-selection.
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
    str(ROOT / "final/round2/coordination/core7_same_runner_completion_20261001"),
))
SCHEDULE_FILTER = os.environ.get("MVP_SCHEDULES", "")
OBJECT_LIMIT = int(os.environ.get("MVP_OBJECT_LIMIT", "0"))  # 0 = all 276
OBJECT_INDICES = os.environ.get("MVP_OBJECT_INDICES", "")  # comma list, preflight only
STEPS = 50


def stage(progress: float, early: float, middle: float, late: float) -> float:
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def no_adapter(progress: float) -> float:
    # geo_feats=None bypasses the adapter entirely; the returned scale is
    # unused by the wrapper in that state (kept for code-path identity).
    return 0.0


def global_fixed_low(progress: float) -> float:
    # Preflight anchor only: pairs this runner against the frozen R0 rows.
    return 1.25


def global_fixed_high(progress: float) -> float:
    return 2.50


ALL_SCHEDULES = {
    "no_adapter": no_adapter,
    "global_fixed_low": global_fixed_low,
    "global_fixed_high": global_fixed_high,
}
ALLOWED = {"no_adapter", "global_fixed_high", "global_fixed_low"}

SCHEDULES = dict(ALL_SCHEDULES)
if SCHEDULE_FILTER:
    wanted = [s.strip() for s in SCHEDULE_FILTER.split(",") if s.strip()]
    unknown = [s for s in wanted if s not in ALLOWED]
    if unknown:
        raise RuntimeError(f"schedules outside the frozen Core-7 additions: {unknown}")
    SCHEDULES = {k: ALL_SCHEDULES[k] for k in wanted}

SCHEDULE_VALUES = {
    "no_adapter": "adapter bypassed (geo_feats=None); nominal scale 0.0 unused",
    "global_fixed_low": 1.25,
    "global_fixed_high": 2.50,
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


def csv_row(row: dict) -> dict:
    return {k: v for k, v in row.items() if k != "input_hashes"}


def write_method_csv(rows, schedule: str) -> None:
    subset = [csv_row(r) for r in rows if r["schedule"] == schedule]
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
    subset = [csv_row(r) for r in rows]
    fields = list(subset[0])
    temporary = RUN_DIR / "per_object_metrics.csv.tmp"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(subset)
    temporary.replace(RUN_DIR / "per_object_metrics.csv")


def protocol_manifest() -> dict:
    return {
        "protocol": "layer-confirmation-strict276-v1 (verbatim per-object code path)",
        "task": "Core-7 same-runner completion (pre-registered)",
        "realization": "realization0_namespace (object_seed = 42 + object_idx)",
        "reference_seed_policy": (
            "object_seed = 42 + object_idx for python random / numpy / torch "
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
        "no_adapter_semantics": (
            "geo_feats computed for RNG-code-path identity but NOT set on wrappers; "
            "GeoTexResnetWrapper skips correction when _current_geo_feats is None "
            "= unmodified pipeline (precedent geotex/round2_main_eval.py no_adapter)"
        ),
        "pre_registration": (
            "final/round2/coordination/core7_same_runner_completion_20261001/"
            "PROTOCOL_LOCK_CORE7_COMPLETION.md"
        ),
        "in_run_integrity": (
            "per object, cond/target/normal/depth/global_embeds/init-latent tensors must "
            "hash identically across the schedules in this process; abort on any mismatch"
        ),
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

    if OBJECT_INDICES:
        object_range = [int(x) for x in OBJECT_INDICES.split(",") if x.strip()]
    elif OBJECT_LIMIT > 0:
        object_range = range(min(OBJECT_LIMIT, len(object_ids)))
    else:
        object_range = range(len(object_ids))

    expected_total = len(list(object_range)) * len(SCHEDULES)
    print(
        f"core7 run: device={device} schedules={sorted(SCHEDULES)} "
        f"objects={len(list(object_range))} done={len(completed)}/{expected_total}",
        flush=True,
    )

    for obj_idx in object_range:
        object_id = object_ids[obj_idx]
        pending = [s for s in sorted(SCHEDULES) if (obj_idx, s) not in completed]
        if not pending:
            continue
        object_seed = 42 + obj_idx
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
            geo_feats_arg = None if schedule_name == "no_adapter" else geo_feats
            pred = exp.generate_with_schedule(
                model, batch, device, dtype, geo_feats_arg, SCHEDULES[schedule_name], STEPS,
                init_latents.clone(), {},
            )
            metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
            # -------------------------------------------------------------------
            # shared-input integrity across the schedules of this process.
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
                "seed_base": 42,
                "elapsed_seconds": time.time() - started,
                **{k: float(v) for k, v in metrics.items()},
                "input_hashes": integrity,
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
        done = sum(1 for o in object_range for s in SCHEDULES
                   if (int(o), s) in {(int(r["object_idx"]), r["schedule"]) for r in rows})
        print(f"[{done}/{expected_total}] {object_id} device={device}", flush=True)

    atomic_json(
        RUN_DIR / "run_manifest.json",
        {**protocol_manifest(), "status": "complete", "row_count": len(rows)},
    )
    print(f"saved {len(rows)} rows (schedules={sorted(SCHEDULES)})", flush=True)


if __name__ == "__main__":
    main()
