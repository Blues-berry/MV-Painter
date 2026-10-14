# Final V4 build verification

The authoritative V4 text revision started from PR #1 HEAD `11006e003842b25976e20cafd51a7970770f269f` on `codex/cg-final-v4-20261014`. The official manuscript, response and marked source were rebuilt from that continuation. Current page counts are: main 13, Supplement 71, response 5, marked manuscript 20.

The official main text now uses the revised abstract, six-paragraph Introduction, implementation-aware method framing, a three-part baked-appearance section, the study-specific native-interface comparison, a compressed historical sensitivity section, and a four-theme Discussion. The Supplement source and all seven numeric table bodies are unchanged from the starting V4 baseline. `quality_review/FROZEN_CONTENT_CHECK_V4.json` records seven unchanged table bodies, unchanged numeric table sources and Supplement source, and zero inference or GPU runs.

The marked manuscript was regenerated against the authenticated original submission source. The baseline identity and current target, marked source, PDF and full expanded-source diff hashes are recorded in `quality_review/MARKED_MANUSCRIPT_CHECK_V4.json` and `marked/MARKED_DIFF_SCOPE_V4.json`.

The final PDF page audit is in `FINAL_LAYOUT_AND_SCIENCE_CHECK_V4.md` and `TABLE_1_TO_7_LAYOUT_AUDIT.md`. Figure 2 is on p7 and Figure 3 on p9; the actual A/B Figure 3 and four/three-row Figure 2 pages are retained in `quality_review/`. Build success is reported separately from the independent scientific readiness judgment.
