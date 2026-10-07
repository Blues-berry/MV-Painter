# Final cap/budget causal accounting — FRESH_CONFIRM_B

The 4,500-row B campaign passed its integrity gate. All conditions below share the same objects, checkpoint, runner, inputs, seed policy, views, and metric implementation. Paired effects are condition A minus condition B, with 10,000 object bootstrap resamples (seed 20261002). FG-PSNR is higher-is-better; FG-LPIPS is lower-is-better. The frozen Holm family contains seven comparisons per endpoint.

## Requested/applied scales, cap semantics, realized correction dose, and scores

Requested/applied values are 50-step scale integrals in deep/middle/shallow order. `E` is the mean per-object root-sum-square of actual post-scale wrapper corrections over all 50 steps, by layer. For TGU, the manifest's uncapped flag is authoritative: requested scale is actually applied even though logged `eff_scale` is hypothetical.

| Condition | Forward path | Requested scale integral D/M/S | Applied scale integral D/M/S | Cap activation D/M/S | Mean E D/M/S | Mean FG-PSNR | Mean FG-LPIPS |
|---|---|---:|---:|---:|---:|---:|---:|
| `native_gfl` | native capped | 62.50/62.50/62.50 | 62.50/62.50/40.00 | 0/0/100% | 316813209.958/16304030.244/1343655.216 | 10.848 | 0.19676 |
| `native_gfh` | native capped | 125.00/125.00/125.00 | 125.00/125.00/40.00 | 0/0/100% | 1266092224.602/51178826.680/1352717.162 | 12.103 | 0.18337 |
| `native_gc3` | native capped | 82.50/82.50/82.50 | 82.50/82.50/40.00 | 0/0/100% | 698881925.517/36931254.790/1317232.327 | 11.349 | 0.19163 |
| `true_global_0p80` | uncapped diagnostic | 40.00/40.00/40.00 | 40.00/40.00/40.00 | 0/0/0% | 128290308.026/7371512.707/1360370.932 | 9.346 | 0.21029 |
| `true_global_1p25` | uncapped diagnostic | 62.50/62.50/62.50 | 62.50/62.50/62.50 | 0/0/0% | 314242613.141/15996707.748/3159555.257 | 9.331 | 0.20168 |
| `true_global_1p675` | uncapped diagnostic | 83.75/83.75/83.75 | 83.75/83.75/83.75 | 0/0/0% | 561663016.587/25980882.124/5684032.884 | 8.842 | 0.19852 |
| `true_global_2p50` | uncapped diagnostic | 125.00/125.00/125.00 | 125.00/125.00/125.00 | 0/0/0% | 1245722654.795/50618681.438/12910693.691 | 7.768 | 0.19932 |
| `lfm_exact` | native capped | 83.75/83.75/29.25 | 83.75/83.75/29.25 | 0/0/0% | 571409117.621/26794937.005/737622.735 | 11.553 | 0.18581 |
| `layer_llh` | native capped | 83.75/83.75/29.25 | 83.75/83.75/29.25 | 0/0/0% | 645875001.673/29509041.492/879658.181 | 11.878 | 0.18120 |
| `layer_hll` | native capped | 83.75/83.75/29.25 | 83.75/83.75/29.25 | 0/0/0% | 948969107.672/30844938.662/683331.029 | 11.191 | 0.19218 |

## Frozen contrast semantics

| Contrast | Same per-layer requested mean? | Same high duration/position? | Same cap path and activation rate? | Same actual dose? | Same runner? | Allowed causal statement |
|---|---|---|---|---|---|---|
| LLH − GFL | No | No; staged vs constant | No | No; logged E differs | Yes | Combined allocation/budget/cap-profile effect only. |
| LLH − LFM-EXACT | Yes | No; variable vs constant | Yes | No; logged E differs | Yes | Temporal redistribution at matched per-layer requested means; not post-scale dose equality. |
| LLH − HLL | Yes | Same 17-step high duration; position differs | Yes | No; logged E differs | Yes | Early-versus-late position effect at equal 17-step high duration. |
| GFL − TGU-1.25 | Yes | Same constant requested trace | No | No; logged E differs | Yes | Native shallow-cap effect at a fixed requested global scale. |
| LFM-EXACT − TGU-1.675 | No | Both constant over time | No | No; logged E differs | Yes | Combined shallow-exposure/cap-path difference; not pure depth redistribution. |
| TGU-1.25 − TGU-0.80 | No | Both constant over time | Yes | No; logged E differs | Yes | Uniform requested-dose effect on the uncapped diagnostic path. |
| LLH − TGU-1.675 | No | No; staged vs constant | No | No; logged E differs | Yes | Descriptive multi-factor contrast only. |

