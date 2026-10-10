#!/usr/bin/env python3
"""Recompute formal pairwise signs from raw shard ledgers across campaigns."""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
FORMAL = ROOT / "final/round2/scientific_validation_v3/formal"
OUT = ROOT / "1006/data/derived/formal_pairwise_sign_audit.json"
OUT_MD = ROOT / "1006/evidence/audits/FORMAL_PAIRWISE_DIRECTION_AUDIT_20261006.md"
HIGHER_IS_BETTER = {
    "fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim",
    "crop_psnr", "crop_ssim", "edge_fscore", "edge_psnr",
}


def campaign_rows(directory: Path, condition: str) -> tuple[dict[str, dict], list[dict]]:
    rows = {}
    duplicates = []
    for path in sorted(directory.glob("rows_shard*.json")):
        for row in json.loads(path.read_text()):
            if row.get("condition") != condition:
                continue
            uid = str(row.get("object_uid") or row.get("object"))
            if uid in rows:
                prior = rows[uid]
                first = {k: v for k, v in prior.items() if k != "elapsed_seconds"}
                current = {k: v for k, v in row.items() if k != "elapsed_seconds"}
                if first != current:
                    raise RuntimeError(f"conflicting duplicate row for {directory.name}/{condition}/{uid}")
                duplicates.append({"uid": uid, "campaign": directory.name,
                                   "condition": condition, "duplicate_shard": path.name,
                                   "scientific_fields_identical": True})
                continue
            rows[uid] = row
    return rows, duplicates


@lru_cache(maxsize=None)
def load_condition(directory: Path, condition: str) -> tuple[dict[str, dict], str]:
    rows, duplicates = campaign_rows(directory, condition)
    DUPLICATES.extend(duplicates)
    if rows:
        return rows, directory.name
    for sibling in sorted(FORMAL.glob("campaign_*")):
        if sibling == directory or not sibling.is_dir():
            continue
        rows, duplicates = campaign_rows(sibling, condition)
        DUPLICATES.extend(duplicates)
        if rows:
            return rows, sibling.name
    raise FileNotFoundError(f"condition {condition} absent in {directory.name} and siblings")


def recompute(delta: np.ndarray) -> dict:
    rng = np.random.default_rng(20261002)
    draws = rng.integers(0, len(delta), size=(10_000, len(delta)))
    means = delta[draws].mean(axis=1)
    p = 2.0 * min(float((means <= 0).mean()), float((means >= 0).mean()))
    return {
        "n": len(delta), "mean_delta": float(delta.mean()), "median_delta": float(np.median(delta)),
        "ci95": [float(x) for x in np.percentile(means, [2.5, 97.5])],
        "win_rate": float((delta > 0).mean()), "loss_rate": float((delta < 0).mean()),
        "p_bootstrap": max(p, 1 / 10_000),
    }


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-10)


DUPLICATES: list[dict] = []


