#!/usr/bin/env python3
"""Independent row-level audit and paired statistics for the frozen Core-7.

This is intentionally separate from analyze_core7_20261001.py. It reads the
committed per-condition CSVs, checks the 276 x 7 matrix, and writes the final
audit tables without touching experiment outputs or manuscript sources.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/coordination/final_evidence_freeze_20261001"
COORD = ROOT / "final/round2/coordination"
CORE7 = COORD / "core7_same_runner_completion_20261001"
EXPECTED_N = 276
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_RESAMPLES = 10_000

SOURCES = {
    "no_adapter": CORE7 / "formal_no_adapter/per_object_metrics.csv",
    "global_fixed_low": COORD / "final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930/global_fixed_low_per_object_metrics.csv",
    "global_fixed_high": CORE7 / "formal_global_fixed_high/per_object_metrics.csv",
    "global_c3": COORD / "main_backbone_robustness1_20260930/r0_completion_global_c3/per_object_metrics.csv",
    "layer_fixed_mean": COORD / "layer_confirmation_20260930/layer_fixed_mean_per_object_metrics.csv",
    "layer_lhl": COORD / "layer_confirmation_20260930/layer_lhl_per_object_metrics.csv",
    "layer_llh": COORD / "layer_confirmation_20260930/layer_llh_per_object_metrics.csv",
}

MANIFESTS = {
    "no_adapter": CORE7 / "formal_no_adapter/protocol_manifest.json",
    "global_fixed_low": COORD / "final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930/global_fixed_low_protocol_manifest.json",
    "global_fixed_high": CORE7 / "formal_global_fixed_high/protocol_manifest.json",
    "global_c3": COORD / "main_backbone_robustness1_20260930/r0_completion_global_c3/protocol_manifest.json",
    "layer_fixed_mean": COORD / "layer_confirmation_20260930/layer_fixed_mean_protocol_manifest.json",
    "layer_lhl": COORD / "layer_confirmation_20260930/layer_lhl_protocol_manifest.json",
    "layer_llh": COORD / "layer_confirmation_20260930/layer_llh_protocol_manifest.json",
}

METRICS = [
    "fg_psnr", "fg_ssim", "fg_lpips",
    "full_psnr", "full_ssim", "full_lpips", "edge_ssim",
]
HIGHER_BETTER = {"fg_psnr", "fg_ssim", "full_psnr", "full_ssim", "edge_ssim"}
LOWER_BETTER = {"fg_lpips", "full_lpips"}
GT_METRICS = ["gt_fg_rgb_std", "gt_fg_grad_mag", "gt_fg_lap_var", "gt_fg_hf_energy"]
COMPARISONS = [
    ("layer_llh", "global_fixed_low"),
    ("layer_llh", "global_fixed_high"),
    ("layer_llh", "global_c3"),
    ("layer_llh", "layer_fixed_mean"),
    ("layer_llh", "layer_lhl"),
    ("global_fixed_high", "global_fixed_low"),
    ("layer_fixed_mean", "global_fixed_low"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_manifest(method: str, path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("checkpoint_sha256") != "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0":
        raise ValueError(f"{method}: checkpoint SHA mismatch in {path}")
    if data.get("object_list_sha256") != "a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044":
        raise ValueError(f"{method}: object-list SHA mismatch in {path}")
    if data.get("steps") != 50:
        raise ValueError(f"{method}: expected 50 steps in {path}")
    if data.get("target_view_mode") != "unique6" or data.get("target_views") != [0, 15, 12, 16, 13, 14]:
        raise ValueError(f"{method}: target-view protocol mismatch in {path}")
    if data.get("metric_path") != "geotex.eval_exploration.compute_metrics":
        raise ValueError(f"{method}: metric implementation mismatch in {path}")
    for key in ("seed", "latent_seed", "seed_base"):
        if key in data and data[key] is not None and int(data[key]) != 42:
            raise ValueError(f"{method}: expected R0 seed 42, found {key}={data[key]} in {path}")
    if "scale_semantics" in data and "deep 3.0 / middle 3.5 / shallow 0.8" not in data["scale_semantics"]:
        raise ValueError(f"{method}: capped scale semantics mismatch in {path}")
    return data


def load_matrix() -> tuple[dict[str, dict[int, dict]], dict]:
    if len(SOURCES) != 7:
        raise AssertionError("expected exactly seven source conditions")
    matrix: dict[str, dict[int, dict]] = {}
    audit: dict = {"conditions": {}, "errors": []}
    canonical_objects: dict[int, str] | None = None
    canonical_gt: dict[int, tuple[float, ...]] | None = None
    for method, path in SOURCES.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        rows = read_rows(path)
        ids = [int(r["object_idx"]) for r in rows]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        keyed = {int(r["object_idx"]): r for r in rows}
        missing = sorted(set(range(EXPECTED_N)) - set(keyed))
        extra = sorted(set(keyed) - set(range(EXPECTED_N)))
        if len(rows) != EXPECTED_N or duplicates or missing or extra:
            raise ValueError(
                f"{method}: row matrix failure rows={len(rows)}, duplicates={duplicates[:5]}, "
                f"missing={missing[:5]}, extra={extra[:5]}"
            )
        schedule_values = sorted({r.get("schedule", "") for r in rows})
        if schedule_values != [method]:
            raise ValueError(f"{method}: wrong schedule labels {schedule_values}")
        row_seeds = {int(r["seed_base"]) for r in rows if r.get("seed_base")}
        if row_seeds and row_seeds != {42}:
            raise ValueError(f"{method}: serialized per-row seed is not R0 seed 42: {row_seeds}")
        for idx, row in keyed.items():
            if row.get("object", "") == "":
                raise ValueError(f"{method}/{idx}: missing object label")
            for key, value in row.items():
                if key in {"object", "schedule"}:
                    continue
                try:
                    number = float(value)
                except (ValueError, TypeError):
                    continue
                if not math.isfinite(number):
                    raise ValueError(f"{method}/{idx}: non-finite {key}={value}")
            for metric in METRICS:
                if metric not in row:
                    raise ValueError(f"{method}/{idx}: missing metric {metric}")
                if not math.isfinite(float(row[metric])):
                    raise ValueError(f"{method}/{idx}: non-finite {metric}")
        object_map = {idx: keyed[idx]["object"] for idx in range(EXPECTED_N)}
        gt_map = {
            idx: tuple(float(keyed[idx][m]) for m in GT_METRICS)
            for idx in range(EXPECTED_N)
        }
        if canonical_objects is None:
            canonical_objects, canonical_gt = object_map, gt_map
        else:
            if object_map != canonical_objects:
                raise ValueError(f"{method}: object_idx-to-object mapping differs")
            if gt_map != canonical_gt:
                raise ValueError(f"{method}: serialized GT metric values differ")

        manifest_path = MANIFESTS[method]
        manifest = validate_manifest(method, manifest_path)
        matrix[method] = {
            idx: {k: (v if k in {"object", "schedule"} else float(v)) for k, v in keyed[idx].items()}
            for idx in keyed
        }
        audit["conditions"][method] = {
            "rows": len(rows),
            "objects": len(object_map),
            "object_idx_min": min(object_map),
            "object_idx_max": max(object_map),
            "schedule_labels": schedule_values,
            "csv": str(path.relative_to(ROOT)),
            "csv_sha256": sha256(path),
            "manifest": str(manifest_path.relative_to(ROOT)),
            "manifest_sha256": sha256(manifest_path),
            "seed_base_serialized": sorted({r["seed_base"] for r in rows if r.get("seed_base")}),
            "manifest_realization": manifest.get("realization", "R0 seed=42; old manifests use seed=42"),
        }
    audit["row_matrix"] = "PASS: 276 unique object_idx values x 7 conditions = 1932 rows"
    audit["cross_condition_object_mapping"] = "PASS: object label identical for every object_idx"
    audit["cross_condition_gt_metric_serialization"] = "PASS: four GT texture metric columns bit-identical in CSV serialization"
    audit["limits"] = [
        "The five original Core-5 rows do not serialize per-object tensor/input hashes. Their runner/protocol manifests pin R0 seed=42+idx, latent seed=42, and the same runner/checkpoint/list; deterministic input equality is supported by the frozen protocol and prior shared-input preflight, not by a full 276-row input-hash table.",
        "The two formal completion arms do serialize six per-object input hashes; SHARED_INPUT_AUDIT_CORE7.json reports 0/276 mismatches between no_adapter and global_fixed_high.",
        "GT-derived metric equality is a consistency check, not a substitute for hashes of all preprocessed tensors."
    ]
    return matrix, audit


def bootstrap(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(values)
    means = values[rng.integers(0, n, size=(BOOTSTRAP_RESAMPLES, n))].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return float(low), float(high)


def write_statistics(matrix: dict[str, dict[int, dict]], audit: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    aggregate_rows = []
    means_by_metric: dict[str, dict[str, float]] = {m: {} for m in METRICS}
    for method, rows in matrix.items():
        for metric in METRICS:
            vals = np.asarray([rows[i][metric] for i in range(EXPECTED_N)], dtype=np.float64)
            means_by_metric[metric][method] = float(vals.mean())
            aggregate_rows.append({
                "condition": method,
                "n": len(vals),
                "metric": metric,
                "direction": "higher-is-better" if metric in HIGHER_BETTER else "lower-is-better",
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "rank_best_to_worst": None,
            })
    for metric in METRICS:
        reverse = metric in HIGHER_BETTER
        ordered = sorted(means_by_metric[metric], key=lambda k: means_by_metric[metric][k], reverse=reverse)
        rank = {method: pos + 1 for pos, method in enumerate(ordered)}
        for row in aggregate_rows:
            if row["metric"] == metric:
                row["rank_best_to_worst"] = rank[row["condition"]]
    with (OUT / "CORE7_FINAL_AGGREGATES.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(aggregate_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(aggregate_rows)

    stat_rows = []
    for left, right in COMPARISONS:
        for metric in METRICS:
            raw = np.asarray(
                [matrix[left][i][metric] - matrix[right][i][metric] for i in range(EXPECTED_N)],
                dtype=np.float64,
            )
            benefit = raw if metric in HIGHER_BETTER else -raw
            low, high = bootstrap(benefit)
            wins = int(np.count_nonzero(benefit > 0))
            losses = int(np.count_nonzero(benefit < 0))
            ties = int(np.count_nonzero(benefit == 0))
            stat_rows.append({
                "left": left,
                "right": right,
                "metric": metric,
                "direction": "higher-is-better" if metric in HIGHER_BETTER else "lower-is-better",
                "raw_delta_convention": "left_minus_right",
                "raw_mean_delta": float(raw.mean()),
                "raw_median_delta": float(np.median(raw)),
                "benefit_delta_convention": "positive_means_left_better",
                "benefit_mean_delta": float(benefit.mean()),
                "benefit_median_delta": float(np.median(benefit)),
                "benefit_ci95_low": low,
                "benefit_ci95_high": high,
                "raw_ci95_low": low if metric in HIGHER_BETTER else -high,
                "raw_ci95_high": high if metric in HIGHER_BETTER else -low,
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "n": len(benefit),
                "inference": "NO_DETECTED_DIFFERENCE" if low <= 0 <= high else "CI_EXCLUDES_ZERO",
            })
    with (OUT / "CORE7_FINAL_PAIRED_STATISTICS.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(stat_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(stat_rows)

    audit_path = OUT / "CORE7_ROW_AUDIT.json"
    prior_path = CORE7 / "PAIRED_BOOTSTRAP_CORE7.csv"
    prior_rows = read_rows(prior_path)
    prior_index = {(r["comparison"], r["metric"]): r for r in prior_rows}
    reconciled = 0
    mismatches = []
    for row in stat_rows:
        key = (f"{row['left']} - {row['right']}", row["metric"])
        old = prior_index.get(key)
        if old is None:
            continue
        columns = {
            "n": (float(row["n"]), float(old["n"])),
            "mean_delta": (row["raw_mean_delta"], float(old["mean_delta"])),
            "median_delta": (row["raw_median_delta"], float(old["median_delta"])),
            "ci95_low": (row["raw_ci95_low"], float(old["ci95_low"])),
            "ci95_high": (row["raw_ci95_high"], float(old["ci95_high"])),
        }
        failed = [name for name, (new, old_value) in columns.items()
                  if not math.isclose(new, old_value, rel_tol=0.0, abs_tol=1e-12)]
        if failed:
            mismatches.append({"comparison": key[0], "metric": key[1], "fields": failed})
        else:
            reconciled += 1

    target_idx = next(i for i, row in matrix["layer_llh"].items()
                      if row["object"] == "obj_0066")
    figure_delta = {
        i: matrix["layer_llh"][i]["fg_psnr"] - matrix["global_fixed_low"][i]["fg_psnr"]
        for i in range(EXPECTED_N)
    }
    target_value = figure_delta[target_idx]
    figure_rank = 1 + sum(value > target_value for value in figure_delta.values())
    audit["statistics"] = {
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256(Path(__file__).resolve()),
        "metrics": METRICS,
        "pairwise_comparisons": [f"{a} - {b}" for a, b in COMPARISONS],
        "bootstrap": {"unit": "object", "resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED, "ci": "percentile 95%"},
        "lower_is_better_benefit_sign_reversed": sorted(LOWER_BETTER),
        "reconciliation_to_preexisting_bootstrap": {
            "source": str(prior_path.relative_to(ROOT)),
            "matched_pair_metric_rows": reconciled,
            "compared_pair_metric_rows": len(prior_index),
            "mismatches": mismatches,
            "status": "PASS" if reconciled == 42 and not mismatches else "FAIL",
        },
    }
    audit["figure_crosscheck"] = {
        "object": "obj_0066",
        "comparison": "layer_llh - global_fixed_low",
        "metric": "fg_psnr",
        "object_idx": target_idx,
        "benefit_delta_db": target_value,
        "rank_best_to_worst": figure_rank,
        "n": EXPECTED_N,
    }
    (OUT / "CORE7_ROW_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote Core-7 audit outputs to {OUT}")
    print(f"rows=7x276; comparisons={len(COMPARISONS)}x{len(METRICS)}; bootstrap={BOOTSTRAP_RESAMPLES}")
    for r in stat_rows:
        if r["left"] == "global_fixed_high" and r["right"] == "global_fixed_low" and r["metric"] == "full_psnr":
            print(json.dumps(r, sort_keys=True))


def main() -> None:
    matrix, audit = load_matrix()
    write_statistics(matrix, audit)


if __name__ == "__main__":
    main()
