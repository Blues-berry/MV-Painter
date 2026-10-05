# Stage-boundary sensitivity protocol lock

Frozen: 2026-10-05 UTC, before any FRESH_CONFIRM_B method output.

## Question and scope

Test robustness of a fixed-width late high pulse to the late-stage onset
implied by the four candidate partitions named in the continuation protocol.
This is a bounded boundary-sensitivity family, not an optimization search and
not evidence for a physical diffusion phase boundary.

## Cohort and shared run

- Cohort: the full frozen FRESH_CONFIRM_B list, n=150; UID-list SHA256
  `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`.
- Input manifest SHA256:
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Runner: `scripts/run_validation_v3_experiment.py`, SHA256
  `bcf49f4bdb3995ae80c0e2bd70b04c31936a2fb3347dd9642172b19f27b9c0ae`.
- GeoTex checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`,
  SHA256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- All conditions share the same checkpoint, object seed policy (42 + sorted
  cohort index), initial latent seed 42, 50 Euler steps, 256×256 model output,
  view order, cap semantics, and paired per-object inputs.
- The `a3_baseline` row from the same combined B run is the shared low-scale
  baseline (`deep=1.25, middle=1.25, shallow=0.50`). No second baseline run is
  substituted or selected after outcomes.

## Frozen condition family

All four profiles use LOW outside the pulse and HIGH inside it, with the same
10 consecutive high steps and native cap semantics:

| Partition | Late-stage onset | High steps | Duration |
|---|---:|---|---:|
| 20/60/20 | 40 | 40–49 | 10 |
| 30/40/30 | 35 | 35–44 | 10 |
| 34/32/34 | 33 | 33–42 | 10 |
| 40/20/40 | 30 | 30–39 | 10 |

LOW=`{deep:1.25, middle:1.25, shallow:0.50}`;
HIGH=`{deep:2.50, middle:2.50, shallow:0.75}`. Every layer is pulsed
simultaneously, and the effective shallow scale remains below its 0.8 cap.
The only changed property within this family is pulse position.

## Outcomes and analysis

- Primary: FG-LPIPS. Secondary: FG-PSNR, Full-PSNR, LPIPS, Edge-SSIM,
  CIEDE2000, and GT-relative texture diagnostics.
- Report paired object-level deltas and 95% percentile bootstrap intervals
  using 10,000 resamples and seed 20261002.
- Compare each profile with the shared low baseline; Holm-correct the four
  primary-metric contrasts as one family.
- Compare the 34/32/34 pulse with the other three profiles using paired
  object-level deltas and one Holm family of three. Report confidence
  intervals and all four contrasts; do not select an optimum or tune another
  boundary from these results.
- If no stable preference is established, describe thirds as a convenient
  discretization. Even a stable preference only supports the frozen family
  and cannot establish a universal or exact optimal boundary.

The four condition names and step onsets are frozen in the runner registry as
`boundary_late_onset_{20_60_20,30_40_30,34_32_34,40_20_40}`.
