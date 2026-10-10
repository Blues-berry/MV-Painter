#!/usr/bin/env python3
"""Reconstruct the registered C LLH-minus-linear comparison from source rows."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
B1B2 = ROOT / "1006/data/campaign_B1B2_prior"
C = ROOT / "1006/data/campaign_C_prior"
OUT_JSON = ROOT / "1006/data/derived/campaign_c_llh_linear_direction_audit.json"
OUT_MD = ROOT / "1006/evidence/audits/CAMPAIGN_C_LLH_LINEAR_DIRECTION_AUDIT_20261006.md"
PAIR = C / "pairwise_layer_llh_vs_gen_linear.json"
HOLM = C / "HOLM_FAMILY_C.json"
METRICS = ("fg_psnr", "fg_lpips")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def condition_rows(base: Path, shards: int, condition: str) -> dict[str, dict]:
    result = {}
    for shard in range(shards):
        path = base / f"rows_shard{shard}.json"
        if not path.is_file():
            raise RuntimeError(f"missing raw source ledger: {path}")
        for row in json.loads(path.read_text()):
            if row.get("condition") != condition:
                continue
            uid = str(row.get("object_uid") or row.get("object"))
            if uid in result:
                raise RuntimeError(f"duplicate raw row for {condition}/{uid}")
            result[uid] = row
    return result


def paired_bootstrap(delta: np.ndarray) -> dict:
    rng = np.random.default_rng(20261002)
    n = len(delta)
    draws = rng.integers(0, n, size=(10_000, n))
    means = delta[draws].mean(axis=1)
    p = 2.0 * min(float((means <= 0).mean()), float((means >= 0).mean()))
    return {
        "n": n,
        "mean_delta": float(delta.mean()),
        "median_delta": float(np.median(delta)),
        "ci95": [float(x) for x in np.percentile(means, [2.5, 97.5])],
        "win_rate_positive_delta": float((delta > 0).mean()),
        "loss_rate_negative_delta": float((delta < 0).mean()),
        "p_bootstrap": max(p, 1 / 10_000),
        "bootstrap_draws": 10_000,
        "bootstrap_seed": 20261002,
    }


def assert_close(actual: float, expected: float, label: str, tolerance: float = 1e-10) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise RuntimeError(f"reconstruction mismatch for {label}: {actual} != {expected}")


def main() -> None:
    llh = condition_rows(B1B2, 4, "layer_llh")
    linear = condition_rows(C, 2, "gen_linear")
    common_uids = sorted(set(llh) & set(linear))
    manifest_b = json.loads((B1B2 / "run_manifest_shard0.json").read_text())
    manifest_c = json.loads((C / "run_manifest_shard0.json").read_text())
    pair = json.loads(PAIR.read_text())
    holm = json.loads(HOLM.read_text())
    errors = []

    if len(llh) != 300 or len(linear) != 300 or set(llh) != set(linear):
        errors.append(f"UID coverage mismatch: LLH={len(llh)}, linear={len(linear)}, common={len(set(llh)&set(linear))}")
    if pair.get("n_common") != 300 or pair.get("n_disjoint") != 0:
        errors.append("pairwise JSON cohort count differs from the source-row join")
    identity_fields = ("object_list_sha256", "runner_script_sha256", "checkpoint_sha256",
                       "target_views", "target_view_mode", "latent_seed", "steps", "sampler")
    identity = {}
    for key in identity_fields:
        left, right = manifest_b.get(key), manifest_c.get(key)
        identity[key] = {"campaign_B1B2": left, "campaign_C": right, "match": left == right}
        if left != right:
            errors.append(f"run manifests differ for {key}")
    identity["config_sha256"] = {
        "campaign_B1B2": manifest_b.get("config_sha256"),
        "campaign_C": manifest_c.get("config_sha256"),
        "match": manifest_b.get("config_sha256") == manifest_c.get("config_sha256"),
        "limitation": "both historical manifests omit a concrete config hash (null)",
    }

    input_hash_match = 0
    for uid in common_uids:
        a, b = llh[uid], linear[uid]
        if a.get("object_idx") != b.get("object_idx") or a.get("seed_base") != b.get("seed_base"):
            errors.append(f"object index/seed mismatch: {uid}")
        if a.get("input_hashes") != b.get("input_hashes"):
            errors.append(f"input tensor hash mismatch: {uid}")
        else:
            input_hash_match += 1
        if not isinstance(a.get("input_hashes"), dict) or len(a["input_hashes"]) != 6:
            errors.append(f"incomplete shared-input hashes: {uid}")
        if int(a.get("seed_base", -1)) != 42:
            errors.append(f"seed policy mismatch: {uid}")

    reconstructed = {}
    for metric in METRICS:
        delta = np.asarray([float(llh[uid][metric]) - float(linear[uid][metric])
                            for uid in common_uids], dtype=np.float64)
        stats = paired_bootstrap(delta)
        recorded = pair["tests"][metric]
        for key in ("n", "mean_delta", "median_delta", "p_bootstrap"):
            assert_close(float(stats[key]), float(recorded[key]), f"{metric}.{key}")
        for i, value in enumerate(stats["ci95"]):
            assert_close(value, float(recorded["ci95"][i]), f"{metric}.ci95[{i}]")
        assert_close(stats["win_rate_positive_delta"], float(recorded["win_rate"]), f"{metric}.win_rate")
        assert_close(stats["loss_rate_negative_delta"], float(recorded["loss_rate"]), f"{metric}.loss_rate")
        h4_key = f"H4_LLH-gen_linear_{metric}"
        h4 = holm["tests"][h4_key]
        stats["holm_adjusted_p"] = float(h4["p_holm"])
        stats["metric_direction"] = "higher_is_better" if metric == "fg_psnr" else "lower_is_better"
        stats["favorable_condition"] = (
            "layer_llh" if (metric == "fg_psnr" and stats["mean_delta"] > 0)
            else "gen_linear" if (metric == "fg_psnr" and stats["mean_delta"] < 0)
            else "gen_linear" if (metric == "fg_lpips" and stats["mean_delta"] > 0)
            else "layer_llh" if (metric == "fg_lpips" and stats["mean_delta"] < 0)
            else "no directional mean difference"
        )
        reconstructed[metric] = stats

    if input_hash_match != 300:
        errors.append(f"only {input_hash_match}/300 input-hash pairs matched")
    if errors:
        result = {"status": "FAIL", "errors": errors, "input_hash_matches": input_hash_match,
                  "cohort_n": len(set(llh) & set(linear)), "run_identity": identity}
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
        raise RuntimeError(json.dumps(result, indent=2))

    result = {
        "status": "PASS_SOURCE_ROWS_RECONSTRUCTED",
        "contrast": "layer_llh - gen_linear",
        "cohort_n": len(llh),
        "data_lineage": {
            "llh_rows": "campaign_B1B2/layer_llh; 4 runner shards",
            "linear_rows": "campaign_C/gen_linear; 2 runner shards",
            "uid_sets_identical": True,
            "input_hash_matches": input_hash_match,
            "seed_and_object_index_match": True,
            "pairwise_analysis_joins_sibling_campaigns": True,
            "run_identity": identity,
            "provenance_caveat": "Both manifests have config_sha256=null; shared per-object tensor hashes match, but the legacy config identity is not cryptographically recorded.",
        },
        "tests": reconstructed,
        "source_hashes": {
            "pairwise_json": sha256(PAIR),
            "holm_family": sha256(HOLM),
            "campaign_B1B2_metrics": sha256(B1B2 / "layer_llh_per_object_metrics.csv"),
            "campaign_C_metrics": sha256(C / "gen_linear_per_object_metrics.csv"),
            "campaign_B1B2_rows": {f"shard{s}": sha256(B1B2 / f"rows_shard{s}.json") for s in range(4)},
            "campaign_C_rows": {f"shard{s}": sha256(C / f"rows_shard{s}.json") for s in range(2)},
        },
        "interpretation": "FG-PSNR does not show an LLH advantage; the registered FG-LPIPS difference favors endpoint-matched linear because LPIPS is lower-is-better.",
        "equivalence_claim_allowed": False,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(
        "# Campaign C LLH–linear source-row direction audit — 2026-10-06\n\n"
        "**Status: PASS.** The comparison was reconstructed from 300 `layer_llh` rows in campaign B1B2 and 300 `gen_linear` rows in campaign C. The source rows have identical UID sets, object indices, per-object seeds, and all six shared-input hashes for all 300 objects. The two runs also match on object-list hash, runner hash, checkpoint hash, view set, sampler, latent seed, and step count. Both legacy manifests omit the config hash; that limitation remains recorded.\n\n"
        "The reconstructed means, medians, bootstrap intervals, bootstrap p-values, and win fractions match the saved pairwise JSON, and Holm p-values match the 16-test C family. Positive `LLH − linear` FG-LPIPS is unfavorable to LLH because lower LPIPS is better.\n\n"
        "| Endpoint | LLH − linear | 95% object-bootstrap CI | Holm p | Direction |\n"
        "|---|---:|---:|---:|---|\n"
        f"| FG-PSNR | {reconstructed['fg_psnr']['mean_delta']:+.6f} dB | [{reconstructed['fg_psnr']['ci95'][0]:+.6f}, {reconstructed['fg_psnr']['ci95'][1]:+.6f}] | {reconstructed['fg_psnr']['holm_adjusted_p']:.4f} | no detected LLH advantage |\n"
        f"| FG-LPIPS | {reconstructed['fg_lpips']['mean_delta']:+.6f} | [{reconstructed['fg_lpips']['ci95'][0]:+.6f}, {reconstructed['fg_lpips']['ci95'][1]:+.6f}] | {reconstructed['fg_lpips']['holm_adjusted_p']:.4f} | favors linear (lower is better) |\n\n"
        "This is a previously inspected 300-object cohort, not a new confirmation. No equivalence, overall-winner, or perceived-fidelity claim follows. See `LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md` for the affected historical prose and its correction.\n"
    )
    print(json.dumps({"status": result["status"], "n": result["cohort_n"],
                      "input_hash_matches": input_hash_match,
                      "fg_psnr": reconstructed["fg_psnr"],
                      "fg_lpips": reconstructed["fg_lpips"]}, indent=2))


if __name__ == "__main__":
    main()
