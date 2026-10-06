# Cap and residual-budget diagnostic protocol lock

Frozen: 2026-10-05 UTC, before any FRESH_CONFIRM_B method output.

## Cohort and run

- Cohort: all 150 identities in `fresh_confirm_b/fresh_confirm_b.txt`;
  SHA256 `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`.
- Full input manifest SHA256:
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Runner SHA256:
  `bcf49f4bdb3995ae80c0e2bd70b04c31936a2fb3347dd9642172b19f27b9c0ae`.
- GeoTex checkpoint SHA256:
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- One combined run with the A3b and stage-boundary conditions will use the
  same runner, checkpoint, object seeds, initial latent seed, inputs, view
  order, and metrics. The shared `a3_baseline` is the low-scale reference.

## Frozen diagnostic conditions

| Runner condition | Registered meaning |
|---|---|
| `native_gfl` | Native capped fixed request 1.25 |
| `native_gfh` | Native capped fixed request 2.50 |
| `native_gc3` | Native capped C3 schedule |
| `true_global_0p80` | Uniform 0.80 with the true-uniform bypass path |
| `true_global_1p25` | Uniform 1.25, caps bypassed |
| `true_global_1p675` | Uniform 1.675, caps bypassed |
| `true_global_2p50` | Uniform 2.50, caps bypassed |
| `lfm_exact` | Exact layer-constant mean-matched schedule |
| `layer_llh` | Low-low-high three-stage schedule |
| `layer_hll` | High-low-low three-stage schedule |

The explicit TGU-0.80 condition closes the missing diagnostic endpoint. Its
requested and applied scales are all 0.80; the bypass flag is retained to
keep it in the same implementation family as the other TGU conditions. No
cap activation occurs at this value.

## Pre-specified contrasts and reporting

Report requested scale, effective scale, cap activation, post-scale residual
norm by layer and step, integrated residual dose by layer, and paired
performance metrics for every condition. `uncapped=true` in a run manifest
means the applied scale is the requested scale even if a residual log still
contains a hypothetical clipped `eff_scale`; analysis must follow the actual
forward path recorded by the manifest.

The fixed contrast family is:

1. LLH − GFL: combined allocation, nominal-budget, and cap-profile change.
2. LLH − LFM-EXACT: temporal variation at the exact layer-mean budget.
3. LLH − HLL: position change at matched per-layer high duration.
4. GFL − TGU-1.25: cap semantics at the same requested global scale.
5. LFM-EXACT − TGU-1.675: shallow exposure differs; this is not a pure
   equal-total-dose layer-allocation contrast.
6. TGU-1.25 − TGU-0.80: uniform requested-dose contrast.
7. LLH − TGU-1.675: combined layer allocation and cap/exposure contrast.

Primary performance endpoint: FG-PSNR. Co-reported endpoint: FG-LPIPS.
Compute paired object-level bootstrap intervals with 10,000 resamples and
seed 20261002. Holm-correct the seven predeclared contrasts separately for
each of these two metrics. Other logged metrics are descriptive. The contrast
semantics above are fixed: do not sum contrasts with different endpoints or
call the combined contrasts pure cap, layer, or temporal effects. TGU remains
a causal diagnostic and must not be described as a deployment baseline.
