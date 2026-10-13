# PRIMARY_HYPOTHESES — Phase III (pre-registered before any formal run)

- Date frozen: 2026-10-02
- Status: **FROZEN** before any FRESH_CONFIRM outcome is observed.
- Cohort: FRESH_CONFIRM_N (selection frozen per `COHORT_FREEZE.md`).
- Statistical unit: **object** (all CIs/tests are paired at object level).

## Global statistical rules

- Paired object-level bootstrap, **10,000 resamples**, bootstrap seed
  **20261002** (all analyses).
- Effect sizes reported as mean and median paired differences with **95% CI**
  and win rate (fraction of objects with positive paired effect in the
  favorable direction). P-values alone are never sufficient.
- **Holm correction** within each predefined confirmation family (below);
  families never mix experiments.
- No "equivalence" claim unless its margin is predeclared (see H2).
- The word "primary" applies ONLY to the hypotheses in this file.
- Metric implementations are exactly those of the authoritative Core-7
  runner/audit namespace (`core7_same_runner_completion_20261001` /
  `final_evidence_freeze_20261001`); the same LPIPS net, mask handling, and
  per-view aggregation are reused. No metric is re-tuned.

## Primary hypotheses

### H1 — Dose-normalized Layer × Time interaction (Experiment A3)

- Hypothesis: after residual-dose normalization, adapter-residual scaling
  effects depend jointly on UNet depth group and temporal window
  (Layer × Window interaction on ΔFG-LPIPS).
- Test: two-way (Layer 3 × Window 5) model on object-level paired deltas
  vs baseline; interaction tested with object-level cluster bootstrap
  (10,000 resamples).
- Primary metric: **FG-LPIPS**.
- Secondary: FG-PSNR, Full-PSNR, Full-LPIPS, FG-SSIM, Edge-SSIM, CIEDE2000,
  GT-relative Laplacian / RGB-std / gradient / HF-energy errors.
- Confirmation family A: 15 cell-wise ΔFG-LPIPS tests (intervention vs
  baseline) + 1 interaction test → Holm-corrected as one family (16 tests).
- Interpretation lock: if the interaction is not supported after dose
  normalization, NO general layer×timestep interaction may be claimed.

### H2 — LLH vs LFM-EXACT (Experiment B1)

- Hypothesis: LLH (temporal variation) beats LFM-EXACT (constant, exactly
  mean-matched per layer: deep/middle 1.675, shallow 0.585) on FG-PSNR.
- Directional test: ΔFG-PSNR = LLH − LFM-EXACT > 0.
- Predeclared equivalence margins (only for the "budget explains the gain"
  interpretation): |ΔFG-PSNR| CI ⊂ (−0.5, +0.5) dB AND |ΔFG-LPIPS| CI ⊂
  (−0.01, +0.01) → the temporal-variation advantage is declared
  budget-explained; otherwise the advantage (or disadvantage) stands as a
  temporal effect.
- Confirmation family B1: H2 on FG-PSNR (primary) + FG-LPIPS (secondary
  confirmation) → Holm family of 2.

### H3 — Temporal-location contrast (Experiment B2)

- Hypothesis: late-high (LLH) differs from early-high (HLL) and from
  double-low (LLL) with equal nominal high-duration (17 steps).
- Tests: ΔFG-PSNR(LLH−HLL), ΔFG-PSNR(LLH−LLL), same on FG-LPIPS.
- Confirmation family B2: 4 tests → Holm.

### H4 — LLH vs generic schedule family (Experiment C)

- Hypothesis: LLH outperforms the pre-frozen generic schedule family
  (linear warm-up, cosine bump, trapezoid, Gaussian peak; both
  endpoint-matched and budget-matched variants) under the SAME runner,
  cohort, seeds, and budget accounting.
- Primary metric FG-PSNR; secondary FG-LPIPS.
- Confirmation family C: one test per generic schedule (both variants
  pooled only if pre-specified as one comparison per schedule name) →
  family size = 4 schedules × 2 variants = 8 → Holm.
- No schedule parameters may be tuned on FRESH_CONFIRM_N.

### H5 — Prospective texture-complexity failure relationship (Experiment E)

- H0: ΔFG-PSNR(LLH−GFL) and ΔFG-LPIPS(LLH−GFL) are independent of GT-only
  texture complexity.
- Tests: Spearman rho (with bootstrap CI) between paired deltas and GT-only
  Laplacian variance / RGB std / gradient energy / HF energy / foreground
  coverage; texture-complexity quartile effects; win/loss rate by quartile.
- Confirmation family E: 2 metrics × 5 GT statistics = 10 Spearman tests →
  Holm.
- No result-based object exclusion is permitted.

## Secondary / descriptive (non-confirmatory)

- Experiment A2 raw (non-dose-normalized) map: descriptive only.
- TRUE-GLOBAL diagnostics (B3): causal decomposition, descriptive.
- Experiment F unified bake metrics: object-paired CIs per comparison;
  confirmatory only for the claim scope defined in CLAIM_TEST_MATRIX.md.
- Experiment G MV-Adapter replication: verdict options frozen in
  CLAIM_TEST_MATRIX.md; no mapping re-search after results.

## Deviation policy

Any deviation from this file must be recorded in
`DEVIATION_LOG.md` with rationale BEFORE the affected outcomes are inspected,
or the affected tests are demoted to exploratory.
