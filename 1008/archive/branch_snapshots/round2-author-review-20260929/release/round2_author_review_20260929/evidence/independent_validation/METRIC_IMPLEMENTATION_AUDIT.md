# Metric Implementation Audit

Status: **PARTIALLY VERIFIED**. Core PSNR/SSIM/Edge-SSIM values were independently recomputed from the stored prediction PNGs and original source RGBA/depth PNGs for 11 objects in the `predeclared diagnostic sample` scope and four conditions. PSNR and foreground/edge SSIM are comparatively close on this sample, but Full SSIM has a systematic stored-CSV versus PNG/source mismatch that is not explained by ordinary PNG quantization alone. The original float prediction tensors and exact metric-dtype provenance are unavailable here; LPIPS was not rerun with a learned network.

## Protocol and implementation comparison

| item | paper/protocol definition | code actually used | independent finding |
|---|---|---|---|
| Full PSNR | RGB PSNR on the full 3×2 panel | `geotex/round2_main_eval.py` calls `eval_exploration.compute_metrics`; `compute_psnr` averages all RGB/panel values; no foreground-only denominator | Background is included and can dominate when the object mask is small. It is not a 3D texture metric. |
| Foreground MSE/PSNR | foreground RGB error under alpha mask | alpha is resized with the same bicubic pipeline; `compute_psnr` thresholds mask values at `>0.5`, expands one mask over RGB, then averages selected RGB values | Denominator is selected foreground RGB values, not all panel pixels. |
| Foreground SSIM | masked local SSIM | 3×3 average-pool SSIM; mask is 3×3 max-pooled and values are multiplied before averaging where pooled mask `>0.5` | Edge pixels enter the statistic through mask dilation; this is not a crop or a strict original-alpha-only SSIM. |
| RGBA/GT | white-background composite from RGBA | dataset uses `RGB*alpha + white*(1-alpha)` and retains alpha masks | Independently reconstructed target agrees with saved GT within PNG/resampling quantization; see summary JSON. |
| 512→256 | bicubic antialiased resize per view, then panel assembly | dataset/data preparation uses torchvision resize and 3×2 rearrangement | Reproduced locally; reverse order and rotations are included. |
| unique6 | `[0,15,12,16,13,14]`, or reversed `[14,15,0,16,12,13]` with rotations | dataset implements this exact mapping | Reproduced locally for every object. |
| Edge-SSIM | depth/normal discontinuity proxy | round-2 runner selects normalized real depth when present, falls back to normal; `compute_edge_mask` averages 3 channels, Sobel-normalizes per panel, thresholds `>0.1`; SSIM then max-pools the edge mask | This is a depth-derived edge mask in the frozen run, not a joint depth+normal discontinuity detector. |
| No-adapter | same unmodified pipeline with adapter contribution disabled | round-2 schedule sets scale 0 and still uses the same condition image, scheduler, seed, target and metric code | Definitionally consistent with an adapter-free baseline, conditional on the zero-scale wrapper behavior. |

## Recomputed aggregate comparison

| condition | metric | stored CSV mean | PNG/source recompute mean | mean absolute difference | max absolute difference |
|---|---|---:|---:|---:|---:|
| no_adapter | full_psnr | 10.470990 | 10.470950 | 0.000863 | 0.002322 |
| no_adapter | fg_psnr | 9.112419 | 9.108018 | 0.004982 | 0.034882 |
| no_adapter | full_ssim | 0.737145 | 0.773223 | 0.036078 | 0.046552 |
| no_adapter | fg_ssim | 0.425858 | 0.431112 | 0.010388 | 0.025776 |
| no_adapter | edge_ssim | 0.520825 | 0.530921 | 0.010096 | 0.020120 |
| fixed_low | full_psnr | 17.109665 | 17.101761 | 0.009166 | 0.033051 |
| fixed_low | fg_psnr | 9.038353 | 9.034425 | 0.006288 | 0.051444 |
| fixed_low | full_ssim | 0.871525 | 0.903122 | 0.031665 | 0.061670 |
| fixed_low | fg_ssim | 0.383089 | 0.384344 | 0.001255 | 0.003858 |
| fixed_low | edge_ssim | 0.549232 | 0.556515 | 0.009089 | 0.028345 |
| fixed_high | full_psnr | 14.555207 | 14.553776 | 0.006792 | 0.034855 |
| fixed_high | fg_psnr | 7.893915 | 7.890478 | 0.004567 | 0.040878 |
| fixed_high | full_ssim | 0.846910 | 0.877017 | 0.030178 | 0.053832 |
| fixed_high | fg_ssim | 0.293025 | 0.294353 | 0.001390 | 0.003966 |
| fixed_high | edge_ssim | 0.536608 | 0.544459 | 0.009244 | 0.025283 |
| c3 | full_psnr | 16.853050 | 16.847302 | 0.013968 | 0.043197 |
| c3 | fg_psnr | 8.697624 | 8.694554 | 0.005276 | 0.042248 |
| c3 | full_ssim | 0.878406 | 0.904343 | 0.025976 | 0.057091 |
| c3 | fg_ssim | 0.387498 | 0.388770 | 0.001413 | 0.003932 |
| c3 | edge_ssim | 0.549513 | 0.555132 | 0.007571 | 0.023111 |

The supplied `METRIC_RECOMPUTE_SAMPLE.csv` is a predeclared diagnostic sample: top/bottom three C3−fixed-low foreground-PSNR objects using the stored CSV, top three no-adapter foreground-SSIM objects using the stored CSV, and the two smallest/two largest independently reconstructed foreground coverages. It is not used to change pooled statistics.

## Interpretation of the reported anomaly

The observed ordering—no-adapter having higher foreground structure values than C3, and fixed-high being worse than fixed-low on foreground structure—is present in the stored metrics and is not erased by the independent PNG/source recomputation. Full-image metrics can still favor adapter conditions because background agreement and silhouette/edge behavior contribute over the entire panel. This is a genuine shape–texture trade-off signal under the current definitions, not evidence that foreground metrics should be redefined.

Potential bias sources retained rather than corrected: small foreground masks make Full PSNR background-dominated; max-pooled SSIM masks include a one-pixel neighborhood around the alpha boundary; alpha is antialiased before the `>0.5` threshold; Sobel edge masks are panel-normalized and threshold-relative; PNG quantization changes recomputed values slightly; LPIPS values remain float-run provenance and were not silently replaced. The Full SSIM discrepancy is a separate metric-provenance/implementation-mismatch candidate and remains pending until the original float predictions or an exact rerun are available.

## Required follow-up

A candidate minimal float32 hardening patch is recorded in `METRIC_FLOAT32_RECOMMENDED.patch` but is intentionally not applied: it must be tested against the original float predictions before changing shared metric code. The paper-facing Full SSIM column should be re-audited or explicitly caveated; a future robustness appendix should also report mask coverage and a strict-eroded foreground sensitivity table, and should avoid describing Edge-SSIM as a full normal/depth discontinuity metric unless the normal branch is actually used.

Evidence: `METRIC_RECOMPUTE_ALL.csv`, `METRIC_RECOMPUTE_SAMPLE.csv`, and `METRIC_RECOMPUTE_SUMMARY.json` in this directory.
