# A — Why the large-cohort LLH result and the 26-object diagnosis differ

**Verdict: `LLH_GFL_CONTRADICTION_EXPLAINED = PARTIAL`.** The evidence supports a real, reproducible average LLH advantage on Fresh C and the independent Fresh B holdout, alongside a GT-predictable high-texture failure boundary. The 26-object diagnosis is a selected forensic set and its saved RGB is a different prediction instance from the overlapping Fresh C UIDs. The evidence therefore does not support either “LLH always helps” or “the 26-object result disproves the larger studies.”

## Separate cohort effects

| Cohort and scope | LLH−GFL CIEDE2000 | FG-PSNR | FG-LPIPS | GT-relative Laplacian error |
|---|---:|---:|---:|---:|
| Fresh C, all 300 | `−2.232` [`−3.137, −1.338`], 187/300 lower | `+1.143 dB` [`+0.814, +1.480`], 169/300 higher | `−0.01748` [`−0.02003, −0.01496`], 221/300 lower | `−0.01786` [`−0.01866, −0.01709`], lower on 300/300 |
| Fresh C, exclude diagnostic-overlap UIDs, 280 | `−2.188` [`−3.120, −1.274`], 173/280 lower | `+1.097 dB` [`+0.768, +1.431`], 156/280 higher | `−0.01732` [`−0.01977, −0.01490`], 209/280 lower | `−0.01779` [`−0.01856, −0.01702`], lower on 280/280 |
| Fresh B independent holdout, 150 | `−1.905` [`−3.262, −0.529`], 85/150 lower | `+1.030 dB` [`+0.577, +1.493`], 77/150 higher | `−0.01556` [`−0.01920, −0.01192`], 111/150 lower | `−0.01871` [`−0.02016, −0.01743`], lower on 150/150 |
| Diagnostic-26 forensic set, 26 | `+3.583` [`+0.544, +6.619`], lower on 9/26 | `−0.197 dB` [`−1.562, +1.304`], higher on 7/26 | `−0.01294` [`−0.02708, +0.00025`], lower on 13/26 | `−0.00879` [`−0.01109, −0.00669`], lower on 26/26 |

Intervals are 10,000 paired-object bootstrap percentile intervals. Lower is better for CIEDE2000, LPIPS and GT-relative Laplacian error; higher is better for FG-PSNR. The diagnostic set is not an independent cohort and is not combined with Fresh C/B. All raw per-object differences and SHA links are retained in the cohort CSVs.

## A real high-texture limit coexists with the mean benefit

Fresh B's fixed GT Laplacian-variance quartiles reproduce the previously documented failure boundary. In Q1 (38 texture-poor objects), LLH−GFL is `−8.756` CIEDE2000 [−10.805, −6.569], `+3.646 dB` FG-PSNR [2.761, 4.471], and `−0.03768` FG-LPIPS [−0.04295, −0.03250]. In Q4 (38 texture-rich objects), it is `+3.624` CIEDE2000 [1.907, 5.303], `−0.770 dB` FG-PSNR [−1.165, −0.315], and `−0.00008` FG-LPIPS [−0.00562, +0.00519]. Only 10/38 Q4 objects have lower CIEDE2000 and 7/38 have higher PSNR.

Fresh C was assigned the same Fresh-B cut points without retuning them. Its Q4 CIEDE2000 delta is `+1.956` [0.105, 3.833] across all 58 objects and `+1.598` [−0.197, 3.403] after excluding the 3 diagnostic-overlap objects in this quartile; FG-PSNR is `−0.346` [−0.848, +0.177] for all Q4. These Fresh C cross-cohort groups are exploratory; they are directionally consistent with, but do not replace, the independent Fresh B result. Continuous associations show that higher GT texture complexity accompanies smaller LLH gains and worse color deltas (e.g., ΔCIEDE2000 versus GT HF energy: Spearman ρ `0.629` in Fresh C and `0.672` in Fresh B). Those correlations describe heterogeneity; they do not prove a mechanism.

