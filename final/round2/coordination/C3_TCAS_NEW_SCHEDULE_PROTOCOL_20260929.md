# C3/TCAS schedule follow-up protocol

Status: **frozen before new inference; development-only**.

This protocol is separate from the frozen CAI calibration and does not authorize a 276-object or Exact-76 holdout run.

## Fixed conditions

- Cohort: clean-v2 probe 24, unique6, seed 42, 50 steps.
- Baselines: `fixed_low`, `C3_TCAS`, `HLL_eq`, `LLH_eq`.
- Primary metric: FG-LPIPS, lower is better.
- Secondary metrics: PSNR, FG-SSIM, Edge-SSIM and FG-MAE.
- Statistics: object-level paired bootstrap, 10,000 resamples, seed 20260929.

## New schedule family

- `LLH_ramp_eq`: fixed-low for 33 steps, then a linear 17-step ramp from 1.25 to 3.6029411764705883.
- `LLH_cosine_eq`: fixed-low through the first two thirds, then a cosine half-ramp with the same peak and nominal scale sum.
- Both schedules have nominal scale sum 82.5, matching the existing equal-budget pilot conditions.

## Gate

A candidate is eligible for later validation only if its FG-LPIPS paired 95% CI is strictly below zero against both C3 and fixed-low. All secondary regressions remain reportable. A failure stops promotion and does not authorize holdout inference.

This is schedule-only exploratory screening. It does not alter checkpoints, datasets, metrics, frozen CAI rules, or manuscript files.
