# Frozen campaign protocol summary

## A2 discovery map

- Cohort: 300 unique objects in `data/FRESH_CONFIRM_300.txt`.
- Conditions: one shared low-scale baseline plus the complete 3-layer ×
  5-window perturbation map.
- Inference: 50 Euler steps; unique six target views `[0, 15, 12, 16, 13, 14]`;
  object seed `42 + object_idx`; latent seed 42.
- Native caps: deep 3.0, middle 3.5, shallow 0.8.
- Checkpoint SHA256:
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- The corrected object-cluster Wald interaction analysis is exploratory
  reanalysis of A2. The prior object-resampling null test is retired because it
  has zero power for the object-shared interaction pattern.

## FRESH_CONFIRM_B comparison represented here

- Cohort: 150 unique objects in `data/FRESH_CONFIRM_B_150.txt`, disjoint from
  A2 under the frozen identity audit.
- The included B result rows are `layer_llh`, `lfm_exact`, `layer_hll`, and
  `a3_baseline`. `a3_baseline` was verified in the frozen B report to have the
  all-low LLL scale trace. These rows support the locked LLH−LFM-EXACT and
  LLH−HLL/LLL contrasts. They are not a full reproduction of B's
  30-condition generation campaign.
- Delta: LLH minus LFM-EXACT. Paired object bootstrap: 10,000 draws, seed
  `20261002`; FG-PSNR higher-is-better, FG-LPIPS lower-is-better.
- This estimates the temporal redistribution effect at matched requested
  layer means. Actual post-scale correction norms differ, so it is not an
  equal-realized-dose result.
- The locked LLH−HLL and LLH−LLL contrasts favor LLH on both mean endpoints.
  HLL−LLL is a post-unblinding exploratory comparison: its FG-PSNR interval
  crosses zero while FG-LPIPS is worse for HLL. The user's full two-endpoint
  directional signature therefore does not pass.
- The LLH−LFM-EXACT intervals lie within the preregistered practical margins
  (±0.5 dB PSNR; ±0.01 LPIPS); report the small directional differences
  without claiming a practically large temporal-redistribution gain.

## Provenance

The A2/B campaign runner's original source SHA256 is
`4ee5fdb84ad729663d65494c1fa9f97bdc692b8801c4b8bff9afedbdb7b68ec6`, from
source commit `5359dd773a5093508755985ecd63a8104b96d8fe`. The portable copy
changes filesystem roots only; see `RUNNER_PROVENANCE.json`. Input table and
UID-list hashes are recorded there. Model weights and the rendered source
dataset remain external inputs and are not included.
