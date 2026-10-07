# FRESH_CONFIRM_B temporal confirmation

Cohort: the fresh, disjoint 150-object FRESH_CONFIRM_B set. This report follows
the committed pre-unblinding snapshot (`273780c`) and its passing formal
integrity gate. Effects are paired object-level contrasts (`condition A −
condition B`), with 10,000 bootstrap resamples and seed 20261002. Positive
FG-PSNR and negative FG-LPIPS changes favor A. The bootstrap p method and its
finite reporting floor are recorded in the per-contrast JSON.

## LLH versus LFM-EXACT — temporal variation at matched layer means

The contrast was frozen as `layer_llh − lfm_exact`. Both profiles have the
same requested per-layer time mean (deep/middle 1.675, shallow 0.585); neither
profile activates a native cap. FG-PSNR is primary and FG-LPIPS is
co-reported. Favorable-object rates use higher-is-better semantics for PSNR
and lower-is-better semantics for LPIPS.

| Metric | Mean paired change | 95% paired-bootstrap CI | Favorable objects | Bootstrap p (raw) |
|---|---:|---:|---:|---:|
| FG-PSNR | +0.325 dB | [+0.209, +0.446] | 54.0% | ≤0.0001 |
| FG-LPIPS | −0.00460 | [−0.00563, −0.00357] | 76.0% | ≤0.0001 |

The frozen practical-equivalence margins were ±0.5 dB FG-PSNR and ±0.01
FG-LPIPS. Both 95% CIs fall entirely inside their respective margins. Under
the predeclared interpretation rule, this fresh cohort classifies the LLH
versus exact layer-mean constant difference as **budget-explained within the
specified practical margins**, despite a small, statistically detectable
average difference. This does not establish equality outside those margins.

The seven-contrast cap/budget Holm family has not yet been completed, so the
raw bootstrap p-values above are not final family-adjusted p-values. The
final cap/budget report will provide the locked seven-test correction for
each metric. The residual-dose/common-support analysis is also pending; this
comparison alone does not separate requested-scale timing from actual
post-scale residual dose.

Per-object source and bootstrap output:
`formal/campaign_FRESH_CONFIRM_B_20261005/paired_layer_llh_minus_lfm_exact.json`.

## Early-versus-late placement

The locked B2 family compares LLH with HLL and LLL on both endpoints
(four tests Holm-corrected together). The combined B run did not include a
separate `layer_lll` label. Before analysis, `a3_baseline` was verified to
have the same 50-step requested trace as the all-low LLL schedule, with the
same capped adapter path; it is therefore the B-cohort LLL control.

| Contrast | Metric | Mean paired change | 95% CI | Favorable objects | Holm p upper bound |
|---|---|---:|---:|---:|---:|
| LLH − HLL | FG-PSNR | +0.687 dB | [+0.404, +0.981] | 45.3% | ≤0.0004 |
| LLH − HLL | FG-LPIPS | −0.01098 | [−0.01349, −0.00851] | 80.7% | ≤0.0004 |
| LLH − LLL | FG-PSNR | +0.734 dB | [+0.597, +0.875] | 79.3% | ≤0.0004 |
| LLH − LLL | FG-LPIPS | −0.00845 | [−0.01029, −0.00659] | 82.0% | ≤0.0004 |

All four locked mean contrasts reject zero after Holm correction. The
LLH−HLL FG-PSNR mean is heterogeneous: its median is −0.104 dB and only
45.3% of objects favor LLH, even though the mean and its confidence interval
are positive. Thus the aggregate PSNR difference is driven by an uneven
object response; LPIPS favors LLH for about four-fifths of objects. LLH also
improves both mean endpoints over the all-low control. These results support
a schedule-location effect in the registered contrasts, while ruling out a
simple claim that late-high LLH improves PSNR for a typical object.

The four-test family and its bootstrap-floor bounds are in
`formal/campaign_FRESH_CONFIRM_B_20261005/HOLM_FAMILY_B2_FRESH_CONFIRM_B.json`.
The paired estimates are in the two `paired_layer_llh_minus_*.json` files in
the same run directory. The overlapping LLH−HLL contrast will also appear in
the separate seven-contrast cap/budget family because that second family was
explicitly frozen in the combined B lock.

## HLL versus LLL — user-requested post-unblinding exploratory contrast

The addendum also requests HLL−LLL to assess whether early-high itself is
harmful. This contrast was not in the frozen H3 family and was computed after
the other B temporal contrasts had been opened; it is therefore exploratory,
with a separate two-endpoint Holm correction. `a3_baseline` was verified from
the B manifest to be the all-low LLL profile.

| Contrast | Metric | Mean paired change | Median | 95% CI | Favorable objects | Holm p |
|---|---|---:|---:|---:|---:|---:|
| HLL − LLL | FG-PSNR | +0.047 dB | +0.476 dB | [−0.120, +0.208] | 66.0% favor HLL | 0.5696 |
| HLL − LLL | FG-LPIPS | +0.00253 | +0.00139 | [+0.00155, +0.00354] | 40.0% favor HLL | ≤0.0002 |

The PSNR mean is near zero and its interval includes zero; its positive median
and 66% favorable rate show a skewed object distribution. LPIPS instead
reliably favors LLL over HLL on average. This does **not** support a broad
claim that early-high hurts across endpoints. Together, the locked LLH
contrasts support a late-position advantage for the registered comparisons,
but the direction depends on the metric and object; “early-high hurts / late-
high helps” must be narrowed to the specific contrast and endpoint evidence.
The raw paired analysis and exploratory Holm family are
`formal/campaign_FRESH_CONFIRM_B_20261005/paired_layer_hll_minus_a3_baseline_exploratory.json`
and `HOLM_FAMILY_HLL_LLL_EXPLORATORY.json`.
