# Practical-effect reference from pre-existing realization robustness

**Status: `RETROSPECTIVE_REFERENCE — CREATED AFTER PRIOR B OUTCOME EXPOSURE`;
not a valid pre-unblind lock.** No B rows were used to calculate this drift
reference. It is derived only from the previously generated repeated-seed
robustness data named below.

## Method

The development-only layer-factorial probe contains the same 24 objects, 8
fixed schedules, and three previously generated realization seeds (42, 43,
44). For each object × schedule cell, I formed all three pairwise absolute
seed differences, pooling 192 cells × 3 pairs = 576 differences per metric.
P95 is the empirical nearest-rank quantile, rank `ceil(0.95 n)`.

| Metric | Pairwise drifts | Median absolute drift | 95th percentile absolute drift | Mean absolute drift | Max absolute drift |
|---|---:|---:|---:|---:|---:|
| FG-PSNR (dB) | 576 | 3.094010 | 9.548559 | 3.695648 | 12.799191 |
| FG-LPIPS | 576 | 0.026770 | 0.112665 | 0.038258 | 0.175546 |
| Full-PSNR (dB) | 576 | 3.825664 | 12.914941 | 4.782108 | 15.424849 |
| Full-LPIPS | 576 | 0.037444 | 0.139041 | 0.050323 | 0.258623 |

## Interpretation limits

These are per-object, same-condition realization drifts from a 24-object
development-only probe, not standard errors for the 150-object B mean and not
acceptance thresholds. They provide a scale reference only. Do not call a
statistically significant population mean “large” based on its p-value; report
its absolute effect, CI, and effect/drift ratios against both the median and
P95 above. Ratios below one mean the per-object effect is smaller than a
typical single-cell realization drift; they do not invalidate a paired
population-level estimate.

No arbitrary practical cutoff is introduced here. H2's frozen ±0.5 dB and
±0.01 margins retain only their original registered interpretation.

## Retrospective effect-to-drift comparisons

These ratios place already-reported effects next to the single-cell
realization distribution. They do not test equivalence, replace paired
confidence intervals, or estimate the standard error of a cohort mean.

| Contrast | Endpoint | Mean effect [95% CI] | Absolute effect / median drift | Absolute effect / P95 drift |
|---|---|---:|---:|---:|
| A2 middle-W5 cell vs baseline | FG-LPIPS | −0.006405 [−0.007075, −0.005732] | 0.239 | 0.0568 |
| A2 shallow-W5 cell vs baseline | FG-LPIPS | +0.000358 [+0.000085, +0.000633] | 0.0134 | 0.0032 |
| A2 middle-W5 cell vs baseline | FG-PSNR | +0.5145 [+0.4610, +0.5695] dB | 0.166 | 0.0539 |
| B LLH − LFM-EXACT | FG-PSNR | +0.325 [+0.209, +0.446] dB | 0.105 | 0.0340 |
| B LLH − LFM-EXACT | FG-LPIPS | −0.00460 [−0.00563, −0.00357] | 0.172 | 0.0408 |
| B LLH − HLL | FG-PSNR | +0.687 [+0.404, +0.981] dB | 0.222 | 0.0719 |
| B LLH − HLL | FG-LPIPS | −0.01098 [−0.01349, −0.00851] | 0.410 | 0.0975 |
| B LLH − LLL | FG-PSNR | +0.734 [+0.597, +0.875] dB | 0.237 | 0.0769 |
| B LLH − LLL | FG-LPIPS | −0.00845 [−0.01029, −0.00659] | 0.316 | 0.0750 |
| B exploratory HLL − LLL | FG-PSNR | +0.047 [−0.120, +0.208] dB | 0.0152 | 0.0049 |
| B exploratory HLL − LLL | FG-LPIPS | +0.00253 [+0.00155, +0.00354] | 0.0945 | 0.0225 |
| C registered LLH − `gen_linear` | FG-PSNR | +0.0049 [−0.0350, +0.0469] dB | 0.0016 | 0.0005 |
| C registered LLH − `gen_linear` | FG-LPIPS | +0.00123 [+0.00069, +0.00182] | 0.0458 | 0.0109 |
| B post-lock LLH − `gen_linear` | FG-PSNR | −0.0373 [−0.0829, +0.0086] dB | 0.0121 | 0.0039 |
| B post-lock LLH − `gen_linear` | FG-LPIPS | +0.0011 [+0.0004, +0.0019] | 0.0411 | 0.0098 |

The A2 FG-LPIPS cell means span about 0.013–0.239 of the median per-cell
seed drift (0.003–0.057 of P95); the displayed middle-W5 FG-PSNR effect is
0.166 of the median drift (0.054 of P95). Their Holm-adjusted population
tests can be significant at N=300 while the cell means remain small relative
to typical single-object realization changes. For B, the registered
LLH−LFM-EXACT FG-PSNR difference is 0.105 of the median drift and remains
inside its preregistered practical margin. LLH−HLL and LLH−LLL means are
larger relative to the drift reference but still below one quarter of the
median FG-PSNR drift; the contrast-specific LPIPS ratios are higher. The
registered and post-lock `gen_linear` FG-PSNR estimates are close to zero on
this scale.

These are contextual scale comparisons across a development reference and
later cohorts, not confirmatory standardized effects. Keep cohort-level
confidence intervals and the frozen margins as the inferential basis. The
ratio values above were computed after B outcome exposure and cannot be
described as pre-unblind safeguards.

## Provenance

Source: `final/round2/coordination/layer_factorial_v1_20260930/`. Both protocol
manifests mark the run `development_only`, with 24 objects, methods fixed
before evaluation, and seeds 42/43/44. SHA256:

- `rows_seed42.json`: `c4fdc9287ae0c52080c502c28ec598ab01e423f430042fcde187b14a3bbc74e4`
- `rows_seed43_44.json`: `6536be748ab58a597df42dcbf207e11ec86d620728c321d83cb68faaa3f85465`
- `protocol_manifest_seed42.json`: `abe11059137b01eb28fd51bbebf21d3ed00de9096d316f2d13495e3d7fb56cf2`
- `protocol_manifest_seed43_44.json`: `a6369fbb4cb89a0674499b37f8a47a63f008af3304ffed508dbf105412768360`

No B condition results were used for the drift distribution.
