# Figure asset provenance for the 1008 revision

## Main figure source

Main Figures 4 and 5 were rebuilt from existing Fresh C RGB outputs. No GPU inference was launched. For each selected UID, the reference render and method outputs use target view 0; fixed-low GFL, fixed-high GFH, C3, and Generic Linear outputs are traced to the same Fresh C cohort and run manifests. The primary and addendum manifests pin the same frozen checkpoint SHA-256 0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0 and runner SHA-256 e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3.

The figure builder extracts the saved view-0 tile from each method-level six-view PNG, composites the transparent reference on white, applies the same fixed pixel ROI to every method for that UID, and marks that ROI in the full-object context. It does not alter method colors, contrast, sharpness, or texture. Crops use uniform resampling only. The original source figures are unchanged.

FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv records each image path and SHA-256, object UID, view, method, checkpoint, runner, seed policy, input tile bounds, shared ROI bounds, per-method crop pixel hashes, source result and run-manifest hashes, and final PNG/PDF output hashes. The accompanying builder is build_fresh_c_qualitative_figures.py. The external Fresh C image archive is not copied into this revision or uploaded as a bulk dataset.

## Third-party model credits

The rights ledger FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv records the selected Fresh C model assets as CC Attribution (CC BY 4.0), with publication-figure use permitted when attributed. The full credit lines appear in Supplementary Table S1 and are summarized in FIGURE_ASSET_CREDITS.csv.

| Figure panel | UID | Model | Creator | Source | License |
|---|---|---|---|---|---|
| Fig. 4(a) | c76ac44df995482185077da81939b306 | Building 03 | Shalmon | [Sketchfab](https://sketchfab.com/3d-models/c76ac44df995482185077da81939b306) | CC BY 4.0 |
| Fig. 4(b) | d0e116a62bfc4cdd9edf60671073b306 | Boat Low Poly Game Ready | INinja | [Sketchfab](https://sketchfab.com/3d-models/d0e116a62bfc4cdd9edf60671073b306) | CC BY 4.0 |
| Fig. 5(a) | 0571e6db30c84b1593bc55a8e145a430 | Octaèdre | Segolene Delamare | [Sketchfab](https://sketchfab.com/3d-models/0571e6db30c84b1593bc55a8e145a430) | CC BY 4.0 |
| Fig. 5(b) | 06fa4974f8cd4d4ea792e98fa1521457 | Cube 01 | b0rF4x | [Sketchfab](https://sketchfab.com/3d-models/06fa4974f8cd4d4ea792e98fa1521457) | CC BY 4.0 |

The 01549 source figures remain byte-identical under `1008/manuscript/source_01549/`. `1008/audits/01549_fig4_fig6_vs_fresh_c_layout_review_20261009.pdf` pairs original Fig. 4 / Fig. 6 with the new Fresh C figures. The private GitHub branch is for author review; it is not a journal submission or public asset release.

## Historical color-failure panel in main-text Figure 6

The current Figure 6 asset, `figures/fig8_color_failure_01549.pdf`, is byte-identical to `1008/manuscript/source_01549/fig4.pdf` (SHA-256 `0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620`). The panel-level object/run mapping could not be recovered, and the underlying model/source asset and its publication/redistribution rights have not been independently verified. The manuscript labels it as an archival illustration of the historical failure, not as Fresh C evidence or a quantitative estimate. Keep it flagged for author rights/provenance confirmation before public release or journal submission; remove or replace it if that confirmation cannot be obtained.

## Adapter baseline distinction

Fresh C No Adapter sets the adapter scale to zero. In the MVPainter wrapper, an unset scale field applies the geometry residual without a scale multiplier. No Adapter therefore differs from the active native-default adapter path. Fresh C has no separate output for that default-active path; the R1.1 unmodified-pipeline visual comparison remains unresolved.
