#!/usr/bin/env python3
"""Freeze and audit the existing C3/TCAS evidence without model inference.

The script intentionally reads completed artifacts only.  It keeps the
MVPainter 276-object stage-placement evidence separate from the MV-Adapter
Exact 76-object evidence, and it treats missing metrics as missing rather than
trying to reconstruct them from incompatible tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np


SEED = 20260928
BOOTSTRAP_REPS = 10_000
MAIN_SCHEDULES = ("fixed_mean", "hll", "llh", "c3_lhl")
MAIN_METRICS = (
    ("full_psnr", "higher"),
    ("fg_psnr", "higher"),
    ("fg_ssim", "higher"),
    ("edge_ssim", "higher"),
    ("fg_lpips", "lower"),
    ("full_lpips", "lower"),
)
SERIALIZED_METRICS = (("full_ssim", "higher"),)
MV_REQUIRED_METRICS = (
    "psnr",
    "fg_ssim",
    "edge_ssim",
    "fg_lpips",
    "ciede2000",
    "gt_relative_texture_error",
)


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def finite_check(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict:
    missing: Counter[str] = Counter()
    nonfinite: Counter[str] = Counter()
    for row in rows:
        for field in fields:
            value = row.get(field)
            if value in (None, ""):
                missing[field] += 1
                continue
            try:
                if not math.isfinite(float(value)):
                    nonfinite[field] += 1
            except ValueError:
                nonfinite[field] += 1
    return {
        "rows": len(rows),
        "missing": dict(missing),
        "nonfinite": dict(nonfinite),
        "passed": not missing and not nonfinite,
    }


def object_schedule_table(rows: list[dict[str, str]], object_key: str, schedule_key: str) -> dict[str, dict[str, dict[str, str]]]:
    table: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        obj = row[object_key]
        schedule = row[schedule_key]
        if obj in table and schedule in table[obj]:
            raise ValueError(f"duplicate object/schedule row: {obj}/{schedule}")
        table.setdefault(obj, {})[schedule] = row
    return table


def bootstrap_ci(values: np.ndarray, seed: int = SEED) -> list[float]:
    rng = np.random.default_rng(seed)
    index = rng.integers(0, len(values), size=(BOOTSTRAP_REPS, len(values)))
    means = values[index].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def paired_stats(
    left: dict[str, dict[str, str]],
    right: dict[str, dict[str, str]],
    metric: str,
    direction: str,
) -> dict:
    objects = sorted(set(left) & set(right))
    left_values = np.asarray([float(left[obj][metric]) for obj in objects], dtype=np.float64)
    right_values = np.asarray([float(right[obj][metric]) for obj in objects], dtype=np.float64)
    delta = left_values - right_values
    favorable = delta if direction == "higher" else -delta
    return {
        "n": len(objects),
        "mean_raw_delta_left_minus_right": float(delta.mean()),
        "ci95_raw_delta": bootstrap_ci(delta),
        "direction": direction,
        "mean_delta_favoring_left": float(favorable.mean()),
        "ci95_delta_favoring_left": bootstrap_ci(favorable),
        "wins_favoring_left": int(np.sum(favorable > 0.0)),
        "ties": int(np.sum(favorable == 0.0)),
        "win_rate_favoring_left": float(np.mean(favorable > 0.0)),
        "bootstrap": {
            "unit": "object-level paired differences",
            "resamples": BOOTSTRAP_REPS,
            "seed": SEED,
            "confidence": 0.95,
        },
    }


def audit_main(root: Path) -> tuple[dict, dict, list[str]]:
    stage_dir = root / "final/round2/stage_placement_276_20260929"
    stage_path = stage_dir / "per_object_metrics.csv"
    serialized_path = stage_dir / "serialized_full_ssim_per_object.csv"
    rows = read_csv(stage_path)
    serialized_rows = read_csv(serialized_path)
    table = object_schedule_table(rows, "object", "schedule")
    serialized_table = object_schedule_table(serialized_rows, "object", "schedule")
    object_ids = sorted(table)
    errors: list[str] = []
    if len(object_ids) != 276:
        errors.append(f"main object count={len(object_ids)}, expected=276")
    if set(table) != set(serialized_table):
        errors.append("serialized Full-SSIM object set differs from formal stage CSV")
    for obj in object_ids:
        if set(table[obj]) != set(MAIN_SCHEDULES):
            errors.append(f"{obj}: stage schedule set mismatch")
        if set(serialized_table.get(obj, {})) != set(MAIN_SCHEDULES):
            errors.append(f"{obj}: serialized schedule set mismatch")
    metric_fields = tuple(metric for metric, _ in MAIN_METRICS)
    finite = finite_check(rows, metric_fields)
    serialized_finite = finite_check(serialized_rows, ("full_ssim",))
    if not finite["passed"] or not serialized_finite["passed"]:
        errors.append("main stage metrics contain missing/non-finite values")

    comparisons = {}
    c3 = {obj: table[obj]["c3_lhl"] for obj in object_ids}
    for comparator in ("fixed_mean", "hll", "llh"):
        comparisons[f"c3_lhl_minus_{comparator}"] = {
            metric: paired_stats(c3, {obj: table[obj][comparator] for obj in object_ids}, metric, direction)
            for metric, direction in MAIN_METRICS
        }
    serialized_comparisons = {}
    serialized_c3 = {obj: serialized_table[obj]["c3_lhl"] for obj in object_ids}
    for comparator in ("fixed_mean", "hll", "llh"):
        serialized_comparisons[f"c3_lhl_minus_{comparator}"] = {
            metric: paired_stats(
                serialized_c3,
                {obj: serialized_table[obj][comparator] for obj in object_ids},
                metric,
                direction,
            )
            for metric, direction in SERIALIZED_METRICS
        }

    eval_list_path = root / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
    provenance_path = root / "final/round2/main_adapter_clean_v2/clean_v2_provenance_300.csv"
    final_manifest_path = stage_dir / "final_manifest.json"
    final_manifest = json.loads(final_manifest_path.read_text())
    runner_manifest = final_manifest.get("runner_manifest", {})
    main_code_paths = {
        "stage_runner": root / "scripts/run_stage_placement_276_20260929.py",
        "stage_validator": root / "scripts/validate_stage_placement_276_20260929.py",
        "stage_evaluator": root / "geotex/stage_placement_eval.py",
    }
    eval_uids = [line.strip() for line in eval_list_path.read_text().splitlines() if line.strip()]
    provenance = {row["uid"]: row for row in read_csv(provenance_path)}
    source_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    exact_local_count = 0
    provenance_rows = 0
    for obj in object_ids:
        position = int(obj.rsplit("_", 1)[1])
        if position >= len(eval_uids):
            errors.append(f"{obj}: position outside clean-v2 evaluation list")
            continue
        record = provenance.get(eval_uids[position])
        if record is None:
            errors.append(f"{obj}: UID missing from clean-v2 provenance")
            continue
        provenance_rows += 1
        source_counts[record.get("source_type", "")] += 1
        status_counts[record.get("source_status", "")] += 1
        if record.get("local_exact_glb") and Path(record["local_exact_glb"]).is_file():
            exact_local_count += 1

    manifest = {
        "audit": "c3-tcas-full-baseline-v1",
        "status": "complete" if not errors else "complete_with_checks",
        "scope": "existing artifacts only; no inference launched",
        "main_adapter": {
            "cohort": "clean-v2 strict 276",
            "objects": len(object_ids),
            "rows": len(rows),
            "schedules": list(MAIN_SCHEDULES),
            "stage_csv": rel(root, stage_path),
            "serialized_full_ssim_csv": rel(root, serialized_path),
            "geometry_provenance_label": "clean-v2 source-stratified; not all objects have locally verified original GLB files",
            "source_type_counts": dict(source_counts),
            "source_status_counts": dict(status_counts),
            "provenance_rows": provenance_rows,
            "local_exact_glb_count": exact_local_count,
            "metrics_available_per_object": [metric for metric, _ in MAIN_METRICS],
            "metrics_not_available_in_stage_csv": ["ciede2000", "gt_relative_texture_error"],
            "serialized_full_ssim": {
                "ground_truth": "original RGBA composited over white float32",
                "rows": len(serialized_rows),
                "finite": serialized_finite["passed"],
            },
            "checkpoint": {
                "path": runner_manifest.get("checkpoint"),
                "sha256": runner_manifest.get("checkpoint_sha256"),
            },
            "object_list": {
                "path": runner_manifest.get("object_list"),
                "sha256": runner_manifest.get("object_list_sha256"),
                "count": runner_manifest.get("num_objects"),
            },
            "code_hashes": {label: sha256(path) for label, path in main_code_paths.items()},
            "finite_checks": {"formal_stage": finite, "serialized_full_ssim": serialized_finite},
            "paired_comparisons": comparisons,
            "serialized_full_ssim_paired_comparisons": serialized_comparisons,
        },
        "source_hashes": {
            rel(root, stage_path): sha256(stage_path),
            rel(root, serialized_path): sha256(serialized_path),
            rel(root, final_manifest_path): sha256(final_manifest_path),
            rel(root, stage_dir / "acceptance_manifest.json"): sha256(stage_dir / "acceptance_manifest.json"),
            rel(root, eval_list_path): sha256(eval_list_path),
            rel(root, provenance_path): sha256(provenance_path),
        },
    }
    return manifest, {"main": comparisons, "main_serialized_full_ssim": serialized_comparisons}, errors


def audit_mv(root: Path) -> tuple[dict, list[str]]:
    mv_root = root / "final/round2/mv_adapter"
    unified_path = mv_root / "MV_ADAPTER_UNIFIED_RESULTS.csv"
    unified = read_csv(unified_path)
    errors: list[str] = []
    required_unified = {"method", "object_count", *MV_REQUIRED_METRICS}
    if unified and not required_unified.issubset(unified[0]):
        errors.append(f"MV unified table missing {sorted(required_unified - set(unified[0]))}")
    for row in unified:
        if row.get("object_count") != "76":
            errors.append(f"MV method {row.get('method')} has object_count={row.get('object_count')}")
        for metric in MV_REQUIRED_METRICS:
            try:
                if not math.isfinite(float(row[metric])):
                    errors.append(f"MV unified {row.get('method')}/{metric} non-finite")
            except (KeyError, ValueError):
                errors.append(f"MV unified {row.get('method')}/{metric} invalid")

    result_specs = {
        "historical_exact_holdout": (mv_root / "results/holdout_exact_76/per_object_metrics.csv", None),
        "direct_lhl_shape_transfer": (mv_root / "results/holdout_exact_lhl_shape_transfer_76/per_object_metrics.csv", "LHL"),
        "matched_range_follow_up": (mv_root / "results/holdout_exact_matched_range_76/per_object_metrics.csv", None),
        "equal_budget_follow_up": (mv_root / "results/holdout_exact_equal_budget_76/equal_budget_per_object_metrics.csv", None),
    }
    checks = {}
    for label, (path, _) in result_specs.items():
        rows = read_csv(path)
        objects = sorted({row["object"] for row in rows})
        finite = finite_check(rows, MV_REQUIRED_METRICS)
        geometry = Counter(row.get("geometry_source", "") for row in rows)
        if len(objects) != 76:
            errors.append(f"{label}: object count={len(objects)}")
        if any(value != "exact_mesh" for value in geometry):
            errors.append(f"{label}: non-exact geometry sources={dict(geometry)}")
        if not finite["passed"]:
            errors.append(f"{label}: non-finite/missing metrics")
        checks[label] = {
            "path": rel(root, path),
            "rows": len(rows),
            "objects": len(objects),
            "geometry_source_counts": dict(geometry),
            "finite_checks": finite,
            "schedules": sorted({row["schedule"] for row in rows}),
        }

    for label, path in (
        ("calibration_exact_24", mv_root / "results/calibration_exact_24/per_object_metrics.csv"),
        ("calibration_exact_selected_pair_24", mv_root / "results/calibration_exact_selected_pair_24/per_object_metrics.csv"),
    ):
        rows = read_csv(path)
        geometry = Counter(row.get("geometry_source", "") for row in rows)
        finite = finite_check(rows, MV_REQUIRED_METRICS)
        expected = 288 if label == "calibration_exact_24" else 192
        if len(rows) != expected or len({row["object"] for row in rows}) != 24:
            errors.append(f"{label}: rows/objects do not match expected {expected}/24")
        if geometry != Counter({"exact_mesh": len(rows)}):
            errors.append(f"{label}: geometry sources={dict(geometry)}")
        if not finite["passed"]:
            errors.append(f"{label}: non-finite/missing metrics")
        checks[label] = {
            "path": rel(root, path),
            "rows": len(rows),
            "objects": len({row["object"] for row in rows}),
            "geometry_source_counts": dict(geometry),
            "finite_checks": finite,
            "schedules": sorted({row["schedule"] for row in rows}),
        }

    recovery_path = mv_root / "GLB_RECOVERY_MANIFEST.json"
    recovery = json.loads(recovery_path.read_text())
    recovery_records = recovery.get("records", recovery if isinstance(recovery, list) else [])
    exact_count = sum(record.get("classification") == "Exact" for record in recovery_records)
    base_path = mv_root / "BASE_MODEL_VERIFICATION.json"
    defaults_path = mv_root / "OFFICIAL_DEFAULTS.json"
    defaults = json.loads(defaults_path.read_text())
    adapter_path = mv_root / "models/mv-adapter/mvadapter_ig2mv_sd21.safetensors"
    base = json.loads(base_path.read_text())
    code_paths = {
        "runner": mv_root / "run_experiment.py",
        "unified_generator": mv_root / "generate_unified_results.py",
        "geometry_scale": mv_root / "upstream/mvadapter/geometry_scale.py",
    }
    model_hashes = {
        "adapter": sha256(adapter_path),
        "base_text_encoder": base.get("component_sha256", {}).get("text_encoder/model.safetensors"),
        "base_unet": base.get("component_sha256", {}).get("unet/diffusion_pytorch_model.safetensors"),
        "base_vae": base.get("component_sha256", {}).get("vae/diffusion_pytorch_model.fp16.safetensors"),
    }
    return {
        "cohort": {"calibration": 24, "holdout": 76, "geometry_source": "exact_mesh"},
        "unified_results": {"path": rel(root, unified_path), "rows": len(unified), "methods": [row.get("method") for row in unified]},
        "result_checks": checks,
        "recovery": {"manifest": rel(root, recovery_path), "records": len(recovery_records), "exact_records": exact_count},
        "base_model_provenance": {
            "path": rel(root, base_path),
            "resolved_repository": base.get("resolved_repository"),
            "resolved_commit": base.get("resolved_commit"),
            "component_sha256": base.get("component_sha256", {}),
        },
        "adapter_provenance": {
            "repository": defaults.get("source", {}).get("repository"),
            "commit": defaults.get("source", {}).get("commit"),
            "path": rel(root, adapter_path),
            "sha256": model_hashes["adapter"],
        },
        "code_hashes": {label: sha256(path) for label, path in code_paths.items()},
        "model_hashes": model_hashes,
        "paired_bootstrap": rel(root, mv_root / "MV_ADAPTER_PAIRED_COMPARISONS.json"),
        "source_hashes": {
            rel(root, unified_path): sha256(unified_path),
            rel(root, recovery_path): sha256(recovery_path),
            rel(root, base_path): sha256(base_path),
            rel(root, defaults_path): sha256(defaults_path),
        },
    }, errors


def audit_pilot(
    path: Path,
    method: str,
    comparator_names: tuple[str, ...],
    bootstrap_seed_offsets: dict[str, int] | None = None,
) -> dict:
    data = json.loads(path.read_text())
    results = data.get("results", {})
    rows_by_method = {name: {row["object"]: row for row in results.get(name, [])} for name in results}
    method_rows = rows_by_method.get(method, {})
    checks = {
        "num_objects": data.get("num_objects") == 24,
        "method_rows": len(method_rows) == 24,
        "primary_metric_present": all("fg_lpips" in row and math.isfinite(float(row["fg_lpips"])) for row in method_rows.values()),
        "timing_present": all(
            all(field in row and math.isfinite(float(row[field])) for field in ("calibration_seconds", "inference_seconds", "controller_total_seconds"))
            for row in method_rows.values()
        ),
        "calibration_records": len(data.get("calibration", {}).get("per_object", [])) == 24,
        "forward_steps": data.get("calibration", {}).get("forward_steps_per_object") == 50,
    }
    comparisons = {}
    for comparator in comparator_names:
        left = method_rows
        right = rows_by_method.get(comparator, {})
        objects = sorted(set(left) & set(right))
        delta = np.asarray([float(left[obj]["fg_lpips"]) - float(right[obj]["fg_lpips"]) for obj in objects])
        comparisons[comparator] = {
            "n": len(objects),
            "mean_delta_method_minus_comparator": float(delta.mean()),
            "ci95": bootstrap_ci(delta, seed=20260929 + (bootstrap_seed_offsets or {}).get(comparator, 0)),
            "win_rate_favoring_method": float(np.mean(delta < 0.0)),
            "lower_is_better": True,
        }
    summary = data.get("summary", {}).get(method, {})
    gate = {
        "rule": "primary FG-LPIPS CI must be strictly below zero versus both fixed_low and C3_TCAS",
        "comparators": comparator_names,
        "passed": all(comparisons[name]["ci95"][1] < 0.0 for name in comparator_names if name in comparisons),
    }
    return {
        "artifact": str(path),
        "protocol": data.get("protocol"),
        "method": method,
        "checks": checks,
        "summary": summary,
        "comparisons": comparisons,
        "primary_gate": gate,
        "decision": "eligible_only_if_gate_passes" if gate["passed"] and all(checks.values()) else "do_not_promote",
        "source_sha256": sha256(path),
        "bootstrap_seed_offsets": bootstrap_seed_offsets or {},
    }


def write_protocol(root: Path) -> tuple[dict, str]:
    protocol = {
        "protocol": "c3-tcas-schedule-followup-development-v1",
        "status": "protocol_frozen_before_new_inference",
        "purpose": "development-only inference-time schedule screening after the existing C3 baseline audit",
        "scope": {
            "cohort": "clean-v2 probe 24",
            "object_list": "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt",
            "object_count": 24,
            "holdouts_locked": ["clean-v2 strict 276", "MV-Adapter Exact 76"],
        },
        "invariants": {
            "checkpoint": "existing controlled clean-v2 checkpoint; no retraining",
            "data": "unchanged clean-v2 data and unique6 views",
            "seed": 42,
            "steps": 50,
            "primary_metric": "fg_lpips",
            "primary_direction": "lower_is_better",
            "secondary_metrics": ["psnr", "fg_ssim", "edge_ssim", "fg_mae"],
            "bootstrap": {"unit": "object", "resamples": 10000, "seed": 20260929, "confidence": 0.95},
        },
        "conditions_fixed_before_run": {
            "baselines": ["fixed_low", "C3_TCAS", "HLL_eq", "LLH_eq"],
            "new_schedule_family": [
                {
                    "name": "LLH_ramp_eq",
                    "definition": "fixed-low for first 33 steps; linear ramp from 1.25 to 3.6029411764705883 over final 17 steps",
                    "nominal_scale_sum": 82.5,
                    "purpose": "test whether a smooth late high avoids the abrupt LLH transition while preserving nominal budget",
                },
                {
                    "name": "LLH_cosine_eq",
                    "definition": "fixed-low until the final third; cosine half-ramp from 1.25 with peak 3.6029411764705883 over final 17 steps",
                    "nominal_scale_sum": 82.5,
                    "purpose": "test a smooth late-peaked schedule at the same nominal scale budget",
                },
            ],
        },
        "promotion_gate": {
            "no_holdout_access": True,
            "primary": "new schedule must have paired 95% FG-LPIPS CI strictly below zero versus both C3_TCAS and fixed_low",
            "guardrails": "report PSNR, FG-SSIM, Edge-SSIM and FG-MAE; any unfavorable guardrail is retained and not hidden",
            "failure_action": "do_not_promote; do not run strict 276 or Exact 76 for this candidate",
            "interpretation": "development screening only; passing does not create a CAI winner or a cross-backbone claim",
        },
        "provenance": {
            "controller_implementation": "/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py",
            "controller_sha256": sha256(Path("/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py")),
            "main_worktree_policy": "do not modify the frozen main-adapter or MV-Adapter artifacts",
        },
    }
    markdown = "\n".join([
        "# C3/TCAS schedule follow-up protocol",
        "",
        "Status: **frozen before new inference; development-only**.",
        "",
        "This protocol is separate from the frozen CAI calibration and does not authorize a 276-object or Exact-76 holdout run.",
        "",
        "## Fixed conditions",
        "",
        "- Cohort: clean-v2 probe 24, unique6, seed 42, 50 steps.",
        "- Baselines: `fixed_low`, `C3_TCAS`, `HLL_eq`, `LLH_eq`.",
        "- Primary metric: FG-LPIPS, lower is better.",
        "- Secondary metrics: PSNR, FG-SSIM, Edge-SSIM and FG-MAE.",
        "- Statistics: object-level paired bootstrap, 10,000 resamples, seed 20260929.",
        "",
        "## New schedule family",
        "",
        "- `LLH_ramp_eq`: fixed-low for 33 steps, then a linear 17-step ramp from 1.25 to 3.6029411764705883.",
        "- `LLH_cosine_eq`: fixed-low through the first two thirds, then a cosine half-ramp with the same peak and nominal scale sum.",
        "- Both schedules have nominal scale sum 82.5, matching the existing equal-budget pilot conditions.",
        "",
        "## Gate",
        "",
        "A candidate is eligible for later validation only if its FG-LPIPS paired 95% CI is strictly below zero against both C3 and fixed-low. All secondary regressions remain reportable. A failure stops promotion and does not authorize holdout inference.",
        "",
        "This is schedule-only exploratory screening. It does not alter checkpoints, datasets, metrics, frozen CAI rules, or manuscript files.",
        "",
    ])
    return protocol, markdown


def render_report(root: Path, manifest: dict, stats: dict, pilot: dict, protocol: dict, errors: list[str]) -> str:
    main = manifest["main_adapter"]
    mv = manifest["mv_adapter"]
    lines = [
        "# C3/TCAS full baseline audit",
        "",
        "Date: 2026-09-29 UTC",
        "",
        "## Decision",
        "",
        "The existing C3 evidence is frozen as the complete baseline available in this workspace. No C3 inference was repeated and no frozen result was overwritten. The main-adapter 276-object evidence and MV-Adapter Exact-76 evidence remain separate.",
        "",
        f"Audit errors: **{len(errors)}**.",
        "",
        "## Main adapter: clean-v2 strict 276",
        "",
        f"- Records: `{main['rows']}` = `{main['objects']} objects × 4 schedules`.",
        f"- Schedules: `{', '.join(main['schedules'])}`.",
        f"- Formal stage metrics finite: **{main['finite_checks']['formal_stage']['passed']}**.",
        f"- Serialized Full-SSIM metrics finite: **{main['finite_checks']['serialized_full_ssim']['passed']}**.",
        f"- Local verified original GLBs represented in the strict-276 provenance join: `{main['local_exact_glb_count']}/{main['objects']}`.",
        "- CIEDE2000 and GT-relative texture error are not fields in this main-adapter stage CSV; they are not inferred from other metrics.",
        "- The main cohort is therefore labelled clean-v2 source-stratified, not all-Exact-Mesh.",
        "",
        "### Main paired comparisons",
        "",
        "All deltas are C3/LHL minus comparator; lower-is-better metrics use a direction-aware win rate.",
        "",
        "| comparator | metric | mean delta | 95% CI | win rate |",
        "|---|---|---:|---|---:|",
    ]
    for comp, values in stats["main"].items():
        for metric, value in values.items():
            lines.append(f"| {comp.replace('c3_lhl_minus_', '')} | {metric} | {value['mean_raw_delta_left_minus_right']:+.6f} | [{value['ci95_raw_delta'][0]:+.6f}, {value['ci95_raw_delta'][1]:+.6f}] | {value['win_rate_favoring_left']:.1%} |")
    lines += [
        "",
        "Serialized Full-SSIM is kept as a separate saved-artifact branch; it is not mixed with the formal pre-save metric column.",
        "",
        "| comparator | saved-artifact Full-SSIM mean delta | 95% CI | win rate |",
        "|---|---:|---|---:|",
    ]
    for comp, values in stats["main_serialized_full_ssim"].items():
        value = values["full_ssim"]
        lines.append(f"| {comp.replace('c3_lhl_minus_', '')} | {value['mean_raw_delta_left_minus_right']:+.6f} | [{value['ci95_raw_delta'][0]:+.6f}, {value['ci95_raw_delta'][1]:+.6f}] | {value['win_rate_favoring_left']:.1%} |")
    lines += [
        "",
        "## MV-Adapter: Exact 76",
        "",
        f"- Unified rows: `{mv['unified_results']['rows']}` methods, each with 76 Exact objects and six requested metrics.",
        f"- Exact calibration/holdout checks: `{', '.join(sorted(mv['result_checks']))}`.",
        f"- Recovered GLB records in the manifest: `{mv['recovery']['exact_records']}/{mv['recovery']['records']}` Exact.",
        "- Detailed paired bootstrap remains in `final/round2/mv_adapter/MV_ADAPTER_PAIRED_COMPARISONS.json`.",
        "- CAI remains undefined/set-valued; no C3/LHL holdout result is renamed CAI-calibrated.",
        "",
        "## 24-object pilot gate",
        "",
    ]
    for name, result in pilot.items():
        gate = result["primary_gate"]
        lines += [
            f"### {name}",
            "",
            f"- Integrity checks: `{all(result['checks'].values())}`; FG-LPIPS present: `{result['checks']['primary_metric_present']}`; calibration timing present: `{result['checks']['timing_present']}`.",
            f"- Decision: **{result['decision']}**.",
            "",
            "| comparator | mean Δ FG-LPIPS | 95% CI | win rate favoring candidate |",
            "|---|---:|---|---:|",
        ]
        for comparator, value in result["comparisons"].items():
            lines.append(f"| {comparator} | {value['mean_delta_method_minus_comparator']:+.6f} | [{value['ci95'][0]:+.6f}, {value['ci95'][1]:+.6f}] | {value['win_rate_favoring_method']:.1%} |")
        lines += [
            "",
            f"- Promotion gate passed: **{gate['passed']}**. No strict-276 TRB holdout is authorized.",
            "",
        ]
    lines += [
        "## Evidence boundaries",
        "",
        "- Exact Mesh provenance is satisfied for the MV-Adapter 24/76 cohort; it is not automatically satisfied for the main clean-v2 276 stage table.",
        "- Calibration/holdout disjointness is established for MV-Adapter Exact 24/76; main 276 is a strict holdout relative to the clean-v2 probe list but not a second-bone Exact-Mesh claim.",
        "- Official MV-Adapter pretraining UID disjointness remains unknown.",
        "- Stage effects are supported by paired tables; they do not establish a unique CAI schedule or a universal cross-backbone gain.",
        "- No absolute PSNR comparison is made between the two backbones.",
        "",
        "## New schedule status",
        "",
        "The independent schedule-only development protocol is frozen in `C3_TCAS_NEW_SCHEDULE_PROTOCOL_20260929.json/.md`. It is limited to the 24-object development cohort and does not authorize holdout inference until its gate is evaluated.",
        "",
    ]
    if errors:
        lines += ["## Audit checks requiring attention", ""]
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    return "\n".join(lines)


def claim_ledger() -> str:
    return """# C3/TCAS claim ledger

