# MV-Adapter Equal-Mean-Budget Mechanism Results

This is a targeted follow-up analysis on the already-used 76-object Exact
holdout. It was protocolized before the new inference and does not claim to be
the original confirmatory freeze.

## Conditions

All schedules have mean scale `5/6 = 0.8333333333333334` over three equal
stages:

| Condition | Early | Middle | Late |
|---|---:|---:|---:|
| Fixed mean | 5/6 | 5/6 | 5/6 |
| HLL | 1.00 | 0.75 | 0.75 |
| LHL | 0.75 | 1.00 | 0.75 |
| LLH | 0.75 | 0.75 | 1.00 |

Protocol: `results/holdout_exact_equal_budget_76/PROTOCOL.json`  
New runner CSV: `results/holdout_exact_equal_budget_76/per_object_metrics.csv`  
Combined four-condition CSV:
`results/holdout_exact_equal_budget_76/equal_budget_per_object_metrics.csv`

The LHL rows are the completed pre-existing Exact LHL diagnostic and were
reused without rerunning.

## Object-level means

| Condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | ΔE00 | GT-relative texture error |
|---|---:|---:|---:|---:|---:|---:|
| Fixed mean | 13.337215 | 0.527776 | 0.240051 | 0.188163 | 20.196643 | 2.202812 |
| HLL | 13.320944 | 0.526805 | 0.239621 | 0.188194 | 20.243426 | 2.232062 |
| LHL | 13.344064 | 0.528325 | 0.240235 | 0.188051 | 20.182146 | 2.269096 |
| LLH | 13.353306 | 0.527814 | 0.239974 | 0.188346 | 20.157122 | 2.198930 |

## Paired bootstrap and mechanism-level reading

Bootstrap output:

`results/holdout_exact_equal_budget_76/equal_budget_bootstrap.json`

All pairwise comparisons use 10,000 object-level resamples, seed `20260928`,
95% CIs. The complete JSON also reports each condition against conservative
`fixed_low`.

The most relevant paired mean deltas are:

| Comparison | ΔPSNR | ΔFG-SSIM | ΔEdge-SSIM | ΔFG-LPIPS* | ΔΔE00* | ΔGT-texture* |
|---|---:|---:|---:|---:|---:|---:|
| Fixed mean − HLL | 0.016271 | 0.000971 | 0.000429 | 0.000030 | 0.046783 | 0.029249 |
| Fixed mean − LHL | −0.006849 | −0.000549 | −0.000184 | −0.000113 | −0.014497 | 0.066284 |
| Fixed mean − LLH | −0.016090 | −0.000038 | 0.000077 | 0.000183 | −0.039521 | −0.003882 |
| HLL − LHL | −0.023119 | −0.001520 | −0.000613 | −0.000143 | −0.061280 | 0.037034 |
| HLL − LLH | −0.032361 | −0.001009 | −0.000353 | 0.000153 | −0.086304 | −0.033132 |
| LHL − LLH | −0.009242 | 0.000511 | 0.000261 | 0.000296 | −0.025024 | −0.070166 |

*Error columns are direction-adjusted so positive favors the left condition.

The data show measurable schedule-position differences, but not a uniformly
dominant placement across structure, perceptual error and texture error. In
particular, this analysis confirms that an undefined CAI choice does **not**
mean that all stage schedules are statistically identical; it means only that
the frozen rule did not define a legal unique selection.

## Cross-backbone boundary

The main-adapter repository contains a separate stage-placement protocol and
some C3-vs-fixed-low/high bootstrap results, but its equal-mean/HLL/LLH formal
inference is still marked pending in `final/round2/STAGE_PLACEMENT_RESULTS.md`.
Its existing C3 comparisons also use a different scale protocol. Therefore:

- no absolute PSNR comparison between MVPainter and MV-Adapter is made;
- no cross-backbone direction claim is made yet;
- no causal claim is made about residual injection location, amplitude or
  architecture;
- the present equal-budget results establish only the MV-Adapter-side
  mechanism diagnostic.

Once the main-adapter equal-budget experiment exists under a matched protocol,
the valid comparison is the sign and CI of relative contrasts: fixed mean vs
stage schedules, HLL vs LHL, LHL vs LLH, dynamic vs conservative fixed scale,
and whether a shape/texture trade-off appears in both backbones.

## LaTeX table

```latex
\begin{table}[t]
\centering
\caption{Equal-mean-scale temporal placement follow-up on the Exact MV-Adapter holdout.}
\begin{tabular}{lrrrrrr}
\toprule
Condition & PSNR$\uparrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ & FG-LPIPS$\downarrow$ & $\Delta E_{00}\downarrow$ & GT-texture$\downarrow$\\
\midrule
Fixed mean & 13.337215 & 0.527776 & 0.240051 & 0.188163 & 20.196643 & 2.202812\\
HLL & 13.320944 & 0.526805 & 0.239621 & 0.188194 & 20.243426 & 2.232062\\
LHL & 13.344064 & 0.528325 & 0.240235 & 0.188051 & 20.182146 & 2.269096\\
LLH & 13.353306 & 0.527814 & 0.239974 & 0.188346 & 20.157122 & 2.198930\\
\bottomrule
\end{tabular}
\end{table}
```
