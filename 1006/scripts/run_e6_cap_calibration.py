#!/usr/bin/env python3
"""Locked development campaign; never launches Fresh D or edits a manuscript."""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

import run_e5_residual_dose as frozen
from cap_residual_calibration import GROUPS, MULTIPLIERS, install_hooks

ROOT = frozen.ROOT
DATA = ROOT / "1006/data/e6_cap_calibration"
RUN = DATA / "runs"
PROTOCOL = ROOT / "1006/evidence/protocols/E6_CAP_CALIBRATION_DEVELOPMENT_PROTOCOL_20261006.md"
SPEC = ROOT / "1006/evidence/protocols/E6_CAP_CALIBRATION_METHOD_SPEC_20261006.md"
PILOT_INDICES = frozen.OBJECT_INDICES
METRICS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")


def sha(path):
    return frozen.sha256_file(Path(path))


def write(path, value):
    frozen.atomic_json(Path(path), value)


def objects():
    uids = frozen.OBJECT_LIST.read_text().split()
    if len(uids) != 24 or len(set(uids)) != 24:
        raise RuntimeError("development cohort must be exactly the original 24 objects")
    return uids


def sources():
    paths = [PROTOCOL, SPEC, Path(__file__), Path(__file__).with_name("cap_residual_calibration.py"),
             Path(__file__).with_name("test_cap_residual_calibration.py"),
             Path(__file__).with_name("continue_e6_development.py")]
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


def verify():
    lock = json.loads((DATA / "E6_LOCK.json").read_text())
    if sources() != lock["e6_sources"] or frozen.source_hashes() != lock["core_sources"]:
        raise RuntimeError("E6/core source identity changed after freeze")
    if sha(frozen.OBJECT_LIST) != lock["object_list_sha256"] or objects() != lock["ordered_uids"]:
        raise RuntimeError("development input UID list changed")
    return lock


def freeze():
    if (DATA / "E6_LOCK.json").exists() or any(RUN.glob("**/rows_shard*.json")):
        raise RuntimeError("refuse to overwrite an existing lock or create one after outputs")
    core = frozen.source_hashes()
    if core != frozen.EXPECTED_SOURCE_HASHES:
        raise RuntimeError("the preserved core differs from its historical frozen identity")
    write(DATA / "E6_LOCK.json", {
        "protocol": "e6_cap_calibration_development_v1", "status": "PRE_OUTPUT_FROZEN",
        "locked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "e6_sources": sources(), "core_sources": core,
        "object_list_sha256": sha(frozen.OBJECT_LIST), "ordered_uids": objects(),
        "multipliers": list(MULTIPLIERS), "latent_seeds": [42, 43, 44],
        "technical_indices": list(PILOT_INDICES), "expected_rows": {
            "calibrate": 24, "technical": 30, "develop": 288},
        "novelty_status": "DEVELOPMENT_ONLY; NOT_ESTABLISHED; REVIEW_REQUIRED_BEFORE_FRESH_D",
    })


def rows(stage):
    result = []
    for path in sorted((RUN / stage).glob("rows_shard*.json")):
        result.extend(json.loads(path.read_text()))
    return result


def read_trace(row):
    path = Path(row["trace_path"])
    if sha(path) != row["trace_sha256"]:
        raise RuntimeError("trace hash mismatch")
    with gzip.open(path, "rt") as stream:
        return json.load(stream)


def expected_keys(stage):
    if stage == "calibrate":
        return {(i, 42, "native_gfl") for i in range(24)}
    if stage == "technical":
        conditions = ["native_gc3", "observer_noop", *[f"calibrated_{k:g}" for k in MULTIPLIERS]]
        return {(i, 42, c) for i in PILOT_INDICES for c in conditions}
    return {(i, seed, c) for i in range(24) for seed in (42, 43, 44)
            for c in ["native_gc3", *[f"calibrated_{k:g}" for k in MULTIPLIERS]]}


def checked_rows(stage):
    result = rows(stage)
    keys = [(r["object_idx"], r["latent_seed"], r["condition"]) for r in result]
    if len(set(keys)) != len(keys) or set(keys) != expected_keys(stage):
        raise RuntimeError(f"{stage}: incomplete or duplicate rows ({len(keys)})")
    identity = {}
    for row in result:
        if row["uid"] != objects()[row["object_idx"]]:
            raise RuntimeError("UID/index identity mismatch")
        key = row["object_idx"], row["latent_seed"]
        if key in identity and row["input_hashes"] != identity[key]:
            raise RuntimeError("paired input/latent identity mismatch")
        identity[key] = row["input_hashes"]
        read_trace(row)
        if stage == "develop":
            if not all(math.isfinite(row["metrics"][metric]) for metric in METRICS):
                raise RuntimeError("missing or nonfinite Core7 metrics")
            if sha(row["prediction_path"]) != row["prediction_sha256"]:
                raise RuntimeError("saved prediction hash mismatch")
    return result


