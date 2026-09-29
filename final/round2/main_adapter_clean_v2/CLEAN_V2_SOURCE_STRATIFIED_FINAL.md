# Clean-v2 source-stratified supplementary candidate

Status: frozen source-composition audit. This table is descriptive and was not used to remove objects, select a checkpoint, select C3, or select a schedule.

## Provenance and isolation

| group | n | unique source UIDs | historical 1118 overlap | relation to train_objects_1200 |
|---|---:|---:|---:|---|
| retained old evaluation | 199 | 199/199 | 0 | inherited old-evaluation membership |
| replacement | 101 | 101/101 | 0 | 101/101 are in candidate pool |

The full clean-v2 list has 300 unique source UIDs and zero intersection with historical `train_objects_1118`. The candidate pool `train_objects_1200` contains 1,011 historical-1118 UIDs; replacement-101 is a subset of the pool but disjoint from historical-1118. Source UIDs and available source-asset SHA-256 values are recorded in `clean_v2_provenance_300.csv`.

## Absolute metrics

Values are means over the indicated source group, using the frozen original float-eval per-object CSVs. LPIPS retains the `REUSED_ORIGINAL_EVAL` provenance.

| group | n | condition | Full PSNR | FG PSNR | Full SSIM | FG SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| retained | 199 | no adapter | 10.283 | 8.029 | 0.721 | 0.438 | 0.219 | 0.455 |
| retained | 199 | fixed-low | 15.411 | 7.460 | 0.847 | 0.354 | 0.202 | 0.499 |
| retained | 199 | fixed-high | 13.701 | 5.844 | 0.823 | 0.245 | 0.210 | 0.499 |
| retained | 199 | C3 | 15.210 | 7.205 | 0.852 | 0.351 | 0.201 | 0.499 |
| replacement | 101 | no adapter | 11.164 | 10.809 | 0.739 | 0.585 | 0.178 | 0.541 |
| replacement | 101 | fixed-low | 14.040 | 5.822 | 0.858 | 0.355 | 0.208 | 0.499 |
| replacement | 101 | fixed-high | 12.303 | 4.183 | 0.821 | 0.188 | 0.217 | 0.476 |
| replacement | 101 | C3 | 13.807 | 5.545 | 0.861 | 0.342 | 0.207 | 0.499 |

## Paired C3 differences

Entries are `C3 − baseline`; CI is object-level paired bootstrap, 10,000 resamples, seed `20260928`. Full machine-readable results are in `source_stratified_results.json`.

| group | baseline | metric | mean | 95% CI | C3 win rate |
|---|---|---|---:|---|---:|
| retained | fixed-low | Full PSNR | -0.201 | [-0.226, -0.176] | 0.121 |
| retained | fixed-low | FG PSNR | -0.255 | [-0.284, -0.228] | 0.075 |
| retained | fixed-low | Full SSIM | 0.0049 | [0.0042, 0.0057] | 0.854 |
| retained | fixed-low | FG SSIM | -0.0032 | [-0.0057, -0.0007] | 0.427 |
| retained | fixed-low | FG-LPIPS | 0.0011 | [0.0006, 0.0016] | 0.573 |
| retained | fixed-high | Full PSNR | 1.509 | [1.434, 1.587] | 1.000 |
| retained | fixed-high | FG PSNR | 1.362 | [1.267, 1.455] | 0.965 |
| retained | fixed-high | Full SSIM | 0.0284 | [0.0253, 0.0315] | 0.925 |
| retained | fixed-high | FG SSIM | 0.1063 | [0.0972, 0.1154] | 0.955 |
| retained | fixed-high | FG-LPIPS | 0.0088 | [0.0074, 0.0103] | 0.754 |
| replacement | fixed-low | Full PSNR | -0.232 | [-0.267, -0.198] | 0.030 |
| replacement | fixed-low | FG PSNR | -0.277 | [-0.316, -0.237] | 0.020 |
| replacement | fixed-low | Full SSIM | 0.0038 | [0.0026, 0.0051] | 0.752 |
| replacement | fixed-low | FG SSIM | -0.0123 | [-0.0165, -0.0081] | 0.337 |
| replacement | fixed-low | FG-LPIPS | 0.0008 | [0.0003, 0.0014] | 0.624 |
| replacement | fixed-high | Full PSNR | 1.505 | [1.370, 1.649] | 0.980 |
| replacement | fixed-high | FG PSNR | 1.362 | [1.174, 1.528] | 0.980 |
| replacement | fixed-high | Full SSIM | 0.0403 | [0.0350, 0.0459] | 0.990 |
| replacement | fixed-high | FG SSIM | 0.1544 | [0.1395, 0.1692] | 0.980 |
| replacement | fixed-high | FG-LPIPS | 0.0097 | [0.0070, 0.0124] | 0.703 |

The source groups differ materially in absolute foreground quality, especially for no-adapter, but the C3-versus-fixed-low/high directional conclusions are not rescued by removing either group. No object is deleted or substituted after observing these results.
