#!/usr/bin/env python3
"""Integrity-gate and analyze the frozen Fresh C3-versus-GFL follow-up."""
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

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
RUN = DATA / "runs/c3_confirmation"
EXPECTED_CONDITIONS = {"no_adapter", "native_gfl", "native_gfh", "native_gc3"}
METRICS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")
HIGHER_IS_BETTER = {"fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim"}
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
EXPECTED_HASHES = {
    "runner": "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3",
    "adapter_wrapper": "b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0",
    "data_utils": "e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3",
    "generation_logic": "5da7fff22ea73b6d9500603d0905eda9a1ac9c44406346b259f3aba368b6ca13",
    "metric_implementation": "adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5",
    "checkpoint": "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0",
    "config": "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def object_ids() -> list[str]:
    return [x.strip() for x in (DATA / "fresh_c_objects.txt").read_text().splitlines() if x.strip()]


def canonical_metrics(row: dict[str, Any]) -> dict[str, float]:
    out = {}
    for metric in METRICS:
        value = float(row[metric])
        if not math.isfinite(value):
            raise ValueError(f"non-finite metric {metric}: {value}")
        out[metric] = value
    return out


def write_combined_csv(rows: list[dict[str, Any]], path: Path) -> None:
    flat = []
    for row in rows:
        item = {k: row.get(k) for k in (
            "object_uid", "object_idx", "condition", "uncapped", "seed_base", "elapsed_seconds")}
        item.update(canonical_metrics(row))
        for key, value in (row.get("input_hashes") or {}).items():
            item[f"input_{key}_sha256"] = value
        flat.append(item)
    fields = list(flat[0]) if flat else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)


