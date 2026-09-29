# Full-SSIM reconciliation

Status: completed from the frozen 300-object PNG/eval artifacts; no model inference or metric compensation was performed.

## A/B/C definitions

- A: recorded `original_float_ssim` from the original per-object float-eval CSV.
- B: `png_original_impl_ssim`, reloaded PNG prediction and saved GT using the original consolidated 3x3 implementation.
- C: `raw_audit_ssim`, reloaded PNG prediction against independently reconstructed raw RGBA/white-background GT using the current raw audit implementation.

The CSV contains all per-object values, per-view diagnostics, Gaussian-window diagnostics, and A/B/C deltas.

## Overall Full-SSIM values

| representation | no adapter | fixed low | fixed high | C3 |
|---|---:|---:|---:|---:|
| A original float | 0.727334 | 0.850439 | 0.822611 | 0.855002 |
| B PNG/original impl | 0.764174 | 0.882058 | 0.857681 | 0.881467 |
| C PNG/raw GT audit | 0.764067 | 0.881914 | 0.857469 | 0.881327 |

## Fixed 12-object reconciliation subset

The fixed subset is the frozen Exact-GLB cohort at object indices `13,15,38,48,54,66,68,78,82,83,110,111`; it is a diagnostic subset and was not selected for SSIM performance.

| representation | no adapter | fixed low | fixed high | C3 |
|---|---:|---:|---:|---:|
| A original float | 0.751344 | 0.867758 | 0.821831 | 0.868465 |
| B PNG/original impl | 0.790606 | 0.895336 | 0.857722 | 0.891905 |
| C PNG/raw GT audit | 0.790599 | 0.895304 | 0.857633 | 0.891871 |

| representation | comparison | mean C3-minus-baseline | 95% CI | win rate |
|---|---|---:|---|---:|
| A | c3_vs_fixed_low | 0.000708 | [-0.002502, 0.003429] | 0.667 |
| A | c3_vs_fixed_high | 0.046634 | [0.028389, 0.065469] | 0.917 |
| B | c3_vs_fixed_low | -0.003430 | [-0.005781, -0.001341] | 0.250 |
| B | c3_vs_fixed_high | 0.034184 | [0.021557, 0.047628] | 1.000 |
| C | c3_vs_fixed_low | -0.003432 | [-0.005783, -0.001339] | 0.250 |
| C | c3_vs_fixed_high | 0.034238 | [0.021599, 0.047695] | 1.000 |

## A/B/C error distributions

| delta | method | mean | mean abs | p05 | median | p95 | max abs | over threshold |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| B-A | no_adapter | 0.036840 | 0.036840 | 0.027864 | 0.037351 | 0.044320 | 0.048658 | 300/300 |
| B-A | fixed_low | 0.031620 | 0.031630 | -0.000008 | 0.038891 | 0.056807 | 0.061872 | 232/300 |
| B-A | fixed_high | 0.035070 | 0.035073 | 0.000185 | 0.042539 | 0.051134 | 0.054642 | 252/300 |
| B-A | c3 | 0.026465 | 0.026482 | -0.000087 | 0.033263 | 0.050003 | 0.057258 | 206/300 |
| C-B | no_adapter | -0.000107 | 0.000123 | -0.000320 | -0.000090 | 0.000066 | 0.000658 | 0/300 |
| C-B | fixed_low | -0.000145 | 0.000150 | -0.000326 | -0.000129 | 0.000024 | 0.000788 | 0/300 |
| C-B | fixed_high | -0.000212 | 0.000212 | -0.000467 | -0.000185 | -0.000031 | 0.001011 | 1/300 |
| C-B | c3 | -0.000140 | 0.000145 | -0.000339 | -0.000127 | 0.000022 | 0.000745 | 0/300 |
| C-A | no_adapter | 0.036733 | 0.036733 | 0.027748 | 0.037329 | 0.044227 | 0.048559 | 300/300 |
| C-A | fixed_low | 0.031475 | 0.031504 | -0.000113 | 0.038759 | 0.056667 | 0.061670 | 232/300 |
| C-A | fixed_high | 0.034858 | 0.034872 | -0.000026 | 0.042316 | 0.051010 | 0.054336 | 252/300 |
| C-A | c3 | 0.026325 | 0.026371 | -0.000185 | 0.033156 | 0.049931 | 0.057091 | 206/300 |

## Paired C3 differences

Positive values mean C3 has higher Full-SSIM. Bootstrap is object-level, 10,000 resamples, seed 20260928.

| representation | comparison | mean C3-minus-baseline | 95% CI | win rate |
|---|---|---:|---|---:|
| A | c3_vs_fixed_low | 0.004563 | [0.003909, 0.005210] | 0.820 |
| A | c3_vs_fixed_high | 0.032391 | [0.029603, 0.035301] | 0.947 |
| B | c3_vs_fixed_low | -0.000592 | [-0.000988, -0.000194] | 0.463 |
| B | c3_vs_fixed_high | 0.023786 | [0.021718, 0.025936] | 0.990 |
| C | c3_vs_fixed_low | -0.000587 | [-0.000984, -0.000188] | 0.463 |
| C | c3_vs_fixed_high | 0.023858 | [0.021792, 0.026008] | 0.990 |

## Reconciliation conclusion

B and C isolate the PNG/GT preprocessing branch from the SSIM implementation branch. The primary implementation uses a 3x3 box window, padding=1, no Gaussian weighting, C1=0.01^2, C2=0.03^2, [0,1] inputs, map clamp [0,1], and the complete 3x2 montage. Per-view means and an 11x11 Gaussian diagnostic are reported but are not substituted into the primary result.

If B is close to C while A differs, the remaining discrepancy is between the recorded pre-save float tensors and the reloaded 8-bit PNG panels (including float precision/quantization), not a fitted correction. If B and C differ, the difference is confined to GT reconstruction/preprocessing and is retained as an audit finding.

Full-SSIM should not be delivered to Codex C as a unified number until the chosen provenance is stated explicitly. No compensation value is applied.
