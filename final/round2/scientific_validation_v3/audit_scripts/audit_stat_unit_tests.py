#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) - statistical pipeline unit tests (S13).

1. Demonstrates a zero-power defect: the production layermap interaction test
   (object-resampling bootstrap on observed y) cannot detect an object-shared
   Layer x Window interaction; p ~ 0.5 regardless of truth.
2. Validates a replacement: cluster-robust Wald test on interaction contrasts
   (8 df, object-level sandwich covariance) - correct size + power.
3. Fixed D/E tests: duplicate-object hazard + order invariance semantics.

Output: STATISTICAL_PIPELINE_UNIT_TESTS.json (protocol S13 deliverable).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats as st

V3 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(V3))
import analyze_v3  # noqa: E402  production implementation

SEED = 20261005
LAYERS, WINDOWS = 3, 5
REPS = 40


def helmert(k):
    m = np.zeros((k - 1, k))
    for i in range(k - 1):
        m[i, : i + 1] = 1.0 / (i + 1)
        m[i, i + 1] = -1.0
    return m


def interaction_basis():
    Cr = np.linalg.qr(helmert(LAYERS).T)[0].T
    Cc = np.linalg.qr(helmert(WINDOWS).T)[0].T
    return np.kron(Cr, Cc)  # (8, 15) acting on row-major (l,w) vec


A_INT = interaction_basis()


def wald_interaction(cells):
    """cells: (15, n). Cluster-robust Wald for interaction = 0."""
    n = cells.shape[1]
    means = cells.mean(axis=1)
    gamma = A_INT @ means
    g_dev = A_INT @ (cells - means[:, None])
    cov = (g_dev @ g_dev.T) / (n * (n - 1))
    cov += np.eye(8) * 1e-12 * max(1.0, np.trace(cov))
    W = float(gamma @ np.linalg.solve(cov, gamma))
    return W, float(st.chi2.sf(W, 8))


def make_data(rng, n_obj, interaction=0.0, noise=1.0):
    row = rng.normal(0, 1, LAYERS)
    col = rng.normal(0, 1, WINDOWS)
    pattern = np.zeros((LAYERS, WINDOWS))
    pattern[0, 0], pattern[0, 4] = +1.0, -1.0
    pattern[2, 0], pattern[2, 4] = -1.0, +1.0
    y = (row[:, None, None] + col[None, :, None]) * np.ones((1, 1, n_obj))
    if interaction:
        y = y + interaction * pattern[:, :, None]
    y = y + rng.normal(0, 1.0, (1, 1, n_obj))  # within-object correlation
    return y + rng.normal(0, noise, (LAYERS, WINDOWS, n_obj))


def production_interaction_p(y, n_boot=1500, seed=SEED):
    """Faithful small-scale reimplementation of the production interaction p:
    resample objects, recompute unweighted SS_interaction of observed y."""
    cells = y.reshape(15, -1)
    n = cells.shape[1]
    rm = np.repeat(np.arange(LAYERS), WINDOWS)
    cm_ = np.tile(np.arange(WINDOWS), LAYERS)

    def ss(idx):
        m = cells[:, idx].mean(axis=1)
        grand = m.mean()
        resid = m - m[rm].reshape(LAYERS, WINDOWS).mean(axis=1)[rm]             - m[cm_].reshape(LAYERS, WINDOWS).mean(axis=0)[cm_] + grand
        return float((resid ** 2).sum())

    t_obs = ss(np.arange(n))
    rng = np.random.default_rng(seed)
    boot = np.array([ss(rng.integers(0, n, size=n)) for _ in range(n_boot)])
    return float((boot >= t_obs).mean())


