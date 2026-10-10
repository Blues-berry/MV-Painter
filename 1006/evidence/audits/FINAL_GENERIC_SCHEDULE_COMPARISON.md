# Final generic-schedule comparison — FRESH_CONFIRM_B

**Evidence class:** post-lock, same-cohort sensitivity; not independent confirmation. The independent pre-outcome Experiment C on FRESH_CONFIRM_300 remains separate and is not pooled with this result.

The eight extension conditions were generated for the frozen 150-object B cohort with the same checkpoint, runner, inputs, seed policy, and native cap path as `layer_llh`. The extension passed its integrity gate. The contemporaneous provenance note records one accidental raw-row exposure before that gate and a duplicate runner launch that was stopped during model loading; neither was used to change the locked conditions, analysis family, objects, or rows. See `B_GENERIC_EXTENSION_EARLY_ROW_EXPOSURE_NOTE_20261005.md`.

The locked H4 comparison reports LLH minus each generic schedule. Positive FG-PSNR and negative FG-LPIPS favor LLH. Intervals are paired object bootstrap 95% CIs (10,000 draws, seed 20261002); Holm correction is separate across the eight schedules for each metric.

## Locked paired H4 comparisons

| Schedule | FG-PSNR Δ [95% CI]; win; Holm p | FG-LPIPS Δ [95% CI]; win; Holm p |
|---|---:|---:|
| `gen_linear` | -0.0373 [-0.0829, +0.0086]; 43.3% win; Holm 0.1150 | +0.0011 [+0.0004, +0.0019]; 48.7% win; Holm 0.0024 |
| `gen_linear_bm` | +0.0967 [+0.0594, +0.1357]; 65.3% win; Holm ≤0.0008 | -0.0009 [-0.0013, -0.0004]; 65.3% win; Holm 0.0008 |
| `gen_cosine_bump` | +0.3367 [+0.2216, +0.4576]; 63.3% win; Holm ≤0.0008 | -0.0047 [-0.0059, -0.0034]; 76.7% win; Holm ≤0.0008 |
| `gen_cosine_bump_bm` | +0.4629 [+0.3526, +0.5780]; 74.7% win; Holm ≤0.0008 | -0.0059 [-0.0071, -0.0046]; 80.0% win; Holm ≤0.0008 |
| `gen_trapezoid` | +0.1875 [+0.0697, +0.3099]; 50.0% win; Holm 0.0036 | -0.0035 [-0.0047, -0.0023]; 74.7% win; Holm ≤0.0008 |
| `gen_trapezoid_bm` | +0.4404 [+0.3334, +0.5521]; 74.0% win; Holm ≤0.0008 | -0.0057 [-0.0070, -0.0045]; 78.0% win; Holm ≤0.0008 |
| `gen_gaussian_peak` | +0.4092 [+0.2934, +0.5302]; 68.0% win; Holm ≤0.0008 | -0.0052 [-0.0065, -0.0040]; 77.3% win; Holm ≤0.0008 |
| `gen_gaussian_peak_bm` | +0.4711 [+0.3584, +0.5892]; 74.7% win; Holm ≤0.0008 | -0.0058 [-0.0071, -0.0045]; 79.3% win; Holm ≤0.0008 |

## Co-reported fidelity and structure outcomes

Descriptive, unadjusted paired effects; these metrics are not added to the frozen H4 Holm families.

