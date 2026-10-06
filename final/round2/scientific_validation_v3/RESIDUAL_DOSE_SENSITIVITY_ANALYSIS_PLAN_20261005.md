# FRESH_CONFIRM_B residual-dose sensitivity analysis plan — 2026-10-05

**Status:** Analysis choices frozen before joining the B A3b outcome rows to
its residual-dose logs. This is a post-request sensitivity analysis on an
already opened cohort, not an independent or prospective confirmation.
The locked A3b cell tests remain primary; dose-adjusted results are sensitivity
analyses and cannot be used to retune scales.

## Dose extraction

For each object, layer, and condition, combine wrapper `l2` values within each
step as a Euclidean norm (`sqrt(sum(wrapper_l2^2))`). From the frozen residual
logs report both (a) integrated post-scale norm, the sum of the per-step
layer norms, and (b) squared correction norm, the sum of squared wrapper
`l2` values. Record these over the full 50 steps and separately over the
active 10-step window. Also report the paired net norm and squared-norm
changes against the shared low baseline. The manifest and per-step `scale`,
`eff_scale`, and `uncapped` semantics are authoritative.

For comparability with the frozen development calibration, additionally
report its explicitly approximate incremental-dose proxy:
`(high - baseline) × sum(active-window layer_norm / actual_eff_scale)`.
Do not call this a counterfactual residual or exact injected dose: changing a
scale can change later activations and residuals.

## Locked sensitivity analyses

1. **Dose-adjusted model:** for each endpoint, fit cell-minus-baseline change
   with categorical `Layer × Window`, centered active-window integrated
   post-scale norm as a linear covariate, and object fixed effects; use
   object-cluster robust covariance. Fit one prespecified nonlinear
   sensitivity using `log(active-window norm)` because norms are positive and
   may vary multiplicatively. Report interaction Wald tests, coefficient
   estimates, and model-based interaction RMSE. No transform will be selected
   by its result.
2. **Common support:** using dose values only, find each layer's central 90%
   interval (5th–95th percentiles) over all five windows and objects. Define
   common support as the intersection of the three intervals. Retain only
   intervention rows inside that interval, regardless of quality outcome,
   report retained counts/fraction by layer and cell, and refit the linear
   dose-adjusted model if the intersection is nonempty and the design remains
   estimable. If the intersection is empty or cells become non-estimable,
   report that no cross-layer common-support estimate is available; do not
   widen support post hoc.
3. **Dose strata:** define pooled tertiles from the active-window integrated
   norm alone. Within each tertile, report layer/window cell counts and fit
   the interaction model only if all 15 cells have at least 10 observations
   and the design is full rank; otherwise label the interaction not
   estimable in that stratum. This is a dose-overlap diagnostic, not a new
   confirmatory family.
4. **Triangulation:** compare B bounded-map directions with the already
   reported A2 native-dose and A3 stress-test maps. Describe direction and
   scale regime; do not pool p-values or imply equal dose across experiments.

The primary causal interpretation is determined by the frozen A3b
FG-LPIPS family and its object-level interaction test. Loss after dose
adjustment will be described as dose-mediated/ambiguous; directional reversal
will weaken the interaction claim. Persistence cannot upgrade this imbalanced
bounded-dose map to an equal-dose experiment.

For sensitivity interaction p-values, apply Holm separately within each
endpoint across six planned slots: linear-dose model, log-dose model,
common-support linear-dose model, and the three dose-tertile interaction
models. An analysis that is not estimable remains explicitly unavailable and
is conservatively assigned p=1 for the family adjustment; report both raw and
adjusted values. This correction does not replace the locked 16-test A3b
primary or secondary families.
