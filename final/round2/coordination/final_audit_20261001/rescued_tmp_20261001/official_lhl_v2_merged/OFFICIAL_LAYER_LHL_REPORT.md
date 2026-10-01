# Temporary official layer-LHL holdout analysis

This report is outside the repository and uses the frozen clean-v2 276-object holdout.
Rows are paired by object ID. Positive deltas mean layer-LHL minus comparator; for LPIPS, lower is better and win rates use the correct direction.

## Standard metrics

| comparator | Full PSNR | Full SSIM | Full LPIPS | FG PSNR | FG SSIM | FG LPIPS | Edge SSIM |
|---|---:|---:|---:|---:|---:|---:|---:|
| layer vs fixed_low | 22.0516 (+6.9652) | 0.8841 (+0.0339) | 0.1857 (-0.0079) | 14.7763 (+7.7467) | 0.5510 (+0.1962) | 0.1338 (-0.0687) | 0.5533 (+0.0531) |
| layer vs c3 | 22.0516 (+7.1771) | 0.8841 (+0.0293) | 0.1857 (-0.0038) | 14.7763 (+8.0134) | 0.5510 (+0.2027) | 0.1338 (-0.0676) | 0.5533 (+0.0533) |
| layer vs fixed_high | 22.0516 (+8.6869) | 0.8841 (+0.0608) | 0.1857 (-0.0040) | 14.7763 (+9.3667) | 0.5510 (+0.3219) | 0.1338 (-0.0766) | 0.5533 (+0.0596) |
| layer vs fixed_mean | 22.0516 (+7.7402) | 0.8841 (+0.0416) | 0.1857 (-0.0025) | 14.7763 (+8.5196) | 0.5510 (+0.2350) | 0.1338 (-0.0714) | 0.5533 (+0.0548) |
| layer vs c3_lhl | 22.0516 (+7.1838) | 0.8841 (+0.0296) | 0.1857 (-0.0039) | 14.7763 (+8.0167) | 0.5510 (+0.2029) | 0.1338 (-0.0676) | 0.5533 (+0.0531) |
| layer vs llh | 22.0516 (+6.9157) | 0.8841 (+0.0323) | 0.1857 (+0.0048) | 14.7763 (+7.8396) | 0.5510 (+0.1941) | 0.1338 (-0.0658) | 0.5533 (+0.0178) |
| layer vs hll | 22.0516 (+8.6546) | 0.8841 (+0.0589) | 0.1857 (-0.0164) | 14.7763 (+9.1932) | 0.5510 (+0.2923) | 0.1338 (-0.0778) | 0.5533 (+0.0898) |

Format: layer mean (layer minus comparator mean). Full details, medians, 95% paired bootstrap CIs, and win rates are in `official_comparisons.json`.

## Texture probes

| comparator | RGB std delta | gradient delta | Lap variance delta | HF energy delta |
|---|---:|---:|---:|---:|
| layer vs fixed_low | -0.021719 | -0.198242 | -0.022268 | -0.081576 |
| layer vs c3 | -0.014454 | -0.183332 | -0.022018 | -0.090215 |
| layer vs fixed_high | +0.000000 | -0.127940 | -0.015274 | -0.127636 |
| layer vs fixed_mean | -0.012985 | -0.174558 | -0.020199 | -0.103134 |
| layer vs c3_lhl | -0.014472 | -0.183439 | -0.022003 | -0.090317 |
| layer vs llh | -0.013744 | -0.175086 | -0.015944 | -0.102973 |
| layer vs hll | -0.010810 | -0.145642 | -0.022590 | -0.103822 |
