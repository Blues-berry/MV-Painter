import csv
import json
import sys
from pathlib import Path

import torch
from omegaconf import OmegaConf

sys.path.insert(0, "/4T/CXY/MV-Painter")
sys.path.insert(0, "/4T/CXY/MV-Painter/geotex")
sys.path.insert(0, "/4T/CXY/MV-Painter/MVPainter")
from src.utils.train_util import instantiate_from_config
import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp


CONFIG = "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml"
CHECKPOINT = "/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
OUTPUT = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_holdout")
ROWS_JSON = OUTPUT / "rows.json"


def stage(progress, early, middle, late):
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def layer_lhl(progress):
    return {
        "deep": stage(progress, 1.25, 2.50, 1.25),
        "middle": stage(progress, 1.25, 2.50, 1.25),
        "shallow": stage(progress, 0.50, 0.75, 0.50),
    }


def save_rows(rows):
    ROWS_JSON.write_text(json.dumps(rows, indent=2) + "\n")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = json.loads(ROWS_JSON.read_text()) if ROWS_JSON.exists() else []
    completed = {int(row["object_idx"]) for row in rows}
    device = torch.device("cuda:0")
    config = OmegaConf.load(CONFIG)
    model = ee.load_model(CONFIG, CHECKPOINT, device)
    dataset = instantiate_from_config(config.data.params.validation)
    weight_dtype = torch.float16
    print(f"layer_LHL holdout: {len(dataset)} objects; already done={len(completed)}", flush=True)

    for obj_idx in range(len(dataset)):
        if obj_idx in completed:
            continue
        object_id = f"obj_{obj_idx + 24:04d}"
        batch = exp.collate_batch(dataset, obj_idx, device)
        _, target_imgs, _, _, geo_input, mask = exp.prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)
        residual_log = {}
        pred = exp.generate_with_schedule(
            model, batch, device, weight_dtype, geo_feats,
            layer_lhl, 50, init_latents.clone(), residual_log
        )
        metrics = exp.compute_probes(pred, target_imgs, mask)
        rows.append({"object": object_id, "object_idx": obj_idx, "schedule": "layer_LHL", **metrics})
        rows.sort(key=lambda row: int(row["object_idx"]))
        save_rows(rows)
        print(f"[{len(rows)}/{len(dataset)}] {object_id} psnr={metrics['psnr']:.4f} fg_ssim={metrics['fg_ssim']:.4f}", flush=True)
        del pred, batch, target_imgs, geo_input, mask, geo_feats, init_latents
        torch.cuda.empty_cache()

    fields = list(rows[0])
    with (OUTPUT / "per_object_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {len(rows)} rows to {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
