# V4 continuation build verification

The sole manuscript source was PR #1 HEAD c3017645. Its four PDF hashes and source hashes matched the committed V4 manifest before edits. The current V4 continuation has a revised Figure 2/3 presentation, small supported narrative changes, current source/credit/video clarifications and a regenerated original-submission marked manuscript. Its PDFs intentionally differ from c3017645.

Current builds: main 13 pages; Supplement 71; response 5; marked manuscript 21. All manuscript and Supplement numeric table blocks are byte-identical to c3017645. The original GeoTex timing primary is retained as Table 7, and the two bake LPIPS primaries remain in Table 5. `quality_review/FROZEN_CONTENT_CHECK_V4.json` and the final hash manifest record this validation.

Marked-source authentication reproduced the committed c3017645 marked TeX byte-for-byte from the authenticated original 01549 source, then regenerated against the final V4 TeX. Figures/tables are atomic in CFONT markup; `marked/CHANGES_FROM_01549_V4.diff` supplies the complete expanded-source change record.
