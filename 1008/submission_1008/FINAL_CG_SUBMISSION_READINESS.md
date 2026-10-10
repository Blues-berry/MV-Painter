# C&G 1008 author-review readiness

**Captured:** 2026-10-10 · **Package state:** `AUTHOR_REVIEW_READY / DRAFT` · **Journal submission:** not made · **Approval:** `SUBMISSION_APPROVED=NO`

**Starting main baseline:** `815ab0f70bf408e2d3e2a1b76ce366ec5829c41f`.

## Scientific position

TCAS is presented as a task-specific way to request, apply, and measure geometry-residual strength in one multi-view texturing pipeline. Fresh C supports a bounded C3−GFL FG-PSNR gain of `+0.522352 dB` (N=300; 95% object-bootstrap CI `[+0.404160,+0.640669]`), while GFH and Generic Linear have stronger means on all four reported endpoints. The applied deep/middle sums differ (`82.5` vs. `62.5`), so that comparison does not isolate timing. The separate post-inspection strict-276 analysis favors temporal L–L–H on six endpoints but does not match realized residual dose.

The paper withdraws CAI's selector/proof/optimality claim and acknowledges SSI as prior layer/time scheduling work. Its remaining contribution is an empirical, graphics-task-specific control characterization. A retrospective 76-object MV-Adapter layer/time panel adds metric-dependent sensitivity evidence. The MVDiffusion 75-object panel remains on a compatibility base and was not rerun on its native mirror. Its raw L-LLH−G-FL CIEDE2000 difference is +1.373 [+.418,+2.375], indicating higher color error under L-LLH; the archived −1.373 was improvement-coded. Within P5, only FG-LPIPS has a pointwise interval excluding zero, favoring G-LLH; all 30 intervals are unadjusted. The full raw A−B table is in Supplementary Table S12. These probes do not establish matched cross-backbone transfer. Color, baked 3D/PBR, and native-default evidence also remain incomplete; no repair or broad schedule law is claimed.

The A3b map is retained as response heterogeneity under the tested interventions. Its former `0/2,250` common-support result and probe-24 development calibration compared raw $L_2$ values across feature groups with different spatial dimensions and unlogged channel counts; they do not establish cross-layer dose support, equal-dose targeting, or lack of support. The recorded scales remain tested settings. Supplementary S4 and the author-review audit report per-entry correction magnitudes descriptively, without treating them as an equal-dose intervention.

## Reviewer status

The source-verified item-by-item closure, evidence identity, page locators, response coverage, and residual limits are recorded in `Author_Review/FINAL_REVIEWER_CLOSURE_MATRIX.md`.

| Issue | Status |
|---|---|
| R1.1 color and 3D fidelity | Partial; failure-enriched color analysis, no validated repair or valid Fresh C bake/seam/PBR result. |
| R1.2 matched comparison / R1.4 uncertainty | Addressed with bounds; counter-results and dose difference reported; no equivalence claim. |
| R1.3 texture fidelity | Addressed with limits; variation and preference are distinguished from fidelity. |
| R1.5 FAC | Partial; 1,706/1,200 list mismatch and incomplete run binding disclosed. |
| R2.1 contribution | Partial; editorial novelty risk remains against prior scheduling work. |
| R2.2 CAI | Addressed by withdrawing its selector, proof, and optimality claim. |
| R2.3 cross-backbone | Open; the 76-object MV-Adapter panel is retrospective and the MVDiffusion native-mirror check covers one object only. The probes remain interface-specific, not matched transfer. |
| R3 | Acknowledged; no technical request inferred. |

## Deliverables and build state

- Main manuscript: 16 pages. Marked-up copy: 16 pages. Supplement: 16 pages. Reviewer response: 4-page PDF plus editable DOCX. Risk/experiment decision table: 1-page landscape PDF.
- Working-tree and clean ZIP extraction builds passed for the manuscript, Supplement, and marked-up PDF. Clean-build extracted text matches the review copies; no unresolved citations or cross-references remain. The build record, exact hashes, and page review are in [`Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md`](Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md).
- The deterministic clean source archive contains 70 members, includes the selected Figure 6 and its frozen selection record, plus Figure 1's source-derived thumbnail crops and provenance record, and excludes experiment JSON, checkpoints, GLBs, and caches. The separate author-review package includes hash-audited cross-backbone and CPU-only applied-budget preflight snapshots; the preflight validates schedule arithmetic only, and its GPU-idle gate failed before inference.

## Open author actions

1. The response page references have been refreshed and checked against the current four-page PDF. The exact local CAG-D-26-00962 review text is retained in `Author_Review/Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt`; its “Initial submission” header is reconciled with the author-confirmed round map.
2. Check Figure 6 attribution and the response's updated page references. The active panel is a licensed, identity-traced Fresh C example; the unrecoverable historical panel remains only in the authenticated 01549 baseline.
3. Decide whether the task-specific empirical contribution meets the journal's novelty threshold and review the remaining R1.1/R2.3 limitations.
4. Verify carried-forward author details, funding, conflict declaration, current manuscript ID, and any portal-specific upload requirements.

## Final gates

`SCIENTIFIC_EVIDENCE_FREEZE = YES`  
`REVIEWER_RESPONSE_READY = YES, WITH EXPLICIT PARTIAL/OPEN ITEMS`  
`MANUSCRIPT_BUILD_PASSED = YES`  
`SUBMISSION_PACKAGE_COMPLETE = YES`  
`SUBMISSION_READY = NO`  
`SUBMISSION_APPROVED = NO`

“Build passed” refers to the repository's LaTeX scripts and clean-archive rebuilds. It does not imply author approval, authenticated reviewer wording, or journal submission. No GPU experiment was launched.
