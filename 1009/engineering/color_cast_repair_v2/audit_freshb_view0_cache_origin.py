#!/usr/bin/env python3
"""Input-only test for cached embeddings on every Fresh B object selected from view 014."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
LIST = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/fresh_confirm_b/fresh_confirm_b.txt")
DATA_ROOT = Path("/4T/CXY/MV-Painter/data/fresh_confirm_v3_renders")
PROVENANCE = HERE / "runs/phase_a/FRESHB_INPUT_EMBEDDING_PROVENANCE.csv"
LOCK = HERE / "protocol/FRESHB_INPUT_AUDIT_AMENDMENT_04.json"
OUT = HERE / "runs/phase_a"
sys.path[:0] = [str(ROOT), str(ROOT / "geotex"), str(ROOT / "MVPainter"), str(HERE)]

import geotex.eval_exploration as ee
from run_color_intervention import encode_global_embedding, sha_file, tensor_sha
from src.data.mvpainter_dataset import MVPainterData


def compare(cache: np.ndarray, candidate: np.ndarray) -> tuple[float, float, float]:
    left = cache.astype(np.float32, copy=False).reshape(-1)
    right = candidate.astype(np.float32, copy=False).reshape(-1)
    delta = right - left
    cosine = float(np.dot(left, right) / max(np.linalg.norm(left) * np.linalg.norm(right), 1e-12))
    return float(np.max(np.abs(delta))), float(np.mean(np.abs(delta))), cosine


def main() -> None:
    started_utc = datetime.now(timezone.utc).isoformat()
    lock = json.loads(LOCK.read_text())
    if sha_file(LIST) != "f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28":
        raise RuntimeError("Fresh B frozen UID list SHA changed")
    if sha_file(CHECKPOINT) != "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0":
        raise RuntimeError("checkpoint hash mismatch")
    if sha_file(CONFIG) != "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b":
        raise RuntimeError("config hash mismatch")
    with PROVENANCE.open(newline="") as handle:
        input_rows = {row["uid"]: row for row in csv.DictReader(handle)}
    uids = [line.strip() for line in LIST.read_text().splitlines() if line.strip()]
    selected = [uid for uid in uids if input_rows[uid]["source_view_id"] == "14"]
    if len(selected) != int(lock["expected_n"]):
        raise RuntimeError(f"expected {lock['expected_n']} selected-014 objects, found {len(selected)}")

    torch.set_num_threads(4)
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
        object_dir = Path(dataset.paths[index])
        view0_path = object_dir / "image" / "000.png"
        view0_rgb, _ = dataset.load_im(str(view0_path), [1.0, 1.0, 1.0])
        cache_path = object_dir / "embeddings" / "global_embeds.npy"
        cache = np.load(cache_path, allow_pickle=False)
        embedding = encode_global_embedding(model, view0_rgb.unsqueeze(0)).numpy()
        if cache.shape != embedding.shape:
            raise RuntimeError(f"embedding shape mismatch for {uid}")
        alt_max, alt_mean, alt_cosine = compare(cache, embedding)
        prior = input_rows[uid]
        selected_raw_max = float(prior["cache_raw_source_max_abs_delta"])
        selected_raw_cosine = float(prior["cache_raw_source_cosine"])
        rows.append({
            "uid": uid,
            "object_index": index,
            "object_seed": 42 + index,
            "selected_source_view": 14,
            "alternate_source_view": 0,
            "view0_png_sha256": sha_file(view0_path),
            "view0_tensor_sha256": tensor_sha(view0_rgb),
            "cache_sha256": sha_file(cache_path),
            "cache_vs_selected_view14_raw_max_abs_delta": selected_raw_max,
            "cache_vs_selected_view14_raw_cosine": selected_raw_cosine,
            "cache_vs_view0_raw_max_abs_delta": alt_max,
            "cache_vs_view0_raw_mean_abs_delta": alt_mean,
            "cache_vs_view0_raw_cosine": alt_cosine,
            "view0_is_closer_by_max_abs": alt_max < selected_raw_max,
            "view0_has_higher_cosine": alt_cosine > selected_raw_cosine,
        })

    out_csv = OUT / "FRESHB_VIEW0_CACHE_ORIGIN_AUDIT.csv"
    with out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    selected_deltas = np.asarray([r["cache_vs_selected_view14_raw_max_abs_delta"] for r in rows])
    view0_deltas = np.asarray([r["cache_vs_view0_raw_max_abs_delta"] for r in rows])
    summary = {
        "status": "complete",
        "started_utc": started_utc,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "pid": __import__("os").getpid(),
        "model_device": "cpu",
        "torch": torch.__version__,
        "torch_threads": torch.get_num_threads(),
        "uid_list_sha256": sha_file(LIST),
        "checkpoint_sha256": sha_file(CHECKPOINT),
        "config_sha256": sha_file(CONFIG),
        "runner_sha256": sha_file(Path(__file__)),
        "input_provenance_csv_sha256": sha_file(PROVENANCE),
        "lock_sha256": sha_file(LOCK),
        "n": len(rows),
        "view0_closer_count": sum(bool(r["view0_is_closer_by_max_abs"]) for r in rows),
        "view0_higher_cosine_count": sum(bool(r["view0_has_higher_cosine"]) for r in rows),
        "selected_view14_max_abs_delta_median": float(np.median(selected_deltas)),
        "view0_max_abs_delta_median": float(np.median(view0_deltas)),
        "median_max_abs_improvement_for_view0": float(np.median(selected_deltas - view0_deltas)),
        "interpretation_scope": "input/cache source identity only; no prediction, GT quality, or repair outcomes read",
        "csv_sha256": sha_file(out_csv),
    }
    out_json = OUT / "FRESHB_VIEW0_CACHE_ORIGIN_AUDIT.json"
    out_json.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
