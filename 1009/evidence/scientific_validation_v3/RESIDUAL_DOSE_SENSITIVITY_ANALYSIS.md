# Residual-dose sensitivity analysis — FRESH_CONFIRM_B A3b

**Evidence class:** post-outcome sensitivity on the already opened FRESH_CONFIRM_B cohort; not an independent or equal-dose confirmation. The A3b map and its frozen 16-test endpoint families remain primary. Dose regressions condition on observed post-treatment residual norms and cannot reconstruct counterfactual equal-dose interventions.

The object-cell artifact contains all 150 × 3 layers × 5 windows = 2,250 unique paired rows. For each cell it records active-window integrated post-scale norm, squared correction norm, corresponding baseline dose, net changes, full-window dose, frozen development increment proxy, and metric deltas. Residual logs and manifest scale semantics are authoritative.

## Realized dose and overlap

| Layer | Mean active integrated norm | Mean active squared norm | Mean net norm change vs baseline | Mean frozen increment proxy | Central 90% active-dose interval |
|---|---:|---:|---:|---:|---:|
| deep | 66,508.8 | 448,409,408 | 657.7 | 661.1 | [56,358.6, 79,926.5] |
| middle | 15,484.6 | 24,645,891 | 626.9 | 664.9 | [11,421.3, 19,336.0] |
| shallow | 4,253.9 | 1,891,619 | 1,582.0 | 1,595.2 | [2,816.5, 5,192.6] |

No layer-level central-90 dose overlap exists: deep spans 56,359–79,927, middle 11,421–19,336, and shallow 2,816–5,193. The pre-frozen common-support rule therefore retains 0/2,250 rows; no common-support interaction estimate is available. The cap activation fraction is 0% for all layers; shallow's requested high value equals its native ceiling but was not clipped.

## Dose-adjusted interaction models

Both models include categorical Layer × Window terms and object fixed effects, with object-cluster robust covariance. The linear model uses centered active-window integrated norm; the nonlinear sensitivity uses log norm. These are conditional associations; dose is post-treatment and the layer dose ranges do not overlap.

| Endpoint | Dose term | Interaction Wald (df=8) | Raw p | Holm p, six-slot family | Interaction RMSE per cell | Dose coefficient [95% CI] | Dose p |
|---|---|---:|---:|---:|---:|---:|---:|
| FG-LPIPS | centered linear norm | W=207.766 | 1.47e-40 | 8.84e-40 | 0.000499063 | +8.403e-08 [-8.265e-08, +2.507e-07] | 0.323 |
| FG-LPIPS | log norm | W=174.492 | 1.47e-33 | 7.37e-33 | 0.000340933 | +9.513e-05 [-0.003176, +0.003367] | 0.955 |
| FG-PSNR | centered linear norm | W=426.696 | 3.63e-87 | 1.81e-86 | 0.0463031 | +1.385e-05 [-8.848e-06, +3.655e-05] | 0.232 |
| FG-PSNR | log norm | W=506.439 | 2.92e-104 | 1.75e-103 | 0.0402485 | +0.2941 [-0.1455, +0.7337] | 0.19 |

The Layer × Window test remains significant under both prespecified parametric adjustments. The interaction RMSE is 0.000499/0.000341 FG-LPIPS and 0.0463/0.0402 dB FG-PSNR for linear/log dose, respectively. These fits are extrapolative across the separated layer dose ranges: significance after a linear or log covariate does not establish dose independence.

## Dose-stratified analysis

