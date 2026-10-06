# TEXTURE_COMPLEXITY_FAILURE_BOUNDARY — Experiment E (H5)

Pre-registered H0: LLH−GFL performance is independent of GT texture complexity.
CONFIRMATORY result: **H0 rejected — the failure boundary REPLICATES
prospectively** on FRESH_CONFIRM_300 (no result-based exclusions).

Artifacts: formal/campaign_B3/pairwise_layer_llh_vs_native_gfl.json,
spearman_texture_boundary.json, gt_stats.json (GT-only statistics, cross-checked
condition-independent), build_gt_stats_json.py.

Overall paired effect (n=300): LLH − GFL = +1.288 dB FG-PSNR [0.938, 1.635],
−0.0165 FG-LPIPS [−0.0189, −0.0141].

Spearman (10k paired-object bootstrap CIs; texture-only correlations below
exclude zero):
  * ΔFG-PSNR ~ GT HF energy −0.691 [−0.745, −0.626]
  * ΔFG-PSNR ~ GT Laplacian variance −0.524 [−0.603, −0.435]
  * ΔFG-PSNR ~ GT gradient magnitude −0.464; ~ GT RGB std −0.380
  * ΔFG-LPIPS ~ GT HF energy +0.677; ~ GT Laplacian variance +0.604
  * coverage: weaker (FG-PSNR rho −0.134; FG-LPIPS rho −0.118 and its CI
    touches zero)

The canonical reanalysis applies the pre-registered 10-test Holm family and
plus-one Monte Carlo p-values; nine of ten tests reject at .05. GT coverage is
significant for FG-PSNR after Holm (p=.0352), but not for FG-LPIPS (p=.0508).
See `PROSPECTIVE_FAILURE_BOUNDARY_REPORT.md` and the corrected
`formal/campaign_B3/spearman_texture_boundary.json`. The earlier zero-tail
bootstrap file is preserved as `spearman_texture_boundary_legacy_unadjusted.json`.

## Independent replication on FRESH_CONFIRM_B

The frozen H5 comparison was repeated separately on the disjoint 150-object
FRESH_CONFIRM_B cohort. All eight GT texture-complexity associations
replicated in the preregistered direction after the same 10-test Holm family;
coverage was not stable across endpoints (FG-PSNR null, FG-LPIPS significant).
The upper-texture quartile again had little or negative mean FG-PSNR gain and
no average FG-LPIPS advantage. Cohorts remain separate and are not pooled.
Full results, including the B-specific GT-only statistics and quartiles, are
in `PROSPECTIVE_FAILURE_BOUNDARY_REPORT.md` and
`formal/campaign_FRESH_CONFIRM_B_20261005/SPEARMAN_TEXTURE_BOUNDARY_B.json`.

Texture-complexity quartiles (GT Laplacian variance), (mean ΔFG-PSNR, LLH win rate):
  Q1 +4.14 dB (0.92) | Q2 +1.13 dB (0.52) | Q3 −0.09 dB (0.41) | Q4 −0.03 dB (0.45)

Interpretation: LLH's average advantage is carried by texture-poor objects.
On texture-rich objects GFL matches or beats LLH — the 34-loss pattern found
forensically on strict-276 reproduces as a systematic, GT-predictable failure
boundary (LLH under-delivers high-frequency detail where the GT is rich).
This boundary is scientifically more valuable than hiding the losses and
directly constrains deployment claims.
