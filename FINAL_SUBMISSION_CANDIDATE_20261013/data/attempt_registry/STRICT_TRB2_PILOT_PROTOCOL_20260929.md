# Strict TRB2 Development Pilot Protocol

Status: pre-specified before the TRB2 run; development evidence only.  
Date: 2026-09-29 UTC

## Purpose

This is a finite repair pilot for the residual-budget controller. It isolates
the identified budget-accounting defect in the original `TRB_TCAS` pilot. It
does not use the 276-object holdout and cannot authorize a holdout run by
itself.

## Fixed comparison

- Cohort: the clean-v2 24-object probe list used by the completed strict pilot.
- Views: `unique6`.
- Seed: `42`, with Python, NumPy and PyTorch reset before dataset construction
  and before each object.
- Shared per-object batch and initial latent across all conditions.
- Checkpoint, reference path, geometry conditioning, camera mapping and
  50-step Euler schedule are unchanged from the completed strict pilot.
- Conditions: `fixed_low`, `C3_TCAS`, `HLL_eq`, `LLH_eq`, `TRB2_TCAS`.
- Primary metric: foreground AlexNet LPIPS (`FG-LPIPS`, lower is better).
- Secondary metrics: FG-PSNR, FG-SSIM, Edge-SSIM, FG-MAE, LapCorr,
  LapVar and excess high-frequency error.

## TRB2 definition

1. Run an input-only C3 calibration pass.
2. Record the residual after the actual C3 scale and per-layer cap, using
   element-count-weighted residual RMS for each depth/stage group.
3. During TRB2 inference, start from the actual C3 scale. If the current
   residual exceeds its calibrated group budget, attenuate it by
   `min(1, (target/current)^0.75)`.
4. Never increase above C3 and preserve the fixed-low floor wherever the layer
   cap permits it.

The repair therefore removes the old implicit transformation
`scale=(target/raw_rms)^0.75`, which under-dosed the C3 middle stage even when
there was no budget violation. No spatial gate, learned parameter or new
holdout-derived rule is introduced.

## Acceptance gate

The pilot is not promoted if any of the following holds:

- TRB2 does not improve FG-LPIPS relative to both fixed-low and C3 under the
  pre-specified paired analysis;
- its practical improvement is not stable under the 10,000-resample
  object-level bootstrap, or is only a structural-smoothing effect;
- it materially degrades the secondary structure/edge metrics without a clear
  FG-LPIPS justification;
- calibration cost, extra forward steps and actual residual budget are not
  reported.

No schedule or threshold will be selected after inspecting the 24-object
results. A failed gate leaves the 276-object holdout unlocked and the result
as internal method-development evidence only.

## Reproducibility

The run uses `geotex/residual_budget_pilot.py` with the independent method
label `TRB2_TCAS` and a new output directory. The runner records per-object
FG-LPIPS, timing, calibration steps, actual residual traces and a progress
checkpoint. Existing TRB and all main-worktree results are preserved.
