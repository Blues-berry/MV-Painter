#!/usr/bin/env python
"""Robustness-1 input-realization difference statistics (task item 11).

For every strict-276 object, build the reference-preprocessing realization
twice — Realization-0 (object_seed = 42 + idx) and Realization-1
(object_seed = 10042 + idx) — and quantify how much the conditioning input
actually differs. Purpose: prove R1 is a genuinely independent preprocessing
realization, not a near-duplicate of R0. No third augmentation is introduced
and no schedule is touched.

Per object, recorded passively (RNG draw sequence untouched):
- stretch/compress scales consumed by MVPainterData.random_stretch_or_compress
  (two random.uniform draws per load; random_resize ratio is a constant 0.8);
- pixel MAE between the two effective conditioning tensors (the img_size
  resize actually consumed by generation);
- SSIM between them (geotex.metrics.compute_ssim, same implementation as the
  official metric path);
- VAE conditioning-latent L2 norms, latent L2 difference, cosine similarity
  (encode seeded identically for both sides so the latent_dist.sample() noise
  cancels — the difference is purely input-driven).

Resume: rows already present in the output CSV are skipped.
"""

from __future__ import annotations

import csv
import json
import random
import statistics
import sys
from pathlib import Path

import numpy as np
import torch
import torchvision.transforms.v2 as v2

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee  # noqa: E402
from data_utils import collate_batch  # noqa: E402
from metrics import compute_ssim  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402

CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
OUT_DIR = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
CSV_PATH = OUT_DIR / "REFERENCE_REALIZATION_DIFFERENCE.csv"

SEED_R0 = 42
SEED_R1 = 10042
ENCODE_SEED = 777  # identical eps stream for both sides' VAE latent sampling

FIELDS = [
    "object_idx", "object",
    "r0_scale_width", "r0_scale_height", "r1_scale_width", "r1_scale_height",
    "cond_mae", "cond_ssim",
    "cond_lat_norm_r0", "cond_lat_norm_r1",
    "cond_lat_l2_diff", "cond_lat_cosine",
]


def effective_cond(batch, img_size: int) -> torch.Tensor:
    cond = batch["cond_imgs"]
    return v2.functional.resize(cond, img_size, interpolation=3, antialias=True).clamp(0, 1)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0")

    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    from omegaconf import OmegaConf
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    dataset = instantiate_from_config(validation)
    if len(dataset) != 276:
        raise RuntimeError(f"expected 276 objects, got {len(dataset)}")
    object_ids = [f"obj_{idx + 24:04d}" for idx in range(len(dataset))]

    # Passive recording of random.uniform draws + stretch calls. The recorded
    # wrapper returns the original values, so the realization is untouched.
    orig_uniform = random.uniform
    uniform_draws: list[float] = []

    def recording_uniform(a, b):
        value = orig_uniform(a, b)
        uniform_draws.append(value)
        return value

    random.uniform = recording_uniform

    stretch_calls: list[tuple[float, float]] = []
    orig_stretch = dataset.random_stretch_or_compress

    def logged_stretch(image, min_scale=0.5, max_scale=1.5):
        start = len(uniform_draws)
        out = orig_stretch(image, min_scale, max_scale)
        stretch_calls.append(tuple(uniform_draws[start:]))
        return out

    dataset.random_stretch_or_compress = logged_stretch

    done: set[int] = set()
    if CSV_PATH.exists():
        with CSV_PATH.open() as handle:
            done = {int(r["object_idx"]) for r in csv.DictReader(handle)}
        print(f"resuming: {len(done)} objects already recorded", flush=True)
    else:
        with CSV_PATH.open("w", newline="") as handle:
            csv.DictWriter(handle, fieldnames=FIELDS).writeheader()

    out_rows: list[dict] = []
    for obj_idx in range(len(dataset)):
        if obj_idx in done:
            continue
        object_id = object_ids[obj_idx]
        record = {"object_idx": obj_idx, "object": object_id}
        lats: dict[str, torch.Tensor] = {}
        conds: dict[str, torch.Tensor] = {}

        for label, base in (("r0", SEED_R0), ("r1", SEED_R1)):
            start_draws = len(stretch_calls)
            random.seed(base + obj_idx)
            np.random.seed(base + obj_idx)
            torch.manual_seed(base + obj_idx)
            batch = collate_batch(dataset, obj_idx, device)
            scales = stretch_calls[start_draws]
            if len(scales) != 2:
                raise RuntimeError(
                    f"expected 2 stretch draws for {object_id} {label}, got {len(scales)}"
                )
            cond = effective_cond(batch, model.img_size)
            conds[label] = cond
            record[f"{label}_scale_width"] = scales[0]
            record[f"{label}_scale_height"] = scales[1]
            torch.manual_seed(ENCODE_SEED)
            with torch.no_grad():
                lat = model.encode_condition_image(cond).float()
            lats[label] = lat
            del batch

        a, b = conds["r0"], conds["r1"]
        la, lb = lats["r0"], lats["r1"]
        record["cond_mae"] = (a - b).abs().mean().item()
        record["cond_ssim"] = compute_ssim(a.squeeze(0), b.squeeze(0))
        record["cond_lat_norm_r0"] = la.norm().item()
        record["cond_lat_norm_r1"] = lb.norm().item()
        record["cond_lat_l2_diff"] = (la - lb).norm().item()
        record["cond_lat_cosine"] = (
            torch.nn.functional.cosine_similarity(
                la.flatten().unsqueeze(0), lb.flatten().unsqueeze(0)
            ).item()
        )
        out_rows.append(record)
        with CSV_PATH.open("a", newline="") as handle:
            csv.DictWriter(handle, fieldnames=FIELDS).writerow(record)
        if obj_idx % 25 == 0:
            print(f"[{obj_idx + 1}/276] {object_id} mae={record['cond_mae']:.4f} ssim={record['cond_ssim']:.4f}", flush=True)
        del a, b, la, lb, conds, lats
        torch.cuda.empty_cache()

    # distribution summary over all recorded rows
    with CSV_PATH.open() as handle:
        all_rows = list(csv.DictReader(handle))
    summary = {"n_objects": len(all_rows), "seed_rule": {"r0": "42+idx", "r1": "10042+idx"}}
    for field in FIELDS[2:]:
        values = [float(r[field]) for r in all_rows]
        values.sort()
        n = len(values)
        summary[field] = {
            "median": statistics.median(values),
            "iqr": [values[int(0.25 * (n - 1))], values[int(0.75 * (n - 1))]],
            "p05": values[int(0.05 * (n - 1))],
            "p95": values[int(0.95 * (n - 1))],
            "mean": statistics.mean(values),
        }
    (OUT_DIR / "REFERENCE_REALIZATION_DIFFERENCE_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps({k: v for k, v in summary.items() if k in
                      ("n_objects", "cond_mae", "cond_ssim", "cond_lat_l2_diff")}, indent=1))
    print("done", flush=True)


if __name__ == "__main__":
    main()
