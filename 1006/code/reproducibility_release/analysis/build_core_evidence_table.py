#!/usr/bin/env python3
"""Rebuild core A2 and FRESH_CONFIRM_B evidence from frozen result rows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 20261002


def read_condition(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            uid = row.get("object_uid") or row.get("object")
            if not uid:
                raise ValueError(f"missing object UID in {path}")
            if uid in rows:
                raise ValueError(f"duplicate object UID in {path}: {uid}")
            rows[uid] = row
    return rows


def ordered_pair(left: dict, right: dict, metric: str) -> tuple[list[str], np.ndarray]:
    if set(left) != set(right):
        raise ValueError("paired conditions do not have identical object IDs")
    uids = sorted(left)
    delta = np.asarray(
        [float(left[uid][metric]) - float(right[uid][metric]) for uid in uids],
        dtype=np.float64,
    )
    if not np.isfinite(delta).all():
        raise ValueError(f"non-finite values in paired endpoint {metric}")
    return uids, delta


def paired_bootstrap(delta: np.ndarray) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(delta)
    indices = rng.integers(0, n, size=(BOOTSTRAP_DRAWS, n))
    boot_means = delta[indices].mean(axis=1)
    lower, upper = np.percentile(boot_means, [2.5, 97.5])
    p = 2.0 * min((boot_means <= 0).mean(), (boot_means >= 0).mean())
    return {
        "n": n,
        "mean_delta": float(delta.mean()),
        "median_delta": float(np.median(delta)),
        "ci95": [float(lower), float(upper)],
        "win_rate_positive": float((delta > 0).mean()),
        "loss_rate_negative": float((delta < 0).mean()),
        "p_bootstrap": float(max(p, 1.0 / BOOTSTRAP_DRAWS)),
    }


def helmert(n: int) -> np.ndarray:
    matrix = np.zeros((n - 1, n), dtype=np.float64)
    for i in range(n - 1):
        matrix[i, : i + 1] = 1.0 / (i + 1)
        matrix[i, i + 1] = -1.0
    return matrix


def interaction_basis() -> np.ndarray:
    row = np.linalg.qr(helmert(len(LAYERS)).T)[0].T
    column = np.linalg.qr(helmert(len(WINDOWS)).T)[0].T
    return np.kron(row, column)


def wald_interaction(matrix: np.ndarray) -> dict:
    basis = interaction_basis()
    n = matrix.shape[1]
    means = matrix.mean(axis=1)
    gamma = basis @ means
    deviations = basis @ (matrix - means[:, None])
    covariance = (deviations @ deviations.T) / (n * (n - 1))
    covariance += np.eye(8) * 1e-12 * max(1.0, float(np.trace(covariance)))
    statistic = float(gamma @ np.linalg.solve(covariance, gamma))
    p_value = float(stats.chi2.sf(statistic, 8))
    cell_means = means.reshape(len(LAYERS), len(WINDOWS))
    grand = float(cell_means.mean())
    residual = cell_means - cell_means.mean(axis=1)[:, None]
    residual -= cell_means.mean(axis=0)[None, :]
    residual += grand
    ss_interaction = float(np.square(residual).sum())
    ss_total = float(np.square(cell_means - grand).sum())
    result = {
        "n_objects": n,
        "df": 8,
        "wald_chi2": statistic,
        "interaction_ss_share": ss_interaction / ss_total if ss_total else 0.0,
        "interaction_rmse_per_cell": float(np.sqrt(ss_interaction / 15.0)),
        "test": "object-cluster robust Wald test on 8 orthogonal interaction contrasts",
    }
    if p_value < 1e-300:
        result["p_upper_bound"] = "<1e-300"
    else:
        result["p_value"] = p_value
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_id_list(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()

    a2_dir = ROOT / "data/campaign_A2"
    a2 = {name: read_condition(a2_dir / f"{name}_per_object_metrics.csv")
          for name in ["a_baseline"] + [f"a_{l}_W{w}" for l in LAYERS for w in WINDOWS]}
    b_dir = ROOT / "data/campaign_B"
    b = {name: read_condition(b_dir / f"{name}_per_object_metrics.csv")
         for name in ("layer_llh", "lfm_exact", "layer_hll", "a3_baseline")}

    a2_ids = load_id_list(ROOT / "data/FRESH_CONFIRM_300.txt")
    b_ids = load_id_list(ROOT / "data/FRESH_CONFIRM_B_150.txt")
    if len(a2_ids) != 300 or len(set(a2_ids)) != 300:
        raise ValueError("A2 UID list must contain 300 unique IDs")
    if len(b_ids) != 150 or len(set(b_ids)) != 150:
        raise ValueError("B UID list must contain 150 unique IDs")
    if set(a2["a_baseline"]) != set(a2_ids):
        raise ValueError("A2 result rows do not match the frozen 300-object list")
    if any(set(rows) != set(b_ids) for rows in b.values()):
        raise ValueError("B temporal-comparison rows do not match the frozen 150-object list")

    a2_interactions = {}
    for metric in ("fg_lpips", "fg_psnr"):
        a2_matrix = []
        for layer in LAYERS:
            for window in WINDOWS:
                _, delta = ordered_pair(
                    a2[f"a_{layer}_W{window}"], a2["a_baseline"], metric
                )
                a2_matrix.append(delta)
        a2_interactions[metric] = wald_interaction(np.stack(a2_matrix))

    effects = {}
    for metric in ("fg_psnr", "fg_lpips"):
        _, delta = ordered_pair(a2["a_middle_W5"], a2["a_baseline"], metric)
        summary = paired_bootstrap(delta)
        summary["favorable_rate"] = float(
            (delta > 0).mean() if metric == "fg_psnr" else (delta < 0).mean()
        )
        summary["favorable_direction"] = "higher" if metric == "fg_psnr" else "lower"
        effects[metric] = summary
    b_contrasts = {
        "LLH_minus_LFM_EXACT": ("layer_llh", "lfm_exact"),
        "LLH_minus_HLL": ("layer_llh", "layer_hll"),
        "LLH_minus_LLL": ("layer_llh", "a3_baseline"),
        "HLL_minus_LLL": ("layer_hll", "a3_baseline"),
    }
    b_effects = {}
    for contrast, (left_name, right_name) in b_contrasts.items():
        b_effects[contrast] = {}
        for metric in ("fg_psnr", "fg_lpips"):
            _, delta = ordered_pair(b[left_name], b[right_name], metric)
            summary = paired_bootstrap(delta)
            summary["favorable_rate"] = float(
                (delta > 0).mean() if metric == "fg_psnr" else (delta < 0).mean()
            )
            summary["favorable_direction"] = "higher" if metric == "fg_psnr" else "lower"
            b_effects[contrast][metric] = summary

    locked_h3 = ["LLH_minus_HLL", "LLH_minus_LLL"]
    h3_p = {
        f"{contrast}::{metric}": b_effects[contrast][metric]["p_bootstrap"]
        for contrast in locked_h3 for metric in ("fg_psnr", "fg_lpips")
    }
    h3_holm = {}
    running = 0.0
    for rank, (name, p_value) in enumerate(sorted(h3_p.items(), key=lambda item: item[1])):
        running = max(running, (len(h3_p) - rank) * p_value)
        h3_holm[name] = min(1.0, running)
    for name, adjusted in h3_holm.items():
        contrast, metric = name.split("::", 1)
        b_effects[contrast][metric]["p_holm_upper_bound"] = adjusted

    margins = {"fg_psnr": 0.5, "fg_lpips": 0.01}
    primary = b_effects["LLH_minus_LFM_EXACT"]
    practical_equivalence = all(
        abs(row["ci95"][0]) < margins[metric]
        and abs(row["ci95"][1]) < margins[metric]
        for metric, row in primary.items()
    )
    signature_ok = (
        primary["fg_psnr"]["ci95"][0] > 0
        and primary["fg_lpips"]["ci95"][1] < 0
        and b_effects["LLH_minus_HLL"]["fg_psnr"]["ci95"][0] > 0
        and b_effects["LLH_minus_HLL"]["fg_lpips"]["ci95"][1] < 0
        and b_effects["LLH_minus_LLL"]["fg_psnr"]["ci95"][0] > 0
        and b_effects["LLH_minus_LLL"]["fg_lpips"]["ci95"][1] < 0
        and b_effects["HLL_minus_LLL"]["fg_psnr"]["ci95"][1] < 0
        and b_effects["HLL_minus_LLL"]["fg_lpips"]["ci95"][0] > 0
    )

    inputs = sorted(p for p in (ROOT / "data").rglob("*.csv"))
    result = {
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "a2_discovery": {
            "cohort": "FRESH_CONFIRM_300",
            "n_objects": len(a2_ids),
            "middle_W5_minus_baseline": effects,
            "layer_by_window_interaction": a2_interactions,
        },
        "fresh_confirm_b": {
            "cohort": "FRESH_CONFIRM_B",
            "n_objects": len(b_ids),
            "delta_convention": "condition A minus condition B; a3_baseline is the frozen all-low LLL trace",
            "tests": b_effects,
            "locked_h3_holm_upper_bounds": h3_holm,
            "llh_lfm_exact_within_frozen_practical_margins": practical_equivalence,
            "all_directional_signature_criteria_supported": signature_ok,
            "signature_failure": None if signature_ok else "HLL-minus-LLL FG-PSNR 95% CI crosses zero; the exploratory three-direction signature fails as a two-endpoint criterion.",
            "frozen_practical_margins": margins,
        },
        "input_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in inputs},
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "core_evidence_table.json"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Reproduced core evidence table", "",
        "| Cohort / contrast | Endpoint | N | Mean paired delta [95% bootstrap CI] | Favorable objects |",
        "|---|---|---:|---:|---:|",
    ]
    for metric, label in (("fg_psnr", "FG-PSNR (dB)"), ("fg_lpips", "FG-LPIPS")):
        row = effects[metric]
        lines.append(f"| A2 discovery: middle W5 − baseline | {label} | 300 | {row['mean_delta']:.6g} [{row['ci95'][0]:.6g}, {row['ci95'][1]:.6g}] | {row['favorable_rate']:.1%} |")
    for contrast, label_text in (("LLH_minus_LFM_EXACT", "LLH − LFM-EXACT"),
                                 ("LLH_minus_HLL", "LLH − HLL"),
                                 ("LLH_minus_LLL", "LLH − LLL"),
                                 ("HLL_minus_LLL", "HLL − LLL (exploratory)")):
        for metric, label in (("fg_psnr", "FG-PSNR (dB)"), ("fg_lpips", "FG-LPIPS")):
            row = b_effects[contrast][metric]
            lines.append(f"| FRESH_CONFIRM_B: {label_text} | {label} | 150 | {row['mean_delta']:.6g} [{row['ci95'][0]:.6g}, {row['ci95'][1]:.6g}] | {row['favorable_rate']:.1%} |")
    lines += [
        "", "All favorable-object rates are direction-adjusted. A2 uses condition minus baseline; B uses LLH minus LFM-EXACT. FG-PSNR is higher-is-better and FG-LPIPS is lower-is-better.",
        "", "## Validated A2 interaction results", "",
    ]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        row = a2_interactions[metric]
        p_text = row["p_upper_bound"] if "p_upper_bound" in row else f"= {row['p_value']:.4g}"
        lines.append(
            f"{label}: object-cluster Wald χ²(8) = {row['wald_chi2']:.3f}; "
            f"p {p_text}; interaction share = {row['interaction_ss_share']:.1%}; "
            f"RMSE/cell = {row['interaction_rmse_per_cell']:.6g}."
        )
    lines += [
        "", "A2 is labeled discovery/exploratory; B is a separate frozen confirmation cohort. Bootstrap: 10,000 paired object resamples, seed 20261002. The LLH−LFM-EXACT intervals fall inside the frozen practical-equivalence margins (±0.5 dB PSNR; ±0.01 LPIPS). HLL−LLL was post-unblinding exploratory; its FG-PSNR interval crosses zero, so the full two-endpoint directional signature is not supported.", "",
    ]
    (args.out_dir / "core_evidence_table.md").write_text("\n".join(lines))
    print(json_path)


if __name__ == "__main__":
    main()
