# Existing-schedule supplementary validation complete

No new algorithm. Same fixedGSO100 inputs and native interface; no profile search. New4 profiles frozen before outputs, after baseline exposure. Bake calibration addendum is post hoc and rawUV failure retained.

Middle-high minusFixedMean primary all-six FG-PSNR: {'a': 'middle_high', 'b': 'fixed_mean', 'metric': 'fg_psnr', 'mean_difference': -0.013660193648603209, 'ci95_pointwise': [-0.030564535330566998, 0.0035187320121460378], 'p_raw': 0.12227938860305698, 'n_objects': 100, 'seed_means': [-0.008346889416376815, -0.023743611574172815, -0.008890079955260007], 'p_primary': 0.12227938860305698}
GT self-bake mean: {'fg_psnr': 19.36440462144938, 'fg_ssim': 0.7136894668367775, 'fg_lpips': 0.06023042547431858, 'ciede2000': 5.105194036527113}
Baked/image method-rank mean Spearman: 0.601399, objectCI [0.44020979020979023, 0.7332167832167833]
Original375 baked records reproduce exactly. All740 finalbakes retained.

| Bake condition | PSNR | LPIPS | SSIM | dE00 |
|---|---:|---:|---:|---:|
| native | 15.4791 | 0.100869 | 0.478145 | 12.0310 |
| fixed_mean | 15.4995 | 0.100892 | 0.478469 | 11.9734 |
| late_high | 15.5074 | 0.100976 | 0.479614 | 11.9672 |
| grid_projection | 15.1491 | 0.105237 | 0.459246 | 12.3226 |
| view_projection | 14.9979 | 0.106430 | 0.454666 | 12.5020 |
| interaction_projection | 15.1627 | 0.104859 | 0.461116 | 12.2472 |
| apg_projection_only | 15.4998 | 0.101912 | 0.478293 | 11.9522 |
| apg_paper_sd21_at_native_cfg | 15.3046 | 0.102604 | 0.476672 | 12.4743 |
| fixed_low | 15.4845 | 0.101085 | 0.477831 | 11.9939 |
| early_high | 15.4792 | 0.101014 | 0.476968 | 11.9976 |
| middle_high | 15.4728 | 0.101020 | 0.477573 | 12.0327 |
| generic_linear | 15.4989 | 0.100987 | 0.478928 | 11.9795 |