| Claim | Status | Permitted wording | Not permitted |
|---|---|---|---|
| Existing C3 results are complete | `SUPPORTED` | Existing main 276 and MV-Adapter Exact 76 C3 artifacts were audited and frozen | Claiming a new C3 rerun was performed |
| Main-adapter stage-position effect | `SUPPORTED_WITH_LIMITATIONS` | Paired 276-object stage comparisons show the observed relative effects | Calling the main cohort all-Exact-Mesh or comparing absolute PSNR with MV-Adapter |
| MV-Adapter Exact stage-position effect | `SUPPORTED_WITH_LIMITATIONS` | Exact-76 paired diagnostics show measurable schedule effects | Calling LHL a CAI-calibrated winner |
| CAI selected a unique schedule | `UNDEFINED_SET_VALUED` | The frozen rule did not define a legal unique winner | Adding a favorable post-hoc tie-break |
| TRB/TRB2 improves C3 | `NOT_SUPPORTED` | Both strict 24-object pilots remain internal negative/neutral method-screening evidence | Locking a 276-object TRB holdout |
| MV-Adapter pretraining disjointness | `UNKNOWN` | Report that official training UID overlap could not be verified | Claiming pretraining disjointness from GLB recovery alone |
| New schedule follow-up | `PENDING_DEVELOPMENT_ONLY` | Use only after the frozen protocol and 24-object gate are evaluated | Selecting a candidate from 76/276 holdout results |

