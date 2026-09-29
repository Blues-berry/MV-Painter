# MV-Adapter Matched-Range Exact Results

This is a targeted follow-up analysis, not the originally frozen confirmatory
holdout. It corrects the scale-range mismatch identified in the original
holdout: both dynamic schedules below use `low=0.75, high=1.00`.

## Data and provenance

Directory: `results/holdout_exact_matched_range_76/`

- 76 objects × 2 new schedules = 152 rows;
- all rows `geometry_source=exact_mesh`;
- same object IDs, reference images, camera order, seed `20260928` and 50 steps
  as `holdout_exact_76`;
- code, manifest and model records are in `PROTOCOL.json`;
- historical high=1.50 linear/cosine rows remain in
  `results/holdout_exact_76/`.

## Object-level means

| Schedule | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | ΔE00 | GT-relative texture error |
|---|---:|---:|---:|---:|---:|---:|
| Linear warmup (0.75→1.00) | 13.332426 | 0.528047 | 0.240094 | 0.188445 | 20.194007 | 2.182502 |
| Cosine bump (0.75↗1.00↘0.75) | 13.327002 | 0.527812 | 0.239955 | 0.188232 | 20.211197 | 2.215665 |

For reference, the reused Exact constants are `fixed_low=0.75`,
`fixed_1.0=1.00`, and `no_geometry=0.0`; their source remains the original
five-condition CSV.

## Paired bootstrap

Machine-readable output:

`results/holdout_exact_matched_range_76/matched_range_bootstrap.json`

All comparisons use 10,000 object-level resamples, seed `20260928`, 95% CIs.
The full six-metric result includes both new schedules against
`no_geometry`, `fixed_low`, `fixed_1.0`, and LHL, plus linear-vs-cosine and
LHL-vs-each-new-dynamic comparison.

Selected direction-aware deltas (new schedule minus comparator) are:

| Comparison | ΔPSNR | ΔFG-SSIM | ΔEdge-SSIM | ΔFG-LPIPS* | ΔΔE00* | ΔGT-texture* |
|---|---:|---:|---:|---:|---:|---:|
| Linear − fixed-low | −0.024752 | 0.000508 | 0.000097 | −0.000752 | −0.044464 | 0.041546 |
| Cosine − fixed-low | −0.030175 | 0.000273 | −0.000043 | −0.000539 | −0.061654 | 0.008382 |
| Linear − fixed-1.0 | 0.014802 | 0.000698 | 0.000441 | 0.000314 | 0.070203 | 0.015376 |
| Cosine − fixed-1.0 | 0.009379 | 0.000463 | 0.000301 | 0.000527 | 0.053013 | −0.017788 |
| Linear − cosine | 0.005424 | 0.000234 | 0.000140 | −0.000213 | 0.017190 | 0.033164 |

*Error columns are direction-adjusted so positive favors the left schedule.
Exact CIs, win rates and all remaining comparisons are retained in the JSON.

## Interpretation

Once the scale range is matched, linear and cosine remain close. Neither
provides a uniform improvement over the conservative fixed-low baseline across
all metrics. This is evidence about the measured schedule effects, not proof
of a causal architecture mechanism and not a CAI winner selection.

## LaTeX table

```latex
\begin{table}[t]
\centering
\caption{Matched-range Exact MV-Adapter follow-up on 76 holdout objects.}
\begin{tabular}{lrrrrrr}
\toprule
Schedule & PSNR$\uparrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ & FG-LPIPS$\downarrow$ & $\Delta E_{00}\downarrow$ & GT-texture$\downarrow$\\
\midrule
Linear warmup (0.75--1.00) & 13.332426 & 0.528047 & 0.240094 & 0.188445 & 20.194007 & 2.182502\\
Cosine bump (0.75--1.00) & 13.327002 & 0.527812 & 0.239955 & 0.188232 & 20.211197 & 2.215665\\
\bottomrule
\end{tabular}
\end{table}
```
