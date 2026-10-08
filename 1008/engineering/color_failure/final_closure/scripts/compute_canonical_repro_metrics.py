#!/usr/bin/env python3
"""Re-score archived/Py3.13/Py3.10 PNGs under one pinned evaluation runtime."""
from __future__ import annotations

import csv
import hashlib
import random
import sys
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
BASE = Path("/4T/CXY/MV-Painter")
ARTIFACT = ROOT.parent
FRESH = BASE / "1006/data/fresh_c"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
OBJECT_LIST = FRESH / "fresh_c_objects.txt"
DATA_ROOT = FRESH / "renders"
CHECKPOINT_SHA = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"

sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "geotex"))
sys.path.insert(0, str(PROJECT / "MVPainter"))
from data_utils import collate_batch, prepare_batch  # noqa: E402
from eval_exploration import compute_metrics, get_lpips_fn  # noqa: E402
from metrics import compute_edge_mask  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402

OBJECTS = [
    ("freshc_panel_01", 232, "c76ac44df995482185077da81939b306"),
    ("freshc_panel_03", 236, "ca887928bb664bcba121219f0af41293"),
    ("freshc_panel_20", 10, "06fa4974f8cd4d4ea792e98fa1521457"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_tensor(path: Path, device: torch.device) -> torch.Tensor:
    array = np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8).copy()
    if array.shape != (768, 512, 3):
        raise ValueError(f"invalid six-view RGB grid: {path}: {array.shape}")
    return torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0).to(device).float() / 255.0


def ciede(reference: np.ndarray, prediction: np.ndarray, mask: np.ndarray) -> dict:
    all_de, all_da, all_db = [], [], []
    for view in range(6):
        row, col = divmod(view, 2)
        ys, xs = slice(row * 256, (row + 1) * 256), slice(col * 256, (col + 1) * 256)
        fg = mask[ys, xs] > 127
        ref = reference[ys, xs].astype(np.float32) / 255.0
        pred = prediction[ys, xs].astype(np.float32) / 255.0
        lab_ref, lab_pred = rgb2lab(ref), rgb2lab(pred)
        delta = lab_pred - lab_ref
        all_de.append(float(deltaE_ciede2000(lab_ref, lab_pred)[fg].mean()))
        all_da.append(float(delta[..., 1][fg].mean()))
        all_db.append(float(delta[..., 2][fg].mean()))
    return {"mean_fg_ciede2000": float(np.mean(all_de)),
            "mean_delta_a_star": float(np.mean(all_da)),
            "mean_delta_b_star": float(np.mean(all_db))}


def main() -> None:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    lpips_fn = get_lpips_fn(device)
    if lpips_fn is None:
        raise RuntimeError("canonical evaluation requires LPIPS")
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    validation.params.root_dir_list = [str(DATA_ROOT.resolve())]
    dataset = instantiate_from_config(validation)
    ids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    run_images = {
        "historical_archive_py313": FRESH / "runs/c3_confirmation/predictions/native_gfl",
        "current_trace_py313": ROOT / "repro/python313_trace_repeat1/run/predictions/native_gfl",
        "current_trace_py310": ROOT / "repro/python310_trace/run/predictions/native_gfl",
    }
    rows = []
    for sample_id, object_idx, uid in OBJECTS:
        if ids[object_idx] != uid:
            raise RuntimeError(f"object list identity mismatch for {sample_id}")
        seed = 42 + object_idx
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        batch = collate_batch(dataset, object_idx, device)
        _, _, _, real_depth, _, mask = prepare_batch(batch, 256, device)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1).to(device)
        mask = mask.to(device)
        ref_path = ARTIFACT / "raw_rgb" / sample_id / "reference.png"
        reference = image_tensor(ref_path, device)
        reference_array = np.asarray(Image.open(ref_path).convert("RGB"), dtype=np.uint8)
        mask_path = ARTIFACT / "masks" / f"{sample_id}.png"
        mask_array = np.asarray(Image.open(mask_path).convert("L"), dtype=np.uint8)
        for run, directory in run_images.items():
            path = directory / f"{uid}.png"
            prediction = image_tensor(path, device)
            values = compute_metrics(prediction, reference, mask, edge, lpips_fn, device)
            pred_array = np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)
            rows.append({
                "sample_id": sample_id,
                "uid": uid,
                "object_idx": object_idx,
                "object_seed": seed,
                "run": run,
                "png_sha256": sha(path),
                "reference_sha256": sha(ref_path),
                "mask_sha256": sha(mask_path),
                "metric_runtime_python": sys.version.split()[0],
                "metric_runtime_torch": torch.__version__,
                "metric_runtime_diffusers": __import__("diffusers").__version__,
                "metric_runtime_lpips": "geotex.eval_exploration.get_lpips_fn; AlexNet weights v0.1",
                "checkpoint_sha256": CHECKPOINT_SHA,
                **{k: float(v) for k, v in values.items()},
                **ciede(reference_array, pred_array, mask_array),
            })
    out = ROOT / "P0_CANONICAL_EVALUATION_METRICS.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} PNG metric rows under {device} to {out}")


if __name__ == "__main__":
    main()
