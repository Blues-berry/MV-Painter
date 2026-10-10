# MV-Adapter Layer-wise Protocol (Second Backbone, Round-2 Cross-Backbone Task)

Status: pre-registered before any layer-wise MV-Adapter inference.
Date: 2026-09-30. Branch: `codex/next-review-response-20260930`.

This protocol defines the layer-wise (per-injection-point) residual scaling
validation for MV-Adapter. It reuses the already-frozen global-schedule
runner, checkpoints, dataset, seeds and metrics. Nothing here may be changed
after the first layer-wise run; no PSNR/SSIM may be consulted to alter the
grouping, profile, or scales.

## 1. Scope

Only these new conditions are run:

| Label | Meaning | Schedule (temporal) | Layer multipliers |
|---|---|---|---|
| L-FIX | layer-wise, temporally fixed | constant 5/6 | transferred profile |
| L-LHL | layer-wise low-high-low | 0.75/1.00/0.75 | transferred profile |
| L-LLH | layer-wise low-low-high | 0.75/0.75/1.00 | transferred profile |

Existing global results are reused without rerun (R0 = `no_geometry`,
G-FL = `fixed_low`, G-LHL = `LHL`, G-LLH = `LLH`; see §7).

## 2. Injection points (verified topology)

`pipe.cond_encoder` is a diffusers `T2IAdapter` over
`FullAdapter(channels=[320, 640, 1280, 1280], num_res_blocks=2, downscale_factor=8)`.
Its forward returns exactly one feature per body block; the pipeline scales
each feature by the global temporal scale and passes the list to the UNet as
`down_intrablock_additional_residuals`. diffusers 0.37.0 consumes the list in
order: one entry per down block (`CrossAttnDownBlock2D` x3 then `DownBlock2D`;
`sample += residual` after each block's processing).

For the SD2.1-base UNet at 512x512 with a 6-channel 512x512 control image the
verified points are:

| idx | UNet module | block type | channels | resolution | consumed by |
|---|---|---|---|---|---|
| 0 | `down_blocks.0` | CrossAttnDownBlock2D | 320 | 64x64 | `additional_residuals` kwarg |
| 1 | `down_blocks.1` | CrossAttnDownBlock2D | 640 | 32x32 | `additional_residuals` kwarg |
| 2 | `down_blocks.2` | CrossAttnDownBlock2D | 1280 | 16x16 | `additional_residuals` kwarg |
| 3 | `down_blocks.3` | DownBlock2D | 1280 | 8x8 | `sample += residual` |

Shapes will be re-verified at runtime during the identity audit (logged in
`MVADAPTER_LAYERWISE_IDENTITY_AUDIT.md`); any mismatch aborts the protocol.

## 3. Mechanical shallow/middle/deep mapping (frozen)

Rule, using network topology, resolution and relative depth only:

1. Order the 4 injection points by decreasing resolution (equivalently
   increasing relative depth): 64 > 32 > 16 > 8. There are no ties.
2. Assign group sizes carried over 1:1 from the frozen MVPainter profile,
   whose 4 injection points split shallow=1 / middle=1 / deep=2
   (`up_2` -> shallow; `up_1` -> middle; `up_0`, `mid` -> deep):
   - point 0 (320ch @ 64) = **shallow**
   - point 1 (640ch @ 32) = **middle**
   - points 2, 3 (1280ch @ 16, 1280ch @ 8) = **deep**

No metric was consulted before or during this mapping, and none may change it.

## 4. Frozen layer profile transfer

Source: `layer_fixed_mean = {deep: 1.65, middle: 1.65, shallow: 0.58}` from
`geotex/layer_lhl_ablation_shared.py` (exact means under the 17/16/17 stage
partition), also used unchanged by `scripts/run_layer_confirmation_276_20260930.py`.

Normalization: weighted mean over injection points = 1.0, weights = per-group
injection-point counts (2/1/1):

- weighted mean = (2x1.65 + 1x1.65 + 1x0.58)/4 = 1.3825
- deep = middle = 1.65/1.3825 = 1.193490054249548
- shallow = 0.58/1.3825 = 0.4195298372513563
- point-indexed list: `[0.4195298372513563, 1.193490054249548, 1.193490054249548, 1.193490054249548]`

Machine record: `layer_profile_transfer.json` (includes SHA-256 provenance of
all source files). The profile is frozen; MV-Adapter results may not modify it.

## 5. Absolute scale freeze

Identical to the frozen MV-Adapter global scales; recalibration forbidden:

- low = 0.75, high = 1.00, fixed mean = 5/6 = 0.8333333333333334
- `FIXED_MEAN` is interpreted as base temporal scale 5/6 (constant), then
  multiplied per point by the layer multiplier.

## 6. Runner semantics

A thin wrapper `run_layerwise_experiment.py` reuses `run_experiment.py`
machinery (dataset loading, checkpoint, scheduler, seed, cameras, metrics,
global scale code). The only addition: the wrapper pre-multiplies each
`cond_encoder` output feature by its frozen layer multiplier, so the pipeline's
existing per-step global scaling produces exactly

```
effective_scale(point, t) = layer_multiplier(point) x temporal_scale(t)
```

Model weights stay frozen; scaling is inference-only. When all multipliers are
1.0 the wrapped state equals the original state bitwise, which is what the
identity audit checks.

## 7. Combined standard panel (no rerun of global rows)

Panel = Reference-0 + Core-5 + Robustness-1 on the 76-object Exact holdout:

| Label | Source (existing/new) |
|---|---|
| R0 (no geometry) | `results/holdout_exact_76/` schedule `no_geometry` |
| G-FL (fixed 0.75) | `results/holdout_exact_76/` schedule `fixed_low` |
| G-LHL | `results/holdout_exact_lhl_shape_transfer_76/` schedule `LHL` |
| G-LLH | `results/holdout_exact_equal_budget_76/` schedule `LLH` |
| L-FIX | new `results/holdout_exact_layer_fixed_76/` |
| L-LLH | new `results/holdout_exact_layer_llh_76/` |
| L-LHL | new `results/holdout_exact_layer_lhl_76/` |

Additional context only (not part of the 7-condition panel): `fixed_1.0`,
`fixed_0.8333333333333334`, `HLL`, `linear_warmup`, `cosine_bump` rows already
on disk.

## 8. Formal commands (semantics; CLI names may be adapted as specified by the task)

All runs: `--split holdout --geometry-source exact --seed 20260928 --steps 50
--low 0.75 --high 1.00`, same manifest/base model/adapter as the global runs,
`CUDA_VISIBLE_DEVICES` per available GPU, `HF_HUB_OFFLINE=1`, `PYTHONPATH=.`.

```bash
# L-FIX
python final/round2/mv_adapter/run_layerwise_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --layer-profile final/round2/mv_adapter/layer_profile_transfer.json \
  --output-dir final/round2/mv_adapter/results/holdout_exact_layer_fixed_76 \
  --split holdout --geometry-source exact --device cuda:0 \
  --seed 20260928 --steps 50 --low 0.75 --high 1.00 --schedule FIXED_MEAN

# L-LHL
python final/round2/mv_adapter/run_layerwise_experiment.py \
  ... --output-dir final/round2/mv_adapter/results/holdout_exact_layer_lhl_76 \
  ... --schedule LHL

# L-LLH
python final/round2/mv_adapter/run_layerwise_experiment.py \
  ... --output-dir final/round2/mv_adapter/results/holdout_exact_layer_llh_76 \
  ... --schedule LLH
```

## 9. Gates before the formal runs

1. **Identity audit** (`MVADAPTER_LAYERWISE_IDENTITY_AUDIT.md`): with all
   layer multipliers = 1.0, the wrapper must reproduce the global runner
   bitwise on >= 3 objects for G-FL, G-LHL, G-LLH (PNG SHA-256, pixel
   equality, max abs pixel difference, metric equality). `PASS` required.
2. **Smoke** (`MVADAPTER_LAYERWISE_SMOKE.md`): 3 objects x {L-FIX, L-LHL,
   L-LLH}; checks are technical only (no NaN, all views generated, all metrics
   finite, methods differ, effective residual norms differ as expected). No
   parameter may be tuned based on smoke quality.

## 10. Completeness and statistics

- Each new condition: 76/76 objects, `exact_mesh`, all metrics finite
  (228 new rows total).
- Metrics: PSNR up, FG-SSIM up, Edge-SSIM up, FG-LPIPS down, CIEDE2000 down,
  GT-relative texture error down. LPIPS/ΔE00/texture are direction-adjusted in
  all paired deltas (lower-is-better flipped so positive favors the left
  condition of a comparison).
- Primary paired comparisons (10,000 object-level paired bootstrap,
  seed 20260928, 95% CI, mean + median + win rate):
  - P1 L-LLH vs G-FL
  - P2 L-LLH vs G-LLH
  - P3 L-LLH vs L-FIX
  - P4 L-LHL vs G-LHL
  - P5 G-LLH vs G-LHL
- Negative or mixed results are reported as found. No re-search of low/high,
  profile, stage boundaries, or mapping is permitted; no seventh method.

## 11. Completion gate

`MVADAPTER_EXPERIMENT_COMPLETE = YES` requires: identity audit PASS, 76x3 new
runs complete and finite, paired statistics complete, hash/provenance manifest
complete. Reports are experiment facts only; paper texts are not touched.
