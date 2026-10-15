# 01549 Visual Reuse Decision

## Scope and decision

I inspected the original 01549 submitted manuscript PDF, its matching `final_0903.tex`, the archived source files `fig1.pdf`–`fig7.pdf`, and the rendered per-figure previews in `audit/01549_review/rendered/`. The source artwork can be inspected, but the figure assets do not carry an object-level provenance map.

**No 01549 figure pixels are reused as current V4 experimental evidence.** Figures 1, 4, and 6 remain available in the internal atlas as historical artwork only. Figures 2, 3, 5, and 7 are excluded from current analysis and from the revised main text because their underlying numerical inputs and experiment identity cannot be verified. Figure 1 is unchanged from the verified V3 baseline; it is not reconstructed from old artwork.

The current Fresh C and Bake10 provenance identifies a later frozen checkpoint, runner, object manifests, and camera protocols. The 01549 figure PDFs and TeX do not map their rows or plotted values to those identities. An experiment-identity match therefore cannot be established for any of the seven figures.

## Per-figure audit

| 01549 figure | What the submitted figure claims or shows | UID / target / checkpoint / runner / seed / camera / execution parameter audit | Source pixels, transformation, rights, current identity | Decision |
|---|---|---|---|---|
| 1 | Method and TCAS/FAC overview schematic. | Not applicable to generated-object rows; no source code or editable vector source is present in this archive. The diagram is not tied to a run, object UID, or camera. | The submitted figure PDF exists; no independent element-to-code map, crop history, or asset attribution is included in the supplied source. Its old description is superseded by the current V3 method diagram. | **C — historical schematic only; not reused.** |
| 2 | Uniform-scale sweep curves and structural metric trend. | The TeX describes a 50-object, 13-scale study and says the experiments share a seed and pipeline, but provides no per-object UID list, target-frame mapping, checkpoint digest, runner digest, or run/step record for the plotted values. Exact executed scales and aggregation are not independently reconstructable from the figure source alone. | `fig2.pdf` and the caption are available; a generating script and point-level source table are absent from the 01549 figure archive. No reproducible source-pixel map, crop/display parameters, or source-asset credits accompany it. | **D — do not reuse or restore the old trend as current evidence.** |
| 3 | Per-object FG-SSIM heatmap across 50 objects and 13 scales. | The caption names the sample size and scales but does not identify rows by UID, target image, camera, seed, checkpoint, runner, or exact execution settings. The matrix cannot be independently joined to a verified object-level ledger. | Only the plotted PDF is present; the 50×13 source matrix and row-order map are not in the archive. No crop or display transform source is recorded. | **D — do not reuse or infer current object-level behavior from it.** |
| 4 | Selected multi-object visual examples comparing 1.25, 2.50, and C3; the text describes progressive texture loss. | The displayed rows cannot be mapped to source UIDs, reference PNGs, training/checkpoint instance, runner, random seed, camera IDs, or rendering protocol. The image also cannot establish that its output is from the later Fresh C or Bake10 run. | Original figure PDF and raster preview are preserved, but the source image bytes and exact tile/crop coordinates are not identified. Asset creator/license attribution is not linked to the displayed rows in the archived figure package. | **C — historical illustration only; not reused.** |
| 5 | Texture-statistic ratios on 26 objects, including a selected “best-improvement” subset. | No UID denominator, per-object numerator/denominator table, target correspondence, checkpoint/runner/seed identity, or executed parameter record is shipped with the figure. The accompanying prose uses “texture loss” categories not recoverable from the graph alone. | The plot PDF exists; the source values and code used to derive the displayed ratios are absent. No source-image or asset-rights map accompanies the rows. | **D — do not reuse or revive the withdrawn texture-fidelity inference.** |
| 6 | GT, 1.25, 2.50, and C3 multi-object visual comparison. | The TeX calls the objects representative but gives no UID-to-panel map, exact target/reference image, checkpoint, runner, seed, camera ID, or rendering record for each row. The visible arrangement cannot be authenticated against a current Fresh C object or output. | The original figure PDF and preview are available; exact per-cell bytes, uniform-frame coordinates, crop parameters, and asset credits are not recorded in the source package. | **C — historical illustration only; not reused.** |
| 7 | Pareto plot for 17 variants, with a text claim that C3 occupies a favorable region. | The figure source does not provide an auditable 17-row object/variant table, underlying per-object metric values, UID mapping, or a complete checkpoint/runner/seed record. It cannot be recomputed or aligned to the current frozen matched-budget primary. | Original plot PDF exists, but data and plotting script are absent from the 01549 figure archive. The claim also conflicts with the later V3 evidence boundary, which does not support a general or optimal schedule claim. | **D — do not reuse or restore the old Pareto/optimality claim.** |

## Provenance fields checked

| Required field | Result for the 01549 figure package |
|---|---|
| Original figure bytes | `audit/01549_review/fig1.pdf` through `fig7.pdf` are present and individually hashed in `visual_candidates/VISUAL_SOURCE_INDEX.csv`. |
| Matching TeX and submitted PDF | `audit/01549_review/final_0903.tex` and `audit/01549_review/01549_submitted_manuscript_0907.pdf` are present; their hashes are recorded in the source index. |
| Per-panel source UID | Not recoverable for Figures 2–6; Figures 1 and 7 do not expose image-row identities. |
| Input reference / target image | General protocol is described in TeX, but no figure-row target path or pixel hash is mapped. |
| Checkpoint and training instance | TeX names checkpoint locations and training-pool descriptions, but the figure assets have no digest-to-run mapping. The current Fresh C/Bake10 checkpoint is not linked to them. |
| Runner / sampling configuration / executed parameter | Some paper-level parameters appear in prose; figure-specific executed run records and output-to-parameter maps are absent. |
| Camera and render protocol | A 17-view Blender protocol is described generally. Figure-level camera IDs and view-to-panel mappings are absent. |
| Crop and display transform | No source crop coordinates or reproducible figure-construction script is attached to the 01549 figure PDFs. |
| Source asset rights | No row-level creator/license mapping is attached to the 01549 image panels. Historical visual inspection is not used to claim new rights clearance. |
| Same identity as Fresh C or Bake10 | **Not verified for all figures.** No matching UID/checkpoint/runner/input/output-hash chain was found. |

## Consequence for the V4 revision

The new main figures use current, hash-indexed Fresh C and Bake10 outputs with explicit UIDs, views, run identities, and source credits. The 01549 figures remain in the local forensic atlas so their historical claims and visual appearance can be reviewed, but they contribute no current data, selected examples, effect estimates, or material-fidelity claim.
