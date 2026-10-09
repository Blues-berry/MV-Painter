# 1008 clean-source package and build check

**Captured:** 2026-10-09T07:12:46Z UTC  
**State:** `AUTHOR_REVIEW_READY`; journal submission not made; `SUBMISSION_APPROVED=NO`.

## Source identity

- Active manuscript and author-review TeX are byte-identical; SHA-256 `9ffa845eff67d22ec75fbf1c135967fa1d8057bc7c4b13ad44b7c8c1a9ea55bb`.
- Active Supplement and author-review TeX are byte-identical; SHA-256 `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`.
- Source ZIP has 44 entries, passes CRC, and contains no JSON, NPZ, checkpoint, or GLB members; SHA-256 `fcfecf9787b087296bd922301f59953d445795815ba4b7253aee9e4bff74c37c` (32,009,054 bytes).
- ZIP manuscript and Supplement members match the active TeX byte-for-byte (`9ffa845eff67d22ec75fbf1c135967fa1d8057bc7c4b13ad44b7c8c1a9ea55bb`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`).
- Authenticated 01549 TeX SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.
- Authenticated 01549 source ZIP SHA-256: `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`.

## Current review PDFs

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 13 | 3,952,228 | `29e48af0348377bd45f887a3be662937c83857a58aee67af70c12727c22df6d5` |
| `Marked-up_Manuscript_1008.pdf` | 13 | 3,966,148 | `3c78161c31d68163007ea8f337c06b8259ad90fb96d39a789958974ff23447d5` |
| `Supplementary_1008.pdf` | 11 | 4,036,330 | `8bc53b24ef4b43a420d40356e8f91daca5137852c6aab7cbda418932f8c5b898` |
| `Response_to_Reviewers_1008.pdf` | 5 | 35,462 | `c9cebb9dc8198ec9077d36f3dcf1dad084a9b064793bce9678303228a28d96a0` |

- Response Markdown SHA-256: `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; DOCX SHA-256: `0cbd727f360bd8df865738ccdbd14aab6fdd18ec6706a78c8c431a65465bfe96`.

## Clean extraction and content checks

- Extracted the source ZIP into a new empty temporary directory and ran all three included build scripts: manuscript (13 pages), Supplement (11 pages), and marked-up manuscript (13 pages). Each script ran pdfLaTeX twice; the second pass had no unresolved citations or references, and each extracted PDF text matched its delivered counterpart after whitespace normalization.
- The one-pass unresolved-reference messages in first-pass LaTeX output are expected; the checked second pass resolves them. All three commands exited successfully and wrote their PDFs.
- The response PDF was regenerated from the synchronized Markdown using Pandoc/XeLaTeX; no missing-glyph warning remains. Its five-page location map still points to the built manuscript and Supplement pages.
- Main manuscript: Tables 3–4 p. 7; stage analysis p. 8; R1.1 limitations pp. 8–9; Figures 4–5 pp. 11–12. Supplementary Figure S1 is p. 9. Reviewer locations are listed in `REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv`.
- Checked the stage-placement direction, R1.1 visual/numeric gate distinctions, and R2.3 inference language against the extracted PDFs. The invalid production additive-bootstrap p=0.6523 is absent; the exploratory robust-Wald analysis and Holm-adjusted values remain explicitly bounded.
- Rendered Fresh C figure pages and Supplementary Figure S1 were visually checked. Figures remain illustrative; no valid Fresh C bake, seam, PBR result, or native-default Adapter comparison is claimed.

## Review-source provenance note

The retained `final/round2/coordination/reviewer_materials/CAG-D-26-00962-reviews.txt` and `.pdf` are identical across 23 local refs (TXT SHA-256 `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5`; PDF SHA-256 `fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb`). The PDF identifies them as initial-submission reviews dated 14/24/28 September 2026, not the authenticated second-round R1/R2/R3 export. The current response uses the itemized second-round requirements and evidence recorded in the reviewer reanalysis; exact verbatim second-round source authentication remains incomplete and is flagged in final readiness.

## Limits and author checks

- Fresh C is a matched 300-object image-space comparison on a controlled-retraining checkpoint, not a numerical reproduction of the historical 01549 `+0.96 dB` result. The selected figures are examples, not a failure-prevalence estimate.
- The appearance-embedding pathway controls chroma in four selected development cases. A cache/source alignment discrepancy is plausible but not a complete causal explanation. C1 passed its numeric gate but failed its locked visual gate; B2 completed eight generations but failed its frozen numeric gate. No independent Fresh B repair validation was run.
- No native-default adapter output, valid Fresh C bake, seam, PBR, or matched cross-backbone test is available. CAI optimality is withdrawn; TCAS novelty remains task-specific and subject to editorial judgment.
- The Codex built-in LaTeX compiler reported unavailable platform standard directories. The project build scripts and clean extracted ZIP builds above passed with the installed pdfLaTeX environment.
- Verify the title page, author names/contact, funding and acknowledgements, interests declaration, current editor instructions, and whether the 0907 conference attachment, graphical abstract, or demo media is required. Cover letter, highlights, graphical abstract, and title page remain `DRAFT`.
