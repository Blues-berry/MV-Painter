"""Shared integrity checks for the pre-inference Fresh C embedding amendment."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
UIDS_PATH = DATA / "fresh_c_objects.txt"
COHORT_PATH = DATA / "FRESH_C_COHORT_MANIFEST.json"
AMENDMENT_PATH = ROOT / "1006/evidence/protocols/FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_V3_20261006.json"
MANIFEST_PATH = DATA / "FRESH_C_INPUT_EMBEDDINGS_MANIFEST.json"
PIPELINE_ROOT = ROOT / "checkpoints/hf_repo"
PARENT_AMENDMENT_PATH = ROOT / "1006/evidence/protocols/FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_V2_20261006.json"
PRIOR_MANIFEST_PATH = DATA / "FRESH_C_INPUT_EMBEDDINGS_MANIFEST_ATTEMPT1_20261006.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_verified_input_embeddings() -> tuple[dict[str, Any], str]:
    if not AMENDMENT_PATH.is_file() or not MANIFEST_PATH.is_file():
        raise RuntimeError("pre-inference Fresh C embedding amendment/manifest is missing")
    amendment = json.loads(AMENDMENT_PATH.read_text())
    manifest = json.loads(MANIFEST_PATH.read_text())
    if amendment.get("status") != "FROZEN_PRE_INFERENCE":
        raise RuntimeError("embedding preprocessing amendment is not frozen")
    if sha256(PARENT_AMENDMENT_PATH) != amendment.get("supersedes_amendment_json_sha256"):
        raise RuntimeError("gate amendment does not bind the preserved parent input amendment")
    if sha256(PRIOR_MANIFEST_PATH) != amendment.get("prior_manifest_attempt1_sha256"):
        raise RuntimeError("gate amendment does not bind the preserved first cache manifest")
    if manifest.get("supersedes_input_amendment_json_sha256") != sha256(PARENT_AMENDMENT_PATH):
        raise RuntimeError("current cache manifest does not identify its parent input amendment")
    if manifest.get("prior_manifest_attempt1_sha256") != sha256(PRIOR_MANIFEST_PATH):
        raise RuntimeError("current cache manifest does not identify the preserved prior manifest")
    if sha256(AMENDMENT_PATH.with_suffix(".md")) != amendment.get("amendment_markdown_sha256"):
        raise RuntimeError("embedding amendment markdown hash mismatch")
    for relative, expected_hash in amendment.get("orchestration_source_hashes", {}).items():
        source = ROOT / relative
        if not source.is_file() or sha256(source) != expected_hash:
            raise RuntimeError(f"embedding amendment orchestration hash mismatch: {relative}")
    if manifest.get("status") != "PASS" or manifest.get("method_outputs_exist") is not False:
        raise RuntimeError("embedding manifest does not certify a pre-inference PASS")
    if manifest.get("amendment_json_sha256") != sha256(AMENDMENT_PATH):
        raise RuntimeError("embedding manifest was built under a different amendment")
    if manifest.get("amendment_markdown_sha256") != sha256(AMENDMENT_PATH.with_suffix(".md")):
        raise RuntimeError("embedding manifest markdown identity mismatch")
    cohort = json.loads(COHORT_PATH.read_text())
    uids = [line.strip() for line in UIDS_PATH.read_text().splitlines() if line.strip()]
    uid_hash = sha256(UIDS_PATH)
    if len(set(uids)) != len(uids) or len(uids) != cohort.get("selected_count"):
        raise RuntimeError("frozen UID list count/uniqueness mismatch")
    if manifest.get("cohort_n") != len(uids) or manifest.get("cohort_uid_list_sha256") != uid_hash:
        raise RuntimeError("embedding manifest does not match the frozen UID list")
    if manifest.get("cohort_manifest_sha256") != sha256(COHORT_PATH):
        raise RuntimeError("embedding manifest does not match the frozen cohort manifest")
    if manifest.get("embedding_source_hashes") != amendment.get("embedding_source_hashes"):
        raise RuntimeError("embedding implementation sources differ from the amendment")
    if manifest.get("embedding_source_paths") != amendment.get("embedding_source_paths"):
        raise RuntimeError("embedding source path map differs from the amendment")
    if manifest.get("method_source_hashes") != amendment.get("method_source_hashes"):
        raise RuntimeError("method source registry differs from the amendment")
    if manifest.get("vision_pipeline_file_hashes") != amendment.get("vision_pipeline_file_hashes"):
        raise RuntimeError("vision pipeline files differ from the amendment")
    if manifest.get("runtime_versions") != amendment.get("runtime_versions"):
        raise RuntimeError("embedding runtime versions differ from the amendment")
    runtime_versions = {
        package: importlib.metadata.version(package)
        for package in ("torch", "torchvision", "transformers", "diffusers", "numpy")
    }
    if runtime_versions != amendment.get("runtime_versions"):
        raise RuntimeError("current runtime package versions differ from the amendment")
    for key, relative in amendment.get("embedding_source_paths", {}).items():
        expected_hash = amendment.get("embedding_source_hashes", {}).get(key)
        if not expected_hash or sha256(ROOT / relative) != expected_hash:
            raise RuntimeError(f"embedding preprocessing source changed: {relative}")
    current_pipeline_hashes = {}
    for component in ("vision_encoder", "vision_encoder_2", "vision_processor"):
        folder = PIPELINE_ROOT / component
        if not folder.is_dir():
            raise RuntimeError(f"vision pipeline component is missing: {component}")
        current_pipeline_hashes[component] = {
            str(path.relative_to(PIPELINE_ROOT)): sha256(path)
            for path in sorted(path for path in folder.rglob("*") if path.is_file())
        }
    if current_pipeline_hashes != amendment.get("vision_pipeline_file_hashes"):
        raise RuntimeError("on-disk vision pipeline files differ from the amendment")
    records = manifest.get("objects", [])
    if [record.get("uid") for record in records] != uids:
        raise RuntimeError("embedding manifest UID coverage/order mismatch")
    for index, record in enumerate(records):
        if record.get("index") != index or record.get("seed") != 42 + index:
            raise RuntimeError(f"embedding manifest index/seed mismatch at {record.get('uid')}")
        path = Path(record.get("embedding_file", ""))
        expected = DATA / "renders" / uids[index] / "embeddings/global_embeds.npy"
        if path.resolve() != expected.resolve() or not path.is_file():
            raise RuntimeError(f"embedding cache path mismatch at {uids[index]}")
        if sha256(path) != record.get("embedding_file_sha256"):
            raise RuntimeError(f"embedding cache file hash mismatch at {uids[index]}")
        array = np.load(path, allow_pickle=False)
        if array.shape != (1, 1, 2048) or array.dtype != np.float32 or not np.isfinite(array).all():
            raise RuntimeError(f"embedding cache shape/dtype/value mismatch at {uids[index]}")
    return manifest, sha256(MANIFEST_PATH)
