"""Run the complete binary layer-wise stage ablation on the clean-v2 probe.

This file is intentionally outside the repository.  The experiment fixes the
two layer-wise values already used by layer-LHL and enumerates every temporal
low/high pattern (LLL through HHH).  It is a development selection run only;
the strict 276-object holdout is not used for choosing a schedule here.
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
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
OUTPUT = Path(os.environ.get(
    "MVP_OUTPUT",
    "/4T/tmp/mvpainter-recovery-HLzm9O/full_factorial_layer_ablation/probe_run",
))
SEEDS = tuple(
    int(value.strip())
    for value in os.environ.get("MVP_SEEDS", "42,43,44").split(",")
    if value.strip()
)
STEPS = 50

METHODS = ("lll", "llh", "lhl", "lhh", "hll", "hlh", "hhl", "hhh")
LOW = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
HIGH = {"deep": 2.50, "middle": 2.50, "shallow": 0.75}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stage_index(progress: float) -> int:
    if progress < 1.0 / 3.0:
        return 0
    if progress < 2.0 / 3.0:
        return 1
    return 2


def make_schedule(pattern: str):
    if pattern not in METHODS or len(pattern) != 3:
        raise ValueError(f"invalid binary stage pattern: {pattern}")

    def schedule(progress: float) -> dict[str, float]:
        values = HIGH if pattern[stage_index(progress)] == "h" else LOW
        return dict(values)

    return schedule


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def write_csv(rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    temporary = OUTPUT / "per_object_metrics.csv.tmp"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(OUTPUT / "per_object_metrics.csv")


def protocol_manifest() -> dict[str, object]:
    return {
        "protocol": "layer-wise-binary-full-factorial-probe-v1",
        "status": "development_only",
        "checkpoint": str(CHECKPOINT.resolve()),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "object_list": str(OBJECT_LIST.resolve()),
        "object_list_sha256": sha256(OBJECT_LIST),
        "object_count": len([line for line in OBJECT_LIST.read_text().splitlines() if line.strip()]),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "resolution": [256, 256],
        "steps": STEPS,
        "seeds": list(SEEDS),
        "methods": list(METHODS),
        "low_values": LOW,
        "high_values": HIGH,
        "stage_boundaries": {"early": [0, 16], "middle": [17, 32], "late": [33, 49]},
        "shared_inputs": "one collated batch, geo features and initial latent per seed/object reused by all methods",
        "condition_vae_seed_reset_before_each_method": True,
        "selection_metric": "fg_lpips (lower is better), with PSNR/SSIM and edge metrics reported as secondary",
        "holdout_selection": "forbidden; strict-276 is not used to choose a schedule",
    }


def main() -> None:
    if len([line for line in OBJECT_LIST.read_text().splitlines() if line.strip()]) != 24:
        raise RuntimeError("probe protocol requires exactly 24 objects")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for method in METHODS:
        (OUTPUT / "predictions" / method).mkdir(parents=True, exist_ok=True)

    manifest_path = OUTPUT / "protocol_manifest.json"
    if not manifest_path.exists():
        atomic_json(manifest_path, protocol_manifest())

    rows_path = OUTPUT / "rows.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    completed = {
        (int(row["seed"]), int(row["object_idx"]), str(row["schedule"]))
        for row in rows
    }

    device = torch.device("cuda:0")
    dtype = torch.float16
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    dataset = instantiate_from_config(validation)
    lpips_fn = ee.get_lpips_fn(device)

    print(
        f"full factorial probe: {len(dataset)} objects x {len(SEEDS)} seeds x {len(METHODS)} methods; "
        f"completed={len(completed)}",
        flush=True,
    )

    for seed in SEEDS:
        for obj_idx in range(len(dataset)):
            object_id = f"obj_{obj_idx:04d}"
            object_seed = seed + obj_idx
            random.seed(object_seed)
            np.random.seed(object_seed)
            torch.manual_seed(object_seed)
            batch = collate_batch(dataset, obj_idx, device)
            _, target, _, real_depth, geo_input, mask = prepare_batch(
                batch, model.img_size, device
            )
            geo_clean = torch.nan_to_num(
                geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0
            )
            geo_feats = model.geo_encoder(geo_clean)
            edge = compute_edge_mask(real_depth.float(), threshold=0.1)

            torch.manual_seed(object_seed)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            init_latents = torch.randn(
                1, 4, latent_h, latent_w, device=device, dtype=dtype
            )

            for method in METHODS:
                key = (seed, obj_idx, method)
                if key in completed:
                    continue
                residual_log: dict[str, object] = {}
                started = time.time()
                # The condition VAE samples inside generation; this reset is
                # required for exact method pairing, not only for the latent.
                torch.manual_seed(object_seed)
                pred = exp.generate_with_schedule(
                    model,
                    batch,
                    device,
                    dtype,
                    geo_feats,
                    make_schedule(method),
                    STEPS,
                    init_latents.clone(),
                    residual_log,
                )
                metrics = ee.compute_metrics(
                    pred, target, mask, edge, lpips_fn, device
                )
                row = {
                    "seed": seed,
                    "object": object_id,
                    "object_idx": obj_idx,
                    "object_seed": object_seed,
                    "schedule": method,
                    "residual_steps": len(residual_log),
                    "elapsed_seconds": time.time() - started,
                    **{key: float(value) for key, value in metrics.items()},
                }
                rows.append(row)
                completed.add(key)
                rows.sort(key=lambda item: (int(item["seed"]), int(item["object_idx"]), item["schedule"]))
                atomic_json(rows_path, rows)
                write_csv(rows)
                if seed == SEEDS[0] and obj_idx == 0:
                    save_image(pred, OUTPUT / "predictions" / method / f"{object_id}.png")
                del pred
                torch.cuda.empty_cache()

            print(
                f"seed={seed} [{obj_idx + 1}/{len(dataset)}] {object_id} "
                f"rows={len(rows)}",
                flush=True,
            )
            del batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
            torch.cuda.empty_cache()

    atomic_json(
        OUTPUT / "run_manifest.json",
        {
            **protocol_manifest(),
            "status": "complete",
            "row_count": len(rows),
            "expected_row_count": len(SEEDS) * len(dataset) * len(METHODS),
        },
    )
    print(f"saved {len(rows)} rows to {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
