# C&G V4 continuation — authoritative submission package

Continue from the current HEAD of [PR #1](https://github.com/Blues-berry/MV-Painter/pull/1), in this directory. The only input manuscript for this revision was c3017645. Previous local V4 directories and c3017645 are historical snapshots; this remains V4, not a new manuscript version series.

Final deliverables: `FINAL_V4_MANUSCRIPT.pdf/.tex` (13 pages), `FINAL_V4_SUPPLEMENTARY.pdf/.tex` (71), `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` (5) and `FINAL_V4_MARKED_MANUSCRIPT.pdf` (21). References end on main p13; S35/S36 remain on Supplement p58/p59.

Figure 3 uses B: an input-property median Tire plus an explicitly post-outcome largest LPIPS-benefit font among seven display-cleared candidates. Actual A/B pages, four/three-row Figure 2 pages, independent scientific assessment and source checks are in `quality_review/`. Those page excerpts are author-review records, not alternate submission manuscripts. Absolute-LPIPS ranking is retained as an audit input and is not the current benefit-selection rule.

The local complete journal delivery, including separately uploaded MP4s and stills, is indexed by `JOURNAL_SUBMISSION_HANDOFF_V4.md`. The videos and complete frozen research evidence archive stay local; they are not required in this GitHub change. All source-selected pixel files needed to rebuild current figures are included.

From this directory, rebuild in order:

1. `python3 visual_candidates/build_figures_v4.py`
2. `python3 build_v4_manuscript.py`
3. `bash review/build_response.sh`
4. `python3 marked/regenerate_marked_v4.py`
5. `python3 marked/build_marked_pdf.py`
6. `python3 alignment/build_submission_manifest.py`

The original-submission TeX under marked/original_submission is an authenticated difference reference only. It is not an editing base for the manuscript. Frozen statistics have not changed; no GPU experiment or inferential recalculation was performed. Scientific scope and remaining gaps are evaluated in `quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md`, rather than inferred from compilation success.
