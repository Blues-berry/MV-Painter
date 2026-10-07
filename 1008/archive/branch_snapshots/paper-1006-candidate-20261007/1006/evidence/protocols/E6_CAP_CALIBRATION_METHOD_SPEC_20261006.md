# E6: cap-respecting residual calibration — candidate, not an established contribution

## One-page method definition

Keep the geometry-texturing task, checkpoint, additive adapter, native caps and
50-step sampler of 01549. At wrapper j in layer group l, let h be the pre-adapter
hidden mosaic and r the unscaled correction, both from the current target-read
pass. Measure norms over the entire object mosaic, not separately per view.
Reference-write calls remain byte-for-byte on their original path.

On the original 24 development objects, native GFL at latent seed 42 supplies
rho = min(1.25, cap_l) * ||r|| / ||h||. First take the median over wrapper/step
observations within each object/group, then the median over objects to obtain
q_l. Thus q_l is a native-GFL applied-reference ratio calculated from unscaled
residuals, not a new quality-selected target. All calibration observations are
retained; zero/nonfinite observations stop calibration rather than being dropped.

Set a(t) = native C3(t)/1.65. The discrete 17/16/17-step C3 has mean 1.65,
not LLH's 1.675. For k in {0.75, 1.00, 1.25}, target tau = k*q_l*a(t), request
s_req = tau*||h||/||r||, and apply s = min(s_req, cap_l). Output h+s*r using
the original activation dtype. When a norm is zero, apply zero and record the
case; nonfinite values abort. One scalar is shared across the complete packed
object mosaic at each wrapper/step; this is not a surface-consistency constraint.

Log raw and hidden norms, target/request/applied scale, dtype, cap saturation,
target gap, rounding error, wrapper/group/step and write-pass preservation.
Saturation is an expected execution limit, not evidence of equal dose. Do not
redistribute clipped budget to another layer or view. Do not add projection,
momentum, retraining, spatial masks or extra schedule families in this candidate.

## Prior-art difference and decision

| Source | Established overlap | Candidate distinction to test |
|---|---|---|
| [SSI](https://arxiv.org/abs/2605.26538) | Depth/time injection and geometric ControlNet schedules already exist. | Current-state calibration of one native capped additive residual; fixed C3 shape is not novel. |
| [APG](https://arxiv.org/abs/2410.02416) | Guidance projection, rescaling and momentum already exist. | No CFG-vector projection or momentum; calibrated geometry-residual/hidden ratio and native per-layer caps. |
| [beta-CFG](https://arxiv.org/abs/2502.10574) | Adaptive norm control combined with a temporal curve already exists. | Development-derived layer references and joint-object execution under heterogeneous adapter caps; normalization plus a curve is not a novelty claim. |
| [NAG](https://arxiv.org/abs/2505.21179) | Attention-space extrapolation with normalization already exists. | No negative-attention branch; operates on the geometry adapter's additive correction. |
| Original FAC | Trained correction extension was unsuccessful under stricter controls. | No learned parameters or training data update; do not revive FAC as a successful predecessor. |

**Decision: bounded development permitted; methodological novelty NOT ESTABLISHED.**
This is more specific than directly changing a global guidance scale, but could
still be judged an incremental application of norm control. Independent quality
evidence alone will not establish algorithmic originality. Before Fresh D, write
a second decision using the full formula, component ablations and the above
overlap; if only generic normalization remains, stop the method claim.

The consulted primary sources were inspected on 2026-10-06. This is not an
exhaustive priority search and is not a claim that no equivalent method exists.
