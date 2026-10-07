# 01549 manuscript-revision entry verdict — 2026-10-07

## Entry decision

**READY_FOR_MANUSCRIPT_REVISION = YES.** The evidence-entry gate passed before formal source editing began. This is an entry decision, not a claim that reviewer items are closed or that a response has been submitted.

## Current implementation state

The formal revision is now in the isolated authority worktree. `final/final_0903.tex` and `final/supplementary_0903.tex` contain the revised manuscript and supplement. The eight-page main PDF and four-page supplementary PDF compiled successfully; the reviewer-facing draft now cites verified page/line locations. See [the external response draft](response_to_reviewers_external_draft_20261007.md) and [evidence closure matrix](REVIEWER_EVIDENCE_CLOSURE_MATRIX_V2.md).

| Item | Evidence status | Manuscript status | Implemented action / remaining point |
|---|---|---|---|
| R1.1 | PARTIAL | READY_TO_EDIT | Added selected image-space illustrations and withdrew unsupported 3D/seam claims. Unseen-view, baked-texture, material, and seam quality remain unvalidated. |
| R1.2 | READY | READY_TO_EDIT | Reported Fresh C N=300 main-adapter result and its follow-up/registration limits. |
| R1.3 | READY | READY_TO_EDIT | Recast variation diagnostics and removed unsupported fidelity inferences; participant-level human data were not analyzed. |
| R1.4 | READY | READY_TO_EDIT | Reported Fresh C paired C3−GFH trade-off as post hoc; Fresh B remains separate; no equivalence/non-inferiority claim. |
| R1.5 | READY | READY_TO_EDIT | FAC removed from the main manuscript and supplement; disposition `REMOVED_FROM_REVISION`. |
| R2.1 | PARTIAL | READY_TO_EDIT | Two bounded empirical contributions and prior art are reflected in the revision; novelty sufficiency remains an internal venue risk. |
| R2.2 | READY | READY_TO_EDIT | CAI model and predictive/optimality claims removed from main text and supplement. |
| R2.3 | READY | READY_TO_EDIT | Boundary tests, compatibility-base limitation, and bounded transfer scope added. |
| R3 | READY | NOT_STARTED | Thank-you response only; no manuscript change requested. |

The plan's controlled manuscript-status vocabulary is retained; these values do not imply reviewer closure. No item is marked `CLOSED`.

## Stage outputs and gates

- **FAC_DISPOSITION = REMOVED_FROM_REVISION**
- **FRESH_C_C3_GFH_POSTHOC = PASS**
- **VISUAL_CANDIDATE_POOL = PASS** — full N=300 index and audited candidate pool are present.
- **MAIN_PAPER_VISUAL_SELECTION = PASS** — selected UIDs, reasons, metrics, rights, attribution, and hashes are frozen and used in Fig. 4.
- **REVIEWER_EXTERNAL_DRAFT = READY** — completed-revision wording with verified page/line references; still a working draft for author review.
- **REVIEWER_SOURCE = ROUND_IDENTITY_UNCERTAIN** — documented; work continues on the supplied R1–R3 set.
- **CLEAN_CHECKOUT_REPRODUCIBILITY = PARTIAL / OPEN** — the exact candidate passed clean-checkout paired-statistic reaggregation (42 rows), the 20-panel pool hash audit, and clean compilation of the 8-page main manuscript and 4-page supplement. Full generation-source reconstruction remains open because all run-bound manifests and prediction/render inputs are not packaged. See [the candidate addendum](CLEAN_CHECKOUT_REPRODUCIBILITY_ADDENDUM_20261007.md); the older report is a historical snapshot.
- **REVIEWER_CLOSURE = OPEN** — final package review remains; no submission or reviewer acceptance is claimed.

## Entry-condition audit

| Plan condition | Result | Basis |
|---|---|---|
| Fresh C C3−GFH audit complete or technically blocked | PASS | Paired audit completed after source-integrity gate passed. |
| R1.4 numerical authority frozen | PASS | Fresh C post-hoc rows appear in both authority tables with source hashes and allowed/forbidden wording. |
| Reviewer visual candidate pool complete | PASS | Full-cohort index, rights-cleared groups, metadata, and audit are present. |
| Main-paper visual candidates frozen | PASS | Final selected UIDs are recorded with rationale, rights, attribution, and hashes. |
| R1.3 fidelity-language audit complete | PASS | Sentence-level audit is present and reflected in the revised source. |
| FAC disposition selected | PASS | `REMOVED_FROM_REVISION`, with removal reflected in main and supplementary sources. |
| R2.1 contribution set frozen | PASS | Two bounded empirical contributions; venue risk remains explicit internally. |
| CAI manuscript action selected | PASS | `REMOVE_CORE / SUPPLEMENT_ONLY`; CAI itself is not retained in the revised manuscript or supplement. |
| R2.3 final scope wording selected | PASS | Interface-specific boundary wording and limitations are included in both revised sources. |
| Reviewer-source provenance verified or marked uncertain | PASS | `ROUND_IDENTITY_UNCERTAIN` is documented; supplied set is retained. |
| External response draft generated | PASS | Separate external draft reports implemented changes and verified locations. |
| Evidence matrix V2 complete | PASS | R1.1–R1.5, R2.1–R2.3, and R3 are mapped; none is marked closed. |
| Reviewer-facing numbers traceable | PASS | Fresh C primary, addendum, and C3−GFH figures map to numerical authority and result registry. |
| Retired claims absent from external draft | PASS | 3D/seam superiority, CAI optimality, universal winner/transfer, and fidelity guarantees are withdrawn or bounded. |

## Remaining before submission

1. Decide whether the disclosed generation-source reconstruction limit is acceptable for submission; no new generation or training run is needed for the bounded current claims.
2. Perform final author review of the revised source, figures/attributions, supplementary material, and external response.
3. Reconcile any final edits against the numerical authorities and recompile to refresh page/line references.
4. Submit only after the authors choose to do so; no submission action has occurred here.
