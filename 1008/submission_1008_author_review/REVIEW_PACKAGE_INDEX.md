# 1008 author-review package index

**State:** `AUTHOR_REVIEW_READY / DRAFT` · **Historical base:** 01549 submitted 2026-09-07 · **Submission approval:** `NO`

## Core review files

- Revised manuscript: `Manuscript_1008.tex` and 16-page `Manuscript_1008.pdf`.
- Marked-up manuscript against 01549: 16-page `Marked-up_Manuscript_1008.pdf`.
- Supplement: `Supplementary_1008.tex` and 16-page `Supplementary_1008.pdf`.
- Reviewer response: synchronized Markdown source, editable DOCX, and page count recorded in the build check.
- Figure 1 (main p. 4) is an author-generated vector schematic that shows the TCAS cap-aware scale gate on the GeoTex residual path. Figures 4–7 appear with their related development/evaluation text (main pp. 8–13); none is deferred beyond the references. Figure 6 uses a licensed, hash-traced Fresh C case; the unrecoverable historical panel is absent from the active package.
- `01549_TO_1008_CHANGELOG.md`: concise statement of retained, revised, removed, and added scientific claims.
- `Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt`: exact local plain-text reviewer source, retained for author traceability; it is not part of the journal upload files. SHA-256: `52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245`.
- `UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.md` and its one-page PDF: current reviewer risks and gated E1–E3 decisions.
- `LaTeX_Source_1008.zip`: deterministic clean source archive with the active figures, figure manifests, frozen Figure 6 selection row, and original 01549 baseline sources. Its manuscript and Supplement TeX match the active sources byte-for-byte.
- `Cross_Backbone_Evidence_20261010/`: hash-audited MV-Adapter 76-object and MVDiffusion 75-object evidence snapshot with chronology, interface, and native-mirror limits.
- `MVDIFFUSION_RAW_DIRECTION_CORRECTION_20261010/`: raw A-minus-B recomputation of all five MVDiffusion paired contrasts, all 30 bootstrap intervals, panel means, and input hashes. It accompanies the preserved improvement-coded archive output and explicitly corrects both the CIEDE2000 sign and the old P5 FG-LPIPS direction statement.
- `Applied_Budget_Preflight_20261010/`: read-only snapshot of the CPU schedule-arithmetic preflight and failed GPU-idle gate; it records no inference result and does not establish matched realized dose.
- `SOURCE_PACKAGE_BUILD_CHECK.md`: build results, page counts, hashes, evidence spot-checks, and open author actions.

## Main evidence boundaries

- Residual_Norm_Dimension_Audit_20261010/: CPU-only audit of the A3b raw-L2 feature-dimension issue, its withdrawn cross-layer support interpretation, and a descriptive per-entry magnitude sensitivity. It records no inference and supports no equal-dose or causal claim.
- A3b's former 0/2,250 common-support statistic and development equal-dose calibration compared raw L2 values across feature groups with different dimensions; cross-layer dose support is unresolved. The manuscript retains only response heterogeneity under the tested interventions.

- Fresh C is a matched 300-object image-space comparison on a controlled-retraining checkpoint. C3−GFL FG-PSNR is `+0.522352` dB (95% CI `[+0.404160,+0.640669]`); GFH and Generic Linear have stronger means on all four displayed endpoints. Applied deep/middle sums differ (`82.5` vs. `62.5`), so this is not a timing-only contrast.
- Strict-276 temporal L–L–H is a separate post-inspection result and is favored over C3 on six endpoints, but realized residual dose is unmatched. Fresh B/A3b and Core-7 remain retrospective sensitivity evidence.
- The 76-object MV-Adapter layer/time panel is retrospective and interface-specific; its 30 pointwise intervals are unadjusted. The MVDiffusion compatibility-base panel has a one-object native-mirror check, but was not rerun on the mirror. Neither establishes matched second-backbone transfer.
- In the MVDiffusion panel, raw L-LLH−G-FL CIEDE2000 is +1.373 [+0.418,+2.375], so color error is higher under L-LLH; the archived −1.373 was improvement-coded. In P5, raw G-LLH−G-LHL FG-LPIPS is −0.001371 [−0.002642,−0.000141], favoring G-LLH; the old report text naming G-LHL is incorrect. The corrected full table is Supplementary Table S12 and the 525-row recomputation is included above.
- Color diagnostics document a failure-enriched set and no validated repair. No valid Fresh C bake, seam/PBR result, native-default comparison, or new Fresh C human-preference result is claimed.
- CAI's selector, proof, and optimality claim are withdrawn. TCAS is framed as a graphics-task-specific empirical control contribution; general scheduling novelty remains an editorial risk.
- Recent human responses remain internal-only. No participant-level material is included.

## Author checks before any submission

- Response page references were refreshed and checked against the current PDFs. The exact local CAG-D-26-00962 review source is retained under `Reviewer_Source/`; its “Initial submission” header is reconciled with the author-confirmed round map.
- Check the Figure 6 caption and attribution against the review PDF. The current panel is licensed and identity-traced; the legacy asset remains only in the authenticated 01549 baseline.
- Review final editorial suitability. This package is for author review only; no journal submission has been made and `SUBMISSION_APPROVED=NO`.
