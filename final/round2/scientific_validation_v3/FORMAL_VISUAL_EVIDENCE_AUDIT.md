# FORMAL_VISUAL_EVIDENCE_AUDIT — Experiment D

Objects: the 24-object set frozen in visualization_24.txt BEFORE any method
metric was computed (GT-only stratification: texture tercile x coverage
tercile, geometry-tercile spread within cells, seed 20261002; see
stratification_summary.json). No "representative" imagery is used anywhere.

Artifacts: formal_qualitative_archive/ —
  * panel_<i>_<uid>.png: per object, GT (unique6 views 0,15,12,16,13,14) +
    no_adapter + native GFL/GFH/GC3 + LFM-EXACT + LHL + LLH
  * contact_sheet_24.png: full 24-object contact sheet
  * archive_manifest.json (selection rule, condition list, missing count = 0)

Provenance: all prediction panels are byte-frozen outputs of the formal
campaigns (predictions/<condition>/<uid>.png, shared latents per object,
latent seed 42) — identical reference draw across conditions.

Post-metric figure sets (strongest win / median / strongest loss) were NOT
generated: any such selection would require a rank rule and disclosure; the
pre-frozen stratified set was preferred to keep the archive strictly
selection-free. If needed later, the rank rule must be pre-registered and
disclosed in captions.

## Manual review (2026-10-05)

I inspected all 24 frozen panels at full panel resolution, comparing the GT
views with no-adapter, GFL, GFH, GC3, LFM-EXACT, LHL, and LLH outputs. The
panel set was fixed by the existing GT-only stratification; no outcome-based
selection or rank-based sampling was added. Per-object observations are in
`FORMAL_VISUAL_PANEL_CLASSIFICATION.csv`.

Recurring visible issues are:

- **Color/material mismatch:** many saturated, cool, green, or dark reference
  surfaces become muted tan/brown generated surfaces. This is conspicuous on
  the blue, green, red, and neutral-gray examples.
- **Fine-detail loss:** repeated texture, narrow stripes, and small surface
  variations are softened or replaced by coarse mottling.
- **Thin/small-part readability:** narrow rails and small disconnected
  elements are less clear in a subset of the panels.

Coarse object form is often recognizable. The side-by-side schedule columns
do not show a stable, clearly visible winner across this stratified set; the
qualitative review does not justify a schedule-ranking claim. The color and
detail failures are present across schedule conditions and are consistent
with the quantitative warning that image metrics do not establish faithful
material reproduction. These panels are 2D generated views; they do not assess
UV seams or unseen-view baking, which remain covered separately by Experiment
F.

This is a descriptive audit of the fixed 24-object set, not a population
estimate and not a blinded human-preference study. Any human study must use a
separate preregistered sampling and ranking protocol.

## Closure update — rank examples and texture-rich sheet (2026-10-05)

The earlier note that ranked sheets were not generated is historical. A
deterministic FG-PSNR ranking rule was frozen in
`FORMAL_VISUAL_RANK_PROTOCOL.md` before extracting ranks. The resulting
strongest-win, median-effect, strongest-loss, and GT-Laplacian top-six sheets
are in `formal_visual_evidence/`; the sample and its original GT-only order
were not changed. These are explicitly metric-ranked illustrations, not
independent evidence or population estimates. The consolidated result and
limitations are in `FORMAL_VISUAL_EVIDENCE_REPORT.md`.
