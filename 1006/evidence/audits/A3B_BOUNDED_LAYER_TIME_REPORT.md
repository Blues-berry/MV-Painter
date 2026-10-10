# A3b bounded-dose Layer × Window report — FRESH_CONFIRM_B

**Classification: bounded local perturbation map, not equal-dose or dose-matched.** The frozen development calibration missed its ±20% dose-balance target: deep −20.01%, middle −20.20%, shallow +98.98%. The candidate scales were retained without outcome-based retuning.

The B campaign passed its 4,500/4,500-row integrity gate before this analysis. This report covers the frozen baseline plus 15 layer-by-window interventions on the same 150 objects. Each cell-minus-baseline effect uses paired object bootstrap (10,000 resamples; seed 20261002). Positive FG-PSNR and negative FG-LPIPS are favorable. Holm families contain the 15 cell contrasts plus the 8-df interaction test, separately for each endpoint.

## Locked cell contrasts

| Intervention | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ dB [95% CI] | Favorable objects | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| `deep_W1` | +0.000020 [+0.000006, +0.000035] | 38.7% | 0.027 | -0.0029 [-0.0038, -0.0021] | 32.7% | 0.0015 |
| `deep_W2` | -0.000031 [-0.000043, -0.000018] | 66.0% | 0.0015 | +0.0001 [-0.0008, +0.0010] | 48.0% | 1 |
| `deep_W3` | -0.000056 [-0.000077, -0.000036] | 65.3% | 0.0015 | +0.0029 [+0.0016, +0.0042] | 52.7% | 0.0015 |
| `deep_W4` | -0.000023 [-0.000048, +0.000001] | 52.7% | 0.186 | +0.0013 [+0.0005, +0.0022] | 50.7% | 0.0112 |
| `deep_W5` | -0.000020 [-0.000039, -0.000002] | 58.7% | 0.134 | +0.0000 [-0.0005, +0.0006] | 42.7% | 1 |
| `middle_W1` | -0.000146 [-0.000191, -0.000102] | 72.0% | 0.0015 | +0.0084 [+0.0065, +0.0103] | 85.3% | 0.0015 |
| `middle_W2` | -0.000092 [-0.000128, -0.000057] | 66.0% | 0.0015 | +0.0037 [+0.0019, +0.0055] | 61.3% | 0.0015 |
| `middle_W3` | -0.000018 [-0.000063, +0.000027] | 50.0% | 0.459 | -0.0004 [-0.0031, +0.0024] | 38.0% | 1 |
| `middle_W4` | -0.000128 [-0.000188, -0.000069] | 64.0% | 0.0015 | +0.0156 [+0.0122, +0.0193] | 76.7% | 0.0015 |
| `middle_W5` | -0.000329 [-0.000390, -0.000269] | 79.3% | 0.0015 | +0.0274 [+0.0238, +0.0312] | 94.7% | 0.0015 |
| `shallow_W1` | +0.001315 [+0.000853, +0.001787] | 40.0% | 0.0015 | +0.0521 [-0.0245, +0.1274] | 62.0% | 1 |
| `shallow_W2` | +0.002467 [+0.001820, +0.003126] | 32.0% | 0.0015 | +0.0013 [-0.0985, +0.0993] | 58.7% | 1 |
| `shallow_W3` | +0.002307 [+0.001740, +0.002877] | 30.0% | 0.0015 | +0.0041 [-0.0781, +0.0851] | 59.3% | 1 |
| `shallow_W4` | +0.001616 [+0.001146, +0.002092] | 34.0% | 0.0015 | +0.0468 [-0.0132, +0.1063] | 62.7% | 0.925 |
| `shallow_W5` | +0.000352 [-0.000094, +0.000792] | 46.0% | 0.253 | +0.1306 [+0.0760, +0.1851] | 69.3% | 0.0018 |

## Interaction evidence and magnitude

| Endpoint | Object-cluster Wald (df=8) | Holm p, 16-test family | Interaction share of cell-mean variation | Interaction RMSE per cell | GEE interaction Wald (df=8), p |
|---|---:|---:|---:|---:|---:|
| FG-LPIPS | W=225.015, p=3.35e-44 | 5.37e-43 | 14.0% | 0.000341967 | W=226.717, p=1.46e-44 |
| FG-PSNR | W=525.700, p=2.15e-108 | 3.43e-107 | 36.0% | 0.0204556 | W=529.230, p=3.75e-109 |

The independently formulated object-cluster Wald and Gaussian GEE both detect Layer × Window heterogeneity. The absolute contrast-space interaction RMSE is 0.000342 FG-LPIPS and 0.0205 dB FG-PSNR; the corresponding interaction accounts for 14.0% and 36.0% of variation among the 15 cell means. The large sample-level significance should therefore be read together with these absolute magnitudes and the unequal realized-dose calibration.

### GEE main-effect cross-check

