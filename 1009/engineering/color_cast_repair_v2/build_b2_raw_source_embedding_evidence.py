#!/usr/bin/env python3
"""Verify and summarize the locked B2 raw-source embedding intervention."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from omegaconf import OmegaConf
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(BASE / "MVPainter"))

from src.utils.train_util import instantiate_from_config

from geotex.data_utils import prepare_batch
from run_raw_source_embedding_intervention import grid_targets, grid_tiles, tile_mask_grid

HERE = Path(__file__).resolve().parent
LOCK_PATH = HERE / "protocol/B2_RAW_SOURCE_EMBEDDING_LOCK.json"
PHASE_B_LOCK_PATH = HERE / "protocol/B_PROTOCOL_LOCK.json"
AMENDMENT_01 = HERE / "protocol/B2_PROTOCOL_AMENDMENT_01.json"
AMENDMENT_02 = HERE / "protocol/B2_PROTOCOL_AMENDMENT_02.json"
RUN_DIR = HERE / "runs/phase_b2_raw_source_embedding_attempt_04"
RAW_RESULTS = RUN_DIR / "B2_RAW_SOURCE_EMBEDDING_RESULTS.csv"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
DATASET_IMPL = BASE / "MVPainter/src/data/mvpainter_dataset.py"
PREPARE_BATCH_IMPL = ROOT / "geotex/data_utils.py"

PAIRED_OUT = HERE / "B2_RAW_SOURCE_EMBEDDING_PAIRED_RESULTS.csv"
OBJECT_OUT = HERE / "B2_RAW_SOURCE_EMBEDDING_OBJECT_RESULTS.csv"
SUMMARY_OUT = HERE / "B2_RAW_SOURCE_EMBEDDING_SUMMARY.csv"
CASEBOOK_OUT = HERE / "B2_RAW_SOURCE_EMBEDDING_CASEBOOK.pdf"
INPUT_AUDIT_OUT = HERE / "B2_METRIC_INPUT_RECONSTRUCTION.json"
TMP_DIR = RUN_DIR / "metric_input_reconstruction"

SHARED_FIELDS = (
    "condition_tensor_sha256",
    "source_alpha_sha256",
    "geometry_feature_sha256",
    "initial_latent_sha256",
    "vae_processor_pixels_sha256",
    "posterior_mean_sha256",
    "posterior_std_sha256",
    "posterior_sample_sha256",
    "posterior_noise_sha256",
    "posterior_rng_before_sha256",
    "posterior_rng_after_sha256",
)
METRICS = (
    "fg_ciede2000",
    "fg_psnr",
    "fg_lpips",
    "lstar_ssim_to_gt",
    "gt_laplacian_error",
    "lstar_ssim_vs_cached",
)
BOOTSTRAP_SEED = 20261009
BOOTSTRAP_DRAWS = 10000


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: str | Path) -> str:
    return sha_bytes(Path(path).read_bytes())


def tensor_sha(tensor: torch.Tensor) -> str:
    value = tensor.detach().cpu().contiguous().numpy()
    return sha_bytes(value.tobytes())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write an empty CSV: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_audit_dataset(root: Path, uids: list[str], tag: str):
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.root_dir_list = [str(root)]
    list_path = TMP_DIR / "object_lists" / f"{tag}.txt"
    list_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.write_text("\n".join(uids) + "\n")
    validation.params.object_list_file = str(list_path.resolve())
    dataset = instantiate_from_config(validation)
    if getattr(dataset, "target_view_mode", None) != "unique6":
        raise RuntimeError(f"{tag}: dataset did not instantiate with unique6")
    return dataset


def reconstruct_targets(lock: dict, device: torch.device) -> tuple[dict, list[dict]]:
    phase_lock = json.loads(PHASE_B_LOCK_PATH.read_text())
    phase_by_uid = {item["uid"]: item for item in phase_lock["objects"]}
    ordered_specs = [phase_by_uid[uid] for uid in lock["development_objects"]]
    groups: dict[str, list[dict]] = {}
    for spec in ordered_specs:
        tag = "legacy_fig4" if "rendered_full" in spec["root"] else "freshc_dev"
        groups.setdefault(tag, []).append(spec)

    reconstructed: dict[str, dict] = {}
    source_records: list[dict] = []
    config = OmegaConf.load(CONFIG)
    image_size = int(config.model.params.img_size)
    for tag, specs in groups.items():
        root = Path(specs[0]["root"])
        dataset = load_audit_dataset(root, [spec["uid"] for spec in specs], tag)
        for local_idx, spec in enumerate(specs):
            seed_all(int(spec["object_seed"]))
            item = dataset[local_idx]
            batch = {
                key: value.unsqueeze(0).to(device) if torch.is_tensor(value) else value
                for key, value in item.items()
            }
            _, target_grid, _, _, _, mask_grid = prepare_batch(batch, image_size, device)
            targets = grid_targets(target_grid)
            masks = tile_mask_grid(mask_grid)
            target_order = [int(value) for value in spec["target_order"]]
            if len(targets) != 6 or len(target_order) != 6 or len(masks) != 6:
                raise RuntimeError(f"{spec['uid']}: target reconstruction is not unique6")

            tile_records = []
            for idx, (view_id, target, mask) in enumerate(zip(target_order, targets, masks)):
                image_path = root / spec["uid"] / "image" / f"{view_id:03d}.png"
                if not image_path.is_file():
                    raise FileNotFoundError(image_path)
                tile_records.append({
                    "view_idx": idx,
                    "target_view_id": view_id,
                    "is_source_view": idx == 0,
                    "gt_rgb_path": str(image_path.resolve()),
                    "gt_rgb_file_sha256": sha_file(image_path),
                    "gt_tile_uint8_sha256": sha_bytes(np.ascontiguousarray(target).tobytes()),
                    "mask_tensor_tile_sha256": sha_bytes(np.ascontiguousarray(mask).tobytes()),
                    "mask_binary_sha256": sha_bytes(np.ascontiguousarray(mask >= 0.5).tobytes()),
                    "foreground_pixels": int(np.sum(mask >= 0.5)),
                    "gt_tile_rgb": target,
                    "mask_tile": mask,
                })
                source_records.append({
                    "uid": spec["uid"],
                    "view_idx": idx,
                    "target_view_id": view_id,
                    "gt_rgb_path": str(image_path.resolve()),
                    "gt_rgb_file_sha256": sha_file(image_path),
                    "gt_tile_uint8_sha256": sha_bytes(np.ascontiguousarray(target).tobytes()),
                })
            reconstructed[spec["uid"]] = {
                "spec": spec,
                "target_grid_tensor_sha256": tensor_sha(target_grid),
                "mask_grid_tensor_sha256": tensor_sha(mask_grid),
                "tiles": tile_records,
            }
    return reconstructed, source_records


def verify_run(lock: dict, rows: list[dict], reconstructed: dict) -> tuple[dict, dict]:
    if len(rows) != 48:
        raise RuntimeError(f"expected 48 raw rows, got {len(rows)}")
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_pair[(row["uid"], row["condition"])].append(row)
        prediction = Path(row["prediction_png"])
        if not prediction.is_file() or sha_file(prediction) != row["prediction_png_sha256"]:
            raise RuntimeError(f"prediction identity mismatch: {prediction}")
        source = Path(row["source_png"])
        if not source.is_file() or sha_file(source) != row["source_png_sha256"]:
            raise RuntimeError(f"source RGB identity mismatch: {source}")

    expected_uids = set(lock["development_objects"])
    if {row["uid"] for row in rows} != expected_uids:
        raise RuntimeError("B2 output objects differ from the locked object list")
    paired = {}
    object_rows = {}
    for uid in lock["development_objects"]:
        base = sorted(by_pair[(uid, "cached_baseline")], key=lambda row: int(row["view_idx"]))
        treatment = sorted(by_pair[(uid, "selected_raw_source_embedding")], key=lambda row: int(row["view_idx"]))
        if len(base) != 6 or len(treatment) != 6:
            raise RuntimeError(f"{uid}: expected six rows per arm")
        spec = reconstructed[uid]["spec"]
        tile_inputs = reconstructed[uid]["tiles"]
        view_rows = []
        for b, t, gt in zip(base, treatment, tile_inputs):
            if b["target_view_id"] != t["target_view_id"] or int(b["target_view_id"]) != gt["target_view_id"]:
                raise RuntimeError(f"{uid}: paired target-view mapping differs")
            if b["is_source_view"] != t["is_source_view"] or (b["is_source_view"].lower() == "true") != gt["is_source_view"]:
                raise RuntimeError(f"{uid}: source-view identity differs")
            for field in SHARED_FIELDS:
                if b[field] != t[field]:
                    raise RuntimeError(f"{uid}/{b['target_view_id']}: paired factor mismatch in {field}")
            if b["paired_metrics"] != t["paired_metrics"]:
                raise RuntimeError(f"{uid}/{b['target_view_id']}: paired metric record differs between arms")
            metrics = json.loads(b["paired_metrics"])
            target_delta = metrics["delta"]
            row = {
                "uid": uid,
                "cohort": b["cohort"],
                "object_seed": b["object_seed"],
                "source_view_id": int(spec["source_view"]),
                "view_idx": int(b["view_idx"]),
                "target_view_id": int(b["target_view_id"]),
                "is_source_view": gt["is_source_view"],
                "gt_rgb_path": gt["gt_rgb_path"],
                "gt_rgb_file_sha256": gt["gt_rgb_file_sha256"],
                "gt_tile_uint8_sha256_reconstructed": gt["gt_tile_uint8_sha256"],
                "gt_target_grid_tensor_sha256_reconstructed": reconstructed[uid]["target_grid_tensor_sha256"],
                "mask_tensor_tile_sha256_reconstructed": gt["mask_tensor_tile_sha256"],
                "mask_binary_sha256_reconstructed": gt["mask_binary_sha256"],
                "foreground_pixels_reconstructed": gt["foreground_pixels"],
                "source_rgb_path": b["source_png"],
                "source_rgb_sha256": b["source_png_sha256"],
                "condition_tensor_sha256": b["condition_tensor_sha256"],
                "cached_embedding_sha256": b["cached_embedding_sha256"],
                "selected_raw_embedding_sha256": b["selected_raw_embedding_sha256"],
                "geometry_feature_sha256": b["geometry_feature_sha256"],
                "initial_latent_sha256": b["initial_latent_sha256"],
                "posterior_sample_sha256": b["posterior_sample_sha256"],
                "checkpoint_sha256": b["checkpoint_sha256"],
                "config_sha256": b["config_sha256"],
                "protocol_sha256": b["protocol_sha256"],
                "runner_sha256": b["runner_sha256"],
                "cached_prediction_png": b["prediction_png"],
                "cached_prediction_png_sha256": b["prediction_png_sha256"],
                "treatment_prediction_png": t["prediction_png"],
                "treatment_prediction_png_sha256": t["prediction_png_sha256"],
                "treatment_background_changed_fraction": metrics["selected_raw_source_embedding"]["background_changed_fraction"],
                "delta_fg_ciede2000": target_delta["fg_ciede2000"],
                "delta_fg_psnr_db": target_delta["fg_psnr"],
                "delta_fg_lpips": target_delta["fg_lpips"],
                "delta_foreground_lstar_ssim_to_gt": target_delta["lstar_ssim_to_gt"],
                "delta_gt_laplacian_error": target_delta["gt_laplacian_error"],
                "lstar_ssim_treatment_vs_cached": target_delta["lstar_ssim_vs_cached"],
                "gt_rgb": gt["gt_tile_rgb"],
                "cached_rgb": grid_tiles(np.asarray(Image.open(b["prediction_png"]).convert("RGB")))[int(b["view_idx"])],
                "treatment_rgb": grid_tiles(np.asarray(Image.open(t["prediction_png"]).convert("RGB")))[int(t["view_idx"])],
            }
            view_rows.append(row)
        paired[uid] = view_rows

        unseen = [row for row in view_rows if not row["is_source_view"]]
        source_row = next(row for row in view_rows if row["is_source_view"])
        aggregate = {
            "uid": uid,
            "cohort": base[0]["cohort"],
            "object_seed": base[0]["object_seed"],
            "source_view_id": spec["source_view"],
            "unseen_view_count": len(unseen),
            "source_delta_fg_ciede2000": source_row["delta_fg_ciede2000"],
            "source_delta_fg_psnr_db": source_row["delta_fg_psnr_db"],
            "source_delta_fg_lpips": source_row["delta_fg_lpips"],
            "source_delta_lstar_ssim_to_gt": source_row["delta_foreground_lstar_ssim_to_gt"],
            "source_delta_gt_laplacian_error": source_row["delta_gt_laplacian_error"],
            "mean_unseen_delta_fg_ciede2000": statistics.mean(float(row["delta_fg_ciede2000"]) for row in unseen),
            "mean_unseen_delta_fg_psnr_db": statistics.mean(float(row["delta_fg_psnr_db"]) for row in unseen),
            "mean_unseen_delta_fg_lpips": statistics.mean(float(row["delta_fg_lpips"]) for row in unseen),
            "mean_unseen_delta_lstar_ssim_to_gt": statistics.mean(float(row["delta_foreground_lstar_ssim_to_gt"]) for row in unseen),
            "mean_unseen_delta_gt_laplacian_error": statistics.mean(float(row["delta_gt_laplacian_error"]) for row in unseen),
            "mean_unseen_lstar_ssim_treatment_vs_cached": statistics.mean(float(row["lstar_ssim_treatment_vs_cached"]) for row in unseen),
            "mean_unseen_treatment_background_changed_fraction": statistics.mean(float(row["treatment_background_changed_fraction"]) for row in unseen),
            "unseen_view_ciede2000_deltas": json.dumps([float(row["delta_fg_ciede2000"]) for row in unseen]),
            "unseen_view_psnr_deltas_db": json.dumps([float(row["delta_fg_psnr_db"]) for row in unseen]),
            "unseen_view_lpips_deltas": json.dumps([float(row["delta_fg_lpips"]) for row in unseen]),
            "paired_output_identity_verified": True,
        }
        object_rows[uid] = aggregate
    return paired, object_rows


def summarize(object_rows: dict[str, dict]) -> list[dict]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    fields = {
        "unseen_mean_fg_ciede2000": ("mean_unseen_delta_fg_ciede2000", "lower_is_better"),
        "unseen_mean_fg_psnr_db": ("mean_unseen_delta_fg_psnr_db", "higher_is_better"),
        "unseen_mean_fg_lpips": ("mean_unseen_delta_fg_lpips", "lower_is_better"),
        "unseen_mean_foreground_lstar_ssim_to_gt": ("mean_unseen_delta_lstar_ssim_to_gt", "higher_is_better"),
        "unseen_mean_gt_laplacian_error": ("mean_unseen_delta_gt_laplacian_error", "lower_is_better"),
        "unseen_mean_lstar_ssim_vs_cached": ("mean_unseen_lstar_ssim_treatment_vs_cached", "descriptive_similarity"),
    }
    rows = []
    ordered_uids = list(object_rows)
    for metric, (field, direction) in fields.items():
        values = np.asarray([float(object_rows[uid][field]) for uid in ordered_uids], dtype=np.float64)
        draws = rng.integers(0, len(values), size=(BOOTSTRAP_DRAWS, len(values)))
        means = values[draws].mean(axis=1)
        if direction == "lower_is_better":
            wins = int(np.sum(values < 0))
        elif direction == "higher_is_better":
            wins = int(np.sum(values > 0))
        else:
            wins = "NA"
        rows.append({
            "metric": metric,
            "direction": direction,
            "n_objects": len(values),
            "mean_object_paired_delta": float(values.mean()),
            "median_object_paired_delta": float(np.median(values)),
            "bootstrap_95ci_lower": float(np.quantile(means, 0.025)),
            "bootstrap_95ci_upper": float(np.quantile(means, 0.975)),
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "objects_favoring_treatment": wins,
            "object_values_json": json.dumps(values.tolist()),
        })
    return rows


def render_casebook(path: Path, paired: dict[str, list[dict]], object_rows: dict[str, dict]) -> None:
    with PdfPages(path) as pdf:
        for uid, rows in paired.items():
            aggregate = object_rows[uid]
            fig, axes = plt.subplots(6, 3, figsize=(13, 17))
            fig.suptitle(
                f"B2 selected raw-source embedding intervention\n{uid} | {aggregate['cohort']}",
                fontsize=13, y=0.995,
            )
            headers = ("GT metric target", "Cached embedding", "Selected raw-source embedding")
            for col, title in enumerate(headers):
                axes[0, col].set_title(title, fontsize=10, pad=8)
            for idx, row in enumerate(rows):
                images = (row["gt_rgb"], row["cached_rgb"], row["treatment_rgb"])
                for col, image in enumerate(images):
                    axes[idx, col].imshow(image)
                    axes[idx, col].set_xticks([])
                    axes[idx, col].set_yticks([])
                    for edge in axes[idx, col].spines.values():
                        edge.set_visible(False)
                marker = "SOURCE" if row["is_source_view"] else "UNSEEN"
                axes[idx, 0].set_ylabel(
                    f"view {row['target_view_id']}\n{marker}", fontsize=9, rotation=0,
                    labelpad=32, va="center",
                )
            footer = (
                "Object mean over five unseen views: "
                f"ΔFG-CIEDE2000={float(aggregate['mean_unseen_delta_fg_ciede2000']):+.3f}; "
                f"ΔFG-PSNR={float(aggregate['mean_unseen_delta_fg_psnr_db']):+.3f} dB; "
                f"ΔFG-LPIPS={float(aggregate['mean_unseen_delta_fg_lpips']):+.4f}; "
                f"Δforeground L* SSIM-to-GT={float(aggregate['mean_unseen_delta_lstar_ssim_to_gt']):+.4f}\n"
                f"Selected source RGB SHA-256: {next(row for row in rows if row['is_source_view'])['source_rgb_sha256']}\n"
                "Panels use the locked unique6 order; no GT RGB was used to build the treatment."
            )
            fig.text(0.5, 0.012, footer, ha="center", va="bottom", fontsize=8)
            fig.tight_layout(rect=(0.04, 0.035, 0.99, 0.97), h_pad=0.12, w_pad=0.08)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def main() -> None:
    outputs = (PAIRED_OUT, OBJECT_OUT, SUMMARY_OUT, CASEBOOK_OUT, INPUT_AUDIT_OUT)
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite evidence outputs: " + ", ".join(existing))
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("use exactly the locked physical GPU 1 via CUDA_VISIBLE_DEVICES=1 for exact target resize reconstruction")
    if __import__("os").environ.get("CUDA_VISIBLE_DEVICES") != "1":
        raise RuntimeError("refusing to reconstruct metric inputs on a different GPU binding")

    lock = json.loads(LOCK_PATH.read_text())
    amend_01 = json.loads(AMENDMENT_01.read_text())
    amend_02 = json.loads(AMENDMENT_02.read_text())
    if sha_file(LOCK_PATH) != amend_02["base_lock_sha256"]:
        raise RuntimeError("B2 base protocol hash differs from Amendment 02")
    if sha_file(AMENDMENT_01) != amend_02["prior_amendment_sha256"]:
        raise RuntimeError("B2 amendment chain is broken")
    runner_path = HERE / "run_raw_source_embedding_intervention.py"
    if sha_file(runner_path) != amend_02["runner_sha256"]:
        raise RuntimeError("sampling runner no longer matches the pre-generation amendment")
    if amend_01["superseding_runner_sha256"] != amend_02["superseded_runner_sha256"]:
        raise RuntimeError("B2 runner supersession chain is inconsistent")
    if lock["model"]["new_runner_sha256"] != amend_01["superseded_runner_sha256"]:
        raise RuntimeError("B2 base runner identity is inconsistent with Amendment 01")

    rows = read_csv(RAW_RESULTS)
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
    reconstructed, source_records = reconstruct_targets(lock, device)
    paired, object_rows = verify_run(lock, rows, reconstructed)

    flat_rows = [{key: value for key, value in row.items() if key not in {"gt_rgb", "cached_rgb", "treatment_rgb", "mask_tile"}}
                 for uid in lock["development_objects"] for row in paired[uid]]
    ordered_objects = [object_rows[uid] for uid in lock["development_objects"]]
    summary_rows = summarize(object_rows)
    write_csv(PAIRED_OUT, flat_rows)
    write_csv(OBJECT_OUT, ordered_objects)
    write_csv(SUMMARY_OUT, summary_rows)
    render_casebook(CASEBOOK_OUT, paired, object_rows)

    identity_fields = {"condition_tensor_sha256", "source_alpha_sha256", "geometry_feature_sha256", *SHARED_FIELDS}
    reconstruction = {
        "purpose": "Supplement the B2 live manifest with source RGB identities and a same-runner, same-seed reconstruction of the metric targets and masks.",
        "caveat": "The sampling CSV did not record the target_grid or mask_grid tensor hashes during generation. These hashes are a faithful post-run reconstruction from the unchanged raw RGB files, locked unique6 order, dataset implementation and the same CUDA resize path; they cannot be compared with a missing in-process target tensor hash.",
        "created_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "protocol_sha256": sha_file(LOCK_PATH),
        "amendment_01_sha256": sha_file(AMENDMENT_01),
        "amendment_02_sha256": sha_file(AMENDMENT_02),
        "runner_sha256": sha_file(runner_path),
        "phase_b_protocol_sha256": sha_file(PHASE_B_LOCK_PATH),
        "metric_runner_sha256": sha_file(HERE / "run_chroma_anchor_evaluation.py"),
        "dataset_implementation_path": str(DATASET_IMPL),
        "dataset_implementation_sha256_at_reconstruction": sha_file(DATASET_IMPL),
        "prepare_batch_implementation_path": str(PREPARE_BATCH_IMPL),
        "prepare_batch_implementation_sha256_at_reconstruction": sha_file(PREPARE_BATCH_IMPL),
        "config_sha256": sha_file(CONFIG),
        "cuda_device": torch.cuda.get_device_name(0),
        "cuda_visible_devices": "1",
        "metric_target_resize_device": str(device),
        "target_view_mode": "unique6",
        "target_view_order_by_uid": {uid: reconstructed[uid]["spec"]["target_order"] for uid in lock["development_objects"]},
        "full_target_tensor_sha256_by_uid_reconstructed": {uid: reconstructed[uid]["target_grid_tensor_sha256"] for uid in lock["development_objects"]},
        "full_mask_tensor_sha256_by_uid_reconstructed": {uid: reconstructed[uid]["mask_grid_tensor_sha256"] for uid in lock["development_objects"]},
        "per_view_rgb_source_and_reconstruction": source_records,
        "paired_factor_identity_fields_verified": sorted(identity_fields),
        "paired_factor_identity_check": "PASS for condition tensor, source alpha, geometry features, initial latent, VAE pixels/posterior/noise/RNG; global-embedding-derived prompt hashes are treatment-dependent by design.",
        "raw_prediction_pngs_sha_verified": len(rows),
        "result_files": {
            "paired_results_sha256": sha_file(PAIRED_OUT),
            "object_results_sha256": sha_file(OBJECT_OUT),
            "summary_sha256": sha_file(SUMMARY_OUT),
            "casebook_sha256": sha_file(CASEBOOK_OUT),
        },
        "statistics": {
            "paired_unit": "object",
            "unseen_view_aggregation": "equally average the five locked non-source views within each object",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_type": "percentile cluster bootstrap over four object-level paired means",
        },
    }
    INPUT_AUDIT_OUT.write_text(json.dumps(reconstruction, indent=2) + "\n")
    print(json.dumps({
        "paired_view_rows": len(flat_rows),
        "objects": len(ordered_objects),
        "summary": summary_rows,
        "casebook": str(CASEBOOK_OUT),
        "metrics": str(PAIRED_OUT),
        "metric_input_reconstruction": str(INPUT_AUDIT_OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
