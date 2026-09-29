"""Evaluate fixed-mean and equal-mean temporal placement schedules.

The default ``--dry-run`` performs only protocol and schedule checks, which is
safe on a CPU-only host. Formal inference requires the frozen checkpoint and a
CUDA device and is intentionally explicit with ``--run``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
# Make direct execution independent of the caller's working directory.  The
# config targets live under both the repository root and MVPainter/.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

from data_utils import collate_batch, prepare_batch
from eval_exploration import compute_metrics, generate, get_lpips_fn, load_model
from metrics import compute_edge_mask
from geotex.runtime import require_cuda


SCHEDULES = {
    "fixed_mean": {"scale": 5.0 / 3.0, "timestep_schedule": None},
    "hll": {"scale": None, "timestep_schedule": {"early": 2.50, "mid": 1.25, "late": 1.25}},
    "llh": {"scale": None, "timestep_schedule": {"early": 1.25, "mid": 1.25, "late": 2.50}},
    "c3_lhl": {"scale": None, "timestep_schedule": {"early": 1.25, "mid": 2.50, "late": 1.25}},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def expected_stage(index: int, steps: int = 50) -> str:
    frac = index / max(steps - 1, 1)
    if frac < 0.33:
        return "early"
    if frac < 0.66:
        return "mid"
    return "late"


def stage_scale_trace(schedule: dict[str, object], steps: int) -> list[dict[str, object]]:
    if schedule["timestep_schedule"] is None:
        scale = float(schedule["scale"])
        return [{"index": i, "stage": expected_stage(i, steps), "scale": scale} for i in range(steps)]
    values = schedule["timestep_schedule"]
    return [
        {"index": i, "stage": expected_stage(i, steps), "scale": float(values[expected_stage(i, steps)])}
        for i in range(steps)
    ]


def collect_residual_hook(model: torch.nn.Module, records: list[dict[str, float]]):
    """Capture actual scaled adapter correction norms once per UNet call.

    The historical ``generate`` function keeps the correction on each wrapper
    and clears it after the denoising loop.  A UNet forward hook therefore gives
    the post-scale residual for each actual denoising step without changing the
    historical generation code or schedule semantics.
    """

    def hook(_module, _inputs, _output):
        corrections = [
            module._last_correction
            for module in model.unet.modules()
            if getattr(module, "_last_correction", None) is not None
        ]
        if not corrections:
            return
        sum_sq = sum(float(value.float().pow(2).sum().item()) for value in corrections)
        count = sum(value.numel() for value in corrections)
        records.append({
            "l2": math.sqrt(sum_sq),
            "rms": math.sqrt(sum_sq / max(count, 1)),
            "elements": float(count),
        })

    return model.pipeline.unet.register_forward_hook(hook)


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def protocol_check(args: argparse.Namespace) -> dict:
    objects = [x.strip() for x in args.object_list.read_text().splitlines() if x.strip()]
    if len(objects) != 276:
        raise ValueError(f"stage placement protocol requires 276 objects, found {len(objects)}")
    if args.steps != 50 or args.seed != 42:
        raise ValueError("formal protocol is fixed to 50 steps and seed 42")
    expected = {"early": list(range(17)), "mid": list(range(17, 33)), "late": list(range(33, 50))}
    actual = {stage: [i for i in range(args.steps) if expected_stage(i, args.steps) == stage] for stage in expected}
    if actual != expected:
        raise AssertionError(f"stage mapping mismatch: {actual}")
    if not args.config.is_file() or not args.checkpoint.is_file():
        raise FileNotFoundError("config and checkpoint must exist before formal launch")
    return {
        "protocol": "clean-v2-stage-placement-followup-v1",
        "checkpoint": str(args.checkpoint.resolve()),
        "checkpoint_sha256": sha256(args.checkpoint),
        "object_list": str(args.object_list.resolve()),
        "object_list_sha256": sha256(args.object_list),
        "num_objects": len(objects),
        "object_ids": [f"obj_{i + 24:04d}" for i in range(len(objects))],
        "object_uids": objects,
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "resolution": [256, 256],
        "seed": args.seed,
        "steps": args.steps,
        "stage_indices": {"early": list(range(17)), "mid": list(range(17, 33)), "late": list(range(33, 50))},
        "schedules": SCHEDULES,
        "schedule_traces": {name: stage_scale_trace(schedule, args.steps) for name, schedule in SCHEDULES.items()},
        "shared_initial_latents": True,
        "shared_gt_camera_mask": True,
        "runtime_checks": {
            "seed_reset_before_each_schedule": True,
            "shared_initial_latent_per_object": True,
            "schedule_mapping_test": "passed",
            "residual_logging": "actual scaled adapter correction L2/RMS captured by UNet forward hook",
        },
        "followup_status": "pre-specified after clean-v2 inspection; not blind",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--object-list", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run", action="store_true", help="perform formal inference; otherwise dry-run only")
    parser.add_argument("--resume", action="store_true", help="reuse completed per-object JSON records")
    args = parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    manifest = protocol_check(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not args.run:
        manifest["status"] = "dry_run_passed_no_model_loaded"
        (args.output_dir / "stage_placement_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest, indent=2))
        return
    device = require_cuda(args.device, "formal stage-placement inference")
    dtype = torch.float16
    model = load_model(str(args.config), str(args.checkpoint), device)
    config = OmegaConf.load(args.config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(args.object_list.resolve())
    dataset = __import__("src.utils.train_util", fromlist=["instantiate_from_config"]).instantiate_from_config(validation)
    lpips_fn = get_lpips_fn(device)
    prediction_dir = args.output_dir / "predictions"
    record_dir = args.output_dir / "records"
    record_dir.mkdir(parents=True, exist_ok=True)
    error_log = args.output_dir / "errors.jsonl"
    for name in [*SCHEDULES, "ground_truth"]:
        (prediction_dir / name).mkdir(parents=True, exist_ok=True)
    rows = []
    torch.manual_seed(args.seed)
    for obj_idx in range(len(dataset)):
        object_seed = args.seed + obj_idx
        random.seed(object_seed)
        np.random.seed(object_seed)
        torch.manual_seed(object_seed)
        object_id = f"obj_{obj_idx + 24:04d}"
        record_path = record_dir / f"{object_id}.json"
        if args.resume and record_path.is_file():
            try:
                cached = json.loads(record_path.read_text())
                if cached.get("object") == object_id and set(cached.get("rows", {})) == set(SCHEDULES):
                    rows.extend(cached["flat_rows"])
                    continue
            except (OSError, json.JSONDecodeError, KeyError):
                pass
        batch = collate_batch(dataset, obj_idx, device)
        _, target, normal, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(args.seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1)
        object_rows = {}
        flat_rows = []
        residual_logs = {}
        try:
            for name, schedule in SCHEDULES.items():
                torch.manual_seed(args.seed)
                residual_records = []
                hook = collect_residual_hook(model, residual_records)
                started = time.time()
                try:
                    pred = generate(model, batch, device, dtype, geo_feats, schedule["scale"], args.steps, shared_latents, timestep_schedule=schedule["timestep_schedule"])
                finally:
                    hook.remove()
                metrics = compute_metrics(pred, target, mask, edge, lpips_fn, device)
                row = {"object": object_id, "object_idx": obj_idx, "schedule": name, **metrics}
                flat_rows.append(row)
                object_rows[name] = row
                residual_logs[name] = {
                    "steps_observed": len(residual_records),
                    "elapsed_seconds": time.time() - started,
                    "nominal_scale_trace": stage_scale_trace(schedule, args.steps),
                    "actual_scaled_residual": residual_records,
                }
                save_image(pred, prediction_dir / name / f"{object_id}.png")
                if name == "fixed_mean":
                    save_image(target, prediction_dir / "ground_truth" / f"{object_id}.png")
                del pred
            rows.extend(flat_rows)
            atomic_json(record_path, {"object": object_id, "rows": object_rows, "flat_rows": flat_rows, "residual_logs": residual_logs})
        except Exception as exc:
            with error_log.open("a") as handle:
                handle.write(json.dumps({"object": object_id, "object_idx": obj_idx, "error": repr(exc)}) + "\n")
            print(f"ERROR {object_id}: {exc!r}; resume will retry this object", flush=True)
        del batch, target, normal, real_depth, geo_input, mask, geo_feats, edge
        torch.cuda.empty_cache()
        if (obj_idx + 1) % 10 == 0:
            print(f"[{obj_idx + 1}/{len(dataset)}]", flush=True)
    if not rows:
        raise RuntimeError("formal inference produced no completed objects")
    fields = list(rows[0])
    with (args.output_dir / "per_object_metrics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    for name in SCHEDULES:
        with (args.output_dir / f"per_object_{name}.csv").open("w", newline="") as f:
            subset = [r for r in rows if r["schedule"] == name]
            writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(subset)
    completed_objects = {row["object"] for row in rows}
    failed_objects = [f"obj_{i + 24:04d}" for i in range(len(dataset)) if f"obj_{i + 24:04d}" not in completed_objects]
    manifest["status"] = "formal_inference_complete" if not failed_objects else "formal_inference_partial_resume_required"
    manifest["completed_object_count"] = len(completed_objects)
    manifest["failed_objects"] = failed_objects
    manifest["resume_records"] = str(record_dir.resolve())
    manifest["error_log"] = str(error_log.resolve())
    (args.output_dir / "stage_placement_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
