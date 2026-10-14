# Author handoff — V4

## Authoritative version

Continue from this directory for all future edits. It is the V4 source of truth in the GitHub submission. Do not use V1, V2 or V3 as the editing base; those remain historical versions outside this package. Submit only the V4 manuscript, Supplement and reviewer response from this directory.

## Current files and layout

- Main manuscript: `FINAL_V4_MANUSCRIPT.pdf` / `.tex` (13 pages; final reference [41] on p. 13).
- Supplement: `FINAL_V4_SUPPLEMENTARY.pdf` / `.tex` (71 pages; S35 on p. 58, S36 on p. 59).
- Response: `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` and matching sources in `review/` (5 pages).
- Marked manuscript: `FINAL_V4_MARKED_MANUSCRIPT.pdf` and `marked/FINAL_V4_MARKED_MANUSCRIPT.tex` (20 pages).
- Figure 3 selection: `visual_candidates/VISUAL_SELECTION_REPORT_V4.md`, `BAKE10_CANDIDATE_RANKING_V4.csv`, and `VISUAL_SELECTION_MANIFEST_V4_PUBLIC.csv`.
- Figure credits and frozen statistic validation: `figures/BAKED_ASSET_CREDITS.csv`, `figures/FIGURE_ASSET_CREDITS.csv`, and `figures/FIG6_DATA_VALIDATION_V3.json`.
- Final build record and package hash manifest: `BUILD_VERIFICATION_V4.md` and `alignment/SUBMISSION_MANIFEST_V4.json`.

## V4 visual and scientific handoff

Figure 3 uses one rights-cleared best-case Bake10 object (UID `238ff3e41c964655b83aa9c8770cc766`), lowest on both existing 11-view FG-LPIPS summaries among the seven cleared display candidates: Fixed Mean 0.05895328; Late-high 0.05848895. Treat it only as an explicitly post-outcome example. The source projection is raw view 000; the three bake panels share held-out unseen raw view 004 and a common crop. The figure does not establish prevalence or general material fidelity. Selected source pixels, display crops and a sanitized UID/license/hash/camera record are included. Unselected candidate pixels and the full atlas remain in the internal archive.

Actual source PNGs and the renderer setting are 512×512. The upstream per-render manifest field says 1024×1024 for these files; this discrepancy is recorded in the layout/science report. Do not silently change that record.

The original Figure 6 primary remains `Middle − mean(Early, Late)` for GeoTex Fresh C: −0.0338775 dB, 95% CI [−0.117170, +0.051422], p = 0.432378. No experiment result or statistic was recalculated, and no GPU run was made. R1's material-fidelity concern remains. R2.1 remains a partial response: task-specific empirical evidence, without claiming a new general scheduling method.

## Rebuild

From this package directory, run `python3 build_v4_manuscript.py`, `bash review/build_response.sh`, `python3 marked/build_marked_pdf.py`, and `python3 alignment/build_submission_manifest.py`. The submitted selection ranking is frozen in its public files. Regenerating it requires the separate internal candidate archive, which is intentionally not included with the public submission.
