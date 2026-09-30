# Manuscript changelog — next-round revision (2026-09-30)

Base: `final/round2/archive/revision_before_next_round_20260930/` (previous
layer-wise author-review snapshot, preserved unmodified). Current deliverable:
`final/round2/final_round2.tex`, `supplementary_round2.tex`,
`response_letter_round2.md`.

## main_round2.tex (final_round2.tex)

| # | Change | Reason |
|---|---|---|
| 1 | Removed all four `\iffalse` provenance blocks (old abstract, historical sweep/probe tables, pooled 300-object + CLIP-IQA + preference block, historical adapter-dependence block) from the source; prior version archived | Deliverable must not contain retired claims (+0.96 dB, CLIP-IQA, preference) even commented |
| 2 | New Figure 1 (`fig1_layerwise_20260930.pdf`, generator `scripts/make_fig1_layerwise_20260930.py`): three depth groups with caps, per-group schedules, layer-LHL example | Old figure was TCAS/FAC-centred; the method is layer-wise |
| 3 | Abstract rewritten: layer-wise method, complete factorial result (late-high helps, early-high hurts; LLH strongest on 5/7), pre-registered strict-276 confirmation, honest bake boundary | Align abstract with actual evidence |
| 4 | Contributions (1)-(4) rewritten; explicit counterexamples; no optimality/selector claims | R2.1 |
| 5 | Method section: explicit `up_0/up_1/up_2 -> deep/middle/shallow` mapping, per-group caps 3.0/3.5/0.8, min-cap semantics (global fixed-low effectively shallow-capped at 0.8), layer-fixed-mean = exact 17/16/17 means (1.65/0.58), no-forward-overhead statement | Reviewer request for implementation clarity; audit findings |
| 6 | Section 3.3 retitled "Stage-aware Adapter Scaling: Shared-layer TCAS and the Layer-wise Form"; TCAS/C3 positioned as shared-layer baseline throughout (naming audit of every "TCAS" mention) | Main method is layer-wise |
| 7 | Metrics section: four-dimension taxonomy (structure / reference fidelity / texture variation / 3D output); variation metrics can never imply fidelity alone | R1.3 |
| 8 | Ablation section restructured into (i) global vs layer-wise, (ii) constant vs scheduled, (iii) complete 8-pattern factorial with new Table `tab:factorial`; robust-directions-only claim added | R2.1; complete binary ablation (D18) |
| 9 | New confirmation subsection (`subsec:confirmation`, Stage B) with same-runner strict-276 results | Pre-registered confirmation (protocol lock) |
| 10 | Stage-placement table caption clarified: those HLL/LHL/LLH rows are GLOBAL schedules | D18 scope correction |
| 11 | Layer-LHL transfer-record paragraph: discloses unseeded Python RNG (non-reproducible on restart); conclusions moved to the seeded confirmation set | METHOD_IMPLEMENTATION_AUDIT finding |
| 12 | Second-backbone section: interface audit paragraph; labeled global stage-position replication, not layer-wise cross-backbone validation | R2.3 |
| 13 | Limitations rewritten around the layer-wise method: probe-vs-holdout boundary, non-equal-budget placement, bake covers global conditions only, second-backbone global-only, runner-sensitivity | Phase 7 item 11 |
| 14 | Conclusion rewritten to the four directly supported conclusions; negative results retained | Phase 7 item 12 |
| 15 | Data availability: concrete artifact list, license constraints, no supplementary video | R1.5; honesty |

## supplementary_round2.tex

| # | Change |
|---|---|
| S9 | Added runner-sensitivity paragraph (reference-image random augmentation; within-run pairing only) |
| S10 | NEW: complete binary temporal-pattern factorial (protocol, table, paired comparisons, no-dominance statement) |
| S11 | NEW: strict-276 confirmation of pre-registered candidates (table + paired bootstrap + cross-runner replica check) |
| S4b | NEW: layer-wise bake extension with same-draw global controls (4-way table; LLH 12/12 wins vs LHL and vs global C3) |
| S1 | Protocol hashes unchanged (verified 2026-09-30) |

## response_letter_round2.md

Rewritten point-by-point in the reviewers' original order (R1.1-R1.5, R2.1-
R2.3, R3), each with direct answer, changes made, evidence, scope/limits,
manuscript locations, and artifact paths. R1.1 now reports the two-layer
bake evidence (original global case study + same-draw layer-wise extension);
R1.2 reports the confirmation numbers and the replica cross-check.

## New evidence artifacts

- `coordination/layer_factorial_v1_20260930/`: 576-row factorial (rows,
  manifests, summary, SHA-256 index).
- strict-276 confirmation records: `/4T/tmp/mvpainter-layer-confirmation-20260930/`
  (rows/CSV/manifests per schedule; analysis JSON) — copied into
  `coordination/layer_confirmation_20260930/` at finalization.
- Layer-wise bake extension: `BAKE_INPUT_HANDOFF_LAYERWISE_20260930.json`,
  `cpu_bake_12_layerwise/` outputs, evaluation tables.
