#!/usr/bin/env python3
"""Test replacing the cached global embedding with the official raw source-view embedding."""

from __future__ import annotations

import csv
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from diffusers import EulerDiscreteScheduler
from PIL import Image
from torchvision.utils import save_image

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
LOCK = HERE / "protocol/B2_RAW_SOURCE_EMBEDDING_LOCK.json"
AMENDMENT = HERE / "protocol/B2_PROTOCOL_AMENDMENT_02.json"
PHASE_B_LOCK = HERE / "protocol/B_PROTOCOL_LOCK.json"
OUT = HERE / "runs/phase_b2_raw_source_embedding"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from geotex.data_utils import prepare_batch
from run_color_intervention import (
    encode_global_embedding,
    install_vae_trace,
    load_data,
    prompt_condition_trace,
    seed_all,
    sha_file,
    tensor_sha,
    tensor_grid_tiles,
    tile_mask_grid,
    utc_now,
)
from run_chroma_anchor_evaluation import _get_lpips, lpips_values, tile_metrics
from src.utils.train_util import instantiate_from_config
from omegaconf import OmegaConf


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty result table: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def grid_tiles(image: np.ndarray) -> list[np.ndarray]:
    h, w = image.shape[:2]
    if h % 3 or w % 2:
        raise ValueError(f"expected a 3x2 unique6 grid, got {image.shape}")
    th, tw = h // 3, w // 2
    return [image[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
            for r in range(3) for c in range(2)]


def grid_targets(tensor: torch.Tensor) -> list[np.ndarray]:
    array = tensor.detach().float().clamp(0, 1)[0].cpu().permute(1, 2, 0).numpy()
    h, w = array.shape[:2]
    th, tw = h // 3, w // 2
    return [np.floor(np.clip(array[r * th:(r + 1) * th, c * tw:(c + 1) * tw], 0, 1) * 255 + 0.5)
            .astype(np.uint8) for r in range(3) for c in range(2)]


def object_specs(lock: dict) -> list[dict]:
    phase_b = json.loads(PHASE_B_LOCK.read_text())
    by_uid = {item["uid"]: item for item in phase_b["objects"]}
    return [by_uid[uid] for uid in lock["development_objects"]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    out_dir = args.output_dir.resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite an existing intervention: {out_dir}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing to substitute CPU generation")
    lock = json.loads(LOCK.read_text())
    amendment = json.loads(AMENDMENT.read_text())
    if amendment["base_lock_sha256"] != sha_file(LOCK):
        raise RuntimeError("B2 amendment does not pin the frozen protocol")
    if amendment["runner_sha256"] != sha_file(Path(__file__).resolve()):
        raise RuntimeError("runner SHA-256 differs from the pre-generation B2 amendment")
    if sha_file(CHECKPOINT) != lock["model"]["checkpoint_sha256"]:
        raise RuntimeError("checkpoint SHA-256 differs from the frozen B2 lock")
    if sha_file(CONFIG) != lock["model"]["config_sha256"]:
        raise RuntimeError("config SHA-256 differs from the frozen B2 lock")
    expected_gpu = str(lock["gpu"]["cuda_visible_devices"])
    if os.environ.get("CUDA_VISIBLE_DEVICES") != expected_gpu:
        raise RuntimeError("CUDA_VISIBLE_DEVICES differs from the frozen GPU binding")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "predictions").mkdir()
    run_state = {
        "status": "running", "pid": os.getpid(), "generation_count": 0,
        "started_utc": utc_now(), "last_uid": None, "last_condition": None,
    }
    rows: list[dict] = []
    runtime = {
        "status": "running",
        "started_utc": run_state["started_utc"],
        "pid": os.getpid(),
        "python": sys.version,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "diffusers": __import__("diffusers").__version__,
        "transformers": __import__("transformers").__version__,
        "numpy": np.__version__,
        "device": torch.cuda.get_device_name(0),
        "visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "physical_gpu_index": lock["gpu"]["physical_gpu_index"],
        "device_uuid": str(torch.cuda.get_device_properties(0).uuid),
        "unet_dtype": None,
        "vae_dtype": None,
        "checkpoint_sha256": sha_file(CHECKPOINT),
        "config_sha256": sha_file(CONFIG),
        "protocol_sha256": sha_file(LOCK),
        "protocol_amendment_sha256": sha_file(AMENDMENT),
        "phase_b_protocol_sha256": sha_file(PHASE_B_LOCK),
        "runner_sha256": sha_file(Path(__file__).resolve()),
        "generation_helper_sha256": sha_file(ROOT / "geotex/explore_contradiction.py"),
        "metric_runner_sha256": sha_file(HERE / "run_chroma_anchor_evaluation.py"),
        "sampling_scheduler_class": None,
        "sampling_scheduler_config": None,
        "xformers_available": importlib.util.find_spec("xformers") is not None,
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
        "cudnn_tf32": torch.backends.cudnn.allow_tf32,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "flash_sdp": torch.backends.cuda.flash_sdp_enabled(),
        "mem_efficient_sdp": torch.backends.cuda.mem_efficient_sdp_enabled(),
        "math_sdp": torch.backends.cuda.math_sdp_enabled(),
        "generation_calls_expected": 8,
    }
    (out_dir / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
    (out_dir / "run_state.json").write_text(json.dumps(run_state, indent=2) + "\n")

    start_all = time.monotonic()
    try:
        device = torch.device("cuda:0")
        model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
        model.unet.eval()
        model.pipeline.vae.eval()
        scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
        vae_trace = install_vae_trace(model, device)
        runtime.update({
            "unet_dtype": str(next(model.unet.parameters()).dtype),
            "vae_dtype": str(next(model.pipeline.vae.parameters()).dtype),
            "vision_encoder_dtype": str(next(model.pipeline.vision_encoder.parameters()).dtype),
            "vision_encoder_2_dtype": str(next(model.pipeline.vision_encoder_2.parameters()).dtype),
            "pipeline_scheduler_class": type(model.pipeline.scheduler).__name__,
            "pipeline_scheduler_config": dict(model.pipeline.scheduler.config),
            "sampling_scheduler_class": type(scheduler).__name__,
            "sampling_scheduler_config": dict(scheduler.config),
            "vae_processor_class": type(model.pipeline.feature_extractor_vae).__name__,
            "vae_processor_config": model.pipeline.feature_extractor_vae.to_dict(),
            "vision_processor_class": type(model.pipeline.vision_processor).__name__,
            "vision_processor_config": model.pipeline.vision_processor.to_dict(),
        })
        (out_dir / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")

        grouped: dict[str, list[dict]] = {}
        for spec in object_specs(lock):
            tag = "legacy_fig4" if "rendered_full" in spec["root"] else "freshc_dev"
            grouped.setdefault(tag, []).append(spec)
        lpips_model = _get_lpips()

        for tag, specs in grouped.items():
            data_root = Path(specs[0]["root"])
            dataset = load_data(data_root, [spec["uid"] for spec in specs])
            for local_idx, spec in enumerate(specs):
                uid = spec["uid"]
                seed_all(int(spec["object_seed"]))
                item = dataset[local_idx]
                alpha = getattr(dataset, "_v2_condition_alpha", None)
                condition_path = Path(getattr(dataset, "_v2_condition_path", ""))
                if alpha is None or not condition_path.is_file():
                    raise RuntimeError(f"condition provenance missing for {uid}")
                batch = {key: value.unsqueeze(0).to(device) if torch.is_tensor(value) else value
                         for key, value in item.items()}
                source_path = data_root / uid / "image" / f"{int(spec['source_view']):03d}.png"
                raw_source, _ = dataset.load_im(str(source_path), [1.0, 1.0, 1.0])
                raw_source_embedding = encode_global_embedding(model, raw_source.unsqueeze(0))
                cached_feature = item["global_embeds"].detach()
                if cached_feature.numel() != raw_source_embedding.numel():
                    raise RuntimeError(
                        f"cached/raw embedding feature count mismatch for {uid}: "
                        f"{cached_feature.shape} vs {raw_source_embedding.shape}"
                    )
                # The pipeline consumes each flattened feature as [B, 1, D];
                # cache storage may retain extra singleton batch/token axes.
                cached_embedding = cached_feature.reshape(1, 1, -1).to(device)
                raw_embedding = raw_source_embedding.reshape(1, 1, -1).to(
                    device=device, dtype=cached_embedding.dtype
                )

                _, target_grid, _, _, geo_input, mask_grid = prepare_batch(batch, model.img_size, device)
                targets = grid_targets(target_grid)
                masks = tile_mask_grid(mask_grid)
                with torch.inference_mode():
                    geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0,
                                                 posinf=1.0, neginf=0.0)
                    geo_features = model.geo_encoder(geo_clean)
                if isinstance(geo_features, dict):
                    geometry_hashes = {key: tensor_sha(value)
                                       for key, value in sorted(geo_features.items())}
                elif isinstance(geo_features, (list, tuple)):
                    geometry_hashes = [tensor_sha(value) for value in geo_features]
                else:
                    geometry_hashes = [tensor_sha(geo_features)]
                seed_all(int(lock["model"]["initial_latent_seed"]))
                init_latents = torch.randn(
                    1, 4, model.img_size * 3 // 8, model.img_size * 2 // 8,
                    device=device, dtype=torch.float16,
                )
                init_latent_hash = tensor_sha(init_latents)
                cond = item["cond_imgs"].unsqueeze(0).to(device)
                condition_hash = tensor_sha(cond)
                gt_ids = [int(x) for x in spec["target_order"]]
                cached_tiles: list[np.ndarray] | None = None
                pair_tiles: dict[str, list[np.ndarray]] = {}

                for condition_name, embedding in (
                    ("cached_baseline", cached_embedding),
                    ("selected_raw_source_embedding", raw_embedding),
                ):
                    vae_trace.clear()
                    seed_all(int(lock["model"]["initial_latent_seed"]))
                    prompt_trace = prompt_condition_trace(
                        model, embedding, cached_embedding, device, torch.float16
                    )
                    started = time.monotonic()
                    prediction = exp.generate_with_schedule(
                        model,
                        {**batch, "cond_imgs": cond, "global_embeds": embedding},
                        device,
                        torch.float16,
                        geo_features,
                        lambda _progress: 1.25,
                        50,
                        init_latents.clone(),
                        {},
                    )
                    torch.cuda.synchronize(device)
                    elapsed = time.monotonic() - started
                    output_path = out_dir / "predictions" / uid / f"{condition_name}.png"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    save_image(prediction, output_path)
                    with Image.open(output_path) as image:
                        grid = np.asarray(image.convert("RGB"))
                    tiles = grid_tiles(grid)
                    pair_tiles[condition_name] = tiles
                    if condition_name == "cached_baseline":
                        cached_tiles = tiles
                    if cached_tiles is None:
                        raise RuntimeError("cached baseline must be generated first")

                    for view_idx, (pred_tile, base_tile, gt_tile, mask_tile) in enumerate(
                        zip(tiles, cached_tiles, targets, masks)
                    ):
                        rows.append({
                            "uid": uid,
                            "cohort": spec["cohort"],
                            "object_idx": spec["object_idx"],
                            "object_seed": spec["object_seed"],
                            "condition": condition_name,
                            "view_idx": view_idx,
                            "target_view_id": gt_ids[view_idx],
                            "is_source_view": view_idx == 0,
                            "checkpoint_sha256": runtime["checkpoint_sha256"],
                            "config_sha256": runtime["config_sha256"],
                            "protocol_sha256": runtime["protocol_sha256"],
                            "runner_sha256": runtime["runner_sha256"],
                            "source_png": str(source_path.resolve()),
                            "source_png_sha256": sha_file(source_path),
                            "source_condition_png": str(condition_path.resolve()),
                            "source_condition_png_sha256": sha_file(condition_path),
                            "condition_tensor_sha256": condition_hash,
                            "source_alpha_sha256": tensor_sha(alpha),
                            "cached_embedding_sha256": tensor_sha(item["global_embeds"]),
                            "cached_embedding_storage_shape": json.dumps(list(item["global_embeds"].shape)),
                            "selected_raw_embedding_sha256": tensor_sha(raw_source_embedding),
                            "selected_raw_embedding_shape": json.dumps(list(raw_source_embedding.shape)),
                            "embedding_used_sha256": tensor_sha(embedding),
                            "geometry_feature_sha256": json.dumps(geometry_hashes, sort_keys=True),
                            "initial_latent_sha256": init_latent_hash,
                            "vae_processor_pixels_sha256": vae_trace.get("vae_processor_pixels_sha256"),
                            "posterior_mean_sha256": vae_trace.get("posterior_mean_sha256"),
                            "posterior_std_sha256": vae_trace.get("posterior_std_sha256"),
                            "posterior_sample_sha256": vae_trace.get("posterior_sample_sha256"),
                            "posterior_noise_sha256": vae_trace.get("posterior_noise_sha256"),
                            "posterior_rng_before_sha256": vae_trace.get("cuda_rng_before_posterior_sha256"),
                            "posterior_rng_after_sha256": vae_trace.get("cuda_rng_after_posterior_sha256"),
                            "prompt_embeds_sha256": prompt_trace["prompt_embeds_sha256"],
                            "prediction_png": str(output_path.resolve()),
                            "prediction_png_sha256": sha_file(output_path),
                            "generation_elapsed_seconds": elapsed,
                            "foreground_pixels": int(np.sum(np.asarray(mask_tile) >= 0.5)),
                        })
                    run_state["generation_count"] += 1
                    run_state["last_uid"] = uid
                    run_state["last_condition"] = condition_name
                    run_state["updated_utc"] = utc_now()
                    (out_dir / "run_state.json").write_text(json.dumps(run_state, indent=2) + "\n")
                    write_rows(out_dir / "B2_RAW_SOURCE_EMBEDDING_RESULTS.csv", rows)
                    del prediction
                    torch.cuda.empty_cache()

                tile_lpips = lpips_values(
                    lpips_model,
                    pair_tiles["cached_baseline"] + pair_tiles["selected_raw_source_embedding"],
                    targets + targets,
                    masks + masks,
                )
                for view_idx in range(6):
                    base_metrics = tile_metrics(
                        pair_tiles["cached_baseline"][view_idx], targets[view_idx],
                        pair_tiles["cached_baseline"][view_idx], masks[view_idx],
                        tile_lpips[view_idx],
                    )
                    raw_metrics = tile_metrics(
                        pair_tiles["selected_raw_source_embedding"][view_idx], targets[view_idx],
                        pair_tiles["cached_baseline"][view_idx], masks[view_idx],
                        tile_lpips[view_idx + 6],
                    )
                    rows[-12 + view_idx]["paired_metrics"] = json.dumps({
                        "cached": base_metrics,
                        "selected_raw_source_embedding": raw_metrics,
                        "delta": {
                            "fg_ciede2000": raw_metrics["candidate_fg_ciede2000"]
                                            - base_metrics["candidate_fg_ciede2000"],
                            "fg_psnr": raw_metrics["candidate_fg_psnr"]
                                       - base_metrics["candidate_fg_psnr"],
                            "fg_lpips": raw_metrics["candidate_fg_lpips"]
                                        - base_metrics["candidate_fg_lpips"],
                            "lstar_ssim_to_gt": raw_metrics["candidate_foreground_lstar_ssim_to_gt"]
                                                - base_metrics["gfl_foreground_lstar_ssim_to_gt"],
                            "gt_laplacian_error": raw_metrics["delta_gt_laplacian_error"],
                            "lstar_ssim_vs_cached": raw_metrics["candidate_lstar_ssim_vs_gfl"],
                        },
                    }, sort_keys=True)
                    rows[-6 + view_idx]["paired_metrics"] = rows[-12 + view_idx]["paired_metrics"]
                write_rows(out_dir / "B2_RAW_SOURCE_EMBEDDING_RESULTS.csv", rows)

        if run_state["generation_count"] != 8:
            raise RuntimeError(f"expected eight generation calls, got {run_state['generation_count']}")
        runtime.update({
            "status": "complete",
            "finished_utc": utc_now(),
            "generation_calls_completed": run_state["generation_count"],
            "generation_wall_seconds": time.monotonic() - start_all,
        })
        run_state.update({"status": "complete", "finished_utc": runtime["finished_utc"]})
        (out_dir / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
        (out_dir / "run_state.json").write_text(json.dumps(run_state, indent=2) + "\n")
        print(json.dumps({"status": "complete", "calls": run_state["generation_count"],
                          "wall_seconds": runtime["generation_wall_seconds"]}, indent=2))
    except Exception as exc:
        runtime.update({"status": "failed", "failed_utc": utc_now(), "error": repr(exc)})
        run_state.update({"status": "failed", "failed_utc": runtime["failed_utc"], "error": repr(exc)})
        (out_dir / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
        (out_dir / "run_state.json").write_text(json.dumps(run_state, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
