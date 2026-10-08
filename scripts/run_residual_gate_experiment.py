#!/usr/bin/env python
"""Run the frozen feature-relative residual gate on the diagnostic set."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("/4T/CXY/MV-Painter")
ARTIFACT = ROOT / "1008/engineering/color_failure"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = BASE / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
DEFAULT_CONFIG = ARTIFACT / "config/feature_ratio_gate.json"
CALIBRATION_LOCK = ARTIFACT / "logs/FEATURE_RATIO_GATE_LOCK.json"
RUN_DIR = Path(os.environ.get("MVP_RUN_DIR", str(ARTIFACT / "runs/feature_ratio_gate")))
DEVICE = torch.device(os.environ.get("MVP_DEVICE", "cuda:0"))
STEPS = 50
GATE_ENABLED = os.environ.get("MVP_GATE_ENABLED", "1") == "1"
METHODS = ["c3_feature_gate", "linear_feature_gate"]
ACTIVE_TRACES: dict[int, list] | None = None

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
import geotex.eval_exploration as ee  # noqa: E402
import geotex.explore_contradiction as exp  # noqa: E402
from data_utils import collate_batch, prepare_batch  # noqa: E402
from mvpainter.model_unet_geotex import GeoTexResnetWrapper  # noqa: E402
from metrics import compute_edge_mask  # noqa: E402
from residual_gate import apply_feature_ratio_bound  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def scale_for(method: str, progress: float) -> dict[str, float]:
    low = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
    high = {"deep": 2.50, "middle": 2.50, "shallow": 0.75}
    if method == "c3_feature_gate":
        if progress < 1.0 / 3.0 or progress >= 2.0 / 3.0:
            return low
        return high
    if method == "linear_feature_gate":
        return {depth: low[depth] + progress * (high[depth] - low[depth]) for depth in low}
    raise ValueError(f"unknown method: {method}")


def install_gate(tau_by_depth: dict[str, float]):
    """Patch this isolated process only; the baseline wrapper file is untouched."""
    original = GeoTexResnetWrapper.forward

    def gated_forward(self, *args, **kwargs):
        hidden = self.resnet(*args, **kwargs)
        if GeoTexResnetWrapper._skip_correction or self._current_geo_feats is None:
            return hidden
        geo_feat = self._current_geo_feats.get(self.geo_feat_key)
        if geo_feat is None:
            return hidden
        if geo_feat.shape[2:] != hidden.shape[2:]:
            import torch.nn.functional as F
            geo_feat = F.interpolate(geo_feat, size=hidden.shape[2:], mode="bilinear", align_corners=False)
        if self._correction_controller is not None:
            raise RuntimeError("feature-ratio gate prototype requires the baseline controller to be disabled")

        residual = self.adapter.compute_correction(hidden, geo_feat)
        requested_scale = float(getattr(self, "_adapter_scale", 1.0))
        effective_scale = min(requested_scale, self._max_scale)
        if GATE_ENABLED:
            applied, stats = apply_feature_ratio_bound(
                residual, hidden, scale=effective_scale, tau=tau_by_depth[self.depth_group]
            )
        else:
            applied, stats = apply_feature_ratio_bound(
                residual, hidden, scale=effective_scale, tau=1.0e30
            )
        self._last_correction = applied
        self._last_hidden = hidden.detach()
        if ACTIVE_TRACES is None:
            raise RuntimeError("gate trace collection is not active")
        ACTIVE_TRACES.setdefault(self.adapter_idx, []).append({
            "depth": self.depth_group,
            "requested_scale": requested_scale,
            "effective_scale_before_gate": effective_scale,
            "tau": tau_by_depth[self.depth_group] if GATE_ENABLED else None,
            **stats,
        })
        return hidden + applied

    GeoTexResnetWrapper.forward = gated_forward
    return original


def serialize_trace(traces: dict[int, list]) -> dict:
    output = {}
    counts = {len(values) for values in traces.values()}
    if counts != {STEPS}:
        raise RuntimeError(f"expected {STEPS} calls per adapter, got {sorted(counts)}")
    for step in range(STEPS):
        output[str(step)] = {}
        for adapter_idx, records in traces.items():
            record = records[step]
            output[str(step)][str(adapter_idx)] = {
                key: (float(value.cpu()) if torch.is_tensor(value) else value)
                for key, value in record.items()
            }
    return output


def make_dataset(sample: dict):
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(Path(sample["object_list"]).resolve())
    validation.params.root_dir_list = [str(Path(sample["data_root"]).resolve())]
    return instantiate_from_config(validation)


def main() -> None:
    global ACTIVE_TRACES
    freeze_path = ARTIFACT / "SAMPLE_FREEZE.json"
    gate_config_path = Path(os.environ.get("MVP_FEATURE_GATE_CONFIG", str(DEFAULT_CONFIG)))
    freeze = json.loads(freeze_path.read_text())
    gate_config = json.loads(gate_config_path.read_text())
    calibration_lock = json.loads(CALIBRATION_LOCK.read_text())
    tau_by_depth = gate_config["tau_by_depth"]
    if tau_by_depth != calibration_lock["tau_by_depth"]:
        raise RuntimeError("gate config thresholds differ from the frozen baseline calibration lock")
    if "MVP_GATE_ENABLED" not in os.environ and gate_config.get("enabled_by_default") != GATE_ENABLED:
        raise RuntimeError("gate config default disagrees with runner default")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "predictions").mkdir(exist_ok=True)
    (RUN_DIR / "residual_logs").mkdir(exist_ok=True)

    model = ee.load_model(str(CONFIG), str(CHECKPOINT), DEVICE)
    lpips_fn = ee.get_lpips_fn(DEVICE)
    if lpips_fn is None:
        raise RuntimeError("LPIPS is unavailable; refusing to run an incomplete metric set")
    datasets = {}
    rows = []
    identity_by_uid = {}
    method_records = {method: [] for method in METHODS}
    original_forward = install_gate(tau_by_depth)
    try:
        for sample in freeze["samples"]:
            source = sample["source"]
            if source not in datasets:
                datasets[source] = make_dataset(sample)
            obj_idx = int(sample["object_idx"])
            object_seed = int(sample["object_seed"])
            reference_integrity = None
            for method in METHODS:
                random.seed(object_seed)
                np.random.seed(object_seed)
                torch.manual_seed(object_seed)
                batch = collate_batch(datasets[source], obj_idx, DEVICE)
                _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, DEVICE)
                geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
                geo_feats = model.geo_encoder(geo_clean)
                edge = compute_edge_mask(real_depth.float(), threshold=0.1)
                torch.manual_seed(42)
                latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
                init_latents = torch.randn(1, 4, latent_h, latent_w, device=DEVICE, dtype=torch.float16)
                torch.manual_seed(42)

                integrity = {
                    "cond": tensor_sha(batch["cond_imgs"]),
                    "target": tensor_sha(batch["target_imgs"]),
                    "normal": tensor_sha(batch["depth_imgs"]),
                    "depth": tensor_sha(batch["real_depth_imgs"]),
                    "global_embeds": tensor_sha(batch["global_embeds"]),
                    "init_latent": tensor_sha(init_latents),
                }
                if reference_integrity is None:
                    reference_integrity = integrity
                elif integrity != reference_integrity:
                    raise RuntimeError(f"shared-input integrity failure: {sample['sample_id']}/{method}")

                traces: dict[int, list] = {}
                ACTIVE_TRACES = traces
                model._set_geo_feats_on_wrappers(geo_feats)
                started = time.time()
                prediction = exp.generate_with_schedule(
                    model, batch, DEVICE, torch.float16, geo_feats,
                    lambda progress, name=method: scale_for(name, progress),
                    STEPS, init_latents.clone(), {},
                )
                metrics = ee.compute_metrics(prediction, target, mask, edge, lpips_fn, DEVICE)
                pred_dir = RUN_DIR / "predictions" / method
                pred_dir.mkdir(parents=True, exist_ok=True)
                save_image(prediction, pred_dir / f"{sample['uid']}.png")
                trace_dir = RUN_DIR / "residual_logs" / method
                trace_dir.mkdir(parents=True, exist_ok=True)
                (trace_dir / f"{sample['uid']}.json").write_text(
                    json.dumps(serialize_trace(traces), indent=2) + "\n"
                )
                row = {
                    "sample_id": sample["sample_id"], "uid": sample["uid"],
                    "source": source, "object_idx": obj_idx, "object_seed": object_seed,
                    "method": method, "gate_enabled": GATE_ENABLED,
                    "elapsed_seconds": time.time() - started,
                    **{key: float(value) for key, value in metrics.items() if value is not None},
                    "input_hashes": integrity,
                }
                rows.append(row)
                method_records[method].append(row)
                model._clear_geo_feats_on_wrappers()
                ACTIVE_TRACES = None
                del prediction, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
                torch.cuda.empty_cache()
            print(f"finished {sample['sample_id']} ({len(rows)}/{len(freeze['samples']) * len(METHODS)})", flush=True)
    finally:
        ACTIVE_TRACES = None
        GeoTexResnetWrapper.forward = original_forward
        model._clear_geo_feats_on_wrappers()

    rows_path = RUN_DIR / "per_object_metrics.csv"
    csv_rows = [{key: value for key, value in row.items() if key != "input_hashes"} for row in rows]
    with rows_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_rows[0].keys())
        writer.writeheader()
        writer.writerows(csv_rows)
    (RUN_DIR / "rows.json").write_text(json.dumps(rows, indent=2) + "\n")
    sources = [ROOT / "scripts/run_residual_gate_experiment.py", ROOT / "geotex/residual_gate.py",
               ROOT / "geotex/explore_contradiction.py", ROOT / "geotex/eval_exploration.py",
               ROOT / "MVPainter/mvpainter/model_unet_geotex.py"]
    manifest = {
        "status": "complete", "checkpoint": str(CHECKPOINT), "checkpoint_sha256": sha256(CHECKPOINT),
        "config": str(CONFIG), "config_sha256": sha256(CONFIG),
        "sample_freeze_sha256": sha256(freeze_path),
        "gate_config_sha256": sha256(gate_config_path),
        "gate_calibration_lock_sha256": sha256(CALIBRATION_LOCK),
        "tau_by_depth": tau_by_depth, "gate_enabled": GATE_ENABLED,
        "gate_rule": "g=min(1,tau_depth/(RMS(scale_capped_residual)/RMS(pre_adapter_feature)+eps)); apply g to the scale-capped residual",
        "methods": METHODS, "rows": len(rows), "steps": STEPS,
        "target_view_mode": "unique6", "device": str(DEVICE),
        "shared_inputs_equal_across_methods": True,
        "source_sha256": {str(path): sha256(path) for path in sources},
        "method_elapsed_seconds_mean": {
            method: float(np.mean([r["elapsed_seconds"] for r in method_records[method]]))
            for method in METHODS
        },
        "note": "Prototype only. It uses frozen depth-group thresholds from baseline GFL; no color metric enters calibration.",
    }
    (RUN_DIR / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"saved {len(rows)} rows to {rows_path}", flush=True)


if __name__ == "__main__":
    main()
