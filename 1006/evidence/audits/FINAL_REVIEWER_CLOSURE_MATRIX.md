# Reviewer closure matrix — evidence state before manuscript rewrite

## Source coverage

The user supplied `/4T/CXY/MV-Painter/第二轮审稿意见.txt` on 2026-10-06
as the second-round reviewer source. Its substantive R1/R2/R3 text matches
`coordination/reviewer_materials/CAG-D-26-00962-reviews.txt`; normalized
alphanumeric comparison differs only in page numbers (similarity 0.999566).
Both retain internal “Initial submission” labels and discuss a revision.
Use the user-designated file for this round and preserve that labeling
ambiguity rather than inferring an additional missing review round. Its
SHA256 is `52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245`.
No new substantive concern is added by the supplied copy. An editor decision
has not been provided, but is not required to map all supplied reviewer
comments. `response_letter_round2.md` is an author response, not a reviewer
source. See `continuation_20261006/REVIEWER_CONTINUATION_PLAN.md`.

Allowed dispositions follow the protocol: `CLOSED_BY_EVIDENCE`,
`CLOSED_BY_CLAIM_REDUCTION`, `REQUIRES_EXPERIMENT`, or `BLOCKING`. Evidence
closure and manuscript integration are separate: the manuscript files remain
unchanged, so claim reductions below still need to be implemented after the
scientific evidence gate.

The claim-level evidence authority and supersession map is recorded in
`next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`; its source-hash and
reference checks pass. This bookkeeping pass does not close the human,
novelty, seam, or paper-wide reconstruction gates.

## Reviewer 1

| ID | Recorded concern | Current evidence / limitation | Disposition now | Paper closure still required |
|---|---|---|---|---|
| R1.1 | Visible purple/color shifts, repeated patterns, full-object quality; compare unmodified and fixed-scale baselines; show unseen baked views and seams. | GT-only 24-object visual audit found material/color mismatch in 18/24 and detail loss in 21/24. Stored N=20 GLBs now have a sampler-conformant base-color evaluation, but LLH results are metric-dependent; human answers are absent and four no-UV objects remain outside 3D coverage. | `REQUIRES_EXPERIMENT` | Complete the locked human study; report GLB-native N=20 results by endpoint, state the four-object exclusion, and avoid a full-PBR or human-fidelity claim. |
| R1.2 | The 0.96 dB main-adapter gain was not tested on the disjoint 276-object set; same-protocol held-out comparison requested. | A read-only strict-276 Core-7 re-evaluation gives GC3−GFL FG-PSNR +1.207771 dB (nominal object-bootstrap 95% CI [+1.116967,+1.294989], 259/276 favorable); all seven metric directions favor GC3 versus GFL. Against GFH, the comparison is mixed: GC3−GFH is −1.214235 dB FG-PSNR but +0.725229 dB Full-PSNR and +0.001229 Full-SSIM; five of seven metric directions favor GFH. These are nominal unadjusted paired intervals. The GC3−GFL pair was not a registered primary Core-7 contrast, and the legacy GFL/GC3 input-tensor hash chain and common-runner identity are not fully verifiable. FRESH_CONFIRM_B is a disjoint N=150 cohort for registered LLH contrasts; it does not confirm C3. | `CLOSED_BY_CLAIM_REDUCTION` only if the final paper states the strict-276 results as retrospective same-cohort supplements; they are not new independent confirmations. | Remove any claim that the old pooled +0.96 dB was independently confirmed. If strict-276 is reported, disclose its retrospective status, metric trade-off, nominal unadjusted intervals, and provenance limits. Do not substitute LLH for C3. |
| R1.3 | Texture variation diagnostics do not establish faithful texture; distinguish high-frequency variation from fidelity. | The visual archive and texture-complexity analysis bound the evidence but cannot establish human-perceived material fidelity. No responses exist. | `REQUIRES_EXPERIMENT` | Report variation separately from fidelity and complete the locked human study before making a human-fidelity claim. |
| R1.4 | CI crossing zero is not equivalence; Edge-SSIM trade-off must be reported or supported by a margin. | The V3 decision records no registered equivalence margin for `gen_linear` and preserves metric-specific outcomes. No new non-inferiority margin is introduced. | `CLOSED_BY_CLAIM_REDUCTION` | Keep paired intervals and the Edge-SSIM trade-off; avoid equivalence/non-inferiority language. |
| R1.5 | FAC experiments are difficult to reproduce; code release encouraged. | FAC is reported as a negative extension. Campaign hashes and a sanitized package exist, but full clean-clone/paper-wide reconstruction and portable archive closure remain incomplete. | `REQUIRES_EXPERIMENT` | Complete the clean-clone artifact reconstruction and make the implementation/results traceable in the final availability package. |

