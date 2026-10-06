#!/usr/bin/env python3
"""P0-1 CLOSURE (2026-10-05) - valid interaction re-test on Experiment G data.

The production G interaction p = 0.58 (layermap_g.json) came from the same
zero-power object-resampling SS test as A2/A3 (P0-1 in
PRE_ACCEPTANCE_AUDIT_20261005.md). This script applies the validated
cluster-robust Wald test (audit_interaction_valid_test.py, size- and
power-checked in STATISTICAL_PIPELINE_UNIT_TESTS.json) to the G per-object
cell deltas.

Analysis-only: reads formal ledgers, writes only this audit's JSON.
Output: AUDIT_INTERACTION_VALID_TEST_G.json
"""
import json
import argparse
from pathlib import Path

import numpy as np
from scipy import stats as st

V3 = Path(__file__).resolve().parent.parent
LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)


def helmert(k):
    m = np.zeros((k - 1, k))
    for i in range(k - 1):
        m[i, : i + 1] = 1.0 / (i + 1)
        m[i, i + 1] = -1.0
    return m


def interaction_basis():
    Cr = np.linalg.qr(helmert(len(LAYERS)).T)[0].T
    Cc = np.linalg.qr(helmert(len(WINDOWS)).T)[0].T
    return np.kron(Cr, Cc)


A_INT = interaction_basis()


def wald_interaction(cells):
    n = cells.shape[1]
    means = cells.mean(axis=1)
    gamma = A_INT @ means
    g_dev = A_INT @ (cells - means[:, None])
    cov = (g_dev @ g_dev.T) / (n * (n - 1))
    cov += np.eye(8) * 1e-12 * max(1.0, np.trace(cov))
    W = float(gamma @ np.linalg.solve(cov, gamma))
    return W, float(st.chi2.sf(W, 8))


def load_g(run_dir):
    rows = []
    for p in sorted(Path(run_dir).glob("rows_shard*.json")):
        rows += json.loads(p.read_text())
    return rows


def cell_matrix(rows, metric):
    base = {r["object"]: float(r[metric]) for r in rows
            if r["condition"] == "g_baseline"}
    cells = {}
    for l in LAYERS:
        for w in WINDOWS:
            cond = f"g_{l}_W{w}"
            cells[(l, w)] = {r["object"]: float(r[metric])
                             for r in rows if r["condition"] == cond}
    idxs = sorted(base)
    M = np.array([[base[i] - cells[(l, w)][i] for i in idxs]
                  for l in LAYERS for w in WINDOWS])
    return M, len(idxs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, default=V3 / "g_formal")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "AUDIT_INTERACTION_VALID_TEST_G.json")
    args = ap.parse_args()
    rows = load_g(args.run_dir)
    conds = set(r["condition"] for r in rows)
    assert len(conds) == 16, f"expected 16 conditions, got {len(conds)}"
    out = {"n_rows": len(rows),
           "note": "production G interaction p=0.58 inherits the P0-1 "
                   "zero-power test; Wald re-test below"}
    for metric in ("fg_lpips", "psnr", "fg_ssim", "ciede2000"):
        M, n = cell_matrix(rows, metric)
        W, p = wald_interaction(M)
        tab = M.mean(axis=1).reshape(len(LAYERS), len(WINDOWS))
        grand = tab.mean()
        resid = tab - tab.mean(axis=1)[:, None] - tab.mean(axis=0)[None, :] + grand
        ss_int = float((resid ** 2).sum())
        ss_tot = float(((tab - grand) ** 2).sum())
        # layer/window marginal structure for interpretation
        row_means = tab.mean(axis=1)
        col_means = tab.mean(axis=0)
        key = f"G_{metric}"
        out[key] = {"n_objects": n, "W": round(W, 3), "p": p,
                    "interaction_ss_share": ss_int / ss_tot if ss_tot else 0.0,
                    "interaction_rmse_per_cell": float(np.sqrt(ss_int / 15)),
                    "layer_marginal_deltas": {l: float(row_means[i])
                                              for i, l in enumerate(LAYERS)},
                    "window_marginal_deltas": {f"W{w}": float(col_means[w - 1])
                                               for w in WINDOWS}}
        print(f"{key}: n={n} W={W:.3f} p={p:.4g} "
              f"intSS_share={out[key]['interaction_ss_share']:.4f}")
    metric_keys = {m: f"G_{m}" for m in ("fg_lpips", "psnr", "fg_ssim", "ciede2000")}
    ordered_p = sorted(metric_keys, key=lambda m: out[metric_keys[m]]["p"])
    adjusted, running = {}, 0.0
    for i, metric in enumerate(ordered_p):
        running = max(running, (len(ordered_p) - i) * out[metric_keys[metric]]["p"])
        adjusted[metric] = min(1.0, running)
    out["exploratory_metric_family_holm"] = {
        "method": "Holm-Bonferroni",
        "family_size": len(metric_keys),
        "adjusted_p": adjusted,
        "note": "Exploratory; Wald statistic selected after discovery of zero-power production bootstrap.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
