# Clean-v2 source-stratified results

This is a prespecified source-composition sensitivity audit. It does not remove or select objects.

## Set relations

- `historical_train_1118_count`: `1118`
- `train_objects_1200_count`: `1200`
- `historical_intersection_candidate_pool_count`: `1011`
- `replacement_101_count`: `101`
- `replacement_subset_candidate_pool`: `True`
- `replacement_intersection_historical_train`: `0`
- `clean_v2_count`: `300`
- `clean_v2_intersection_historical_train`: `0`
- `clean_v2_decomposition`: `199 retained old-eval UIDs + 101 replacement UIDs`

## Group means

| group | n | condition | Full PSNR | FG PSNR | Full SSIM | FG SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| retained_199 | 199 | no_adapter | 10.283 | 8.029 | 0.721 | 0.438 | 0.219 | 0.455 |
| retained_199 | 199 | fixed_low | 15.411 | 7.460 | 0.847 | 0.354 | 0.202 | 0.499 |
| retained_199 | 199 | fixed_high | 13.701 | 5.844 | 0.823 | 0.245 | 0.210 | 0.499 |
| retained_199 | 199 | c3 | 15.210 | 7.205 | 0.852 | 0.351 | 0.201 | 0.499 |
| replacement_101 | 101 | no_adapter | 11.164 | 10.809 | 0.739 | 0.585 | 0.178 | 0.541 |
| replacement_101 | 101 | fixed_low | 14.040 | 5.822 | 0.858 | 0.355 | 0.208 | 0.499 |
| replacement_101 | 101 | fixed_high | 12.303 | 4.183 | 0.821 | 0.188 | 0.217 | 0.476 |
| replacement_101 | 101 | c3 | 13.807 | 5.545 | 0.861 | 0.342 | 0.207 | 0.499 |

## Paired C3 differences

The JSON contains 10,000 object-level bootstrap resamples and 95% CIs for C3 versus fixed-low and fixed-high. All pairs use source UIDs mapped to the clean-v2 object IDs; no sequence-number substitution is used.
