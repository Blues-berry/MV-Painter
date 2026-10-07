# R1.4 post-hoc paired audit: C3 versus high fixed scale

**Purpose.** Add the paired C3−GFH Edge-SSIM interval requested by Reviewer 1 using already-generated non-human outputs. This analysis was not in the frozen confirmatory families and is not a replacement for the original N=300 Table 4 result.

## Source and pairing checks

- Cohort: `FRESH_CONFIRM_B`, 150 objects.
- Source: `/4T/CXY/MV-Painter/1006/data/fresh_b/per_object_metrics.csv`.
- Source SHA-256: `ce7ba03f6dcb9f1d275b389c633e23dc544404eeac4ddf090e90a11ad278e081`.
- Source rows: 4,500 object-condition rows. The raw CSV currently resides in the shared `/4T/CXY/MV-Painter` checkout and is not included in this clean evidence worktree; the hash identifies the input used, but this note alone is not a clean-checkout reproduction package.
- Contrast: `native_gc3 − native_gfh` (C3 minus global high fixed scale).
- Pairing checks: 150 unique object IDs per condition; exact UID-set match; no duplicate condition/UID key; generation seed matches within every pair. All checks passed.
- The cohort is disjoint from the earlier selected 300-object cohort. The comparison was selected after outcomes had been unblinded; it is retrospective/post-hoc.

## Estimator

For each metric, compute one C3−GFH difference per object. The object is the inferential unit. Use 10,000 paired object-bootstrap resamples, NumPy `default_rng(20261002)`, and the two-sided percentile 95% interval. Report the proportion of objects favoring C3 using higher-is-better for PSNR/SSIM and lower-is-better for LPIPS. A two-sided bootstrap sign-crossing p-value and Holm adjustment across the seven Core-7 endpoints are included only as post-hoc sensitivity summaries; they do not restore preregistration.

## Results

| Endpoint | C3 − GFH mean | Nominal 95% paired object-bootstrap CI | Median | Objects favoring C3 | Post-hoc Holm p |
|---|---:|---:|---:|---:|---:|
| FG-PSNR (dB) | −0.7531 | [−0.9278, −0.5786] | −0.7586 | 44/150 (29.3%) | 0.0007 |
| FG-SSIM | −0.03888 | [−0.04440, −0.03346] | −0.03688 | 20/150 (13.3%) | 0.0007 |
| FG-LPIPS | +0.008264 | [+0.006007, +0.010452] | +0.008486 | 40/150 (26.7%) | 0.0007 |
| Full-PSNR (dB) | +0.7490 | [+0.6548, +0.8414] | +0.7830 | 133/150 (88.7%) | 0.0007 |
| Full-SSIM | +0.002662 | [+0.001089, +0.003999] | +0.004660 | 115/150 (76.7%) | 0.0048 |
| Full-LPIPS | −0.000272 | [−0.002556, +0.002002] | −0.000334 | 78/150 (52.0%) | 0.7974 |
| Edge-SSIM | −0.018486 | [−0.021465, −0.015527] | −0.016451 | 26/150 (17.3%) | 0.0007 |

For Edge-SSIM, higher is better, so the estimate and interval favor GFH. The result also shows an endpoint trade-off: full-image PSNR/SSIM favor C3, while foreground PSNR/SSIM/LPIPS and Edge-SSIM favor GFH; full-image LPIPS is inconclusive. Favorable-object fractions are descriptive and do not imply a typical-object benefit.

## Interpretation limits

This is a post-hoc comparison in a separate N=150 cohort. It is not an independent preregistered test of the original Table 4 contrast, does not set a non-inferiority margin, and does not justify equivalence or a universal winner. The primary manuscript response should disclose this status and narrow the preservation claim.
