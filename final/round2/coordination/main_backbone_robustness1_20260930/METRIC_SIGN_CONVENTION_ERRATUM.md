# ERRATUM — sign convention clarification for MAIN_BACKBONE_ROBUSTNESS1_REPORT (2026-10-01)

The report's statistics paragraph says "Mean paired deltas (first minus
second)". The analysis code (scripts/analyze_robustness1_20260930.py,
`BETTER` map, L57-58) applies a benefit-oriented transform: for
lower-is-better metrics (fg_lpips, full_lpips) the difference is
sign-reversed. Reported deltas therefore mean:

  delta > 0  <=>  the FIRST-named condition is better on that metric,

not the literal arithmetic difference of the raw metric values. Example:
"layer_llh − global_fixed_low FG-LPIPS = +0.0308" means LLH's FG-LPIPS is
0.0308 LOWER (better) than GFL's; the raw LPIPS difference is −0.0308.
Win rates and stability labels use the same transform throughout; all
numbers in the report remain correct and mutually consistent. The
PROTOCOL_LOCK statistics-plan wording "'minus' = first minus second"
carries the same omission. Full audit: 
../core7_same_runner_completion_20261001/METRIC_SIGN_CONVENTION_AUDIT.md.
