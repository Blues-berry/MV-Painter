# Clean LaTeX source package and final build check

> **Historical build report:** this 2026-10-09 snapshot is superseded by [`../submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md`](../submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md), which records the current 2026-10-10 16/16/16-page build and 63-member source archive.

**Captured:** 2026-10-09T04:16:30Z UTC  
**Package state:** `AUTHOR_REVIEW_READY` (not submission-approved)

## Source identity

- Active manuscript and author-package TeX SHA-256: `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`; byte-identical.
- Active Supplement and author-package Supplement SHA-256: `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f`; byte-identical.
- Authenticated 01549 TeX SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.
- Authenticated 01549 source ZIP SHA-256: `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`.
- `LaTeX_Source_1008.zip` SHA-256: `d6cae77abcba75fa9b3617e953784ee813dbbf2160a7fd5f0c1f86a04c470401` (32,008,864 bytes); ZIP integrity passed, with no JSON members.

## Author-review PDFs

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| Manuscript_1008.pdf | 13 | 3,952,160 | `65e950d0457199d1bac0c88f4b455f61f70a38f12159fbdad9f5bb5941ccdc6e` |
| Marked-up_Manuscript_1008.pdf | 13 | 3,965,896 | `9efec4f36001d485719edc57369fc8a280e74b1f030fae1618c65cc061808a0b` |
| Supplementary_1008.pdf | 11 | 4,036,225 | `577d23b4f03416935044d6dfe7f21b809fdb6fe7158be8d8376c5cb4f8e41487` |
| Response_to_Reviewers_1008.pdf | 3 | 31,057 | `963538da8bdef6d648648b69fb6c016896f46b055be4004635098d19d5204dbb` |

## Clean extraction and visual checks

- The source ZIP was extracted into an empty temporary directory. Baseline verification passed; the main manuscript, Supplement, and marked-up comparison each compiled from the extracted package. Their page counts match the author-review deliverables.
- The author-review PDFs are the corresponding active project builds; each PDF hash matches its build output in `revision_01549_restored/build/`.
- The marked-up file highlights additions relative to authenticated 01549 and intentionally omits deleted spans to avoid carrying obsolete citation and reference text. It is a change-marked reading copy, not a redline of removals.
- Pages 11–12 of the final manuscript were rendered at normal reading scale and visually checked. Fresh C Fig. 4 and Fig. 5 show context and shared ROI crops; the Generic Linear counterexample remains visible.
- The built-in editor compiler request was attempted on the project TeX and hung beyond five minutes; it was stopped without changing files. The standalone project build and clean-extraction builds passed with no unresolved references/citations or fatal LaTeX errors.
- `python -m py_compile` passed for the selected implementation, evidence, and build scripts. Selected statistics suite: 15 passed (`test_round2_stats.py`, `test_round2_bake_metrics.py`, `test_round2_texture.py`). No GPU experiment was run.

The ZIP includes only TeX sources, build instructions/scripts, the authenticated original template/figures, and final figure assets required by the documents. It excludes experiment JSON, participant-level records, checkpoints, raw generated image collections, and caches.
