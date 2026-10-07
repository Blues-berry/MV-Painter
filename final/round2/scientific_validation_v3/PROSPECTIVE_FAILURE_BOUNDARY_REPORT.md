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

## Independent replication on FRESH_CONFIRM_B

The same frozen H5 comparison and 10-test family were evaluated separately on the disjoint FRESH_CONFIRM_B cohort (n=150), using the already frozen `layer_llh` and `native_gfl` conditions. No object was removed by outcome. The five predictors were fixed GT-only measurements. The four GT texture statistics are exactly condition-invariant across all 30 B conditions. Coverage was recomputed from the six official target-view GT images in the frozen B manifest as the mean per-view alpha>0 pixel fraction, matching the original cohort's coverage definition; it was not taken from prediction-side `crop_area`.

**Timing boundary:** H5 and its 10-test family appear in the 2026-10-02
pre-run `PRIMARY_HYPOTHESES.md`, and the B identity cohort was frozen at
2026-10-05 07:35 UTC before B method outputs. The B-wide multiplicity lock and
checksum inventory were created later; `B_PREUNBLIND_MANIFEST.md` explicitly
states that B outcomes had already been disclosed, and the lock labels itself
retrospective. Accordingly, this is disjoint-cohort corroboration of the
pre-existing H5 pattern, not a claim that the full B campaign was prospectively
locked or that its other analyses are confirmatory.

The paired B effect was +1.030 dB FG-PSNR [0.570, 1.496] (51.3% of objects favored LLH) and −0.01556 FG-LPIPS [−0.01914, −0.01192] (74.0% favored LLH). The modest PSNR win rate alongside a positive mean indicates a skewed distribution, so the mean gain should not be described as a typical per-object gain.

| Outcome | GT predictor | Spearman rho, 95% bootstrap CI | Raw p (plus-one) | Holm p (10 tests) | Reject at .05 |
|---|---|---:|---:|---:|---|
| FG-PSNR | GT Laplacian variance | −0.538 [−0.645, −0.410] | 0.000200 | 0.00200 | Yes |
| FG-PSNR | GT RGB std | −0.288 [−0.451, −0.114] | 0.00200 | 0.00800 | Yes |
| FG-PSNR | GT gradient magnitude | −0.476 [−0.595, −0.336] | 0.000200 | 0.00200 | Yes |
| FG-PSNR | GT HF energy | −0.624 [−0.714, −0.513] | 0.000200 | 0.00200 | Yes |
| FG-PSNR | foreground coverage | −0.068 [−0.230, +0.100] | 0.42856 | 0.42856 | No |
| FG-LPIPS | GT Laplacian variance | +0.665 [+0.556, +0.753] | 0.000200 | 0.00200 | Yes |
| FG-LPIPS | GT RGB std | +0.264 [+0.087, +0.438] | 0.00460 | 0.01380 | Yes |
| FG-LPIPS | GT gradient magnitude | +0.623 [+0.499, +0.726] | 0.000200 | 0.00200 | Yes |
| FG-LPIPS | GT HF energy | +0.647 [+0.546, +0.730] | 0.000200 | 0.00200 | Yes |
| FG-LPIPS | foreground coverage | −0.206 [−0.367, −0.039] | 0.01760 | 0.03520 | Yes |

Nine of ten tests reject in B as well. All eight texture-complexity tests replicate with the preregistered direction. Coverage does not: it is unrelated to FG-PSNR in B, while its FG-LPIPS association is significant, the reverse of the original cohort's endpoint-specific coverage pattern.

The B texture quartiles were computed within B from GT Laplacian variance (cutpoints 0.006856, 0.017710, 0.031392; group sizes 38/37/37/38):

| B GT texture quartile | Mean ΔFG-PSNR (dB) | LLH favorable rate, FG-PSNR | Mean ΔFG-LPIPS | LLH favorable rate, FG-LPIPS |
|---|---:|---:|---:|---:|
| Q1 (n=38) | +3.646 | 84.2% | −0.03768 | 100.0% |
| Q2 (n=37) | +1.260 | 62.2% | −0.01741 | 91.9% |
| Q3 (n=37) | −0.037 | 40.5% | −0.00688 | 59.5% |
| Q4 (n=38) | −0.770 | 18.4% | −0.00008 | 44.7% |

The independent B replication again places the largest gains in the lower-texture quartiles; in its highest-texture quartile, LLH loses on mean FG-PSNR and has no average FG-LPIPS advantage. Quartile thresholds were not chosen from method outcomes.

Machine-readable B evidence:

- GT-only statistics: `formal/campaign_FRESH_CONFIRM_B_20261005/GT_TEXTURE_STATS_FRESH_CONFIRM_B.json` (SHA256 `aa37597c0fd781dbc50c272666272c00385ad919f72947c50e1f286de4a94578`)
- Spearman tests and quartiles: `formal/campaign_FRESH_CONFIRM_B_20261005/SPEARMAN_TEXTURE_BOUNDARY_B.json` (SHA256 `a9c604096aecd691b164e73fa1573d414079fc33aab4f90d08ff5a947a985002`)
- Overall paired contrast: `formal/campaign_FRESH_CONFIRM_B_20261005/FAILURE_BOUNDARY_PAIRWISE_B.json`

## Conclusion and limits

**Replicated GT-predictable applicability boundary.** Two separate cohorts support the same direction for all eight GT texture-complexity associations across FG-PSNR and FG-LPIPS. In both, gains are largest for low-texture objects and shrink toward zero or reverse in the highest-texture quartile. Coverage is less stable and should not be promoted as a general predictor. These are metric-based associations, not evidence that GT texture statistics cause the errors or a substitute for human perceptual evaluation. The analysis does not establish which weaker or less concentrated intervention would work best for texture-rich objects.

The prior cohort's old unadjusted bootstrap JSON is preserved as `spearman_texture_boundary_legacy_unadjusted.json` (SHA256 `7f8b9f9c8f72dfcc0d322b131fdcc2fa8b09b09474fe556cd3f68f6825c374ab`). Both cohorts are reported separately; no pooling, threshold fitting, or outcome-based exclusions were performed.
