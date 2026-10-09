# A3_DOSE_VALIDITY_AUDIT — §10 status + extreme-dose validity (2026-10-05)

Script: `audit_scripts/audit_a3_dose_and_residuals.py`; machine-readable results in
`audit_scripts/AUDIT_A3_DOSE_VALIDITY.json`.

## 1. Status

A3 = **COMPLETE**: 4800 rows (16 conditions × 300 objects), ledger/CSV consistent,
integrity PASS (ROW_INTEGRITY_AUDIT), identity PROVEN (INPUT_IDENTITY_AUDIT).
`a3_baseline` is bit-identical to A2 `a_baseline` on all metrics for all 300 objects —
cross-campaign determinism anchor.

## 2. Frozen spec re-derivation (§8 manual residual recompute)

From the probe-24 dev residual logs (24 objects × `a_baseline`, 50 steps × per-wrapper l2):
recomputed `window_M`, `mean_M`, `C = 1.25·mean(M_deep)`, and
`high_l = LOW_l + C/mean(M_l)` — **all match `a3_normalization.json` to relative error 0.0**
(frozen 10-02 11:32, ~47 h before A3 results; `frozen_before_fresh_evaluation: true`).

Residual-log semantics (code-verified, `model_unet_geotex.py` L349-366 + runner L269-274):
the logged per-step quantity is `_last_correction` = the correction **actually injected into
the hidden state — post-scale, post-cap** (uncapped path: post-scale, cap bypassed);
requested `scale` and effective `eff_scale` are logged alongside per wrapper, so pre-scale /
post-scale quantities are never conflated. Integrated norm E_l = sqrt(Σ_t R_l,t²) per
`analyze_residual_budgets.py` matches the spec rule. **§8 verdict: semantics correct.**

## 3. Measured dose-regime evidence (60 deterministic objects; 300-object metric rates)

| Condition | Requested scale vs native high | Integrated residual E (intervention layer) | E ratio vs A2 same-window condition |
|---|---|---|---|
| a3_deep_W3   | 2.50 / 2.50 = 1.0×  | 5.82e8 (deep)    | **1.00×** (bit-identical regime) |
| a3_middle_W3 | 6.84 / 2.50 = 2.73× | 1.82e8 (middle)  | 5.12× (superlinear in scale) |
| a3_shallow_W3| 30.38 / 0.75 = 40.5×| 1.12e9 (shallow) | **1394×** (strongly superlinear) |

Metric regime over all 300 objects (audit-defined thresholds, documented in the JSON):

| Condition | fg_psnr drop >3 dB | color collapse (entropy<0.5 or rgb_std<0.01) | fg_lpips worse >0.10 | extreme-pixel fraction (24-object PNG sample) |
|---|---|---|---|---|
| a3_deep_W3    | 0.0%  | 0.0% | 0.0% | — |
| a3_middle_W3  | 0.0%  | 0.0% | 0.0% | 5.4% (baseline 4.8%) |
| a3_shallow_W3 | **65.3%** | 2.0% | 8.7% | **76.9%** |

NaN/Inf in A3 ledger: 0 rows (ROW_INTEGRITY_AUDIT).

## 4. Classification (per frozen condition, not per campaign)

- **deep (2.50)**: `VALID_DOSE_NORMALIZED_CONFIRMATION` — identical to the native high-dose
  regime (cap 3.0 not binding; `uncapped` flag immaterial at 2.5).
- **middle (6.84)**: `DOSE_NORMALIZED_DIAGNOSTIC (with caveat)` — outputs remain a local
  perturbation (no collapse, saturation ≈ baseline), but the frozen linear normalization
  under-corrects for the measured superlinearity (E ratio 5.1× where the request ratio is
  2.73×); treat "equal dose" as approximate for middle.
- **shallow (30.38)**: `STRESS_TEST_ONLY` — 1394× the native-high integrated residual,
  65% of objects lose >3 dB PSNR, 77% of output pixels at the dynamic-range extremes. This
  is a qualitatively different saturation regime, **not** a local perturbation and **not**
  a dose-normalized confirmation. Statements about shallow high-dose behavior must be
  worded as stress observations.

## 5. Consequences for the decision report

- CLAIM 1's "shallow uniformly harmful" remains *observationally* true but is a
  stress-regime statement; deep/middle components keep their confirmatory reading.
- The "dose-normalized interaction p = 1.0" quoted for A3 inherits the P0 interaction-test
  defect (see STATISTICAL_REPRO_AUDIT §2-3): the valid Wald test on A3 gives p ≈ 1e-136
  (FG-LPIPS) / ≈0 (FG-PSNR) with much smaller variance shares than A2 — the correct
  statement is "interaction present but variance-share strongly reduced at matched dose",
  not "not supported".
- No A3 row needs rerunning; no A3 artifact is invalid.

## 6. Verdict

A3_DOSE_VALIDITY: **VALID WITH CLASSIFICATION** — deep = confirmation, middle = diagnostic
(approximate dose normalization), shallow = stress test only. Data integrity and provenance
are fully admissible.