| Endpoint | Layer omnibus (df=2), Holm p across two main effects | Window omnibus (df=4), Holm p across two main effects |
|---|---:|---:|
| FG-LPIPS | W=47.156, p=5.76e-11, Holm=1.15e-10 | W=45.245, p=3.54e-09, Holm=3.54e-09 |
| FG-PSNR | W=136.443, p=2.35e-30, Holm=4.71e-30 | W=57.683, p=8.9e-12, Holm=8.9e-12 |

## Co-reported fidelity, structure, and GT-relative texture outcomes

These endpoints are descriptive and have no multiplicity correction in this report. Each entry is the cell-minus-baseline mean; paired CIs and favorable-object rates for every entry are available in `formal/campaign_FRESH_CONFIRM_B_20261005/A3B_BOUNDED_MAP_ANALYSIS.json`.

| Intervention | Full-PSNR | Full-LPIPS | FG-SSIM | Edge-SSIM | CIEDE2000 | Laplacian log error | RGB-std log error | Gradient log error | HF-energy log error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deep_W1` | -0.00467 | +9.92e-05 | -1.01e-05 | -6.92e-05 | +0.0129 | +0.000311 | +0.000483 | +0.000202 | +3.82e-05 |
| `deep_W2` | -0.00108 | +7.66e-05 | +0.00017 | -6.72e-05 | +0.00178 | +0.000722 | -0.000561 | -0.000163 | +4.19e-05 |
| `deep_W3` | +0.00141 | +4.26e-06 | +0.000316 | -3.8e-05 | -0.00475 | +0.000397 | -0.000623 | -0.000426 | +3.53e-05 |
| `deep_W4` | +0.000463 | +0.000137 | +0.000172 | -1.87e-05 | -0.00133 | +0.000632 | -3.63e-05 | -4.25e-05 | +3.34e-05 |
| `deep_W5` | -0.000464 | +0.000106 | +0.00011 | -3.94e-05 | +0.000367 | +0.000737 | +0.000151 | -3.29e-05 | -3.46e-05 |
| `middle_W1` | -0.00309 | -0.000725 | +0.000868 | +0.00014 | -0.0245 | +0.0019 | -0.000721 | -0.00141 | -5.84e-05 |
| `middle_W2` | -0.00644 | -0.000819 | +0.000391 | -6.99e-05 | -0.00722 | +0.00107 | -0.0004 | -0.000842 | -3.91e-05 |
| `middle_W3` | -0.00215 | -0.00165 | -2.89e-05 | -0.000316 | +0.00854 | -0.0019 | -3.63e-05 | -0.000717 | -0.000238 |
| `middle_W4` | +0.0179 | -0.00329 | +0.00051 | -7.55e-05 | -0.0262 | -0.00256 | -0.000831 | -0.00203 | -0.000492 |
| `middle_W5` | +0.028 | -0.00315 | +0.000569 | +0.000402 | -0.0416 | +0.00562 | -0.000593 | -0.000951 | -0.000161 |
| `shallow_W1` | -0.0774 | -0.0051 | -0.00296 | -0.000592 | -0.412 | -0.0148 | -0.0107 | +0.00999 | -0.00239 |
| `shallow_W2` | -0.0276 | -0.00928 | -0.00531 | -0.00116 | -0.349 | -0.0314 | -0.00554 | +0.0151 | -0.00348 |
| `shallow_W3` | +0.0294 | -0.0112 | -0.00355 | -0.0012 | -0.32 | -0.0443 | -0.00532 | +0.00933 | -0.00389 |
| `shallow_W4` | +0.0883 | -0.016 | -0.000234 | +6.9e-05 | -0.369 | -0.0462 | -0.00586 | +0.00184 | -0.00506 |
| `shallow_W5` | +0.207 | -0.0213 | +0.00245 | +0.00557 | -0.546 | -0.0426 | -0.0137 | +0.00226 | -0.00729 |

## Interpretation

- The frozen bounded intervention produces statistically clear Layer × Window heterogeneity on both FG-LPIPS and FG-PSNR, with agreement between two independent formulations.
- This does not identify an equal-dose or dose-independent mechanism: the shallow scale increment was at the cap and its development proxy was about 1.99× target, while deep and middle were about 20% below target. The interaction may include realized-dose differences.
- The response surface is not uniformly favorable. FG-LPIPS improves across most middle cells but worsens substantially across shallow cells; FG-PSNR has a different pattern, including a positive shallow-W5 mean with wide object-level dispersion. Co-reported color/texture measures also do not move uniformly with the perceptual endpoints.
- Consequently this confirms heterogeneity of the frozen bounded map on FRESH_CONFIRM_B, but does not by itself prove that a dose-controlled 2D allocation law is practically large or universally beneficial. Do not describe A3b as equal-dose, dose-matched, residual-budget controlled, or pure Layer × Time causal proof.

## Provenance

- Protocol: `A3B_PROTOCOL_LOCK.md`.
- Calibration limits: `A3B_DOSE_FEASIBILITY_AUDIT.md`.
- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).
- Complete paired estimates: `formal/campaign_FRESH_CONFIRM_B_20261005/A3B_BOUNDED_MAP_ANALYSIS.json`.
- Texture extension: `formal/campaign_FRESH_CONFIRM_B_20261005/a3b_texture_extension_per_object.csv`.
