#!/usr/bin/env python3
"""Gate and analyze the pre-output Fresh C LLH/linear comparison addendum."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import ttest_rel

from fresh_c_input_embedding_gate import load_verified_input_embeddings

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
RUN = DATA / "runs/revision_era_addendum"
PRIMARY_RUN = DATA / "runs/c3_confirmation"
LOCK = ROOT / "1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.json"
CONDITIONS = {"layer_llh", "gen_linear"}
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
METRICS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")
PRIMARY_METRICS = ("fg_psnr", "fg_lpips")
HIGHER_IS_BETTER = {"fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim"}
CONTRASTS = (
    ("LLH-C3", "layer_llh", "native_gc3"),
    ("LLH-linear", "layer_llh", "gen_linear"),
    ("C3-linear", "native_gc3", "gen_linear"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def object_ids() -> list[str]:
    return [line.strip() for line in (DATA / "fresh_c_objects.txt").read_text().splitlines() if line.strip()]


def condition_trace(condition: str) -> list[dict[str, float]]:
    lows = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
    highs = {"deep": 2.50, "middle": 2.50, "shallow": 0.75}
    stages = {
        "deep": (1.25, 1.25, 2.50),
        "middle": (1.25, 1.25, 2.50),
        "shallow": (0.50, 0.50, 0.75),
    }
    trace = []
    for step in range(50):
        progress = step / 49
        if condition == "layer_llh":
            stage = 0 if progress < 1 / 3 else 1 if progress < 2 / 3 else 2
            trace.append({group: float(stages[group][stage]) for group in lows})
        elif condition == "gen_linear":
            trace.append({group: float(lows[group] + progress * (highs[group] - lows[group])) for group in lows})
        else:
            raise ValueError(condition)
    return trace


def holm_adjust(p_values: list[float]) -> list[float]:
    if not p_values or not all(math.isfinite(p) and 0 <= p <= 1 for p in p_values):
        raise ValueError("Holm adjustment requires finite p-values in [0,1]")
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=np.float64)
    running = 0.0
    size = len(p_values)
    for rank, index in enumerate(order):
        running = max(running, (size - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def paired_ttest(a: np.ndarray, b: np.ndarray) -> tuple[float | None, float]:
    delta = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    if len(delta) < 2 or not np.isfinite(delta).all():
        raise ValueError("paired t-test requires at least two finite paired values")
    if float(delta.std(ddof=1)) == 0.0:
        return (None, 1.0 if float(delta.mean()) == 0.0 else 0.0)
    result = ttest_rel(a, b, alternative="two-sided", nan_policy="raise")
    return float(result.statistic), float(result.pvalue)


def bootstrap_summary(delta: np.ndarray, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    n = len(delta)
    means = np.empty(10_000, dtype=np.float64)
    for start in range(0, len(means), 500):
        stop = min(start + 500, len(means))
        indices = rng.integers(0, n, size=(stop - start, n))
        means[start:stop] = delta[indices].mean(axis=1)
    ci = np.quantile(means, [0.025, 0.975], method="linear")
    return {
        "mean": float(delta.mean()), "median": float(np.median(delta)),
        "sd": float(delta.std(ddof=1)), "bootstrap_ci95": [float(ci[0]), float(ci[1])],
        "bootstrap_draws": 10_000, "bootstrap_seed": seed,
        "positive_fraction": float(np.mean(delta > 0)),
        "negative_fraction": float(np.mean(delta < 0)),
        "tie_fraction": float(np.mean(delta == 0)),
    }


def raw_rows(run_dir: Path, shard_count: int = 2) -> list[dict[str, Any]]:
    rows = []
    for shard in range(shard_count):
        path = run_dir / f"rows_shard{shard}.json"
        if not path.is_file():
            raise RuntimeError(f"missing raw shard ledger: {path}")
        rows.extend(json.loads(path.read_text()))
    return rows


def integrity_gate() -> dict[str, Any]:
    lock = json.loads(LOCK.read_text())
    embedding_manifest, embedding_manifest_hash = load_verified_input_embeddings()
    amendment = json.loads((ROOT / "1006/evidence/protocols/FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_20261006.json").read_text())
    primary_gate_path = DATA / "FRESH_C_INTEGRITY_GATE.json"
    if not primary_gate_path.is_file() or json.loads(primary_gate_path.read_text()).get("status") != "PASS":
        raise RuntimeError("primary Fresh C integrity gate must pass before addendum audit")
    launch = json.loads((RUN / "LAUNCH_IDENTITY.json").read_text())
    primary_launch = json.loads((PRIMARY_RUN / "LAUNCH_IDENTITY.json").read_text())
    cohort_path = DATA / "FRESH_C_COHORT_MANIFEST.json"
    cohort = json.loads(cohort_path.read_text())
    uids = object_ids()
    if len(uids) != cohort.get("selected_count") or len(set(uids)) != len(uids):
        raise RuntimeError("frozen cohort count/UID uniqueness failed")
    if launch.get("cohort_n") != len(uids) or launch.get("cohort_uid_list_sha256") != sha256(DATA / "fresh_c_objects.txt"):
        raise RuntimeError("addendum launch does not match the frozen UID list")
    if launch.get("cohort_manifest_sha256") != sha256(cohort_path):
        raise RuntimeError("addendum launch does not match the frozen cohort manifest")
    if launch.get("cohort_manifest_sha256") != primary_launch.get("cohort_manifest_sha256"):
        raise RuntimeError("primary and addendum cohort manifests differ")
    if launch.get("cohort_uid_list_sha256") != primary_launch.get("cohort_uid_list_sha256"):
        raise RuntimeError("primary and addendum UID lists differ")
    if launch.get("input_embeddings_manifest_sha256") != embedding_manifest_hash:
        raise RuntimeError("addendum launch does not match the frozen embedding manifest")
    if primary_launch.get("input_embeddings_manifest_sha256") != embedding_manifest_hash:
        raise RuntimeError("primary and addendum launch embedding identities differ")
    if launch.get("source_hashes") != lock.get("source_hashes"):
        raise RuntimeError("source hashes differ from the frozen addendum lock")
    if launch.get("protocol_lock_sha256") != sha256(LOCK):
        raise RuntimeError("launch used a different machine-readable addendum lock")
    if launch.get("protocol_markdown_sha256") != sha256(LOCK.with_suffix(".md")):
        raise RuntimeError("launch used a different addendum protocol document")
    if sha256(ROOT / "1006/evidence/protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md") != lock.get("original_protocol_sha256"):
        raise RuntimeError("original Fresh C protocol changed after the addendum lock")
    if sha256(DATA / "CANDIDATE_QUEUE_LOCK.json") != lock.get("candidate_queue_lock_sha256"):
        raise RuntimeError("frozen Fresh C candidate queue changed after the addendum lock")
    if launch.get("primary_integrity_gate_sha256") != sha256(primary_gate_path):
        raise RuntimeError("primary integrity gate changed after addendum launch")
    if amendment.get("original_addendum_lock_sha256") != sha256(LOCK):
        raise RuntimeError("embedding amendment does not bind the unchanged addendum lock")
    if amendment.get("original_addendum_orchestration_hashes") != lock.get("orchestration_hashes"):
        raise RuntimeError("embedding amendment does not preserve original orchestration hashes")
    if set(launch.get("conditions", [])) != CONDITIONS:
        raise RuntimeError("addendum condition list differs from the frozen two-condition set")
    expected_embedding_tensors = {
        row["uid"]: row["embedding_tensor_sha256"] for row in embedding_manifest["objects"]
    }

    primary_rows = raw_rows(PRIMARY_RUN)
    primary_by_uid = {}
    for row in primary_rows:
        if row.get("condition") == "native_gc3":
            uid = str(row.get("object_uid") or row.get("object"))
            if uid in primary_by_uid:
                raise RuntimeError(f"duplicate primary GC3 row for {uid}")
            primary_by_uid[uid] = row
    if set(primary_by_uid) != set(uids):
        raise RuntimeError("primary native_gc3 rows do not cover the frozen object list")

    errors: list[str] = []
    seen: dict[tuple[int, str], dict[str, Any]] = {}
    rows = []
    for shard in (0, 1):
        manifest_path = RUN / f"run_manifest_shard{shard}.json"
        if not manifest_path.is_file():
            errors.append(f"missing shard manifest {shard}")
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("status") != "complete":
            errors.append(f"shard {shard} is incomplete")
        if set(manifest.get("conditions", [])) != CONDITIONS:
            errors.append(f"shard {shard} condition registry mismatch")
        if manifest.get("checkpoint_sha256") != lock["source_hashes"]["checkpoint"]:
            errors.append(f"shard {shard} checkpoint hash mismatch")
        if manifest.get("config_sha256") != lock["source_hashes"]["config"]:
            errors.append(f"shard {shard} config hash mismatch")
        if manifest.get("object_list_sha256") != launch["cohort_uid_list_sha256"]:
            errors.append(f"shard {shard} object-list hash mismatch")
        shard_path = RUN / f"rows_shard{shard}.json"
        if not shard_path.is_file():
            errors.append(f"missing raw shard ledger {shard}")
            continue
        shard_rows = json.loads(shard_path.read_text())
        if manifest.get("row_count") != len(shard_rows):
            errors.append(f"shard {shard} raw row count mismatch")
        for shard_row in shard_rows:
            if int(shard_row.get("object_idx", -1)) % 2 != shard:
                errors.append(f"wrong object shard assignment in shard {shard}")
        rows.extend(shard_rows)
        sources = manifest.get("code_source_sha256", {})
        for key in ("runner", "adapter_wrapper", "data_utils", "generation_logic", "metric_implementation"):
            if sources.get(key, {}).get("sha256") != lock["source_hashes"][key]:
                errors.append(f"shard {shard} source hash mismatch: {key}")
        specs = manifest.get("condition_specs", {})
        if set(specs) != CONDITIONS:
            errors.append(f"shard {shard} scale registry mismatch")
        else:
            for condition in sorted(CONDITIONS):
                spec = specs[condition]
                expected_trace = condition_trace(condition)
                if spec.get("uncapped") is not False:
                    errors.append(f"unexpected cap bypass in {condition}")
                if spec.get("scale_trace_requested") != expected_trace:
                    errors.append(f"requested scale trace mismatch in {condition}")

    id_map = dict(enumerate(uids))
    hashes_by_uid: dict[str, dict[str, str]] = {}
    for row in rows:
        try:
            index = int(row["object_idx"])
            uid = str(row.get("object_uid") or row.get("object"))
            condition = str(row["condition"])
            key = (index, condition)
            if key in seen:
                errors.append(f"duplicate object-condition key {key}")
                continue
            seen[key] = row
            if condition not in CONDITIONS:
                errors.append(f"unexpected condition {condition}")
            if index not in id_map or id_map[index] != uid:
                errors.append(f"object index/UID mismatch {index}/{uid}")
            if index % 2 != int(row.get("shard", index % 2)) and row.get("shard") is not None:
                errors.append(f"unexpected row shard at {uid}/{condition}")
            if row.get("uncapped") is not False or int(row.get("seed_base", -1)) != 42:
                errors.append(f"cap/seed mismatch at {uid}/{condition}")
            for metric in METRICS:
                if not math.isfinite(float(row[metric])):
                    errors.append(f"non-finite {metric} at {uid}/{condition}")
            hashes = row.get("input_hashes")
            if not isinstance(hashes, dict) or set(hashes) != {"cond", "target", "normal", "depth", "global_embeds", "init_latent"}:
                errors.append(f"malformed shared-input hash set at {uid}/{condition}")
            else:
                if hashes != primary_by_uid[uid].get("input_hashes"):
                    errors.append(f"addendum shared-input hashes differ from primary GC3 at {uid}/{condition}")
                if hashes.get("global_embeds") != expected_embedding_tensors.get(uid):
                    errors.append(f"addendum input embedding tensor hash mismatch at {uid}/{condition}")
                previous = hashes_by_uid.setdefault(uid, hashes)
                if hashes != previous:
                    errors.append(f"addendum input hashes differ across methods for {uid}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"malformed addendum row: {type(exc).__name__}: {str(exc)[:160]}")

    expected_keys = {(index, condition) for index in range(len(uids)) for condition in CONDITIONS}
    if set(seen) != expected_keys:
        errors.append(f"key coverage mismatch: missing={len(expected_keys-set(seen))}, extra={len(set(seen)-expected_keys)}")
    if len(rows) != 2 * len(uids):
        errors.append(f"row count {len(rows)} != expected {2*len(uids)}")

    output_hashes = []
    manifests = [json.loads((RUN / f"run_manifest_shard{shard}.json").read_text()) for shard in (0, 1)
                 if (RUN / f"run_manifest_shard{shard}.json").is_file()]
    specs = manifests[0].get("condition_specs", {}) if manifests else {}
    for row in rows:
        uid, condition = str(row.get("object_uid") or row.get("object")), str(row["condition"])
        prediction = RUN / "predictions" / condition / f"{uid}.png"
        residual = RUN / "residual_logs" / condition / f"{uid}.json"
        if not prediction.is_file():
            errors.append(f"missing prediction {condition}/{uid}")
        else:
            output_hashes.append({"kind": "prediction", "condition": condition, "uid": uid,
                                  "path": str(prediction), "bytes": prediction.stat().st_size,
                                  "sha256": sha256(prediction)})
        if not residual.is_file():
            errors.append(f"missing residual log {condition}/{uid}")
            continue
        try:
            log = json.loads(residual.read_text())
            if set(log) != {str(step) for step in range(50)}:
                raise ValueError("residual log does not have exactly 50 steps")
            trace = specs[condition]["scale_trace_requested"]
            for step in range(50):
                entries = log[str(step)]
                if not isinstance(entries, dict) or not entries:
                    raise ValueError(f"empty residual record at step {step}")
                for entry in entries.values():
                    group = entry.get("depth")
                    if group not in CAPS:
                        raise ValueError(f"unknown depth group {group}")
                    requested, effective = float(entry["scale"]), float(entry["eff_scale"])
                    if requested != float(trace[step][group]):
                        raise ValueError(f"requested scale mismatch at {step}/{group}")
                    if effective != min(requested, CAPS[group]):
                        raise ValueError(f"effective cap mismatch at {step}/{group}")
                    if not all(math.isfinite(float(v)) for v in entry.values() if isinstance(v, (int, float))):
                        raise ValueError("non-finite residual diagnostic")
            output_hashes.append({"kind": "residual_log", "condition": condition, "uid": uid,
                                  "path": str(residual), "bytes": residual.stat().st_size,
                                  "sha256": sha256(residual)})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"residual trace audit failed {condition}/{uid}: {exc}")

    if errors:
        gate = {"status": "FAIL", "errors": errors[:200], "error_count": len(errors),
                "verified_rows": len(rows), "expected_rows": 2 * len(uids)}
        (DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json").write_text(json.dumps(gate, indent=2) + "\n")
        raise RuntimeError(json.dumps(gate, indent=2))

    combined_path = RUN / "per_object_metrics.csv"
    flat = []
    for row in sorted(rows, key=lambda r: (int(r["object_idx"]), str(r["condition"]))):
        item = {key: row.get(key) for key in ("object_uid", "object_idx", "condition", "uncapped", "seed_base", "elapsed_seconds")}
        item.update({metric: float(row[metric]) for metric in METRICS})
        item.update({f"input_{key}_sha256": value for key, value in row["input_hashes"].items()})
        flat.append(item)
    with combined_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)
    hash_path = RUN / "OUTPUT_FILE_SHA256.csv"
    with hash_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "condition", "uid", "path", "bytes", "sha256"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_hashes)
    gate = {
        "status": "PASS", "cohort_n": len(uids), "conditions": sorted(CONDITIONS),
        "expected_rows": 2 * len(uids), "verified_rows": len(rows),
        "shared_input_objects": len(hashes_by_uid), "verified_output_files": len(output_hashes),
        "cohort_manifest_sha256": sha256(cohort_path),
        "input_embeddings_manifest_sha256": embedding_manifest_hash,
        "primary_integrity_gate_sha256": sha256(primary_gate_path),
        "combined_csv_sha256": sha256(combined_path),
        "output_hash_manifest_sha256": sha256(hash_path),
        "status_reason": "same-cohort identity, complete rows, shared inputs, finite metrics, native caps, predictions, and residual logs passed",
    }
    gate_path = DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"
    gate_path.write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))
    return gate


def analyze() -> dict[str, Any]:
    gate_path = DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"
    primary_gate = DATA / "FRESH_C_INTEGRITY_GATE.json"
    if not gate_path.is_file() or json.loads(gate_path.read_text()).get("status") != "PASS":
        raise RuntimeError("addendum integrity gate must pass before analysis")
    if not primary_gate.is_file() or json.loads(primary_gate.read_text()).get("status") != "PASS":
        raise RuntimeError("primary Fresh C integrity gate must pass before analysis")

    raw_primary = raw_rows(PRIMARY_RUN)
    raw_addendum = raw_rows(RUN)
    by_key = {}
    for row in raw_primary + raw_addendum:
        uid = str(row.get("object_uid") or row.get("object"))
        key = (uid, str(row["condition"]))
        if key in by_key:
            raise RuntimeError(f"duplicate condition row across Fresh C namespaces: {key}")
        by_key[key] = row
    uids = object_ids()
    family_results: list[dict[str, Any]] = []
    delta_rows = []
    for name, first, second in CONTRASTS:
        for uid in uids:
            left, right = by_key[(uid, first)], by_key[(uid, second)]
            row = {"object_uid": uid, "contrast": name}
            for metric in METRICS:
                row[metric] = float(left[metric]) - float(right[metric])
            delta_rows.append(row)
        for metric in METRICS:
            delta = np.asarray([by_key[(uid, first)][metric] for uid in uids], dtype=np.float64) - np.asarray(
                [by_key[(uid, second)][metric] for uid in uids], dtype=np.float64)
            result = bootstrap_summary(delta, 20261007)
            paired_a = np.asarray([float(by_key[(uid, first)][metric]) for uid in uids])
            paired_b = np.asarray([float(by_key[(uid, second)][metric]) for uid in uids])
            paired_statistic, paired_p = paired_ttest(paired_a, paired_b)
            result.update({
                "contrast": name, "condition_a": first, "condition_b": second,
                "metric": metric, "paired_t_statistic": paired_statistic,
                "paired_t_p_raw": paired_p,
                "favorable_direction_for_a": "higher" if metric in HIGHER_IS_BETTER else "lower",
                "favorable_object_fraction_for_a": result["positive_fraction"] if metric in HIGHER_IS_BETTER else result["negative_fraction"],
                "inferential_unit": "object",
            })
            family_results.append(result)

    primary_family = [r for r in family_results if r["metric"] in PRIMARY_METRICS]
    secondary_family = [r for r in family_results if r["metric"] not in PRIMARY_METRICS]
    if len(primary_family) != 6 or len(secondary_family) != 15:
        raise RuntimeError("multiplicity-family construction failed")
    for result, adjusted in zip(primary_family, holm_adjust([r["paired_t_p_raw"] for r in primary_family])):
        result["holm_adjusted_p"] = adjusted
        result["multiplicity_family"] = "six primary endpoint-contrast tests"
    for result, adjusted in zip(secondary_family, holm_adjust([r["paired_t_p_raw"] for r in secondary_family])):
        result["holm_adjusted_p"] = adjusted
        result["multiplicity_family"] = "15 secondary Core-7 endpoint-contrast tests"

    output = {
        "cohort": "FRESH_C_REVISION_ERA_LLH_LINEAR_ADDENDUM",
        "n_objects": len(uids), "contrasts": [
            {"name": name, "a": first, "b": second, "delta": "A minus B"}
            for name, first, second in CONTRASTS
        ],
        "primary_family": [f"{r['contrast']}:{r['metric']}" for r in primary_family],
        "secondary_family": [f"{r['contrast']}:{r['metric']}" for r in secondary_family],
        "integrity_gate_sha256": sha256(gate_path),
        "primary_integrity_gate_sha256": sha256(primary_gate),
        "delta_convention": "condition A minus condition B",
        "bootstrap": {"unit": "object", "draws": 10000, "seed": 20261007,
                      "interval": "two-sided percentile 95%"},
        "tests": family_results,
        "equivalence_claim_allowed": False,
    }
    out_json = DATA / "FRESH_C_ADDENDUM_ANALYSIS.json"
    out_json.write_text(json.dumps(output, indent=2) + "\n")
    delta_path = DATA / "fresh_c_addendum_object_deltas.csv"
    with delta_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["object_uid", "contrast", *METRICS], lineterminator="\n")
        writer.writeheader()
        writer.writerows(delta_rows)
    print(json.dumps(output, indent=2))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("integrity", "analyze"))
    args = parser.parse_args()
    if args.command == "integrity":
        integrity_gate()
    else:
        analyze()


if __name__ == "__main__":
    main()
