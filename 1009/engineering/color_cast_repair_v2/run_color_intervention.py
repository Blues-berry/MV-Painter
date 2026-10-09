#!/usr/bin/env python3
"""Run the locked six-view, same-noise Lab color intervention on development objects."""

from __future__ import annotations

import csv
import argparse
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from diffusers import EulerDiscreteScheduler
from omegaconf import OmegaConf
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab
from skimage.metrics import structural_similarity
from torchvision.transforms import v2
from torchvision.utils import save_image

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
LOCK = HERE / "protocol/B_PROTOCOL_LOCK.json"
AMENDMENT = HERE / "protocol/B_PROTOCOL_AMENDMENT_01.json"
GPU_AMENDMENT = HERE / "protocol/B_PROTOCOL_AMENDMENT_02.json"
INPUT_AUDIT = HERE / "runs/phase_a/FRESHB_INPUT_EMBEDDING_AUDIT.json"
INPUT_PROVENANCE = HERE / "runs/phase_a/FRESHB_INPUT_EMBEDDING_PROVENANCE.json"
OUT = HERE / "runs/phase_b"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from color_repair import perturb_foreground_lab
from embedding_refresh import replace_cached_embedding
from geotex.data_utils import prepare_batch
from src.utils.train_util import instantiate_from_config


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def tensor_sha(tensor: torch.Tensor) -> str:
    array = tensor.detach().cpu().contiguous().numpy()
    return sha_bytes(array.tobytes())


def array_sha(array: np.ndarray) -> str:
    return sha_bytes(np.ascontiguousarray(array).tobytes())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_data(root: Path, uids: list[str]):
    list_dir = OUT / "object_lists"
    list_dir.mkdir(parents=True, exist_ok=True)
    tag = "legacy_fig4" if "rendered_full" in str(root) else "freshc_dev"
    list_path = list_dir / f"{tag}.txt"
    list_path.write_text("\n".join(uids) + "\n")
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.root_dir_list = [str(root)]
    validation.params.object_list_file = str(list_path.resolve())
    dataset = instantiate_from_config(validation)

    original = dataset.load_im_cond

    def capture_condition_alpha(path, color, random_ratio=0.8):
        cond, alpha = original(path, color, random_ratio)
        dataset._v2_condition_alpha = alpha
        dataset._v2_condition_path = str(path)
        return cond, alpha

    dataset.load_im_cond = capture_condition_alpha
    return dataset


def encode_global_embedding(model, condition: torch.Tensor) -> torch.Tensor:
    """Recompute exactly the two-encoder global appearance feature from a 512 RGB tensor."""
    images = [v2.functional.to_pil_image(condition[i].detach().cpu())
              for i in range(condition.shape[0])]
    pixels = model.pipeline.vision_processor(images=images, return_tensors="pt").pixel_values
    pixels = pixels.to(device="cpu", dtype=next(model.pipeline.vision_encoder.parameters()).dtype)
    with torch.inference_mode():
        first = model.pipeline.vision_encoder(pixels, output_hidden_states=False).image_embeds.unsqueeze(-2)
        second = model.pipeline.vision_encoder_2(pixels, output_hidden_states=False).image_embeds.unsqueeze(-2)
        return torch.cat([first, second], dim=-1).detach().float()


