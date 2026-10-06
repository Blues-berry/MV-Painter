# AUTHORITATIVE_GENERIC_SCHEDULE_REPORT — Experiment C (H4)

Cohort: FRESH_CONFIRM_300; same runner/cap semantics/seed/budget accounting as
all Phase III conditions. Definitions frozen in
scripts/run_validation_v3_experiment.py before execution:
  * shapes: linear u=t/T; cosine bump 0.5(1−cos 2πu); trapezoid rise-hold-fall
    (thirds); Gaussian peak exp(−(u−0.5)²/(2σ²)), σ=1/6
  * endpoint-matched (A): s_l = LOW_l + shape·(HIGH_l − LOW_l), per layer
  * budget-matched (B): multiplicative rescale to the LLH per-layer mean
    budget (1.675 / 1.675 / 0.585)
  * native cap semantics retained (effective = min(requested, cap))

Artifacts: formal/campaign_C/per_object_metrics.csv, pairwise_layer_llh_vs_gen_*.json,
HOLM_FAMILY_C.json (16 tests, Holm).

## Result (paired, n=300, LLH − schedule)

FG-PSNR (dB): cosine bump +0.456; trapezoid +0.304; Gaussian peak +0.531;
linear warm-up +0.005 (n.s., Holm p = 0.81). Budget-matched variants:
cosine +0.577; trapezoid +0.550; Gaussian +0.590; linear +0.145 (all
Holm-rejected). FG-LPIPS: LLH slightly better everywhere except vs
endpoint-matched linear (−0.001, Holm p = 0.0016, tiny).

## Key question

Does L-TCAS still provide a meaningful advantage once generic schedules are
tested under the SAME runner, cohort, seeds and budget accounting?
**Partially**: LLH beats 3 of 4 temporal shapes and all their budget-matched
variants. The endpoint-matched linear warm-up was not detectably different
from LLH on FG-PSNR under the registered difference test (`p=0.81`), but no
equivalence margin was frozen for H4, so this is **not an equivalence result**.
The point estimate is near zero; it remains a credible simple competitor.
FG-LPIPS detects a small average difference versus this linear schedule
(`−0.001`, Holm `p=0.0016`), whose practical importance was not bounded by a
predeclared margin. Combined with A3 (interaction real but with a collapsed
matched-dose variance share — AMENDED P0-1) and B (decomposition), the
supported structure is: (i) per-layer allocation with shallow protection,
(ii) a monotone late-increasing temporal profile. The specific 3-stage LLH
shape shows an approximately 0.4 dB point-estimate advantage over the
constant layer-mean control but not over endpoint-matched linear warm-up;
this does not establish practical equivalence to either schedule.
