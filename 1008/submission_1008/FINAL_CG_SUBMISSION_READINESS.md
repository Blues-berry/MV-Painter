# C&G 1008 Final Submission Readiness

**Captured:** `2026-10-09T07:21:54Z` UTC  
**Package state:** `AUTHOR_REVIEW_READY / DRAFT`  
**Journal submission:** not made  
**Author submission approval:** `NO`  
**Main base at final-package preparation:** `8cf02b797c5d467db764d05ea4940937c207fe96`  
**Verified package-delivery commit:** `4035771fb6459dc6c3aa51897ef77ea43d66b426`; local and `mvpainter/main` matched at 2026-10-09T07:20:48Z UTC. The final readiness/package-metadata closeout commit SHA is supplied in the completion handoff.

## Scientific narrative

The manuscript retains Timestep-Conditioned Adapter Scaling (TCAS) as a task-specific, training-free inference intervention on the existing GeoTex-Adapter residual. C3 `(1.25, 2.50, 1.25)` is not presented as a universally optimal or dose-matched schedule. In Fresh C's matched 300-object image-space comparison, C3 minus GFL FG-PSNR is `+0.522352 dB` (object-bootstrap 95% CI `[+0.404160, +0.640669]`). GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. C3/GFL deep and middle cumulative applied scales differ (`82.5` vs `62.5`), so the contrast does not isolate timing alone.

The separate stage-placement follow-up favors temporal L–L–H over C3 on all six formal endpoints. C3 minus Fixed FG-PSNR is `+0.502875 dB`; C3 minus temporal L–L–H is `−0.177084 dB`. This supports limited time-position sensitivity, not a schedule optimum. Texture-variation metrics are not described as texture fidelity. Fresh C is 2D image-space evidence and does not establish material, seam, PBR, or 3D texture quality.

## Second-round reviewer status

| Point | Status | Paper/response treatment and remaining boundary |
|---|---|---|
| R1.1 — visual artifacts and 3D texture fidelity | `PARTIAL` | Figures 4–5 show full-object context plus shared ROIs and adverse examples. The appearance embedding controls chroma in four selected development objects; Fresh B cache/source alignment is a plausible, unproven contributor. C1 passed numeric but failed the locked visual gate, including a faint cyan/blue rim. B2 completed 8 generations (4 objects × 6 views), reproduced baseline 4/4, but failed the numeric repair gate (mean `+0.172906`, 95% CI `[−0.204353,+0.681015]`, one of four improved) and showed no clear visual correction. No independent Fresh B repair validation, valid Fresh C bake, seam, PBR, or native-default adapter result exists. No validated color repair is claimed. |
| R1.2 — matched held-out evaluation | `ADDRESSED WITH LIMITS` | Fresh C N=300 is internally matched and disjoint from development/evaluation cohorts; strong GFH and Generic Linear counter-results are reported. It does not numerically reproduce historical `+0.96 dB`; Core-7 stays retrospective Supplement evidence with runner/input identity caveats. |
| R1.3 — texture metrics | `ADDRESSED WITH LIMITS` | Variation proxies are not fidelity measures; historical 3AFC remains subjective preference only. |
| R1.4 — paired uncertainty | `PARTIAL` | Object-bootstrap intervals and C3–GFH Edge-SSIM trade-off are reported. There is no prespecified non-inferiority margin, so no equivalence/non-inferiority claim is made. |
| R1.5 — FAC reproducibility/code | `PARTIAL; FIRST-ROUND RESULT RETAINED` | Historical negative result is retained with the 1,200 vs 1,706 configuration-list gap and missing run-bound seed/output manifest. No new run or public-release claim. |
| R2.1 — methodological contribution | `PARTIAL; EDITORIAL NOVELTY RISK` | TCAS is compared with SSI, but scheduling is not claimed as a general new algorithm. Journal-level sufficiency of task-specific novelty remains for the editor. |
| R2.2 — CAI selection argument | `ADDRESSED BY WITHDRAWING CAI CLAIM` | CAI selector/proposition/proof/optimality claim removed. TCAS, C3 definition, and historical development record remain. |
| R2.3 — cross-backbone inference | `NOT FULLY ANSWERED` | The invalid production additive-bootstrap `p=0.6523` inference is withdrawn. Exploratory object-cluster robust Wald results do not survive four-metric Holm correction; they do not prove absence of interaction. MV-Adapter and MVDiffusion probes use different interfaces/runners; matched cross-backbone generalization remains unestablished. |
| R3 | `ACKNOWLEDGED` | Positive assessment thanked; no technical request or experiment invented. |

