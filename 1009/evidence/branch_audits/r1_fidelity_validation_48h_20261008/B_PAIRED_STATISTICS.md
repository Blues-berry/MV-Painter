# B — Saved-RGB paired validation statistics

## Scope and analysis

This phase reuses frozen Fresh C and Fresh B RGB outputs; it runs no new model inference. The primary contrast is `LLH − GFL`, paired by UID within each cohort. Fresh C has `n=300`; Fresh B is a disjoint `n=150` confirmation holdout. An additional Fresh C `n=280` view excludes all 20 UIDs that overlap the previous diagnostic set. Cohorts are never pooled.

Prediction PNGs were checked against their source SHA-256 lists. GFL/LLH have identical hashes for all six logged model-input tensors on every object: Fresh C 300/300 and Fresh B 150/150. The analysis uses saved 8-bit RGB for equal-view CIEDE2000, signed Lab shifts and GT-relative Laplacian error; FG-PSNR, FG-LPIPS, FG-SSIM and Edge-SSIM are the corresponding frozen per-object campaign values. Each interval below is a two-sided 95% object-level paired percentile bootstrap interval from 10,000 resamples. The full table includes medians, median intervals, Cohen's dz, wins/losses/ties and every per-object difference.

## Primary paired endpoints

| Cohort | Metric (direction) | Mean LLH−GFL [95% CI] | Median | Favorable objects |
|---|---|---:|---:|---:|
| Fresh C `n=300` | FG-CIEDE2000 (lower) | `−2.232` [−3.137, −1.338] | −2.275 | 187/300 (62.3%) |
|  | FG-PSNR dB (higher) | `+1.143` [+0.814, +1.480] | +0.599 | 169/300 (56.3%) |
|  | FG-LPIPS (lower) | `−0.01748` [−0.02003, −0.01496] | −0.01523 | 221/300 (73.7%) |
|  | FG-SSIM (higher) | `+0.04111` [+0.03543, +0.04677] | +0.03685 | 230/300 (76.7%) |
|  | Edge-SSIM (higher) | `+0.01353` [+0.01049, +0.01655] | +0.01125 | 196/300 (65.3%) |
|  | GT-relative Laplacian error (lower) | `−0.01786` [−0.01866, −0.01709] | −0.01686 | 300/300 (100%) |
| Fresh B `n=150` | FG-CIEDE2000 (lower) | `−1.905` [−3.262, −0.529] | −2.109 | 85/150 (56.7%) |
|  | FG-PSNR dB (higher) | `+1.030` [+0.577, +1.493] | +0.253 | 77/150 (51.3%) |
|  | FG-LPIPS (lower) | `−0.01556` [−0.01920, −0.01192] | −0.01398 | 111/150 (74.0%) |
|  | FG-SSIM (higher) | `+0.03723` [+0.02897, +0.04589] | +0.03292 | 108/150 (72.0%) |
|  | Edge-SSIM (higher) | `+0.01442` [+0.00982, +0.01890] | +0.01159 | 95/150 (63.3%) |
|  | GT-relative Laplacian error (lower) | `−0.01871` [−0.02016, −0.01743] | −0.01752 | 150/150 (100%) |

Fresh C after excluding the 20 diagnostic-overlap UIDs remains similar: CIEDE2000 `−2.188` [−3.120, −1.274], FG-PSNR `+1.097` [+0.768, +1.431], FG-LPIPS `−0.01732` [−0.01977, −0.01490], and GT-relative Laplacian error `−0.01779` [−0.01856, −0.01702]. This sensitivity view does not turn the remaining 280 objects into a separately frozen cohort; Fresh B remains the independent holdout.

## Complexity boundary

Fresh B quartiles use its frozen GT-only Laplacian-variance cut points `0.00685639`, `0.01771007`, and `0.03139245`; `np.digitize` reproduces counts 38/37/37/38. The same thresholds are applied unchanged to Fresh C and labeled cross-cohort exploratory there.

| Cohort and GT texture stratum | FG-CIEDE2000 mean [95% CI]; LLH favorable | FG-PSNR mean [95% CI]; LLH favorable | FG-LPIPS mean [95% CI]; LLH favorable |
|---|---:|---:|---:|
| Fresh B Q1, low complexity, `n=38` | `−8.756` [−10.805, −6.569]; 34/38 | `+3.646` [+2.761, +4.471]; 32/38 | `−0.03768` [−0.04295, −0.03250]; 38/38 |
| Fresh B Q4, high complexity, `n=38` | `+3.624` [+1.907, +5.303]; 10/38 | `−0.770` [−1.165, −0.315]; 7/38 | `−0.00008` [−0.00562, +0.00519]; 17/38 |
| Fresh C Q4, same Fresh B cut points, `n=58` | `+1.956` [+0.105, +3.833]; 26/58 | `−0.346` [−0.848, +0.177]; 23/58 | `−0.00447` [−0.00930, +0.00037]; 30/58 |
| Fresh C Q4, diagnostic UIDs excluded, `n=55` | `+1.598` [−0.197, +3.403]; 25/55 | `−0.315` [−0.813, +0.191]; 22/55 | `−0.00608` [−0.01069, −0.00164]; 29/55 |

The high-complexity result is the key boundary: the average LLH benefit does not extend uniformly to texture-rich targets. Texture metrics alone are not treated as perceptual proof; GT-relative error is used so a larger response is not automatically called better detail.

## Illustrative gallery selection

`B_FAILURE_AND_SUCCESS_GALLERY.pdf` shows one object each from Fresh B Q1, Q3 and Q4. Selection is the object nearest the GT-only median Laplacian variance within each preassigned quartile, with UID as a deterministic tie-break. Generated outcomes were not used to choose objects. The pages show the original target panel and frozen GFL/LLH PNGs with their hashes and paired endpoint deltas; they are illustrations, not subgroup estimates. `B_GALLERY_SELECTION.csv` and `B_GALLERY_SELECTION_RULE.json` record the selection and image identities.

## Evidence files

- Every Fresh C/B object and both conditions: `A_COHORT_HETEROGENEITY.csv` and `B_OBJECT_LEVEL_RESULTS.csv`.
- All paired means, intervals, paired effects and win counts: `PAIRED_BOOTSTRAP_STATISTICS.csv`.
- Every quartile estimate: `A_QUARTILE_EFFECTS.csv`; fixed cut points: `A_QUARTILE_CUTPOINTS.json`.
- Output and target provenance: `RGB_HASH_AND_INPUT_AUDIT.csv`, `ALL_COHORT_INPUT_PAIR_AUDIT.csv`.
- Residual logs: `RESIDUAL_LOG_IDENTITY_AUDIT.csv`, `RESIDUAL_LOG_STEP_PAIRED.csv`, `RESIDUAL_LOG_STEP_SUMMARY.csv` (descriptive only).
- CPU metric reconstruction: `recompute_paired_rgb_metrics.py`; protocol lock: `B_VALIDATION_PROTOCOL.json`; method changes: `ANALYSIS_METHOD_CHANGELOG.md`.
