#!/usr/bin/env python3
"""Create deterministic per-object global image embeddings before Fresh C inference."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "1006/data/fresh_c"
RENDERS = DATA / "renders"
UIDS_PATH = DATA / "fresh_c_objects.txt"
COHORT_PATH = DATA / "FRESH_C_COHORT_MANIFEST.json"
COHORT_AUDIT_PATH = DATA / "FRESH_C_COHORT_AUDIT.json"
AMENDMENT_PATH = ROOT / "1006/evidence/protocols/FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_V3_20261006.json"
MANIFEST_PATH = DATA / "FRESH_C_INPUT_EMBEDDINGS_MANIFEST.json"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
PIPELINE_ROOT = ROOT / "checkpoints/hf_repo"
sys.path[:0] = [str(ROOT), str(ROOT / "geotex"), str(ROOT / "MVPainter")]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor_sha256(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def atomic_npy(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        np.save(handle, array, allow_pickle=False)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def cache_files() -> dict[str, Path]:
    return {p.parent.parent.name: p for p in RENDERS.glob("*/embeddings/global_embeds.npy")}


def refuse_if_method_outputs_exist() -> None:
    for name in ("c3_confirmation", "revision_era_addendum"):
        run = DATA / "runs" / name
        if not run.exists():
            continue
        patterns = (
            "rows_shard*.json", "run_manifest_shard*.json", "per_object_metrics.csv",
            "predictions/**/*.png", "residual_logs/**/*.json",
        )
        found = [str(path) for pattern in patterns for path in run.glob(pattern)]
        if found:
            raise RuntimeError(f"method output already exists in {run}; refusing pre-inference cache build: {found[:5]}")


def pipeline_file_hashes() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for component in ("vision_encoder", "vision_encoder_2", "vision_processor"):
        folder = PIPELINE_ROOT / component
        if not folder.is_dir():
            raise FileNotFoundError(folder)
        files = sorted(p for p in folder.rglob("*") if p.is_file())
        result[component] = {str(p.relative_to(PIPELINE_ROOT)): sha256(p) for p in files}
    return result


def selected_view_and_source_hashes(render_dir: Path) -> tuple[str, dict[str, str]]:
    import cv2

    alpha_zero_counts = {}
    source_hashes = {}
    for view in ("000", "014"):
        image_path = render_dir / "image" / f"{view}.png"
        decoded = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if decoded is None or decoded.ndim != 3 or decoded.shape[2] != 4:
            raise RuntimeError(f"expected RGBA render for source view {view}: {image_path}")
        alpha_zero_counts[view] = int(np.count_nonzero(decoded[:, :, 3] == 0))
        source_hashes[view] = sha256(image_path)
    selected = "014" if alpha_zero_counts["000"] > alpha_zero_counts["014"] else "000"
    return selected, {
        "alpha_zero_pixels": alpha_zero_counts,
        "image_file_sha256": source_hashes,
    }


def embed_from_condition_image(model: Any, cond_img: torch.Tensor) -> np.ndarray:
    from torchvision.transforms import v2

    if cond_img.ndim == 3:
        cond_img = cond_img.unsqueeze(0)
    if cond_img.ndim != 4 or cond_img.shape[1] != 3:
        raise RuntimeError(f"unexpected condition tensor shape: {tuple(cond_img.shape)}")
    pipeline = model.pipeline
    images = [v2.functional.to_pil_image(cond_img[i]) for i in range(cond_img.shape[0])]
    pixels = pipeline.vision_processor(images=images, return_tensors="pt").pixel_values
    pixels = pixels.to(device="cpu", dtype=next(pipeline.vision_encoder.parameters()).dtype)
    with torch.inference_mode():
        first = pipeline.vision_encoder(pixels, output_hidden_states=False).image_embeds.unsqueeze(-2)
        second = pipeline.vision_encoder_2(pixels, output_hidden_states=False).image_embeds.unsqueeze(-2)
        embedding = torch.cat([first, second], dim=-1)
    array = embedding.detach().cpu().float().numpy()
    if array.shape != (1, 1, 2048) or not np.isfinite(array).all():
        raise RuntimeError(f"unexpected global embedding shape/values: {array.shape}")
    return array


def main() -> None:
    if not CONFIG.is_file() or not CHECKPOINT.is_file():
        raise FileNotFoundError("Fresh C config or checkpoint is missing")
    if MANIFEST_PATH.exists():
        previous = json.loads(MANIFEST_PATH.read_text())
        if previous.get("status") == "PASS":
            verify_existing_manifest(previous)
            print(json.dumps({"status": "ALREADY_PASS", "manifest": str(MANIFEST_PATH)}, indent=2))
            return
        raise RuntimeError("an existing non-PASS embedding manifest requires manual audit; refusing overwrite")

    refuse_if_method_outputs_exist()
    cohort = json.loads(COHORT_PATH.read_text())
    cohort_audit = json.loads(COHORT_AUDIT_PATH.read_text())
    if cohort.get("status") not in {"FROZEN_FRESH_C_300", "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET"}:
        raise RuntimeError(f"cohort not frozen: {cohort.get('status')}")
    if cohort_audit.get("status") != cohort.get("status") or cohort_audit.get("method_outputs_exist") is not False:
        raise RuntimeError("cohort audit does not certify a pre-inference frozen cohort")
    uids = [line.strip() for line in UIDS_PATH.read_text().splitlines() if line.strip()]
    uid_hash = sha256(UIDS_PATH)
    if len(uids) != cohort.get("selected_count") or len(set(uids)) != len(uids):
        raise RuntimeError("frozen UID list count/uniqueness mismatch")
    if uid_hash != cohort.get("selected_uid_list_sha256"):
        raise RuntimeError("frozen UID-list hash differs from cohort manifest")

    amendment = json.loads(AMENDMENT_PATH.read_text())
    if amendment.get("status") != "FROZEN_PRE_INFERENCE":
        raise RuntimeError("input-embedding amendment is not frozen before inference")
    if sha256(Path(__file__)) != amendment.get("embedding_builder_sha256"):
        raise RuntimeError("embedding builder differs from the frozen amendment")
    for directory in (DATA / "runs/c3_confirmation", DATA / "runs/revision_era_addendum"):
        if directory.exists() and any(directory.glob("rows_shard*.json")):
            raise RuntimeError(f"method rows already exist: {directory}")

    from launch_fresh_c_confirm import EXPECTED as METHOD_EXPECTED, sha256 as launch_sha256
    from geotex import eval_exploration as ee

    source_path_relatives = {
        "dataset": "MVPainter/src/data/mvpainter_dataset.py",
        "pipeline": "MVPainter/mvpainter/mvpainter_pipeline.py",
        "model": "MVPainter/mvpainter/model_unet_geotex.py",
        "model_loader": "geotex/eval_exploration.py",
        "config_factory": "MVPainter/src/utils/train_util.py",
        "embedding_builder": "1006/scripts/precompute_fresh_c_global_embeds.py",
    }
    source_paths = {key: ROOT / relative for key, relative in source_path_relatives.items()}
    source_hashes = {key: sha256(path) for key, path in source_paths.items()}
    if source_hashes != amendment.get("embedding_source_hashes"):
        raise RuntimeError(f"embedding source hashes differ from amendment: {source_hashes}")
    if source_path_relatives != amendment.get("embedding_source_paths"):
        raise RuntimeError("embedding source path map differs from amendment")
    if launch_sha256(CONFIG) != METHOD_EXPECTED["config"] or launch_sha256(CHECKPOINT) != METHOD_EXPECTED["checkpoint"]:
        raise RuntimeError("Fresh C config/checkpoint hash mismatch")
    if METHOD_EXPECTED != amendment.get("method_source_hashes"):
        raise RuntimeError("method source registry differs from the frozen amendment")
    model_file_hashes = pipeline_file_hashes()
    if model_file_hashes != amendment.get("vision_pipeline_file_hashes"):
        raise RuntimeError("vision pipeline/processor files differ from the frozen amendment")
    runtime_versions = {
        package: importlib.metadata.version(package)
        for package in ("torch", "torchvision", "transformers", "diffusers", "numpy")
    }
    if runtime_versions != amendment.get("runtime_versions"):
        raise RuntimeError(f"runtime package versions differ from the amendment: {runtime_versions}")

    existing = cache_files()
    unexpected = sorted(set(existing) - set(uids))
    if unexpected:
        raise RuntimeError(f"embedding caches exist for UIDs outside the frozen cohort: {unexpected[:5]}")

    # Import the same dataset class through the same package path as the locked runner.
    sys.path.insert(0, str(ROOT / "MVPainter"))
    from src.data.mvpainter_dataset import MVPainterData

    dataset = MVPainterData(
        root_dir_list=[str(RENDERS.resolve())],
        object_list_file=str(UIDS_PATH.resolve()),
        target_view_mode="unique6",
    )
    if len(dataset) != len(uids):
        raise RuntimeError("dataset length does not match frozen UID list")
    for index, uid in enumerate(uids):
        if Path(dataset.paths[index]).name != uid:
            raise RuntimeError(f"dataset order differs from frozen UID list at {index}: {uid}")

    # The runner's loader uses CPU vision encoders for this same two-encoder operation.
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), torch.device("cpu"))
    model.pipeline.vision_encoder.eval()
    model.pipeline.vision_encoder_2.eval()

    object_records = []
    for index, uid in enumerate(uids):
        seed = 42 + index
        render_dir = Path(dataset.paths[index])
        selected_view, source_record = selected_view_and_source_hashes(render_dir)

        seed_all(seed)
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            batch = dataset[index]
        captured = stdout_capture.getvalue()
        if "wrong path:" in captured:
            raise RuntimeError(f"dataset fallback/error while reading frozen UID {uid}: {captured[-500:]}")
        if "cond_imgs" not in batch:
            raise RuntimeError(f"dataset omitted cond_imgs for {uid}")
        cond_hash = tensor_sha256(batch["cond_imgs"])

        seed_all(seed)
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            repeated = dataset[index]
        if "wrong path:" in stdout_capture.getvalue() or tensor_sha256(repeated["cond_imgs"]) != cond_hash:
            raise RuntimeError(f"seeded condition tensor did not reproduce for {uid}")

        embedding = embed_from_condition_image(model, batch["cond_imgs"])
        embedding_hash = hashlib.sha256(np.ascontiguousarray(embedding).tobytes()).hexdigest()
        cache_path = render_dir / "embeddings/global_embeds.npy"
        if cache_path.exists():
            old = np.load(cache_path, allow_pickle=False)
            old_hash = hashlib.sha256(np.ascontiguousarray(old).tobytes()).hexdigest()
            if old_hash != embedding_hash or old.dtype != np.float32 or old.shape != embedding.shape:
                raise RuntimeError(f"existing cache conflicts with deterministic output for {uid}")
        else:
            atomic_npy(cache_path, embedding)
        object_records.append({
            "index": index,
            "uid": uid,
            "seed": seed,
            "selected_condition_view": selected_view,
            "condition_source": source_record,
            "condition_tensor_sha256": cond_hash,
            "embedding_tensor_sha256": embedding_hash,
            "embedding_file": str(cache_path.resolve()),
            "embedding_file_sha256": sha256(cache_path),
            "embedding_shape": list(embedding.shape),
            "embedding_dtype": str(embedding.dtype),
        })
        if (index + 1) % 25 == 0 or index + 1 == len(uids):
            print(f"verified embeddings {index + 1}/{len(uids)}", flush=True)

    if len(object_records) != len(uids) or len(cache_files()) != len(uids):
        raise RuntimeError("not every frozen UID has exactly one verified embedding cache")
    refuse_if_method_outputs_exist()
    manifest = {
        "status": "PASS",
        "protocol": "fresh_c_deterministic_global_embedding_preprocessing_amendment_20261006",
        "created_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "method_outputs_exist": False,
        "cohort_n": len(uids),
        "cohort_manifest_sha256": sha256(COHORT_PATH),
        "cohort_audit_sha256": sha256(COHORT_AUDIT_PATH),
        "cohort_uid_list_sha256": uid_hash,
        "amendment_json_sha256": sha256(AMENDMENT_PATH),
        "amendment_markdown_sha256": sha256(AMENDMENT_PATH.with_suffix(".md")),
        "config_sha256": sha256(CONFIG),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "vision_pipeline_file_hashes": model_file_hashes,
        "embedding_source_hashes": source_hashes,
        "embedding_source_paths": source_path_relatives,
        "supersedes_input_amendment_json_sha256": amendment["supersedes_amendment_json_sha256"],
        "prior_manifest_attempt1_sha256": amendment["prior_manifest_attempt1_sha256"],
        "runtime_versions": runtime_versions,
        "method_source_hashes": METHOD_EXPECTED,
        "embedding_shape": [1, 1, 2048],
        "embedding_dtype": "float32",
        "objects": object_records,
    }
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    temporary.replace(MANIFEST_PATH)
    print(json.dumps({"status": "PASS", "cohort_n": len(uids),
                      "uid_sha256": uid_hash, "manifest": str(MANIFEST_PATH)}, indent=2))


def verify_existing_manifest(manifest: dict[str, Any]) -> None:
    uids = [line.strip() for line in UIDS_PATH.read_text().splitlines() if line.strip()]
    if manifest.get("cohort_uid_list_sha256") != sha256(UIDS_PATH) or manifest.get("cohort_n") != len(uids):
        raise RuntimeError("existing embedding manifest does not match frozen UID list")
    rows = manifest.get("objects", [])
    if [row.get("uid") for row in rows] != uids:
        raise RuntimeError("existing embedding manifest UID order mismatch")
    for row in rows:
        path = Path(row["embedding_file"])
        if not path.is_file() or sha256(path) != row.get("embedding_file_sha256"):
            raise RuntimeError(f"existing embedding cache hash mismatch: {row.get('uid')}")


if __name__ == "__main__":
    main()