def summarize_calibration():
    verify()
    result = checked_rows("calibrate")
    per_object = {group: [] for group in GROUPS}
    for row in result:
        traces = read_trace(row)
        for group in GROUPS:
            observed = [t for t in traces if t["group"] == group and t["status"] == "observed_unchanged"]
            if not observed or any(t["hidden_norm"] <= 0 or t["raw_norm"] <= 0 for t in observed):
                raise RuntimeError("invalid/zero calibration trace; no observation deletion allowed")
            per_object[group].append(float(np.median([t["native_scale"] * t["raw_over_hidden"] for t in observed])))
    refs = {group: float(np.median(per_object[group])) for group in GROUPS}
    refs["pooled"] = float(np.median(list(refs.values())))
    refs["definition"] = "median over objects of within-object median native-GFL applied r/h; unscaled raw observed"
    path = DATA / "E6_REFERENCES.json"
    if path.exists():
        if json.loads(path.read_text()) != refs:
            raise RuntimeError("existing calibrated reference differs; refuse replacement")
    else:
        write(path, refs)
    write(DATA / "E6_REFERENCE_LOCK.json", {"reference_sha256": sha(path),
          "calibration_rows": 24, "cohort": "REUSED_DEVELOPMENT_24",
          "calibration_row_ledger_hashes": {p.name: sha(p) for p in (RUN / "calibrate").glob("rows_shard*.json")}})


def references():
    path = DATA / "E6_REFERENCES.json"
    lock = json.loads((DATA / "E6_REFERENCE_LOCK.json").read_text())
    if sha(path) != lock["reference_sha256"]:
        raise RuntimeError("reference changed after calibration freeze")
    return json.loads(path.read_text())


def audit_technical():
    verify()
    references()
    result = checked_rows("technical")
    indexed = {(r["object_idx"], r["condition"]): r for r in result}
    errors, strata, saturated, active = [], {}, 0, 0
    for i in PILOT_INDICES:
        if indexed[i, "native_gc3"]["output_tensor_sha256"] != indexed[i, "observer_noop"]["output_tensor_sha256"]:
            errors.append(f"no-op output differs on object {i}")
    for row in result:
        traces = read_trace(row)
        if not traces:
            continue  # Baseline has no observer.
        writes = {(t["adapter_idx"], t["step"]) for t in traces if t["status"] == "reference_write_unchanged"}
        reads = [t for t in traces if t["status"] != "reference_write_unchanged"]
        expected = {(j, t) for j in row["adapter_indices"] for t in range(50)}
        if writes != expected or {(t["adapter_idx"], t["step"]) for t in reads} != expected or len(reads) != len(expected):
            errors.append(f"write/read step completeness mismatch: {row['uid']}/{row['condition']}")
        for t in reads:
            active += 1
            scale = t["applied_scale"]
            if not math.isfinite(scale) or not 0 <= scale <= t["cap"]:
                errors.append("cap bound/nonfinite scale")
            if t["hidden_norm"] <= 0 or t["raw_norm"] <= 0:
                errors.append("GPU zero norm; candidate technical gate stops")
            if t["status"] == "saturated":
                saturated += 1
            if t["status"] == "unsaturated":
                key = f"{row['condition']}:{t['group']}"
                good, total = strata.get(key, (0, 0))
                strata[key] = good + int(t["relative_rounding_error"] <= .05), total + 1
    for c in [f"calibrated_{k:g}" for k in MULTIPLIERS]:
        for group in GROUPS:
            key = f"{c}:{group}"
            good, total = strata.get(key, (0, 0))
            if total == 0 or good / total < .99:
                errors.append(f"unsaturated precision gate fails or cannot be assessed: {key}")
    report = {"status": "PASS" if not errors else "STOP_TECHNICAL_FAILURE", "errors": errors,
              "row_count": len(result), "active_read_steps": active, "saturated_steps": saturated,
              "precision_strata": strata, "no_quality_metrics": True,
              "scientific_efficacy": "NOT_TESTED", "equal_dose": "NOT_ESTABLISHED"}
    write(DATA / "E6_TECHNICAL_GATE.json", report)
    print(json.dumps(report, indent=2))
    if errors:
        raise RuntimeError("E6 technical gate stopped the candidate")


