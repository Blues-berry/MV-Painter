#!/usr/bin/env python
"""Materialize full RGB comparison grids for the frozen color-failure set."""
from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("/4T/CXY/MV-Painter")
ARTIFACT = ROOT / "1008/engineering/color_failure"
FREEZE = ARTIFACT / "SAMPLE_FREEZE.json"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
METHODS = ["no_adapter", "native_gfl", "native_gfh", "native_gc3", "gen_linear", "layer_llh"]
DISPLAY_NAMES = {
    "no_adapter": "No Adapter",
    "native_gfl": "GFL",
    "native_gfh": "GFH",
    "native_gc3": "C3",
    "gen_linear": "Generic Linear",
    "layer_llh": "LLH",
}

sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
sys.path.insert(0, str(ROOT))
from data_utils import collate_batch, prepare_batch  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def build_dataset(sample: dict):
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(Path(sample["object_list"]).resolve())
    validation.params.root_dir_list = [str(Path(sample["data_root"]).resolve())]
    return instantiate_from_config(validation)


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    out_root = ARTIFACT / "raw_rgb"
    masks_root = ARTIFACT / "masks"
    out_root.mkdir(parents=True, exist_ok=True)
    masks_root.mkdir(parents=True, exist_ok=True)

    legacy_rows = json.loads((ARTIFACT / "runs/fig4_fig6_six_condition/rows_shard0.json").read_text())
    legacy_by_uid = {row["object_uid"]: row for row in legacy_rows}
    asset_rows = []
    datasets = {}

    for sample in freeze["samples"]:
        sample_id = sample["sample_id"]
        uid = sample["uid"]
        source = sample["source"]
        if source not in datasets:
            datasets[source] = build_dataset(sample)
        dataset = datasets[source]
        seed = int(sample["object_seed"])
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        batch = collate_batch(dataset, int(sample["object_idx"]), device)
        _, target, _, _, _, mask = prepare_batch(batch, 256, device)

        expected_target = None
        # Both frozen comparison identities hash the six raw dataset targets;
        # the rendered reference grid is separately built by prepare_batch.
        actual_target = tensor_sha(batch["target_imgs"])
        if sample.get("input_hashes"):
            expected_target = sample["input_hashes"].get("input_target_sha256")
        elif uid in legacy_by_uid:
            expected_target = legacy_by_uid[uid]["input_hashes"]["target"]
        else:
            expected_target = None
        if expected_target and actual_target != expected_target:
            raise RuntimeError(
                f"target tensor hash mismatch for {sample_id}/{uid}: "
                f"{actual_target} != frozen {expected_target}"
            )

        sample_dir = out_root / sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)
        reference_path = sample_dir / "reference.png"
        save_image(target, reference_path)
        mask_path = masks_root / f"{sample_id}.png"
        save_image(mask, mask_path)
        asset_rows.append({
            "sample_id": sample_id, "uid": uid, "kind": "reference",
            "method": "reference", "source_path": "reconstructed_from_frozen_dataset",
            "source_sha256": actual_target, "output_path": str(reference_path),
            "output_sha256": sha256(reference_path),
            "identity_target_tensor_sha256": actual_target,
            "prepared_reference_grid_tensor_sha256": tensor_sha(target),
        })

        for method in METHODS:
            if source == "existing_formal_fresh_c_gallery":
                src = ARTIFACT / "runs/fresh_c_observer/predictions" / method / f"{uid}.png"
                expected_source_sha = None
                source_action = "fresh_current_rerun_to_pair_with_residual_log; original_gallery_png_retained_unmodified"
            else:
                src = (ARTIFACT / "runs/fig4_fig6_six_condition/predictions" /
                       method / f"{uid}.png")
                expected_source_sha = None
                source_action = "frozen_historical_six_condition_run; observer_output_byte_identical"
            if not src.is_file():
                raise FileNotFoundError(src)
            src_sha = sha256(src)
            if expected_source_sha and src_sha != expected_source_sha:
                raise RuntimeError(f"frozen gallery hash mismatch: {src}")
            dst = sample_dir / f"{method}.png"
            shutil.copy2(src, dst)
            if sha256(dst) != src_sha:
                raise RuntimeError(f"copy hash mismatch: {src} -> {dst}")
            asset_rows.append({
                "sample_id": sample_id, "uid": uid, "kind": "prediction",
                "method": DISPLAY_NAMES[method], "source_path": str(src),
                "source_sha256": src_sha, "output_path": str(dst),
                "output_sha256": sha256(dst),
                "identity_target_tensor_sha256": actual_target,
                "prepared_reference_grid_tensor_sha256": tensor_sha(target),
                "source_action": source_action,
            })

    manifest = ARTIFACT / "logs/RAW_RGB_ASSET_SHA256.csv"
    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=asset_rows[0].keys())
        writer.writeheader()
        writer.writerows(asset_rows)
    (ARTIFACT / "logs/RAW_RGB_ASSET_SUMMARY.json").write_text(json.dumps({
        "sample_count": len(freeze["samples"]),
        "methods": DISPLAY_NAMES,
        "grid_layout": "3 rows x 2 columns, six unique RGB target views, each 256x256",
        "prediction_action": "historical outputs from locked run; Fresh-C outputs from paired current rerun",
        "reference_action": "reconstructed with frozen validation dataset and prepare_batch",
        "target_tensor_hashes_verified": sum(bool(s.get("input_hashes")) or s["uid"] in legacy_by_uid for s in freeze["samples"]),
        "asset_count": len(asset_rows),
        "assets_csv": str(manifest),
    }, indent=2) + "\n")
    print(f"materialized {len(freeze['samples'])} samples, {len(asset_rows)} RGB grids; device={device}")


if __name__ == "__main__":
    main()
