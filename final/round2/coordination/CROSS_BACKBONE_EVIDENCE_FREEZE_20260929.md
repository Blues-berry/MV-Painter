# Cross-backbone evidence freeze

Date: 2026-09-29 UTC  
Scope: existing MV-Adapter Exact Mesh package; no MVDiffusion claim is added.

## What is auditable

- 76 object UIDs (`obj_0024`–`obj_0099`) with exact-mesh conditioning and
  per-object metrics.
- 50 inference steps, seed `20260928`, shared implementation hashes, and
  object-level bootstrap (`10,000` resamples, 95% CI).
- Recorded conditions include no geometry, fixed-low, fixed-1.0, matched-range
  schedules, direct LHL transfer, and a pre-specified equal-mean follow-up.
- The equal-mean follow-up uses fixed mean `5/6` and HLL/LHL/LLH placements.

## Frozen interpretation

The second backbone demonstrates that the residual-scaling interface and a
stage-placement comparison can be executed on a distinct implementation. It
also shows measurable schedule-position differences: LHL has the highest
FG-SSIM/Edge-SSIM among the four equal-mean rows, while LLH has the highest
PSNR and lowest GT-relative texture error. No condition dominates all targets.

The direct LHL row is a shape-transfer diagnostic, not a CAI-selected winner.
The frozen CAI rule is `undefined_set_valued`. LHL does not establish a
uniform practical gain over conservative fixed-low or equal-mean fixed scale.

## Claims explicitly excluded

- No absolute metric comparison between MVPainter and MV-Adapter.
- No claim that quality gains transfer across backbones.
- No claim that MVDiffusion deployment alone is a controlled backbone result.
- No causal explanation for why a stage position helps.
- No claim of pretraining disjointness beyond the recorded UID audit; the
  official MV-Adapter pretraining list is unavailable.

## Follow-up gate

The main-adapter strict-276 stage table is not an equal-effective-budget
experiment: 50 steps are partitioned as 17/16/17 and the nominal per-step
scale averages differ (`1.650` for LHL versus `1.675` for HLL/LLH). A matched
main-adapter rerun may be used to answer whether the stage-position pattern is
replicated, but until then the cross-backbone evidence is implementation
transfer plus within-backbone stage sensitivity, not cross-backbone benefit
transfer.

## Sources

- `final/round2/mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.csv`
- `final/round2/mv_adapter/MV_ADAPTER_PAIRED_COMPARISONS.json`
- `final/round2/mv_adapter/results/holdout_exact_equal_budget_76/PROTOCOL.json`
- `final/round2/mv_adapter/MV_ADAPTER_FINAL_INTERPRETATION.md`
