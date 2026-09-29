"""Trace the prediction tensor through float evaluation and PNG serialization.

The existing clean-v2 run did not preserve the pre-save prediction tensor.  This
utility therefore has two explicit modes:

* ``--audit-only``: audit the frozen CSV/PNG artifacts without inference.  It
  records the missing A/B tensor provenance and computes float16/float32 PNG
  proxies for diagnosis.
* ``--run``: on an assigned CUDA device, reproduce the frozen 12-object
  protocol and save A (float-eval tensor), B (PNG encoder input), and C (PNG
  reload) for all four conditions from the same generation.

The script never changes the dataset, checkpoint, C3, or any paper-facing
table.  It is deliberately separate from the frozen 300-object runner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision.utils import save_image


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_GEOTEX = Path("/tmp/mv_main_rerun/geotex")
if HISTORICAL_GEOTEX.is_dir():
    sys.path.insert(0, str(HISTORICAL_GEOTEX))

from data_utils import collate_batch, prepare_batch  # noqa: E402
from eval_exploration import generate, load_model  # noqa: E402
from metrics import compute_ssim  # noqa: E402
from omegaconf import OmegaConf  # noqa: E402


METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
FIXED12 = (13, 15, 38, 48, 54, 66, 68, 78, 82, 83, 110, 111)
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_png(path: Path) -> torch.Tensor:
    arr = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)


def tensor_stats(tensor: torch.Tensor) -> dict[str, object]:
    value = tensor.detach().float().cpu()
    return {
        "shape": list(value.shape),
        "dtype": str(tensor.dtype),
        "min": float(value.min()),
        "max": float(value.max()),
        "mean": float(value.mean()),
        "std": float(value.std(unbiased=False)),
    }


def tensor_stats_preserve_dtype(tensor: torch.Tensor) -> dict[str, object]:
    stats = tensor_stats(tensor)
    stats["dtype"] = str(tensor.dtype)
    return stats


def mse(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a.detach().float() - b.detach().float()).pow(2).mean())


def pixel_mae(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a.detach().float() - b.detach().float()).abs().mean())


def max_abs(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a.detach().float() - b.detach().float()).abs().max())


def psnr_from_mse(value: float) -> float:
    if value <= 0.0:
        return float("inf")
    return float(10.0 * math.log10(1.0 / value))


def full_ssim(pred: torch.Tensor, target: torch.Tensor) -> float:
    return float(compute_ssim(pred, target))


def base_paths(eval_dir: Path) -> tuple[dict, dict[tuple[int, str], dict]]:
    manifest = load_json(eval_dir / "evaluation_manifest.json")
    rows = {}
    for method in METHODS:
        with (eval_dir / f"per_object_{method}.csv").open(newline="") as handle:
            for row in csv.DictReader(handle):
                rows[(int(row["object_idx"]), method)] = row
    return manifest, rows


def audit_only(eval_dir: Path, object_list: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest, csv_rows = base_paths(eval_dir)
    uids = [line.strip() for line in object_list.read_text().splitlines() if line.strip()]
    if len(uids) != 300:
        raise ValueError(f"expected 300 UIDs in {object_list}, found {len(uids)}")

    rows: list[dict[str, object]] = []
    for object_idx in FIXED12:
        object_id = f"obj_{object_idx:04d}"
        gt_path = eval_dir / "predictions" / "ground_truth" / f"{object_id}.png"
        gt = load_png(gt_path)
        for method in METHODS:
            png_path = eval_dir / "predictions" / method / f"{object_id}.png"
            png = load_png(png_path)
            csv_row = csv_rows[(object_idx, method)]
            png_fp16_ssim = full_ssim(png.to(torch.float16), gt.float())
            png_fp32_ssim = full_ssim(png.float(), gt.float())
            row = {
                "object": object_id,
                "object_idx": object_idx,
                "source_uid": uids[object_idx],
                "method": method,
                "original_float_eval_full_ssim_scalar": float(csv_row["full_ssim"]),
                "png_reload_float16_prediction_full_ssim": png_fp16_ssim,
                "png_reload_float32_prediction_full_ssim": png_fp32_ssim,
                "png_fp16_proxy_minus_recorded_A": png_fp16_ssim - float(csv_row["full_ssim"]),
                "png_fp32_minus_recorded_A": png_fp32_ssim - float(csv_row["full_ssim"]),
                "png_path": str(png_path.resolve()),
                "png_sha256": sha256(png_path),
                "png_reload_shape": json.dumps(list(png.shape)),
                "png_reload_dtype": str(png.dtype),
                "png_reload_min": float(png.min()),
                "png_reload_max": float(png.max()),
                "png_reload_mean": float(png.mean()),
                "png_reload_std": float(png.std(unbiased=False)),
                "A_tensor_available": False,
                "B_pre_encoder_tensor_available": False,
                "C_png_reload_tensor_available": True,
                "pixel_comparison_status": "ORIGINAL_A_B_TENSORS_NOT_SAVED",
                "csv_png_object_mapping_verified": csv_row["object"] == object_id
                and int(csv_row["object_idx"]) == object_idx
                and manifest["object_ids"][object_idx] == object_id,
            }
            rows.append(row)

    fields = list(rows[0])
    with (output_dir / "FLOAT_PNG_PIXEL_COMPARISON.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    audit_manifest = {
        "mode": "audit_only",
        "status": "original_float_and_pre_encoder_tensors_unavailable",
        "eval_dir": str(eval_dir.resolve()),
        "object_list": str(object_list.resolve()),
        "object_list_sha256": sha256(object_list),
        "fixed12_indices": list(FIXED12),
        "methods": list(METHODS),
        "checkpoint": manifest["checkpoint"],
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "protocol": manifest,
        "csv_png_mapping_all_verified": all(row["csv_png_object_mapping_verified"] for row in rows),
        "interpretation": (
            "The saved artifacts prove filename/object alignment and expose the PNG reload branch. "
            "They cannot provide A/B pixel MAE because the original pre-save tensors were not retained."
        ),
    }
    (output_dir / "float_png_serialization_manifest.json").write_text(
        json.dumps(audit_manifest, indent=2) + "\n"
    )


def run_trace(config_path: Path, checkpoint: Path, object_list: Path, output_dir: Path, device_name: str,
              steps: int, seed: int) -> None:
    if not torch.cuda.is_available() or not device_name.startswith("cuda"):
        raise RuntimeError("controlled tensor trace requires an assigned CUDA device; use --audit-only on this host")

    output_dir.mkdir(parents=True, exist_ok=True)
    tensor_dir = output_dir / "tensors"
    tensor_dir.mkdir(exist_ok=True)
    manifest = {
        "mode": "controlled_rerun",
        "status": "running",
        "config": str(config_path.resolve()),
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": sha256(checkpoint),
        "object_list": str(object_list.resolve()),
        "object_list_sha256": sha256(object_list),
        "fixed12_indices": list(FIXED12),
        "methods": list(METHODS),
        "steps": steps,
        "seed": seed,
        "device": device_name,
        "shared_initial_latent": True,
        "same_generation_for_A_B_C": True,
        "png_encoder": "torchvision.utils.save_image: round clamp to uint8 then PIL PNG",
    }
    (output_dir / "float_png_serialization_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    from metrics import compute_edge_mask  # local historical import, kept for protocol parity

    config = OmegaConf.load(str(config_path))
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(object_list.resolve())
    from src.utils.train_util import instantiate_from_config

    device = torch.device(device_name)
    dtype = torch.float16
    model = load_model(str(config_path), str(checkpoint), device)
    dataset = instantiate_from_config(validation)
    if getattr(dataset, "target_view_mode", None) != "unique6":
        raise RuntimeError("dataset did not instantiate with unique6")
    if len(dataset) != 300:
        raise RuntimeError(f"expected 300-object dataset, got {len(dataset)}")

    rows: list[dict[str, object]] = []
    for object_idx in FIXED12:
        object_id = f"obj_{object_idx:04d}"
        batch = collate_batch(dataset, object_idx, device)
        _, target, normal, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(seed)
        shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)

        gt_cpu = target.detach().cpu()
        torch.save(gt_cpu, tensor_dir / f"{object_id}_gt_float_eval.pt")
        save_image(target, output_dir / f"{object_id}_gt.png")
        gt_reload = load_png(output_dir / f"{object_id}_gt.png")
        torch.save(gt_reload, tensor_dir / f"{object_id}_gt_png_reload.pt")

        for method in METHODS:
            schedule = SCHEDULES[method]
            torch.manual_seed(seed)
            prediction = generate(
                model,
                batch,
                device,
                dtype,
                None if method == "no_adapter" else geo_feats,
                schedule["scale"],
                steps,
                shared_latents,
                timestep_schedule=schedule["timestep_schedule"],
            )
            A = prediction.detach().cpu()
            B = prediction.detach().clone()
            png_path = output_dir / f"{object_id}_{method}.png"
            save_image(B, png_path)
            C = load_png(png_path)
            torch.save(A, tensor_dir / f"{object_id}_{method}_A_float_eval.pt")
            torch.save(B.cpu(), tensor_dir / f"{object_id}_{method}_B_pre_encoder.pt")
            torch.save(C, tensor_dir / f"{object_id}_{method}_C_png_reload.pt")
            row = {
                "object": object_id,
                "object_idx": object_idx,
                "method": method,
                "A_full_ssim": full_ssim(A, gt_cpu),
                "B_full_ssim": full_ssim(B, target),
                "C_full_ssim": full_ssim(C, gt_reload),
                "A_B_pixel_mae": pixel_mae(A, B.cpu()),
                "A_B_max_abs": max_abs(A, B.cpu()),
                "A_B_psnr": psnr_from_mse(mse(A, B.cpu())),
                "B_C_pixel_mae": pixel_mae(B.cpu(), C),
                "B_C_max_abs": max_abs(B.cpu(), C),
                "B_C_psnr": psnr_from_mse(mse(B.cpu(), C)),
                "A_C_pixel_mae": pixel_mae(A, C),
                "A_C_max_abs": max_abs(A, C),
                "A_C_psnr": psnr_from_mse(mse(A, C)),
                "png_sha256": sha256(png_path),
                "A_stats": json.dumps(tensor_stats_preserve_dtype(A), sort_keys=True),
                "B_stats": json.dumps(tensor_stats_preserve_dtype(B), sort_keys=True),
                "C_stats": json.dumps(tensor_stats_preserve_dtype(C), sort_keys=True),
                "same_generation_for_A_B_C": True,
            }
            rows.append(row)
            del prediction, A, B, C
            torch.cuda.empty_cache()

        del batch, target, normal, real_depth, geo_input, mask, geo_feats, shared_latents
        torch.cuda.empty_cache()

    with (output_dir / "FLOAT_PNG_PIXEL_COMPARISON.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest["status"] = "completed"
    (output_dir / "float_png_serialization_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("audit-only", "run"), required=True)
    parser.add_argument("--eval-dir", type=Path, default=ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6")
    parser.add_argument("--object-list", type=Path, default=ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "final/round2/main_adapter_clean_v2/float_png_trace_12")
    parser.add_argument("--config", type=Path, default=Path("/tmp/mv_main_rerun/MVPainter/configs/mvpainter-geotex-full-train.yaml"))
    parser.add_argument("--checkpoint", type=Path, default=ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt")
    parser.add_argument("--device", default="cuda:1")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.mode == "audit-only":
        audit_only(args.eval_dir, args.object_list, args.output_dir)
    else:
        run_trace(args.config, args.checkpoint, args.object_list, args.output_dir, args.device, args.steps, args.seed)


if __name__ == "__main__":
    main()
