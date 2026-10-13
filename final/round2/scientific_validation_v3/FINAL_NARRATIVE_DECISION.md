# Final narrative decision under the acceptance addendum

3D update 2026-10-06: stored N=20/8 GLBs now have a sampler-conformant
base-color evaluation. The results are mixed across FG-PSNR, FG-LPIPS, and
CIEDE2000 and do not change the provisional narrative or establish a unique
schedule winner. See `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`.

**Current status: provisional.** The human study remains open, so this file is
not the post-closure final narrative. The B pre-unblind inventory, practical
reference, multiplicity lock, and narrative switch rules were recorded after
earlier B outcome exposure; they are retrospective safeguards and do not
restore blinding.

**Current provisional class: `NARRATIVE_D` — characterize adapter scaling and
residual allocation, with depth allocation primary and tested temporal
contrasts secondary, scoped to the tested backbone.** This supersedes the
earlier provisional `NARRATIVE_B` selection; see
`NARRATIVE_SWITCH_REASSESSMENT_20261005.md`.

“Separate” here means that the paper should present and test these dimensions
through distinct contrasts. It does not mean the experiments established
statistical independence, equal post-scale dose, or an additive decomposition.

## Evidence under the safeguard rules

### 1. Do not make the full Layer × Time interaction load-bearing

A2's corrected cluster-Wald results are strong discovery evidence at native
dose (FG-LPIPS W=481.1, interaction share 43.5%; FG-PSNR W=1880.0, share
56.8%). A2 follows discovery of the production bootstrap's zero-power defect,
so these results do not serve as a new independent confirmation.

A3b is classified **`PARTIAL`**. It detects Layer × Window heterogeneity with
both the object-cluster Wald and GEE and remains significant under linear/log
dose covariates, but the bounded-dose calibration missed its ±20% target:
deep −20.01%, middle −20.20%, and shallow +98.98%. The realized-dose
distributions have no three-layer common support (0/2,250 rows retained);
dose-adjusted significance is extrapolative. Therefore a dose-independent
full interaction is not identified. The corresponding MV-Adapter map has no
interaction metric that survives its exploratory four-metric correction
(98/99 planned objects). MVDiffusion supplies a separate 75-object mixed/
negative boundary: CPBlock interpolation trades structure/color metrics
against texture error. These are interface-specific response differences,
not a matched causal architecture test. MV-Adapter uses a bounded one-window
additive-residual intervention; MVDiffusion interpolates serial CPBlock
outputs. Present each within its own cohort as evidence that transfer was not
established across the tested interfaces, not as an architecture-dependent
timing law.

**Permitted:** the main backbone shows a native-dose Layer × Window response
map; bounded interventions also show heterogeneity, but dose-independent
non-additivity remains unresolved. **Do not claim:** a validated equal-dose
Layer × Time mechanism, necessity of a full 2D control law, or cross-backbone
transfer.

### 2. Keep the human study as an open evidence gate

The visual audit found color/material mismatch in 18/24 panels and fine-detail
loss in 21/24; no stable visible schedule winner. The rebuilt offline study
has four pairs (LLH vs GFL/GFH/GC3/registered endpoint-matched `gen_linear`),
40 fixed slots, 24 comparisons per participant, an end-of-study
comprehension check, and a minimum of 36 valid completions. It has no
responses and has not been distributed. This is a high-value open evidence
gate, not evidence already obtained.

### 3. Let B bound the timing claim

The registered FRESH_CONFIRM_B contrasts favor LLH on mean outcomes:

| Contrast | FG-PSNR Δ [95% CI] | FG-LPIPS Δ [95% CI] | Interpretation |
|---|---:|---:|---|
| LLH − LFM-EXACT | +0.325 dB [0.209, 0.446] | −0.00460 [−0.00563, −0.00357] | Statistically detectable; both intervals lie within the frozen practical margins of ±0.5 dB and ±0.01. Requested per-layer means match, but realized correction norms do not. |
| LLH − HLL | +0.687 dB [0.404, 0.981] | −0.01098 [−0.01349, −0.00851] | Registered equal-high-duration placement contrast; mean PSNR is heterogeneous (45.3% favorable; median −0.104 dB). |
| LLH − LLL | +0.734 dB [0.597, 0.875] | −0.00845 [−0.01029, −0.00659] | LLH beats the all-low profile on both mean endpoints; this alone does not isolate placement. |
| HLL − LLL | +0.047 dB [−0.120, 0.208] | +0.00253 [0.00155, 0.00354] | Post-unblinding exploratory contrast. PSNR is inconclusive; LPIPS favors LLL. |

