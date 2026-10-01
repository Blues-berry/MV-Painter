#!/usr/bin/env python
"""Forensic decomposition of the archived layer-LHL vs seeded-replica gap.

Stage 1 (CPU): recompute ee.compute_metrics from the ARCHIVED prediction
PNGs against the current unique6 GT/mask/edge path, for a stratified sample
across source groups. If recomputed == archived rows, the archived records
are metric-consistent with the current protocol and the gap is purely
generation-side (different predicted pixels), not a metric/GT artifact.

Stage 2 (GPU, --regen N): regenerate the same objects under the frozen
seeded protocol (verbatim block) and compare per-object against the
archived predictions, separately for source groups.

No paper-facing numbers are produced here; forensics only.
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from omegaconf import OmegaConf
from torchvision.utils import save_image

ROOT = Path("/4T/CXY/MV-Painter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from src.utils.train_util import instantiate_from_config

CONFIG = "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml"
CHECKPOINT = str(ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt")
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
ARCH_BASE = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule")
SAMPLE = [0, 1, 30, 60, 89, 100, 130, 150, 200, 250, 273, 275]
OUT = ROOT / "final/round2/coordination/core7_same_runner_completion_20261001/lhl_forensics"


def src(uid: str) -> str:
    if uid.startswith("abo"):
        return "abo"
    if uid.startswith("objaverse"):
        return "objaverse"
    return "hexuid"


def load_archived_rows() -> dict[int, dict]:
    rows = {}
    for r in csv.DictReader(open(ARCH_BASE / "layer_official_v2_merged/per_object_metrics.csv")):
        rows[int(r["object_idx"])] = {k: float(v) for k, v in r.items()
                                      if k not in ("object", "object_idx", "schedule")}
    return rows


def archived_pred_path(idx: int) -> Path:
    sub = "layer_official_v2_head" if idx <= 137 else "layer_official_v2_tail"
    return ARCH_BASE / sub / "predictions" / "layer_LHL" / f"obj_{idx + 24:04d}.png"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    rows_json = OUT / "stage1_recompute.json"
    if rows_json.exists():
        print("stage1 already done:", rows_json)
        return

    arch_rows = load_archived_rows()
    uids = [l.strip() for l in OBJECT_LIST.read_text().splitlines() if l.strip()]

    # GT/mask/edge are deterministic; build them once per object (CPU or GPU).
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    dataset = instantiate_from_config(validation)
    lpips_fn = ee.get_lpips_fn(device)

    results = []
    for idx in SAMPLE:
        object_seed = 42 + idx
        random.seed(object_seed)
        np.random.seed(object_seed)
        torch.manual_seed(object_seed)
        batch = collate_batch(dataset, idx, device)
        _, target, _, real_depth, geo_input, mask = prepare_batch(batch, 256, device)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1)

        pred_png = np.asarray(Image.open(archived_pred_path(idx)).convert("RGB"), dtype=np.float32) / 255.0
        pred = torch.from_numpy(pred_png).permute(2, 0, 1).contiguous().unsqueeze(0).to(device)
        metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
        arc = arch_rows[idx]
        row = {
            "object_idx": idx,
            "source": src(uids[idx]),
            "recomputed": {k: float(v) for k, v in metrics.items()},
            "archived_row": arc,
            "diff": {k: float(metrics[k]) - arc[k] for k in metrics if k in arc},
        }
        results.append(row)
        print(f"idx {idx:3d} {src(uids[idx]):9s} fg_psnr recompute={metrics['fg_psnr']:.3f} "
              f"archived={arc['fg_psnr']:.3f} diff={metrics['fg_psnr']-arc['fg_psnr']:+.3f}", flush=True)

    rows_json.write_text(json.dumps(results, indent=2) + "\n")
    print("stage1 complete ->", rows_json)




def stage2() -> None:
    """GPU discriminating experiment (see ARCHIVED_LHL_PROVENANCE_AUDIT.md B.3).

    Regenerates the stage-1 sample objects under (a) the frozen seeded
    protocol with schedule layer_lhl, and (b) the same protocol with the
    cond augmentation path disabled (stretch + random_resize replaced by
    identity on the RUNTIME dataset module). Decisive statistic: the
    regenerated FG-PSNR per object, compared against the seeded frozen row
    (validates the regen) and the archived row (the anomaly).
    """
    import src.data.mvpainter_dataset as ds_mod  # the runtime module instance

    device = torch.device("cuda:0")
    out2 = OUT / "stage2_regen.json"
    arch_uids = [l.strip() for l in OBJECT_LIST.read_text().splitlines() if l.strip()]
    arch_rows = load_archived_rows()
    seeded_rows = {r["object_idx"]: r for r in json.loads(
        (Path("/4T/tmp/mvpainter-layer-confirmation-20260930/layer_lhl_rows.json")).read_text())}

    model = ee.load_model(CONFIG, CHECKPOINT, device)
    config = OmegaConf.load(CONFIG)
    lpips_fn = ee.get_lpips_fn(device)

    lhl_schedule = lambda p: {  # noqa: E731  (frozen LHL)
        "deep": (1.25 if p < 1 / 3 else 2.50 if p < 2 / 3 else 1.25),
        "middle": (1.25 if p < 1 / 3 else 2.50 if p < 2 / 3 else 1.25),
        "shallow": (0.50 if p < 1 / 3 else 0.75 if p < 2 / 3 else 0.50),
    }

    results = []
    for disable_aug in (False, True):
        if disable_aug:
            ds_mod.MVPainterData.random_stretch_or_compress = lambda self, image, min_scale=0.5, max_scale=1.5: image
            ds_mod.MVPainterData.random_resize = lambda self, img, random_ratio=0.8: img
        else:
            # restore originals for the False pass (module-level singletons)
            import importlib
            importlib.reload(ds_mod)
        validation = config.data.params.validation
        validation.params.target_view_mode = "unique6"
        validation.params.object_list_file = str(OBJECT_LIST.resolve())
        dataset = instantiate_from_config(validation)

        for idx in SAMPLE:
            object_seed = 42 + idx
            random.seed(object_seed)
            np.random.seed(object_seed)
            torch.manual_seed(object_seed)
            batch = collate_batch(dataset, idx, device)
            _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
            geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)
            edge = compute_edge_mask(real_depth.float(), threshold=0.1)
            torch.manual_seed(42)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
            torch.manual_seed(42)
            pred = exp.generate_with_schedule(
                model, batch, device, torch.float16, geo_feats, lhl_schedule,
                50, init_latents.clone(), {},
            )
            metrics = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
            tag = "augOFF" if disable_aug else "augON"
            png_path = OUT / f"pred_{tag}_obj_{idx + 24:04d}.png"
            save_image(pred, png_path)
            results.append({
                "object_idx": idx, "source": src(arch_uids[idx]), "aug_disabled": disable_aug,
                "regen_fg_psnr": float(metrics["fg_psnr"]),
                "seeded_row_fg_psnr": float(seeded_rows[idx]["fg_psnr"]),
                "archived_fg_psnr": float(arch_rows[idx]["fg_psnr"]),
                "regen_vs_seeded_diff": float(metrics["fg_psnr"]) - float(seeded_rows[idx]["fg_psnr"]),
                "regen_vs_archived_diff": float(metrics["fg_psnr"]) - float(arch_rows[idx]["fg_psnr"]),
                "pred_png": str(png_path),
            })
            del pred, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
            torch.cuda.empty_cache()
            print(f"{tag} idx={idx:3d} {src(arch_uids[idx]):9s} regen={metrics['fg_psnr']:7.3f} "
                  f"seeded={seeded_rows[idx]['fg_psnr']:7.3f} archived={arch_rows[idx]['fg_psnr']:7.3f}", flush=True)

    out2.write_text(json.dumps(results, indent=2) + "\n")
    print("stage2 complete ->", out2)


if __name__ == "__main__":
    import sys as _sys
    if "--regen" in _sys.argv:
        stage2()
    else:
        main()
