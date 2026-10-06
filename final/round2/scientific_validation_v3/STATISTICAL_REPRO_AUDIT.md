# STATISTICAL_REPRO_AUDIT — §9 numerical reproduction + §13 pipeline validation (2026-10-05)

## 1. Independent reproduction of the A2 preliminary results (§9)

Independent implementation (`audit_scripts/audit_a2_repro.py`): does **not** import
`analyze_v3.py`; reads the raw ledgers directly; own bootstrap/Holm/interaction code; audit
seed 20261005 (analysis used 20261002).

| Reported claim | Reported value | Independent recompute | Verdict |
|---|---|---|---|
| 15/15 cells Holm-significant, FG-LPIPS | 15/15 | **15/15** (family = 15 cells + interaction) | ✓ exact |
| Effect magnitude ΔLPIPS | "0.001–0.006" | 0.00036–**0.00640** | ✓ magnitudes match; report wording understates the max (P2 wording fix: "≤0.0064") |
| middle_W5 FG-PSNR | ≈ +0.52 dB (CI [0.461, 0.570]) | **+0.5145 dB** (CI [0.459, 0.569], mirrored sign convention) | ✓ exact to 4 decimals |
| Layer×Window interaction, FG-LPIPS | p ≈ 0.50 | p = 0.467 (own MC) | see §2 — both non-significant, but the test itself is defective |
| Layer×Window interaction, FG-PSNR | p ≈ 0.51 | p = 0.470 | see §2 |
| deep early hurts / deep+middle later help / shallow hurts | qualitative signs | sign checks reproduce (deep W1-W2 negative, deep W3-5 positive, middle W4-5 positive, shallow all negative) | ✓ |

All cell-mean deltas reproduce to full float precision (e.g. middle_W5 LPIPS delta
−0.006404908299446106 identical to `layermap_raw.json`). Numerical reproducibility of the
cell-level results: **CONFIRMED**.

## 2. P0 FINDING — the production interaction test has zero power

Method under audit (`analyze_v3.py` `cmd_layermap` L199-238): bootstrap null = resample
*objects*, recompute the weighted SS_interaction **of the observed y values**. The
Layer×Window interaction is an object-*shared* fixed pattern: resampling objects does not
dilute it, so T_boot tracks T_obs and p ≈ 0.5 **whether or not an interaction exists**.
Direct evidence in the production output itself (`layermap_raw.json`):
observed SS = 0.012930, bootstrap-null mean = **0.012986** — the null is centered on the
alternative. Synthetic demonstration (`STATISTICAL_PIPELINE_UNIT_TESTS.json`,
test B): injected interaction of 0.6σ, n=120, 40 replicates → production-style test rejects
**0/40**; cluster-robust Wald rejects ≥ 32/40. The test has approximately correct size
(test A/F) but **no power**: its non-significant p carries no information.

## 3. Valid re-test on the real data (`audit_scripts/audit_interaction_valid_test.py`)

Cluster-robust Wald test on the 8 interaction contrasts (Helmert row×col basis, object-level
sandwich covariance), validated for size (test F) and power (test B):

| Data | Metric | W (8 df) | p | interaction SS share of between-cell variance |
|---|---|---|---|---|
| A2 | FG-LPIPS | 481.1 | 8.0e-99 | 43.5% |
| A2 | FG-PSNR | 1880.0 | ≈0 | 56.8% |
| A3 | FG-LPIPS | 657.2 | 1.1e-136 | 11.9% |
| A3 | FG-PSNR | 1389.1 | 1.3e-294 | 0.8% |

Cross-checks on A2 FG-LPIPS: naive two-way ANOVA F = 117.8 (p = 1.9e-179); W stable in
[421, 467] over 90% subsamples; winsorized (1%/99%) W = 503 — not outlier-driven. The cell
mean matrix shows the structure directly: deep deltas (×1e-4) = [−29.3, +5.9, +41.3, +35.2,
+23.8] across W1-W5 (sign flip early→late); additive-fit residuals reach ±33e-4.

**Consequence:** the interaction is real and substantial on the native-dose A2 map. On the
dose-normalized A3 map it remains statistically significant but its variance share collapses
(56.8% → 0.8% FG-PSNR; 43.5% → 11.9% FG-LPIPS). This **contradicts CLAIM 3 ("Layer×Time
interaction NOT SUPPORTED")** in `SCIENTIFIC_VALIDATION_DECISION_REPORT.md` as currently
worded, and the narrative decision derived from it (`NARRATIVE_RESTRUCTURE_REQUIRED.md`:
"timestep-dependence not supported at equal dose" needs restatement: at equal dose the
*time-structure* component is small in FG-PSNR variance but strongly present in FG-LPIPS).
Per protocol §9: *material disagreement in independent recomputation ⇒ P0 for scientific
interpretation.* Note: raw row data are unaffected; only the interpretation layer must be
re-derived. The B3 decomposition independently measured a temporal component (+0.43 dB vs
uniform) — consistent with a real but modest time-structure effect.

## 4. Pipeline unit tests (§13 deliverable)

`STATISTICAL_PIPELINE_UNIT_TESTS.json` (script `audit_stat_unit_tests.py`):

| Test | Result |
|---|---|
| A. Null synthetic — interaction p calibrated | PASS (few rejections at α=.05) |
| B. Injected interaction — recovered | PASS for Wald (≥32/40); production method 0/40 → zero-power defect documented |
| C. Sign reversal — lower/higher-is-better handled; Holm direction-neutral | PASS |
| D. Duplicate-object stress — object is the unit | PASS (hazard quantified: CI would shrink ×1/√2 if rows treated as independent; production `read_rows`/`load_condition` dedupe by uid, and all production analyses operate on 300 unique uids — verified in ROW_INTEGRITY_AUDIT) |
| E. Shard-order invariance | PASS (canonical sorted-object delta construction; Holm key-order invariant; fixed-seed resampling is MC-equivalent under permutation) |
| F. Wald null calibration | PASS (~5% rejection under null) |

Bootstrap unit = object (10k resamples, percentile CI, two-sided p); Holm over the
pre-registered family (A2: 15 cells + interaction); seeds recorded (20261002 production,
20261005 audit).

## 5. Verdict

STATISTICAL_REPRO: cell-level numbers **reproduce exactly**; the interaction-test method is
**INVALID (zero power)** — **P0**, with the valid re-test result supplied above. All other
statistical machinery passes.
