# A3b classification under the mid-run safeguard addendum

**Classification: `PARTIAL`.** The frozen bounded map has a reproducible,
statistically resolved Layer × Window term, including after linear and log
actual-dose adjustment. The three layer dose ranges have no common support,
however, and the development calibration materially missed its target.
Dose-independent non-additivity is therefore not identified.

## Four required checks

1. **Raw bounded-map interaction.** The object-cluster Wald test is W=225.015
   (8 df; raw p=3.35e−44; Holm p=5.37e−43) for FG-LPIPS and W=525.700
   (raw p=2.15e−108; Holm p=3.43e−107) for FG-PSNR. The cross-check GEE
   gives W=226.717 (p=1.46e−44) and W=529.230 (p=3.75e−109).
2. **Actual-dose-adjusted repeated measures.** With object fixed effects and
   object-cluster robust covariance, the interaction remains detectable under
   both frozen sensitivity forms. Linear-dose W=207.766 for FG-LPIPS and
   426.696 for FG-PSNR; log-dose W=174.492 and 506.439. These are conditional
   associations on post-treatment dose, not controlled-dose causal effects.
3. **Common dose support.** The active-dose central-90% intervals are
   deep 56,359–79,927, middle 11,421–19,336, and shallow 2,817–5,193. Their
   three-way intersection is empty: **0/2,250 rows** support a joint
   three-layer interaction estimate.
4. **Magnitude.** The raw interaction RMSE is 0.000342 FG-LPIPS and 0.0205 dB
   FG-PSNR, accounting for 14.0% and 36.0% of variation among the 15 cell
   means. Linear/log dose-adjusted RMSEs are 0.000499/0.000341 and
   0.0463/0.0402 dB, respectively.

## Practical scale reference

The per-cell realization-drift reference is from the prior 24-object,
development-only repeated-seed probe; it is not a standard error for these
150-object mean contrasts or a threshold. Relative to its median and P95
absolute drift:

| Interaction magnitude | FG-LPIPS / median | FG-LPIPS / P95 | FG-PSNR / median | FG-PSNR / P95 |
|---|---:|---:|---:|---:|
| Raw interaction RMSE | 0.0128 | 0.0030 | 0.0066 | 0.0021 |
| Linear-dose RMSE | 0.0186 | 0.0044 | 0.0150 | 0.0048 |
| Log-dose RMSE | 0.0127 | 0.0030 | 0.0130 | 0.0042 |

These ratios only compare the scale of an interaction RMSE to per-cell,
single-realization drift. They do not invalidate the population-level tests,
but they show that the fitted cell interaction magnitudes are small relative
to that per-cell noise reference. The large Wald statistics must not be used
as a practical-size argument.

## Locked wording boundary

The permitted claim is that this frozen, bounded intervention map showed
Layer × Window heterogeneity on FRESH_CONFIRM_B. Its dose balance failed
(deep −20.01%, middle −20.20%, shallow +98.98% versus the target), and actual
three-layer common support is absent. Label the result **PARTIAL** and do not
call it equal-dose, dose-normalized, dose-independent, or a validated
non-separable control law. Do not tune a replacement map on B.

Provenance: `A3B_BOUNDED_LAYER_TIME_REPORT.md`,
`RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.md`,
`A3B_DOSE_FEASIBILITY_AUDIT.md`, and the corresponding frozen B artifacts.
This addendum classification was written after B had already been exposed;
it is not a pre-unblind lock.
