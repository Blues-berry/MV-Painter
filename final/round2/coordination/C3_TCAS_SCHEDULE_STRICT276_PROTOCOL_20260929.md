# C3/TCAS schedule-only strict-276 follow-up protocol

Status: **frozen before strict-276 inference; targeted follow-up**.

The 24-object development gate was completed first. Both `LLH_ramp_eq` and
`LLH_cosine_eq` were retained, so no candidate is selected from the strict-276
results. This follow-up does not modify the frozen CAI rule and does not claim
cross-backbone transfer.

## Fixed conditions

- Cohort: clean-v2 strict 276, disjoint from the 24-object development probe.
- Seed: `42`; inference steps: `50`; target view mode: `unique6`.
- Conditions: `fixed_low`, `C3_TCAS`, `HLL_eq`, `LLH_eq`, `LLH_ramp_eq`,
  `LLH_cosine_eq`.
- Schedule-only execution uses `--skip-calibration`; no adaptive calibration
  pass is counted or hidden.
- Primary metric: FG-LPIPS; secondary metrics: PSNR, FG-SSIM, Edge-SSIM and
  FG-MAE; diagnostics include foreground Laplacian statistics.
- Paired statistics: 10,000 object-level bootstrap resamples, seed `20260929`.

## New schedules

The first 33 steps use scale `1.25`. The final 17 steps use either a linear or
cosine ramp from `1.25` to `3.6029411764705883`. Both have nominal scale sum
`82.5`, matching the existing equal-budget C3/LLH schedule family.

## Evidence boundary

The strict-276 cohort has already been used for the frozen stage-placement
follow-up. These new conditions are therefore reported as targeted follow-up
results, not retroactively promoted to the original confirmatory protocol.
The main-adapter cohort is clean-v2 source-stratified and is not described as
an all-Exact-Mesh cohort. No manuscript or response-letter file is modified.