## Reviewer 2

| ID | Recorded concern | Current evidence / limitation | Disposition now | Paper closure still required |
|---|---|---|---|---|
| R2.1 | Contribution may be schedule selection for an existing adapter rather than a substantial method; CAI may formalize a selected schedule. | B and E1 do not establish a unique winner. E2 supports a bounded deep+middle static-scale effect on a reused 48-object subset. A3b has no three-layer dose common support. *Scheduled Style Injection* is published in the [CVPR 2026 NTIRE proceedings](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf) and schedules StyleID and geometric ControlNet strength across depth and denoising time. CAI remains descriptive, not predictive. | `BLOCKING` for contribution-readiness judgment; no invalidity implied. | After human/evidence disposition, compare the contribution explicitly with SSI and reassess it in the final reviewer pass. Limit novelty to MVPainter-specific residual/cap semantics, object heterogeneity and conditioning-interface evidence; this may still be too incremental for the venue. |
| R2.2 | CAI interpretation may be post hoc. | No prospective CAI prediction test exists; the current CAI decision is `DESCRIPTIVE_ONLY`. | `CLOSED_BY_CLAIM_REDUCTION` | Retain only as descriptive vocabulary or remove from the core contribution. |
| R2.3 | Cross-backbone validation is the largest generality gap. | MV-Adapter covers 98/99 planned objects and has no corrected global interaction in its tested range. MVDiffusion adds a separate 75-object negative/mixed boundary: its CPBlock interpolation trades structure/color metrics against texture error. These are different cohorts and conditioning interfaces; neither is a matched architecture experiment. | `CLOSED_BY_CLAIM_REDUCTION` | Report MV-Adapter and MVDiffusion separately as tested interface boundaries. Do not pool scores, infer architecture causality, or claim universal transfer/zero interaction. No third backbone is justified by the present evidence. |

## Reviewer 3 and user-designated second-round coverage

| Source | Recorded issue | Disposition now | Paper closure still required |
|---|---|---|---|
| Reviewer 3 supplied comments | The review states that the revision looks good for publication; no separate actionable concern is listed. | No issue recorded in either supplied copy. | This favorable review does not waive R1/R2 evidence requirements. |
| User-designated Round-2 reviewer source | `/4T/CXY/MV-Painter/第二轮审稿意见.txt` supplied and compared with the archived review; substantive concerns coincide. | `CLOSED_BY_EVIDENCE` for source availability and mapping only. | All recorded R1/R2 concerns remain subject to the evidence and manuscript dispositions above; no assertion about unprovided future rounds. |

## Cross-cutting reviewer risk

The strongest remaining risks are human-perceived fidelity and the paper's
novelty after schedule superiority is withdrawn. E1 and E2 have completed with
integrity PASS, but their estimates are conditional on a fixed 48-object B
subset and three seeds; E2 does not vary time. The stored N=20 GLB base-color
evaluation is complete; the new LLH human study is pre-collection, strict N=24
3D scope is unsupported, and the paper has not been rewritten to provisional
`NARRATIVE_D`. The strict-276 GC3−GFL estimate is a retrospective supplemental
comparison, not an independent confirmation. Accordingly, this matrix is
pre-rewrite and does not pass the final reviewer gate. See
`FINAL_SCIENTIFIC_READINESS_20261006.md`,
`next_stage_20261006/NARRATIVE_DECISION_MAP.md`, and `FINAL_ADVERSARIAL_REVIEW.md`.
