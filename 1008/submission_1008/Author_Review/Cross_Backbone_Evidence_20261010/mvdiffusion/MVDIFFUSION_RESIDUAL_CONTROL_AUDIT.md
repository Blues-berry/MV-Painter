# MVDiffusion Residual Control Audit (Third Backbone, Round-2 Cross-Backbone Task)

Status: pre-registered before any scheduled MVDiffusion inference.
Date: 2026-09-30. Branch: `codex/next-review-response-20260930`.

## 1. Inspected files

- `upstream/src/models/depth/MVDepthModel.py` (`MultiViewBaseModel`)
- `upstream/src/models/depth/modules.py` (`CPBlock`, `CPAttn`, `ImageEncodingBlock`)
- `upstream/src/lightning_depth.py` (`DepthGenerator.inference_gen`, `gen_cls_free_guide_pair`)
- `upstream/src/dataset/Scannet.py` (batch fields)
- `scripts/run_mvdiffusion_depth.py` (deployed runner, `type='generation'` path)

## 2. How geometry enters the deployed generation path

`inference_gen` calls `gen_cls_free_guide_pair(..., type='generation')`:

- `latents = cat([latents, depth_inv_norm_small], dim=2)` — the (normalized
  inverse) depth map is concatenated to the latents as a 5th channel and enters
  through `unet.conv_in`. `meta` gets NO `'condition'` key.
- Consequently `condition_flag = False` in `MultiViewBaseModel.forward`: the
  literal additive branches `hidden_states += condition_states_i`
  (`condition_conv_in` + `condition_downblocks`/`condition_upblocks`) are
  **inactive in the deployed generation path** (they are used only by the
  panorama `type='interpolation'` path).
- `get_correspondence(meta)` computes cross-view correspondence maps and
  overlap masks from `depths`, `poses`, `K` — geometry inputs, untouched by any
  scaling considered here.

