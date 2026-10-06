#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) — §9 independent reproduction of A2 preliminary results.

Deliberately independent implementation (no import of analyze_v3.py):
source data = raw formal ledgers (rows_shard*.json), statistics re-derived
from scratch. Seed recorded. Recomputes:
  * 15 cell mean paired deltas (FG-LPIPS, FG-PSNR), 10k object-level
    percentile bootstrap CI, two-sided bootstrap p
  * Layer x Window interaction p via additive-model SS with object-cluster
    bootstrap null
  * Holm correction over the 16-test family (15 cells + interaction)

Reported claims to verify (LAYER_TIME_CAUSAL_MAP_REPORT.md / DECISION_REPORT):
  15/15 cells Holm-significant on FG-LPIPS; |delta| ~ 0.001-0.006;
  interaction p ~ 0.50 (FG-LPIPS) / 0.51 (FG-PSNR); middle_W5 ~ +0.52 dB.
Output: AUDIT_A2_REPRO.json next to this script.
"""
import json
import sys
from itertools import product
from pathlib import Path

import numpy as np

V3 = Path(__file__).resolve().parent.parent
SEED = 20261005  # audit's own seed (independent of analysis seed 20261002)
BOOT = 10_000
LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)


def load_campaign(name):
    rows = []
    for s in range(4):
        p = V3 / "formal" / f"campaign_{name}" / f"rows_shard{s}.json"
        if p.exists():
            rows.extend(json.loads(p.read_text()))
    return rows


def to_matrix(rows, metric, conditions):
    """dict[(condition)] -> np.array indexed by object_idx."""
    per = {c: {} for c in conditions}
    for r in rows:
        if r["condition"] in per:
            per[r["condition"]][r["object_idx"]] = float(r[metric])
    return {c: np.array([per[c][i] for i in sorted(per[c])]) for c in conditions}


def boot_p_two_sided(deltas, rng, n=BOOT):
    """Own implementation: percentile CI + 2*min(P(<=0), P(>=0)) with +1 smoothing."""
    d = np.asarray(deltas, dtype=np.float64)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    boots = d[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p_le = (np.sum(boots <= 0) + 1) / (n + 1)
    p_ge = (np.sum(boots >= 0) + 1) / (n + 1)
    return {"mean_delta": float(d.mean()), "median_delta": float(np.median(d)),
            "ci95": [float(lo), float(hi)], "p_boot": float(2 * min(p_le, p_ge))}


def holm(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, (m - i) * p)
        adj[k] = min(1.0, running)
    return adj


def interaction_p(cell_delta, objects, rng, n=BOOT):
    """T = sum over cells of (y - row_mean - col_mean + grand_mean)^2 on the
    object-level cell-delta matrix; null = object-cluster bootstrap resample."""
    cells = np.stack([cell_delta[(l, w)] for l in LAYERS for w in WINDOWS])  # (15, n_obj)
    L, N = cells.shape

    def ss(mat):
        grand = mat.mean()
        rowm = mat.mean(axis=1, keepdims=True)
        colm = mat.mean(axis=0, keepdims=True)
        resid = mat - rowm - colm + grand
        return float((resid ** 2).sum())

    t_obs = ss(cells)
    cnt = np.zeros(N, dtype=np.int64)
    boot_t = np.empty(n)
    for b in range(n):
        pick = rng.integers(0, N, size=N)
        cnt[:] = 0
        np.add.at(cnt, pick, 1)
        boot_t[b] = ss(cells[:, pick])
    p = float((np.sum(boot_t >= t_obs) + 1) / (n + 1))
    return t_obs, p


def main():
    rng = np.random.default_rng(SEED)
    rows = load_campaign("A2")
    conds = {r["condition"] for r in rows}
    cells = [f"a_{l}_W{w}" for l, w in product(LAYERS, WINDOWS)]
    missing = [c for c in ["a_baseline", *cells] if c not in conds]
    assert not missing, f"missing conditions: {missing}"

    out = {"seed": SEED, "n_boot": BOOT, "n_objects": None, "metrics": {}}
    for metric in ("fg_lpips", "fg_psnr"):
        mat = to_matrix(rows, metric, ["a_baseline", *cells])
        n_obj = len(mat["a_baseline"])
        out["n_objects"] = n_obj
        base = mat["a_baseline"]
        res = {}
        pvals = {}
        for cell in cells:
            d = base - mat[cell]  # improvement of cell over baseline in natural sign
            st = boot_p_two_sided(d, np.random.default_rng(SEED + hash(cell) % 1000))
            res[cell] = st
            pvals[cell] = st["p_boot"]
        # interaction on cell deltas (y = baseline - cell, per object)
        cell_delta = {k: base - mat[f"a_{k[0]}_W{k[1]}"]
                      for k in product(LAYERS, WINDOWS)}
        objects = np.arange(n_obj)
        t_l, p_l = interaction_p(cell_delta, objects, np.random.default_rng(SEED + 1))
        pvals["interaction"] = p_l
        adj = holm(pvals)
        for cell in cells:
            res[cell]["p_holm"] = adj[cell]
        res["interaction"] = {"T_obs": t_l, "p_boot": p_l, "p_holm": adj["interaction"]}
        n_sig = sum(1 for c in cells if adj[c] < 0.05)
        out["metrics"][metric] = {
            "cells": res,
            "n_cells_holm_significant": n_sig,
            "abs_mean_delta_range": [float(min(abs(res[c]["mean_delta"]) for c in cells)),
                                     float(max(abs(res[c]["mean_delta"]) for c in cells))],
        }
        print(f"[{metric}] holm-significant cells: {n_sig}/15, "
              f"|delta| range: {out['metrics'][metric]['abs_mean_delta_range']}, "
              f"interaction p={p_l:.3f}")
        if metric == "fg_psnr":
            st = res["a_middle_W5"]
            out["middle_W5_psnr"] = st
            print(f"middle_W5 FG-PSNR: {st['mean_delta']:+.4f} dB CI{st['ci95']}")

    # qualitative direction claims
    lp = out["metrics"]["fg_lpips"]["cells"]
    out["direction_checks"] = {
        "deep_early_W1_W2_lpips_sign": [float(np.sign(lp[f"a_deep_W{w}"]["mean_delta"])) for w in (1, 2)],
        "middle_late_W4_W5_lpips_sign": [float(np.sign(lp[f"a_middle_W{w}"]["mean_delta"])) for w in (4, 5)],
        "shallow_all_lpips_sign": [float(np.sign(lp[f"a_shallow_W{w}"]["mean_delta"])) for w in WINDOWS],
    }
    (Path(__file__).parent / "AUDIT_A2_REPRO.json").write_text(json.dumps(out, indent=2))
    print("wrote AUDIT_A2_REPRO.json")


if __name__ == "__main__":
    sys.exit(main())
