# 1008 final author-review build and source-package check

**Captured:** 2026-10-10 05:47 UTC · **State:** `AUTHOR_REVIEW_READY / DRAFT` · **Submission approval:** `NO`

## Source identity and archive

- Active and author-review manuscript TeX are byte-identical (SHA-256 `4dfb499c6115e17263e5f5bcb597b0db73167ad1a8f8882580da3efd694169f5`). Active and author-review Supplement TeX are byte-identical (SHA-256 `df35b089f9c967e75dccb1e81719a48068459bdaddd6e56b1009909f479f1ee1`).
- `LaTeX_Source_1008.zip`: 63 members, 35,933,889 bytes, SHA-256 `4498eed902121127d190e3032e24c7af35be5ec1611c08d72b3e40bdb42538d4`. ZIP CRC passes. It includes the active TeX, build scripts, figures and source dependencies; it excludes experiment JSON, arrays, checkpoints, GLBs, generated PDFs, and caches.
- The source ZIP was extracted into an empty temporary directory. The included scripts rebuilt the main paper, Supplement, and marked-up manuscript at 16 pages each. Whitespace-normalized `pdftotext -layout -nopgbrk` output matches the author-review PDFs for all three documents.
- `submission_1008/SUBMISSION_FILE_MANIFEST.csv` has 121 payload entries. The exact second-round reviewer source is classified as `AUTHOR_REVIEW_MATERIAL`; it is stored under `Author_Review/Reviewer_Source/` and is not a journal upload file.

## Author-review artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 16 | 2,001,189 | `9446a5c69356e3847246aadd8b89e39514d73f88c50df4de85e5d89738a1cae0` |
| `Marked-up_Manuscript_1008.pdf` | 16 | 2,024,582 | `7c6cc0a2bea85b73fca0e8f45a62aaae348f1d1518e325df3969ccfdbfd0c1bd` |
| `Supplementary_1008.pdf` | 16 | 1,675,578 | `db0188400f520a47c97d935124c806f7b74dd3e5e3f28437ca67c9b697764fb6` |
| `Response_to_Reviewers_1008.pdf` | 4 | 35,874 | `b6535a72fa09f0622781809ecd8e0dbf38b8ab318874848279e2a97dde0a8203` |
| `Response_to_Reviewers_1008.docx` | — | 15,176 | `ccccae4f476a8c7a64355ed920ea954032f5f2e06e529d6aad8cbf5e84228705` |
| `LaTeX_Source_1008.zip` | — | 35,933,889 | `4498eed902121127d190e3032e24c7af35be5ec1611c08d72b3e40bdb42538d4` |

## Page and evidence review

- All pages were reviewed in contact sheets; enlarged checks covered the main A3b withdrawal (p. 10), Cross-Interface Table 8 (p. 14), references (p. 16), Supplement S4 (p. 6), raw MVDiffusion Table S12 (p. 11), FAC/retrospective tables (p. 14), color diagnostics (p. 15), response p. 4, and marked-up references (p. 16). No pages are blank, and no clipping was seen. Table S12 contains all five comparisons × six metrics with raw A-minus-B differences and pointwise intervals.
- The final locators are recorded in `1008/audits/1008_RESPONSE_LOCATOR_AUDIT.md`. The response is four pages; its R2.3 answer and A3b withdrawal fit on p. 4.
- The exact local plain-text second-round reviewer source is `Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt` (SHA-256 `52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245`). It matches the supplied attachment after CRLF normalization. The separate PDF text extraction has SHA-256 `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5` and includes pagination/extraction artifacts. The original “Initial submission” header is reconciled with the author-confirmed round map identifying the review as the second round of 01549.
- MVDiffusion correction: all 525 condition-object rows and six scheduled 75-object files were reconciled; the raw A-minus-B bootstrap reports five contrasts × six endpoints. In P1, L-LLH minus G-FL CIEDE2000 is `+1.373021` (95% CI `[+0.418244,+2.374678]`, higher error under L-LLH). Within P5, only FG-LPIPS excludes zero (`−0.001371 [−0.002642,−0.000141]`), favoring G-LLH. The old lower-is-better signs and erroneous P5 sentence are explicitly flagged; original analysis outputs remain preserved as historical records.
- A3b's former `0/2,250` overlap and probe-24 calibration compare raw L2 values across layer groups with different spatial dimensions and unlogged channel counts. The manuscript withdraws the cross-layer dose-support and equal-dose interpretations; only response heterogeneity under tested settings and descriptive per-entry magnitudes remain.
- Main, Supplement, and marked-up builds have no unresolved citations or cross-references. Nonfatal geometry/underfull-box and `latexdiff` Unicode warnings remain; page inspection showed no clipping. No GPU experiment was launched.

## Open author actions

- Check Figure 6 caption and attribution against the rights record.
- Verify carried-forward author metadata, funding, competing-interest statement, current manuscript ID, and portal requirements.
- Review remaining editorial novelty risk and the open R1.1/R2.3 limitations before any submission.

`SUBMISSION_APPROVED=NO`; no journal submission has been made.