Per the task boundary ("do not modify the depth input itself; no scaling of
raw depth / depth normalization / camera geometry"), the latent-concat depth
channel is a **prohibited surface**: scaling it would scale the depth input.

## 3. Active controllable modules: the 9 CPBlocks

With `m > 1` the forward applies one `CPBlock` after each UNet segment:

| # | site | module | position (latent res, 512 input) |
|---|---|---|---|
| 0-3 | `cp_blocks_encoder[i]` | CPBlock | after `down_blocks[0..3]` @ 64/32/16/8 |
| 4 | `cp_blocks_mid` | CPBlock | after `mid_block` @ 8 |
| 5-8 | `cp_blocks_decoder[i]` | CPBlock | after `up_blocks[0..3]` @ 8/16/32/64 |

`CPBlock(x) = BasicResNetBlock(zero_init)(CPAttn(x))`; `CPAttn` runs
correspondence-aware cross-view attention and its `BasicTransformerBlock` has
internal residuals, but the module's I/O semantics is **replacement**:
`y = CPBlock(x)` — there is no literal `x = x + residual` on the deployed path.

## 4. Classification: PARTIAL

- **Not DIRECT_RESIDUAL**: the deployed path has no independent additive
  conditioning branch (the literal additive branch is dead code for
  generation), and the modulatable quantity is a serial replacement module
  whose output contains transformed backbone features, not an additive signal
  from an independent encoder.
- **Not NONE**: an exact, inference-only, weight-frozen residual-scale
  interface exists. Writing `Delta = CPBlock(x) - x`, the replacement
  `y = x + Delta` admits an exact residual scale alpha:
  `y_alpha = x + alpha * Delta = (1 - alpha) * x + alpha * y`.
  At `alpha = 1.0` this is bitwise identical to the original model
  (`0*x + 1*y = y` in IEEE arithmetic); at `alpha = 0` it is exact backbone
  passthrough. alpha is therefore the exact scale of the CPBlock residual
  contribution, directly comparable in form to the MV-Adapter geometry-scale
  intervention, while differing in kind (serial cross-view modulation vs.
  independent geometry-feature injection). Honest label: **PARTIAL**.

## 5. Temporal + layer control (pre-registered mechanical mapping)

alpha(point, t) = layer_multiplier(point) x temporal_scale(t), with the frozen
temporal schedules low = 0.75, high = 1.00, fixed mean = 5/6 (no recalibration).

Scheduled surface (mechanical, topology-only): the 5 decoder-side CPBlocks —
`cp_blocks_mid`, `cp_blocks_decoder[0..3]` — mirroring the source profile's
decoder injection path (MVPainter TCAS groups `mid, up_0, up_1, up_2`).
Encoder-side CPBlocks stay at alpha = 1 (outside the transferred surface,
documented as a protocol boundary).

Group mapping by relative depth / resolution (latent units): the deepest
resolution-tied pair {mid, up_0} @ 8 mirrors the source deep pair; @16 maps
middle; the two shallowest levels @32 and @64 map shallow:

- deep   = {cp_blocks_mid, cp_blocks_decoder[0]}   (2 points)
- middle = {cp_blocks_decoder[1]}                   (1 point)
- shallow= {cp_blocks_decoder[2], cp_blocks_decoder[3]} (2 points)

Two independent mechanical reasonings converge on this 2/1/2 split:
(a) relative-depth fraction thresholds carried over from the source grouping
(deep < 1/2, middle in [1/2, 5/6), shallow >= 5/6 of the decoder path);
(b) resolution-level alignment (tied deepest pair = deep; next level = middle;
remaining levels = shallow). No metric was or will be consulted.

Normalized layer profile (weighted mean over the 5 scheduled points = 1.0,
weights = point counts 2/1/2; source values deep 1.65 / middle 1.65 /
shallow 0.58 preserved as ratios):

- weighted mean = (2x1.65 + 1x1.65 + 2x0.58)/5 = 1.222
- deep = middle = 1.65/1.222 = 1.3502458265122749
- shallow = 0.58/1.222 = 0.4746317504091673

## 6. Identity test plan (before any scheduled run)

alpha = 1.0 at every scheduled point (no layer multipliers, temporal schedule
= constant 1): outputs must be **bitwise identical** (PNG SHA-256 equal) to the
official unmodified model on >= 3 objects x 12 views, because the strict-path
interpolation degenerates to `0*x + 1*y = y` exactly. Any deviation stops
Phase D.

## 7. Forbidden interventions (restated)

No scaling of raw depth, depth normalization, camera geometry, poses, K, or
correspondence computation; no weight modification; no retraining; no
recalibration of low/high/mean; no post-hoc change of the mapping above.

## 8. Identity test result (2026-09-30, addendum)

Executed per section 6 on the deployed compat base, 3 objects
(obj_0024-obj_0026) x 12 views, seed 42, 50 DDIM steps:

- official runner rerun (`scripts/run_mvdiffusion_depth.py`) vs archived
  `holdout_exact_75_50steps` grids: **36/36 PNG SHA-256 equal** (deployment
  protocol is bitwise reproducible);
- scheduled runner `IDENTITY` condition with `--strict-identity`
  (`y' = (1-alpha) x + alpha y` arithmetic exercised, no shortcut) vs official
  rerun: **36/36 PNG SHA-256 equal**.

```
POSTLOAD_STATE_EQUIVALENT  : NOT_APPLICABLE (download blocked)
OUTPUT_EQUIVALENT          : NOT_APPLICABLE (download blocked)
IDENTITY (alpha = 1)       : PASS  (36/36 bitwise)
IDENTITY_AUDIT             : PASS
```

A first identity attempt with a mis-specified condition (layer multipliers
applied, so alpha = 1.35/0.475 rather than 1) produced different outputs,
as expected; it was discarded and rerun with alpha identically 1 at every
scheduled point. Logs: `results/phase_d_identity_*`.