def integrity_gate() -> dict[str, Any]:
    cohort_manifest = json.loads((DATA / "FRESH_C_COHORT_MANIFEST.json").read_text())
    launch = json.loads((RUN / "LAUNCH_IDENTITY.json").read_text())
    uids = object_ids()
    if len(uids) != cohort_manifest["selected_count"] or len(set(uids)) != len(uids):
        raise RuntimeError("cohort list count or UID uniqueness failed")
    if launch["cohort_n"] != len(uids) or launch["cohort_uid_list_sha256"] != sha256(DATA / "fresh_c_objects.txt"):
        raise RuntimeError("launch identity does not match the frozen cohort")
    if launch["source_hashes"] != EXPECTED_HASHES:
        raise RuntimeError("launch source hashes differ from the frozen expected identities")

    all_rows: list[dict[str, Any]] = []
    seen: dict[tuple[int, str], dict[str, Any]] = {}
    input_by_uid: dict[str, dict[str, str]] = {}
    rows_by_shard: dict[int, int] = {}
    expected_idx_uid = dict(enumerate(uids))
    errors: list[str] = []

    for shard in (0, 1):
        manifest_path = RUN / f"run_manifest_shard{shard}.json"
        if not manifest_path.is_file():
            errors.append(f"missing shard manifest {shard}")
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("status") != "complete":
            errors.append(f"shard {shard} status is {manifest.get('status')}")
        if manifest.get("conditions") is None or set(manifest["conditions"]) != EXPECTED_CONDITIONS:
            errors.append(f"shard {shard} condition registry mismatch")
        if manifest.get("checkpoint_sha256") != EXPECTED_HASHES["checkpoint"]:
            errors.append(f"shard {shard} checkpoint hash mismatch")
        if manifest.get("config_sha256") != EXPECTED_HASHES["config"]:
            errors.append(f"shard {shard} config hash mismatch")
        if manifest.get("object_list_sha256") != launch["cohort_uid_list_sha256"]:
            errors.append(f"shard {shard} object list hash mismatch")
        sources = manifest.get("code_source_sha256", {})
        for key, digest in EXPECTED_HASHES.items():
            if key in {"checkpoint", "config"}:
                continue
            if sources.get(key, {}).get("sha256") != digest:
                errors.append(f"shard {shard} code hash mismatch: {key}")
        specs = manifest.get("condition_specs", {})
        if set(specs) != EXPECTED_CONDITIONS:
            errors.append(f"shard {shard} condition scale registry mismatch")
        else:
            for condition, spec in specs.items():
                if spec.get("uncapped") is not False:
                    errors.append(f"unexpected cap bypass in {condition}")
                trace = spec.get("scale_trace_requested")
                if not isinstance(trace, list) or len(trace) != 50:
                    errors.append(f"invalid requested-scale trace for {condition}")

        rows_path = RUN / f"rows_shard{shard}.json"
        if not rows_path.is_file():
            errors.append(f"missing raw ledger for shard {shard}")
            continue
        shard_rows = json.loads(rows_path.read_text())
        rows_by_shard[shard] = len(shard_rows)
        if manifest.get("row_count") != len(shard_rows):
            errors.append(f"shard {shard} raw-ledger row count mismatch")
        for row in shard_rows:
            try:
                idx = int(row["object_idx"])
                condition = str(row["condition"])
                uid = str(row.get("object_uid") or row.get("object"))
                key = (idx, condition)
                if key in seen:
                    errors.append(f"duplicate object-condition key {key}")
                    continue
                seen[key] = row
                if idx not in expected_idx_uid or uid != expected_idx_uid[idx]:
                    errors.append(f"object index/UID mismatch {idx}/{uid}")
                if idx % 2 != shard:
                    errors.append(f"wrong shard assignment for {idx}/{condition}")
                if condition not in EXPECTED_CONDITIONS:
                    errors.append(f"unexpected condition {condition}")
                if row.get("uncapped") is not False or int(row.get("seed_base", -1)) != 42:
                    errors.append(f"cap or seed flag mismatch at {uid}/{condition}")
                canonical_metrics(row)
                hashes = row.get("input_hashes")
                if not isinstance(hashes, dict) or set(hashes) != {
                    "cond", "target", "normal", "depth", "global_embeds", "init_latent"
                }:
                    errors.append(f"malformed shared-input hash set at {uid}/{condition}")
                else:
                    prior = input_by_uid.setdefault(uid, hashes)
                    if hashes != prior:
                        errors.append(f"shared-input identity mismatch across conditions for {uid}")
                all_rows.append(row)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"malformed raw row: {type(exc).__name__}: {str(exc)[:160]}")

    expected_keys = {(idx, cond) for idx in range(len(uids)) for cond in EXPECTED_CONDITIONS}
    missing = expected_keys - set(seen)
    unexpected = set(seen) - expected_keys
    if missing or unexpected:
        errors.append(f"key coverage mismatch: missing={len(missing)}, unexpected={len(unexpected)}")
    if len(all_rows) != len(uids) * len(EXPECTED_CONDITIONS):
        errors.append(f"total row count {len(all_rows)} != {len(uids) * 4}")

    # Validate each complete native residual trace against the exact per-step
    # requested scale and frozen depth-group cap.
    output_hash_rows = []
    for row in all_rows:
        uid, condition = str(row.get("object_uid") or row.get("object")), row["condition"]
        pred = RUN / "predictions" / condition / f"{uid}.png"
        if not pred.is_file():
            errors.append(f"missing prediction {condition}/{uid}")
        else:
            output_hash_rows.append({"kind": "prediction", "condition": condition, "uid": uid,
                                     "path": str(pred), "bytes": pred.stat().st_size,
                                     "sha256": sha256(pred)})
        if condition == "no_adapter":
            continue
        log_path = RUN / "residual_logs" / condition / f"{uid}.json"
        if not log_path.is_file():
            errors.append(f"missing residual log {condition}/{uid}")
            continue
        try:
            log = json.loads(log_path.read_text())
            if set(log) != {str(i) for i in range(50)}:
                raise ValueError("residual log does not contain exactly 50 steps")
            trace = specs[condition]["scale_trace_requested"]
            for step in range(50):
                entries = log[str(step)]
                if not isinstance(entries, dict) or not entries:
                    raise ValueError(f"empty step {step}")
                for entry in entries.values():
                    group = entry.get("depth")
                    if group not in CAPS:
                        raise ValueError(f"unknown depth group {group}")
                    requested = float(entry["scale"])
                    effective = float(entry["eff_scale"])
                    if requested != float(trace[step][group]):
                        raise ValueError(f"requested scale mismatch at step {step}/{group}")
                    if effective != min(requested, CAPS[group]):
                        raise ValueError(f"post-cap scale mismatch at step {step}/{group}")
                    for value in entry.values():
                        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
                            raise ValueError("non-finite residual diagnostic")
            output_hash_rows.append({"kind": "residual_log", "condition": condition, "uid": uid,
                                     "path": str(log_path), "bytes": log_path.stat().st_size,
                                     "sha256": sha256(log_path)})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"residual trace audit failed for {condition}/{uid}: {exc}")

    if errors:
        gate = {"status": "FAIL", "errors": errors[:200], "error_count": len(errors),
                "rows": len(all_rows), "rows_by_shard": rows_by_shard}
        (DATA / "FRESH_C_INTEGRITY_GATE.json").write_text(json.dumps(gate, indent=2) + "\n")
        raise RuntimeError(json.dumps(gate, indent=2))

    all_rows.sort(key=lambda r: (int(r["object_idx"]), str(r["condition"])))
    combined_path = RUN / "per_object_metrics.csv"
    write_combined_csv(all_rows, combined_path)
    hash_path = RUN / "OUTPUT_FILE_SHA256.csv"
    with hash_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "condition", "uid", "path", "bytes", "sha256"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_hash_rows)
    gate = {
        "status": "PASS", "cohort_n": len(uids), "conditions": sorted(EXPECTED_CONDITIONS),
        "expected_rows": len(uids) * 4, "verified_rows": len(all_rows),
        "rows_by_shard": rows_by_shard, "shared_input_objects": len(input_by_uid),
        "verified_output_files": len(output_hash_rows),
        "condition_coverage": {c: sum(r["condition"] == c for r in all_rows) for c in sorted(EXPECTED_CONDITIONS)},
        "cohort_manifest_sha256": sha256(DATA / "FRESH_C_COHORT_MANIFEST.json"),
        "combined_csv_sha256": sha256(combined_path), "output_hash_manifest_sha256": sha256(hash_path),
        "status_reason": "all identity, row, shared-input, finite-metric, native-cap, prediction, and residual-log gates passed",
    }
    (DATA / "FRESH_C_INTEGRITY_GATE.json").write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))
    return gate


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=np.float64)
    running = 0.0
    m = len(p_values)
    for rank, idx in enumerate(order):
        candidate = (m - rank) * p_values[idx]
        running = max(running, candidate)
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()