## Paired performance effects

Adjusted p-values are upper bounds where a raw bootstrap result hit the 1/10,000 resolution floor.

| Contrast | FG-PSNR Δ dB [95% CI] | Favorable objects | Holm p | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| LLH − GFL | +1.030 [+0.570, +1.496] | 51.3% | ≤0.0007 | -0.01556 [-0.01914, -0.01192] | 74.0% | ≤0.0007 |
| LLH − LFM-EXACT | +0.325 [+0.209, +0.446] | 54.0% | ≤0.0007 | -0.00460 [-0.00563, -0.00357] | 76.0% | ≤0.0007 |
| LLH − HLL | +0.687 [+0.404, +0.981] | 45.3% | ≤0.0007 | -0.01098 [-0.01349, -0.00851] | 80.7% | ≤0.0007 |
| GFL − TGU-1.25 | +1.516 [+1.176, +1.842] | 78.0% | ≤0.0007 | -0.00492 [-0.00707, -0.00271] | 67.3% | ≤0.0007 |
| LFM-EXACT − TGU-1.675 | +2.711 [+1.911, +3.491] | 72.0% | ≤0.0007 | -0.01272 [-0.01770, -0.00767] | 64.0% | ≤0.0007 |
| TGU-1.25 − TGU-0.80 | -0.015 [-0.202, +0.181] | 42.0% | 0.8808 | -0.00862 [-0.01113, -0.00620] | 75.3% | ≤0.0007 |
| LLH − TGU-1.675 | +3.036 [+2.158, +3.893] | 70.7% | ≤0.0007 | -0.01732 [-0.02300, -0.01163] | 65.3% | ≤0.0007 |

## Endpoint-connected decomposition

The required identity holds exactly for all 150 object-level pairs on both endpoints:

`LLH − GFL = (LLH − LFM-EXACT) + (LFM-EXACT − GFL)`

| Endpoint | LLH−GFL mean | LLH−LFM-EXACT mean (temporal redistribution) | LFM-EXACT−GFL mean (combined layer/cap/budget) | Max object-level identity residual |
|---|---:|---:|---:|---:|
| FG-PSNR (dB) | +1.030130 | +0.325165 | +0.704965 | 0.0e+00 |
| FG-LPIPS | -0.015557 | -0.004604 | -0.010953 | 0.0e+00 |

The `LFM-EXACT − GFL` term is the combined change in depth allocation, shallow exposure, realized dose, and native cap state; it is not a pure depth-allocation effect. Its mean is shown only as the algebraic remainder required by the same-endpoint identity; it is not added as an eighth test to the frozen Holm families. No decomposition is formed by summing effects from different endpoints.

## Interpretation

- LLH exceeds LFM-EXACT on FG-PSNR by +0.325 dB after Holm correction, with a matched requested per-layer mean schedule; this supports a temporal-redistribution effect under the same nominal layer means, while actual correction norms differ.
- Native GFL exceeds true-uniform TGU-1.25 on both endpoints. At requested 1.25, native GFL clips the shallow layer to 0.80, while TGU-1.25 bypasses that cap and applies 1.25. This identifies the effect of that shallow-cap path in this run.
- TGU-1.25 versus TGU-0.80 shows no detectable FG-PSNR difference (95% CI includes zero) but lower FG-LPIPS at 1.25. No equivalence margin was frozen, so the PSNR result is not an equivalence claim.
- TGU conditions are causal diagnostics, not deployment baselines. LLH−GFL and LLH−TGU-1.675 remain combined contrasts; no further split of the layer/cap/budget component is identified.

## Provenance

- Frozen contrast definitions: `CAP_BUDGET_DIAGNOSTIC_PROTOCOL_LOCK.md`.
- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).
- Paired contrasts and Holm family: `formal/campaign_FRESH_CONFIRM_B_20261005/paired_*.json` and `CAP_BUDGET_HOLM_FAMILY.json`.
- Actual post-scale dose: `formal/campaign_FRESH_CONFIRM_B_20261005/residual_budget_audit.json` and raw residual logs.
- Source metric rows: `formal/campaign_FRESH_CONFIRM_B_20261005/per_object_metrics.csv`.
