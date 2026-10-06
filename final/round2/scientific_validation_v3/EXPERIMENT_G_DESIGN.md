# EXPERIMENT_G_DESIGN — Cross-backbone mechanism test (pre-registered)

- Date frozen: 2026-10-02 (before any G run)
- Question: does ANOTHER additive-residual multi-view adapter also exhibit a
  layer-dependent temporal response? (NOT "does LLH transfer")

## Backbone

MV-Adapter (SD21-base i2mv pipeline), injection at 4 down-block points via
`pipeline_mvadapter_i2mv_sd.py` L576-584 (`geometry_scale` scalar per step ×
all adapter states).

## Depth-group mapping (FROZEN — from mv_adapter/layer_profile_transfer.json,
topology-derived by resolution, NO re-search after results)

| group | injection point |
|-------|-----------------|
| shallow | down_blocks.0 (320@64, idx0) |
| middle | down_blocks.1 (640@32, idx1) |
| deep | down_blocks.2 (1280@16, idx2) + down_blocks.3 (1280@8, idx3) |

## Frozen scale constants (match the historical MV-Adapter protocol)

- base/fixed-low: 0.75 (all points, all steps)
- intervention high: 1.00
- 50 steps; windows W1..W5 = steps 0-9,10-19,20-29,30-39,40-49

## Conditions (replicating Experiment A reduced)

- g_baseline: 0.75 everywhere
- g_{deep|middle|shallow}_W{1..5}: 1.00 on the group's point(s) inside the
  window only, 0.75 elsewhere → 15 interventions + baseline = 16 conditions

## Dose normalization

- Estimate per-point residual norms on DEV objects (calibration_objects)
  from first-call diagnostics extended to per-step logging (to be added in a
  G-runner patch: per-step per-point ||s·A||₂ persisted like the main runner).
- If per-group dose at equal scale differs by >2x, run a dose-normalized
  second map (same rule as a3_normalization.json: delta_l = C/mean_w M_l,w,
  C anchored to the deep group's raw delta). Recorded in g_normalization.json
  BEFORE any holdout G run.

## Cohort

- Preferred: fresh disjoint cohort in MV-Adapter format (render_root =
  fresh_confirm_v3_renders; source_uid_file = fresh_confirm list; manifest
  fields otherwise identical to mv_adapter/data_manifest.json). This is
  buildable because the fresh render tree uses the same 17-view format.
- If the G-runner's input path proves incompatible with the fresh tree, fall
  back to Exact-76, explicitly labeled ALREADY-OBSERVED (never "fresh").

## Frozen conclusion options (identical to MASTER_PROTOCOL_LOCK §8)

A. Layer×Time interaction exists on both backbones (best location may differ)
   → architecture-dependent layer-time allocation principle.
B. Layer redistribution exists but temporal interaction weak on MV-Adapter
   → layer-aware scaling, NOT generic layer-time interaction.
C. Neither transfers → L-TCAS framed as backbone-specific.

## Metrics

psnr, fg_ssim, edge_ssim, fg_lpips, ciede2000, gt_relative_texture_error
(same as MVADAPTER_STANDARD_PANEL_76.csv conventions, run_experiment.py
L128-154). Primary for G: fg_lpips (mirrors H1), secondary fg_psnr.

## Statistics

Object-paired bootstrap, 10,000 resamples, seed 20261002, Holm family =
15 cells + 1 interaction (same layermap machinery as analyze_v3.py).

## Pilot verification (2026-10-04, instrumentation only)

- Runner mechanism verified bit-exactly: scale traces show the requested
  (layer, window) cell change and NOTHING else; deep-point residual norms
  scale by exactly 1.0/0.75 during W3; other points bit-identical.
- Runtime ~21-25 s per object-condition (512x512, 6 views, 50 DDPM steps).
- Per-point residual magnitudes (g_0000, step 25): shallow(pt0)=1530.6,
  middle(pt1)=872.8, deep(pts2+3)=2227.8 -> equal-scale dose ratio
  1 : 0.57 : 1.46 (<2x) -> per the pre-registered rule, NO dose-normalized
  second map is required for G.
- Early observation (pilot only, not evidence): a 10-step deep intervention
  (0.75 -> 1.00) changes outputs only marginally; the formal map on 100
  fresh objects will quantify this with paired CIs.
