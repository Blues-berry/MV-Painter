#!/usr/bin/env python3
"""Build object-level color/quality pairs from byte-identified R1 RGB assets."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import PIL
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT.parent
CHECKPOINT_SHA = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
RUNNER_SHA = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"
VIEWS = [0, 15, 12, 16, 13, 14]
METHODS = ("no_adapter", "native_gfl", "layer_llh")
LABELS = {"no_adapter": "No Adapter", "native_gfl": "GFL", "layer_llh": "LLH"}
sys.path.insert(0, str(ROOT.parents[3]))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_grid(path: Path, mode="RGB") -> np.ndarray:
    image = Image.open(path).convert(mode)
    array = np.asarray(image)
    if array.shape[:2] != (768, 512):
        raise ValueError(f"expected a 3x2 grid of 256px views, got {array.shape} in {path}")
    return array


def image_tensor(array: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(np.asarray(array).copy()).permute(2, 0, 1).unsqueeze(0).float() / 255.0


def ciede_metrics(reference: np.ndarray, prediction: np.ndarray, mask: np.ndarray) -> dict:
    de_by_view, da_by_view, db_by_view = [], [], []
    for view in range(6):
        row, col = divmod(view, 2)
        ys, xs = slice(row * 256, (row + 1) * 256), slice(col * 256, (col + 1) * 256)
        fg = mask[ys, xs] > 127
        ref = reference[ys, xs].astype(np.float32) / 255.0
        pred = prediction[ys, xs].astype(np.float32) / 255.0
        lab_ref, lab_pred = rgb2lab(ref), rgb2lab(pred)
        delta = lab_pred - lab_ref
        de_by_view.append(float(deltaE_ciede2000(lab_ref, lab_pred)[fg].mean()))
        da_by_view.append(float(delta[..., 1][fg].mean()))
        db_by_view.append(float(delta[..., 2][fg].mean()))
    return {"mean_fg_ciede2000": float(np.mean(de_by_view)),
            "mean_delta_a_star": float(np.mean(da_by_view)),
            "mean_delta_b_star": float(np.mean(db_by_view))}


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    torch.set_num_threads(4)
    freeze = json.loads((ARTIFACT / "SAMPLE_FREEZE.json").read_text())
    failure_rows = list(csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open()))
    failure_map = {(r["sample_id"], r["method"]): r for r in failure_rows}
    metric_rows = list(csv.DictReader((ARTIFACT / "logs/RGB_RELOADED_METRICS.csv").open()))
    metric_map = {(r["sample_id"], r["method_key"]): r for r in metric_rows}
    samples = {s["sample_id"]: s for s in freeze["samples"]}
    rows = []
    for sample_id, sample in samples.items():
        if any((sample_id, LABELS[m]) not in failure_map for m in METHODS):
            raise RuntimeError(f"incomplete paired method rows for {sample_id}")
        directory = ARTIFACT / "raw_rgb" / sample_id
        reference_path = directory / "reference.png"
        mask_path = ARTIFACT / "masks" / f"{sample_id}.png"
        reference = read_grid(reference_path)
        mask = read_grid(mask_path, "L")
        for method in METHODS:
            image_path = directory / f"{method}.png"
            prediction = read_grid(image_path)
            fail = failure_map[(sample_id, LABELS[method])]
            metrics = metric_map[(sample_id, method)]
            if fail["uid"] != sample["uid"]:
                raise RuntimeError(f"UID mismatch in {sample_id}/{method}")
            if metrics["uid"] != sample["uid"]:
                raise RuntimeError(f"metric UID mismatch in {sample_id}/{method}")
            expected_hashes = {
                "prediction_sha256": sha(image_path),
                "reference_sha256": sha(reference_path),
                "mask_sha256": sha(mask_path),
            }
            for key, expected in expected_hashes.items():
                if metrics.get(key) != expected:
                    raise RuntimeError(f"{key} mismatch in reloaded RGB metrics for {sample_id}/{method}")
            rows.append({
                "sample_id": sample_id,
                "uid": sample["uid"],
                "source": sample["source"],
                "object_idx": sample.get("object_idx", ""),
                "object_seed": sample.get("object_seed", ""),
                "condition": LABELS[method],
                "checkpoint_sha256": CHECKPOINT_SHA,
                "runner_sha256": RUNNER_SHA,
                "view_mode": "unique6",
                "target_view_ids": json.dumps(sample.get("effective_view_order", VIEWS)),
                "reference_png": str(reference_path),
                "reference_sha256": sha(reference_path),
                "mask_png": str(mask_path),
                "mask_sha256": sha(mask_path),
                "prediction_png": str(image_path),
                "prediction_sha256": sha(image_path),
                **ciede_metrics(reference, prediction, mask),
                "fg_psnr": float(metrics["fg_psnr"]),
                "fg_lpips": float(metrics["fg_lpips"]),
                "edge_ssim": float(metrics["edge_ssim"]),
                "visual_purple_cast": fail["visual_purple_cast"],
                "visual_fine_detail_loss": fail["visual_fine_detail_loss"],
                "visual_structure_damage": fail["visual_structure_damage"],
                "input_condition": "matched per-object seed, geometry/RGB inputs, unique6 target set; paired rows share the same object UID",
            })

    # Texture metrics are recomputed from the same RGB bytes using frozen masks.
    from geotex.metrics_extended import compute_all_extended  # noqa: E402
    for row in rows:
        pred = image_tensor(read_grid(Path(row["prediction_png"])))
        target = image_tensor(read_grid(Path(row["reference_png"])))
        mask_array = read_grid(Path(row["mask_png"]), "L")
        mask_tensor = torch.from_numpy((mask_array > 127).astype(np.float32))[None, None]
        values = compute_all_extended(pred, target, mask_tensor)
        row.update({f"texture_{key}": float(value) for key, value in values.items()})

    out = ROOT / "COLOR_FIDELITY_PAIRED_RESULTS.csv"
    write_csv(out, rows)

    by_sample = defaultdict(dict)
    for row in rows:
        by_sample[row["sample_id"]][row["condition"]] = row
    contrasts = (("GFL", "No Adapter"), ("LLH", "GFL"))
    endpoints = (
        ("mean_fg_ciede2000", "lower"), ("mean_delta_a_star", "signed"),
        ("mean_delta_b_star", "signed"), ("fg_psnr", "higher"),
        ("fg_lpips", "lower"), ("edge_ssim", "higher"),
        ("texture_fg_lap_var", "higher"), ("texture_fg_rgb_std", "higher"),
        ("texture_fg_grad_mag", "higher"), ("texture_fg_hf_energy", "higher"),
        ("texture_fg_color_entropy", "higher"),
    )
    rng = np.random.default_rng(61008)
    summary = []
    for left, right in contrasts:
        for metric, direction in endpoints:
            diffs = np.array([float(by_sample[s][left][metric]) - float(by_sample[s][right][metric])
                              for s in sorted(by_sample)])
            bootstrap = diffs[rng.integers(0, len(diffs), size=(20000, len(diffs)))].mean(axis=1)
            ci_low, ci_high = np.quantile(bootstrap, [0.025, 0.975])
            sd = float(diffs.std(ddof=1))
            if direction == "higher":
                wins = int((diffs > 0).sum())
            elif direction == "lower":
                wins = int((diffs < 0).sum())
            else:
                wins = ""
            summary.append({
                "contrast": f"{left} - {right}", "n_objects": len(diffs), "metric": metric,
                "direction_for_win": direction, "mean_paired_difference": float(diffs.mean()),
                "median_paired_difference": float(np.median(diffs)),
                "paired_bootstrap_95ci_low": float(ci_low),
                "paired_bootstrap_95ci_high": float(ci_high),
                "cohens_dz": float(diffs.mean() / sd) if sd > 0 else "",
                "wins": wins,
            })
    write_csv(ROOT / "P1_PAIRED_SUMMARY.csv", summary)

    reloaded_identity = {
        "n_metric_rows": len(metric_rows),
        "metrics_csv_sha256": sha(ARTIFACT / "logs/RGB_RELOADED_METRICS.csv"),
        "recompute_script_sha256": metric_rows[0]["metric_script_sha256"],
        "sample_freeze_json_sha256": metric_rows[0]["sample_freeze_json_sha256"],
        "config_sha256": metric_rows[0]["config_sha256"],
        "runner_sha256": metric_rows[0]["runner_sha256"],
        "runtime": {
            "python": metric_rows[0]["metric_runtime_python"],
            "torch": metric_rows[0]["metric_runtime_torch"],
            "torchvision": metric_rows[0]["metric_runtime_torchvision"],
            "device": metric_rows[0]["metric_runtime_device"],
            "platform": metric_rows[0]["metric_runtime_platform"],
            "lpips_weights_sha256": metric_rows[0]["lpips_weights_sha256"],
        },
        "identity_checks": {
            "p1_prediction_reference_mask_sha256_match": True,
            "dataset_masks_pixel_match_frozen_mask_png": True,
            "per_row_png_paths_and_sha256": "recorded in RGB_RELOADED_METRICS.csv",
        },
    }
    reloaded_identity_path = ARTIFACT / "logs/RGB_RELOADED_METRICS_IDENTITY.json"
    reloaded_identity_path.write_text(json.dumps(reloaded_identity, indent=2) + "\n")

    identity = {
        "n_objects": len(by_sample),
        "n_condition_rows": len(rows),
        "paired_conditions": ["No Adapter", "GFL", "LLH"],
        "checkpoint_sha256": CHECKPOINT_SHA,
        "runner_sha256": RUNNER_SHA,
        "view_mode": "unique6",
        "target_view_set": sorted(VIEWS),
        "target_view_order": "sample-specific frozen order recorded per row; the six target IDs are unique",
        "paired_bootstrap_seed": 61008,
        "paired_bootstrap_resamples": 20000,
        "metrics": "CIEDE2000/delta-a*/delta-b* recomputed from identified RGB PNGs; FG-PSNR/LPIPS/Edge-SSIM from RGB_RELOADED_METRICS.csv; texture measures recomputed from identified PNGs and frozen foreground masks",
        "metric_sources": {
            "ciede_and_delta_lab": "skimage.color applied to each identified PNG; six foreground views equally weighted",
            "fg_psnr_lpips_edge_ssim": "1008/engineering/color_failure/logs/RGB_RELOADED_METRICS.csv",
            "fg_psnr_lpips_edge_ssim_identity": "1008/engineering/color_failure/logs/RGB_RELOADED_METRICS_IDENTITY.json",
            "texture_metrics": "geotex.metrics_extended.compute_all_extended on the identified RGB PNGs and frozen masks",
            "visual_labels": "1008/engineering/color_failure/OBJECT_FAILURE_TABLE.csv; frozen visual review",
        },
        "source_sha256": {
            "sample_freeze_json": sha(ARTIFACT / "SAMPLE_FREEZE.json"),
            "object_failure_table": sha(ARTIFACT / "OBJECT_FAILURE_TABLE.csv"),
            "rgb_reloaded_metrics": sha(ARTIFACT / "logs/RGB_RELOADED_METRICS.csv"),
            "rgb_reloaded_metrics_identity": sha(reloaded_identity_path),
            "metrics_extended_py": sha(ROOT.parents[3] / "geotex/metrics_extended.py"),
            "analysis_script": sha(Path(__file__).resolve()),
        },
        "postprocess_environment": {
            "python": sys.version,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "scikit_image": __import__("skimage").__version__,
            "pillow": PIL.__version__,
            "platform": platform.platform(),
        },
        "reloaded_rgb_metrics_environment": {
            "python": metric_rows[0]["metric_runtime_python"],
            "torch": metric_rows[0]["metric_runtime_torch"],
            "torchvision": metric_rows[0]["metric_runtime_torchvision"],
            "device": metric_rows[0]["metric_runtime_device"],
            "lpips_weights_sha256": metric_rows[0]["lpips_weights_sha256"],
            "recompute_script_sha256": metric_rows[0]["metric_script_sha256"],
        },
    }
    (ROOT / "P1_PAIRED_RESULTS_IDENTITY.json").write_text(json.dumps(identity, indent=2) + "\n")
    print(f"wrote {len(rows)} object-condition rows and {len(summary)} paired summaries")


if __name__ == "__main__":
    main()