The four-way signature therefore **does not hold consistently across
endpoints**: the needed HLL<LLL direction is unconfirmed on PSNR and was
computed after B was unblinded. The registered LLH−HLL comparison supports a
narrow mean placement effect at matched requested means and equal high
duration, but not a universal “early-high hurts / late-high helps” rule.
Actual post-scale residual norms differ, so this is not a dose-independent
timing mechanism.

Against the required conjunction, the first three mean directions hold in
the observed contrasts, but LLH−LFM-EXACT is inside the practical margins and
actual residual norms differ. The required HLL<LLL direction is not supported:
PSNR is +0.047 dB with a CI crossing zero, while LPIPS points toward LLL.
Therefore the full conjunction fails, and no schedule retuning on this cohort
is justified.

The B integrity gate passed 4,500/4,500 rows before unblinding. B is no longer
blind; the results must be reported with their actual confirmatory and
exploratory labels. The later `B_PREUNBLIND_*` artifacts are retrospective
only.

The retrospective realization reference adds practical scale context. The
LLH−LFM-EXACT FG-PSNR effect is 0.105 of the median same-condition seed drift
and 0.034 of P95; its interval remains inside the registered ±0.5 dB margin.
LLH−HLL and LLH−LLL point estimates are 0.222 and 0.237 of median FG-PSNR
drift. These ratios are not thresholds or standard errors for the B mean;
report them beside, not instead of, the cohort confidence intervals. The
reference itself was created after B exposure. See
`PRACTICAL_EFFECT_REFERENCE.md`.

## Switch-rule decision

The stricter A–D assessment selects `NARRATIVE_D`. A3b does not identify a
dose-independent interaction because three-layer common support is empty.
The exact layer-mean comparison in FRESH_CONFIRM_B falls inside its frozen
practical margins, while HLL−LLL does not support a consistent early-versus-
late directional signature. Most importantly, registered `gen_linear` has
no detectable FG-PSNR difference from LLH in Experiment C. H4 did not freeze
an equivalence margin, so this is not an equivalence claim; it means the
evidence does not establish LLH as the primary-endpoint winner. The post-lock
B generic extension remains a sensitivity analysis, not independent
confirmation.

Accordingly, describe measured residual and depth allocation, keep timing
contrasts narrow and secondary, and retire any single-schedule superiority
claim. `NARRATIVE_REEVALUATION_REQUIRED=YES` is addressed provisionally here;
final ranking remains open until human evidence is collected or formally
waived. The corrected N=20 base-color result is a separate bounded endpoint:
the old CPU metrics remain historical, four no-UV assets remain excluded, and
the new evaluation is not full PBR or human evidence.

## Why `NARRATIVE_D`

The evidence characterizes how adapter residual allocation behaves across
depth and tested time profiles, without establishing a universal schedule
winner. Endpoint-matched linear warm-up is a credible primary-endpoint
competitor; other generic schedules and metrics do not give one universal
ranking. No formal equivalence with `gen_linear` is claimed. No LLH retuning is
justified.

### Approved framing

> We characterize how adapter residual allocation across network depth and
> tested denoising-time profiles changes measured reference fidelity and
> structure on the tested backbone. The observed response varies by contrast,
> metric, and object; the evidence does not identify a universally superior
> schedule.

### Retire or narrow

- Retire a dose-independent Layer × Time mechanism claim and any claim that
  the full matrix is necessary for deployment gains.
- Retire universal early-high harm, universal late-high benefit, and a
  universally optimal three-stage schedule.
- Keep one-third boundaries as a convenient discretization, not an
  empirically discovered phase boundary.
- Report MV-Adapter and MVDiffusion separately within their tested scale
  ranges and interfaces; neither broad transfer nor causal architecture-
  dependent scheduling has been established.
- Do not equate PSNR/LPIPS changes with faithful material or texture
  reproduction until the human gate is completed.
