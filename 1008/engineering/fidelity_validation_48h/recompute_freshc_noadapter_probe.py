#!/usr/bin/env python3
"""Recompute a saved-RGB Fresh C No Adapter versus GFL paired probe."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from recompute_paired_rgb_metrics import (
    load_csv,
    load_json,
    reconstruct_target,
    rgb_panel_to_metrics,
    sha256_file,
    write_csv,
)


ROOT = Path("/4T/CXY/MV-Painter/1006/data/fresh_c")
RUN = ROOT / "runs/c3_confirmation"
COHORT_MANIFEST = Path("/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/FRESH_C_COHORT_MANIFEST.json")
OUTPUT = Path(__file__).resolve().parent / "C_FRESHC_NOADAPTER_GFL_PAIRED_RGB.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()
    cohort = load_json(COHORT_MANIFEST)
    objects = {obj["uid"]: obj for obj in cohort["objects"]}
    expected_hashes = {
        (row["condition"], row["uid"]): row["sha256"]
        for row in load_csv(RUN / "OUTPUT_FILE_SHA256.csv")
        if row.get("kind") == "prediction" and row["condition"] in {"no_adapter", "native_gfl"}
    }
    input_rows: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(RUN.glob("rows_shard*.json")):
        for row in load_json(path):
            if row["condition"] in {"no_adapter", "native_gfl"}:
                input_rows[(row["object_uid"], row["condition"])] = row
    metric_rows = {
        (row["object_uid"], row["condition"]): row
        for row in load_csv(RUN / "per_object_metrics.csv")
        if row["condition"] in {"no_adapter", "native_gfl"}
    }
    run_manifest = load_json(RUN / "run_manifest_shard0.json")
    output_manifest_sha256 = sha256_file(RUN / "OUTPUT_FILE_SHA256.csv")

    rows = []
    for uid, obj in sorted(objects.items(), key=lambda item: int(item[1]["object_index"])):
        pair = {condition: input_rows[(uid, condition)] for condition in ("no_adapter", "native_gfl")}
        no_adapter_hashes = pair["no_adapter"]["input_hashes"]
        gfl_hashes = pair["native_gfl"]["input_hashes"]
        if no_adapter_hashes != gfl_hashes:
            raise ValueError(f"FreshC/{uid}: No Adapter and GFL tensors differ: {no_adapter_hashes} != {gfl_hashes}")
        if int(pair["no_adapter"]["object_idx"]) != int(obj["object_index"]) or int(pair["native_gfl"]["object_idx"]) != int(obj["object_index"]):
            raise ValueError(f"FreshC/{uid}: object index mismatch")
        prediction_paths = {
            "no_adapter": RUN / "predictions/no_adapter" / f"{uid}.png",
            "native_gfl": RUN / "predictions/native_gfl" / f"{uid}.png",
        }
        target, mask, target_ids, reverse, source_digest = reconstruct_target(Path(obj["render_dir"]))
        object_record = {"uid": uid, "object_idx": obj["object_index"], "object_seed": pair["native_gfl"]["seed_base"] + int(obj["object_index"])}
        measured = {}
        for condition, pred_path in prediction_paths.items():
            actual_hash = sha256_file(pred_path)
            if expected_hashes.get((condition, uid)) != actual_hash:
                raise ValueError(f"FreshC/{uid}/{condition}: prediction SHA mismatch")
            measured[condition] = rgb_panel_to_metrics(pred_path, target, mask)
            key = "no_adapter" if condition == "no_adapter" else "gfl"
            object_record[f"{key}_prediction_png"] = str(pred_path)
            object_record[f"{key}_prediction_sha256"] = actual_hash
            object_record[f"{key}_fg_psnr_recorded"] = metric_rows[(uid, condition)].get("fg_psnr", "")
            object_record[f"{key}_fg_lpips_recorded"] = metric_rows[(uid, condition)].get("fg_lpips", "")
            object_record[f"{key}_fg_ssim_recorded"] = metric_rows[(uid, condition)].get("fg_ssim", "")
        for key, value in {
            "target_view_ids": json.dumps(target_ids),
            "reverse_view_rotation": reverse,
            "checkpoint_sha256": run_manifest.get("checkpoint_sha256", ""),
            "runner_sha256": run_manifest.get("runner_script_sha256", ""),
            "config_sha256": run_manifest.get("config_sha256", ""),
            "target_tensor_sha256_logged": no_adapter_hashes.get("target", ""),
            "condition_tensor_sha256_logged": no_adapter_hashes.get("cond", ""),
            "global_embedding_tensor_sha256_logged": no_adapter_hashes.get("global_embeds", ""),
            "initial_latent_sha256_logged": no_adapter_hashes.get("init_latent", ""),
            "all_model_input_hashes_equal": True,
            "gt_render_dir": obj["render_dir"],
            "gt_selected_source_files_digest_sha256": source_digest,
            "run_output_hash_manifest_source": str(RUN / "OUTPUT_FILE_SHA256.csv"),
        }.items():
            object_record[key] = value
        for metric in measured["native_gfl"]:
            no_v = measured["no_adapter"][metric]
            gfl_v = measured["native_gfl"][metric]
            object_record[f"no_adapter_{metric}"] = no_v
            object_record[f"gfl_{metric}"] = gfl_v
            object_record[f"delta_gfl_minus_no_adapter_{metric}"] = gfl_v - no_v
        rows.append(object_record)

    if len(rows) != 300:
        raise ValueError(f"Expected 300 paired Fresh C objects, got {len(rows)}")
    write_csv(args.output, rows)
    print(json.dumps({
        "n": len(rows),
        "input_tensor_pairs_equal": sum(bool(row["all_model_input_hashes_equal"]) for row in rows),
        "checkpoint_sha256": run_manifest.get("checkpoint_sha256"),
        "runner_sha256": run_manifest.get("runner_script_sha256"),
        "config_sha256": run_manifest.get("config_sha256"),
        "output_sha256_manifest_sha256": output_manifest_sha256,
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