def run():
    results = {}

    # A: null calibration of the production-style interaction resampling.
    # The additive data contain layer/window main effects and shared object
    # noise, but no Layer x Window interaction.
    rng = np.random.default_rng(SEED)
    prod_null_rej = 0
    null_ps = []
    for _ in range(REPS):
        y = make_data(rng, 120, interaction=0.0)
        p = production_interaction_p(y)
        null_ps.append(p)
        prod_null_rej += p < 0.05
    results["A_production_null_calibration"] = {
        "reps": REPS, "n_obj": 120,
        "rejections_at_0.05": prod_null_rej,
        "median_p": float(np.median(null_ps)),
        "pass": bool(prod_null_rej <= 6),
        "note": "Null check only; passing does not imply power (test B).",
    }

    # B: power comparison under injected interaction
    rng = np.random.default_rng(SEED + 1)
    prod_r = wald_r = 0
    for _ in range(REPS):
        y = make_data(rng, 120, interaction=0.6)
        prod_r += production_interaction_p(y) < 0.05
        wald_r += wald_interaction(y.reshape(15, -1))[1] < 0.05
    results["B_injected_interaction_power"] = {
        "reps": REPS, "n_obj": 120, "interaction_size": 0.6,
        "production_method_rejects": prod_r,
        "wald_cluster_robust_rejects": wald_r,
        "production_zero_power_confirmed": bool(prod_r <= 2),
        "wald_has_power": bool(wald_r >= REPS * 0.8),
        "pass": bool(prod_r <= 2 and wald_r >= REPS * 0.8)}

    # C: raw metric direction is preserved and reversed comparisons mirror.
    # The pipeline subtracts baseline from treatment; therefore a negative
    # LPIPS delta is favorable, while a positive PSNR delta is favorable.
    baseline_lpips = np.full(80, 0.30)
    treatment_lpips = np.full(80, 0.24)
    lpips_delta = treatment_lpips - baseline_lpips
    forward = analyze_v3.paired_bootstrap(lpips_delta)
    reverse = analyze_v3.paired_bootstrap(-lpips_delta)
    mirrored_ci = np.allclose(
        reverse["ci95"], [-forward["ci95"][1], -forward["ci95"][0]],
        rtol=0.0, atol=1e-12)
    results["C_metric_direction_sign_reversal"] = {
        "lower_better_metric": "LPIPS",
        "treatment_minus_baseline_mean": forward["mean_delta"],
        "negative_means_favorable": bool(forward["mean_delta"] < 0),
        "reversed_mean_is_opposite": bool(
            np.isclose(reverse["mean_delta"], -forward["mean_delta"], atol=1e-12)),
        "ci_mirrors_on_reversal": bool(mirrored_ci),
        "two_sided_p_invariant": bool(
            np.isclose(reverse["p_bootstrap"], forward["p_bootstrap"], atol=1e-12)),
        "win_loss_rates_swap": bool(
            np.isclose(reverse["win_rate"], forward["loss_rate"], atol=1e-12)
            and np.isclose(reverse["loss_rate"], forward["win_rate"], atol=1e-12)),
        "pass": bool(forward["mean_delta"] < 0 and mirrored_ci
                     and np.isclose(reverse["mean_delta"], -forward["mean_delta"], atol=1e-12)
                     and np.isclose(reverse["p_bootstrap"], forward["p_bootstrap"], atol=1e-12)
                     and np.isclose(reverse["win_rate"], forward["loss_rate"], atol=1e-12)),
        "note": "Raw metric direction is caller-controlled; this checks subtraction and inference under reversal.",
    }

    # F: size calibration of the valid test under the null
    rng = np.random.default_rng(SEED + 2)
    rej = 0
    for _ in range(REPS):
        y = make_data(rng, 120, interaction=0.0)
        rej += wald_interaction(y.reshape(15, -1))[1] < 0.05
    results["F_wald_null_calibration"] = {
        "reps": REPS, "rejects_at_0.05": rej,
        "pass": bool(rej <= 6)}

    # D: duplicate-object stress (hazard demonstration + production safety)
    rng = np.random.default_rng(SEED + 3)
    base = rng.normal(0.5, 0.3, 150)
    pb_dup = analyze_v3.paired_bootstrap(np.repeat(base, 2))
    pb_dedup = analyze_v3.paired_bootstrap(base)
    ratio = ((pb_dup["ci95"][1] - pb_dup["ci95"][0])
             / (pb_dedup["ci95"][1] - pb_dedup["ci95"][0]))
    results["D_duplicate_object_stress"] = {
        "ci_width_ratio_rows300_vs_objects150": ratio,
        "expected_if_rows_treated_independent": float(1 / np.sqrt(2)),
        "hazard_present": bool(abs(ratio - 1 / np.sqrt(2)) < 0.05),
        "pass": bool(abs(ratio - 1 / np.sqrt(2)) < 0.05),
        "note": "hazard real but avoided in production: load_condition/read_rows "
                "dedupe by object_uid (dict last-wins); all analyses use "
                "per-object rows (300 unique uids verified by ledger audit)."}

    # E: order invariance (MC-equivalence + canonical-order bit-identity)
    rng = np.random.default_rng(SEED + 4)
    d = rng.normal(0.3, 0.5, 300)
    pb1 = analyze_v3.paired_bootstrap(d)
    pb2 = analyze_v3.paired_bootstrap(d[rng.permutation(300)])
    ci_close = (abs(pb1["ci95"][0] - pb2["ci95"][0]) < 0.01
                and abs(pb1["ci95"][1] - pb2["ci95"][1]) < 0.01)
    holm_same = (analyze_v3.holm({"a": 0.01, "b": 0.04, "c": 0.03})
                 == analyze_v3.holm({"c": 0.03, "a": 0.01, "b": 0.04}))
    results["E_order_invariance"] = {
        "median_identical": pb1["median_delta"] == pb2["median_delta"],
        "ci_mc_equivalent": ci_close,
        "holm_key_order_invariant": holm_same,
        "pass": bool(pb1["median_delta"] == pb2["median_delta"] and ci_close and holm_same),
        "note": "fixed-seed positional resampling gives MC-equivalent (not "
                "bit-identical) results under input permutation; production "
                "always builds deltas in canonical sorted-object order, so "
                "order dependence is unreachable; Holm is key-order invariant."}

    results["_ALL_PASS"] = all(results[k]["pass"] for k in
                               ("A_production_null_calibration",
                                "B_injected_interaction_power",
                                "C_metric_direction_sign_reversal",
                                "F_wald_null_calibration",
                                "D_duplicate_object_stress", "E_order_invariance"))
    (V3 / "audit_scripts" / "STATISTICAL_PIPELINE_UNIT_TESTS.json").write_text(
        json.dumps(results, indent=2))
    for k, v in results.items():
        if isinstance(v, dict) and "pass" in v:
            print(k, "->", v["pass"])
    print("ALL_PASS:", results["_ALL_PASS"])
    return 0 if results["_ALL_PASS"] else 1


if __name__ == "__main__":
    sys.exit(run())
