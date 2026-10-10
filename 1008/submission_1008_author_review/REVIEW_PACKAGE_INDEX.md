# 1008 author-review package index

**State:** `AUTHOR_REVIEW_READY / DRAFT` · **Historical base:** 01549 submitted 2026-09-07 · **Submission approval:** `NO`

## Core review files

- Revised manuscript: `Manuscript_1008.tex` and 16-page `Manuscript_1008.pdf`.
- Marked-up manuscript against 01549: 17-page `Marked-up_Manuscript_1008.pdf`.
- Supplement: `Supplementary_1008.tex` and 13-page `Supplementary_1008.pdf`.
- Reviewer response: Markdown, editable DOCX, and 6-page PDF.
- `01549_TO_1008_CHANGELOG.md`: concise statement of retained, revised, removed, and added scientific claims.
- `UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.md` and its one-page PDF: current reviewer risks and gated E1–E3 decisions.
- `LaTeX_Source_1008.zip`: 45-member clean source archive. Its manuscript and Supplement TeX match the active sources byte-for-byte.
- `SOURCE_PACKAGE_BUILD_CHECK.md`: build results, page counts, hashes, evidence spot-checks, and open author actions.

## Main evidence boundaries

- Fresh C is a matched 300-object image-space comparison on a controlled-retraining checkpoint. C3−GFL FG-PSNR is `+0.522352` dB (95% CI `[+0.404160,+0.640669]`); GFH and Generic Linear have stronger means on all four displayed endpoints. Applied deep/middle sums differ (`82.5` vs. `62.5`), so this is not a timing-only contrast.
- Strict-276 temporal L–L–H is a separate post-inspection result and is favored over C3 on six endpoints, but realized residual dose is unmatched. Fresh B/A3b and Core-7 remain retrospective sensitivity evidence.
- Color diagnostics document a failure-enriched set and no validated repair. No valid Fresh C bake, seam/PBR result, native-default comparison, new Fresh C human-preference result, or matched second-backbone transfer is claimed.
- CAI's selector, proof, and optimality claim are withdrawn. TCAS is framed as a graphics-task-specific empirical control contribution; general scheduling novelty remains an editorial risk.
- Recent human responses remain internal-only. No participant-level material is included.

## Author checks before any submission

- Authenticate response headings against the editor's exact second-round decision; the retained local review PDF is labeled “Initial submission.”
- Confirm Figure 6 source-asset rights or replace the archival panel. The figure is byte-identical to the historical 01549 asset, but panel mapping and underlying model rights are unresolved.
- Review final editorial suitability. This package is for author review only; no journal submission has been made and `SUBMISSION_APPROVED=NO`.