def prompt_condition_trace(
    model,
    embedding: torch.Tensor,
    cached_embedding: torch.Tensor,
    device: torch.device,
    weight_dtype: torch.dtype,
) -> dict:
    """Mirror the frozen runner's global-embedding injection for provenance only."""
    global_embeds = embedding.to(device=device, dtype=weight_dtype).view(1, 1, -1)
    cached = cached_embedding.to(device=device, dtype=weight_dtype).view(1, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
    contribution = global_embeds * ramp
    cached_contribution = cached * ramp
    prompt_embeds = uc_text_emb + contribution
    delta = contribution.float() - cached_contribution.float()
    return {
        "uc_text_embedding_sha256": tensor_sha(uc_text_emb),
        "global_prompt_contribution_sha256": tensor_sha(contribution),
        "global_prompt_contribution_l2": float(contribution.float().norm()),
        "global_prompt_contribution_rms": float(contribution.float().square().mean().sqrt()),
        "prompt_embeds_sha256": tensor_sha(prompt_embeds),
        "global_prompt_delta_from_cached_max_abs": float(delta.abs().max()),
        "global_prompt_delta_from_cached_l2": float(delta.norm()),
    }


def install_vae_trace(model, device: torch.device) -> dict:
    records: dict = {}
    weight_dtype = next(model.pipeline.vae.parameters()).dtype

    def encode_condition_image(images: torch.Tensor) -> torch.Tensor:
        images_pil = [v2.functional.to_pil_image(images[i].detach().cpu())
                      for i in range(images.shape[0])]
        pixels = model.pipeline.feature_extractor_vae(images=images_pil, return_tensors="pt").pixel_values
        pixels = pixels.to(device=device, dtype=weight_dtype)
        posterior = model.pipeline.vae.encode(pixels).latent_dist
        rng_before = torch.cuda.get_rng_state(device).cpu().numpy().tobytes()
        mean = posterior.mean
        std = posterior.std
        sample = posterior.sample()
        noise = (sample.float() - mean.float()) / std.float().clamp_min(1e-8)
        rng_after = torch.cuda.get_rng_state(device).cpu().numpy().tobytes()
        records.update({
            "vae_processor_pixels_sha256": tensor_sha(pixels),
            "vae_processor_pixels_shape": list(pixels.shape),
            "vae_processor_pixels_min": float(pixels.float().min()),
            "vae_processor_pixels_max": float(pixels.float().max()),
            "posterior_mean_sha256": tensor_sha(mean),
            "posterior_std_sha256": tensor_sha(std),
            "posterior_sample_sha256": tensor_sha(sample),
            "posterior_noise_sha256": tensor_sha(noise),
            "cuda_rng_before_posterior_sha256": sha_bytes(rng_before),
            "cuda_rng_after_posterior_sha256": sha_bytes(rng_after),
        })
        return sample

    model.encode_condition_image = encode_condition_image
    return records


def tensor_grid_to_uint8(image: torch.Tensor) -> np.ndarray:
    array = image.detach().float().clamp(0, 1)[0].cpu().permute(1, 2, 0).numpy()
    return np.rint(array * 255.0).astype(np.uint8)


def tensor_grid_tiles(tensor: torch.Tensor) -> list[np.ndarray]:
    array = tensor_grid_to_uint8(tensor)
    h, w = array.shape[:2]
    if h % 3 or w % 2:
        raise ValueError(f"not a 3x2 view grid: {array.shape}")
    th, tw = h // 3, w // 2
    return [array[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
            for r in range(3) for c in range(2)]


def tile_mask_grid(mask: torch.Tensor) -> list[np.ndarray]:
    array = mask.detach().float()[0, 0].cpu().numpy()
    h, w = array.shape
    th, tw = h // 3, w // 2
    return [array[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
            for r in range(3) for c in range(2)]


def tile_lab_stats(rgb: np.ndarray, mask: np.ndarray) -> tuple[float, float, float, int]:
    image = rgb.astype(np.float32) / 255.0
    region = np.asarray(mask) >= 0.5
    count = int(region.sum())
    if count == 0:
        return float("nan"), float("nan"), float("nan"), 0
    lab = rgb2lab(image)
    return (float(np.mean(lab[..., 1][region])),
            float(np.mean(lab[..., 2][region])),
            float(np.mean(lab[..., 0][region])), count)


def tile_probe_values(
    pred: np.ndarray,
    baseline: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
    input_da: float,
    input_db: float,
) -> dict:
    region = np.asarray(mask) >= 0.5
    if int(region.sum()) < 16:
        raise ValueError("too few geometry-mask pixels for per-view probe")
    pred_lab = rgb2lab(pred.astype(np.float32) / 255.0)
    base_lab = rgb2lab(baseline.astype(np.float32) / 255.0)
    target_lab = rgb2lab(target.astype(np.float32) / 255.0)
    out_da = float(np.mean((pred_lab[..., 1] - base_lab[..., 1])[region]))
    out_db = float(np.mean((pred_lab[..., 2] - base_lab[..., 2])[region]))
    denom = input_da * input_da + input_db * input_db
    projection = ((input_da * out_da + input_db * out_db) / denom) if denom else 0.0
    delta_e_from_base = float(np.mean(deltaE_ciede2000(pred_lab[region], base_lab[region])))
    delta_e_to_gt = float(np.mean(deltaE_ciede2000(pred_lab[region], target_lab[region])))
    base_delta_e_to_gt = float(np.mean(deltaE_ciede2000(base_lab[region], target_lab[region])))
    mean_abs_dL = float(np.mean(np.abs((pred_lab[..., 0] - base_lab[..., 0])[region])))
    pred_gray = pred_lab[..., 0]
    base_gray = base_lab[..., 0]
    _, ssim_map = structural_similarity(base_gray, pred_gray, data_range=100.0,
                                         full=True, gaussian_weights=True)
    ssim_fg = float(np.mean(ssim_map[region]))
    return {
        "output_delta_a_star_vs_gfl": out_da,
        "output_delta_b_star_vs_gfl": out_db,
        "response_projection_on_input_direction": projection,
        "output_ciede2000_vs_gfl": delta_e_from_base,
        "gfl_ciede2000_vs_gt": base_delta_e_to_gt,
        "condition_ciede2000_vs_gt": delta_e_to_gt,
        "delta_ciede2000_vs_gt": delta_e_to_gt - base_delta_e_to_gt,
        "mean_abs_delta_l_star_vs_gfl": mean_abs_dL,
        "foreground_lstar_ssim_vs_gfl": ssim_fg,
    }


def sha_png(path: Path) -> str:
    return sha_file(path)


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true",
                        help="load the frozen model and audit data/encoding identities without denoising")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "predictions").mkdir(exist_ok=True)
    lock = json.loads(LOCK.read_text())
    gpu_amendment = json.loads(GPU_AMENDMENT.read_text())
    device = torch.device("cuda:0")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; refusing to claim GPU intervention")
    if sha_file(CHECKPOINT) != lock["checkpoint"]["sha256"]:
        raise RuntimeError("checkpoint identity differs from the locked protocol")
    if sha_file(CONFIG) != lock["config"]["sha256"]:
        raise RuntimeError("config identity differs from the locked protocol")
    if not args.preflight_only and os.environ.get("CUDA_VISIBLE_DEVICES") != str(
        gpu_amendment["cuda_visible_devices"]
    ):
        raise RuntimeError("CUDA_VISIBLE_DEVICES does not match the pre-generation GPU amendment")

    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    model.unet.eval()
    model.pipeline.vae.eval()
    sampling_scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    vae_trace = install_vae_trace(model, device)
    base_seed = 42
    rows: list[dict] = []
    condition_records: list[dict] = []
    preflight_rows: list[dict] = []
    runtime = {
        "started_utc": utc_now(),
        "pid": os.getpid(),
        "python": sys.version,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "diffusers": __import__("diffusers").__version__,
        "transformers": __import__("transformers").__version__,
        "numpy": np.__version__,
        "device": torch.cuda.get_device_name(device),
        "visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "physical_gpu_index": gpu_amendment["physical_gpu_index"],
        "visible_device_index": device.index,
        "device_total_memory_bytes": torch.cuda.get_device_properties(device).total_memory,
        "device_compute_capability": list(torch.cuda.get_device_capability(device)),
        "device_uuid": torch.cuda.get_device_properties(device).uuid if hasattr(torch.cuda.get_device_properties(device), "uuid") else None,
        "unet_dtype": str(next(model.unet.parameters()).dtype),
        "vae_dtype": str(next(model.pipeline.vae.parameters()).dtype),
        "vae_config": dict(model.pipeline.vae.config),
        "vae_image_processor_class": type(model.pipeline.feature_extractor_vae).__name__,
        "vae_image_processor_config": model.pipeline.feature_extractor_vae.to_dict(),
        "vision_processor_class": type(model.pipeline.vision_processor).__name__,
        "vision_processor_config": model.pipeline.vision_processor.to_dict(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
        "cudnn_tf32": torch.backends.cudnn.allow_tf32,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "flash_sdp": torch.backends.cuda.flash_sdp_enabled(),
        "mem_efficient_sdp": torch.backends.cuda.mem_efficient_sdp_enabled(),
        "math_sdp": torch.backends.cuda.math_sdp_enabled(),
        "checkpoint_sha256": sha_file(CHECKPOINT),
        "config_sha256": sha_file(CONFIG),
        "parent_protocol_sha256": sha_file(LOCK),
        "embedding_control_amendment_sha256": sha_file(AMENDMENT),
        "gpu_binding_amendment_sha256": sha_file(GPU_AMENDMENT),
        "freshb_input_only_audit_sha256": sha_file(INPUT_AUDIT),
        "freshb_input_embedding_provenance_sha256": sha_file(INPUT_PROVENANCE),
        "current_runner_sha256": sha_file(Path(__file__)),
        "generation_helper_sha256": sha_file(ROOT / "geotex/explore_contradiction.py"),
        "validation_runner_sha256_from_prior_campaign": lock["prior_campaign_runner_sha256"],
        "pipeline_scheduler_class": type(model.pipeline.scheduler).__name__,
        "pipeline_scheduler_config": dict(model.pipeline.scheduler.config),
        "sampling_scheduler_class": type(sampling_scheduler).__name__,
        "sampling_scheduler_config": dict(sampling_scheduler.config),
        "unet_attention_implementation": getattr(model.unet.config, "_attn_implementation", None),
        "xformers_available": importlib.util.find_spec("xformers") is not None,
        "status": "running",
    }
    (OUT / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
    state = {"status": "running", "pid": os.getpid(), "completed_generation_count": 0,
             "started_utc": runtime["started_utc"], "last_object_uid": None, "last_condition": None}
    (OUT / "run_state.json").write_text(json.dumps(state, indent=2) + "\n")

    roots: dict[str, list[dict]] = {}
    for item in lock["objects"]:
        tag = "legacy_fig4" if "rendered_full" in item["root"] else "freshc_dev"
        roots.setdefault(tag, []).append(item)

    for tag, objects in roots.items():
        root = Path(objects[0]["root"])
        dataset = load_data(root, [o["uid"] for o in objects])
        for local_idx, spec in enumerate(objects):
            uid = spec["uid"]
            seed_all(int(spec["object_seed"]))
            item = dataset[local_idx]
            if "global_embeds" not in item:
                raise RuntimeError(f"missing cached global embedding for {uid}")
            if getattr(dataset, "_v2_condition_alpha", None) is None:
                raise RuntimeError(f"missing source alpha mask for {uid}")
            batch = {key: value.unsqueeze(0).to(device) if torch.is_tensor(value) else value
                     for key, value in item.items()}
            source_rgb = item["cond_imgs"].detach().cpu().permute(1, 2, 0).numpy().astype(np.float32)
            source_alpha = dataset._v2_condition_alpha.detach().cpu().squeeze().numpy().astype(np.float32)
            source_file = Path(dataset._v2_condition_path)
            source_sha = sha_file(source_file)
            cond_hash = tensor_sha(item["cond_imgs"])
            alpha_hash = tensor_sha(dataset._v2_condition_alpha)
            cached_embedding = item["global_embeds"].unsqueeze(0).to(device)
            cached_embedding_hash = tensor_sha(item["global_embeds"])

            # Recompute the unperturbed source embedding to isolate only the
            # color-induced feature delta, retaining the exact cache as baseline.
            baseline_encoded = encode_global_embedding(model, item["cond_imgs"].unsqueeze(0))
            cache_float = item["global_embeds"].detach().cpu().float().unsqueeze(0)
            cache_recompute_delta = baseline_encoded - cache_float
            cache_match = bool(torch.max(torch.abs(cache_recompute_delta)).item() <= 0.03)

            if args.preflight_only:
                source_view_path = Path(spec["root"]) / uid / "image" / f"{int(spec['source_view']):03d}.png"
                source_view_tensor, source_view_alpha = dataset.load_im(str(source_view_path), [1.0, 1.0, 1.0])
                target_source = item["target_imgs"][0]
                target_source_alpha = item["alpha_masks"][0]
                raw_source_embedding = encode_global_embedding(
                    model, source_view_tensor.unsqueeze(0)
                )
                cond_mask_bool = source_alpha >= 0.5
                target_mask_bool = target_source_alpha.squeeze().numpy() >= 0.5
                source_rgb_float = source_view_tensor.permute(1, 2, 0).numpy()
                cond_lab = rgb2lab(np.clip(source_rgb, 0, 1).astype(np.float32))
                source_lab = rgb2lab(np.clip(source_rgb_float, 0, 1).astype(np.float32))
                cond_med = np.median(cond_lab[cond_mask_bool], axis=0)
                source_med = np.median(source_lab[target_mask_bool], axis=0)
                condition_batch = item["cond_imgs"].unsqueeze(0)
                resized_condition = v2.functional.resize(
                    condition_batch, model.img_size, interpolation=3, antialias=True
                ).clamp(0, 1)
                vae_pil = [v2.functional.to_pil_image(resized_condition[0])]
                vae_pixels = model.pipeline.feature_extractor_vae(images=vae_pil, return_tensors="pt").pixel_values
                vision_pil = [v2.functional.to_pil_image(condition_batch[0])]
                vision_pixels = model.pipeline.vision_processor(images=vision_pil, return_tensors="pt").pixel_values
                intersection = int(np.logical_and(cond_mask_bool, target_mask_bool).sum())
                union = int(np.logical_or(cond_mask_bool, target_mask_bool).sum())
                preflight_rows.append({
                    "uid": uid,
                    "cohort": spec["cohort"],
                    "object_idx": spec["object_idx"],
                    "object_seed": spec["object_seed"],
                    "reverse": spec["reverse"],
                    "source_view_id": spec["source_view"],
                    "target_order": json.dumps(spec["target_order"]),
                    "source_target_is_tile0": int(spec["target_order"][0]) == int(spec["source_view"]),
                    "target_tile0_matches_raw_source_rgb": bool(torch.equal(target_source, source_view_tensor)),
                    "condition_source_path": str(source_file.resolve()),
                    "condition_source_png_sha256": source_sha,
                    "target_source_path": str(source_view_path.resolve()),
                    "target_source_png_sha256": sha_file(source_view_path),
                    "condition_tensor_sha256": cond_hash,
                    "condition_alpha_sha256": alpha_hash,
                    "condition_alpha_coverage": float(cond_mask_bool.mean()),
                    "target_source_alpha_coverage": float(target_mask_bool.mean()),
                    "condition_vs_target_mask_iou": float(intersection / max(union, 1)),
                    "condition_median_l_star": float(cond_med[0]),
                    "condition_median_a_star": float(cond_med[1]),
                    "condition_median_b_star": float(cond_med[2]),
                    "target_source_median_l_star": float(source_med[0]),
                    "target_source_median_a_star": float(source_med[1]),
                    "target_source_median_b_star": float(source_med[2]),
                    "condition_512_min": float(condition_batch.min()),
                    "condition_512_max": float(condition_batch.max()),
                    "condition_512_mean_rgb": json.dumps(condition_batch.float().mean(dim=(0, 2, 3)).tolist()),
                    "condition_512_sha256": tensor_sha(condition_batch),
                    "condition_256_sha256": tensor_sha(resized_condition),
                    "condition_256_min": float(resized_condition.min()),
                    "condition_256_max": float(resized_condition.max()),
                    "vae_processor_tensor_sha256": tensor_sha(vae_pixels),
                    "vae_processor_tensor_shape": json.dumps(list(vae_pixels.shape)),
                    "vae_processor_min": float(vae_pixels.min()),
                    "vae_processor_max": float(vae_pixels.max()),
                    "vision_processor_tensor_sha256": tensor_sha(vision_pixels),
                    "vision_processor_tensor_shape": json.dumps(list(vision_pixels.shape)),
                    "cached_global_embedding_sha256": cached_embedding_hash,
                    "recomputed_global_embedding_sha256": tensor_sha(baseline_encoded),
                    "cached_recomputed_max_abs_delta": float(torch.max(torch.abs(cache_recompute_delta)).item()),
                    "cached_recomputed_within_0p03": cache_match,
                    "raw_source_global_embedding_sha256": tensor_sha(raw_source_embedding),
                    "cached_raw_source_max_abs_delta": float(torch.max(torch.abs(
                        raw_source_embedding - item["global_embeds"].detach().cpu().float().unsqueeze(0)
                    )).item()),
                    "current_condition_raw_source_embedding_max_abs_delta": float(torch.max(torch.abs(
                        baseline_encoded - raw_source_embedding
                    )).item()),
                })
                continue

            _, gt_grid, _, _, geo_input, mask_grid = prepare_batch(batch, model.img_size, device)
            target_tiles = tensor_grid_tiles(gt_grid)
            masks = tile_mask_grid(mask_grid)
            with torch.inference_mode():
                geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
                geo_feats = model.geo_encoder(geo_clean)
            if isinstance(geo_feats, dict):
                geo_hashes = {
                    key: tensor_sha(value) for key, value in sorted(geo_feats.items())
                }
            elif isinstance(geo_feats, (tuple, list)):
                geo_hashes = [tensor_sha(value) for value in geo_feats]
            else:
                geo_hashes = [tensor_sha(geo_feats)]
            initial_h = model.img_size * 3 // 8
            initial_w = model.img_size * 2 // 8
            seed_all(base_seed)
            init_latents = torch.randn(1, 4, initial_h, initial_w, device=device, dtype=torch.float16)
            init_latent_hash = tensor_sha(init_latents)
            baseline_tile_images: list[np.ndarray] | None = None
            per_object_records: list[tuple[str, float, float, float, torch.Tensor, str]] = []

            def generate(condition_name: str, condition: torch.Tensor, embedding: torch.Tensor,
                         schedule, adapter_enabled: bool, input_da: float, input_db: float,
                         arm: str, requested_da: float, requested_db: float):
                nonlocal baseline_tile_images
                condition_hash = tensor_sha(condition)
                embed_hash = tensor_sha(embedding)
                if not torch.equal(condition[0].detach().cpu(), item["cond_imgs"]):
                    # The equality guard applies only to unperturbed settings.
                    if input_da == 0 and input_db == 0:
                        raise RuntimeError("baseline condition tensor changed unexpectedly")
                capture: dict = {}
                vae_trace.clear()
                seed_all(base_seed)
                prompt_trace = prompt_condition_trace(
                    model, embedding, cached_embedding, device, torch.float16
                )
                started = time.monotonic()
                pred = exp.generate_with_schedule(
                    model, {**batch, "cond_imgs": condition, "global_embeds": embedding},
                    device, torch.float16, geo_feats if adapter_enabled else None,
                    schedule, 50, init_latents.clone(), {},
                )
                torch.cuda.synchronize(device)
                elapsed = time.monotonic() - started
                path = OUT / "predictions" / uid / f"{condition_name}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                save_image(pred, path)
                with Image.open(path) as opened:
                    grid = np.asarray(opened.convert("RGB"))
                th, tw = grid.shape[0] // 3, grid.shape[1] // 2
                tiles = [grid[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
                         for r in range(3) for c in range(2)]
                if condition_name == "gfl_baseline":
                    baseline_tile_images = tiles
                if baseline_tile_images is None:
                    raise RuntimeError("paired GFL baseline must be generated first")
                label = "GFL" if condition_name == "gfl_baseline" else condition_name
                for tile_idx, (pred_tile, base_tile, gt_tile, mask_tile) in enumerate(
                        zip(tiles, baseline_tile_images, target_tiles, masks)):
                    values = tile_probe_values(
                        pred_tile, base_tile, gt_tile, mask_tile, input_da, input_db
                    )
                    rows.append({
                        "uid": uid,
                        "cohort": spec["cohort"],
                        "object_idx": spec["object_idx"],
                        "object_seed": spec["object_seed"],
                        "condition": condition_name,
                        "arm": arm,
                        "requested_input_delta_a_star": requested_da,
                        "requested_input_delta_b_star": requested_db,
                        "effective_input_delta_a_star": input_da,
                        "effective_input_delta_b_star": input_db,
                        "target_tile_index": tile_idx,
                        "target_view_id": spec["target_order"][tile_idx],
                        "is_source_view": tile_idx == 0,
                        "foreground_pixels": int(np.sum(np.asarray(mask_tile) >= 0.5)),
                        **values,
                        "condition_tensor_sha256": condition_hash,
                        "global_embedding_sha256": embed_hash,
                        "cached_global_embedding_sha256": cached_embedding_hash,
                        "cache_recompute_max_abs_delta": float(torch.max(torch.abs(cache_recompute_delta)).item()),
                        "cache_recompute_identity_within_0p03": cache_match,
                        "source_png_sha256": source_sha,
                        "source_condition_tensor_sha256": cond_hash,
                        "source_alpha_mask_sha256": alpha_hash,
                        "geometry_feature_sha256": json.dumps(geo_hashes),
                        "initial_latent_sha256": init_latent_hash,
                        **prompt_trace,
                        "vae_processor_pixels_sha256": vae_trace.get("vae_processor_pixels_sha256"),
                        "posterior_mean_sha256": vae_trace.get("posterior_mean_sha256"),
                        "posterior_std_sha256": vae_trace.get("posterior_std_sha256"),
                        "posterior_sample_sha256": vae_trace.get("posterior_sample_sha256"),
                        "posterior_noise_sha256": vae_trace.get("posterior_noise_sha256"),
                        "posterior_rng_before_sha256": vae_trace.get("cuda_rng_before_posterior_sha256"),
                        "posterior_rng_after_sha256": vae_trace.get("cuda_rng_after_posterior_sha256"),
                        "prediction_png": str(path.resolve()),
                        "prediction_png_sha256": sha_png(path),
                        "generation_elapsed_seconds": elapsed,
                    })
                condition_records.append({
                    "uid": uid,
                    "condition": condition_name,
                    "arm": arm,
                    "input_delta_ab": [input_da, input_db],
                    "source_rgb_tensor_sha256": condition_hash,
                    "global_embedding_sha256": embed_hash,
                    "cached_embedding_sha256": cached_embedding_hash,
                    "cached_vs_recomputed_max_abs_delta": float(torch.max(torch.abs(cache_recompute_delta)).item()),
                    "cached_vs_recomputed_within_0p03": cache_match,
                    "initial_latent_sha256": init_latent_hash,
                    **prompt_trace,
                    **vae_trace,
                    "prediction_png": str(path.resolve()),
                    "prediction_png_sha256": sha_png(path),
                    "elapsed_seconds": elapsed,
                })
                state["completed_generation_count"] += 1
                state["last_object_uid"] = uid
                state["last_condition"] = condition_name
                state["updated_utc"] = utc_now()
                (OUT / "run_state.json").write_text(json.dumps(state, indent=2) + "\n")
                write_rows(OUT / "COLOR_INTERVENTION_RESULTS.csv", rows)
                (OUT / "condition_encoding_trace.json").write_text(
                    json.dumps(condition_records, indent=2, default=str) + "\n"
                )
                del pred
                torch.cuda.empty_cache()

            baseline_condition = item["cond_imgs"].unsqueeze(0).to(device)
            generate("gfl_baseline", baseline_condition, cached_embedding, lambda p: 1.25,
                     True, 0.0, 0.0, "baseline", 0.0, 0.0)

            refreshed_embedding = replace_cached_embedding(
                item["global_embeds"].detach().cpu(), baseline_encoded
            ).unsqueeze(0).to(device)
            generate("global_embedding_recomputed", baseline_condition, refreshed_embedding,
                     lambda p: 1.25, True, 0.0, 0.0,
                     "embedding_cache_consistency_control", 0.0, 0.0)

            for da, db in lock["intervention_matrix"]["directions"]:
                perturbed_np = perturb_foreground_lab(source_rgb, source_alpha, da, db)
                perturbed_condition = torch.from_numpy(perturbed_np).permute(2, 0, 1).unsqueeze(0).to(
                    device=device, dtype=item["cond_imgs"].dtype
                )
                perturbed_embedding = encode_global_embedding(model, perturbed_condition)
                embed_delta = perturbed_embedding - baseline_encoded
                adjusted_embedding = (cache_float + embed_delta).to(
                    device=device, dtype=item["global_embeds"].dtype
                )
                for arm, cond_tensor, embed_tensor in (
                    ("vae_and_embedding", perturbed_condition, adjusted_embedding),
                    ("vae_only", perturbed_condition, cached_embedding),
                    ("embedding_only", baseline_condition, adjusted_embedding),
                ):
                    name = f"{arm}_da{da:+g}_db{db:+g}".replace("+", "p").replace("-", "m")
                    # Record effective input direction after Lab/RGB gamut and alpha handling.
                    p_rgb = perturbed_np
                    perturbed_lab = rgb2lab(np.clip(p_rgb, 0, 1).astype(np.float32))
                    original_lab = rgb2lab(np.clip(source_rgb, 0, 1).astype(np.float32))
                    weighted = source_alpha >= 0.75
                    actual_da = float(np.mean((perturbed_lab[..., 1] - original_lab[..., 1])[weighted]))
                    actual_db = float(np.mean((perturbed_lab[..., 2] - original_lab[..., 2])[weighted]))
                    generate(name, cond_tensor, embed_tensor, lambda p: 1.25, True,
                             actual_da, actual_db, arm, da, db)

            generate("no_adapter", baseline_condition, cached_embedding, lambda p: 0.0,
                     False, 0.0, 0.0, "adapter_reference", 0.0, 0.0)

            def llh_schedule(progress: float) -> dict:
                step = int(round(progress * 49))
                level = (1.25 if step <= 16 else 1.25 if step <= 32 else 2.50)
                shallow = (0.50 if step <= 32 else 0.75)
                return {"deep": level, "middle": level, "shallow": shallow}

            generate("layer_llh", baseline_condition, cached_embedding, llh_schedule,
                     True, 0.0, 0.0, "adapter_reference", 0.0, 0.0)

    runtime["finished_utc"] = utc_now()
    if args.preflight_only:
        runtime["status"] = "preflight_complete"
        runtime["gpu_generation_count"] = 0
        (OUT / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
        with (OUT / "A_CONDITION_ENCODING_TRACE.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(preflight_rows[0]))
            writer.writeheader()
            writer.writerows(preflight_rows)
        state["status"] = "preflight_complete"
        state["updated_utc"] = utc_now()
        (OUT / "run_state.json").write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps({"status": "preflight_complete", "objects": len(preflight_rows),
                          "gpu_generation_count": 0,
                          "trace": str((OUT / "A_CONDITION_ENCODING_TRACE.csv").resolve())}, indent=2), flush=True)
        return
    runtime["gpu_generation_count"] = int(state["completed_generation_count"])
    expected_count = int(gpu_amendment["expected_total_generation_calls"])
    if runtime["gpu_generation_count"] != expected_count:
        runtime["status"] = "incomplete"
        (OUT / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
        state["status"] = "incomplete"
        state["updated_utc"] = utc_now()
        (OUT / "run_state.json").write_text(json.dumps(state, indent=2) + "\n")
        raise RuntimeError(
            f"completed {runtime['gpu_generation_count']} generation calls; expected {expected_count}"
        )
    runtime["gpu_generation_wall_seconds"] = float(sum(
        record["elapsed_seconds"] for record in condition_records
    ))
    runtime["status"] = "complete"
    (OUT / "runtime.json").write_text(json.dumps(runtime, indent=2, default=str) + "\n")
    state["status"] = "complete"
    state["updated_utc"] = utc_now()
    (OUT / "run_state.json").write_text(json.dumps(state, indent=2) + "\n")
    (OUT / "run_manifest.json").write_text(json.dumps({
        "status": "complete",
        "protocol_sha256": sha_file(LOCK),
        "embedding_control_amendment_sha256": sha_file(AMENDMENT),
        "gpu_binding_amendment_sha256": sha_file(GPU_AMENDMENT),
        "freshb_input_only_audit_sha256": sha_file(INPUT_AUDIT),
        "freshb_input_embedding_provenance_sha256": sha_file(INPUT_PROVENANCE),
        "runtime_sha256": sha_file(OUT / "runtime.json"),
        "result_csv_sha256": sha_file(OUT / "COLOR_INTERVENTION_RESULTS.csv"),
        "condition_trace_sha256": sha_file(OUT / "condition_encoding_trace.json"),
        "gpu_generation_count": runtime["gpu_generation_count"],
        "gpu_generation_wall_seconds": runtime["gpu_generation_wall_seconds"],
        "started_utc": runtime["started_utc"],
        "finished_utc": runtime["finished_utc"],
    }, indent=2) + "\n")
    print(json.dumps({"status": "complete", "generation_count": runtime["gpu_generation_count"],
                      "generation_seconds": runtime["gpu_generation_wall_seconds"],
                      "outputs": str(OUT)}, indent=2), flush=True)


if __name__ == "__main__":
    main()

