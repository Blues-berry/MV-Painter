# Figure asset provenance for the 1008 revision

## Figure 1 control-path schematic

Figure 1 combines OpenAI Images conceptual artwork with reproducible SVG annotations and actual, rights-cleared Fresh C Building03 reference/maps/C3 outputs (Shalmon, CC BY 4.0; original URL in Supplementary Table S1). The generation tool's model version was not recorded. The legacy 01549 thumbnail crops are archived outside the submission package; their unverified credits no longer apply to the active diagram. `fig1_assets/FIG1_THUMBNAIL_PROVENANCE.csv` records replacement sources, hashes and display operations. The conceptual artwork is not an experimental result. AI use is disclosed in its caption and the general manuscript statement, consistent with Elsevier's explanatory-image policy (https://www.elsevier.com/en-gb/about/policies-and-standards/generative-ai-policies-for-journals). The graphical abstract uses reproducible plots/text and actual renders, without general-purpose generated image artwork.

## Main figure source

Fresh C figures in main Figures 5--7 were rebuilt from existing Fresh C RGB outputs. No GPU inference was launched. For each selected UID, the reference render and method outputs use target view 0. Figure 6 shows Reference, No Adapter, GFL, and LLH; Figures 5 and 7 show fixed-scale, C3, and Generic Linear comparisons. These outputs are traced to the same Fresh C cohort and run manifests. The primary and addendum manifests pin the same frozen checkpoint SHA-256 0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0 and runner SHA-256 e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3.

The figure builder extracts the saved view-0 tile from each method-level six-view PNG, composites the transparent reference on white, applies the same fixed pixel ROI to every method for that UID, and marks that ROI in the full-object context. It does not alter method colors, contrast, sharpness, or texture. Crops use uniform resampling only. The original source figures are unchanged.

FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv records each image path and SHA-256, object UID, view, method, checkpoint, runner, seed policy, input tile bounds, shared ROI bounds, per-method crop pixel hashes, source result and run-manifest hashes, and final PNG/PDF output hashes. For Figure 6 it also records the frozen selection ID, contrast, stratum, prior-viewing status, and non-confirmatory use; the one-row FRESH_C_COLOR_FIGURE_SELECTION.csv preserves the source freeze row and its SHA-256. The accompanying builder is build_fresh_c_qualitative_figures.py. The external Fresh C image archive is not copied into this revision or uploaded as a bulk dataset.

## Third-party model credits

The rights ledger FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv records the selected Fresh C model assets as CC Attribution (CC BY 4.0), with publication-figure use permitted when attributed. The full credit lines appear in Supplementary Table S1 and are summarized in FIGURE_ASSET_CREDITS.csv.

| Figure panel | UID | Model | Creator | Source | License |
|---|---|---|---|---|---|
| Fig. 7(a) | c76ac44df995482185077da81939b306 | Building 03 | Shalmon | [Sketchfab](https://sketchfab.com/3d-models/c76ac44df995482185077da81939b306) | CC BY 4.0 |
| Fig. 7(b) | d0e116a62bfc4cdd9edf60671073b306 | Boat Low Poly Game Ready | INinja | [Sketchfab](https://sketchfab.com/3d-models/d0e116a62bfc4cdd9edf60671073b306) | CC BY 4.0 |
| Fig. 5(a) | 0571e6db30c84b1593bc55a8e145a430 | Octaèdre | Segolene Delamare | [Sketchfab](https://sketchfab.com/3d-models/0571e6db30c84b1593bc55a8e145a430) | CC BY 4.0 |
| Fig. 5(b) | 06fa4974f8cd4d4ea792e98fa1521457 | Cube 01 | b0rF4x | [Sketchfab](https://sketchfab.com/3d-models/06fa4974f8cd4d4ea792e98fa1521457) | CC BY 4.0 |
| Fig. 6 | f6979d7ff8e54c4daf00fee46f09a139 | E5-5-2 | artsiyu | [Sketchfab](https://sketchfab.com/3d-models/f6979d7ff8e54c4daf00fee46f09a139) | CC BY 4.0 |

The 01549 source figures remain byte-identical under `1008/manuscript/source_01549/`. `1008/audits/01549_fig4_fig6_vs_fresh_c_layout_review_20261009.pdf` pairs original Fig. 4 / Fig. 6 with the new Fresh C figures. The private GitHub branch is for author review; it is not a journal submission or public asset release.

## Main-text Figure 6 and retired historical panel

The unrecoverable 01549 color-failure panel is no longer used in the active manuscript or submission package. The original PDF remains unchanged under `1008/manuscript/source_01549/fig4.pdf` (SHA-256 `0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620`) as historical source material. Its panel-level object/run mapping could not be recovered, and its underlying model/source asset and publication/redistribution rights remain unverified; it is not linked to the current quantitative diagnostic.

Current Figure 6 is `figures/fig6_color_diagnostic_freshc_context_roi.pdf`, rebuilt from saved Fresh C RGB output for UID `f6979d7ff8e54c4daf00fee46f09a139` (sample `freshc_panel_13`). It shows Reference, No Adapter, GFL, and LLH for target view 0, with one shared 256x256-coordinate ROI `(48,90,208,210)` and its full-context marker. The pre-existing sample freeze identifies the case as the lowest focal FG-LPIPS stratum for C3--GFL; it was not selected for color, had been viewed previously, and is not independent confirmation. It is an illustrative single case, not a prevalence estimate and not a reconstruction of either legacy pink-shift panel. The asset is recorded as CC BY 4.0 in the rights ledger and attributed in Supplementary Table S1. The figure PNG SHA-256 is recorded in `figures/FIGURE_ASSET_CREDITS.csv`; source tiles, crop hashes, and output PNG/PDF hashes are in `figures/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv`.

## Adapter baseline distinction

Fresh C No Adapter sets the adapter scale to zero. In the MVPainter wrapper, an unset scale field applies the geometry residual without a scale multiplier. No Adapter therefore differs from the active native-default adapter path. Fresh C has no separate output for that default-active path; the R1.1 unmodified-pipeline visual comparison remains unresolved.

## Historical C3 development plot

The 1008 Figure 4 is the 24-object C3 development probe from the submitted 01549 Figure 7. Its axes now name the displayed image-space metrics directly: FG-SSIM difference and Laplacian variance difference. Laplacian variance is a variation diagnostic, not a texture-fidelity measure. The title and axis text are regenerated by `scripts/relabel_development_probe_figure.py`; the script masks only the title and axis-label areas. Pixel comparison confirms that all raster content outside those masks, including the plotted points, markers, shading, and annotations, is unchanged. The unavailable candidate-level records prevent independent reanalysis, so the plot remains historical development evidence rather than a verified ranking or optimum.
