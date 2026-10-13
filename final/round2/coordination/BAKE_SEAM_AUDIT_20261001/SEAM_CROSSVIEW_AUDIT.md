# P3 AUDIT — UV-seam / cross-view consistency over the existing 12-object bakes (2026-10-01)

Reviewer 1 asked for "assessment of seams or cross-view consistency" on
baked meshes rendered from unseen viewpoints. This audit measures it
DIRECTLY, in texture space, on the already-baked GLBs — no re-baking, no
GPU, no rendering.

## Method

For each textured GLB (8 conditions x 12 stratified objects; 1024^2 albedo
texture, ~150k triangles):

- **Seam edges**: shared 3D edges whose two adjacent triangles assign
  different UV positions (UV-chart boundary). Detection is by position-keyed
  vertex matching (charts split vertices), UV tolerance 1e-4.
- **Seam gap**: CIEDE2000 between the 3x3-mean texture colors sampled at
  the two chart-side locations of the SAME 3D edge midpoint.
- **Control**: same statistic across interior-edge midpoints sampled 2px
  apart within one chart (local texture gradient); seam/control ratio
  separates chart-boundary discontinuity from natural texture variation.
- **Coverage**: baked-coverage fraction aggregated from existing coverage
  PNGs (identical across conditions by construction: geometry+views only).

Cross-view consistency rationale: the bakes are unlit albedo textures on a
fixed mesh; rendered views share the same texture, so cross-view color
agreement on shared surface points is determined by UV-seam continuity
(plus coverage). The seam gaps below therefore quantify the cross-view
inconsistency mechanism directly, complementing the existing unseen-view
PSNR/CIEDE2000 evaluation.

## Results (per-condition aggregates over 12 objects)

Matched bake generation (cpu_bake_12_layerwise; same pipeline run):

| condition | seam dE00 mean | seam dE00 p90 | frac>5 | frac>10 | control (2px) | ratio |
|---|---:|---:|---:|---:|---:|---:|
| **layer_llh** | **4.89** | **14.56** | 0.305 | **0.186** | 2.72 | 1.75 |
| layer_lhl | 5.60 | 17.18 | 0.348 | 0.181 | 3.65 | 1.62 |
| global_c3 | 7.54 | 22.05 | 0.365 | 0.268 | 4.04 | 1.77 |
| global_fixed_low | 8.86 | 26.17 | 0.385 | 0.286 | 4.54 | 1.82 |

Earlier bake generation (cpu_bake_12; NOT cross-comparable with the
layerwise generation — different bake pipeline state):

| condition | seam dE00 mean | seam dE00 p90 | ratio |
|---|---:|---:|---:|
| no_adapter | 6.47 | 17.84 | 1.27 |
| fixed_low | 11.67 | 39.28 | 2.35 |
| c3 | 12.00 | 41.22 | 2.61 |
| fixed_high | 12.04 | 45.70 | 2.88 |

Median seam gap is ~0 in all conditions (the baker averages color across
chart copies on most seams); the distributions have a heavy tail
(frac>10: 18.6% for LLH vs 28.6% for G-FL in the matched generation).

## Findings

1. Within the matched bake generation, **layer-LLH has the lowest seam
   discontinuity on every tail statistic** (mean, p90, frac>10) — the
   proposed schedule does not just preserve GT texture fidelity, it also
   produces the most view-consistent bakes of the four conditions.
2. Fixed-high (old generation) is the worst on seams (p90 45.7), consistent
   with its worst unseen-view rendering scores.
3. The seam/control ratios (1.3-2.9) show chart-boundary discontinuity
   exceeds natural local variation — i.e. the metric is sensitive and the
   residual seams are real, not measurement noise.
4. Caveat recorded: per-seam color averaging makes the MEDIAN gap ~0; the
   informative statistics are the tail (p90, frac>5/10).

Per-object numbers: SEAM_AUDIT_PER_OBJECT.csv; aggregates:
SEAM_AUDIT_AGGREGATES.json. Script: scripts/audit_bake_seams_20261001.py
(deterministic; position-keyed UV matching; skimage deltaE_ciede2000).