def bootstrap_summary(delta: np.ndarray, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    n = len(delta)
    # Chunk the bootstrap to cap temporary memory if cohort size changes later.
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


def analyze() -> dict[str, Any]:
    gate_path = DATA / "FRESH_C_INTEGRITY_GATE.json"
    if not gate_path.is_file() or json.loads(gate_path.read_text()).get("status") != "PASS":
        raise RuntimeError("Integrity gate has not passed; refusing comparative analysis")
    with (RUN / "per_object_metrics.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    by_key = {(r["object_uid"], r["condition"]): r for r in rows}
    uids = object_ids()
    deltas: dict[str, np.ndarray] = {}
    object_rows = []
    for uid in uids:
        left = by_key[(uid, "native_gc3")]
        right = by_key[(uid, "native_gfl")]
        item: dict[str, Any] = {"object_uid": uid}
        for metric in METRICS:
            delta = float(left[metric]) - float(right[metric])
            item[metric] = delta
        object_rows.append(item)
    for metric in METRICS:
        deltas[metric] = np.asarray([r[metric] for r in object_rows], dtype=np.float64)

    tests: dict[str, dict[str, Any]] = {}
    for idx, metric in enumerate(METRICS):
        delta = deltas[metric]
        result = bootstrap_summary(delta, 20261006)
        ttest = ttest_rel(
            np.asarray([float(by_key[(uid, "native_gc3")][metric]) for uid in uids]),
            np.asarray([float(by_key[(uid, "native_gfl")][metric]) for uid in uids]),
            alternative="two-sided", nan_policy="raise")
        result["paired_t_statistic"] = float(ttest.statistic)
        result["paired_t_p_raw"] = float(ttest.pvalue)
        result["favorable_direction"] = "higher" if metric in HIGHER_IS_BETTER else "lower"
        result["favorable_object_fraction"] = result["positive_fraction"] if metric in HIGHER_IS_BETTER else result["negative_fraction"]
        tests[metric] = result
    secondary = [m for m in METRICS if m != "fg_psnr"]
    adjusted = holm_adjust([tests[m]["paired_t_p_raw"] for m in secondary])
    for metric, p_adj in zip(secondary, adjusted):
        tests[metric]["holm_adjusted_p"] = p_adj
    tests["fg_psnr"]["multiplicity_family"] = "single predeclared primary endpoint; no adjustment"
    result = {
        "cohort": "FRESH_C_C3_CONFIRMATION_REVISION_ERA_FOLLOW_UP",
        "n_objects": len(uids),
        "contrast": "native_gc3 - native_gfl",
        "primary_endpoint": "fg_psnr",
        "primary_confirmed_positive_by_protocol": tests["fg_psnr"]["bootstrap_ci95"][0] > 0,
        "secondary_multiplicity_family": secondary,
        "delta_convention": "condition A minus condition B",
        "inferential_unit": "object; one paired delta per selected source UID",
        "analysis_protocol_sha256": sha256(DATA / "FRESH_C_INTEGRITY_GATE.json"),
        "tests": tests,
    }
    output = DATA / "fresh_c_c3_minus_gfl_analysis.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    delta_path = DATA / "fresh_c_c3_minus_gfl_object_deltas.csv"
    with delta_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["object_uid", *METRICS], lineterminator="\n")
        writer.writeheader()
        writer.writerows(object_rows)
    print(json.dumps(result, indent=2))
    return result


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
