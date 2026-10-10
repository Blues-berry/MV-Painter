# 1008 final author-review build and source-package check

**Build captured:** 2026-10-10 09:30 UTC · **Figure 1 visual redesign:** 2026-10-10 · **State:** `AUTHOR_REVIEW_READY / DRAFT` · **Submission approval:** `NO`

## Source identity and archive

- Active and author-review manuscript TeX are byte-identical (SHA-256 `d977250d6b3452cad2415cf1374cfc30dbc68ab453207a35d4fb3b16e6830b3d`). Active and author-review Supplement TeX are byte-identical (SHA-256 `df35b089f9c967e75dccb1e81719a48068459bdaddd6e56b1009909f479f1ee1`).
- `LaTeX_Source_1008.zip`: 70 members, 37,612,104 bytes, SHA-256 `3ac8e2e259c43c7df95e230677358f650613c1e54527631fbaafed6a6b1db808`. ZIP CRC passes. It includes the active TeX, build scripts, Figure 1 crop assets/provenance, and source dependencies; it excludes experiment JSON, arrays, checkpoints, GLBs, compiled manuscript PDFs, and build caches.
- The source ZIP was extracted into an empty temporary directory. The included scripts rebuilt the main paper, Supplement, and marked-up manuscript at 16 pages each; whitespace-normalized `pdftotext -layout -nopgbrk` output matches the author-review PDFs for all three finalized documents.
- `submission_1008/SUBMISSION_FILE_MANIFEST.csv` has 121 payload entries, including `Author_Review/FINAL_REVIEWER_CLOSURE_MATRIX.md`. The exact second-round reviewer source is classified as `AUTHOR_REVIEW_MATERIAL`; it is stored under `Author_Review/Reviewer_Source/` and is not a journal upload file.
- The upload `Figures/` directory contains exactly the eight files referenced by the active manuscript and Supplement. Figure 1 was redesigned using illustrative thumbnails from 01549 while the authenticated source remains unchanged. All current package checksums pass.

## Author-review artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 16 | 3,310,194 | `9526900173262d20d09187531760e62a9599a3e37c218a44cd63cd977ee89366` |
| `Marked-up_Manuscript_1008.pdf` | 16 | 3,333,973 | `87dc02f5b6069dc25f25168b17125f54051d9bae6633b9266c9c1a6491c29785` |
| `Supplementary_1008.pdf` | 16 | 1,675,578 | `8a79b8eb2bb30a5a3cfaba73831b7eca392b05e07674eb012fc94e694291b59b` |
| `Response_to_Reviewers_1008.pdf` | 4 | 35,363 | `fe58168c82744503d8151002f2c875716bee62d63a9b8400a894e22e84c15c60` |
| `Response_to_Reviewers_1008.docx` | — | 15,246 | `6aab8033bcbc23fc111ea78ca1baba4c610146c824d398e20a33f7c31db4aa1c` |
| `LaTeX_Source_1008.zip` | — | 37,612,104 | `3ac8e2e259c43c7df95e230677358f650613c1e54527631fbaafed6a6b1db808` |

Figure 1 asset:

- `figures/fig1_tcas_control.pdf`: SHA-256 `cd6f30c496bce8116f11ac41f4f5a3a0a489351d004624483cf5d41dfa2dbbe5`.
- Builder `scripts/build_tcas_control_figure.py`: SHA-256 `1eb3df2587f930446ba4c131772e0c1e38a7aa796ec57c973ac2a1ed5a62f2c7`.
- Thumbnail extractor `scripts/extract_fig1_visual_assets.py`: SHA-256 `2e1a4650bbd028498a6629114c5b969b5d38db84f250ccfc2e52ab3154d24e31`.

## Page and evidence review

- Figure 1 was checked in its final page-4 placement. It restores the original reference/geometry/target-view examples, shows the GeoTex residual and cap-aware TCAS gate in separate paths, distinguishes the requested schedule from the Fresh C shallow applied cap, and marks projection/baking as unevaluated context. The withdrawn FAC extension is absent. The 70-member source ZIP was extracted to an empty directory: manuscript, Supplement, and marked-up outputs rebuilt at 16 pages each, with `pdftotext -layout -nopgbrk` output matching the author-review PDFs; ZIP CRC passes. The archived input/target thumbnails' underlying source and credit still require author confirmation. Table S12 contains all five comparisons × six metrics with raw A-minus-B differences and pointwise intervals.
- The response DOCX and PDF in the submission package are byte-identical to the author-review copies and derive from the same response Markdown.
- The final locators are recorded in `1008/audits/1008_RESPONSE_LOCATOR_AUDIT.md` and `FINAL_REVIEWER_CLOSURE_MATRIX.md`. The response is four pages; its R2.3 answer and A3b withdrawal fit on pp. 3–4.
- The exact local plain-text second-round reviewer source is `Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt` (SHA-256 `52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245`). It matches the supplied attachment after CRLF normalization. The separate PDF text extraction has SHA-256 `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5` and includes pagination/extraction artifacts. The original “Initial submission” header is reconciled with the author-confirmed round map identifying the review as the second round of 01549.
- MVDiffusion correction: all 525 condition-object rows and six scheduled 75-object files were reconciled; the raw A-minus-B bootstrap reports five contrasts × six endpoints. In P1, L-LLH minus G-FL CIEDE2000 is `+1.373021` (95% CI `[+0.418244,+2.374678]`, higher error under L-LLH). Within P5, only FG-LPIPS excludes zero (`−0.001371 [−0.002642,−0.000141]`), favoring G-LLH. The old lower-is-better signs and erroneous P5 sentence are explicitly flagged; original analysis outputs remain preserved as historical records.
- A3b's former `0/2,250` overlap and probe-24 calibration compare raw L2 values across layer groups with different spatial dimensions and unlogged channel counts. The manuscript withdraws the cross-layer dose-support and equal-dose interpretations; only response heterogeneity under tested settings and descriptive per-entry magnitudes remain.
- Main, Supplement, and marked-up builds have no unresolved citations or cross-references. Nonfatal geometry/underfull-box and `latexdiff` Unicode warnings remain; page inspection showed no clipping. No GPU experiment was launched.

## Open author actions

- Check Figure 6 caption and attribution against the rights record.
- Verify carried-forward author metadata, funding, competing-interest statement, current manuscript ID, and portal requirements.
- Review remaining editorial novelty risk and the open R1.1/R2.3 limitations before any submission.

`SUBMISSION_APPROVED=NO`; no journal submission has been made.
