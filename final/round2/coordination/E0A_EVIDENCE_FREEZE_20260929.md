# E0-A evidence freeze — 2026-09-29

Status: **PASS_WITH_LIMITATIONS**. This CPU/static audit did not run model inference.

## Exact pairing

- 276 record JSON files, each with exactly four schedules and four flat rows; 1,104 stage rows; 1,104 serialized Full-SSIM rows; 1,104 prediction PNGs plus 276 GT PNGs.
- `records.rows`, `flat_rows`, per-schedule CSVs, combined CSV, serialized CSVs and PNG filenames agree on the object/schedule keys.
- All checked metric columns are finite. No missing value was converted to zero.
- The content-hash manifest contains `1680` entries; canonical hash of that manifest: `b2590aee7acce35473ff3e5e88bbebfdb8e518017de74b3b80cba004effb966e`.

## Protocol separation

The main four-condition clean-v2 run and the stage-placement follow-up share the checkpoint, object IDs, seed and nominal camera/step settings, but the repeated C3 condition is not byte- or value-identical. The largest observed per-metric difference is therefore preserved rather than silently pooled. The final paper should use the main run for no-adapter/fixed-low/fixed-high and use the follow-up only for within-run fixed-mean/HLL/LHL/LLH comparisons.

## Stage-placement result boundary

Within the follow-up, LHL/C3 is compared object-by-object with fixed mean, HLL and LLH. The saved-artifact Full-SSIM branch is PNG-reloaded float32 prediction against raw RGBA/white float32 GT. The machine-readable paired values and all seven pre-save metrics are in the JSON/CSV outputs.

## Actual 50-step budget

The stage trace uses early/mid/late = 17/16/17 steps. LHL, HLL and LLH have nominal scale means 1.650, 1.675 and 1.675, respectively; fixed mean is 1.666667. Exact sums, squared sums, and actual residual L2/RMS summaries are recorded in the JSON. The paper must not call the four schedules strictly equal-budget; their arithmetic mean and residual energy differ.

## Fixed-GT SSIM decomposition

The 12-object saved-tensor decomposition fixes one GT branch at a time and separates prediction dtype, prediction PNG quantization and GT PNG serialization. It is diagnostic only and does not require model rerun.

Machine-readable evidence: `E0A_EVIDENCE_FREEZE_20260929.json` and `E0A_STRICT276_METRICS_FROZEN.csv`.
