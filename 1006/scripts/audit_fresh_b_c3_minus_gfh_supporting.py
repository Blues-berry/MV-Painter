#!/usr/bin/env python3
"""Reproduce the Fresh B C3-minus-GFH retrospective supporting sensitivity."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_SOURCE_SHA256 = "ce7ba03f6dcb9f1d275b389c633e23dc544404eeac4ddf090e90a11ad278e081"
COHORT = "FRESH_CONFIRM_B"
CONDITION_A = "native_gc3"
CONDITION_B = "native_gfh"
EXPECTED_N = 150
N_BOOTSTRAP = 10_000
RNG_SEED = 20261002
CLASSIFICATION = "RETROSPECTIVE_POST_HOC_SUPPORTING_SENSITIVITY"
METRICS = (
    ("FG-PSNR", "fg_psnr", "higher"),
    ("FG-SSIM", "fg_ssim", "higher"),
    ("FG-LPIPS", "fg_lpips", "lower"),
    ("Full-PSNR", "full_psnr", "higher"),
    ("Full-SSIM", "full_ssim", "higher"),
    ("Full-LPIPS", "full_lpips", "lower"),
    ("Edge-SSIM", "edge_ssim", "higher"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def analyze(source: Path) -> list[dict[str, object]]:
    observed_hash = sha256_file(source)
    if observed_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"source hash mismatch: expected {EXPECTED_SOURCE_SHA256}, got {observed_hash}"
        )

    with source.open(newline="", encoding="utf-8") as stream:
        raw_rows = list(csv.DictReader(stream))
    paired: dict[str, dict[str, dict[str, str]]] = {
        CONDITION_A: {},
        CONDITION_B: {},
    }
    for row in raw_rows:
        condition = row["condition"]
        if condition not in paired:
            continue
        uid = row["object_uid"]
        if uid in paired[condition]:
            raise ValueError(f"duplicate condition/object row: {condition}/{uid}")
        paired[condition][uid] = row

    uids_a = set(paired[CONDITION_A])
    uids_b = set(paired[CONDITION_B])
    if len(uids_a) != EXPECTED_N or len(uids_b) != EXPECTED_N or uids_a != uids_b:
        raise ValueError(
            f"pairing failed: C3={len(uids_a)}, GFH={len(uids_b)}, "
            f"same UID set={uids_a == uids_b}"
        )
    uids = sorted(uids_a)
    for uid in uids:
        row_a, row_b = paired[CONDITION_A][uid], paired[CONDITION_B][uid]
        if row_a["object_idx"] != row_b["object_idx"]:
            raise ValueError(f"object index mismatch for {uid}")
        if row_a["seed_base"] != row_b["seed_base"]:
            raise ValueError(f"generation seed mismatch for {uid}")

    results: list[dict[str, object]] = []
    for display_name, column, direction in METRICS:
        delta = np.asarray(
            [
                float(paired[CONDITION_A][uid][column])
                - float(paired[CONDITION_B][uid][column])
                for uid in uids
            ],
            dtype=np.float64,
        )
        rng = np.random.default_rng(RNG_SEED)
        indices = rng.integers(0, len(delta), size=(N_BOOTSTRAP, len(delta)))
        bootstrap_means = delta[indices].mean(axis=1)
        lower, upper = np.percentile(bootstrap_means, [2.5, 97.5])
        favorable = delta > 0 if direction == "higher" else delta < 0
        results.append(
            {
                "experiment_id": "FRESH_B_C3_MINUS_GFH_SUPPORTING_POSTHOC_20261007",
                "cohort": COHORT,
                "N": len(delta),
                "condition_A": CONDITION_A,
                "condition_B": CONDITION_B,
                "metric": display_name,
                "effect": float(delta.mean()),
                "CI_lower": float(lower),
                "CI_upper": float(upper),
                "median": float(np.median(delta)),
                "favorable_count": int(favorable.sum()),
                "favorable_fraction": float(favorable.mean()),
                "statistical_unit": "object",
                "analysis_classification": CLASSIFICATION,
                "bootstrap_resamples": N_BOOTSTRAP,
                "bootstrap_seed": RNG_SEED,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_input = Path(__file__).resolve().parents[1] / "review/numerical_inputs/fresh_b_per_object_metrics.csv"
    parser.add_argument(
        "--input", type=Path, default=default_input,
        help="Hash-pinned Fresh B source CSV (defaults to the bundled copy)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "review",
    )
    args = parser.parse_args()
    source = args.input.resolve()
    repository_root = Path(__file__).resolve().parents[2]
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    results = analyze(source)

    csv_path = output_dir / "R1_4_FRESHB_C3_minus_GFH_supporting_results.csv"
    json_path = output_dir / "R1_4_FRESHB_C3_minus_GFH_supporting_results.json"
    fieldnames = [key for key in results[0] if key not in {"bootstrap_resamples", "bootstrap_seed"}]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fieldnames} for row in results)

    payload = {
        "status": "PASS",
        "analysis_classification": CLASSIFICATION,
        "cohort": COHORT,
        "N": EXPECTED_N,
        "condition_A": CONDITION_A,
        "condition_B": CONDITION_B,
        "statistical_unit": "object",
        "bootstrap_resamples": N_BOOTSTRAP,
        "bootstrap_seed": RNG_SEED,
        "source_path": str(source.relative_to(repository_root)) if source.is_relative_to(repository_root) else str(source),
        "source_sha256": sha256_file(source),
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "output_csv": csv_path.name,
        "output_csv_sha256": sha256_file(csv_path),
        "results": results,
        "limitation": "This is a retrospective supporting sensitivity, not a confirmatory replication; keep it separate from Fresh C and do not infer equivalence or non-inferiority.",
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: wrote {len(results)} object-paired endpoints (N={EXPECTED_N})")
    print(f"source_sha256={payload['source_sha256']}")
    print(f"analysis_script_sha256={payload['analysis_script_sha256']}")
    print(f"output_csv_sha256={payload['output_csv_sha256']}")
    print(f"output_json_sha256={sha256_file(json_path)}")
    for result in results:
        print(
            f"{result['metric']}: {result['effect']:+.6f} "
            f"[{result['CI_lower']:+.6f}, {result['CI_upper']:+.6f}], "
            f"median={result['median']:+.6f}, "
            f"favorable={result['favorable_count']}/{result['N']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
