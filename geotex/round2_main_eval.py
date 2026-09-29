"""Full four-condition main-adapter evaluation for the second revision.

The runner is intentionally independent from the round-two statistics helpers:
it performs inference only and writes long and per-condition object CSVs.
The caller may inject ``target_view_mode=unique6`` into the loaded config.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torchvision.utils import save_image

from eval_exploration import (
    compute_metrics,
    generate,
    get_lpips_fn,
    load_model,
)
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from omegaconf import OmegaConf


SCHEDULES = {
    "no_adapter": {"scale": 0.0, "timestep_schedule": None},
    "fixed_low": {"scale": 1.25, "timestep_schedule": None},
    "fixed_high": {"scale": 2.50, "timestep_schedule": None},
    "c3": {"scale": None, "timestep_schedule": {"early": 1.25, "mid": 2.50, "late": 1.25}},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metric_columns(row: dict[str, object]) -> list[str]:
    return [key for key in row if key not in {"object", "schedule", "object_idx"}]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--num_objects", type=int, default=300)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument(
        "--object-list-file",
        type=Path,
        default=None,
        help="explicit UID list; when supplied, it is used instead of the config validation list",
    )
    args = parser.parse_args()

    # Dataset preprocessing uses Python/NumPy RNGs in addition to PyTorch.
    # Future reruns must control all three before dataset construction.
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = torch.device(args.device)
    dtype = torch.float16
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_dir = output_dir / "predictions"
    for name in [*SCHEDULES, "ground_truth"]:
        (prediction_dir / name).mkdir(parents=True, exist_ok=True)

    print("Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    validation_config = config.data.params.validation
    validation_config.params.target_view_mode = "unique6"
    if args.object_list_file is not None:
        if not args.object_list_file.is_file():
            raise FileNotFoundError(args.object_list_file)
        validation_config.params.object_list_file = str(args.object_list_file.resolve())
    dataset = __import__("src.utils.train_util", fromlist=["instantiate_from_config"]).instantiate_from_config(
        validation_config
    )
    if getattr(dataset, "target_view_mode", None) != "unique6":
        raise RuntimeError("refusing to run: dataset did not instantiate with target_view_mode=unique6")
    num_objects = min(args.num_objects, len(dataset))
    lpips_fn = get_lpips_fn(device)
    print(f"Dataset={len(dataset)}, evaluating={num_objects}, steps={args.steps}, seed={args.seed}", flush=True)

    manifest = {
        "protocol": "round2-main-adapter-four-condition-v1",
        "config": str(args.config),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": sha256(Path(args.checkpoint)),
        "num_objects": num_objects,
        "object_ids": [f"obj_{idx:04d}" for idx in range(num_objects)],
        "object_list_file": str(args.object_list_file.resolve()) if args.object_list_file else None,
        "object_list_sha256": sha256(args.object_list_file) if args.object_list_file else None,
        "object_uids": [line.strip() for line in args.object_list_file.read_text().splitlines() if line.strip()]
        if args.object_list_file
        else None,
        "steps": args.steps,
        "seed": args.seed,
        "device": args.device,
        "schedules": SCHEDULES,
        "shared_initial_latents": True,
        "shared_reference_gt_camera": True,
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
    }
    (output_dir / "evaluation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    rows_by_schedule: dict[str, list[dict[str, object]]] = {name: [] for name in SCHEDULES}
    long_rows: list[dict[str, object]] = []

    for obj_idx in range(num_objects):
        object_seed = args.seed + obj_idx
        random.seed(object_seed)
        np.random.seed(object_seed)
        torch.manual_seed(object_seed)
        object_id = f"obj_{obj_idx:04d}"
        batch = collate_batch(dataset, obj_idx, device)
        _, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = prepare_batch(
            batch, model.img_size, device
        )
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)

        edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
        edge_mask = compute_edge_mask(edge_source, threshold=0.1)
        if edge_mask.shape[2:] != target_imgs.shape[2:]:
            edge_mask = torch.nn.functional.interpolate(edge_mask, size=target_imgs.shape[2:])

        for schedule_name, schedule in SCHEDULES.items():
            torch.manual_seed(args.seed)
            prediction = generate(
                model,
                batch,
                device,
                dtype,
                None if schedule_name == "no_adapter" else geo_feats,
                schedule["scale"],
                args.steps,
                shared_latents,
                timestep_schedule=schedule["timestep_schedule"],
            )
            metrics = compute_metrics(prediction, target_imgs, mask, edge_mask, lpips_fn, device)
            row = {"object": object_id, "object_idx": obj_idx, "schedule": schedule_name, **metrics}
            rows_by_schedule[schedule_name].append(row)
            long_rows.append(row)
            save_image(prediction, prediction_dir / schedule_name / f"{object_id}.png")
            if schedule_name == "no_adapter":
                save_image(target_imgs, prediction_dir / "ground_truth" / f"{object_id}.png")
            del prediction

        del batch, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask, geo_feats, edge_mask
        torch.cuda.empty_cache()
        if (obj_idx + 1) % 10 == 0 or obj_idx == num_objects - 1:
            print(f"[{obj_idx + 1}/{num_objects}] {object_id}", flush=True)

    fields = ["object", "object_idx", "schedule"] + metric_columns(long_rows[0])
    with (output_dir / "per_object_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(long_rows)

    for schedule_name, rows in rows_by_schedule.items():
        path = output_dir / f"per_object_{schedule_name}.csv"
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Done. Wrote {len(long_rows)} rows to {output_dir}", flush=True)


if __name__ == "__main__":
    main()