The second-round response and paper are internally consistent, and page locations below were checked against the final PDFs. Exact verbatim authentication of the second-round reviewer export remains incomplete: the retained review PDF is labeled as initial-submission comments. The response follows the recorded second-round requirements matrix; the provenance limit remains explicit.

## Delivered sources and build verification

- Active manuscript: [`1008/manuscript/revision_01549_restored/manuscript_1008.tex`](../manuscript/revision_01549_restored/manuscript_1008.tex), SHA-256 `9ffa845eff67d22ec75fbf1c135967fa1d8057bc7c4b13ad44b7c8c1a9ea55bb`.
- Active Supplement: [`1008/manuscript/revision_01549_restored/Supplementary_1008.tex`](../manuscript/revision_01549_restored/Supplementary_1008.tex), SHA-256 `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`.
- Response source: [`1008/review/Response_to_Reviewers_1008.md`](../review/Response_to_Reviewers_1008.md), synchronized with the author-review copy; response PDF is five pages.
- Package directory: [`1008/submission_1008/`](./); private GitHub [main package folder](https://github.com/Blues-berry/MVPainter/tree/main/1008/submission_1008).
- Main PDF: 13 pages, SHA-256 `29e48af0348377bd45f887a3be662937c83857a58aee67af70c12727c22df6d5`.
- Marked-up manuscript: 13 pages, SHA-256 `3c78161c31d68163007ea8f337c06b8259ad90fb96d39a789958974ff23447d5`.
- Supplement PDF: 11 pages, SHA-256 `8bc53b24ef4b43a420d40356e8f91daca5137852c6aab7cbda418932f8c5b898`.
- Response PDF: 5 pages, SHA-256 `c9cebb9dc8198ec9077d36f3dcf1dad084a9b064793bce9678303228a28d96a0`; author-review DOCX SHA-256 `0cbd727f360bd8df865738ccdbd14aab6fdd18ec6706a78c8c431a65465bfe96`. The assembled package DOCX is generated from the same Markdown and is covered by the package manifest/checksum.
- LaTeX source ZIP: 44 entries, 32,009,054 bytes, CRC `OK`, SHA-256 `fcfecf9787b087296bd922301f59953d445795815ba4b7253aee9e4bff74c37c`. It excludes raw/generated data and contains the active manuscript and Supplement byte-for-byte.
- Clean extraction builds of manuscript/Supplement/marked-up output passed at 13/11/13 pages. Each included script runs pdfLaTeX twice; unresolved references from pass one are resolved in pass two, and extracted text matches delivered PDFs. Build detail: [`SOURCE_PACKAGE_BUILD_CHECK.md`](Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md).
- Main manuscript pages: Tables 3–4 p. 7; stage analysis p. 8; R1.1 limitations pp. 8–9; Figures 4–5 pp. 11–12. Supplementary Figure S1 p. 9. Traceability is in `Author_Review/REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv`.

The Codex built-in LaTeX compiler could not locate platform standard directories. The included project scripts and clean extracted source builds succeeded; editor-native compilation is not certified.

## Final gates

`MAIN_SINGLE_EDITING_AUTHORITY = PARTIAL`  
`ALL_RELEVANT_BRANCH_CONTENT_REVIEWED = YES`  
`UNIQUE_VALUABLE_SOURCES_ACCOUNTED_FOR = YES`  
`PENDING_117_DISPOSITIONS_RESOLVED_OR_EXPLICITLY_BLOCKED = YES`  
`BULK_EXPERIMENT_DATA_PRESERVED = YES`  
`UNSAFE_MERGES_AVOIDED = YES`  
`SCIENTIFIC_CLAIMS_CONSISTENT = YES`  
`REVIEW_RESPONSE_MATCHES_PAPER = YES`  
`LATEX_BUILD_PASSED = YES`  
`PRIVATE_MAIN_SYNCED = YES`  
`SUBMISSION_APPROVED = NO`

`MAIN_SINGLE_EDITING_AUTHORITY` remains `PARTIAL` until the author opens `/4T/MV-Painter-main` in the editor and verifies the `main` branch. The delivery commit SHA is given in the completion handoff because a report cannot contain the Git SHA of the commit that contains its own final contents.

## Author checks before any upload

1. Verify author names/contact information, title page, acknowledgements/funding, and declaration of interests carried from 0907.
2. Approve the cover letter, highlights, graphical abstract, and title page, all still `DRAFT`.
3. Confirm current manuscript ID/editor instructions and whether the 0907 conference attachment, graphical abstract, or demo media is required.
4. Review R1.1 open 3D/color-fidelity risk, R2.1 novelty risk, R2.3 cross-backbone gap, and second-round review-source provenance.
5. No journal submission has been made. `SUBMISSION_APPROVED=NO`.