| Schedule | Full-PSNR | Full-LPIPS | FG-SSIM | Edge-SSIM | Full-SSIM |
|---|---:|---:|---:|---:|---:|
| `gen_linear` | +0.3011 [+0.2596, +0.3421]; 91.3% win | +0.0044 [+0.0036, +0.0053]; 13.3% win | -0.0100 [-0.0123, -0.0082]; 10.0% win | -0.0017 [-0.0023, -0.0011]; 26.0% win | -0.0040 [-0.0051, -0.0033]; 5.3% win |
| `gen_linear_bm` | +0.2008 [+0.1737, +0.2281]; 94.0% win | +0.0027 [+0.0021, +0.0034]; 23.3% win | -0.0015 [-0.0030, -0.0002]; 38.0% win | +0.0020 [+0.0013, +0.0026]; 68.0% win | -0.0016 [-0.0023, -0.0012]; 18.7% win |
| `gen_cosine_bump` | +0.8668 [+0.7622, +0.9706]; 97.3% win | -0.0035 [-0.0053, -0.0017]; 60.7% win | -0.0009 [-0.0039, +0.0019]; 42.0% win | +0.0090 [+0.0075, +0.0106]; 81.3% win | -0.0030 [-0.0041, -0.0020]; 28.0% win |
| `gen_cosine_bump_bm` | +0.7869 [+0.6972, +0.8763]; 98.7% win | -0.0094 [-0.0116, -0.0071]; 79.3% win | +0.0056 [+0.0027, +0.0086]; 60.0% win | +0.0121 [+0.0105, +0.0137]; 90.7% win | -0.0016 [-0.0026, -0.0008]; 42.0% win |
| `gen_trapezoid` | +1.0350 [+0.9100, +1.1602]; 96.7% win | +0.0004 [-0.0012, +0.0020]; 47.3% win | -0.0088 [-0.0119, -0.0061]; 22.0% win | +0.0050 [+0.0037, +0.0064]; 72.0% win | -0.0036 [-0.0050, -0.0025]; 26.0% win |
| `gen_trapezoid_bm` | +0.8046 [+0.7133, +0.8962]; 98.7% win | -0.0080 [-0.0102, -0.0059]; 77.3% win | +0.0043 [+0.0015, +0.0072]; 59.3% win | +0.0113 [+0.0097, +0.0129]; 89.3% win | -0.0021 [-0.0031, -0.0012]; 36.0% win |
| `gen_gaussian_peak` | +0.8054 [+0.7076, +0.9021]; 98.0% win | -0.0066 [-0.0086, -0.0046]; 74.7% win | +0.0029 [+0.0000, +0.0058]; 52.0% win | +0.0105 [+0.0089, +0.0121]; 86.0% win | -0.0020 [-0.0030, -0.0011]; 36.7% win |
| `gen_gaussian_peak_bm` | +0.7762 [+0.6858, +0.8663]; 98.7% win | -0.0100 [-0.0122, -0.0077]; 81.3% win | +0.0062 [+0.0033, +0.0092]; 63.3% win | +0.0120 [+0.0104, +0.0136]; 90.0% win | -0.0011 [-0.0020, -0.0003]; 43.3% win |

## GT-relative color and texture diagnostics

Negative deltas favor LLH because lower color/texture error is better. These remain descriptive and do not substitute for human preference.

| Schedule | CIEDE2000 | Laplacian log error | RGB-std log error | Gradient log error | HF-energy log error |
|---|---:|---:|---:|---:|---:|
| `gen_linear` | +0.1393 [+0.0063, +0.2633]; 38.0% win | -0.0841 [-0.1096, -0.0572]; 77.3% win | +0.0406 [+0.0308, +0.0496]; 18.7% win | +0.0034 [-0.0080, +0.0151]; 43.3% win | -0.0020 [-0.0054, +0.0020]; 62.0% win |
| `gen_linear_bm` | -0.0734 [-0.1692, +0.0213]; 55.3% win | +0.0044 [-0.0091, +0.0179]; 45.3% win | +0.0094 [+0.0050, +0.0137]; 30.0% win | +0.0025 [-0.0043, +0.0095]; 50.7% win | -0.0010 [-0.0031, +0.0013]; 58.0% win |
| `gen_cosine_bump` | -0.3305 [-0.6282, -0.0362]; 52.7% win | +0.0054 [-0.0257, +0.0363]; 52.0% win | +0.0222 [+0.0101, +0.0337]; 28.0% win | -0.0090 [-0.0250, +0.0073]; 58.0% win | -0.0061 [-0.0110, -0.0008]; 60.0% win |
| `gen_cosine_bump_bm` | -0.5933 [-0.8738, -0.3147]; 64.0% win | +0.0531 [+0.0194, +0.0864]; 42.0% win | +0.0111 [+0.0012, +0.0211]; 34.0% win | -0.0111 [-0.0288, +0.0068]; 54.7% win | -0.0065 [-0.0112, -0.0016]; 60.7% win |
| `gen_trapezoid` | -0.0413 [-0.3503, +0.2652]; 43.3% win | -0.0664 [-0.0985, -0.0340]; 62.0% win | +0.0298 [+0.0155, +0.0436]; 27.3% win | -0.0108 [-0.0259, +0.0047]; 59.3% win | -0.0067 [-0.0118, -0.0011]; 64.0% win |
| `gen_trapezoid_bm` | -0.5841 [-0.8518, -0.3142]; 63.3% win | +0.0361 [+0.0037, +0.0675]; 44.0% win | +0.0071 [-0.0023, +0.0166]; 36.0% win | -0.0118 [-0.0282, +0.0048]; 55.3% win | -0.0068 [-0.0112, -0.0023]; 61.3% win |
| `gen_gaussian_peak` | -0.4680 [-0.7664, -0.1746]; 58.7% win | +0.0409 [+0.0084, +0.0731]; 45.3% win | +0.0152 [+0.0045, +0.0257]; 31.3% win | -0.0095 [-0.0267, +0.0082]; 56.0% win | -0.0063 [-0.0110, -0.0012]; 60.7% win |
| `gen_gaussian_peak_bm` | -0.5986 [-0.8890, -0.3128]; 64.0% win | +0.0588 [+0.0243, +0.0927]; 41.3% win | +0.0098 [-0.0001, +0.0198]; 34.7% win | -0.0117 [-0.0300, +0.0067]; 56.0% win | -0.0064 [-0.0110, -0.0016]; 60.7% win |

