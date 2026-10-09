# A3b bounded-dose confirmation protocol lock

Frozen: 2026-10-05 08:39 UTC, before any FRESH_CONFIRM_B method output.

## Question and scope

Estimate the 3-layer × 5-window response under a small, cap-compliant,
10-step layer-specific intervention. This A3b is a **bounded-dose map**. The
residual-only development calibration failed the preregistered ±20% balance
criterion, so results must not be described as equal-dose or dose-normalized
confirmation. No high value may be retuned after this lock.

## Frozen development dose and calibration

- Development-only candidate spec:
  `a3b_development_residual_only/A3B_CANDIDATE_HIGHS.json`, SHA256
  `68125f9ee9645225387ef9d034f934154d6c4c461b29d7162218a224c0cc89a0`.
- Baseline scales: deep=1.25, middle=1.25, shallow=0.50.
- Candidate highs: deep=1.2625505713698246, middle=1.306085471746726,
  shallow=0.80; native caps are 3.0 / 3.5 / 0.8 and all conditions use the
  native capped forward path (`uncapped=false`).
- The frozen target is 823.8254719987887. In the residual-only probe
  calibration (24 objects, 15 cells, 360 logs), layer-averaged increment
  proxies were deep=658.98 (−20.01%), middle=657.41 (−20.20%), and
  shallow=1,639.28 (+98.98%). The ±20% criterion failed. Candidate highs are
  retained; no image metrics or predictions were generated or read.
- The authoritative residual calibration uses the byte-pinned runner
  `audit_scripts/frozen_a3b_residual_runner.py`, SHA256
  `bcf49f4bdb3995ae80c0e2bd70b04c31936a2fb3347dd9642172b19f27b9c0ae`.
  Its 360 logs match the initial pass byte-for-byte. Full result and
  qualification: `A3B_DOSE_FEASIBILITY_AUDIT.md` and
  `a3b_development_residual_only/A3B_DEV_RESIDUAL_CALIBRATION.json`.

## Confirmation cohort and implementation

- Cohort: every frozen FRESH_CONFIRM_B identity, n=150; sorted UID list SHA256
  `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`.
- Recursive input manifest SHA256
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Runner: `scripts/run_validation_v3_experiment.py`, SHA256
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
  It records the runner hash at import/launch and records the data root,
  config, checkpoint, and key inference/metric source hashes in each manifest.
- Formal data root: `data/fresh_confirm_v3_renders` (explicit
  `MVP_DATA_ROOT`). Config:
  `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml`,
  SHA256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Checkpoint:
  `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`,
  SHA256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- 50 Euler steps, 256×256 output, unique6 target views, object seed
  `42 + sorted B-list index`, initial latent seed 42. Every condition uses
  the same object input, conditioning views, target, and latent; the runner
  aborts if their hashes differ.

## Conditions and endpoints

Run the shared low baseline `a3_baseline` plus all 15 conditions
`a3_{deep,middle,shallow}_W{1..5}`. Each cell increases only its named layer
for the same 10-step window, then returns to baseline. Exact requested and
effective per-step scales are recorded in the run manifest and residual
logs. No condition is dropped or replaced based on output.

- Primary endpoint: FG-LPIPS.
- Secondary endpoint: FG-PSNR.
- Co-reported: Full-PSNR, Full-LPIPS, Edge-SSIM, CIEDE2000, and GT-relative
  Laplacian variance, RGB standard deviation, gradient magnitude, and
  high-frequency energy.

## Frozen inference and correction

- Statistical unit: object. Report each cell-minus-baseline mean and median,
  95% paired percentile-bootstrap CI (10,000 draws, seed 20261002), raw
  positive-delta rate, and direction-aware favorable-object rate.
- For FG-LPIPS, a negative delta is favorable; for FG-PSNR, a positive delta
  is favorable. No raw positive-delta fraction may be labeled a win rate for
  a lower-is-better metric.
- Primary family: the 15 cell contrasts plus the 8-df Layer×Window
  interaction, Holm correction across 16 tests on FG-LPIPS. The interaction
  p-value is from the frozen object-cluster robust Wald test on orthogonal
  interaction contrasts; the defective observed-object bootstrap from the
  old production analysis is not used.
- Secondary family: the same 15 cell contrasts plus the interaction on
  FG-PSNR, Holm corrected across 16. Other metrics are reported with paired
  effects and CIs as descriptive unless explicitly labeled secondary.
- Fit a Gaussian repeated-measures GEE with fixed categorical Layer,
  Window, and Layer×Window terms, object clusters, exchangeable working
  correlation, and robust sandwich covariance. Report Layer and Window
  omnibus tests with Holm correction across those two secondary terms;
  report the GEE interaction as a cross-check to the primary cluster-Wald
  result.
- Log post-scale residual norms by layer and step. For each object and
  active cell, report the frozen increment proxy
  `requested scale delta × sum(post-scale norm / actual effective scale)`
  over its 10 steps, plus the paired net post-scale norm
  change against baseline. Also report integrated post-scale residual energy
  by layer. These measures describe realized bounded-dose exposure; because
  the intervention can change later latents and residuals, dividing the
  high-condition norm by scale is an approximation to its unscaled residual,
  not a counterfactual residual at the baseline trajectory.

## Interpretation boundary

This campaign can confirm whether the frozen bounded intervention has
layer- and window-dependent effects on the fresh cohort. Because the
development dose proxy is substantially imbalanced, a significant
Layer×Window result cannot be called an equal-dose or dose-independent
mechanism. A null result weakens the broad interaction claim. Neither outcome
licenses new scale selection on FRESH_CONFIRM_B.