The conclusion is a bounded performance statement: LLH improves the cohort averages but does not preserve color/detail uniformly, and its mean advantage is concentrated in low-texture objects. It is not evidence that more high-frequency response automatically means more faithful texture.

## Why the 26-object outcome is not a direct contradiction

1. The 26-object set was assembled for visible color/detail failures and includes original Fig. 4/6 cases. It is a forensic stress set, not a random sample from Fresh C/B.
2. Twenty UIDs overlap Fresh C, but all 60 shared No Adapter/GFL/LLH prediction PNG hashes differ. The run inputs, saved RGB and per-object outcomes must be treated as separate instances.
3. In the new Fresh C instance, those same 20 UIDs have LLH−GFL CIEDE2000 `−2.838` [−7.833, +2.090], 14/20 lower; FG-PSNR is `+1.785 dB` [0.137, 3.420]. This small UID-overlap subset is uncertain and does not reproduce the old set's positive CIEDE delta. It is a useful provenance sensitivity check, not a replacement validation set.
4. The preceding reproducibility trace found the first observed cross-stack tensor divergence at FP16 initial-latent scaling for three locked examples; the changed latent propagated through denoising, VAE decode and RGB. It proves that the stacks can yield different images, but does not establish that software versions alone explain the full 26-object outcome. The earlier report also did not tensor-trace all 120 affected images.
5. GFL and LLH are not equal-dose controls. LLH raises late deep/middle effective scales from 1.25 to 2.50 and reduces shallow scales. The residual logs verify the schedule but cannot decompose its causal contribution to color or detail.

Thus the apparent conflict reflects at least two things: a genuine GT-complexity-dependent LLH limit and non-identical diagnostic versus confirmation prediction instances, with a confirmed cross-stack reproducibility risk. The available evidence cannot apportion how much each factor contributes to the exact old 26-object statistic.

## Adapter and color interpretation

Fresh C includes a same-input No Adapter/GFL contrast: all six logged model-input tensor hashes match for 300/300 objects, and both saved PNGs match the run output hash manifest. GFL lowers mean CIEDE2000 by `11.228` [−12.929, −9.540] versus No Adapter (227/300 lower), while absolute mean Δa* and Δb* magnitudes increase by `2.389` [1.747, 3.002] and `1.199` [0.500, 1.884], respectively. This mixed result means the adapter is not a systematic cause of larger CIEDE2000 in this cohort, but neither does it certify color-channel fidelity. In the two original Fig. 4 examples, the frozen visual review marked pink/purple cast in No Adapter and under adapter conditions.

The image metric compares generated RGB with the rendered GT. It is a reconstruction discrepancy; without calibrated physical color references, every numeric mismatch should not be called physically impossible. Specific cases previously visually reviewed as pink/purple artifacts can be described as visible, unwanted color shifts relative to their reference renders.

## Decision

- Keep the C3/LLH average metric results attached to their named cohorts and endpoints.
- State the upper-texture failure boundary beside the average gain; do not use the mean to erase Q4 failures.
- Describe diagnostic-26 as a forensic example set and identify the distinct saved-RGB/runtime lineage. Do not use it to estimate population frequency.
- Do not claim a resolved color mechanism, universal color fidelity, or a validated color repair.
- Leave the strict-276 Core-7 as separate supporting metric evidence; it does not add a comparable saved-RGB CIEDE endpoint.

Supporting files: `A_COHORT_HETEROGENEITY.csv`, `A_UID_OVERLAP_SENSITIVITY.csv`, `A_QUARTILE_EFFECTS.csv`, `A_COMPLEXITY_ASSOCIATIONS.csv`, `PAIRED_BOOTSTRAP_STATISTICS.csv`, `C_CAUSAL_PROBE_STATISTICS.csv`, `ALL_COHORT_INPUT_PAIR_AUDIT.csv`, and the prior `../color_failure/final_closure/REPRODUCIBILITY_ROOT_CAUSE.md`.