## Requested scales, caps, and realized residual norms

Requested/applied scale entries are sums across the 50 frozen steps, ordered deep/middle/shallow. All nine methods use the native capped forward path; no cap activated in these conditions. Residual norms are measured from the actual post-scale wrapper corrections, summed over steps; squared norm is the sum of wrapper `l2²` values.

| Method | Requested = applied scale sums (D/M/S) | Cap activation (D/M/S) | Mean integrated norm | Mean squared norm |
|---|---:|---:|---:|---:|
| `layer_llh` | 83.75/83.75/29.25 | 0%/0%/0% | 440,501 | 4,177,961,420 |
| `gen_linear` | 93.75/93.75/31.25 | 0%/0%/0% | 494,813 | 4,954,420,278 |
| `gen_linear_bm` | 83.75/83.75/29.25 | 0%/0%/0% | 442,874 | 3,969,160,514 |
| `gen_cosine_bump` | 93.12/93.12/31.12 | 0%/0%/0% | 498,575 | 5,259,084,568 |
| `gen_cosine_bump_bm` | 83.75/83.75/29.25 | 0%/0%/0% | 449,004 | 4,266,255,030 |
| `gen_trapezoid` | 103.32/103.32/33.16 | 0%/0%/0% | 553,484 | 6,415,471,316 |
| `gen_trapezoid_bm` | 83.75/83.75/29.25 | 0%/0%/0% | 449,882 | 4,239,619,411 |
| `gen_gaussian_peak` | 88.03/88.03/30.11 | 0%/0%/0% | 471,239 | 4,710,632,463 |
| `gen_gaussian_peak_bm` | 83.75/83.75/29.25 | 0%/0%/0% | 448,601 | 4,269,495,370 |

## Actual-dose sensitivity

The all-nine-method central-90% dose intersection is empty: the largest method-specific lower bound is 513,916, while the smallest upper bound is 462,551. A single dose-adjusted model covering all nine methods is therefore not estimable without extrapolation. The complete method-specific 5th–95th intervals are in the authoritative JSON.

A supplemental pairwise common-support model was added after the extension results were opened and is explicitly exploratory. It uses one fixed rule for all eight pairs, complete objects only, log total post-scale norm, object fixed effects, and Holm across all eight pairs per endpoint. The four budget-matched profiles had pairwise support, but none of their conditional contrasts was significant after the eight-slot Holm correction; intervals were wide. The endpoint-matched linear and Gaussian comparisons were too sparse for 20 complete pairs, and cosine/trapezoid endpoint-matched conditions had no dose overlap with LLH. This analysis does not establish that dose explains the raw advantages; it shows the current cohort cannot separate schedule shape from realized dose with adequate precision.

## Interpretation

1. LLH was not detectably different from endpoint-matched linear warm-up on FG-PSNR (mean −0.037 dB; 95% CI [−0.083, +0.009]); on FG-LPIPS the mean contrast favored linear warm-up by 0.00109 (Holm p=0.0024). This differs in LPIPS direction from the earlier FRESH_CONFIRM_300 Experiment C; the cohorts are not pooled. H4 froze no practical-equivalence margin, so the PSNR null is not an equivalence result.
2. In the locked paired family, LLH had favorable mean FG-PSNR and FG-LPIPS contrasts against all four nominal-budget-matched schedules. The PSNR advantage over budget-matched linear was small (+0.097 dB); effects against cosine, trapezoid, and Gaussian were larger. No cap activated in any of these nine methods.
3. Nominal per-layer requested means do not equalize realized correction dose. The budget-matched schedules had mean integrated total norms about 0.5%–2.1% above LLH, while the endpoint-matched schedules were about 7.0%–25.7% higher. The squared-norm ordering differs slightly. Because the nine-method dose supports do not overlap and the pairwise post-outcome models are imprecise, the B extension does not establish superiority after controlling actual dose.
4. The B extension is post-lock and same-cohort. It is useful as a sensitivity check, not an independent H4 confirmation. The defensible contribution remains allocation characterization; a universal best-schedule claim is not supported by these data.

## Provenance

- Integrity gate: `B_GENERIC_EXTENSION_INTEGRITY_GATE.md` (PASS; 1,200/1,200 rows).
- Frozen extension: `FRESH_CONFIRM_B_GENERIC_EXTENSION_LOCK_20261005.md`.
- Pairwise and dose results: `formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005/FRESH_CONFIRM_B_GENERIC_EXTENSION_ANALYSIS.json`.
- Analysis choices for the all-nine dose model: `GENERIC_RESIDUAL_DOSE_SENSITIVITY_PLAN_20261005.md`.
- Post-outcome pairwise-dose note: `GENERIC_PAIRWISE_DOSE_SENSITIVITY_NOTE_20261005.md`.
- Early exposure/duplicate launch: `B_GENERIC_EXTENSION_EARLY_ROW_EXPOSURE_NOTE_20261005.md`.
