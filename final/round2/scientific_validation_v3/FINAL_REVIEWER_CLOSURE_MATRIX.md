# Reviewer closure matrix — evidence state before manuscript rewrite

## Source coverage

The available source of reviewer comments is
`coordination/reviewer_materials/CAG-D-26-00962-reviews.txt`. It contains the
initial comments from Reviewer 1 (2026-09-14), Reviewer 2 (2026-09-24), and
Reviewer 3 (2026-09-28). The archived `response_letter_round2.md` contains
author responses, not a separate second-round reviewer report. No distinct
Round-2 reviewer comments or editor decision document was found in the
reviewer-materials directory. Therefore this matrix maps every recorded
substantive issue and marks the missing later-round source explicitly; it
does not claim to have answered comments that are not present.

Allowed dispositions follow the protocol: `CLOSED_BY_EVIDENCE`,
`CLOSED_BY_CLAIM_REDUCTION`, `REQUIRES_EXPERIMENT`, or `BLOCKING`. Evidence
closure and manuscript integration are separate: the manuscript files remain
unchanged, so claim reductions below still need to be implemented after the
scientific evidence gate.

## Reviewer 1

| ID | Recorded concern | Current evidence / limitation | Disposition now | Paper closure still required |
|---|---|---|---|---|
| R1.1 | Visible purple/color shifts, repeated patterns, full-object quality; compare unmodified and fixed-scale baselines; show unseen baked views and seams. | GT-only 24-object visual audit found material/color mismatch in 18/24 and detail loss in 21/24. Stored N=20 GLBs now have a sampler-conformant base-color evaluation, but LLH results are metric-dependent; human answers are absent and four no-UV objects remain outside 3D coverage. | `REQUIRES_EXPERIMENT` | Complete the locked human study; report GLB-native N=20 results by endpoint, state the four-object exclusion, and avoid a full-PBR or human-fidelity claim. |
| R1.2 | The 0.96 dB main-adapter gain was not tested on the disjoint 276-object set; same-protocol held-out comparison requested. | FRESH_CONFIRM_B is a disjoint 150-object campaign with 4,500/4,500 unique rows and pre-analysis integrity pass. The original 0.96 dB figure is not re-used as confirmation. | `CLOSED_BY_CLAIM_REDUCTION` | Rebuild claims from the fresh registered contrasts; remove any implication that the old pooled estimate was independently confirmed. |
| R1.3 | Texture variation diagnostics do not establish faithful texture; distinguish high-frequency variation from fidelity. | The visual archive and texture-complexity analysis bound the evidence but cannot establish human-perceived material fidelity. No responses exist. | `REQUIRES_EXPERIMENT` | Report variation separately from fidelity and complete the locked human study before making a human-fidelity claim. |
| R1.4 | CI crossing zero is not equivalence; Edge-SSIM trade-off must be reported or supported by a margin. | The V3 decision records no registered equivalence margin for `gen_linear` and preserves metric-specific outcomes. No new non-inferiority margin is introduced. | `CLOSED_BY_CLAIM_REDUCTION` | Keep paired intervals and the Edge-SSIM trade-off; avoid equivalence/non-inferiority language. |
| R1.5 | FAC experiments are difficult to reproduce; code release encouraged. | FAC is reported as a negative extension. Campaign hashes and a sanitized package exist, but full clean-clone/paper-wide reconstruction and portable archive closure remain incomplete. | `REQUIRES_EXPERIMENT` | Complete the clean-clone artifact reconstruction and make the implementation/results traceable in the final availability package. |

## Reviewer 2

| ID | Recorded concern | Current evidence / limitation | Disposition now | Paper closure still required |
|---|---|---|---|---|
| R2.1 | Contribution may be schedule selection for an existing adapter rather than a substantial method; CAI may formalize a selected schedule. | B and generic comparisons do not establish a unique winner. A2 is discovery evidence; A3b has no common dose support. CAI is descriptive, not predictive. | `CLOSED_BY_CLAIM_REDUCTION` | Present a bounded residual-allocation characterization; retire claims of a derived/optimal universal schedule or load-bearing full interaction. Novelty remains editorially at risk. |
| R2.2 | CAI interpretation may be post hoc. | No prospective CAI prediction test exists; the current CAI decision is `DESCRIPTIVE_ONLY`. | `CLOSED_BY_CLAIM_REDUCTION` | Retain only as descriptive vocabulary or remove from the core contribution. |
| R2.3 | Cross-backbone validation is the largest generality gap. | MV-Adapter covers 98/99 planned objects, with no corrected global interaction in its tested range. Intervention geometry differs from the primary backbone, so architecture is not isolated causally. | `CLOSED_BY_CLAIM_REDUCTION` | State the bounded architecture/intervention boundary; do not claim broad transfer or an architecture-causal response law. No third backbone is justified under the current feasibility matrix. |

## Reviewer 3 and later-round coverage

| Source | Recorded issue | Disposition now | Paper closure still required |
|---|---|---|---|
| Reviewer 3 initial comments | The review states that the revision looks good for publication; no separate actionable concern is listed in the available text. | No issue recorded in this source. | Reconcile against any later report if one exists; current repository does not contain a distinct Round-2 reviewer report. |
| Round-2 reviewer comments | No separate reviewer-comment source located; only the authors' response letter is present. | `BLOCKING` for a claim of complete round-by-round closure. | Obtain and map the actual later-round comments before asserting complete reviewer closure. |

## Cross-cutting reviewer risk

The strongest remaining risks are human-perceived fidelity and the paper's
novelty after schedule superiority is withdrawn. The stored N=20 GLB
base-color evaluation is complete; the human study is pre-collection, strict
N=24 3D scope is unsupported, and the paper has not been rewritten to
provisional `NARRATIVE_D`. Accordingly, this matrix is pre-rewrite and does
not pass the final reviewer gate. See `FINAL_SCIENTIFIC_READINESS_20261006.md` and
`FINAL_ADVERSARIAL_REVIEW.md`.
