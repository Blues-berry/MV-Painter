#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) - valid interaction re-test on REAL data.

Runs the cluster-robust Wald interaction test (validated in
STATISTICAL_PIPELINE_UNIT_TESTS.json) on the real A2 and A3 per-object cell
deltas from the formal ledgers.
Output: AUDIT_INTERACTION_VALID_TEST.json
"""
import json
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


def load(camp):
    rows = []
    for s in range(4):
        p = V3 / "formal" / f"campaign_{camp}" / f"rows_shard{s}.json"
        if p.exists():
            rows += json.loads(p.read_text())
    return rows


def cell_matrix(rows, metric, prefix, base_cond):
    base = {r["object_idx"]: float(r[metric]) for r in rows
            if r["condition"] == base_cond}
    cells = {}
    for l in LAYERS:
        for w in WINDOWS:
            cond = f"{prefix}{l}_W{w}"
            cells[(l, w)] = {r["object_idx"]: float(r[metric])
                             for r in rows if r["condition"] == cond}
    idxs = sorted(base)
    M = np.array([[base[i] - cells[(l, w)][i] for i in idxs]
                  for l in LAYERS for w in WINDOWS])
    return M, len(idxs)


def main():
    out = {}
    for metric in ("fg_lpips", "fg_psnr"):
        for camp, prefix, basec in (("A2", "a_", "a_baseline"),
                                    ("A3", "a3_", "a3_baseline")):
            M, n = cell_matrix(load(camp), metric, prefix, basec)
            W, p = wald_interaction(M)
            tab = M.mean(axis=1).reshape(len(LAYERS), len(WINDOWS))
            grand = tab.mean()
            resid = tab - tab.mean(axis=1)[:, None] - tab.mean(axis=0)[None, :] + grand
            ss_int = float((resid ** 2).sum())
            ss_tot = float(((tab - grand) ** 2).sum())
            key = f"{camp}_{metric}"
            out[key] = {"n_objects": n, "W": round(W, 3), "p": p,
                        "interaction_ss_share": ss_int / ss_tot if ss_tot else 0.0,
                        "interaction_rmse_per_cell": float(np.sqrt(ss_int / 15))}
            print(f"{key}: W={W:.2f} p={p:.4g} intSS_share={out[key]['interaction_ss_share']:.3f}")
    (Path(__file__).parent / "AUDIT_INTERACTION_VALID_TEST.json").write_text(
        json.dumps(out, indent=2))
    print("wrote AUDIT_INTERACTION_VALID_TEST.json")


if __name__ == "__main__":
    main()
