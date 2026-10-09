#!/usr/bin/env python3
"""Input-only probe for whether selected Fresh B caches encode the alternate 000/014 view."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import importlib.metadata

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
LIST = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/fresh_confirm_b/fresh_confirm_b.txt")
DATA_ROOT = Path("/4T/CXY/MV-Painter/data/fresh_confirm_v3_renders")
PROVENANCE = HERE / "runs/phase_a/FRESHB_INPUT_EMBEDDING_PROVENANCE.csv"
LOCK = HERE / "protocol/FRESHB_INPUT_AUDIT_AMENDMENT_03.json"
OUT = HERE / "runs/phase_a"
sys.path[:0] = [str(ROOT), str(ROOT / "geotex"), str(ROOT / "MVPainter"), str(HERE)]

import geotex.eval_exploration as ee
from run_color_intervention import encode_global_embedding, sha_file, tensor_sha
from src.data.mvpainter_dataset import MVPainterData


def tensor_bytes_sha(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def compare(cache: np.ndarray, candidate: np.ndarray) -> tuple[float, float, float]:
    left = cache.astype(np.float32, copy=False).reshape(-1)
    right = candidate.astype(np.float32, copy=False).reshape(-1)
    delta = right - left
    cosine = float(np.dot(left, right) / max(np.linalg.norm(left) * np.linalg.norm(right), 1e-12))
    return float(np.max(np.abs(delta))), float(np.mean(np.abs(delta))), cosine


def main() -> None:
    started_utc = datetime.now(timezone.utc).isoformat()
    lock = json.loads(LOCK.read_text())
    uids = [line.strip() for line in LIST.read_text().splitlines() if line.strip()]
    if sha_file(LIST) != "f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28":
        raise RuntimeError("Fresh B frozen UID list SHA changed")
    with PROVENANCE.open(newline="") as handle:
        provenance_rows = {row["uid"]: row for row in csv.DictReader(handle)}
    selected = lock["uids"]
    if len(selected) != 8 or not set(selected) <= set(uids) or not set(selected) <= set(provenance_rows):
        raise RuntimeError("alternate-view audit UID list does not bind to the frozen cohort and source audit")
    if sha_file(CHECKPOINT) != "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0":
        raise RuntimeError("checkpoint hash mismatch")
    if sha_file(CONFIG) != "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b":
        raise RuntimeError("config hash mismatch")

    dataset = MVPainterData(root_dir_list=[str(DATA_ROOT)], object_list_file=str(LIST), target_view_mode="unique6")
    indices = {uid: index for index, uid in enumerate(uids)}
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), torch.device("cpu"))
    model.pipeline.vision_encoder.eval()
    model.pipeline.vision_encoder_2.eval()

    rows = []
    for uid in selected:
        index = indices[uid]
        if Path(dataset.paths[index]).name != uid:
            raise RuntimeError(f"dataset/list order mismatch for {uid}")
        source_audit = provenance_rows[uid]
        selected_view = int(source_audit["source_view_id"])
        alternate_view = 14 if selected_view == 0 else 0
        seed = 42 + index
        random.seed(seed)
        random_ratio = random.uniform(dataset.random_ratio_range, 1)
        object_dir = Path(dataset.paths[index])
        alternate_path = object_dir / "image" / f"{alternate_view:03d}.png"
        raw_rgb, _ = dataset.load_im(str(alternate_path), [1.0, 1.0, 1.0])
        random.seed(seed)
        random_ratio = random.uniform(dataset.random_ratio_range, 1)
        condition_rgb, condition_alpha = dataset.load_im_cond(
            str(alternate_path), [1.0, 1.0, 1.0], random_ratio
        )
        cache_path = object_dir / "embeddings" / "global_embeds.npy"
        cache = np.load(cache_path, allow_pickle=False)
        raw_embedding = encode_global_embedding(model, raw_rgb.unsqueeze(0)).numpy()
        condition_embedding = encode_global_embedding(model, condition_rgb.unsqueeze(0)).numpy()
        if cache.shape != raw_embedding.shape or cache.shape != condition_embedding.shape:
            raise RuntimeError(f"embedding shape mismatch for {uid}")
        raw_max, raw_mean, raw_cosine = compare(cache, raw_embedding)
        condition_max, condition_mean, condition_cosine = compare(cache, condition_embedding)
        rows.append({
            "uid": uid,
            "object_index": index,
            "object_seed": seed,
            "selected_view": selected_view,
            "alternate_view": alternate_view,
            "alternate_source_png_sha256": sha_file(alternate_path),
            "alternate_raw_tensor_sha256": tensor_sha(raw_rgb),
            "alternate_condition_tensor_sha256": tensor_sha(condition_rgb),
            "alternate_condition_alpha_sha256": tensor_sha(condition_alpha),
            "cache_sha256": sha_file(cache_path),
            "cache_vs_selected_condition_max_abs_delta": source_audit["cache_recompute_max_abs_delta"],
            "cache_vs_selected_raw_max_abs_delta": source_audit["cache_raw_source_max_abs_delta"],
            "cache_vs_alternate_raw_max_abs_delta": raw_max,
            "cache_vs_alternate_raw_mean_abs_delta": raw_mean,
            "cache_vs_alternate_raw_cosine": raw_cosine,
            "cache_vs_alternate_condition_max_abs_delta": condition_max,
            "cache_vs_alternate_condition_mean_abs_delta": condition_mean,
            "cache_vs_alternate_condition_cosine": condition_cosine,
        })

    out_csv = OUT / "FRESHB_CACHE_ALTERNATE_VIEW_AUDIT.csv"
    with out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    selected_max = np.asarray([float(r["cache_vs_selected_condition_max_abs_delta"]) for r in rows])
    alt_raw_max = np.asarray([r["cache_vs_alternate_raw_max_abs_delta"] for r in rows])
    alt_cond_max = np.asarray([r["cache_vs_alternate_condition_max_abs_delta"] for r in rows])
    summary = {
        "status": "complete",
        "started_utc": started_utc,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "pid": __import__("os").getpid(),
        "model_device": "cpu",
        "torch": torch.__version__,
        "torch_threads": torch.get_num_threads(),
        "torch_interop_threads": torch.get_num_interop_threads(),
        "transformers": importlib.metadata.version("transformers"),
        "diffusers": importlib.metadata.version("diffusers"),
        "uid_list_sha256": sha_file(LIST),
        "checkpoint_sha256": sha_file(CHECKPOINT),
        "config_sha256": sha_file(CONFIG),
        "runner_sha256": sha_file(Path(__file__)),
        "previous_provenance_csv_sha256": sha_file(PROVENANCE),
        "lock_sha256": sha_file(LOCK),
        "n": len(rows),
        "selected_view_cache_max_abs_delta_median": float(np.median(selected_max)),
        "alternate_raw_cache_max_abs_delta_median": float(np.median(alt_raw_max)),
        "alternate_condition_cache_max_abs_delta_median": float(np.median(alt_cond_max)),
        "alternate_raw_exact_match_count_within_0p03": int(np.sum(alt_raw_max <= 0.03)),
        "alternate_condition_exact_match_count_within_0p03": int(np.sum(alt_cond_max <= 0.03)),
        "interpretation_scope": "source-view/cache input identity only; no prediction, GT quality, or repair outcomes read",
        "csv_sha256": sha_file(out_csv),
    }
    out_json = OUT / "FRESHB_CACHE_ALTERNATE_VIEW_AUDIT.json"
    out_json.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
