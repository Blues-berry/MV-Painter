# Prospective failure-boundary report — Experiment E / H5

**Cohort:** FRESH_CONFIRM_300, n=300 unique objects. Experiment E and its GT-only predictors were specified before the fresh cohort outcomes; every technically valid object is retained. The comparison is LLH−native GFL under the same B3 runner, checkpoint, inputs, seed, and views. GT texture/coverage statistics are condition-independent and were computed from reference images only.

## Overall paired effect

| Metric | LLH−GFL mean | 95% paired bootstrap CI | Favorable-object rate |
|---|---:|---:|---:|
| FG-PSNR | +1.288 dB | [+0.938, +1.635] | 57.7% |
| FG-LPIPS | -0.01650 | [-0.01887, -0.01413] | 73.3% |

For FG-PSNR, positive deltas favor LLH; for FG-LPIPS, negative deltas favor LLH. Favorable-object rates are direction-aware.

## GT-only texture and coverage relationships

Spearman rho was bootstrapped by resampling paired objects (10,000 draws, seed 20261002). The preregistered family contains 2 outcomes × 5 GT-only statistics; p-values use a plus-one Monte Carlo correction and Holm adjustment across all 10 tests.

| Outcome | GT predictor | Spearman rho, 95% bootstrap CI | Raw p | Holm p | Reject at .05 |
|---|---|---:|---:|---:|---|
| FG-PSNR | GT Laplacian variance | -0.524 [-0.603, -0.435] | 0.00019998 | 0.0019998 | Yes |
| FG-PSNR | GT RGB std | -0.380 [-0.488, -0.266] | 0.00019998 | 0.0019998 | Yes |
| FG-PSNR | GT gradient magnitude | -0.464 [-0.547, -0.371] | 0.00019998 | 0.0019998 | Yes |
| FG-PSNR | GT HF energy | -0.691 [-0.745, -0.626] | 0.00019998 | 0.0019998 | Yes |
| FG-PSNR | foreground coverage | -0.134 [-0.241, -0.026] | 0.017598 | 0.035196 | Yes |
| FG-LPIPS | GT Laplacian variance | +0.604 [+0.511, +0.681] | 0.00019998 | 0.0019998 | Yes |
| FG-LPIPS | GT RGB std | +0.379 [+0.272, +0.482] | 0.00019998 | 0.0019998 | Yes |
| FG-LPIPS | GT gradient magnitude | +0.563 [+0.469, +0.643] | 0.00019998 | 0.0019998 | Yes |
| FG-LPIPS | GT HF energy | +0.677 [+0.599, +0.744] | 0.00019998 | 0.0019998 | Yes |
| FG-LPIPS | foreground coverage | -0.118 [-0.233, +0.000] | 0.050795 | 0.050795 | No |

Nine of ten tests pass the Holm threshold. Four texture-richness measures predict a smaller LLH advantage on both FG-PSNR and FG-LPIPS. Coverage is a weaker correlate: FG-PSNR remains significant after Holm; FG-LPIPS does not. No texture threshold was fitted to the method outcomes.

## Texture-complexity quartiles

Quartiles use frozen GT Laplacian variance, with 75 objects per quartile. Higher quartiles are more texture-rich.

| GT texture quartile | Mean ΔFG-PSNR (dB) | LLH favorable rate, FG-PSNR | Mean ΔFG-LPIPS | LLH favorable rate, FG-LPIPS |
|---|---:|---:|---:|---:|
| Q1 (n=75) | +4.140 | 92.0% | -0.03745 | 97.3% |
| Q2 (n=75) | +1.127 | 52.0% | -0.01665 | 81.3% |
| Q3 (n=75) | -0.087 | 41.3% | -0.00670 | 64.0% |
| Q4 (n=75) | -0.029 | 45.3% | -0.00520 | 50.7% |

The large PSNR gain is concentrated in the lowest-texture quartile. It falls from +4.14 dB in Q1 to approximately zero in Q3/Q4, where the PSNR win rate is below 50%. The LPIPS advantage also shrinks markedly with texture richness, although its mean remains favorable to LLH in all four quartiles. This supports an applicability boundary, not a claim that LLH always loses on textured objects.

## Conclusion and limits

**Prospectively replicated, GT-predictable metric boundary.** The average LLH−GFL gain is not population-uniform: low-texture objects benefit most; high-texture cases show little or no PSNR gain, while LPIPS still favors LLH on average but by less. The predictors support a deployment caveat and the need to preserve texture-rich failures in the narrative. These are metric-based associations, not evidence that the GT statistics causally produce the errors or a substitute for human perceptual evaluation.

The old unadjusted bootstrap JSON is preserved as `spearman_texture_boundary_legacy_unadjusted.json` (SHA256 `7f8b9f9c8f72dfcc0d322b131fdcc2fa8b09b09474fe556cd3f68f6825c374ab`). The canonical `spearman_texture_boundary.json` now records plus-one p-values, the frozen 10-test Holm family, and direction-aware quartile favorable rates. Cell rows and model outputs were not changed.
