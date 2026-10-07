# Multi-seed sensitivity results

Post-B supplementary multi-realization sensitivity; fixed stratified 48-object sample; effects average three generation-seed paired contrasts within object; object bootstrap conditional on these three seeds

All deltas are LLH minus comparator. Positive FG-PSNR and negative FG-LPIPS favor LLH.

## fg_lpips

| Comparator | Mean [95% object-bootstrap CI] | Favorable objects | Same-sign objects in all seeds | Effect / median seed range | Seed means | Holm p |
|---|---:|---:|---:|---:|---|---:|
| native_gfl | -0.014491 [-0.019878, -0.0092541] | 77.1% | 60.4% | 1.22 | 42: -0.015398, 43: -0.014419, 44: -0.013654 | 0.00049995 |
| native_gfh | +0.00052173 [-0.0014321, +0.0026808] | 35.4% | 29.2% | 0.0827 | 42: -0.0015935, 43: +0.0013183, 44: +0.0018404 | 0.62014 |
| native_gc3 | -0.0098889 [-0.013574, -0.0062495] | 77.1% | 56.2% | 0.971 | 42: -0.010168, 43: -0.010456, 44: -0.0090429 | 0.00049995 |
| lfm_exact | -0.003908 [-0.0054916, -0.0024518] | 79.2% | 47.9% | 0.675 | 42: -0.0045133, 43: -0.0051574, 44: -0.0020534 | 0.00049995 |
| gen_linear | +0.00093934 [+6.9259e-05, +0.0018927] | 43.8% | 12.5% | 0.379 | 42: +0.0010835, 43: +0.00067753, 44: +0.001057 | 0.089591 |

## fg_psnr

| Comparator | Mean [95% object-bootstrap CI] | Favorable objects | Same-sign objects in all seeds | Effect / median seed range | Seed means | Holm p |
|---|---:|---:|---:|---:|---|---:|
| native_gfl | +1.1201 [+0.42258, +1.8336] | 58.3% | 45.8% | 0.576 | 42: +0.93528, 43: +2.0032, 44: +0.42175 | 0.0050995 |
| native_gfh | -0.48917 [-0.74656, -0.20843] | 25.0% | 12.5% | 0.71 | 42: -0.41785, 43: -0.323, 44: -0.72667 | 0.0023998 |
| native_gc3 | +0.50994 [+0.019742, +1.0246] | 50.0% | 35.4% | 0.391 | 42: +0.39955, 43: +1.1494, 44: -0.019092 | 0.092791 |
| lfm_exact | +0.32945 [+0.17885, +0.49738] | 75.0% | 41.7% | 0.575 | 42: +0.28366, 43: +0.60464, 44: +0.10005 | 0.0014999 |
| gen_linear | -0.058382 [-0.1371, +0.017826] | 35.4% | 18.8% | 0.224 | 42: -0.043681, 43: -0.061963, 44: -0.069503 | 0.13749 |

Inference describes these 48 fixed objects averaged over these three seeds; seed variability and the absolute-effect/median-seed-range ratio are descriptive, not a random-seed population CI or a test against realization noise. This selected post-B cohort is not independent-object confirmation. p values at the reporting floor are not exact zero.

Provenance: locked integrity gate `cd925e671eb4d47ed405fcde3e959bf9d2732324f99d119b755d044d1d715e8b`; read-only re-audit `514860a5b9f9384153b9ae670fa4105a385a25830adc52335e6e4f80d626da9e`; analysis source `950aad8b634e9db65e0c3a3ee672f8f6e27b50c8f5a5fe0e96141276a8e69046`; 6 raw row files hashed.