def analyze_development():
    verify()
    if json.loads((DATA / "E6_TECHNICAL_GATE.json").read_text())["status"] != "PASS":
        raise RuntimeError("development gate requires technical PASS")
    result = checked_rows("develop")
    indexed = {(r["object_idx"], r["latent_seed"], r["condition"]): r for r in result}
    candidates = []
    deltas = []
    for k in MULTIPLIERS:
        per_object = []
        for i in range(24):
            d = {metric: float(np.mean([indexed[i, seed, f"calibrated_{k:g}"]["metrics"][metric] -
                    indexed[i, seed, "native_gc3"]["metrics"][metric] for seed in (42, 43, 44)])) for metric in METRICS}
            deltas.append({"uid": objects()[i], "multiplier": k, **d})
            per_object.append(d)
        means = {m: float(np.mean([d[m] for d in per_object])) for m in METRICS}
        candidates.append({"multiplier": k, "means": means,
                           "qualifies": means["fg_psnr"] > 0 and means["fg_lpips"] < 0})
    qualified = sorted([c for c in candidates if c["qualifies"]], key=lambda c:
                       (c["means"]["fg_lpips"], -c["means"]["fg_psnr"], abs(c["multiplier"]-1), c["multiplier"]))
    selected = qualified[0]["multiplier"] if qualified else None
    report = {"status": "DEVELOPMENT_QUALIFIED_REQUIRES_NOVELTY_REVIEW" if qualified else "STOP_DEVELOPMENT_NO_JOINT_GAIN",
              "cohort": "REUSED_DEVELOPMENT_24", "candidate_results": candidates,
              "selected_multiplier": selected, "independent_confirmation": False,
              "novelty_established": False, "fresh_d_authorized_by_gate": False,
              "object_deltas": deltas, "core_source_hashes": verify()["core_sources"]}
    if qualified:
        selected_rows = [r for r in result if r["condition"] == f"calibrated_{selected:g}"]
        fixed = {g: {} for g in GROUPS}
        for g in GROUPS:
            for step in range(50):
                # Each object/seed contributes one within-wrapper mean.
                values = [np.mean([t["applied_scale"] for t in read_trace(r)
                          if t["group"] == g and t["step"] == step and t["status"] != "reference_write_unchanged"])
                          for r in selected_rows]
                fixed[g][str(step)] = float(np.mean(values))
        report["development_frozen_fixed_scale_ablation"] = fixed
        for metric, effect in (("fg_psnr", .5), ("fg_lpips", .01)):
            sd = float(np.std([d[metric] for d in deltas if d["multiplier"] == selected], ddof=1))
            # z(.9875)=2.2414, z(.90)=1.2816; conservative marginal planning.
            needed = int(math.ceil(((2.2414 + 1.2816)*sd/effect)**2))
            report.setdefault("fresh_d_precision_planning", {})[metric] = {
                "development_delta_sd": sd, "planning_effect": effect,
                "normal_approximation_n": needed, "not_joint_power_guarantee": True}
        requested = max(300, *[r["normal_approximation_n"] for r in report["fresh_d_precision_planning"].values()])
        report["fresh_d_planned_n"] = min(600, requested)
        report["fresh_d_precision_target_unmet_at_ceiling"] = requested > 600
    write(DATA / "E6_DEVELOPMENT_SELECTION.json", report)
    print(json.dumps({k: v for k, v in report.items() if k != "object_deltas"}, indent=2))


