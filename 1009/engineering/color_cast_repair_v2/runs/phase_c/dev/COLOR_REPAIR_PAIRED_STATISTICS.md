# C1 dev paired results

Objects: 4. Primary unit: object, with the five non-source views averaged equally.
Confidence intervals are 10,000 paired object bootstrap percentile intervals; wins are oriented so favorable change counts as a win.

| Endpoint | n | Mean Δ | 95% CI | Median Δ | Wins / losses / ties | dz |
|---|---:|---:|---:|---:|---:|---:|
| unseen_fg_ciede2000 (lower is better) | 4 | -1.56022 | [-2.26212, -0.62990] | -1.78863 | 4 / 0 / 0 | -1.572 |
| unseen_fg_lpips (lower is better) | 4 | -0.00186 | [-0.00585, 0.00145] | -0.00119 | 3 / 1 / 0 | -0.432 |
| unseen_gt_laplacian_error (lower is better) | 4 | -0.00024 | [-0.00056, 0.00015] | -0.00039 | 3 / 1 / 0 | -0.534 |
| source_fg_ciede2000 (lower is better) | 4 | -1.62049 | [-2.61970, -0.59756] | -1.64421 | 4 / 0 / 0 | -1.337 |
| source_fg_lpips (lower is better) | 4 | -0.00139 | [-0.00700, 0.00268] | 0.00099 | 2 / 2 / 0 | -0.228 |
| unseen_fg_psnr (higher is better) | 4 | 0.18051 | [0.01403, 0.30228] | 0.25033 | 3 / 1 / 0 | 0.995 |
| unseen_lstar_ssim_to_gt (higher is better) | 4 | -0.00015 | [-0.00052, 0.00006] | 0.00002 | 2 / 2 / 0 | -0.386 |
| source_fg_psnr (higher is better) | 4 | 0.20273 | [0.01213, 0.35646] | 0.23961 | 3 / 1 / 0 | 1.043 |
| source_lstar_ssim_to_gt (higher is better) | 4 | 0.00002 | [-0.00033, 0.00039] | 0.00001 | 2 / 2 / 0 | 0.050 |

## Frozen development gate

- `at_least_three_of_four_unseen_ciede_improve`: PASS
- `mean_unseen_ciede_delta_le_minus_1`: PASS
- `mean_unseen_psnr_delta_above_minus_0p5_db`: PASS
- `mean_unseen_lpips_delta_below_plus_0p010`: PASS
- `mean_unseen_lstar_ssim_delta_above_minus_0p010`: PASS
- `all_numeric_development_criteria`: PASS
- `visual_failure_cases_reviewed`: PASS
- `normal_and_high_texture_reviewed`: PASS
- `both_failure_cases_visibly_improved_without_new_cast`: FAIL
- `normal_and_high_texture_quality_preserved`: PASS
- `all_development_criteria_pass`: FAIL

Visual failure-case review and normal/high-texture inspection remain manual gates.
