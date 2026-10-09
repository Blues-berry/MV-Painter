#!/usr/bin/env python3
"""Input-only Fresh B source/embedding audit; does not read prediction or GT metrics."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
LOCK = HERE / "protocol/FRESHB_INPUT_ONLY_AUDIT_LOCK.json"
AMENDMENT = HERE / "protocol/FRESHB_INPUT_AUDIT_AMENDMENT_01.json"
EXECUTION_AMENDMENT = HERE / "protocol/FRESHB_INPUT_AUDIT_AMENDMENT_02.json"
OUT = HERE / "runs/phase_a"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
sys.path.insert(0, str(HERE))

import geotex.eval_exploration as ee
from run_color_intervention import encode_global_embedding, sha_bytes, sha_file, tensor_sha, utc_now
from src.data.mvpainter_dataset import MVPainterData


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lock = json.loads(LOCK.read_text())
    uid_list = Path(lock["cohort_list"])
    if sha_file(uid_list) != lock["cohort_list_sha256"]:
        raise RuntimeError("Fresh B input list SHA does not match frozen lock")
    uids = [line.strip() for line in uid_list.read_text().splitlines() if line.strip()]
    if len(uids) != lock["expected_n"]:
        raise RuntimeError(f"Expected {lock['expected_n']} UIDs, found {len(uids)}")

    dataset = MVPainterData(
        root_dir_list=[lock["data_root"]],
        object_list_file=str(uid_list),
        target_view_mode="unique6",
    )
    device = torch.device("cpu")
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    model.pipeline.vision_encoder.eval()
    model.pipeline.vision_encoder_2.eval()
    started = utc_now()
    rows: list[dict] = []

    for index, uid in enumerate(uids):
        seed = 42 + index
        seed_all(seed)
        random_ratio = random.uniform(dataset.random_ratio_range, 1)
        object_dir = Path(dataset.paths[index])
        source_stats = {}
        for view in (0, 14):
            raw, alpha = dataset.load_im(str(object_dir / "image" / f"{view:03d}.png"), [1.0, 1.0, 1.0])
            source_stats[view] = int(torch.sum(alpha == 0).item())
        reverse = source_stats[0] > source_stats[14]
        source_view = 14 if reverse else 0
        condition, condition_alpha = dataset.load_im_cond(
            str(object_dir / "image" / f"{source_view:03d}.png"),
            [1.0, 1.0, 1.0], random_ratio,
        )
        raw_source, _ = dataset.load_im(
            str(object_dir / "image" / f"{source_view:03d}.png"),
            [1.0, 1.0, 1.0],
        )
        embedding_file = object_dir / "embeddings" / "global_embeds.npy"
        if not embedding_file.is_file():
            raise FileNotFoundError(f"missing embedding cache for Fresh B UID {uid}")
        cache = np.load(embedding_file, allow_pickle=False)
        recomputed = encode_global_embedding(model, condition.unsqueeze(0)).numpy()
        raw_recomputed = encode_global_embedding(model, raw_source.unsqueeze(0)).numpy()
        if cache.shape != recomputed.shape:
            raise RuntimeError(f"embedding shape mismatch for {uid}: {cache.shape} != {recomputed.shape}")
        if cache.shape != raw_recomputed.shape:
            raise RuntimeError(f"raw-source embedding shape mismatch for {uid}: {cache.shape} != {raw_recomputed.shape}")
        cache_cast = cache.astype(recomputed.dtype, copy=False)
        delta = recomputed - cache_cast
        raw_delta = raw_recomputed - cache_cast
        cache_norm = float(np.linalg.norm(cache_cast.reshape(-1)))
        delta_norm = float(np.linalg.norm(delta.reshape(-1)))
        cosine = float(np.dot(cache_cast.reshape(-1), recomputed.reshape(-1)) /
                       max(cache_norm * float(np.linalg.norm(recomputed.reshape(-1))), 1e-12))
        raw_cosine = float(np.dot(cache_cast.reshape(-1), raw_recomputed.reshape(-1)) /
                           max(cache_norm * float(np.linalg.norm(raw_recomputed.reshape(-1))), 1e-12))
        condition_path = object_dir / "image" / f"{source_view:03d}.png"
        rows.append({
            "uid": uid,
            "object_idx": index,
            "object_seed": seed,
            "source_view_id": source_view,
            "reverse": reverse,
            "condition_source_png": str(condition_path.resolve()),
            "condition_source_png_sha256": sha_file(condition_path),
            "condition_tensor_sha256": tensor_sha(condition),
            "condition_alpha_sha256": tensor_sha(condition_alpha),
            "condition_alpha_coverage": float((condition_alpha >= 0.5).float().mean()),
            "condition_random_resize_ratio": random_ratio,
            "global_embedding_cache": str(embedding_file.resolve()),
            "global_embedding_cache_sha256": sha_file(embedding_file),
            "global_embedding_cache_tensor_sha256": sha_bytes(np.ascontiguousarray(cache).tobytes()),
            "global_embedding_cache_dtype": str(cache.dtype),
            "global_embedding_recomputed_sha256": sha_bytes(np.ascontiguousarray(recomputed).tobytes()),
            "cache_recompute_max_abs_delta": float(np.max(np.abs(delta))),
            "cache_recompute_mean_abs_delta": float(np.mean(np.abs(delta))),
            "cache_recompute_cosine": cosine,
            "cache_recompute_within_0p03": bool(np.max(np.abs(delta)) <= 0.03),
            "raw_source_global_embedding_sha256": sha_bytes(np.ascontiguousarray(raw_recomputed).tobytes()),
            "cache_raw_source_max_abs_delta": float(np.max(np.abs(raw_delta))),
            "cache_raw_source_mean_abs_delta": float(np.mean(np.abs(raw_delta))),
            "cache_raw_source_cosine": raw_cosine,
            "cache_raw_source_within_0p03": bool(np.max(np.abs(raw_delta)) <= 0.03),
            "current_condition_raw_source_max_abs_delta": float(np.max(np.abs(recomputed - raw_recomputed))),
        })
        if (index + 1) % 10 == 0 or index + 1 == len(uids):
            with (OUT / "FRESHB_INPUT_EMBEDDING_PROVENANCE.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            print(f"input-only embedding audit {index + 1}/{len(uids)}", flush=True)

    deltas = np.asarray([r["cache_recompute_max_abs_delta"] for r in rows], dtype=float)
    raw_deltas = np.asarray([r["cache_raw_source_max_abs_delta"] for r in rows], dtype=float)
    summary = {
        "status": "complete",
        "started_utc": started,
        "finished_utc": utc_now(),
        "pid": __import__("os").getpid(),
        "source_list_sha256": sha_file(uid_list),
        "checkpoint_sha256": sha_file(CHECKPOINT),
        "config_sha256": sha_file(CONFIG),
        "runner_sha256": sha_file(Path(__file__)),
        "embedding_helper_sha256": sha_file(HERE / "run_color_intervention.py"),
        "audit_lock_sha256": sha_file(LOCK),
        "audit_amendment_sha256": sha_file(AMENDMENT),
        "execution_amendment_sha256": sha_file(EXECUTION_AMENDMENT),
        "model_device": str(device),
        "n": len(rows),
        "within_0p03_count": int(sum(r["cache_recompute_within_0p03"] for r in rows)),
        "max_abs_delta_median": float(np.median(deltas)),
        "max_abs_delta_p95": float(np.quantile(deltas, 0.95)),
        "max_abs_delta_max": float(np.max(deltas)),
        "raw_source_within_0p03_count": int(sum(r["cache_raw_source_within_0p03"] for r in rows)),
        "raw_source_max_abs_delta_median": float(np.median(raw_deltas)),
        "raw_source_max_abs_delta_p95": float(np.quantile(raw_deltas, 0.95)),
        "raw_source_max_abs_delta_max": float(np.max(raw_deltas)),
        "interpretation_scope": "input and embedding identity only; no generated PNGs, GT quality metrics, or repair outcomes read",
        "prior_current_condition_audit_json_sha256": sha_file(OUT / "FRESHB_INPUT_EMBEDDING_AUDIT.json"),
        "csv_sha256": sha_file(OUT / "FRESHB_INPUT_EMBEDDING_PROVENANCE.csv"),
    }
    (OUT / "FRESHB_INPUT_EMBEDDING_PROVENANCE.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()

