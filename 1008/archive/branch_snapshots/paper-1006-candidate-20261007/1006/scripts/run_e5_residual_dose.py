#!/usr/bin/env python3
"""Development-only residual-dose feasibility pilot; records no quality metrics."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/e5_residual_dose"
RUN = DATA / "runs"
RUNNER_PATH = ROOT / "scripts/run_validation_v3_experiment.py"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
DATA_ROOT = ROOT / "data/train_data/rendered_full"
PROTOCOL = ROOT / "1006/evidence/protocols/E5_RESIDUAL_DOSE_FEASIBILITY_PROTOCOL_20261006.md"
EXPECTED_SOURCE_HASHES = {
    "runner": "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3",
    "adapter_wrapper": "b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0",
    "pipeline": "d3bdbaa9de1b0daed7613da8f39074ffb4d6751a1cca9843f55df3bb0357c36c",
    "data_utils": "e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3",
    "generation_logic": "5da7fff22ea73b6d9500603d0905eda9a1ac9c44406346b259f3aba368b6ca13",
    "metric_implementation": "adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5",
    "checkpoint": "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0",
    "config": "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b",
}
OBJECT_INDICES = (0, 4, 9, 13, 16, 21)
GROUPS = ("deep", "middle", "shallow")
WINDOWS = (1, 3, 5)
ALPHAS = (0.005, 0.01, 0.02)
LOW = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
STEPS = 50


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha256(tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def normalized_delta(hidden, raw_correction, alpha: float, activation_dtype):
    """Return the requested delta and its actually realized post-cast increment."""
    hidden32 = hidden.detach().float()
    raw32 = raw_correction.detach().float()
    hidden_norm = float(hidden32.norm().item())
    raw_norm = float(raw32.norm().item())
    if not math.isfinite(hidden_norm) or hidden_norm <= 0:
        raise ValueError("zero or nonfinite hidden-state norm")
    if not math.isfinite(raw_norm) or raw_norm <= 0:
        raise ValueError("zero or nonfinite correction norm")
    requested = float(alpha) * hidden_norm
    delta = (raw32 * (requested / raw_norm)).to(dtype=activation_dtype)
    return hidden_norm, raw_norm, requested, delta


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def source_hashes() -> dict[str, str]:
    paths = {
        "runner": RUNNER_PATH,
        "adapter_wrapper": ROOT / "MVPainter/mvpainter/model_unet_geotex.py",
        "pipeline": ROOT / "MVPainter/mvpainter/mvpainter_pipeline.py",
        "data_utils": ROOT / "geotex/data_utils.py",
        "generation_logic": ROOT / "geotex/explore_contradiction.py",
        "metric_implementation": ROOT / "geotex/eval_exploration.py",
        "checkpoint": CHECKPOINT,
        "config": CONFIG,
    }
    return {name: sha256_file(path) for name, path in paths.items()}


def load_runner(device: str):
    os.environ.update({
        "MVP_REPO_ROOT": str(ROOT), "MVP_CONFIG": str(CONFIG),
        "MVP_CHECKPOINT": str(CHECKPOINT), "MVP_OBJECT_LIST": str(OBJECT_LIST),
        "MVP_DATA_ROOT": str(DATA_ROOT), "MVP_RUN_DIR": str(RUN),
        "MVP_CONDITIONS": "a_baseline", "MVP_DEVICE": device,
        "MVP_NUM_THREADS": "6", "OMP_NUM_THREADS": "6", "MKL_NUM_THREADS": "6",
    })
    spec = importlib.util.spec_from_file_location("frozen_validation_v3_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen validation runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_hooks(runner, model, state: dict[str, Any], cell: dict[str, Any]):
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper

    handles = []
    seen_hidden: dict[int, Any] = {}
    for module in model.pipeline.unet.modules():
        if not isinstance(module, GeoTexResnetWrapper):
            continue
        module_id = id(module)

        def capture_hidden(resnet, inputs, output, key=module_id):
            if not isinstance(output, runner.torch.Tensor):
                raise TypeError("adapter wrapped ResNet must return a Tensor")
            seen_hidden[key] = output

        def apply_normalized_delta(wrapper, inputs, output, key=module_id):
            if not isinstance(output, runner.torch.Tensor):
                raise TypeError("adapter wrapper must return a Tensor")
            if wrapper.depth_group != cell["group"]:
                return output
            step = int(state["step"])
            lo, hi = 10 * (cell["window"] - 1), 10 * cell["window"]
            if not lo <= step < hi:
                return output
            if GeoTexResnetWrapper._skip_correction:
                state["reference_pass_skips"] += 1
                state["traces"].append({
                    "object_idx": int(state["object_idx"]), "uid": state["uid"],
                    "adapter_idx": int(wrapper.adapter_idx), "group": wrapper.depth_group,
                    "window": int(cell["window"]), "step": step,
                    "alpha": float(cell["alpha"]), "status": "reference_pass_skipped_unchanged",
                })
                return output
            hidden = seen_hidden.get(key)
            base = wrapper._last_correction
            record = {
                "object_idx": int(state["object_idx"]), "uid": state["uid"],
                "adapter_idx": int(wrapper.adapter_idx), "group": wrapper.depth_group,
                "window": int(cell["window"]), "step": step,
                "alpha": float(cell["alpha"]), "dtype": str(output.dtype),
                "requested_scale": float(getattr(wrapper, "_adapter_scale", 1.0)),
                "effective_scale": float(min(getattr(wrapper, "_adapter_scale", 1.0), wrapper._max_scale)),
                "cap": float(wrapper._max_scale),
            }
            if float(cell["alpha"]) == 0.0:
                record["status"] = "alpha_zero_noop"
                state["traces"].append(record)
                return output
            if hidden is None or base is None or wrapper._current_geo_feats is None:
                record["status"] = "missing_hidden_base_or_geo"
                state["traces"].append(record)
                return output
            h32 = hidden.detach().float()
            hidden_norm = float(h32.norm().item())
            record["hidden_l2"] = hidden_norm
            record["baseline_scaled_correction_l2"] = float(base.detach().float().norm().item())
            geo = wrapper._current_geo_feats.get(wrapper.geo_feat_key)
            if geo is None:
                record["status"] = "missing_geo_feature"
                state["traces"].append(record)
                return output
            if geo.shape[2:] != hidden.shape[2:]:
                import torch.nn.functional as F
                geo = F.interpolate(geo, size=hidden.shape[2:], mode="bilinear", align_corners=False)
            raw = wrapper.adapter.compute_correction(hidden, geo).detach().float()
            try:
                hidden_norm, raw_norm, requested, proposed = normalized_delta(
                    hidden, raw, float(cell["alpha"]), output.dtype)
            except ValueError as exc:
                record["status"] = "zero_or_nonfinite_hidden" if "hidden" in str(exc) else "zero_or_nonfinite_correction"
                record["error"] = str(exc)
                state["traces"].append(record)
                return output
            changed = output + proposed
            realized_delta = changed.detach().float() - output.detach().float()
            realized_norm = float(realized_delta.norm().item())
            realized_ratio = realized_norm / hidden_norm
            target_error = abs(realized_ratio - float(cell["alpha"])) / float(cell["alpha"])
            record.update({
                "requested_delta_l2": requested,
                "proposed_delta_l2_after_cast": float(proposed.detach().float().norm().item()),
                "realized_delta_l2_after_add": realized_norm,
                "realized_delta_over_raw_correction_l2": realized_norm / raw_norm,
                "baseline_plus_delta_equivalent_scale_l2": float(min(getattr(wrapper, "_adapter_scale", 1.0), wrapper._max_scale)) + realized_norm / raw_norm,
                "equivalent_total_scale_exceeds_cap": (float(min(getattr(wrapper, "_adapter_scale", 1.0), wrapper._max_scale)) + realized_norm / raw_norm) > float(wrapper._max_scale),
                "realized_relative_dose": realized_ratio,
                "relative_target_error": target_error,
                "status": "finite" if all(math.isfinite(v) for v in (realized_norm, realized_ratio, target_error)) else "nonfinite",
            })
            state["traces"].append(record)
            return changed

        handles.append(module.resnet.register_forward_hook(capture_hidden))
        handles.append(module.register_forward_hook(apply_normalized_delta))
    if not handles:
        raise RuntimeError("no GeoTexResnetWrapper hooks found on generation UNet")
    return handles


def generate_one(runner, obj_idx: int, uid: str, dataset, model, device, cell=None):
    torch = runner.torch
    object_seed = 42 + obj_idx
    random.seed(object_seed)
    np.random.seed(object_seed)
    torch.manual_seed(object_seed)
    batch = runner.collate_batch(dataset, obj_idx, device)
    _, target, _, real_depth, geo_input, mask = runner.prepare_batch(batch, model.img_size, device)
    geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
    geo_feats = model.geo_encoder(geo_clean)
    torch.manual_seed(42)
    dtype = torch.float16
    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
    init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
    torch.manual_seed(42)
    batch_hashes = {
        "cond": runner.h_tensor(batch["cond_imgs"]),
        "target": runner.h_tensor(batch["target_imgs"]),
        "normal": runner.h_tensor(batch["depth_imgs"]),
        "depth": runner.h_tensor(batch["real_depth_imgs"]),
        "global_embeds": runner.h_tensor(batch["global_embeds"]),
        "init_latent": runner.h_tensor(init_latents),
    }
    state = {"step": -1, "traces": [], "reference_pass_skips": 0,
             "object_idx": obj_idx, "uid": uid}
    handles = []
    if cell is not None:
        handles = build_hooks(runner, model, state, cell)

    def fixed_schedule(progress: float):
        state["step"] = int(round(progress * (STEPS - 1)))
        return dict(LOW)

    residual_log: dict = {}
    start = time.time()
    try:
        pred = runner.exp.generate_with_schedule(
            model, batch, device, dtype, geo_feats, fixed_schedule, STEPS,
            init_latents.clone(), residual_log,
        )
    finally:
        for handle in handles:
            handle.remove()
    elapsed = time.time() - start
    result = {
        "object_idx": obj_idx, "uid": uid,
        "output_tensor_sha256": tensor_sha256(pred), "input_hashes": batch_hashes,
        "elapsed_seconds": elapsed, "traces": state["traces"],
        "reference_pass_skips": state["reference_pass_skips"],
    }
    del pred, batch, target, real_depth, geo_input, mask, geo_feats, init_latents
    torch.cuda.empty_cache()
    return result


def run_shard(shard: int, device_index: int) -> None:
    import torch
    import diffusers
    import torchvision

    if sha256_file(PROTOCOL) != json.loads((DATA / "E5_LOCK.json").read_text())["protocol_sha256"]:
        raise RuntimeError("E5 protocol hash changed after lock")
    if source_hashes() != EXPECTED_SOURCE_HASHES:
        raise RuntimeError("frozen runner/source/checkpoint/config hash mismatch")
    probe_uids = [x.strip() for x in OBJECT_LIST.read_text().splitlines() if x.strip()]
    selected = {index: probe_uids[index] for index in OBJECT_INDICES}
    lock = json.loads((DATA / "E5_LOCK.json").read_text())
    if lock["selected_objects"] != [{"object_idx": i, "uid": selected[i]} for i in OBJECT_INDICES]:
        raise RuntimeError("E5 selected-object lock mismatch")
    if lock["pilot_script_sha256"] != sha256_file(Path(__file__).resolve()):
        raise RuntimeError("E5 pilot script changed after lock")
    device = f"cuda:{device_index}"
    runner = load_runner(device)
    model = runner.ee.load_model(str(CONFIG), str(CHECKPOINT), torch.device(device))
    config = runner.OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    validation.params.root_dir_list = [str(DATA_ROOT.resolve())]
    dataset = runner.instantiate_from_config(validation)
    if len(dataset) != len(probe_uids):
        raise RuntimeError(f"probe data length {len(dataset)} != UID list length {len(probe_uids)}")
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    wrappers = [m for m in model.pipeline.unet.modules() if isinstance(m, GeoTexResnetWrapper)]
    group_counts = {g: sum(m.depth_group == g for m in wrappers) for g in GROUPS}
    group_adapter_indices = {g: sorted(int(m.adapter_idx) for m in wrappers if m.depth_group == g) for g in GROUPS}
    if any(count == 0 for count in group_counts.values()):
        raise RuntimeError(f"missing wrapper group(s): {group_counts}")
    atomic_json(RUN / f"model_preflight_shard{shard}.json", {
        "device": device, "wrapper_count": len(wrappers), "group_wrapper_counts": group_counts,
        "group_adapter_indices": group_adapter_indices,
        "protocol_sha256": sha256_file(PROTOCOL), "source_hashes": source_hashes(),
        "checkpoint_sha256": sha256_file(CHECKPOINT), "config_sha256": sha256_file(CONFIG),
        "runtime": {"torch": torch.__version__, "cuda": torch.version.cuda,
                    "gpu_name": torch.cuda.get_device_name(device_index),
                    "numpy": np.__version__, "diffusers": diffusers.__version__,
                    "torchvision": torchvision.__version__},
    })

    rows_path = RUN / f"rows_shard{shard}.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    completed = {(r["object_idx"], r["condition"]) for r in rows}
    for obj_idx in OBJECT_INDICES:
        if obj_idx % 2 != shard:
            continue
        uid = selected[obj_idx]
        base = generate_one(runner, obj_idx, uid, dataset, model, torch.device(device), None)
        noop = generate_one(runner, obj_idx, uid, dataset, model, torch.device(device),
                            {"group": "deep", "window": 3, "alpha": 0.0})
        if base["output_tensor_sha256"] != noop["output_tensor_sha256"]:
            raise RuntimeError(f"alpha-zero hook changed output for {uid}")
        for name, record in (("baseline", base), ("alpha0_noop", noop)):
            if (obj_idx, name) not in completed:
                rows.append({"condition": name, **record})
                completed.add((obj_idx, name))
                atomic_json(rows_path, rows)
        for group in GROUPS:
            for window in WINDOWS:
                for alpha in ALPHAS:
                    name = f"{group}_W{window}_a{alpha:g}"
                    if (obj_idx, name) in completed:
                        continue
                    cell = {"group": group, "window": window, "alpha": alpha}
                    record = generate_one(runner, obj_idx, uid, dataset, model,
                                          torch.device(device), cell)
                    rows.append({"condition": name, **record})
                    completed.add((obj_idx, name))
                    atomic_json(rows_path, rows)
                    print(f"E5 shard {shard}: object {obj_idx} condition {name} complete", flush=True)
        print(f"E5 shard {shard}: completed object {obj_idx} / {uid}", flush=True)
    atomic_json(RUN / f"shard{shard}_manifest.json", {
        "status": "complete", "shard": shard, "device": device,
        "row_count": len(rows), "source_hashes": source_hashes(),
        "protocol_sha256": sha256_file(PROTOCOL), "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    })


def lock_protocol() -> None:
    if (RUN / "rows_shard0.json").exists() or (RUN / "rows_shard1.json").exists():
        raise RuntimeError("cannot create E5 lock after any pilot output exists")
    uids = [x.strip() for x in OBJECT_LIST.read_text().splitlines() if x.strip()]
    if len(uids) != 24:
        raise RuntimeError(f"expected the frozen 24-object probe, got {len(uids)}")
    hashes = source_hashes()
    if hashes != EXPECTED_SOURCE_HASHES:
        raise RuntimeError(f"source identity mismatch: {hashes}")
    selected = [{"object_idx": i, "uid": uids[i]} for i in OBJECT_INDICES]
    if any(not (DATA_ROOT / row["uid"]).is_dir() for row in selected):
        raise RuntimeError("one or more selected development objects lack local rendered inputs")
    payload = {
        "protocol": str(PROTOCOL), "protocol_sha256": sha256_file(PROTOCOL),
        "pilot_script": str(Path(__file__).resolve()),
        "pilot_script_sha256": sha256_file(Path(__file__).resolve()),
        "audit_script": str(ROOT / "1006/scripts/audit_e5_residual_dose.py"),
        "audit_script_sha256": sha256_file(ROOT / "1006/scripts/audit_e5_residual_dose.py"),
        "launcher_script": str(ROOT / "1006/scripts/launch_e5_residual_dose.py"),
        "launcher_script_sha256": sha256_file(ROOT / "1006/scripts/launch_e5_residual_dose.py"),
        "locked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_hashes": hashes, "probe_object_list": str(OBJECT_LIST),
        "probe_object_list_sha256": sha256_file(OBJECT_LIST), "data_root": str(DATA_ROOT),
        "selected_objects": selected, "selected_original_indices": list(OBJECT_INDICES),
        "groups": list(GROUPS), "windows": list(WINDOWS), "alphas": list(ALPHAS),
        "baseline_scale": LOW, "caps": CAPS, "steps": STEPS,
        "expected_generation_count": 174,
        "outcomes_blind": True, "quality_metrics_computed": False,
        "output_images_persisted": False,
    }
    atomic_json(DATA / "E5_LOCK.json", payload)
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", action="store_true")
    parser.add_argument("--shard", type=int, choices=(0, 1))
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()
    if args.lock:
        lock_protocol()
    elif args.shard is not None:
        run_shard(args.shard, args.device)
    else:
        parser.error("select --lock or --shard")


if __name__ == "__main__":
    main()
