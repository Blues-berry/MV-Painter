# Internal reviewer-response ledger — supplied R1–R3 set

**Internal status:** revised manuscript and supplement edited and compiled; reviewer closure is not marked closed. The external-facing draft is [response_to_reviewers_external_draft_20261007.md](response_to_reviewers_external_draft_20261007.md). No response has been submitted.

## Scope and provenance

- This ledger uses the supplied R1–R3 comment set. The audited source records do not conclusively identify the formal review round or link the review-export manuscript number to the frozen 01549 PDF; see [reviewer-source provenance](REVIEWER_SOURCE_PROVENANCE_20261007.md), `ROUND_IDENTITY_UNCERTAIN`.
- Evidence and replies use non-human results only. No participant-level human responses were accessed, analyzed, or used to support a reply.
- The revised main source is `final/final_0903.tex`; the revised supplement is `final/supplementary_0903.tex`. Compiled outputs are `final/revision_20261007.pdf` and `final/supplementary_revision_20261007.pdf`.
- The generated image-space evidence does not establish baked-texture, unseen-view, material, perceptual, or seam fidelity. Retired 3D/seam claims remain withdrawn.

## Item ledger

| Item | Evidence status | Implemented manuscript action | Remaining issue |
|---|---|---|---|
| R1.1 | PARTIAL | Added selected rights-cleared side-by-side image-space illustrations; acknowledged visible material/color and detail failures; removed unsupported 3D/seam superiority claims and bounded fidelity language. | Evidence cannot establish baked/unseen-view or seam quality. This is addressed through claim withdrawal, not a new validation. |
| R1.2 | READY | Reported Fresh C N=300 main GeoTex-Adapter result: registered primary C3−GFL FG-PSNR +0.522 dB, 95% CI [+0.404, +0.641], 68.7% favorable; identified it as a revision-era follow-up, not an original-registration replication. | Historical strict-276 estimate remains retrospective support with incomplete legacy runner/input provenance. |
| R1.3 | READY | Recast gradients, Laplacian variance, and color variation as descriptive variation diagnostics; separated image-space similarity from fidelity claims. | No participant-level human evidence was analyzed; no human-preference claim is supported by this response. |
| R1.4 | READY | Added Fresh C N=300 C3−GFH post-hoc paired audit and trade-off; explicitly rejected equivalence/non-inferiority; retained Fresh B N=150 only as a separate supporting sensitivity. | No margin was prespecified. Fresh C is post hoc and not part of its registered primary family. Cohorts remain separate. |
| R1.5 | READY | Removed FAC results and reproducibility claims from main manuscript and supplement; final disposition is `REMOVED_FROM_REVISION`. | No FAC reproducibility or release claim is made. |
| R2.1 | PARTIAL | Reframed contribution as implementation-aware execution semantics plus bounded Fresh C object/endpoint evidence; acknowledged prior scheduling work and reported generic linear alongside C3. | `VENUE_RISK` remains: editorial significance is unresolved. This is not a reason to expand experiments or restore retired claims. |
| R2.2 | READY | Removed CAI model, proposition, formal selector, and optimality/prediction claims from main text and supplement. | Final disposition remains `REMOVE_CORE / SUPPLEMENT_ONLY`; no descriptive CAI diagnostic is retained. |
| R2.3 | READY | Added MVDiffusion and MV-Adapter as interface-specific boundary tests; disclosed the unavailable official MVDiffusion depth weights and exploratory MV-Adapter result; removed broad transfer claims. | Tests are not matched replications and do not identify architecture-level causes. |
| R3 | READY | Thank-you response only. | No technical action requested. |

## Cross-document checks

- Fresh C primary, addendum, and C3−GFH numbers are traceable to the numerical authority and result registry. Fresh B's seven paired values are also authority rows, labeled `RETROSPECTIVE_POST_HOC_SUPPORTING_SENSITIVITY`, with the hash-pinned source and recomputation artifacts. The compact object-level metrics and paired deltas needed to reaggregate these results are bundled under `numerical_inputs`; Fresh B remains a separate cohort and is not pooled with Fresh C.
- Generic-linear results remain visible: mean C3−linear FG-PSNR is −0.593 dB, but median is +0.074 dB and 51.7% of objects favor C3; mean FG-LPIPS favors generic linear. No cross-endpoint score or universal winner is claimed.
- Qualitative selections are identified as illustrations. Rights, source/output hashes, UIDs, methods, and selection metadata are retained in the candidate index and final-selection record.
- Both revised LaTeX sources compiled successfully. The response locations refer to the compiled main PDF and supplement.

## Remaining package gate

- `CLEAN_CHECKOUT_REPRODUCIBILITY = PARTIAL / OPEN`: clean checkout reproduced the bundled paired statistics and compiled both paper sources; full generation-source reconstruction remains open because run-bound manifests and prediction/render inputs are incomplete. The current audit is documented in [the clean-checkout addendum](CLEAN_CHECKOUT_REPRODUCIBILITY_ADDENDUM_20261007.md). No generation or training rerun was needed for the bounded current claims.
- `REVIEWER_SOURCE = ROUND_IDENTITY_UNCERTAIN`: continue with the supplied set and keep the caveat out of the external reply.
- `R2.1 = OPEN / VENUE RISK`: retain internally; do not insert this self-assessment into the reviewer-facing response.
- Final author review and any submission action remain outstanding. No journal submission or reviewer-response upload has occurred.
