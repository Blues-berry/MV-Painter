# 1008 final author-review build and source-package check

**Captured:** 2026-10-10 06:05 UTC · **State:** `AUTHOR_REVIEW_READY / DRAFT` · **Submission approval:** `NO`

## Source identity and archive

- Active and author-review manuscript TeX are byte-identical (SHA-256 `070338bdd40db62e1fa869b0d934534b39d85aff8fb833a2a13c96524a814e5c`). Active and author-review Supplement TeX are byte-identical (SHA-256 `df35b089f9c967e75dccb1e81719a48068459bdaddd6e56b1009909f479f1ee1`).
- `LaTeX_Source_1008.zip`: 63 members, 35,933,982 bytes, SHA-256 `5892aa2d0b0b6b71613ef6170c83b328d5975473d4054abf4bfd4970633365c4`. ZIP CRC passes. It includes the active TeX, build scripts, figures and source dependencies; it excludes experiment JSON, arrays, checkpoints, GLBs, generated PDFs, and caches.
- The source ZIP was extracted into an empty temporary directory. The included scripts rebuilt the main paper, Supplement, and marked-up manuscript at 16 pages each; whitespace-normalized `pdftotext -layout -nopgbrk` output matches the author-review PDFs for all three finalized documents.
- `submission_1008/SUBMISSION_FILE_MANIFEST.csv` has 122 payload entries, including `Author_Review/FINAL_REVIEWER_CLOSURE_MATRIX.md`. The exact second-round reviewer source is classified as `AUTHOR_REVIEW_MATERIAL`; it is stored under `Author_Review/Reviewer_Source/` and is not a journal upload file.

## Author-review artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 16 | 2,001,507 | `62d81a79d626c7fd20683f5c09b11c2234da19ac8273b54565219d773560d80f` |
| `Marked-up_Manuscript_1008.pdf` | 16 | 2,024,947 | `5ac86b8e45fc1efabd1ac6143625df13cc8ee850b495b5cd469eed1651fcd794` |
| `Supplementary_1008.pdf` | 16 | 1,675,578 | `8a79b8eb2bb30a5a3cfaba73831b7eca392b05e07674eb012fc94e694291b59b` |
| `Response_to_Reviewers_1008.pdf` | 4 | 35,363 | `fe58168c82744503d8151002f2c875716bee62d63a9b8400a894e22e84c15c60` |
| `Response_to_Reviewers_1008.docx` | — | 15,246 | `61683013e9879301d47408ed04aa86b851b7d39054ff4316b1736b40118c2ca7` |
| `LaTeX_Source_1008.zip` | — | 35,933,982 | `5892aa2d0b0b6b71613ef6170c83b328d5975473d4054abf4bfd4970633365c4` |

## Page and evidence review

- The changed main pages (Related Work pp. 1–2 and Cross-Interface Table 8 p. 14) and response p. 4 were visually reinspected; the prior full contact-sheet review of remaining pages is retained. No blank pages or clipping were seen. Table S12 contains all five comparisons × six metrics with raw A-minus-B differences and pointwise intervals.
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