def run_stage(stage, shard, device_index):
    verify()
    refs = references() if stage != "calibrate" else None
    if stage == "develop" and json.loads((DATA / "E6_TECHNICAL_GATE.json").read_text())["status"] != "PASS":
        raise RuntimeError("cannot inspect development quality before technical PASS")
    runner = frozen.load_runner(f"cuda:{device_index}")
    torch = runner.torch
    device = torch.device(f"cuda:{device_index}")
    model = runner.ee.load_model(str(frozen.CONFIG), str(frozen.CHECKPOINT), device)
    config = runner.OmegaConf.load(frozen.CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(frozen.OBJECT_LIST)
    validation.params.root_dir_list = [str(frozen.DATA_ROOT)]
    dataset = runner.instantiate_from_config(validation)
    if len(dataset) != 24:
        raise RuntimeError("development dataset count mismatch")
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    adapter_indices = sorted(int(m.adapter_idx) for m in model.pipeline.unet.modules() if isinstance(m, GeoTexResnetWrapper))
    if len(adapter_indices) != 9:
        raise RuntimeError("expected nine wrappers on the frozen pipeline")
    lpips = runner.ee.get_lpips_fn(device) if stage == "develop" else None
    output = RUN / stage
    output.mkdir(parents=True, exist_ok=True)
    ledger = output / f"rows_shard{shard}.json"
    existing = json.loads(ledger.read_text()) if ledger.exists() else []
    done = {(r["object_idx"], r["latent_seed"], r["condition"]) for r in existing}
    for i, seed, condition in sorted(expected_keys(stage)):
        if i % 2 != shard or (i, seed, condition) in done:
            continue
        random.seed(42+i)
        np.random.seed(42+i)
        torch.manual_seed(42+i)
        batch = runner.collate_batch(dataset, i, device)
        _, target, _, depth, geo_input, mask = runner.prepare_batch(batch, model.img_size, device)
        geo = model.geo_encoder(torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0., posinf=1., neginf=0.))
        torch.manual_seed(seed)
        latents = torch.randn(1, 4, model.img_size*3//8, model.img_size*2//8, device=device, dtype=torch.float16)
        torch.manual_seed(seed)
        state = {"step": -1, "traces": []}
        mode = "calibrated" if condition.startswith("calibrated_") else "observe"
        k = float(condition.split("_")[-1]) if mode == "calibrated" else 1.0
        remove = (install_hooks(model, GeoTexResnetWrapper, state, mode, refs, k)
                  if condition != "native_gc3" else lambda: None)

        def schedule(progress):
            state["step"] = int(round(progress*49))
            return 1.25 if stage == "calibrate" else (2.5 if progress >= 1/3 and progress < 2/3 else 1.25)

        import time
        started = time.monotonic()
        try:
            with torch.no_grad():
                prediction = runner.exp.generate_with_schedule(model, batch, device, torch.float16,
                              geo, schedule, 50, latents.clone(), {})
        finally:
            remove()
        stem = f"{i:02d}_s{seed}_{condition}"
        trace_path = output / f"{stem}.json.gz"
        with gzip.open(trace_path, "wt") as stream:
            json.dump(state["traces"], stream)
        row = {"object_idx": i, "uid": objects()[i], "object_seed": 42+i,
               "latent_seed": seed, "condition": condition, "adapter_indices": adapter_indices,
               "input_hashes": {"cond": runner.h_tensor(batch["cond_imgs"]),
                    "target": runner.h_tensor(batch["target_imgs"]), "normal": runner.h_tensor(batch["depth_imgs"]),
                    "depth": runner.h_tensor(batch["real_depth_imgs"]), "global_embeds": runner.h_tensor(batch["global_embeds"]),
                    "init_latent": runner.h_tensor(latents)},
               "output_tensor_sha256": frozen.tensor_sha256(prediction),
               "trace_path": str(trace_path), "trace_sha256": sha(trace_path),
               "elapsed_seconds": time.monotonic()-started}
        if stage == "develop":
            edge = runner.compute_edge_mask(depth.float(), threshold=.1)
            row["metrics"] = {key: float(value) for key, value in
                              runner.ee.compute_metrics(prediction, target, mask, edge, lpips, device).items()}
            prediction_path = output / f"{stem}.png"
            runner.save_image(prediction, prediction_path)
            row.update(prediction_path=str(prediction_path), prediction_sha256=sha(prediction_path))
        existing.append(row)
        write(ledger, existing)
        print(f"E6 {stage} shard {shard}: {stem} complete", flush=True)
        del prediction, batch, target, depth, geo_input, mask, geo, latents
        torch.cuda.empty_cache()
    write(output / f"manifest_shard{shard}.json", {"status": "COMPLETE", "rows": len(existing),
          "lock_sha256": sha(DATA / "E6_LOCK.json"), "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "calibrate", "summarize-calibration", "technical", "audit-technical", "develop", "analyze-development"))
    parser.add_argument("--shard", type=int, choices=(0, 1), default=0)
    parser.add_argument("--device", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    actions = {"freeze": freeze, "summarize-calibration": summarize_calibration,
               "audit-technical": audit_technical, "analyze-development": analyze_development}
    if args.command in actions:
        actions[args.command]()
    else:
        run_stage(args.command, args.shard, args.device)


if __name__ == "__main__":
    main()
