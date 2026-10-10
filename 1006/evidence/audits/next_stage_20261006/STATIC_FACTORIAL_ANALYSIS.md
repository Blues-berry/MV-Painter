# Static 2×2 factor sensitivity

Post-B fixed-cohort static 2x2 sensitivity; each object first averages paired contrasts across three fixed generation seeds.

Effects are arithmetic responses in the reported metric: negative LPIPS is favorable; positive PSNR is favorable.

## fg_lpips

| Factor | Mean [95% object-bootstrap CI] | Favorable objects | Seed means (42 / 43 / 44) | Holm p |
|---|---:|---:|---|---:|
| deep_middle | -0.0066555 [-0.0088679, -0.0045187] | 81.2% | 42: -0.0062195, 43: -0.0072342, 44: -0.0065127 | 0.00029997 |
| shallow | +0.0058408 [+0.0025063, +0.0092667] | 35.4% | 42: +0.0070402, 43: +0.0031162, 44: +0.0073661 | 0.0015998 |
| interaction | -0.00014683 [-0.00092292, +0.00062046] | 54.2% | 42: -0.00023982, 43: +0.00044467, 44: -0.00064533 | 0.71943 |

## fg_psnr

| Factor | Mean [95% object-bootstrap CI] | Favorable objects | Seed means (42 / 43 / 44) | Holm p |
|---|---:|---:|---|---:|
| deep_middle | +0.54377 [+0.32879, +0.76312] | 72.9% | 42: +0.47597, 43: +0.83874, 44: +0.31661 | 0.00029997 |
| shallow | -0.11635 [-0.65467, +0.39861] | 52.1% | 42: -0.0049262, 43: -0.60941, 44: +0.2653 | 0.66773 |
| interaction | +0.36451 [+0.24315, +0.48639] | 72.9% | 42: +0.38611, 43: +0.25781, 44: +0.4496 | 0.00029997 |

Selected 48-object post-B sensitivity, conditional on these three fixed generation seeds; not independent-object confirmation or a random-seed population interval. Deep and middle are moved together; no equal-realized-dose claim. Simple contrasts are descriptive.
