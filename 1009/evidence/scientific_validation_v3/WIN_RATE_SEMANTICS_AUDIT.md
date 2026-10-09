# Win-rate field semantics audit

Date: 2026-10-05.

## Finding

The historical analysis helper `analyze_v3.py::paired_bootstrap` stores
`win_rate = mean(delta > 0)` and `loss_rate = mean(delta < 0)` while preserving
the raw subtraction direction for every metric. This is a positive-delta rate,
not a favorable-outcome rate for lower-is-better metrics such as LPIPS.

## Scope and impact

- Means, medians, confidence intervals, bootstrap p-values, and Holm results
  are unaffected.
- Historical JSON files remain unchanged for provenance; their `win_rate`
  field is interpreted as `positive_delta_rate` unless the report states a
  higher-is-better metric.
- Narrative reports that display an LPIPS win rate must invert the raw
  positive-delta fraction. `EXACT_BUDGET_TEMPORAL_CAUSAL_REPORT.md` does so;
  its reported favorable-object rates are 77.0%, 80.0%, and 86.3% for the
  LLH−LFM-EXACT, LLH−HLL, and LLH−LLL contrasts, respectively.
- A2's cell table explicitly reports the raw `Δ>0` rate and states the sign
  convention, so it does not relabel the rate as favorable.
- The cap/budget report's displayed win rate is for FG-PSNR, a higher-is-better
  metric; no correction is needed there.

## Closure

New FRESH_CONFIRM_B summaries will compute a direction-aware favorable rate
from the frozen metric direction table and will separately retain the raw
positive-delta rate. No experiment rerun is required because the underlying
object-level deltas are intact. Status: **CLOSED as a reporting-semantic
correction; no effect on inferential results.**
