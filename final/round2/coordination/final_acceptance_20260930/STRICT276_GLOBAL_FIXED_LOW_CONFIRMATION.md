# STRICT276_GLOBAL_FIXED_LOW_CONFIRMATION (final acceptance, 2026-09-30)

## Status: COMPLETED

Reviewer-1's missing global fixed-low control was run on the SAME runner,
config, checkpoint, 276-object list, unique6 views, 50 Euler steps, seeds,
preprocessing, metric path, and serialization as the existing strict-276
layer confirmations (`scripts/run_layer_confirmation_276_20260930.py`,
protocol `layer-confirmation-strict276-v1`, pre-registered in
`EXPERIMENT_PROTOCOL_LOCK.md`). No schedule search was performed; the
constant 1.25 value and wrapper cap semantics are frozen from the
clean-v2 global protocol.

- Raw per-object data: `STRICT276_GLOBAL_FIXED_LOW_RAW.csv` (276 x 4 schedules x 7 metrics)
- Provenance/hashes: `STRICT276_GLOBAL_FIXED_LOW_MANIFEST.json`
- Machine-readable analysis: `/4T/tmp/mvpainter-layer-confirmation-20260930/confirmation_analysis.json`

## Same-runner means (276 objects, seeded protocol surface)

| Schedule | Full-PSNR | Full-SSIM | Full-LPIPS | FG-PSNR | FG-SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---:|---:|---:|---:|---:|---:|
| global fixed-low | 18.229 | 0.8439 | 0.2107 | 10.731 | 0.3987 | 0.1917 | 0.5201 |
| layer-fixed-mean | 19.516 | 0.8503 | 0.2082 | 13.100 | 0.4550 | 0.1698 | 0.5363 |
| layer-LHL | 19.635 | 0.8486 | 0.2278 | 12.974 | 0.4445 | 0.1719 | 0.5273 |
| layer-LLH | 20.828 | 0.8514 | 0.1988 | 13.975 | 0.4620 | 0.1610 | 0.5476 |

## Paired differences (object-level, 10,000-resample percentile bootstrap, seed 20260930)

Sign convention: positive = first arm better (LPIPS sign already flipped so
positive = lower/better). "CI excl. 0" = 95% percentile interval excludes zero.

### layer-LLH − global fixed-low (primary Reviewer-1 comparison)

| Metric | mean | median | 95% CI | win rate | CI excl. 0 |
|---|---:|---:|---|---:|---|
| Full-PSNR | +2.599 | +2.447 | [+2.353, +2.838] | 249/276 | yes |
| Full-SSIM | +0.0076 | +0.0071 | [+0.0067, +0.0084] | 245/276 | yes |
| Full-LPIPS | +0.0119 | +0.0104 | [+0.0098, +0.0141] | 196/276 | yes |
| FG-PSNR | +3.244 | +3.366 | [+2.936, +3.542] | 242/276 | yes |
| FG-SSIM | +0.0633 | +0.0647 | [+0.0582, +0.0683] | 252/276 | yes |
| FG-LPIPS | +0.0308 | +0.0277 | [+0.0283, +0.0331] | 261/276 | yes |
| Edge-SSIM | +0.0276 | +0.0210 | [+0.0242, +0.0308] | 237/276 | yes |

layer-LLH is better on **7/7 metrics** with all CIs excluding zero.

### layer-LHL − global fixed-low

| Metric | mean | median | 95% CI | win rate | CI excl. 0 |
|---|---:|---:|---|---:|---|
| Full-PSNR | +1.406 | +1.203 | [+1.212, +1.592] | 227/276 | yes |
| Full-SSIM | +0.0048 | +0.0050 | [+0.0039, +0.0056] | 200/276 | yes |
| Full-LPIPS | −0.0170 | −0.0116 | [−0.0206, −0.0138] | 80/276 | yes (favors global) |
| FG-PSNR | +2.244 | +2.356 | [+2.009, +2.468] | 234/276 | yes |
| FG-SSIM | +0.0458 | +0.0465 | [+0.0417, +0.0499] | 250/276 | yes |
| FG-LPIPS | +0.0198 | +0.0188 | [+0.0180, +0.0216] | 250/276 | yes |
| Edge-SSIM | +0.0072 | +0.0046 | [+0.0050, +0.0095] | 181/276 | yes |

layer-LHL is better on **6/7 metrics**; global fixed-low retains better
full-image LPIPS (consistent with the known full-image vs foreground
trade-off). Reported honestly as a mixed full-image outcome.

### layer-fixed-mean − global fixed-low

| Metric | mean | median | 95% CI | win rate | CI excl. 0 |
|---|---:|---:|---|---:|---|
| Full-PSNR | +1.288 | +1.260 | [+1.108, +1.461] | 225/276 | yes |
| Full-SSIM | +0.0064 | +0.0063 | [+0.0056, +0.0072] | 224/276 | yes |
| Full-LPIPS | +0.0026 | +0.0029 | [+0.0006, +0.0045] | 160/276 | yes |
| FG-PSNR | +2.369 | +2.714 | [+2.155, +2.576] | 245/276 | yes |
| FG-SSIM | +0.0563 | +0.0583 | [+0.0521, +0.0603] | 259/276 | yes |
| FG-LPIPS | +0.0219 | +0.0209 | [+0.0201, +0.0236] | 254/276 | yes |
| Edge-SSIM | +0.0162 | +0.0128 | [+0.0138, +0.0186] | 217/276 | yes |

## Interpretation bounds

- This is a within-surface paired result: every method shared the same
  per-object frozen reference realization, initial latent, and metric code
  (verified by the Phase 3 shared-input audit). Absolute means on this
  surface are not comparable to the clean-v2 four-condition table (different
  reference draws; independent protocol surfaces).
- The development-probe +3.083 dB FG-PSNR figure keeps its development-probe
  label; the confirmation-surface value here is +3.244 dB FG-PSNR
  (LLH − global fixed-low), independently obtained.
- No claim of equivalence is made anywhere a CI excludes zero.
- The archived unseeded layer-LHL record (FG-PSNR 14.776) is NOT pooled with
  any of these numbers; its seeded replica (12.974, rank agreement r=0.658)
  remains the reproducibility caveat documented in the manuscript.
