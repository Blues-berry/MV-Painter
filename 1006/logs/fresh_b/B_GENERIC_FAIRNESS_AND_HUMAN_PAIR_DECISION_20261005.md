# Generic-schedule fairness and human-pair decision

**Decision: add LLH vs endpoint-matched `gen_linear` to the human study.** On
the preregistered primary metric, FG-PSNR, endpoint-matched linear is the
closest generic competitor in both the independent H4 experiment and the
same-cohort B sensitivity. It must remain in the fair visual comparison.

## Registration and evidence status

The original 30-condition FRESH_CONFIRM_B registry does not contain generic
schedule conditions. H4's generic family was registered for Experiment C on
the separate FRESH_CONFIRM_300 cohort. The eight-condition B generic extension
was frozen after the B core outcomes were already open, reused the same
150-object cohort, and has a documented raw-row exposure before its integrity
gate. It is a same-cohort sensitivity, not a blinded or independent B
confirmation. The pre-registered Experiment C result and the post-lock B
extension are reported separately and are not pooled.

## Primary-endpoint comparison and realization reference

Positive FG-PSNR and negative FG-LPIPS contrasts favor LLH. Ratios use the
same-condition per-cell realization drift from the existing 24-object,
three-seed development probe. Ratios are scale context only, not thresholds or
standard errors for a mean.

| Campaign / schedule | Metric | LLH − generic [95% CI] | Holm p | Absolute effect / median drift | Absolute effect / P95 drift |
|---|---|---:|---:|---:|---:|
| C, registered `gen_linear` | FG-PSNR | +0.0049 [−0.0350, +0.0469] dB | 0.8148 | 0.0016 | 0.0005 |
| B extension, `gen_linear` | FG-PSNR | −0.0373 [−0.0829, +0.0086] dB | 0.1150 | 0.0121 | 0.0039 |
| C, registered `gen_linear` | FG-LPIPS | +0.00123 [+0.00069, +0.00182] | 0.0001 | 0.0458 | 0.0109 |
| B extension, `gen_linear` | FG-LPIPS | +0.0011 [+0.0004, +0.0019] | 0.0024 | 0.0411 | 0.0098 |

The exact registered C estimates are from 300 paired objects. The B extension
estimates are from 150 paired objects; its FG-PSNR contrast is not significant
after the eight-schedule Holm family, while FG-LPIPS favors the generic linear
schedule by a small absolute amount. Each statistically resolved effect is
small relative to the per-cell drift reference. This is a genuine comparator
that prevents a “best schedule” claim, even though neither cohort establishes
a practically important PSNR difference.

For completeness, the absolute-effect/drift ratios for every B-extension
schedule in the two H4 endpoints are recorded below. Their absolute effects
and CIs remain in `FINAL_GENERIC_SCHEDULE_COMPARISON.md`.

| B extension schedule | FG-PSNR / median | FG-PSNR / P95 | FG-LPIPS / median | FG-LPIPS / P95 |
|---|---:|---:|---:|---:|
| `gen_linear` | 0.0121 | 0.0039 | 0.0411 | 0.0098 |
| `gen_linear_bm` | 0.0313 | 0.0101 | 0.0336 | 0.0080 |
| `gen_cosine_bump` | 0.1088 | 0.0353 | 0.1755 | 0.0417 |
| `gen_cosine_bump_bm` | 0.1496 | 0.0485 | 0.2204 | 0.0524 |
| `gen_trapezoid` | 0.0606 | 0.0196 | 0.1307 | 0.0311 |
| `gen_trapezoid_bm` | 0.1423 | 0.0461 | 0.2129 | 0.0506 |
| `gen_gaussian_peak` | 0.1322 | 0.0429 | 0.1942 | 0.0461 |
| `gen_gaussian_peak_bm` | 0.1523 | 0.0493 | 0.2167 | 0.0515 |

## Nominal budget and realized residual dose

The closest primary-endpoint competitor, endpoint-matched `gen_linear`,
requests summed scales of 93.75 / 93.75 / 31.25 (deep/middle/shallow) over the
50 steps, versus LLH's 83.75 / 83.75 / 29.25. Its mean integrated post-scale
residual norm is 494,813 versus 440,501 for LLH (+12.3%); mean squared norm is
4.954e9 versus 4.178e9 (+18.6%). No cap activated. Thus nominal schedule
comparison does not equalize realized dose. The eight nominal-budget-matched
profiles all request the same per-layer sums as LLH; their realized integrated
norms are 0.5%–2.1% above LLH. The predeclared all-method central-90% dose
intersection is empty. The post-outcome pairwise model could not estimate the
endpoint-matched linear contrast with 20 complete pairs, so an actual-dose
adjusted linear comparison is **not estimable** from this cohort.

## Human-study consequence

The selected `visualization_24` objects are disjoint from FRESH_CONFIRM_B but
are members of the preregistered FRESH_CONFIRM_300 / Experiment C cohort. The
human package will use `gen_linear` prediction images from the registered C
run for those exact 24 frozen UIDs, alongside the already frozen LLH and
native-control images. The chosen comparator is therefore the endpoint-
matched linear method actually evaluated in both metric campaigns; no object
is selected by its schedule outcome.

The assignment design remains 40 fixed slots × 24 distinct objects per
participant. Each participant receives six objects for each of four pairs:
LLH vs GFL, GFH, GC3, and `gen_linear`; each frozen object/pair cell is
assigned to exactly 10 slots. Both existing questions stay separate. No human
responses exist, so this final pair lock can be frozen before any recruitment.

**`NARRATIVE_REEVALUATION_REQUIRED=YES`.** Retire “our schedule is best.” Keep
the contribution on residual allocation, depth allocation, and contrast-
specific temporal-placement evidence. Do not retune LLH based on this result.
