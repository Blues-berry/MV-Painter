# Exact-budget temporal causal report

Cohort: FRESH_CONFIRM_300, n=300 unique objects. LLH, LFM-EXACT, LLL, HLL, LHL, and LHH were defined in the preregistered B1/B2 campaign before FRESH_CONFIRM_300 outcomes. Runner, checkpoint, paired inputs, seeds, views, and native cap semantics are shared within the campaign. Object is the inference unit; paired bootstrap uses 10,000 resamples and seed 20261002.

## Time-varying versus constant at the same per-layer mean

LFM-EXACT requests constant scales 1.675 / 1.675 / 0.585 for deep/middle/shallow. LLH has the same duration-weighted mean by layer (17/16/17 high/low segmentation), with no cap activation in either condition.

| Contrast | Metric | Mean paired delta (A−B) | 95% CI | Win rate | Holm p (B1 family) |
|---|---|---:|---:|---:|---:|
| LLH − LFM-EXACT | FG-PSNR | +0.434 | [+0.356, +0.516] | 68.7% | 0.0002 |
| LLH − LFM-EXACT | FG-LPIPS | -0.00452 | [-0.00519, -0.00387] | 77.0% | 0.0002 |

The predeclared equivalence rule required both 95% CIs to lie inside ±0.5 dB FG-PSNR and ±0.01 FG-LPIPS. LPIPS meets its margin; PSNR upper CI exceeds +0.5 dB, so the combined equivalence criterion is not met. Evidence supports a small real time-varying advantage over the exact layer-mean constant, not a claim that all of LLH's gain is temporal.

## Early versus late placement

The preregistered B2 family contains LLH−HLL and LLH−LLL on FG-PSNR and FG-LPIPS (four tests, Holm corrected together). LLH and HLL both have one 17-step high segment; LLH−HLL changes its position. LLL is the all-low control.

| Contrast | Metric | Mean paired delta (A−B) | 95% CI | Win rate | Holm p (four-test B2 family) |
|---|---|---:|---:|---:|---:|
| LLH − HLL | FG-PSNR | +0.853 | [+0.658, +1.052] | 58.0% | 0.0004 |
| LLH − HLL | FG-LPIPS | -0.01161 | [-0.01307, -0.01020] | 80.0% | 0.0004 |
| LLH − LLL | FG-PSNR | +0.840 | [+0.747, +0.934] | 81.3% | 0.0004 |
| LLH − LLL | FG-LPIPS | -0.00974 | [-0.01081, -0.00870] | 86.3% | 0.0004 |

Both preregistered contrasts favor LLH on both metrics after Holm correction. This supports late placement under the tested 17-step profile. It does not establish a universal late-phase optimum or a discontinuity at the one-third boundary.

### HLL versus LLL (unregistered derived contrast)

This extra paired contrast was calculated to complete the decision protocol's requested comparison set, but HLL−LLL was not part of the original B2 four-test confirmatory family. It is therefore descriptive/exploratory and receives no confirmatory label: FG-PSNR -0.013 dB, 95% CI [-0.128, +0.098], bootstrap p=0.824; FG-LPIPS +0.00187, 95% CI [+0.00120, +0.00256], p=0.0001. The FG-PSNR result is near zero; LPIPS favors LLL on 56.3% of paired objects.

LHL and LHH remain available as middle/late context schedules; they were not added to the primary B2 family after outcomes were seen. The named tests distinguish: (1) temporal variation at fixed layer means (LLH−LFM-EXACT), (2) late versus early location (LLH−HLL), and (3) late schedule versus no high pulse (LLH−LLL). They do not collapse into a single claim that “time-varying helps.”
