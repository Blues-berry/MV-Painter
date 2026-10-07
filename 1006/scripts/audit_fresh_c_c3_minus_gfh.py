#!/usr/bin/env python3
"""Integrity-gated post-hoc paired audit for Fresh C C3 minus GFH."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


CONDITION_A = "native_gc3"
CONDITION_B = "native_gfh"
EXPECTED_N = 300
N_BOOTSTRAP = 10_000
RNG_SEED = 20261002
METRICS = {
    "FG-PSNR": ("fg_psnr", "higher"),
    "FG-SSIM": ("fg_ssim", "higher"),
    "FG-LPIPS": ("fg_lpips", "lower"),
    "Full-PSNR": ("full_psnr", "higher"),
    "Full-SSIM": ("full_ssim", "higher"),
    "Full-LPIPS": ("full_lpips", "lower"),
    "Edge-SSIM": ("edge_ssim", "higher"),
}
INPUT_IDENTITY_COLUMNS = (
    "input_cond_sha256",
    "input_depth_sha256",
    "input_global_embeds_sha256",
    "input_init_latent_sha256",
    "input_normal_sha256",
    "input_target_sha256",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: Any) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def validate_source(data_dir: Path, raw_csv: Path, script_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    checks: list[dict[str, Any]] = []
    gate_path = data_dir / "FRESH_C_INTEGRITY_GATE.json"
    cohort_path = data_dir / "FRESH_C_COHORT_MANIFEST.json"
    embeddings_path = data_dir / "FRESH_C_INPUT_EMBEDDINGS_MANIFEST.json"
    run_dir = data_dir / "runs" / "c3_confirmation"
    launch_path = run_dir / "LAUNCH_IDENTITY.json"
    output_manifest_path = run_dir / "OUTPUT_FILE_SHA256.csv"
    shard_manifests = [run_dir / "run_manifest_shard0.json", run_dir / "run_manifest_shard1.json"]

    required_files = [gate_path, cohort_path, embeddings_path, launch_path, output_manifest_path, *shard_manifests, raw_csv]
    missing = [str(path) for path in required_files if not path.is_file()]
    add_check(checks, "required_source_files", not missing, {"missing": missing})
    if missing:
        return {"status": "BLOCKED", "reason": "required source file missing", "missing": missing}, checks, []

    gate = read_json(gate_path)
    launch = read_json(launch_path)
    manifests = [read_json(path) for path in shard_manifests]
    hashes = {
        "raw_source_sha256": sha256_file(raw_csv),
        "integrity_gate_sha256": sha256_file(gate_path),
        "cohort_manifest_sha256": sha256_file(cohort_path),
        "input_embeddings_manifest_sha256": sha256_file(embeddings_path),
        "output_hash_manifest_sha256": sha256_file(output_manifest_path),
        "launch_identity_sha256": sha256_file(launch_path),
        "run_manifest_shard0_sha256": sha256_file(shard_manifests[0]),
        "run_manifest_shard1_sha256": sha256_file(shard_manifests[1]),
        "analysis_script_sha256": sha256_file(script_path),
    }

    add_check(checks, "prior_fresh_c_integrity_gate_pass", gate.get("status") == "PASS", gate.get("status"))
    add_check(checks, "cohort_size", gate.get("cohort_n") == EXPECTED_N, gate.get("cohort_n"))
    add_check(checks, "prior_gate_raw_csv_hash", gate.get("combined_csv_sha256") == hashes["raw_source_sha256"], {
        "gate_sha256": gate.get("combined_csv_sha256"), "observed_sha256": hashes["raw_source_sha256"]
    })
    add_check(checks, "prior_gate_cohort_manifest_hash", gate.get("cohort_manifest_sha256") == hashes["cohort_manifest_sha256"], {
        "gate_sha256": gate.get("cohort_manifest_sha256"), "observed_sha256": hashes["cohort_manifest_sha256"]
    })
    add_check(checks, "prior_gate_input_embeddings_hash", gate.get("input_embeddings_manifest_sha256") == hashes["input_embeddings_manifest_sha256"], {
        "gate_sha256": gate.get("input_embeddings_manifest_sha256"), "observed_sha256": hashes["input_embeddings_manifest_sha256"]
    })
    add_check(checks, "prior_gate_output_hash_manifest", gate.get("output_hash_manifest_sha256") == hashes["output_hash_manifest_sha256"], {
        "gate_sha256": gate.get("output_hash_manifest_sha256"), "observed_sha256": hashes["output_hash_manifest_sha256"]
    })

    expected_conditions = {"no_adapter", "native_gfl", CONDITION_B, CONDITION_A}
    add_check(checks, "original_four_conditions_present", expected_conditions.issubset(set(gate.get("conditions", []))), gate.get("conditions"))
    add_check(checks, "gate_c3_gfh_coverage", gate.get("condition_coverage", {}).get(CONDITION_A) == EXPECTED_N and gate.get("condition_coverage", {}).get(CONDITION_B) == EXPECTED_N, gate.get("condition_coverage"))

    cohort = read_json(cohort_path)
    cohort_objects = cohort.get("objects", [])
    cohort_uid_to_index = {str(row.get("uid")): int(row["object_index"]) for row in cohort_objects}
    cohort_uids = set(cohort_uid_to_index)
    add_check(checks, "frozen_cohort_manifest_300_unique_uids", len(cohort_uids) == EXPECTED_N and len(cohort_objects) == EXPECTED_N, {
        "object_rows": len(cohort_objects), "unique_uids": len(cohort_uids)
    })

    import pandas as pd

    frame = pd.read_csv(raw_csv)
    expected_rows = EXPECTED_N * 4
    add_check(checks, "combined_csv_row_count", len(frame) == expected_rows and gate.get("verified_rows") == expected_rows, {
        "csv_rows": len(frame), "gate_verified_rows": gate.get("verified_rows"), "expected_rows": expected_rows
    })
    required_columns = {"object_uid", "object_idx", "condition", "seed_base", *INPUT_IDENTITY_COLUMNS, *(value[0] for value in METRICS.values())}
    missing_columns = sorted(required_columns.difference(frame.columns))
    add_check(checks, "required_csv_columns", not missing_columns, missing_columns)

    if not missing_columns:
        duplicate_count = int(frame.duplicated(["condition", "object_uid"]).sum())
        add_check(checks, "no_duplicate_condition_uid", duplicate_count == 0, {"duplicates": duplicate_count})
        c3 = frame[frame["condition"] == CONDITION_A].copy()
        gfh = frame[frame["condition"] == CONDITION_B].copy()
        c3_uids, gfh_uids = set(c3["object_uid"].astype(str)), set(gfh["object_uid"].astype(str))
        add_check(checks, "c3_and_gfh_each_300_unique_objects", c3["object_uid"].nunique() == EXPECTED_N and gfh["object_uid"].nunique() == EXPECTED_N, {
            "c3_rows": len(c3), "c3_unique_uids": int(c3["object_uid"].nunique()),
            "gfh_rows": len(gfh), "gfh_unique_uids": int(gfh["object_uid"].nunique())
        })
        add_check(checks, "exact_c3_gfh_uid_set_match", c3_uids == gfh_uids == cohort_uids, {
            "c3_minus_gfh": sorted(c3_uids - gfh_uids)[:10],
            "gfh_minus_c3": sorted(gfh_uids - c3_uids)[:10],
            "c3_minus_frozen_cohort": sorted(c3_uids - cohort_uids)[:10],
            "frozen_cohort_minus_c3": sorted(cohort_uids - c3_uids)[:10],
        })
        add_check(checks, "uid_to_frozen_object_index_match", all(
            cohort_uid_to_index.get(str(row.object_uid)) == int(row.object_idx) for row in frame.itertuples()
        ), "object_uid maps to frozen object_index for every condition row")

        wide = frame.pivot(index="object_uid", columns="condition")
        seed_values = wide["seed_base"]
        seed_match = bool((seed_values[CONDITION_A] == seed_values[CONDITION_B]).all())
        add_check(checks, "generation_seed_match", seed_match and bool((seed_values[CONDITION_A] == 42).all()), {
            "seed_base": 42,
            "effective_seed_policy": "seed_base + object_idx",
            "paired_seed_mismatches": int((seed_values[CONDITION_A] != seed_values[CONDITION_B]).sum()),
            "paired_object_index_mismatches": int((wide["object_idx"][CONDITION_A] != wide["object_idx"][CONDITION_B]).sum()),
        })
        identity_mismatches = {}
        for column in INPUT_IDENTITY_COLUMNS:
            identity_mismatches[column] = int((wide[column][CONDITION_A] != wide[column][CONDITION_B]).sum())
        add_check(checks, "reference_and_input_identity_match", all(value == 0 for value in identity_mismatches.values()), identity_mismatches)

        metric_nonfinite = {}
        for display_name, (column, _) in METRICS.items():
            values = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)
            metric_nonfinite[display_name] = int((~np.isfinite(values)).sum())
        add_check(checks, "all_required_metrics_finite", all(value == 0 for value in metric_nonfinite.values()), metric_nonfinite)
    else:
        c3 = gfh = None

    launch_source_hashes = launch.get("source_hashes", {})
    shard_identity = []
    for manifest in manifests:
        code_hashes = manifest.get("code_source_sha256", {})
        shard_identity.append({
            "shard": manifest.get("shard"),
            "status": manifest.get("status"),
            "condition_list": sorted(manifest.get("conditions", [])),
            "runner_script_sha256": manifest.get("runner_script_sha256"),
            "checkpoint_sha256": manifest.get("checkpoint_sha256"),
            "metric_implementation_sha256": code_hashes.get("metric_implementation", {}).get("sha256"),
            "metric_path": manifest.get("metric_path"),
            "config_sha256": manifest.get("config_sha256"),
        })
    same_runner = len({row["runner_script_sha256"] for row in shard_identity}) == 1 and shard_identity[0]["runner_script_sha256"] == launch_source_hashes.get("runner")
    same_checkpoint = len({row["checkpoint_sha256"] for row in shard_identity}) == 1 and shard_identity[0]["checkpoint_sha256"] == launch_source_hashes.get("checkpoint")
    same_metric = len({row["metric_implementation_sha256"] for row in shard_identity}) == 1 and shard_identity[0]["metric_implementation_sha256"] == launch_source_hashes.get("metric_implementation") and len({row["metric_path"] for row in shard_identity}) == 1
    all_complete = all(row["status"] == "complete" for row in shard_identity)
    add_check(checks, "same_runner", same_runner, shard_identity)
    add_check(checks, "same_checkpoint", same_checkpoint, shard_identity)
    add_check(checks, "same_metric_implementation", same_metric, shard_identity)
    add_check(checks, "completed_run_shards", all_complete, shard_identity)

    source_summary = {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED",
        "analysis_classification": "REVIEWER_REQUESTED_POST_HOC_AUDIT",
        "cohort_label": "FROZEN_FRESH_C",
        "cohort_n": EXPECTED_N,
        "condition_A": CONDITION_A,
        "condition_B": CONDITION_B,
        "source_paths": {
            "data_dir": str(data_dir.resolve()),
            "raw_csv": str(raw_csv.resolve()),
            "integrity_gate": str(gate_path.resolve()),
            "cohort_manifest": str(cohort_path.resolve()),
            "input_embeddings_manifest": str(embeddings_path.resolve()),
            "run_identity": str(launch_path.resolve()),
            "shard_manifests": [str(path.resolve()) for path in shard_manifests],
            "output_hash_manifest": str(output_manifest_path.resolve()),
        },
        "source_hashes": hashes,
        "frozen_run_identity": {
            "runner_sha256": launch_source_hashes.get("runner"),
            "checkpoint_sha256": launch_source_hashes.get("checkpoint"),
            "metric_implementation_sha256": launch_source_hashes.get("metric_implementation"),
            "metric_path": shard_identity[0]["metric_path"] if shard_identity else None,
            "reference_seed_policy": manifests[0].get("reference_seed_policy") if manifests else None,
            "effective_data_roots": manifests[0].get("effective_data_roots") if manifests else None,
        },
        "checks": checks,
    }
    return source_summary, checks, frame.to_dict(orient="records") if not missing_columns else []


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True, help="Frozen Fresh C source data directory")
    parser.add_argument("--raw-csv", type=Path, default=None, help="Canonical combined per-object metrics CSV")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "review")
    args = parser.parse_args()
    raw_csv = args.raw_csv or args.data_dir / "runs" / "c3_confirmation" / "per_object_metrics.csv"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    integrity, checks, records = validate_source(args.data_dir, raw_csv, Path(__file__).resolve())
    integrity_path = output_dir / "R1_4_FRESHC_C3_GFH_SOURCE_INTEGRITY.json"
    write_json(integrity_path, integrity)
    if integrity["status"] != "PASS":
        integrity["block_code"] = "R1_4_FRESHC_C3_GFH_AUDIT_BLOCKED"
        integrity["reason"] = "one or more required source integrity/pairing checks failed"
        write_json(integrity_path, integrity)
        print("R1_4_FRESHC_C3_GFH_AUDIT_BLOCKED")
        return 2

    import pandas as pd

    frame = pd.DataFrame(records)
    c3 = frame[frame["condition"] == CONDITION_A].set_index("object_uid").sort_index()
    gfh = frame[frame["condition"] == CONDITION_B].set_index("object_uid").sort_index()
    n = len(c3)
    rng = np.random.default_rng(RNG_SEED)
    bootstrap_indices = rng.integers(0, n, size=(N_BOOTSTRAP, n), dtype=np.int32)
    results: list[dict[str, Any]] = []
    for display_name, (column, direction) in METRICS.items():
        differences = c3[column].to_numpy(dtype=float) - gfh[column].to_numpy(dtype=float)
        favorable = differences > 0 if direction == "higher" else differences < 0
        unfavorable = differences < 0 if direction == "higher" else differences > 0
        bootstrap_means = differences[bootstrap_indices].mean(axis=1)
        lower, upper = np.percentile(bootstrap_means, [2.5, 97.5])
        results.append({
            "experiment_id": "FRESH_C_C3_MINUS_GFH_POSTHOC_20261007",
            "cohort": "FROZEN_FRESH_C",
            "n_objects": n,
            "condition_A": CONDITION_A,
            "condition_B": CONDITION_B,
            "metric": display_name,
            "source_column": column,
            "direction": direction,
            "effect_A_minus_B": float(differences.mean()),
            "ci95_lower": float(lower),
            "ci95_upper": float(upper),
            "median_A_minus_B": float(np.median(differences)),
            "favorable_count_for_condition_A": int(favorable.sum()),
            "favorable_fraction_for_condition_A": float(favorable.mean()),
            "unfavorable_count_for_condition_B": int(unfavorable.sum()),
            "tie_count": int((differences == 0).sum()),
            "statistical_unit": "object",
            "bootstrap_method": "paired object bootstrap; 10000 resamples; two-sided percentile 95% CI",
            "bootstrap_rng": f"numpy.default_rng({RNG_SEED})",
            "analysis_classification": "REVIEWER_REQUESTED_POST_HOC_AUDIT",
        })

    csv_path = output_dir / "R1_4_FRESHC_C3_minus_GFH_posthoc_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    json_path = output_dir / "R1_4_FRESHC_C3_minus_GFH_posthoc_results.json"
    write_json(json_path, {
        "status": "PASS",
        "experiment_id": "FRESH_C_C3_MINUS_GFH_POSTHOC_20261007",
        "analysis_classification": "REVIEWER_REQUESTED_POST_HOC_AUDIT",
        "status_label": "POST_HOC WITHIN FROZEN FRESH-C COHORT",
        "cohort": "FROZEN_FRESH_C",
        "n_objects": n,
        "condition_A": CONDITION_A,
        "condition_B": CONDITION_B,
        "statistical_unit": "object",
        "estimator": {
            "difference": "native_gc3 - native_gfh",
            "bootstrap_resamples": N_BOOTSTRAP,
            "rng": f"numpy.default_rng({RNG_SEED})",
            "interval": "two-sided percentile 95% CI",
            "p_values_computed": False,
        },
        "limitations": [
            "Post-hoc reviewer-requested analysis within a frozen cohort; not part of the registered confirmatory family.",
            "Does not establish equivalence or non-inferiority; no non-inferiority margin was prespecified.",
            "Does not verify the original Table 4 contrast and is not an independent replication.",
            "Favorable-object fractions are descriptive and do not imply universal or typical-object benefit.",
        ],
        "source_integrity_path": str(integrity_path.resolve()),
        "source_hashes": integrity["source_hashes"],
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "results": results,
    })
    integrity["outputs"] = {
        "results_csv": str(csv_path.resolve()),
        "results_csv_sha256": sha256_file(csv_path),
        "results_json": str(json_path.resolve()),
        "results_json_sha256": sha256_file(json_path),
    }
    write_json(integrity_path, integrity)
    print(f"Integrity PASS; wrote {csv_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
