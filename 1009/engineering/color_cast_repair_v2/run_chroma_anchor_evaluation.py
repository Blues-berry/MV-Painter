#!/usr/bin/env python3
"""Apply the frozen C1 chroma anchor to paired six-view RGB and score it."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage
from skimage.color import deltaE_ciede2000, rgb2lab
from skimage.metrics import structural_similarity
from omegaconf import OmegaConf

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

from color_repair import source_conditioned_chroma_anchor
from geotex.data_utils import prepare_batch
from geotex.metrics import compute_psnr
from src.utils.train_util import instantiate_from_config

C1_LOCK = HERE / "protocol/C1_DEV_METHOD_LOCK.json"
B_LOCK = HERE / "protocol/B_PROTOCOL_LOCK.json"
B_RUN = HERE / "runs/phase_b"
HOLDOUT_LOCK = HERE / "protocol/D_VALIDATION_LOCK.json"
HOLDOUT_AMENDMENT = HERE / "protocol/D_VALIDATION_AMENDMENT_01.json"
FINAL_METHOD_LOCK = HERE / "protocol/C_REPAIR_METHOD_LOCK.json"
PRIOR_EVIDENCE = ROOT / "1008/engineering/fidelity_validation_48h"
PRIOR_RESULTS = PRIOR_EVIDENCE / "B_OBJECT_LEVEL_RESULTS.csv"
INPUT_PAIR_AUDIT = PRIOR_EVIDENCE / "ALL_COHORT_INPUT_PAIR_AUDIT.csv"
OUTPUT_AUDIT = PRIOR_EVIDENCE / "RGB_HASH_AND_INPUT_AUDIT.csv"
FRESH_B_ROOT = BASE / "data/fresh_confirm_v3_renders"
PRIOR_CAMPAIGN = BASE / "final/round2/scientific_validation_v3/formal/campaign_FRESH_CONFIRM_B_20261005"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty result table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def hash_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def grid_tiles(rgb: np.ndarray) -> list[np.ndarray]:
    h, w = rgb.shape[:2]
    if h % 3 or w % 2:
        raise ValueError(f"expected a 3x2 unique6 image grid, got {rgb.shape}")
    th, tw = h // 3, w // 2
    return [rgb[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
            for r in range(3) for c in range(2)]


def grid_masks(mask: torch.Tensor) -> list[np.ndarray]:
    arr = mask.detach().float().cpu().numpy()[0, 0]
    h, w = arr.shape
    th, tw = h // 3, w // 2
    return [arr[r * th:(r + 1) * th, c * tw:(c + 1) * tw]
            for r in range(3) for c in range(2)]


def grid_targets(target: torch.Tensor) -> list[np.ndarray]:
    arr = target.detach().float().clamp(0, 1).cpu().numpy()[0]
    arr = np.transpose(arr, (1, 2, 0))
    h, w = arr.shape[:2]
    th, tw = h // 3, w // 2
    return [np.floor(np.clip(arr[r * th:(r + 1) * th, c * tw:(c + 1) * tw], 0, 1) * 255 + 0.5).astype(np.uint8)
            for r in range(3) for c in range(2)]


def stitch(tiles: list[np.ndarray]) -> np.ndarray:
    return np.concatenate([
        np.concatenate(tiles[row * 2:(row + 1) * 2], axis=1)
        for row in range(3)
    ], axis=0)


def ssim_masked(x: np.ndarray, y: np.ndarray, mask: np.ndarray, data_range: float) -> float:
    _, sim = structural_similarity(x, y, data_range=data_range, full=True)
    valid = np.asarray(mask) >= 0.5
    return float(np.mean(sim[valid])) if np.any(valid) else float("nan")


def laplacian_error(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    kernel = np.asarray([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    valid = ndimage.binary_erosion(np.asarray(mask) >= 0.5, iterations=1, border_value=0)
    if not np.any(valid):
        return float("nan")
    pred_lap = np.stack([ndimage.convolve(pred[..., c], kernel, mode="reflect") for c in range(3)], -1)
    target_lap = np.stack([ndimage.convolve(target[..., c], kernel, mode="reflect") for c in range(3)], -1)
    return float(np.abs(pred_lap[valid] - target_lap[valid]).mean())


def lpips_values(model, pred: list[np.ndarray], target: list[np.ndarray], masks: list[np.ndarray]) -> list[float]:
    if model is None:
        raise RuntimeError("AlexNet LPIPS is unavailable; refusing to claim the locked quality gate")
    p = torch.from_numpy(np.stack(pred).transpose(0, 3, 1, 2)).float() / 255.0
    t = torch.from_numpy(np.stack(target).transpose(0, 3, 1, 2)).float() / 255.0
    m = torch.from_numpy(np.stack(masks)[:, None]).float()
    # Match geotex.eval_exploration.compute_lpips exactly: normalize first, then mask.
    p = (p * 2.0 - 1.0) * m
    t = (t * 2.0 - 1.0) * m
    with torch.inference_mode():
        return [float(v) for v in model(p, t).reshape(-1).cpu().tolist()]


def tile_metrics(pred: np.ndarray, target: np.ndarray, baseline: np.ndarray,
                 mask: np.ndarray, lpips_value: float) -> dict:
    valid = np.asarray(mask) >= 0.5
    if int(valid.sum()) < 16:
        raise ValueError("foreground mask is too small for a per-view metric")
    pred_f = pred.astype(np.float32) / 255.0
    base_f = baseline.astype(np.float32) / 255.0
    target_f = target.astype(np.float32) / 255.0
    pred_lab = rgb2lab(pred_f)
    base_lab = rgb2lab(base_f)
    target_lab = rgb2lab(target_f)

    def as_tensor(rgb: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(rgb.transpose(2, 0, 1).copy()).float().unsqueeze(0)

    mask_tensor = torch.from_numpy(np.asarray(mask, dtype=np.float32)).unsqueeze(0).unsqueeze(0)
    pred_tensor, base_tensor, target_tensor = map(as_tensor, (pred_f, base_f, target_f))
    lstar_base = base_lab[..., 0]
    lstar_pred = pred_lab[..., 0]
    color_clip_base = np.any((baseline == 0) | (baseline == 255), axis=-1)
    color_clip_pred = np.any((pred == 0) | (pred == 255), axis=-1)
    return {
        "gfl_fg_ciede2000": float(deltaE_ciede2000(base_lab[valid], target_lab[valid]).mean()),
        "candidate_fg_ciede2000": float(deltaE_ciede2000(pred_lab[valid], target_lab[valid]).mean()),
        "delta_fg_ciede2000": float(deltaE_ciede2000(pred_lab[valid], target_lab[valid]).mean()
                                      - deltaE_ciede2000(base_lab[valid], target_lab[valid]).mean()),
        "gfl_fg_psnr": float(compute_psnr(base_tensor, target_tensor, mask_tensor)),
        "candidate_fg_psnr": float(compute_psnr(pred_tensor, target_tensor, mask_tensor)),
        "delta_fg_psnr": float(compute_psnr(pred_tensor, target_tensor, mask_tensor)
                                - compute_psnr(base_tensor, target_tensor, mask_tensor)),
        "candidate_fg_lpips": lpips_value,
        "gfl_foreground_lstar_ssim_to_gt": ssim_masked(lstar_base, target_lab[..., 0], mask, 100.0),
        "candidate_foreground_lstar_ssim_to_gt": ssim_masked(lstar_pred, target_lab[..., 0], mask, 100.0),
        "candidate_lstar_ssim_vs_gfl": ssim_masked(lstar_pred, lstar_base, mask, 100.0),
        "mean_abs_lstar_change_vs_gfl": float(np.mean(np.abs(lstar_pred[valid] - lstar_base[valid]))),
        "gfl_gt_laplacian_error": laplacian_error(base_f, target_f, mask),
        "candidate_gt_laplacian_error": laplacian_error(pred_f, target_f, mask),
        "delta_gt_laplacian_error": float(laplacian_error(pred_f, target_f, mask)
                                            - laplacian_error(base_f, target_f, mask)),
        "gfl_endpoint_pixel_fraction": float(color_clip_base[valid].mean()),
        "candidate_endpoint_pixel_fraction": float(color_clip_pred[valid].mean()),
        "background_changed_fraction": float(np.any(pred != baseline, axis=-1)[np.asarray(mask) <= 0].mean())
        if np.any(np.asarray(mask) <= 0) else 0.0,
        "foreground_pixels": int(valid.sum()),
    }


def load_item(dataset, index: int, spec: dict) -> tuple:
    random.seed(int(spec["object_seed"]))
    np.random.seed(int(spec["object_seed"]))
    with redirect_stdout(io.StringIO()):
        item = dataset[index]
    alpha = getattr(dataset, "_v2_condition_alpha", None)
    source_path = getattr(dataset, "_v2_condition_path", None)
    if alpha is None or source_path is None:
        raise RuntimeError(f"source condition alpha/path unavailable for {spec['uid']}")
    batch = {key: value.unsqueeze(0) if torch.is_tensor(value) else value
             for key, value in item.items()}
    _, target_grid, _, _, _, mask_grid = prepare_batch(batch, 256, "cpu")
    source_rgb = item["cond_imgs"].detach().cpu().permute(1, 2, 0).numpy().astype(np.float32)
    source_alpha = alpha.detach().cpu().squeeze().numpy().astype(np.float32)
    return (
        source_rgb, source_alpha, grid_targets(target_grid), grid_masks(mask_grid),
        item, Path(source_path),
    )


def _load_data(root: Path, uids: list[str]):
    uid_bytes = ("\n".join(uids) + "\n").encode()
    list_name = hashlib.sha256(uid_bytes).hexdigest()[:16]
    list_dir = HERE / "runs/phase_c/object_lists"
    list_dir.mkdir(parents=True, exist_ok=True)
    list_path = list_dir / f"{list_name}.txt"
    list_path.write_bytes(uid_bytes)
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.root_dir_list = [str(root)]
    validation.params.object_list_file = str(list_path.resolve())
    with redirect_stdout(io.StringIO()):
        dataset = instantiate_from_config(validation)
    original = dataset.load_im_cond

    def capture_condition_alpha(path, color, random_ratio=0.8):
        condition, alpha = original(path, color, random_ratio)
        dataset._v2_condition_alpha = alpha
        dataset._v2_condition_path = str(path)
        return condition, alpha

    dataset.load_im_cond = capture_condition_alpha
    return dataset


def dev_objects() -> list[dict]:
    lock = json.loads(B_LOCK.read_text())
    return [{**obj, "object_seed": int(obj["object_seed"])} for obj in lock["objects"]]


def holdout_objects() -> list[dict]:
    if not FINAL_METHOD_LOCK.exists() or not HOLDOUT_AMENDMENT.exists():
        raise RuntimeError("holdout is sealed until C_REPAIR_METHOD_LOCK and D_VALIDATION_AMENDMENT_01 exist")
    final_lock = json.loads(FINAL_METHOD_LOCK.read_text())
    amendment = json.loads(HOLDOUT_AMENDMENT.read_text())
    c1_lock = json.loads(C1_LOCK.read_text())
    if final_lock.get("validation_authorized") is not True:
        raise RuntimeError("final repair lock does not authorize the independent validation")
    if final_lock.get("phase_b_supports_candidate") is not True:
        raise RuntimeError("Phase B did not support the locked candidate; Fresh B remains sealed")
    if final_lock.get("development_gate_pass") is not True:
        raise RuntimeError("the frozen development gate failed; Fresh B remains sealed")
    if final_lock.get("candidate_code_sha256") != c1_lock["implementation"]["sha256"]:
        raise RuntimeError("final repair lock code hash does not match the frozen candidate")
    if amendment.get("candidate_method_lock_sha256") != sha_file(FINAL_METHOD_LOCK):
        raise RuntimeError("validation amendment does not pin the final repair lock")
    if amendment.get("c1_development_method_lock_sha256") != sha_file(C1_LOCK):
        raise RuntimeError("validation amendment does not pin the development method lock")
    if amendment.get("d_validation_protocol_sha256") != sha_file(HOLDOUT_LOCK):
        raise RuntimeError("validation amendment does not pin the Fresh B protocol")
    if amendment.get("holdout_uid_list_sha256") != json.loads(HOLDOUT_LOCK.read_text())["cohort_list_sha256"]:
        raise RuntimeError("validation amendment has the wrong Fresh B UID list")

    rows = [r for r in read_csv(PRIOR_RESULTS) if r["cohort"] == "FreshB"]
    input_rows = {r["uid"]: r for r in read_csv(INPUT_PAIR_AUDIT) if r["cohort"] == "FreshB"}
    output_rows = {(r["uid"], r["condition"]): r for r in read_csv(OUTPUT_AUDIT) if r["cohort"] == "FreshB"}
    rows.sort(key=lambda r: int(r["object_idx"]))
    if len(rows) != 150:
        raise RuntimeError(f"expected all 150 Fresh B rows, found {len(rows)}")
    list_path = BASE / "final/round2/scientific_validation_v3/fresh_confirm_b/fresh_confirm_b.txt"
    frozen_uids = [line.strip() for line in list_path.read_text().splitlines() if line.strip()]
    if sha_file(list_path) != json.loads(HOLDOUT_LOCK.read_text())["cohort_list_sha256"]:
        raise RuntimeError("Fresh B UID list SHA differs from the frozen validation protocol")
    if frozen_uids != [row["uid"] for row in rows]:
        raise RuntimeError("Fresh B RGB manifest order differs from the frozen UID list")
    out = []
    for row in rows:
        uid = row["uid"]
        src = input_rows.get(uid)
        out_record = output_rows.get((uid, "native_gfl"))
        if src is None or out_record is None or out_record.get("output_sha_pass") != "True":
            raise RuntimeError(f"missing source or verified GFL identity row for {uid}")
        prior_manifest = PRIOR_CAMPAIGN / f"run_manifest_shard{int(row['object_idx']) % 2}.json"
        out.append({
            "uid": uid,
            "object_idx": int(row["object_idx"]),
            "object_seed": int(row["object_seed"]),
            "root": str(FRESH_B_ROOT),
            "prediction_path": row["gfl_prediction_png"],
            "prediction_sha256": row["gfl_prediction_sha256"],
            "target_view_ids": json.loads(row["target_view_ids"]),
            "source_view_id": json.loads(row["target_view_ids"])[0],
            "reverse_view_rotation": row["reverse_view_rotation"],
            "input_cond_sha256": src["input_cond_sha256"],
            "input_target_sha256": src["input_target_sha256"],
            "input_normal_sha256": src["input_normal_sha256"],
            "input_depth_sha256": src["input_depth_sha256"],
            "input_global_embeds_sha256": src["input_global_embeds_sha256"],
            "input_hash_audit_sha256": sha_file(INPUT_PAIR_AUDIT),
            "source_output_audit_sha256": sha_file(OUTPUT_AUDIT),
            "baseline_generation_manifest_sha256": sha_file(prior_manifest),
            "gt_fg_lap_var": float(row["gt_fg_lap_var"]),
            "gt_texture_quartile": int(row["gt_laplacian_quartile_fixed_B_cutpoints"]),
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=("dev", "holdout"), required=True)
    args = parser.parse_args()
    c1_lock = json.loads(C1_LOCK.read_text())
    if sha_file(HERE / "color_repair.py") != c1_lock["implementation"]["sha256"]:
        raise RuntimeError("color_repair.py changed after C1 method lock")

    if args.cohort == "dev":
        manifest = B_RUN / "run_manifest.json"
        if not manifest.exists() or json.loads(manifest.read_text()).get("status") != "complete":
            raise RuntimeError("development correction requires a complete Phase B run")
        objects = dev_objects()
        if [obj["uid"] for obj in objects] != c1_lock["development_objects"]:
            raise RuntimeError("development objects differ from the C1 method lock")
        runtime = json.loads((B_RUN / "runtime.json").read_text())
        b_manifest_sha = sha_file(manifest)
        for obj in objects:
            obj["baseline_generation_manifest_sha256"] = b_manifest_sha
            obj["baseline_runner_sha256"] = runtime["current_runner_sha256"]
        out_dir = HERE / "runs/phase_c/dev"
        _require_empty_output_dir(out_dir)
        input_root_by_obj = {o["uid"]: Path(o["root"]) for o in objects}
        gfl_rows = {(r["uid"], r["condition"]): r for r in read_csv(B_RUN / "COLOR_INTERVENTION_RESULTS.csv")
                    if r["condition"] == "gfl_baseline"}
        if len(gfl_rows) != len(objects):
            raise RuntimeError("incomplete development GFL baseline identity rows")
        paired = []
        for root, group in _groups(objects, input_root_by_obj).items():
            dataset = _load_data(root, [obj["uid"] for obj in group])
            for spec in group:
                uid = spec["uid"]
                condition = gfl_rows[(uid, "gfl_baseline")]
                baseline_path = Path(condition["prediction_png"])
                if sha_file(baseline_path) != condition["prediction_png_sha256"]:
                    raise RuntimeError(f"development baseline SHA mismatch: {uid}")
                data = load_item(dataset, group.index(spec), spec)
                paired.append(_process_object(spec, data, baseline_path, out_dir, args.cohort))
        _finish(out_dir, paired, c1_lock)
        return

    objects = holdout_objects()
    source_dataset = _load_data(FRESH_B_ROOT, [obj["uid"] for obj in objects])
    out_dir = HERE / "runs/phase_d/freshb"
    _require_empty_output_dir(out_dir)
    paired = []
    for index, spec in enumerate(objects):
        data = load_item(source_dataset, index, spec)
        item = data[4]
        reconstructed_hashes = {
            "cond": tensor_sha(item["cond_imgs"]),
            "target": tensor_sha(item["target_imgs"]),
            "normal": tensor_sha(item["depth_imgs"]),
            "depth": tensor_sha(item["real_depth_imgs"]),
            "global_embeds": tensor_sha(item["global_embeds"]),
        }
        expected_hashes = {
            "cond": spec["input_cond_sha256"],
            "target": spec["input_target_sha256"],
            "normal": spec["input_normal_sha256"],
            "depth": spec["input_depth_sha256"],
            "global_embeds": spec["input_global_embeds_sha256"],
        }
        if reconstructed_hashes != expected_hashes:
            raise RuntimeError(f"reconstructed Fresh B model input tensors differ from the frozen hashes: {spec['uid']}")
        baseline_path = Path(spec["prediction_path"])
        if sha_file(baseline_path) != spec["prediction_sha256"]:
            raise RuntimeError(f"Fresh B GFL baseline PNG SHA mismatch: {spec['uid']}")
        if index != spec["object_idx"]:
            raise RuntimeError("Fresh B rows no longer follow the frozen list order")
        paired.append(_process_object(spec, data, baseline_path, out_dir, args.cohort))
        if (index + 1) % 10 == 0:
            print(f"processed {index + 1}/150 Fresh B objects", flush=True)
    if len(paired) != 150:
        raise RuntimeError("Fresh B validation cohort identity/count changed")
    _finish(out_dir, paired, c1_lock)


def _require_empty_output_dir(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to overwrite or mix an existing run: {path}")


def _groups(objects: list[dict], roots: dict[str, Path]) -> dict[Path, list[dict]]:
    result: dict[Path, list[dict]] = {}
    for obj in objects:
        result.setdefault(roots[obj["uid"]], []).append(obj)
    return result


def _process_object(spec: dict, data: tuple, baseline_path: Path,
                    out_dir: Path, cohort: str) -> dict:
    uid = spec["uid"]
    source_rgb, source_alpha, targets, masks, item, source_path = data
    baseline_grid = np.asarray(Image.open(baseline_path).convert("RGB"))
    baseline_tiles = grid_tiles(baseline_grid)
    if len(baseline_tiles) != 6 or any(tile.shape[:2] != (256, 256) for tile in baseline_tiles):
        raise ValueError(f"unexpected saved GFL grid layout for {uid}: {baseline_grid.shape}")
    if "target_view_ids" in spec and len(spec["target_view_ids"]) == 6:
        target_ids = [int(x) for x in spec["target_view_ids"]]
    elif "target_order" in spec and len(spec["target_order"]) == 6:
        target_ids = [int(x) for x in spec["target_order"]]
    else:
        target_ids = [int(x) for x in json.loads(spec["target_view_ids"])]
    expected_source = int(spec.get("source_view", spec.get("source_view_id", target_ids[0])))
    if target_ids[0] != expected_source:
        raise RuntimeError(f"source reference is not tile 0 for {uid}: {target_ids}")

    repaired_tiles, estimate = source_conditioned_chroma_anchor(
        source_rgb, source_alpha, baseline_tiles, masks,
        max_abs_delta=6.0, erosion_px=3, min_pixels=64,
    )
    case_dir = out_dir / "case_images" / uid
    case_dir.mkdir(parents=True, exist_ok=True)
    source_condition_path = case_dir / "source_condition.png"
    gt_grid_path = case_dir / "gt_sixview.png"
    Image.fromarray(np.rint(np.clip(source_rgb, 0, 1) * 255).astype(np.uint8)).save(source_condition_path)
    Image.fromarray(stitch(targets)).save(gt_grid_path)
    image_path = out_dir / "predictions" / uid / "gfl_chroma_anchor.png"
    if image_path.exists():
        raise FileExistsError(f"refusing to overwrite candidate output: {image_path}")
    image_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_grid = stitch(repaired_tiles)
    Image.fromarray(candidate_grid).save(image_path, format="PNG", optimize=False)

    lpips_model = _get_lpips()
    # One paired batch for all six views; both versions use the same target and mask.
    ordered_pred = baseline_tiles + repaired_tiles
    ordered_target = targets + targets
    ordered_mask = masks + masks
    lpips_out = lpips_values(lpips_model, ordered_pred, ordered_target, ordered_mask)
    lpips_gfl, lpips_candidate = lpips_out[:6], lpips_out[6:]

    view_rows = []
    for view_idx in range(6):
        gfl = tile_metrics(baseline_tiles[view_idx], targets[view_idx], baseline_tiles[view_idx],
                           masks[view_idx], lpips_gfl[view_idx])
        candidate = tile_metrics(repaired_tiles[view_idx], targets[view_idx], baseline_tiles[view_idx],
                                 masks[view_idx], lpips_candidate[view_idx])
        row = {
            "uid": uid,
            "cohort": cohort,
            "source_cohort": spec.get("cohort", ""),
            "object_idx": spec.get("object_idx", ""),
            "object_seed": spec.get("object_seed", ""),
            "gt_fg_lap_var": spec.get("gt_fg_lap_var", ""),
            "gt_texture_quartile": spec.get("gt_texture_quartile", ""),
            "view_idx": view_idx,
            "target_view_id": target_ids[view_idx],
            "is_source_view": view_idx == 0,
            "checkpoint_sha256": json.loads(B_LOCK.read_text())["checkpoint"]["sha256"],
            "baseline_runner_sha256": spec.get("baseline_runner_sha256", ""),
            "baseline_generation_manifest_sha256": spec.get("baseline_generation_manifest_sha256", ""),
            "source_png": str(source_path.resolve()),
            "source_png_sha256": sha_file(source_path),
            "source_condition_png": str(source_condition_path.resolve()),
            "source_condition_png_sha256": sha_file(source_condition_path),
            "source_condition_rgb_sha256": hash_array(source_rgb),
            "source_condition_tensor_sha256": tensor_sha(item["cond_imgs"]),
            "source_alpha_sha256": hash_array(source_alpha),
            "target_tensor_sha256": tensor_sha(item["target_imgs"]),
            "normal_tensor_sha256": tensor_sha(item["depth_imgs"]),
            "depth_tensor_sha256": tensor_sha(item["real_depth_imgs"]),
            "global_embedding_tensor_sha256": tensor_sha(item["global_embeds"]),
            "frozen_input_cond_sha256": spec.get("input_cond_sha256", ""),
            "frozen_input_target_sha256": spec.get("input_target_sha256", ""),
            "frozen_input_normal_sha256": spec.get("input_normal_sha256", ""),
            "frozen_input_depth_sha256": spec.get("input_depth_sha256", ""),
            "frozen_input_global_embedding_sha256": spec.get("input_global_embeds_sha256", ""),
            "baseline_png": str(baseline_path.resolve()),
            "baseline_png_sha256": sha_file(baseline_path),
            "candidate_png": str(image_path.resolve()),
            "candidate_png_sha256": sha_file(image_path),
            "target_rgb_tile_sha256": hash_array(targets[view_idx]),
            "target_silhouette_mask_sha256": hash_array(masks[view_idx]),
            "gt_sixview_png": str(gt_grid_path.resolve()),
            "gt_sixview_png_sha256": sha_file(gt_grid_path),
            "repair_method_lock_sha256": sha_file(C1_LOCK),
            "repair_code_sha256": sha_file(HERE / "color_repair.py"),
            "repair_runner_sha256": sha_file(Path(__file__).resolve()),
            "source_median_a_star": estimate.source_median_ab[0],
            "source_median_b_star": estimate.source_median_ab[1],
            "gfl_reference_median_a_star": estimate.generated_reference_median_ab[0],
            "gfl_reference_median_b_star": estimate.generated_reference_median_ab[1],
            "raw_delta_a_star": estimate.raw_delta_ab[0],
            "raw_delta_b_star": estimate.raw_delta_ab[1],
            "applied_delta_a_star": estimate.applied_delta_ab[0],
            "applied_delta_b_star": estimate.applied_delta_ab[1],
            "source_trusted_pixels": estimate.source_pixels,
            "reference_trusted_pixels": estimate.reference_pixels,
            "mask_coverage": float((np.asarray(masks[view_idx]) >= 0.5).mean()),
        }
        for key, val in gfl.items():
            row[f"{key}_gfl"] = val
        for key, val in candidate.items():
            row[f"{key}_candidate"] = val
        row["delta_fg_lpips"] = candidate["candidate_fg_lpips"] - gfl["candidate_fg_lpips"]
        row["delta_foreground_lstar_ssim_to_gt"] = (
            candidate["candidate_foreground_lstar_ssim_to_gt"] - gfl["gfl_foreground_lstar_ssim_to_gt"]
        )
        row["delta_lstar_ssim_vs_gfl"] = candidate["candidate_lstar_ssim_vs_gfl"]
        row["delta_candidate_endpoint_pixel_fraction"] = (
            candidate["candidate_endpoint_pixel_fraction"] - gfl["gfl_endpoint_pixel_fraction"]
        )
        row["delta_gt_laplacian_error"] = candidate["delta_gt_laplacian_error"]
        view_rows.append(row)
    return {
        "uid": uid,
        "view_rows": view_rows,
        "candidate_path": str(image_path.resolve()),
        "candidate_sha256": sha_file(image_path),
        "source_path": str(source_path.resolve()),
        "source_sha256": sha_file(source_path),
        "source_condition_path": str(source_condition_path.resolve()),
        "source_condition_sha256": sha_file(source_condition_path),
        "gt_grid_path": str(gt_grid_path.resolve()),
        "gt_grid_sha256": sha_file(gt_grid_path),
        "baseline_path": str(baseline_path.resolve()),
        "baseline_sha256": sha_file(baseline_path),
        "estimate": estimate,
    }


_LPIPS = None


def _get_lpips():
    global _LPIPS
    if _LPIPS is None:
        try:
            import lpips
            _LPIPS = lpips.LPIPS(net="alex").to("cpu").eval()
        except Exception as exc:
            raise RuntimeError(f"AlexNet LPIPS could not be loaded on CPU: {exc!r}") from exc
    return _LPIPS


def _finish(out_dir: Path, paired: list[dict], c1_lock: dict) -> None:
    all_rows = [row for item in paired for row in item["view_rows"]]
    write_rows(out_dir / "C_REPAIR_PAIRED_RESULTS.csv", all_rows)
    (out_dir / "candidate_png_sha256.json").write_text(json.dumps({
        "method_lock_sha256": sha_file(C1_LOCK),
        "implementation_sha256": c1_lock["implementation"]["sha256"],
        "runner_sha256": sha_file(Path(__file__).resolve()),
        "execution_device": "CPU only; no diffusion generation",
        "images": [{k: item[k] for k in ("uid", "source_path", "source_sha256", "source_condition_path",
                                          "source_condition_sha256", "gt_grid_path", "gt_grid_sha256",
                                          "baseline_path", "baseline_sha256", "candidate_path", "candidate_sha256")}
                   for item in paired],
    }, indent=2) + "\n")
    print(json.dumps({"status": "complete", "cohort": out_dir.name,
                      "objects": len(paired), "view_rows": len(all_rows),
                      "results": str((out_dir / "C_REPAIR_PAIRED_RESULTS.csv").resolve())}, indent=2))


if __name__ == "__main__":
    main()
