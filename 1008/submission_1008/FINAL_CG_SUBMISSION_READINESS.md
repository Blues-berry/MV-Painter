# C&G 1008 author-review readiness

**Captured:** 2026-10-10 · **Package state:** `AUTHOR_REVIEW_READY / DRAFT` · **Journal submission:** not made · **Approval:** `SUBMISSION_APPROVED=NO`

**Starting main baseline:** `245bcafd41d6022aa529080d5a02fc8e1fdfedff`.

## Scientific position

TCAS is presented as a task-specific way to request, apply, and measure geometry-residual strength in one multi-view texturing pipeline. Fresh C supports a bounded C3−GFL FG-PSNR gain of `+0.522352 dB` (N=300; 95% object-bootstrap CI `[+0.404160,+0.640669]`), while GFH and Generic Linear have stronger means on all four reported endpoints. The applied deep/middle sums differ (`82.5` vs. `62.5`), so that comparison does not isolate timing. The separate post-inspection strict-276 analysis favors temporal L–L–H on six endpoints but does not match realized residual dose.

The paper withdraws CAI's selector/proof/optimality claim and acknowledges SSI as prior layer/time scheduling work. Its remaining contribution is an empirical, graphics-task-specific control characterization. Color, baked 3D/PBR, native-default, and matched cross-backbone evidence remain incomplete; no repair or broad schedule law is claimed.

## Reviewer status

| Issue | Status |
|---|---|
| R1.1 color and 3D fidelity | Partial; failure-enriched color analysis, no validated repair or valid Fresh C bake/seam/PBR result. |
| R1.2 matched comparison / R1.4 uncertainty | Addressed with bounds; counter-results and dose difference reported; no equivalence claim. |
| R1.3 texture fidelity | Addressed with limits; variation and preference are distinguished from fidelity. |
| R1.5 FAC | Partial; 1,706/1,200 list mismatch and incomplete run binding disclosed. |
| R2.1 contribution | Partial; editorial novelty risk remains against prior scheduling work. |
| R2.2 CAI | Addressed by withdrawing its selector, proof, and optimality claim. |
| R2.3 cross-backbone | Open; current probes are interface-specific, not matched transfer. |
| R3 | Acknowledged; no technical request inferred. |

## Deliverables and build state

- Main manuscript: 16 pages. Marked-up copy: 17 pages. Supplement: 13 pages. Reviewer response: 6-page PDF plus editable DOCX. Risk/experiment decision table: 1-page PDF.
- Working-tree and clean ZIP extraction builds passed for the manuscript, Supplement, and marked-up PDF. Clean-build extracted text matches the review copies; no unresolved citations or cross-references remain. The build record, exact hashes, and page review are in [`Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md`](Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md).
- The clean source archive contains 45 members and excludes generated data, checkpoints, GLBs, and caches.

## Open author actions

1. Verify the response headings against the editor's exact second-round decision; the retained local PDF is labeled “Initial submission.”
2. Confirm rights/provenance for the archival Figure 6 panel or replace it. Its PDF matches the 01549 source byte-for-byte, but its panel map and source-model rights remain unverified.
3. Decide whether the task-specific empirical contribution meets the journal's novelty threshold and review the remaining R1.1/R2.3 limitations.
4. Verify carried-forward author details, funding, conflict declaration, current manuscript ID, and any portal-specific upload requirements.

## Final gates

`SCIENTIFIC_EVIDENCE_FREEZE = YES`  
`REVIEWER_RESPONSE_READY = PARTIAL`  
`MANUSCRIPT_BUILD_PASSED = YES`  
`SUBMISSION_PACKAGE_COMPLETE = YES`  
`SUBMISSION_APPROVED = NO`

“Build passed” refers to the repository's LaTeX scripts and clean-archive rebuilds. It does not imply author approval, authenticated reviewer wording, or journal submission. No GPU experiment was launched.
