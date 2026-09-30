# MVADAPTER_LAYER_MAPPING (final acceptance, 2026-09-30, static audit — no GPU)

## CROSS_BACKBONE_LAYERWISE = BLOCKED

## Deployment snapshot (frozen)

- Official MV-Adapter SD2.1 at upstream commit `4277e0018232bac82bb2c103caf0893cedb711be`;
  patched pipeline `pipeline_mvadapter_i2mv_sd.py` (per-step GLOBAL geometry
  scale via `upstream/mvadapter/geometry_scale.py`; hashes frozen in
  `CALIBRATION_FREEZE.json` / `CALIBRATION_RESULT_FREEZE.json`).
- Existing cross-backbone evidence = GLOBAL per-step scalar schedules only
  (fixed-low 0.75, fixed-1.0, LHL (0.75,1.0,0.75), equal-budget mean) on the
  76-object exact-mesh holdout — never layer-wise.

## Residual injection points (mechanically enumerated, SD2.1 base UNet)

`cond_encoder = T2IAdapter(in_channels=6, channels=[320,640,1280,1280],
num_res_blocks=2, downscale_factor=8)` (pipeline L711-716). Residuals are
passed as `down_intrablock_additional_residuals` to the UNet (systems
`mvadapter_image_sd.py` L224; pipeline L542: `adapter_state =
self.cond_encoder(control_image_feature)`). Shape enumeration (768x768
control input):

| entry | channels | resolution (768 input) | latent-relative | UNet position |
|---|---:|---|---|---|
| 0 | 320 | 96x96 | 1/1 | down block 0 (CrossAttnDownBlock2D), all intra-block resnets |
| 1 | 640 | 48x48 | 1/2 | down block 1 (CrossAttnDownBlock2D) |
| 2 | 1280 | 24x24 | 1/4 | down block 2 (CrossAttnDownBlock2D) |
| 3 | 1280 | 12x12 | 1/8 | down block 3 (DownBlock2D, no attention) |

## Current scale API

- Official: pre-loop multiplication of the WHOLE `adapter_state` list by one
  scalar (`control_conditioning_scale`).
- Deployed patch: per-denoising-step GLOBAL scalar schedule (same scalar for
  every entry at every step) evaluated inside the loop; official behavior
  retained when no schedule is supplied.
- Per-block scaling: technically feasible — the caller may scale each list
  entry independently before/inside the loop (inference-time residual
  strength only; NO model-weight change). Required code change: extend
  `geometry_scale.py` to a per-entry schedule `entry -> progress -> scale`.

## Why the gate cannot run (two hard blockers)

1. **The 4->3 depth-group assignment is not unique.** The main backbone's
   layer-wise semantics partition NINE adapter modules into deep/middle/
   shallow (3/3/3, caps 3.0/3.5/0.8). MV-Adapter exposes FOUR injection
   groups at resolutions 12/24/48/96. Resolution-anchored assignments
   (e.g. shallow=48+96 vs shallow=96 alone; deep=12 vs 12+24) are all
   defensible from topology alone; no rule pins one. Choosing an assignment
   by looking at results is forbidden selection.
2. **Layer scale values are not transferable and cannot be defined
   calibration-free.** The MVPainter LLH values (deep/middle 1.25->2.50,
   shallow 0.50->0.75) were calibrated for GeoTex residual magnitudes and
   the GeoTex cap table. MV-Adapter's frozen calibration
   (24-object probe split, 12 global schedules, seed 20260928) ended with
   `fixed_scale_selection: NO_CLEAR_TRADEOFF` (pareto front = fixed_1.0)
   and `stage_selection: not_uniquely_defined_by_frozen_rule` — the frozen
   CAI rule did not even define unique GLOBAL stage labels, let alone
   per-group values. Any per-group value choice would be a new calibration
   search, which this acceptance explicitly forbids.

## Gate evaluation

The precondition for running the 24-object gate ("mapping mechanical and
clear, layer scales defined without new calibration") is NOT met on the
value axis. Running the gate with transferred GeoTex scales or with an
arbitrary 4->3 assignment would produce an uninterpretable result and risk
catastrophic regression from out-of-range scales; both would waste the
decision budget without addressing Reviewer 2's gap in a valid way.

## Consequences for the manuscript

- Cross-backbone text must remain "global stage-position replication only"
  (MV-Adapter global temporal placement experiment on 76 exact-mesh holdout
  objects; measurable but non-uniform changes; frozen rule did not select a
  unique schedule).
- The limitation "second-backbone layer-wise status" stays BLOCKED: the
  per-block scaling mechanism is implementable (inference-time-only), but a
  protocol-valid gate requires (a) a pre-registered 4->3 group-assignment
  rule and (b) a per-group calibration protocol on the second backbone —
  both out of scope for this round.
