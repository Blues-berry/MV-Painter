# 01549 revision continuity acceptance

> **Superseded historical snapshot.** This acceptance record describes an earlier 10-page restoration state, including an intermediate Fig. 1 and omitted 3AFC/FAC results. It is not the current second-round submission. The current 1008 package is based on the official 2026-09-07 post-first-round 01549 materials and is listed in `submission_1008_final/README_LaTeX_Source_1008.txt`, `SUBMISSION_BUILD_REPORT.md`, and `01549_TO_1008_CHANGELOG.md`.

**Date:** 2026-10-08

**Clean-checkout target:** `fb0b24cba203549c28e6287996ad76f4dff61a79` (`paper: document restored 01549 content and figure continuity`)

**Clean checkout:** `/4T/tmp/01549-clean-checkout-20261008`

**Active manuscript:** `1008/manuscript/revision_01549_restored/final_0903.tex`

This report separates source continuity, structural accounting, and the scientific limits that remain. It does not infer manuscript identity from a matching title, a successful LaTeX build, or an unchanged original file alone.

## Acceptance gates

| Gate | Result | Evidence and scope |
|---|---|---|
| `ORIGINAL_SOURCE_VERIFIED` | **PASS** | The protected TeX is SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`; it is byte-identical to ZIP member `final_0903.tex`. The submission ZIP is `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`. The two submitted-PDF copies match at SHA-256 `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da`. |
| `ACTIVE_SOURCE_PROVENANCE_VERIFIED` | **PASS** | The active main TeX is regenerated from the authenticated ZIP member; a separate temporary regeneration was byte-identical. Active main, supplement, and response hashes are recorded in `BASELINE_LOCK.json`. |
| `UNJUSTIFIED_STRUCTURAL_DELETION_COUNT` | **0** | All 33 ledger rows have explicit disposition and reason. Every `REMOVE` row has evidence/review basis and justification; every `MOVE` row identifies its destination and limitation. |
| `ORIGINAL_FIGURE_DISPOSITION_COMPLETE` | **PASS — 7/7** | Each original figure has a disposition, source hash, final mapping or explicit removal, and active-asset hash where applicable. The seven-page PDF contains actual rendered original/current images or a removal card, not only TeX path names. |
| `ORIGINAL_TABLE_DISPOSITION_COMPLETE` | **PASS — 9/9** | Original Tables 1–9 are individually mapped. Historical tables are marked as such; Table 9 is retained in Supplement S9 with its different adapter/run lineage and incomplete provenance stated. |
| `ORIGINAL_ARGUMENT_CHAIN_PRESERVED` | **QUALIFIED** | The paper again follows the submitted fixed-scale question → C3 development choice → matched evaluation structure. Fixed-scale and 24-object probe materials remain historical diagnostics because their current row-level records are incomplete; they are not presented as newly verified confirmation. Unsupported conclusions are withdrawn. |
| `REVISION_CLAIMS_TRACEABLE` | **PASS WITH SCOPE LIMITS** | New numerical claims map to the Claim Ledger and run-specific authorities. There is no public code/data reproduction package, so external readers cannot rerun every object-level analysis from the submitted files alone. |
| `RESPONSE_LINE_REFERENCES_VALID` | **PASS** | Every cited main-text line range in the response was checked against the visible line-number gutters in the current compiled PDF. Supplement page/table references were checked against the current PDF. The clean-checkout main and supplement have identical extracted text and 45-dpi page rasters to the committed builds. |
| `CLEAN_REBUILD_PASS` | **PASS — local TeX Live** | A detached clean checkout at the target commit passed baseline verification and rebuilt the 15-page original, 10-page restored main, and 8-page Supplement. The final active logs have no unresolved citations or references. Minor layout warnings remain, noted below. |

## Rebuild record

The detached checkout had an empty Git status before verification. The source ZIP member and protected `source_01549/final_0903.tex` were verified again there. All 43 entries in the `HISTORICAL_1008_NINE_PAGE_CANDIDATE.sha256` manifest passed. The frozen main TeX, supplement, response, and both R2.1 PDFs match the files still present under `revision_1008/` in the original worktree. Rebuilding changed only the two compiled PDF copies in the detached checkout; those clean-build outputs were copied back and are included with this acceptance commit.

The independently compiled original produced 15 pages. Its `pdftotext -layout` output is byte-identical to the submitted PDF, and all 15 page rasters are pixel-identical at 45 dpi. The clean-checkout original build PDF SHA-256 is `7bd7e858a620fbcae0e9e154c8a48d52f8a26977ed298f4c18ef4beb917e92ff`; it differs bytewise from the submitted PDF because of PDF metadata.

The active clean-checkout builds produced:

- Main manuscript: 10 pages, SHA-256 `d55d47494db61d319ff50330bbe19f22734894f37121847d08ed2dc355ba964b`.
- Supplement: 8 pages, SHA-256 `d9e2e297d2612c537a81365ca7e89d155e11b57b2ec74d596d06b8f937faf091`.
- Seven-figure internal comparison: 7 pages, SHA-256 `ce5c82b4879e2103fd1ffc8f8942acb898a28bc6d980effa10bfe7bccf87eee0`.

The clean-checkout main log retains two overfull boxes of 0.78 pt and 1.02 pt in the front matter, plus underfull layout warnings. The Supplement has underfull table/credit lines but no overfull boxes or unresolved citations/references. These are layout warnings, not compilation failures.

The built-in Codex LaTeX compiler was also called on both active `.tex` files. It returned `Unable to find standard directories for platform` for each, before providing LaTeX diagnostics. The local clean-checkout TeX Live builds above are the successful compilation evidence; the built-in compiler limitation is environmental.

## Content and visual continuity

`ORIGINAL_CONTENT_DISPOSITION.csv` contains 17 section/content groups, 7 figures, and 9 tables. The final count is 33 rows; seven content items are explicitly removed and two are moved, each with recorded evidence/review reasons. The page-count change from the submitted 15-page paper to the restored 10-page main is explained by those documented structural decisions, not a page target: unrecoverable texture-proxy and pooled tables, CLIP-IQA/human-preference claims, FAC results, and non-equivalent adapter details leave the main text or move to Supplement. The fixed-scale plots and C3 development record remain in the main paper with historical-evidence labels.

The actual seven-page figure review is [`01549_original_vs_current_figures_internal.pdf`](forensics_R2_1_20261008/01549_original_vs_current_figures_internal.pdf). Its SHA-256 manifest is [`RESTORED_FIGURE_ASSET_MANIFEST.csv`](forensics_R2_1_20261008/RESTORED_FIGURE_ASSET_MANIFEST.csv). The active Figure 1 preserves the original pipeline composition and projection/baking context while omitting FAC. An earlier FAC-containing draft was separately archived and is explicitly not used by the active source.

The restored main, supplement, and response hashes are:

- Main TeX: `eda3ee762ca0484481722ec5f1dda968be9ba990a628c9ac967fc1d660f715d7`
- Supplement TeX: `dc9f887bb48219a3b4b5f65b42e18339abf5592125ba9bf81bd1bebdbcf89037`
- Response draft: `bef00fbce490f384ba0e67d92804af79dde2cce6e20998d379ecadf849c9128a`

## Scientific items that remain open

The continuity and build gates pass, but they do not satisfy every reviewer request. Fresh C includes historical development objects; no probe-disjoint confirmation on the main adapter is available. The strict-276 placement study uses a different adapter/run lineage and is post-inspection, so it is not represented as a replacement holdout. No valid new bake or seam result exists; the historical N=20 result is limited to mixed unlit base-color views. SSI is direct prior art for broad layer/time scheduling, and the contribution remains task/interface-specific with a substantial editorial novelty risk. These limitations are stated in the paper, response, and [adversarial review](01549_ADVERSARIAL_REVIEW.md).

## Phase commits

- `b8ddc50b` — authenticate source, freeze the nine-page candidate, and record version/root-cause evidence.
- `739aa5e5` — restore the active manuscript from the authenticated 01549 source; add the active supplement, response draft, and guarded build entry points.
- `fb0b24cb` — commit the structural/figure dispositions, visual comparison, and adversarial review.
- The current acceptance record and the clean-checkout-built PDF copies are committed as the final validation phase.

The historical `revision_1008/` candidate was not staged or committed by these phases. Its three TeX/response files and both R2.1 PDFs remain byte-identical to the frozen archive.
