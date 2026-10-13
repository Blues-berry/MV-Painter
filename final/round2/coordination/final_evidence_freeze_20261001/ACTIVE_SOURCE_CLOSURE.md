# Active Source Closure — Gate 3 re-evaluation — 2026-10-01

Scope: only the three active sources `final/round2/final_round2.tex`,
`final/round2/supplementary_round2.tex`, `final/round2/response_letter_round2.md`.
No new inference, no new experiment, no schedule search, no cohort change,
no full narrative rewrite. Archive/forensic hits are out of scope and allowed.

## Closure checklist

| Check | Status |
|---|---|
| Historical LHL removed from active claims | PASS |
| RNG causal attribution removed | PASS |
| capped/uncapped distinction explicit | PASS |
| Core-7 current baseline authority | PASS |
| additive decomposition absent | PASS |
| obj_0066 provenance corrected | PASS |

## What was changed

### final_round2.tex
- Old archived-record paragraph (formerly: "did not seed the Python RNG …
  Full-PSNR 22.052 … FG-PSNR 14.776 …") replaced by the provenance sentence:
  the earlier layer-LHL record is excluded from all quantitative claims
  because its runner-time code state cannot be assigned complete reproducible
  provenance; all current holdout comparisons use the seeded same-runner
  records. No archived numbers, no root-cause story.
- Confirmation section: the "FG-PSNR 12.97 vs 14.78; Pearson r=0.66 …
  confirming that the reference-preprocessing draw shifts absolute values"
  sentence replaced by: the seeded layer-LHL replica is the only layer-LHL row
  retained for quantitative confirmation; the earlier historical record is
  excluded because its complete runner-time provenance cannot be
  reconstructed; preprocessing-realization audits do not explain that
  discrepancy. Closing sentence no longer re-imports the archived record.
- `tab:strict276` (clean-v2) caption now marked **LEGACY UNCAPPED DIAGNOSTIC —
  WITHIN-PANEL ONLY**, not comparable with the capped Core-7; the
  "non-dominance result" paragraph is limited to the legacy uncapped panel and
  the current baseline-family ranking is pointed at the capped strict-276
  Core-7 confirmation.
- `tab:stage276` and `tab:serialized276` captions marked legacy uncapped
  within-panel only; follow-up paragraph framed as within-panel diagnostic.
- Caps paragraph: "development-selected, holdout-frozen implementation caps …
  frozen before strict-276 evaluation, with no cap retuning on that cohort";
  all seven Core-7 conditions use the same capped implementation.
- CAI paragraph: "LLH–GFL is a combined allocation effect … the current
  evidence does not identify additive causal contributions in dB." No
  additive dB decomposition anywhere in the active sources.
- obj_0066 figure caption: "high-improvement example … selected as a
  high-improvement case rather than a representative or median case"; panel
  intro text no longer calls the set "representative".
- Limitations: cross-runner non-comparability stated without attributing it
  to the augmentation draw. Conclusion (3): layer-LHL enters the holdout only
  as a seeded same-runner confirmation row.
- Abstract (pre-existing working-tree edit, retained): Core-7 LLH best mean on
  four of seven metrics with explicit metric-dependent reversals on the other
  three — no universal-dominance wording.

### supplementary_round2.tex
- "Cross-runner replica check" paragraph (unseeded RNG / 12.97 vs 14.78 /
  r=0.66 / single unseeded run) deleted and replaced by "Historical layer-LHL
  record": retained only as a forensic artifact, excluded from quantitative
  claims, all paired holdout conclusions use the seeded same-runner protocol.
- S1: main four-condition run and stage-placement follow-up labeled legacy
  uncapped diagnostics, not pooled with the capped Core-7; new
  "Reproducibility scope of the Core-7 protocol" note (shared-input audits,
  protocol identity, paired records; full per-object serialized tensor hashes
  retained for the added completion arms but not for all earlier frozen
  Core-5 arms). Not placed in Abstract/Conclusion.
- S2 header marked legacy uncapped within-panel diagnostic.
- S4b: cross-runner non-comparability stated without attributing it to
  reference draws.

### response_letter_round2.md
- R1.1: "representative improvement" → "high-improvement example".
- R1.2 item 2: clean-v2 panel non-dominance limited to the legacy uncapped
  panel; current baseline-family ranking pointed at the capped strict-276
  Core-7 protocol.
- R1.2 item 3: archived record no longer labeled an independent transfer
  record; explicit **Audit correction** added: "During the audit we identified
  an earlier layer-LHL record whose complete runner-time provenance cannot be
  reconstructed. We therefore removed it from all quantitative comparisons
  rather than attributing the discrepancy to preprocessing randomness. All
  revised holdout results are taken from the seeded same-runner Core-7
  protocol."
- R1.1 bake rationale and R1.3 texture-diagnostics label reworded to remove
  refuted draw-causality and stale "transfer record" phrasing (the texture CIs
  themselves come from the seeded same-runner confirmation rows and remain).

## Static scan result (active sources only)

Patterns scanned: `14.776`, `14.78`, `22.052`, `12.97 vs 14.78`, `r=0.66`,
`unseeded`, `Python RNG`, refuted preprocessing-draw causal phrasing,
additive-dB-decomposition phrasing, unqualified `obj_0066 representative`.

- Remaining `12.974` hits: the seeded Core-7 replica rows only (allowed; the
  quarantine forbids its use against the archived 14.78 record, which no
  longer appears).
- Remaining "representative" hits: layer-LHL-as-representative-pattern
  framing and the correction sentences themselves (allowed).
- Remaining "preprocessing draw" mentions: neutral protocol descriptions of
  per-object seeding (no causal claim about the archived discrepancy).
- Cross-panel absolute comparisons: none; all legacy panels are labeled
  within-panel-only and not pooled with the capped Core-7.

Build check: `final_round2.tex` and `supplementary_round2.tex` recompile with
0 errors (13 pp / 7 pp).

## Verdict

All six checks PASS. Gate 3 active-source blockers are closed.