All claims above are bounded by the audit artifacts in this directory. The manuscript and response letter are intentionally untouched.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / "final/round2/coordination"
    out.mkdir(parents=True, exist_ok=True)

    main_manifest, stats, main_errors = audit_main(root)
    mv_manifest, mv_errors = audit_mv(root)
    original = audit_pilot(
        Path("/4T/tmp/mvpainter-adaptive-control/outputs/trb_clean_v2_dev24_seed42_lpips_r1/pilot_results.json"),
        "TRB_TCAS",
        ("fixed_low", "C3_TCAS"),
        bootstrap_seed_offsets={"fixed_low": 0, "C3_TCAS": 1000},
    )
    trb2 = audit_pilot(
        Path("/4T/tmp/mvpainter-adaptive-control/outputs/trb2_clean_v2_dev24_seed42/pilot_results.json"),
        "TRB2_TCAS",
        ("fixed_low", "C3_TCAS"),
        bootstrap_seed_offsets={"fixed_low": 0, "C3_TCAS": 0},
    )
    pilot = {"TRB_TCAS": original, "TRB2_TCAS": trb2}
    protocol, protocol_md = write_protocol(root)
    manifest = {
        "audit": "c3-tcas-full-baseline-v1",
        "generated_at": "2026-09-29T00:00:00Z",
        "execution": "read-only artifact audit; no model inference",
        "python": sys.version,
        "platform": platform.platform(),
        "main_adapter": main_manifest["main_adapter"],
        "mv_adapter": mv_manifest,
        "pilot_gate": pilot,
        "protocol": protocol,
        "source_hashes": {**main_manifest["source_hashes"], **mv_manifest["source_hashes"]},
        "audit_errors": main_errors + mv_errors,
    }
    (out / "C3_TCAS_BASELINE_MANIFEST_20260929.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (out / "C3_TCAS_PAIRED_STATISTICS_20260929.json").write_text(json.dumps(stats, indent=2) + "\n")
    (out / "STRICT_TRB_DEVELOPMENT_GATE_SUPPLEMENT_20260929.json").write_text(json.dumps(pilot, indent=2) + "\n")
    (out / "C3_TCAS_NEW_SCHEDULE_PROTOCOL_20260929.json").write_text(json.dumps(protocol, indent=2) + "\n")
    (out / "C3_TCAS_NEW_SCHEDULE_PROTOCOL_20260929.md").write_text(protocol_md)
    report = render_report(root, {"main_adapter": main_manifest["main_adapter"], "mv_adapter": mv_manifest}, stats, pilot, protocol, main_errors + mv_errors)
    (out / "C3_TCAS_FULL_BASELINE_AUDIT_20260929.md").write_text(report)
    (out / "C3_TCAS_CLAIM_LEDGER_20260929.md").write_text(claim_ledger())
    print(json.dumps({
        "main_errors": main_errors,
        "mv_errors": mv_errors,
        "pilot_decisions": {name: value["decision"] for name, value in pilot.items()},
        "output_dir": str(out),
    }, indent=2))


if __name__ == "__main__":
    main()
