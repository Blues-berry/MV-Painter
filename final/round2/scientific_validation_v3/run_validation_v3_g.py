#!/usr/bin/env python
"""Phase III Experiment G runner (MV-Adapter cross-backbone mechanism test).

Reuses the frozen MV-Adapter runner stack (final/round2/mv_adapter) verbatim
for data loading, pipeline preparation, generation call, and metrics
(prepare_pipeline / run_pipeline / object_metrics). New capability: per-point
x per-window scale schedules (3 depth groups x 5 windows) via a monkeypatch of
the pipeline module-level schedule_for_step, with per-step per-point residual
norm logging at the injection multiplication.

Depth-group mapping (FROZEN, EXPERIMENT_G_DESIGN.md):
  shallow = point 0, middle = point 1, deep = points 2 and 3.

Conditions: g_baseline (low everywhere) + g_{layer}_W{w} (high on the
group's points inside the 10-step window). Seed 42 per generation shared
across conditions (paired).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import torch

MV = Path("/4T/CXY/MV-Painter/final/round2/mv_adapter")
ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(MV))
sys.path.insert(0, str(MV / "upstream"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

from scripts.inference_ig2mv_sd import prepare_pipeline, run_pipeline  # noqa: E402
from mvadapter.pipelines import pipeline_mvadapter_i2mv_sd as _pipe_mod  # noqa: E402
from run_experiment import object_metrics, save_grid  # noqa: E402
from geotex.metrics.image_metrics import get_lpips_fn  # noqa: E402

LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)
POINTS_OF = {"deep": [2, 3], "middle": [1], "shallow": [0]}


class PerPointApplier:
    """Returned by the patched schedule_for_step; applied once per injection
    point in list order (the pipeline list comprehension is left-to-right).
    Resets its point counter at every schedule evaluation (= once per step)."""

    def __init__(self, scales, counter, log, step_index):
        self.scales = scales
        self.counter = counter
        self.log = log
        self.step_index = step_index

    def __rmul__(self, state):
        idx = self.counter["i"]
        self.counter["i"] += 1
        s = float(self.scales[idx]) if idx < len(self.scales) else 1.0
        scaled = state * s
        if idx < len(self.scales):
            self.log.setdefault(self.step_index, {})[idx] = {
                "l2": float(scaled.float().norm()),
                "scale": s,
            }
        return scaled


_ORIG_SCHEDULE_FOR_STEP = _pipe_mod.schedule_for_step


def make_patched(schedule_table, counter, log):
    def patched(geometry_scale_schedule, step_index, num_steps):
        if isinstance(geometry_scale_schedule, dict) and geometry_scale_schedule.get("__per_point__"):
            counter["i"] = 0
            scales = geometry_scale_table_at(geometry_scale_schedule, step_index, num_steps)
            log.setdefault("scales", {})[step_index] = list(scales)
            return PerPointApplier(scales, counter, log, step_index)
        return _ORIG_SCHEDULE_FOR_STEP(geometry_scale_schedule, step_index, num_steps)
    return patched


def geometry_scale_table_at(spec, step_index, num_steps):
    base = spec["base"]
    table = list(base)
    layer = spec["layer"]
    w = spec["window"]
    lo, hi = 10 * (w - 1), 10 * w - 1
    if layer is not None and lo <= step_index <= hi:
        for p in POINTS_OF[layer]:
            table[p] = spec["high"]
    return table


def build_condition(condition: str, low: float, high: float) -> dict:
    if condition == "g_baseline":
        return {"__per_point__": True, "base": [low] * 4, "layer": None, "window": 0, "high": None}
    if condition.startswith("g_"):
        body = condition[2:]
        layer, w = body.rsplit("_W", 1)
        return {"__per_point__": True, "base": [low] * 4, "layer": layer,
                "window": int(w), "high": high}
    raise ValueError(condition)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--base-model", type=Path, required=True)
    ap.add_argument("--adapter-path", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--conditions", default="")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--low", type=float, default=0.75)
    ap.add_argument("--high", type=float, default=1.0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--shard", type=int, default=0)
    args = ap.parse_args()

    conditions = (args.conditions.split(",") if args.conditions else
                  ["g_baseline"] + [f"g_{l}_W{w}" for l in LAYERS for w in WINDOWS])

    payload = json.loads(args.manifest.read_text())
    rows = [dict(payload["objects"][payload["holdout_objects"].index(oid)])
            for oid in payload["holdout_objects"]]
    rows = [r for i, r in enumerate(rows) if i % args.num_shards == args.shard]

    device = args.device
    pipe = prepare_pipeline(
        base_model=str(args.base_model), vae_model=None, unet_model=None,
        lora_model=None, adapter_path=str(args.adapter_path), scheduler="ddpm",
        num_views=6, device=device, dtype=torch.float16,
    )
    lpips_fn = get_lpips_fn(device)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "images").mkdir(exist_ok=True)
    (out / "residual_logs").mkdir(exist_ok=True)

    ledger = out / f"rows_shard{args.shard}.json"
    done_rows = json.loads(ledger.read_text()) if ledger.exists() else []
    completed = {(r["object"], r["condition"]) for r in done_rows}

    orig_schedule_for_step = _pipe_mod.schedule_for_step
    counter = {"i": 0}
    log = {}

    fields = ["object", "source_uid", "condition", "elapsed_seconds",
              "psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
              "gt_relative_texture_error"]

    for row in rows:
        pending = [c for c in conditions if (row["object"], c) not in completed]
        if not pending:
            continue
        for condition in pending:
            spec = build_condition(condition, args.low, args.high)
            log.clear()
            _pipe_mod.schedule_for_step = make_patched(spec, counter, log)
            started = time.time()
            try:
                images, _, _, _ = run_pipeline(
                    pipe,
                    mesh_path=row["mesh_path"],
                    num_views=6,
                    text="high quality",
                    image=row["reference_image"],
                    height=512,
                    width=512,
                    num_inference_steps=args.steps,
                    guidance_scale=3.0,
                    seed=args.seed,
                    reference_conditioning_scale=1.0,
                    control_conditioning_scale=1.0,
                    geometry_scale_schedule=spec,
                    device=device,
                )
            finally:
                _pipe_mod.schedule_for_step = orig_schedule_for_step
            metrics = object_metrics(images, row["gt_images_official_order"], lpips_fn, device)
            elapsed = time.time() - started

            rlog = {k: v for k, v in log.items() if k != "scales"}
            (out / "residual_logs" / condition).mkdir(parents=True, exist_ok=True)
            (out / "residual_logs" / condition / (row["object"] + ".json")).write_text(
                json.dumps({"scales": log.get("scales", {}), "norms": rlog}, indent=2))
            save_grid(images, out / "images" / condition / (row["object"] + ".png"))

            done_rows.append({
                "object": row["object"], "source_uid": row["source_uid"],
                "condition": condition, "elapsed_seconds": elapsed,
                **metrics,
            })
            ledger.write_text(json.dumps(done_rows, indent=2))
            print(f"[{len(done_rows)}] {row['object']} {condition} "
                  f"fg_lpips={metrics['fg_lpips']:.4f}", flush=True)

    # final CSV
    with (out / f"per_object_metrics_shard{args.shard}.csv").open("w", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=fields)
        writer.writeheader()
        writer.writerows(done_rows)
    print(f"saved {len(done_rows)} rows", flush=True)


if __name__ == "__main__":
    main()