For FG-LPIPS, pooled dose-only tertile cutpoints are 7,073.1 and 29,086.4.
- Tertile 1: not estimable as a 3-layer interaction; rows by layer are {'deep': 0, 'middle': 0, 'shallow': 750}.
- Tertile 2: not estimable as a 3-layer interaction; rows by layer are {'deep': 0, 'middle': 750, 'shallow': 0}.
- Tertile 3: not estimable as a 3-layer interaction; rows by layer are {'deep': 750, 'middle': 0, 'shallow': 0}.
For FG-PSNR, pooled dose-only tertile cutpoints are 7,073.1 and 29,086.4.
- Tertile 1: not estimable as a 3-layer interaction; rows by layer are {'deep': 0, 'middle': 0, 'shallow': 750}.
- Tertile 2: not estimable as a 3-layer interaction; rows by layer are {'deep': 0, 'middle': 750, 'shallow': 0}.
- Tertile 3: not estimable as a 3-layer interaction; rows by layer are {'deep': 750, 'middle': 0, 'shallow': 0}.

Because the pooled tertiles separate layers by their native residual-norm scale, none contains all three layers. This is the same support failure expressed as strata; the planned 3×5 within-tertile interaction cannot be estimated. Non-estimable slots were conservatively assigned p=1 in each six-slot Holm family.

## Cross-experiment triangulation

Cell-mean directions are compared descriptively across the 15 map cells; no p-values are assigned to these correlations. A2 and A3 both use FRESH_CONFIRM_300, and all five A3 deep cells are objectwise identical to A2. They are not independent replications. A3b uses the disjoint FRESH_CONFIRM_B cohort.

| Metric | Map pair | Pearson r | Spearman ρ | Same-sign cells |
|---|---|---:|---:|---:|
| FG-LPIPS | A2_native_300 vs A3_dose_normalized_300 | 0.679 | 0.889 | 14/15 |
| FG-LPIPS | A2_native_300 vs A3b_bounded_B150 | 0.632 | 0.832 | 14/15 |
| FG-LPIPS | A3_dose_normalized_300 vs A3b_bounded_B150 | 0.831 | 0.886 | 13/15 |
| FG-PSNR | A2_native_300 vs A3_dose_normalized_300 | 0.447 | 0.818 | 11/15 |
| FG-PSNR | A2_native_300 vs A3b_bounded_B150 | 0.080 | 0.396 | 13/15 |
| FG-PSNR | A3_dose_normalized_300 vs A3b_bounded_B150 | -0.503 | -0.071 | 9/15 |

Against A2's native-dose map, the fresh B bounded map has the same mean-effect sign in 14/15 FG-LPIPS cells and 13/15 FG-PSNR cells, but the magnitudes are much smaller and this 15-cell sign count is descriptive. Against A3's high-dose map, sign agreement is 13/15 for FG-LPIPS and 9/15 for FG-PSNR; the shallow A3 stress regime is especially unlike the bounded map. The direction pattern is partly reproducible at native/bounded scales, while magnitude and some metric responses change with dose regime.

## Interpretation

The bounded-map interaction survives linear and log dose adjustment, but the actual-dose support is completely separated by layer and the dose-tertile models cannot include all three layers. Therefore dose confounding remains unresolved for a dose-independent Layer × Window mechanism. The model results do not show that actual dose is irrelevant; they show that this cohort cannot identify its independent contribution without extrapolation.

Do not call A3b equal-dose, do not describe the sensitivity models as causal dose control, and do not tune a new map on FRESH_CONFIRM_B. Whether a third untouched cohort with a directly norm-controlled diagnostic is necessary should be decided only after the full evidence and narrative gate; it must not be run merely to seek a favorable result.

## Provenance

- Frozen analysis plan: `RESIDUAL_DOSE_SENSITIVITY_ANALYSIS_PLAN_20261005.md`.
- A3b protocol and scale bounds: `A3B_PROTOCOL_LOCK.md` and `A3B_DOSE_FEASIBILITY_AUDIT.md`.
- Full model results: `formal/campaign_FRESH_CONFIRM_B_20261005/RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.json`.
- Per-object × cell dose table: `formal/campaign_FRESH_CONFIRM_B_20261005/RESIDUAL_DOSE_OBJECT_CELL_DATA.csv`.