def main() -> None:
    pair_files = sorted(FORMAL.glob("campaign_*/pairwise_*.json"))
    audits, errors, warnings = [], [], []
    for pair_path in pair_files:
        pair = json.loads(pair_path.read_text())
        directory = pair_path.parent
        left, source_a = load_condition(directory, pair["a"])
        right, source_b = load_condition(directory, pair["b"])
        common = sorted(set(left) & set(right))
        disjoint = len(set(left) ^ set(right))
        pair_errors = []
        if len(common) != int(pair.get("n_common", -1)):
            pair_errors.append(f"n_common saved={pair.get('n_common')} raw={len(common)}")
        if disjoint != int(pair.get("n_disjoint", -1)):
            pair_errors.append(f"n_disjoint saved={pair.get('n_disjoint')} raw={disjoint}")

        input_mismatches, seed_mismatches, index_mismatches = [], [], []
        for uid in common:
            a, b = left[uid], right[uid]
            if a.get("input_hashes") != b.get("input_hashes"):
                input_mismatches.append(uid)
            if a.get("seed_base") != b.get("seed_base"):
                seed_mismatches.append(uid)
            if a.get("object_idx") != b.get("object_idx"):
                index_mismatches.append(uid)
        if input_mismatches:
            pair_errors.append(f"shared input hash mismatches: {len(input_mismatches)}")
        if seed_mismatches:
            pair_errors.append(f"seed mismatches: {len(seed_mismatches)}")
        if index_mismatches:
            pair_errors.append(f"object-index mismatches: {len(index_mismatches)}")

        test_audits = {}
        for metric, saved in pair.get("tests", {}).items():
            delta = np.asarray([float(left[uid][metric]) - float(right[uid][metric]) for uid in common], dtype=np.float64)
            raw = recompute(delta)
            mismatches = []
            for key in ("n", "mean_delta", "median_delta", "p_bootstrap", "win_rate", "loss_rate"):
                if not close(float(raw[key]), float(saved[key])):
                    mismatches.append(key)
            for index in (0, 1):
                if not close(float(raw["ci95"][index]), float(saved["ci95"][index])):
                    mismatches.append(f"ci95[{index}]")
            if mismatches:
                pair_errors.append(f"{metric} differs from saved pairwise JSON: {mismatches}")
            higher = metric in HIGHER_IS_BETTER
            favorable_fraction = float((delta > 0).mean()) if higher else float((delta < 0).mean())
            test_audits[metric] = {
                **raw,
                "positive_delta_favors_a": higher,
                "favorable_fraction_for_a": favorable_fraction,
                "favorable_mean_condition": (
                    pair["a"] if (raw["mean_delta"] > 0) == higher
                    else pair["b"] if raw["mean_delta"] != 0 else "no mean direction"
                ),
                "saved_result_matches_raw_rows": not mismatches,
                "mismatched_fields": mismatches,
            }
        if pair_errors:
            errors.append({"file": str(pair_path.relative_to(ROOT)), "errors": pair_errors})
        source_dirs = sorted({source_a, source_b})
        source_manifest_audit = {}
        for source_campaign in source_dirs:
            source_dir = FORMAL / source_campaign
            manifests = []
            for manifest_path in sorted(source_dir.glob("run_manifest_shard*.json")):
                manifest = json.loads(manifest_path.read_text())
                manifests.append({"file": manifest_path.name, "status": manifest.get("status"),
                                  "shard": manifest.get("shard"), "num_shards": manifest.get("num_shards"),
                                  "row_count": manifest.get("row_count"),
                                  "object_list_sha256": manifest.get("object_list_sha256"),
                                  "runner_script_sha256": manifest.get("runner_script_sha256"),
                                  "checkpoint_sha256": manifest.get("checkpoint_sha256"),
                                  "config_sha256": manifest.get("config_sha256")})
            nshards = sorted({m["num_shards"] for m in manifests if m["num_shards"] is not None})
            if len(nshards) > 1:
                warnings.append({"campaign": source_campaign,
                                 "warning": f"run manifests record inconsistent num_shards values: {nshards}; duplicate rows were checked for exact agreement"})
            source_manifest_audit[source_campaign] = {"manifests": manifests, "num_shards_values": nshards}
        duplicate_audit = [d for d in DUPLICATES if d["campaign"] in source_dirs]
        audits.append({
            "file": str(pair_path.relative_to(ROOT)), "campaign": directory.name,
            "condition_a": pair["a"], "condition_a_source_campaign": source_a,
            "condition_b": pair["b"], "condition_b_source_campaign": source_b,
            "cohort_n": len(common), "disjoint_uids": disjoint,
            "input_hash_matches": len(common) - len(input_mismatches),
            "seed_matches": len(common) - len(seed_mismatches),
            "object_index_matches": len(common) - len(index_mismatches),
            "source_run_manifests": source_manifest_audit,
            "identical_duplicate_rows_in_source_campaigns": duplicate_audit,
            "tests": test_audits, "status": "PASS" if not pair_errors else "FAIL",
            "errors": pair_errors,
        })

    # The same source campaign may be reached from several comparison files.
    # Keep the raw duplicate-row count, but de-duplicate repeated audit entries.
    duplicate_keys = {
        (row["campaign"], row["condition"], row["uid"], row["duplicate_shard"])
        for row in DUPLICATES
    }
    duplicate_groups = {}
    duplicate_counts = {}
    for campaign, condition, uid, shard in sorted(duplicate_keys):
        key = (campaign, condition)
        group = duplicate_groups.setdefault(key, {"uids": set(), "shards": set(), "rows": 0})
        group["uids"].add(uid)
        group["shards"].add(shard)
        group["rows"] += 1
    duplicate_summary = [
        {"campaign": campaign, "condition": condition,
         "identical_duplicate_row_count": group["rows"],
         "affected_uid_count": len(group["uids"]),
         "duplicate_shards": sorted(group["shards"]),
         "scientific_fields_identical_except_elapsed_seconds": True,
         "sample_uids": sorted(group["uids"])[:10]}
        for (campaign, condition), group in sorted(duplicate_groups.items())
    ]
    unique_warnings = {
        (row["campaign"], row["warning"]): row for row in warnings
    }
    formal_count = sum("EXPLORATORY" not in row["file"].upper() for row in audits)
    exploratory_count = len(audits) - formal_count
    result = {
        "status": "PASS" if not errors else "FAIL",
        "pairwise_file_count": len(pair_files),
        "formal_pairwise_file_count": formal_count,
        "exploratory_pairwise_file_count": exploratory_count,
        "passed_count": sum(row["status"] == "PASS" for row in audits),
        "failed_count": sum(row["status"] == "FAIL" for row in audits),
        "delta_convention": "condition A minus condition B; stored win_rate is the positive-delta fraction",
        "metric_directions": {metric: "higher_is_better" if metric in HIGHER_IS_BETTER else "lower_is_better"
                              for metric in sorted({m for row in audits for m in row["tests"]})},
        "bootstrap": {"draws": 10000, "seed": 20261002, "interval": "two-sided percentile object bootstrap"},
        "errors": errors,
        "pairwise_audits": audits,
        "warnings": list(unique_warnings.values()),
        "identical_duplicate_raw_row_count": len(duplicate_keys),
        "identical_duplicate_raw_row_audit": duplicate_summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Formal pairwise direction and row-reproduction audit — 2026-10-06", "",
        f"**Status: {result['status']}** — {formal_count} registered/formal and "
        f"{exploratory_count} explicitly exploratory pairwise files; "
        f"{result['passed_count']} of {len(pair_files)} reproduced from raw shard rows.", "",
        "Each contrast is condition A minus condition B. Higher FG-PSNR favors A; "
        "lower FG-LPIPS favors A, so a positive LPIPS delta favors B. The reported "
        "A-favorable fraction is direction-aware; the archived `win_rate` field "
        "is only the positive-delta fraction and must not be read as A wins for LPIPS.", "",
        "The audit rechecks paired UID count, disjoint count, object index, seed, "
        "six input hashes, mean, median, percentile object-bootstrap interval, "
        "two-tail bootstrap sign p-value, and positive/negative fractions. "
        "A p-value at 0.0001 is at the stored 10,000-draw reporting floor, not an exact zero.", "",
        "| Pairwise file | N | Source rows A / B | Metric | A−B mean | 95% object-bootstrap CI | A-favorable objects | Raw bootstrap p |", "|---|---:|---|---|---:|---:|---:|---:|",
    ]
    for audit in audits:
        for metric, test in audit["tests"].items():
            ci = test["ci95"]
            p_text = f"≤{test['p_bootstrap']:.4g}" if test["p_bootstrap"] <= 0.0001 else f"{test['p_bootstrap']:.4g}"
            lines.append(
                f"| `{Path(audit['file']).name}` | {audit['cohort_n']} | "
                f"{audit['condition_a_source_campaign']} / {audit['condition_b_source_campaign']} | "
                f"{metric} | {test['mean_delta']:+.6g} | "
                f"[{ci[0]:+.6g}, {ci[1]:+.6g}] | "
                f"{test['favorable_fraction_for_a']:.1%} | {p_text} |"
            )
    lines += [
        "", "## Provenance findings", "",
        "- `campaign_B3` has 750 identical duplicate raw rows across five conditions "
        "(150 per condition); duplicate scientific fields match after excluding "
        "elapsed time. Unique paired N remains 300. Its shard manifests disagree "
        "on `num_shards` (2 versus 4), so retain this as a provenance warning.",
        "- The 300-object LLH-versus-generic comparisons source LLH from "
        "`campaign_B1B2` and generic conditions from `campaign_C`. All paired "
        "UIDs, indices, seeds, and six input hashes match; both run manifests omit "
        "a configuration hash. These remain same-cohort retrospective paired "
        "comparisons, not independent confirmation.",
        "- Pairwise bootstrap p-values above are not a substitute for the frozen "
        "multiplicity families. Recomputed Holm adjustments for all five archived "
        "families and 28 tests are in `FORMAL_HOLM_FAMILY_AUDIT_20261006.md`.",
        "- These tables preserve endpoint-specific differences; no weighted "
        "cross-metric score or overall winner is computed.", "",
        "Machine-readable result: `../../data/derived/formal_pairwise_sign_audit.json`.",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": result["status"], "files": result["pairwise_file_count"],
                      "passed": result["passed_count"], "failed": result["failed_count"],
                      "formal": result["formal_pairwise_file_count"],
                      "exploratory": result["exploratory_pairwise_file_count"],
                      "duplicate_raw_rows": result["identical_duplicate_raw_row_count"],
                      "warnings": result["warnings"], "errors": errors[:8]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
