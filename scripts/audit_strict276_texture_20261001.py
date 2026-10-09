#!/usr/bin/env python
"""Strict-276 offline texture-fidelity audit (final_audit_20261001, Phase 3).

Two evidence parts, no generation, no GPU:

Part A (confirmation set, rescued CSVs): the same-runner Core-4 confirmation
CSVs already carry per-object generation/GT texture probes (fg_rgb_std,
fg_grad_mag, fg_lap_var, fg_hf_energy and their gt_* counterparts) computed by
geotex.eval_exploration at run time. This script reframes them as GT-relative
distances |gen - gt| and runs the paired bootstrap.

Part B (stage-placement images): deterministic offline recomputation from the
retained prediction/GT PNG grids. Masks are rebuilt on CPU through the exact
dataset path used by the runner (collate_batch -> prepare_batch, alpha branch,
unique6). Metrics per object, on the same 3x2 view grid the runner evaluated:
masked_ciede2000(erosion=1) and variation_diagnostics -> symmetric log errors
(geotex.round2_texture conventions, identical to the cross-backbone panels).
Recomputed GT statistics are validated against the runner CSV gt_* columns.

Sign convention (benefit-oriented, per METRIC_SIGN_CONVENTION_ERRATUM):
delta > 0 <=> layer_llh (the first-named condition) is better.
For lower-better metrics delta = other - llh; for higher-better delta = llh - other.

Bootstrap: 10,000 object-level percentile resamples, seed 20260930.

Outputs (under --output-dir):
  partA_confirmation_texture_probes.csv / .json
  partB_per_object_texture.csv
  partB_validation_vs_runner_csv.json
  paired_bootstrap.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

CONFIRM_DIR = ROOT / "final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930"
STAGE_DIR = ROOT / "final/round2/stage_placement_276_20260929"
CONFIG = ROOT / "final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/clean_holdout.yaml"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"

PART_A_PROBES = ["fg_rgb_std", "fg_grad_mag", "fg_lap_var", "fg_hf_energy"]
PART_A_CONDITIONS = ["global_fixed_low", "layer_fixed_mean", "layer_lhl", "layer_llh"]
PART_B_SCHEDULES = ["fixed_mean", "c3_lhl", "hll", "llh"]
HIGHER_BETTER = {"psnr", "fg_ssim", "edge_ssim"}


def read_csv(path: Path) -> dict[str, dict]:
    with path.open(newline="") as handle:
        return {row["object"]: row for row in csv.DictReader(handle)}


def boot_ci(delta: np.ndarray, seed: int, resamples: int = 10000):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(delta), size=(resamples, len(delta)))
    means = delta[idx].mean(axis=1)
    return [float(np.quantile(means, q)) for q in (0.025, 0.975)]


def paired_table(per_object: dict[str, dict[str, float]], metrics: list[str],
                 base: str, others: list[str], seed: int) -> dict:
    """Benefit-oriented paired deltas: positive = base condition better."""
    objects = sorted(per_object)
    out = {}
    for other in others:
        for metric in metrics:
            a = np.array([per_object[o][f"{base}:{metric}"] for o in objects])
            b = np.array([per_object[o][f"{other}:{metric}"] for o in objects])
            delta = (a - b) if metric in HIGHER_BETTER else (b - a)
            mean = float(delta.mean())
            lo, hi = boot_ci(delta, seed)
            out[f"{base}_minus_{other}:{metric}"] = {
                "metric": metric,
                "mean_delta": mean,
                "ci95": [lo, hi],
                "ci_excludes_zero": bool(lo > 0 or hi < 0),
                "win_rate_base": f"{int((delta > 0).sum())}/{len(delta)}",
                "sign_convention": "positive = base better",
            }
    return out


def part_a(output_dir: Path, seed: int) -> dict:
    tables = {c: read_csv(CONFIRM_DIR / f"{c}_per_object_metrics.csv") for c in PART_A_CONDITIONS}
    objects = sorted(tables["layer_llh"])
    per_object: dict[str, dict[str, float]] = {}
    for obj in objects:
        row_out: dict[str, float] = {}
        for cond, table in tables.items():
            for probe in PART_A_PROBES:
                gen = float(table[obj][probe])
                gt = float(table[obj][f"gt_{probe}"])
                row_out[f"{cond}:dist_{probe}"] = abs(gen - gt)
        per_object[obj] = row_out
    metrics = [f"dist_{p}" for p in PART_A_PROBES]
    comparisons = paired_table(per_object, metrics, "layer_llh",
                               ["global_fixed_low", "layer_fixed_mean", "layer_lhl"], seed)
    with (output_dir / "partA_confirmation_texture_probes.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["object", *next(iter(per_object.values()))])
        writer.writeheader()
        for obj in objects:
            writer.writerow({"object": obj, **per_object[obj]})
    return {"n_objects": len(objects), "probes": PART_A_PROBES,
            "distance": "abs(gen - gt), runtime tensors (no PNG reload)",
            "comparisons": comparisons}


def build_masks_and_gt(config: Path, object_list: Path, n_expected: int = 276):
    """Deterministic CPU dataset pass: masks + GT grids identical to the runner path."""
    import torch  # local import: heavy
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from data_utils import collate_batch, prepare_batch

    config = OmegaConf.load(config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(object_list.resolve())
    dataset = instantiate_from_config(validation)
    if len(dataset) != n_expected:
        raise RuntimeError(f"expected {n_expected} objects, got {len(dataset)}")
    masks, gts = {}, {}
    for idx in range(len(dataset)):
        batch = collate_batch(dataset, idx, device="cpu")
        _, target, _, _, _, mask = prepare_batch(batch, 256, "cpu")
        masks[idx] = mask[0, 0].numpy().astype(np.float32)          # (768, 512)
        gts[idx] = target[0].permute(1, 2, 0).numpy().astype(np.float32)  # (768, 512, 3)
        if idx % 50 == 0:
            print(f"  mask/gt rebuild {idx + 1}/{len(dataset)}", flush=True)
    return masks, gts


def part_b(output_dir: Path, seed: int, schedules: list[str]) -> dict:
    from geotex.round2_texture import (
        masked_ciede2000,
        texture_stat_errors,
        variation_diagnostics,
    )

    masks, gt_grids = build_masks_and_gt(CONFIG, OBJECT_LIST)
    objects = [f"obj_{idx + 24:04d}" for idx in range(len(masks))]

    runner_llh = read_csv(STAGE_DIR / "per_object_llh.csv")
    validation = {"note": "PNG-reload + erosion-convention deviation vs runtime tensors",
                  "objects": {}}
    for probe, runner_key in (("laplacian_variance", "gt_fg_lap_var"),
                              ("rgb_std", "gt_fg_rgb_std"),
                              ("gradient_magnitude", "gt_fg_grad_mag")):
        deltas = []
        for idx in (0, 50, 137, 200, 275):
            obj = f"obj_{idx + 24:04d}"
            stats = variation_diagnostics(gt_grids[idx], masks[idx])
            if not all(np.isfinite(v) for v in stats.values()):
                continue
            deltas.append(abs(stats[probe] - float(runner_llh[obj][runner_key])))
        validation["objects"][probe] = {
            "max_abs_deviation_sampled": float(np.max(deltas)),
            "sampled": [f"obj_{i + 24:04d}" for i in (0, 50, 137, 200, 275)],
        }

    per_object: dict[str, dict[str, float]] = {}
    excluded: list[str] = []
    from PIL import Image
    for idx, obj in enumerate(objects):
        gt = gt_grids[idx]
        mask = masks[idx]
        gt_stats = variation_diagnostics(gt, mask)
        if not all(np.isfinite(v) for v in gt_stats.values()):
            excluded.append(obj)  # foreground empty after erosion_radius=1
            continue
        row_out: dict[str, float] = {}
        for sched in schedules:
            pred_path = STAGE_DIR / "predictions" / sched / f"{obj}.png"
            pred = np.asarray(Image.open(pred_path).convert("RGB")).astype(np.float32) / 255.0
            if pred.shape != gt.shape:
                raise RuntimeError(f"{obj}: shape mismatch {pred.shape} vs {gt.shape}")
            dE = masked_ciede2000(pred, gt, mask, erosion_radius=1)
            pred_stats = variation_diagnostics(pred, mask)
            errors = texture_stat_errors(pred_stats, gt_stats)["symmetric_log_error"]
            row_out[f"{sched}:ciede2000"] = dE
            for name, value in errors.items():
                row_out[f"{sched}:logerr_{name}"] = value
        per_object[obj] = row_out
        if idx % 50 == 0:
            print(f"  partB metrics {idx + 1}/{len(objects)}", flush=True)
    if excluded:
        print(f"  excluded (empty eroded foreground): {excluded}", flush=True)

    fields = list(next(iter(per_object.values())))
    with (output_dir / "partB_per_object_texture.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["object", *fields])
        writer.writeheader()
        for obj in sorted(per_object):
            writer.writerow({"object": obj, **per_object[obj]})

    metrics = ["ciede2000", "logerr_laplacian_variance", "logerr_rgb_std",
               "logerr_gradient_magnitude"]
    comparisons = paired_table(per_object, metrics, "llh",
                               [s for s in schedules if s != "llh"], seed)
    (output_dir / "partB_validation_vs_runner_csv.json").write_text(
        json.dumps(validation, indent=2) + "\n")
    return {"n_objects": len(objects), "n_used": len(per_object),
            "n_excluded_empty_eroded_mask": excluded,
            "mask_source": "dataset alpha branch, unique6, CPU deterministic",
            "metric_surface": "3x2 view grid (768x512), identical arrangement to the runner",
            "validation": validation, "comparisons": comparisons}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-seed", type=int, default=20260930)
    parser.add_argument("--skip-part-b", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    result = {"protocol": "final_audit_20261001/STRICT276_TEXTURE_FIDELITY_AUDIT",
              "bootstrap": {"resamples": 10000, "seed": args.bootstrap_seed,
                            "method": "object-level percentile"}}
    result["partA"] = part_a(args.output_dir, args.bootstrap_seed)
    if not args.skip_part_b:
        result["partB"] = part_b(args.output_dir, args.bootstrap_seed, PART_B_SCHEDULES)
    (args.output_dir / "paired_bootstrap.json").write_text(json.dumps(result, indent=2) + "\n")
    for part in ("partA", "partB"):
        if part in result:
            print(f"{part}: comparisons={len(result[part]['comparisons'])}")
    print(f"done -> {args.output_dir / 'paired_bootstrap.json'}", flush=True)


if __name__ == "__main__":
    main()
