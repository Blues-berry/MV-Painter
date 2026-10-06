# Retrospective narrative-switch reassessment — 2026-10-05

Update 2026-10-06: the GLB-native base-color audit is complete for the stored
N=20/eight-condition cohort. Its mixed endpoints do not change the narrative
decision. Strict N=24 coverage and human-perceived fidelity remain open; see
`FINAL_SCIENTIFIC_READINESS_20261006.md`.

**Status:** retrospective. B outcomes were exposed before the addendum locks;
this reassessment applies the supplied A–D rules but cannot restore a
prospective decision gate. It supersedes the earlier provisional selection of
`NARRATIVE_B` in `FINAL_NARRATIVE_DECISION.md` and related summaries.

## Decision

**Current provisional class: `NARRATIVE_D`.** Frame the work as a measured
adapter-scaling and residual-allocation characterization, with depth allocation
as the main dimension and the tested temporal contrasts as secondary evidence.
Do not present LLH as a winning schedule, a universal timing rule, or a
dose-independent Layer × Time law. At the time of this 2026-10-05 decision,
the human and 3D gates remained open; the updated N=20 3D scope is recorded
above, while the human gate remains open.

## Rule-by-rule assessment

| Rule | Evidence | Ruling |
|---|---|---|
| **A — full layer × time mechanism** | A3b is `PARTIAL`: linear/log dose covariates retain significance, but the three layer dose ranges have no common support (0/2,250 rows); calibration errors are deep −20.01%, middle −20.20%, shallow +98.98%. | **Not met.** No dose-independent interaction claim. |
| **B — two separately supported control dimensions** | A2 supports a native-dose depth × window response map. B supports specific temporal contrasts, but the LLH−LFM-EXACT effects fall inside the frozen practical margins; the required HLL<LLL direction is not stable across endpoints (PSNR CI crosses zero; LPIPS favors LLL). | **Not the headline.** Preserve distinct depth and timing measurements, without calling them independent mechanisms. |
| **C — weaken timing after exact-budget control** | In FRESH_CONFIRM_B, LLH−LFM-EXACT is +0.325 dB FG-PSNR [0.209, 0.446] and −0.00460 FG-LPIPS [−0.00563, −0.00357], both inside the predeclared ±0.5 dB / ±0.01 margins. LLH−HLL remains a registered contrast, but PSNR is object-heterogeneous (45.3% favorable; median −0.104 dB). | **Applies.** Keep timing secondary and contrast-specific. |
| **D — generic schedules match or exceed LLH** | In registered Experiment C, LLH−`gen_linear` is +0.004885 dB FG-PSNR [−0.034994, +0.046888], Holm p=0.8148. The post-lock B sensitivity is −0.0373 dB [−0.0829, +0.0086], Holm p=0.1150. Neither shows a primary-endpoint LLH advantage. | **Use D's characterization framing.** These results do not establish formal equivalence because H4 had no equivalence margin; they do rule out a supported “best schedule” claim. The B extension remains same-cohort, post-lock sensitivity, not independent confirmation. |

The four-way B signature does not pass: LLH exceeds the listed comparators on
mean contrasts, but HLL−LLL is exploratory, inconclusive on FG-PSNR, and favors
LLL on FG-LPIPS. Therefore the data do not support a general rule that early
high control hurts while late high control helps. Keep the narrow registered
LLH−HLL result and its object/metric heterogeneity visible.

## Consequences

- Keep `gen_linear` in the frozen human comparison. The four-pair study remains
  unlaunched, with no responses.
- Do not tune LLH or add schedules/backbones in response to these outcomes.
- Keep A3b `PARTIAL`, stage boundaries `HEURISTIC_ONLY`, CAI
  `DESCRIPTIVE_ONLY`, and MV-Adapter conclusions bounded to its tested
  intervention.
- Keep `SUBMISSION_READY=NO`; do not edit the manuscript, supplement, or
  response letter before the remaining evidence gates close or receive a
  documented waiver.
