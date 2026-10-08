#!/usr/bin/env python3
"""Audit Fresh C appearance image, tensor, embedding, and run-input identity."""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image
from skimage.color import rgb2lab


ROOT = Path("/4T/CXY/MV-Painter")
HERE = Path(__file__).resolve().parent
MANIFEST_PATH = Path("/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/FRESH_C_INPUT_EMBEDDINGS_MANIFEST.json")
COHORT_PATH = Path("/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/FRESH_C_COHORT_MANIFEST.json")
UID_LIST = ROOT / "1006/data/fresh_c/fresh_c_objects.txt"
RUN_GFL = ROOT / "1006/data/fresh_c/runs/c3_confirmation"
RUN_LLH = ROOT / "1006/data/fresh_c/runs/revision_era_addendum"
PIPELINE_ROOT = ROOT / "checkpoints/hf_repo"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha256(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def condition_source_lab(path: Path) -> dict[str, float]:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    rgb = rgba[:, :, :3].astype(np.float32) / 255.0
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    composite = rgb * alpha[:, :, None] + (1.0 - alpha[:, :, None])
    lab = rgb2lab(composite)
    foreground = alpha > (127 / 255.0)
    if foreground.any():
        pixels = lab[foreground]
    else:
        pixels = lab.reshape(-1, 3)
    return {
        "source_foreground_fraction_alpha_gt_127": float(foreground.mean()),
        "source_mean_L_star": float(pixels[:, 0].mean()),
        "source_mean_a_star": float(pixels[:, 1].mean()),
        "source_mean_b_star": float(pixels[:, 2].mean()),
        "source_std_a_star": float(pixels[:, 1].std()),
        "source_std_b_star": float(pixels[:, 2].std()),
    }


def load_rows(run_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    result = {}
    for path in sorted(run_dir.glob("rows_shard*.json")):
        for row in load_json(path):
            result[(row["object_uid"], row["condition"])] = row
    return result


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    cohort = load_json(COHORT_PATH)
    if manifest.get("status") != "PASS" or manifest.get("cohort_n") != 300:
        raise ValueError("Fresh C embedding manifest is not the expected PASS/n=300 artifact")
    objects = {obj["uid"]: obj for obj in cohort["objects"]}
    embedding_records = {obj["uid"]: obj for obj in manifest["objects"]}
    uids = [line.strip() for line in UID_LIST.read_text().splitlines() if line.strip()]
    if len(uids) != 300 or set(uids) != set(objects) or set(uids) != set(embedding_records):
        raise ValueError("Fresh C UID source sets differ")

    # Verify the frozen preprocessing source and vision assets against the manifest.
    source_root_map = {
        "dataset": "MVPainter/src/data/mvpainter_dataset.py",
        "pipeline": "MVPainter/mvpainter/mvpainter_pipeline.py",
        "model": "MVPainter/mvpainter/model_unet_geotex.py",
        "model_loader": "geotex/eval_exploration.py",
        "config_factory": "MVPainter/src/utils/train_util.py",
        "embedding_builder": "1006/scripts/precompute_fresh_c_global_embeds.py",
    }
    source_checks = {}
    for key, relative in source_root_map.items():
        actual = sha256_file(ROOT / relative)
        expected = manifest["embedding_source_hashes"][key]
        source_checks[key] = {"path": str(ROOT / relative), "expected_sha256": expected, "actual_sha256": actual, "pass": actual == expected}
        if actual != expected:
            raise ValueError(f"Fresh C input source hash mismatch: {relative}")
    vision_checks = []
    for component, files in manifest["vision_pipeline_file_hashes"].items():
        for relative, expected in files.items():
            path = PIPELINE_ROOT / relative
            actual = sha256_file(path)
            vision_checks.append({"component": component, "path": str(path), "expected_sha256": expected, "actual_sha256": actual, "pass": actual == expected})
            if actual != expected:
                raise ValueError(f"Fresh C vision asset hash mismatch: {relative}")

    sys.path[:0] = [str(ROOT), str(ROOT / "geotex"), str(ROOT / "MVPainter")]
    from src.data.mvpainter_dataset import MVPainterData  # imported after frozen source checks

    dataset = MVPainterData(
        root_dir_list=[str(ROOT / "1006/data/fresh_c/renders")],
        object_list_file=str(UID_LIST),
        target_view_mode="unique6",
    )
    if len(dataset) != len(uids) or [Path(p).name for p in dataset.paths] != uids:
        raise ValueError("Fresh C dataset UID order differs from its frozen object list")
    gfl_rows = load_rows(RUN_GFL)
    llh_rows = load_rows(RUN_LLH)
    if len([k for k in gfl_rows if k[1] == "native_gfl"]) != 300 or len([k for k in llh_rows if k[1] == "layer_llh"]) != 300:
        raise ValueError("Fresh C runner rows are incomplete for GFL/LLH input audit")
    run_manifest_gfl = load_json(RUN_GFL / "run_manifest_shard0.json")
    run_manifest_llh = load_json(RUN_LLH / "run_manifest_shard0.json")
    if run_manifest_gfl["checkpoint_sha256"] != manifest["checkpoint_sha256"] or run_manifest_llh["checkpoint_sha256"] != manifest["checkpoint_sha256"]:
        raise ValueError("Fresh C embeddings and generated outputs do not share the frozen checkpoint")

    rows = []
    for index, uid in enumerate(uids):
        record = embedding_records[uid]
        render_dir = Path(objects[uid]["render_dir"])
        source_view = record["selected_condition_view"]
        source_path = render_dir / "image" / f"{source_view}.png"
        source_sha_actual = sha256_file(source_path)
        source_sha_expected = record["condition_source"]["image_file_sha256"][source_view]
        if source_sha_actual != source_sha_expected:
            raise ValueError(f"Fresh C/{uid}: condition source image hash mismatch")

        embed_path = Path(record["embedding_file"])
        embed_file_sha_actual = sha256_file(embed_path)
        embedding = np.load(embed_path, allow_pickle=False)
        embed_tensor_sha_actual = hashlib.sha256(np.ascontiguousarray(embedding).tobytes()).hexdigest()
        if embed_file_sha_actual != record["embedding_file_sha256"] or embed_tensor_sha_actual != record["embedding_tensor_sha256"]:
            raise ValueError(f"Fresh C/{uid}: global embedding file/tensor hash mismatch")

        seed = int(record["seed"])
        if record["index"] != index or seed != 42 + index:
            raise ValueError(f"Fresh C/{uid}: embedding seed/index mismatch")
        seed_all(seed)
        batch = dataset[index]
        condition = batch["cond_imgs"]
        cond_tensor_hash = tensor_sha256(condition)
        if cond_tensor_hash != record["condition_tensor_sha256"]:
            raise ValueError(f"Fresh C/{uid}: rebuilt condition tensor hash mismatch")

        gfl = gfl_rows[(uid, "native_gfl")]
        llh = llh_rows[(uid, "layer_llh")]
        gfl_input = gfl["input_hashes"]
        llh_input = llh["input_hashes"]
        if gfl_input != llh_input:
            raise ValueError(f"Fresh C/{uid}: GFL/LLH input tensor hashes differ")
        if gfl_input.get("cond") != record["condition_tensor_sha256"] or gfl_input.get("global_embeds") != record["embedding_tensor_sha256"]:
            raise ValueError(f"Fresh C/{uid}: run input hashes do not bind to audited condition/embedding")
        if int(gfl["seed_base"]) != 42 or int(llh["seed_base"]) != 42:
            raise ValueError(f"Fresh C/{uid}: unexpected seed base")

        channel_means = condition.float().mean(dim=(1, 2)).tolist()
        channel_stds = condition.float().std(dim=(1, 2), unbiased=False).tolist()
        row = {
            "cohort": "FreshC",
            "uid": uid,
            "object_index": index,
            "object_seed": seed,
            "selected_condition_view": source_view,
            "condition_source_png": str(source_path),
            "condition_source_png_sha256_expected": source_sha_expected,
            "condition_source_png_sha256_actual": source_sha_actual,
            "condition_source_hash_pass": True,
            "condition_tensor_sha256_manifest": record["condition_tensor_sha256"],
            "condition_tensor_sha256_rebuilt": cond_tensor_hash,
            "condition_tensor_hash_pass": True,
            "condition_tensor_shape": json.dumps(list(condition.shape)),
            "condition_tensor_dtype": str(condition.dtype),
            "condition_tensor_min": float(condition.min()),
            "condition_tensor_max": float(condition.max()),
            "condition_tensor_rgb_mean": json.dumps(channel_means),
            "condition_tensor_rgb_std": json.dumps(channel_stds),
            "condition_tensor_range_interpretation": "RGB float32 in [0,1] after RGBA white composite and deterministic dataset transforms",
            "global_embedding_file": str(embed_path),
            "global_embedding_file_sha256_expected": record["embedding_file_sha256"],
            "global_embedding_file_sha256_actual": embed_file_sha_actual,
            "global_embedding_tensor_sha256_expected": record["embedding_tensor_sha256"],
            "global_embedding_tensor_sha256_actual": embed_tensor_sha_actual,
            "global_embedding_shape": json.dumps(list(embedding.shape)),
            "global_embedding_dtype": str(embedding.dtype),
            "global_embedding_file_and_tensor_hash_pass": True,
            "gfl_logged_condition_tensor_sha256": gfl_input["cond"],
            "gfl_logged_embedding_tensor_sha256": gfl_input["global_embeds"],
            "llh_logged_condition_tensor_sha256": llh_input["cond"],
            "llh_logged_embedding_tensor_sha256": llh_input["global_embeds"],
            "gfl_llh_input_tensor_hashes_equal": True,
            "checkpoint_sha256": manifest["checkpoint_sha256"],
            "global_encoder_pipeline_asset_manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
            "gt_render_dir": str(render_dir),
            **condition_source_lab(source_path),
        }
        rows.append(row)

    out = HERE / "C_APPEARANCE_CONDITION_OBJECT_AUDIT.csv"
    from recompute_paired_rgb_metrics import write_csv
    write_csv(out, rows)
    report = {
        "status": "PASS",
        "n": len(rows),
        "condition_view_counts": {view: sum(r["selected_condition_view"] == view for r in rows) for view in ("000", "014")},
        "condition_tensor_rebuilt_matches_manifest": sum(bool(r["condition_tensor_hash_pass"]) for r in rows),
        "global_embedding_asset_hashes_pass": sum(bool(r["global_embedding_file_and_tensor_hash_pass"]) for r in rows),
        "runner_input_hashes_match_manifest": sum(bool(r["gfl_llh_input_tensor_hashes_equal"]) for r in rows),
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "embedding_manifest_path": str(MANIFEST_PATH),
        "embedding_manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
        "dataset_and_builder_source_checks": source_checks,
        "vision_pipeline_asset_checks_count": len(vision_checks),
        "vision_pipeline_asset_checks_all_pass": all(r["pass"] for r in vision_checks),
        "run_code_sha256": run_manifest_gfl.get("runner_script_sha256"),
        "run_config_sha256": run_manifest_gfl.get("config_sha256"),
        "condition_processing": "Dataset selects 000/014 by frozen alpha-zero rule, white-composites RGBA, applies deterministic dataset transforms under seed 42+index, then the runner resizes to model.img_size=256 with bicubic antialiasing before the VAE feature extractor. Global embedding is from the same condition tensor via the two frozen vision encoders and vision processor.",
        "output_csv": str(out),
        "vision_pipeline_asset_checks": vision_checks,
    }
    (HERE / "C_APPEARANCE_CONDITION_AUDIT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "vision_pipeline_asset_checks"}, indent=2))


if __name__ == "__main__":
    main()
