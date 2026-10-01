# Baking Seam / Cross-View Consistency Report (final_audit_20261001, Phase 4)

Date: 2026-10-01. Script: `scripts/audit_bake_consistency_20261001.py` (CPU + EGL
offscreen rendering; no new baking, no GPU inference). Data:
`bake_consistency/bake_consistency_per_asset.csv`, `bake_consistency_summary.json`.
Cohort: the existing 12-object stratified bake (`main_adapter_baking/cpu_bake_12{,_layerwise}`),
8 method variants × 12 objects = 96 textured GLBs. **Descriptive only** — no
inferential statistics; the cohort is a stratified case study, not a population sample.

## 1. What is measured

1. **UV-seam color discontinuity**: 3D-adjacent surface points whose UV charts
   disagree (glTF vertex splits) are enumerated; for each seam edge, matching
   parameters on both chart sides are sampled 2 texels inside their charts and
   compared with CIEDE2000 (up to 4000 edges/object, 16 samples/edge, both normal
   directions). `seam/baseline` normalizes by the mean CIEDE2000 of adjacent in-chart
   texel pairs (ordinary texture variation). Lower = more color-continuous seams.
2. **Cross-view reprojection consistency**: the mesh is rendered from 8 fixed
   orthographic cameras (vertex-colored mesh — see script docstring; the
   view-to-view difference cancels the interpolation convention). A vertex visible in
   both views of a pair defines a surface-point correspondence; the compared colors
   are the rendered colors at the vertex's projected pixel in each view. Reported:
   mean and p90 ΔE00 over 56 ordered view pairs.

## 2. Results (12-object means)

| method | seam ΔE00 | seam/baseline | cross-view mean ΔE00 | cross-view p90 |
|---|---:|---:|---:|---:|
| c3 (base bake) | 10.31 | 4.57 | 9.79 | 25.86 |
| fixed_high (base) | 11.54 | 5.87 | 11.35 | 29.95 |
| fixed_low (base) | 10.11 | 4.26 | 9.59 | 25.35 |
| no_adapter (base) | 6.85 | 2.26 | 7.56 | 20.75 |
| global_c3 (layerwise bake) | 6.31 | 2.95 | 6.96 | 17.83 |
| global_fixed_low (layerwise) | 7.32 | 2.99 | 7.59 | 19.61 |
| layer_lhl (layerwise) | 5.34 | 2.86 | 6.19 | 15.82 |
| **layer_llh (layerwise)** | **4.40** | 3.16 | **5.41** | **13.75** |

## 3. Reading

1. **layer_llh is the best of all eight variants on seam discontinuity (4.40) and on
   cross-view color stability (mean 5.41, p90 13.75)**; layer_lhl is second on both.
2. The layerwise bake family (bottom four) improves on the corresponding base-bake
   variants (top four) — e.g. global_c3 6.31 vs c3 10.31 seam ΔE00.
3. The ordering is consistent with the Core-7 texture-energy mechanism note
   (`CORE7_SAME_RUNNER_REPORT.md`): fixed_high/fixed_low over-inject high-frequency
   energy (1.54× GT at fixed-low) and show the largest seam/cross-view instability;
   no_adapter is blurriest (0.89× GT) and has the lowest seam/baseline ratio (2.26) —
   smooth outputs trivially agree across seams; layer_llh calibrates energy closest to
   GT (1.13×) and achieves the lowest absolute seam and cross-view discrepancies.
4. Per-asset values (12 objects × 8 methods) are in the CSV; extremes exist (e.g.
   obj_0083/fixed_high cross-view mean 33.98) and are retained unfiltered.

## 4. Boundaries

- 12 stratified objects: case-study descriptors only; no population claim, no
  significance test, no preference claim.
- Vertex-colored rendering for the cross-view metric (texture upload unsupported by
  the installed PyOpenGL under numpy 2); the view-to-view difference design makes the
  interpolation choice cancel, but absolute cross-view values should be read as
  render-time stability descriptors, not texture-fidelity metrics.
- Seam metric operates in texture space on the baked texture with the bake's own
  uv→texel convention; it does not measure geometric seams (mesh cracks), which are
  absent by construction (single watertight Exact-GLB mesh per object).
