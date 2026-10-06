# Scientific readiness — 2026-10-05

Historical snapshot. Superseded for the 3D renderer gate by
`FINAL_SCIENTIFIC_READINESS_20261006.md`; the prior P1-9-open status is
closed for the supported stored N=20/eight-condition GLBs. Other gates and
this snapshot's original rationale remain in the dated record below.

## Verdict

`MORE_EXPERIMENTS_REQUIRED`

`SUBMISSION_READY=NO`

`SCIENTIFIC_EVIDENCE_FREEZE=NO`

`HUMAN_EVIDENCE_GATE=OPEN`

`PRE_ACCEPTANCE_P0=0`; `SCIENTIFIC_P1=1` (P1-9); `OPERATIONAL_P1=1` (P1-2).

The current evidence supports provisional `NARRATIVE_D`: characterize adapter
scaling and residual allocation, with depth allocation primary and tested
temporal contrasts secondary on the primary backbone. Do not make a full
Layer × Time interaction load-bearing. A2 is a native-dose discovery map;
A3b is `PARTIAL` because layer-dose ranges have no three-layer common support
(0/2,250 rows). The MV-Adapter result is a bounded intervention-specific
boundary. Its different intervention geometry does not isolate architecture
as a cause.

## Evidence state

- **B:** 4,500/4,500 unique rows passed the formal integrity gate before
  condition-level analysis. B was already unblinded before the practical
  reference and narrative safeguards were written. Those safeguards are
  retrospective; they do not restore prospective blinding.
- **B interpretation:** LLH−LFM-EXACT is statistically detectable but lies
  inside the frozen practical margins. The full LLH/HLL/LLL directional
  conjunction fails: HLL−LLL has an FG-PSNR interval crossing zero and
  FG-LPIPS points toward LLL. Registered `gen_linear` is a credible
  primary-endpoint competitor; Experiment C and the same-cohort post-lock B
  sensitivity show no LLH FG-PSNR advantage. No equivalence claim is made.
- **Practical reference:** historical same-condition drift from a 24-object,
  three-seed development probe is frozen in
  `PRACTICAL_EFFECT_REFERENCE.md`. It is retrospective, was not calculated
  from B rows, and is a scale reference rather than an acceptance threshold.
- **Human study:** four pairs are locked, including LLH vs `gen_linear`; 40
  assignment slots, fixed stopping, 24 comparisons per participant, eight
  separate endpoints, and a minimum of 36 valid completions. No responses
  have been collected. The site is local/offline; no participant recruitment
  or distribution has occurred.
- **Cross-backbone:** MV-Adapter has 98/99 planned objects. No corrected
  global Layer × Window interaction survives its exploratory four-metric
  family. Report this bounded result without searching scales, windows, or
  objects. It is consistent with intervention-specific response surfaces,
  but is not a matched causal architecture test.
- **3D:** current N=20 outputs are historical diagnostics, not faithful-GLB
  validation. The CPU bake and unseen renderer clamp UVs; exported GLBs omit
  wrap fields and default to repeat. The CPU renderer also lacks the exported
  mipmap minification filter. Six baked objects have substantial UVs outside
  [0,1]. In addition, the run summary lists 16 objects/128 records while
  output GLBs, metadata, and the unseen ledger cover 20 objects/160 rows.
  No corrected render/bake was performed, and strict 24-object closure is
  open. See `UV_VALIDITY_AUDIT_20261005.md`.
- **Reproducibility:** compact statistics and one full A2 condition have
  clean-clone evidence; full paper-wide table/figure regeneration and
  post-rewrite forensic review remain open. The manuscript is unchanged.

## Closure gates

| Gate | State | Required closure |
|---|---|---|
| Scientific integrity | **OPEN** | Resolve scientific P1-9 with conformant UV addressing/filtering and a frozen malformed-UV rule, then re-evaluate the frozen bake cohort; or formally remove the 3D claim and justify the evidence de-scope without implying faithful rendering. |
| Causal identification | **BOUNDED** | Keep A3b native/bounded-dose scope and avoid dose-independent interaction or equal-dose language. |
| Independent confirmation | **PARTIAL** | B is complete and integrity-checked, but later safeguards are retrospective; label discovery, registered, and exploratory results accurately. |
| Perceptual validity | **OPEN** | Run the locked four-pair human study to the fixed 40-slot stop and report all eight endpoints; at least 36 valid completions are required. |
| 3D practical validity | **OPEN** | Establish GLB-equivalent addressing and filtering, handle repeat-boundary splatting/inpainting, and document the four no-UV exclusions. |
| Generalization | **BOUNDED** | Keep MV-Adapter scoped to its tested design; do not claim architecture causality or broad transfer. A third backbone is not justified by the current feasibility record. |
| Reproducibility | **PARTIAL** | Complete a clean-clone full-condition/paper artifact reconstruction and archive portable inputs, code, and hashes. |
| Narrative | **PROVISIONAL D** | Preserve the bounded characterization; no unique schedule winner, validated full interaction law, or universal timing signature. |
| Reviewer closure | **PRE-REWRITE** | Use `FINAL_REVIEWER_CLOSURE_MATRIX.md`; re-run the four-persona audit after any future manuscript rewrite. |
| Final forensic audit | **OPEN** | Regenerate every final table/figure and verify manuscript values only after evidence closure and an authorized rewrite. |

## Decision at the B unblind point

- **Do not run a third backbone now.** The current MV-Adapter evidence is a
  useful boundary, and the feasibility matrix has no candidate satisfying
  the frozen gates.
- **Do not run FRESH_CONFIRM_C to search for a winning schedule.** B does not
  support unique LLH superiority; another same-family schedule search would
  not repair the dose or perceptual gaps. Reconsider C only for a newly
  justified hypothesis frozen on a new cohort.
- **Proceed to the already locked human study only after a participant
  recruitment and response-return channel is arranged.** Do not change its
  pairs or analysis and do not inspect preferences before all slots resolve.
- **Keep the corrected 3D gate open.** The current environment has no Blender
  executable; do not call the old CPU outputs corrected GLB renders.

No manuscript edits, participant contact, external study distribution,
schedule retuning, third-backbone run, corrected bake, or remote push occurred
in this continuation.
