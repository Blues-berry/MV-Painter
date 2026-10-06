# A2 final interpretation

Date: 2026-10-05. Cohort: FRESH_CONFIRM_300, n=300 objects, 15 layer-window cells plus shared low baseline. The A2 measurements are historical outcomes; this audit is an exploratory reanalysis after the production interaction-test defect was discovered. It is not a new preregistered confirmation on this cohort.

## Statistical model and interaction

The primary response is the object-paired cell-minus-baseline FG-LPIPS change. We analyzed the repeated 3×5 measurements with (1) a Gaussian GEE with object clusters, exchangeable working correlation, robust sandwich covariance, and categorical Layer×Window terms; and (2) the independently validated cluster-robust Wald test on the eight object-level interaction contrasts. Both detect a Layer×Window interaction: GEE χ²(8)=482.708, p=3.6e-99; validated Wald W(8)=481.081, p=8.04e-99. The FG-LPIPS interaction accounts for 43.5% of between-cell variance. For FG-PSNR, GEE χ²(8)=1886.250, p<1e-300 (numerical underflow in the returned tail probability); Wald W(8)=1879.963, p<1e-300; interaction share 56.8%.

The object-paired contrast-of-contrasts is the eight-degree-of-freedom Layer×Window term above. The cell curves show a non-additive pattern: deep changes from adverse in W1 to favorable in later windows, while middle and shallow have distinct, nonparallel responses. The raw pointwise table below is descriptive. The 15-cell FG-LPIPS family used the pre-existing paired-bootstrap CIs and Holm adjustment; all 15 adjusted p-values are below .05. The original production interaction bootstrap is invalid for this question: it resamples object labels while preserving an object-shared interaction pattern and therefore has zero power (0/40 detections at the registered synthetic signal; see `STATISTICAL_PIPELINE_UNIT_TESTS.json`).

| Layer | Window | ΔFG-LPIPS (cell−baseline), 95% CI | Holm p | Win rate (Δ>0) | ΔFG-PSNR (cell−baseline), 95% CI |
|---|---:|---:|---:|---:|---:|
| Deep | W1 | +0.002927 [+0.002414, +0.003480] | 0.0016 | 78.7% | -0.1952 [-0.2358, -0.1562] |
| Deep | W2 | -0.000592 [-0.000812, -0.000360] | 0.0016 | 34.3% | +0.0258 [-0.0007, +0.0516] |
| Deep | W3 | -0.004126 [-0.004623, -0.003632] | 0.0016 | 15.3% | +0.1961 [+0.1355, +0.2563] |
| Deep | W4 | -0.003516 [-0.004075, -0.002979] | 0.0016 | 24.7% | +0.2422 [+0.1724, +0.3116] |
| Deep | W5 | -0.002383 [-0.002847, -0.001933] | 0.0016 | 29.3% | +0.0623 [+0.0222, +0.1034] |
| Middle | W1 | -0.003098 [-0.003601, -0.002627] | 0.0016 | 21.3% | +0.2208 [+0.1996, +0.2428] |
| Middle | W2 | -0.001610 [-0.001882, -0.001351] | 0.0016 | 22.7% | +0.0786 [+0.0612, +0.0966] |
| Middle | W3 | +0.000845 [+0.000620, +0.001063] | 0.0016 | 72.0% | -0.0776 [-0.0974, -0.0569] |
| Middle | W4 | -0.001917 [-0.002376, -0.001471] | 0.0016 | 35.0% | +0.1324 [+0.0912, +0.1736] |
| Middle | W5 | -0.006405 [-0.007075, -0.005732] | 0.0016 | 15.3% | +0.5145 [+0.4610, +0.5695] |
| Shallow | W1 | +0.001076 [+0.000814, +0.001343] | 0.0016 | 65.3% | +0.0138 [-0.0355, +0.0631] |
| Shallow | W2 | +0.001960 [+0.001588, +0.002336] | 0.0016 | 68.0% | -0.0422 [-0.1059, +0.0221] |
| Shallow | W3 | +0.001790 [+0.001446, +0.002139] | 0.0016 | 67.7% | -0.0396 [-0.0935, +0.0132] |
| Shallow | W4 | +0.001176 [+0.000881, +0.001477] | 0.0016 | 63.3% | +0.0066 [-0.0331, +0.0453] |
| Shallow | W5 | +0.000358 [+0.000085, +0.000633] | 0.0204 | 53.0% | +0.0727 [+0.0384, +0.1064] |

Sign convention: raw metric change is condition minus baseline; negative LPIPS and positive PSNR are favorable. In FG-LPIPS, deep W1 is adverse, deep W3–W5 improve, and shallow effects are adverse; the response is not summarized by one common temporal curve. The raw FG-PSNR map contains related but not identical directions.

## Outcome class and scope

**A2-I — strong interaction evidence in the observed raw-dose map, exploratory reanalysis.** The interaction is statistically clear, but A2 alone does not establish that the interaction is dose-independent, optimal, or confirmatorily replicated. The contrast shows heterogeneity of the cell responses under the native-dose A2 design; it does not identify a unique best schedule. The extreme A3 shallow dose was separately judged `STRESS_TEST_ONLY`, so it cannot establish a matched-dose mechanism across all layers. The bounded A3b design on FRESH_CONFIRM_B is the preregistered post-discovery confirmation for the full layer-by-time interaction question.

Synthetic validation supports the replacement Wald procedure: 40/40 detections at the injected interaction used by the audit and 4/40 null rejections at α=.05. These finite-replicate checks validate this statistic for the tested design; they do not convert the post hoc A2 reanalysis into prospective confirmation.
