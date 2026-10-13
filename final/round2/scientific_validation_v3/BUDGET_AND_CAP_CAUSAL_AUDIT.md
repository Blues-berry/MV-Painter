# BUDGET_AND_CAP_CAUSAL_AUDIT — corrected contrast accounting

Date: 2026-10-05. Cohort: FRESH_CONFIRM_300 (n=300). Raw sources:
`formal/campaign_B1B2/` and `formal/campaign_B3/` manifests, ledgers, per-object
metrics, residual logs, and `formal/campaign_B3/residual_budget_audit.json`.
The B3 residual audit was recomputed from raw logs after correcting how
uncapped conditions are classified.

## Scale, cap, integrated dose, and performance

`E` is the per-object integrated residual norm by layer
`sqrt(sum_t(sum_wrappers(l2^2)))`, averaged over objects. Scores are object
means. FG-PSNR is higher-is-better; FG-LPIPS is lower-is-better. Scale triples
are deep/middle/shallow. For stage schedules, requested entries are reported
as low/high values and the listed mean is duration-weighted.

| Condition | Requested scale D/M/S | Applied scale D/M/S | Cap activation D/M/S | Mean E D/M/S | Mean FG-PSNR / FG-LPIPS |
|---|---|---|---|---|---|
| Native GFL | 1.25 / 1.25 / 1.25 | 1.25 / 1.25 / 0.80 | 0 / 0 / 100% | 3.149e8 / 1.613e7 / 1.343e6 | 10.931 / 0.20209 |
| Native GFH | 2.50 / 2.50 / 2.50 | 2.50 / 2.50 / 0.80 | 0 / 0 / 100% | 1.259e9 / 5.083e7 / 1.356e6 | 12.306 / 0.18710 |
| Native GC3 | 1.25→2.50 / 1.25→2.50 / 1.25→2.50 (mean 1.65 each) | same D/M; 0.80 at every shallow step | 0 / 0 / 100% | 6.956e8 / 3.671e7 / 1.318e6 | 11.456 / 0.19652 |
| LFM-EXACT | 1.675 / 1.675 / 0.585 | same | 0 / 0 / 0 | 5.681e8 / 2.656e7 / 7.387e5 | 11.784 / 0.19011 |
| LLH | 1.25→2.50 / 1.25→2.50 / 0.50→0.75 (mean 1.675 / 1.675 / 0.585) | same | 0 / 0 / 0 | 6.424e8 / 2.924e7 / 8.808e5 | 12.219 / 0.18559 |
| TGU-1.25 | 1.25 / 1.25 / 1.25 | same; native cap bypassed | 0 / 0 / 0 | 3.124e8 / 1.582e7 / 3.156e6 | 9.328 / 0.20657 |
| TGU-1.675 | 1.675 / 1.675 / 1.675 | same; native cap bypassed | 0 / 0 / 0 | 5.583e8 / 2.572e7 / 5.683e6 | 8.790 / 0.20310 |
| TGU-2.50 | 2.50 / 2.50 / 2.50 | same; native cap bypassed | 0 / 0 / 0 | 1.238e9 / 5.021e7 / 1.293e7 | 7.648 / 0.20400 |
| TGU-0.80 | **not run** | — | — | — | — |

The native cap limits shallow scales to 0.80. In GC3 it therefore flattens the
shallow schedule to 0.80 for all 50 steps; deep and middle retain the
low–high–low schedule. TGU conditions use the uncapped forward path, so their
actual applied scale equals the requested scale.

### Residual-log correction

`geotex.explore_contradiction` writes `eff_scale=min(requested, cap)` into the
log even when `scripts/run_validation_v3_experiment.py` has swapped in
`uncapped_forward`, which multiplies the correction by the requested scale
without applying the cap. Thus `eff_scale` in TGU logs is hypothetical; the
logged correction `l2` is the actual uncapped correction. The manifest's
`uncapped` flag and the forward implementation are authoritative. The updated
`analyze_residual_budgets.py` now reads that flag and reports actual effective
scales and cap rates accordingly. No generated row or residual norm changed.

## Contrast table: what each comparison identifies

| Contrast (A−B) | Effect on FG-PSNR (95% CI; win rate) | Depth allocation changes? | Temporal allocation changes? | Residual dose changes? | Cap semantics/profile changes? | Allowed interpretation |
|---|---|---:|---:|---:|---:|---|
| LLH − GFL | +1.288 dB [0.938, 1.635]; 57.7% | Yes | Yes | Yes | Yes: GFL shallow capped, LLH not | Combined allocation effect only |
| LLH − LFM-EXACT | +0.435 dB [0.356, 0.516]; 68.7% | No | Yes | Realized residual norms differ; nominal per-layer means match | No cap activates in either | Clean temporal-variation contrast at matched per-layer requested means |
| LLH − HLL | +0.854 dB [0.658, 1.052]; 58.0% | No | Yes, position only | Integrated outputs differ as a consequence of position | No | Clean early-versus-late placement contrast; equal 17-step high duration |
| LFM-EXACT − GFL | +0.853 dB [0.568, 1.144]; 57.0%* | Yes | No | Yes | Yes: GFL shallow cap active | Combined layer-dose/cap contrast, not isolated redistribution |
| GFL − TGU-1.25 | +1.603 dB [1.369, 1.830]; 78.7% | No in requested scales | No | Yes, shallow actual dose differs | Yes: cap bypass vs native | Effect of native shallow cap at fixed requested global 1.25 |
| LFM-EXACT − TGU-1.675 | +2.994 dB [2.425, 3.550]; 69.7% | Shallow dose only; D/M requests match | No | Yes | TGU bypasses cap; LFM does not reach it | Effect of reducing shallow exposure while deep/middle requested scales match; not equal-total-dose redistribution |
| LLH − TGU-1.675 | +3.429 dB [2.805, 4.044]; 69.3% | Yes | Yes | Yes | Yes | Descriptive multi-factor contrast only |
| GFH − TGU-2.50 | +4.659 dB [4.07, 5.23]** | No in requested scales | No | Yes, shallow actual dose differs | Yes: cap bypass vs native | Effect of native shallow cap at fixed requested global 2.50 |

\* LFM-EXACT−GFL is a post-hoc paired decomposition contrast (10,000 object
bootstrap resamples, seed 20261007); it is descriptive and was not included in
a registered confirmatory family. The same-object identity
`LLH−GFL = (LLH−LFM-EXACT) + (LFM-EXACT−GFL)` holds numerically. It does not
mean the second component is a pure depth-allocation effect: its scales,
realized dose, and shallow cap state differ.

\** Existing paired result in `pairwise_layer_llh_vs_true_global_2p50.json`
and the decision report; this is a diagnostic contrast, not a deployment
comparison.

## Corrections to prior interpretation

The previously stated “cap (+1.6) + layer redistribution (+3.0) + temporal
(+0.4) explains the total” was not a valid decomposition of LLH−GFL. Those
terms use different comparator scales and endpoints; their sum (~+5.0 dB)
does not equal the observed LLH−GFL effect (+1.288 dB). The same-endpoint
decomposition above shows a small clean temporal component (+0.435 dB) and a
remaining +0.853 dB combined layer-dose/cap-profile contrast. No additive
causal decomposition of the headline is supported by these controls.

The explicit protocol family also requested TGU-0.80. B3 contains only
TGU-1.25, TGU-1.675, and TGU-2.50, so the causal diagnostic family is
incomplete. TGU-0.80 must be frozen and run on FRESH_CONFIRM_B before the cap /
uniform-scale comparison is described as complete. Until then, use only the
named contrasts above and do not claim a complete cap/budget decomposition.
