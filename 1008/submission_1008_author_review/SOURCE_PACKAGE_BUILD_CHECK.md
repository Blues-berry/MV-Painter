# 1008 clean-source package and build check

**Captured:** 2026-10-09 05:31 UTC  
**State:** `AUTHOR_REVIEW_READY`; journal submission not made; `SUBMISSION_APPROVED=NO`.

## Source identity

- Active manuscript TeX and author-review/package copies are byte-identical; SHA-256: `7286a2652a983a8099c5e038ee56aaf719e6c977944a528fc6b9a858f118a8b2`.
- Active Supplement TeX and author-review/package copies are byte-identical; SHA-256: `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`.
- Both TeX files in `LaTeX_Source_1008.zip` were checked byte-for-byte against the active sources. The archive has 44 entries, passes ZIP CRC verification, and contains no `.json`, `.npz`, checkpoint, or `.glb` members.
- Source ZIP SHA-256: `4ae0ff7b720419de1a62851189aa1d8f2da9f958ca2368ddde27dad1d2d13ed5` (32,008,507 bytes).
- Authenticated 01549 TeX SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.
- Authenticated 01549 source ZIP SHA-256: `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`.

## Current review PDFs

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 13 | 3,950,994 | `37096ad1893f9b557a18bc7e1a95a8aa8ca9fdfed43a4c3fc4d0f8cc01f8caf8` |
| `Marked-up_Manuscript_1008.pdf` | 13 | 3,965,037 | `3f2e2c87c372ce9ef60d5ac4ccb90649aaeb077bc09bdac4ea7ba401239d4740` |
| `Supplementary_1008.pdf` | 11 | 4,036,330 | `b1fb25cf24f0e65ee152897ff0045c120428f892aaf5c69dba2a2b59f879bc0f` |
| `Response_to_Reviewers_1008.pdf` | 5 | 45,451 | `922ca00ee4896b3b76532a9ff5bea894aea4a06f21091b2ef2a087ef0b5b8fef` |
| `Manuscript_with_Response_1008.pdf` | 18 | 4,015,579 | `48b4a88d47d1f083c70f0c8911e16661e2ef56e69daf390109705567b219fd2e` |

## Clean extraction and content checks

- Extracted the source ZIP into an empty temporary directory and rebuilt the manuscript, Supplement, and marked-up comparison with the included scripts. All three builds passed: 13, 11, and 13 pages.
- Extracted PDF text matches the packaged PDFs after whitespace and line-wrap normalization. Binary hashes vary between builds because PDF metadata is regenerated.
- Build logs contain no unresolved citations/references or fatal LaTeX errors.
- Verified the main-text stage-placement direction: temporal L–L–H outperforms C3 on all six formal endpoints; the reversed statement is absent. The reviewer response omits the invalid `p=0.6523` bootstrap inference and reports the exploratory robust-Wald results with Holm correction.
- Main manuscript Figures 4–5 are on pp. 11–12. Supplementary Figure S1 is on p. 9; Supplementary Tables S3–S13 and response references were checked against the built PDF page numbering. Page references are recorded in `REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv`.
- Rendered and checked the Fresh C figure pages and Supplementary Figure S1. Figures remain illustrative; no valid Fresh C bake, seam, or PBR result is claimed.

## Review-source provenance note

The retained `final/round2/coordination/reviewer_materials/CAG-D-26-00962-reviews.txt` and `.pdf` were checked on the unified, surgical, color, V3, and round-two evidence branches; both blobs are identical across 23 local branch refs (TXT SHA-256 `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5`; PDF SHA-256 `fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb`). The PDF explicitly labels the comments as initial-submission reviews dated 14/24/28 September 2026. They are not the second-round R1/R2/R3 export. The current response uses the itemized second-round requirements and evidence recorded in the 1008 reviewer reanalysis and requirement matrix. Exact verbatim second-round source-text authentication remains incomplete and is flagged in the final acceptance report.

## Limits and author checks

- Fresh C is a matched 300-object image-space comparison on a controlled-retraining checkpoint; it is not a numerical reproduction of the historical 01549 `+0.96 dB` result.
- The selected figures are examples, not a failure-prevalence estimate. No native-default adapter output, valid Fresh C bake, seam, PBR, or matched cross-backbone test is available.
- CAI's selector/proof/optimality claim is withdrawn; TCAS remains the retained method. The task-specific novelty contribution remains an editorial risk.
- Verify the title page, author names/contact, funding and acknowledgements, interests declaration, current editor instructions, and whether the 0907 conference attachment, graphical abstract, or demo media is required. Cover letter, highlights, graphical abstract, and title page remain `DRAFT`.
