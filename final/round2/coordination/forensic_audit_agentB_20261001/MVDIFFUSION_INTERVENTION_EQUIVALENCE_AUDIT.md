# MVDIFFUSION_INTERVENTION_EQUIVALENCE_AUDIT.md (Phase 13 — agent B)

Question (task doc): MVPainter scales an independent geometry-residual branch
`h + s·A(h,G)`; MVDiffusion scales a serial module via
`y_α = (1−α)x + α·CPBlock(x)`. Is this the same intervention? If not, the
experiment must be classified as a boundary/interface transfer, not a direct
replication.

## 1. Where α acts (code-verified)

`scripts/run_mvdiffusion_schedule.py` L9, L90–105: the 5 scheduled
decoder-side CPBlocks are wrapped with a convex interpolation of their
**output**: `(1.0 − α)·x + α·y` with `y = CPBlock(x)`, equivalently
`x + α·(y − x)`.

- α = 1 → bitwise original model (identity gate PASS 36/36, strict path).
- α = 0 → CPBlock fully bypassed (`y_α = x`); module internals still compute
  but their effect is discarded.
- α > 1 → extrapolation beyond the trained module output; arithmetically
  well-defined, semantically untrained.
- The CPBlock's internals (attention/norms) always run at full strength; α
  rescales only the recombination. The depth pathway itself (latent concat,
  5-channel conv_in) is never scaled — it is a prohibited surface (scaling it
  would scale the depth *input*, not a residual).
- Encoder-side CPBlocks stay at α = 1 by the frozen mapping (the scheduled
  surface is the 5 decoder blocks: deep={mid, up_0}, middle={up_1},
  shallow={up_2, up_3}; pre-registered, topology-derived — relative-depth
  fraction thresholds and resolution-level alignment converge; multiplier
  normalization weighted mean 1.0 with point-count weights 2/1/2, deep=middle
  1.35025, shallow 0.47463).

## 2. Is `x + α·Δ` the same intervention as `h + s·A(h,G)`?

Scalar algebra looks identical, but the intervention semantics differ in
three load-bearing ways:

| aspect | MVPainter / MV-Adapter | MVDiffusion CPBlock |
|---|---|---|
| residual status | `A(h,G)` is an **additive correction branch by construction**; `s` scales the residual itself | `Δ = CPBlock(x) − x` is only an **apparent residual**; the module is a serial replacement whose internals are not residual-shaped |
| α/s = 0 meaning | backbone unchanged, correction removed | module effect fully removed (equivalent to deleting the CPBlock from the forward path) |
| scaling surface | per-layer-group multiplicative factor on an injected feature | recombination ratio on a replacement module's output |

Because of (1) in particular, "layer-wise α profile" on MVDiffusion tests
whether **reweighting a serial correspondence module's influence** helps — a
different causal question from scaling an additive geometry residual. The two
experiments share the schedule algebra (low/high 0.75/1.00, mean 5/6,
boundaries 1/3, 2/3 — frozen identically to the MV-Adapter freeze, no
recalibration) but not the intervention object.

## 3. Consequence for classification (binding)

MVDiffusion must be written as a **boundary / interface transfer experiment**:

> "On a third backbone whose controllable conditioning surface is a serial
> correspondence module rather than an additive residual branch, the
> layer-wise reallocation did not replicate: structure/color metrics
> (PSNR, FG-/Edge-SSIM, ΔE00) significantly favor global conditions while
> GT-relative texture error significantly favors layer-wise; FG-LPIPS is not
> separated."

Forbidden phrasings: "direct replication on MVDiffusion", "the method
generalizes across backbones", any pooled cross-backbone absolute numbers
(only within-backbone paired contrasts are valid — 75-object panel, seed 42,
bootstrap seed 20260928, n=75).

## 4. Cross-checks performed

- Identity gate: α≡1 strict path 36/36 PNG SHA-256 bitwise vs official model;
  archived deployment reproduced 36/36 (provenance upgraded by the native
  SD2-depth mirror: 1552/1552 tensors + 12/12 views bitwise).
- Evaluator: legacy interop PSNR/SSIM reproduced archived values with diff 0.0;
  NaN convention for near-empty GT foreground views (obj_0029) reported, not faked.
- No tuning after results: scales/mapping/schedules frozen pre-run; negative
  direction preserved as found.

## Verdict

`VALIDATED` as a **boundary experiment**; `NOT_REPLICATED` as a replication
claim. The intervention-equivalence gap is structural (serial module vs
additive branch), documented, and must bound all cross-backbone claim widths
(see `CROSS_BACKBONE_CLAIM_BOUNDARY.md`).
