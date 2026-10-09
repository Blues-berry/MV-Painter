#!/usr/bin/env python3
"""Reproduce the A3 cluster-robust Wald interaction statistics from CSV rows."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from scipy import stats

LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)
METRICS = ("fg_lpips", "fg_psnr")

def helmert(k: int) -> np.ndarray:
    matrix = np.zeros((k - 1, k))
    for i in range(k - 1):
        matrix[i, :i + 1] = 1.0 / (i + 1)
        matrix[i, i + 1] = -1.0
    return matrix

def interaction_basis() -> np.ndarray:
    row = np.linalg.qr(helmert(len(LAYERS)).T)[0].T
    col = np.linalg.qr(helmert(len(WINDOWS)).T)[0].T
    return np.kron(row, col)

def read_condition(input_dir: Path, name: str) -> dict[str, dict[str, str]]:
    path = input_dir / f"{name}_per_object_metrics.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = {row["object_idx"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate object_idx in {path}")
    return result

def analyze(input_dir: Path) -> dict[str, dict[str, float | int]]:
    baseline = read_condition(input_dir, "a3_baseline")
    conditions = {
        f"a3_{layer}_W{window}": read_condition(input_dir, f"a3_{layer}_W{window}")
        for layer in LAYERS for window in WINDOWS
    }
    object_ids = sorted(baseline)
    if len(object_ids) != 300:
        raise ValueError(f"expected 300 A3 objects, found {len(object_ids)}")
    for name, records in conditions.items():
        if set(records) != set(object_ids):
            raise ValueError(f"object set mismatch in {name}")
    basis = interaction_basis()
    output = {}
    for metric in METRICS:
        # Keep the original audit's baseline-minus-cell orientation.
        cells = np.array([
            [float(baseline[obj][metric]) - float(conditions[f"a3_{layer}_W{window}"][obj][metric])
             for obj in object_ids]
            for layer in LAYERS for window in WINDOWS
        ])
        if not np.isfinite(cells).all():
            raise ValueError(f"non-finite values in {metric}")
        means = cells.mean(axis=1)
        gamma = basis @ means
        deviations = basis @ (cells - means[:, None])
        covariance = (deviations @ deviations.T) / (len(object_ids) * (len(object_ids) - 1))
        covariance += np.eye(8) * 1e-12 * max(1.0, float(np.trace(covariance)))
        wald = float(gamma @ np.linalg.solve(covariance, gamma))
        table = means.reshape(len(LAYERS), len(WINDOWS))
        residual = table - table.mean(axis=1)[:, None] - table.mean(axis=0)[None, :] + table.mean()
        ss_interaction = float((residual ** 2).sum())
        ss_total = float(((table - table.mean()) ** 2).sum())
        output[f"A3_{metric}"] = {
            "n_objects": len(object_ids),
            "W": round(wald, 3),
            "p": float(stats.chi2.sf(wald, 8)),
            "interaction_ss_share": ss_interaction / ss_total if ss_total else 0.0,
            "interaction_rmse_per_cell": float(np.sqrt(ss_interaction / 15)),
        }
    return output

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parent / "conditions")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(args.input_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

if __name__ == "__main__":
    main()
