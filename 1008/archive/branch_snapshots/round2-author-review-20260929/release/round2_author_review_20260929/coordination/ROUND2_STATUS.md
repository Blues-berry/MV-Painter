# Round-two working status

This directory is a new working branch for the review round after CAG-S-26-01549.
The 01549 baseline remains unchanged at:

- `final/final_0903.tex` SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`
- `final/supplementary_0903.tex` SHA-256 `a4c797c3c90f6592bde08a802f6c67ec07e8c9c887472232adb1c5d66c5f854a`

## Implemented

- Unique six-view protocol in `MVPainter/src/data/mvpainter_dataset.py`, with
  the historical duplicated-top order preserved as the default audit mode.
- Fixed object splits, protocol manifest, deterministic 10,000-resample
  object bootstrap, direction-aware paired deltas, and symmetric log-ratio
  texture-statistic errors in `geotex/round2_*.py`.
- CIEDE2000, stratified qualitative sampling, UV seam difference, and
  cross-view texel variance utilities.
- Main-adapter and official MV-Adapter protocol launch guards.
- New manuscript/supplementary working copies and a new response letter;
  Reviewer 3 has the requested thank-you response.
- Local tests for split validation, bootstrap reproducibility, texture errors,
  and bake metrics.

## Blocking assets

The following are not present in the workspace and are required before any
numerical claim can be finalized:

- `geotex_refattn_v1/geotex_step_0002000.pt`
- the old main-adapter evaluation configuration snapshot
- the old main-adapter 300-object per-object CSVs
- an external checkout/weights for the official MV-Adapter SD2.1 pipeline

Until these are recovered, the round-two manuscript remains a working draft;
the former 0.96 dB number and old full-pool protocol are explicitly not final
claims in the new conclusion. Existing v2/FAC CSVs must not be substituted for
the missing main-adapter evidence.

The built-in LaTeX compiler was invoked for the new manuscript but the app
reported that standard compiler directories were unavailable. The source is
preserved; compile again after the environment/compiler is available.
