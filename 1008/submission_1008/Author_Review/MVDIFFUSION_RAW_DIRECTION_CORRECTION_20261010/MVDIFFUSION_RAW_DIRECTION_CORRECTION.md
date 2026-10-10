# MVDiffusion raw-contrast direction correction

## Scope and preservation

This correction reanalyses the archived 75-object MVDiffusion panel without changing its run outputs, per-object CSVs, or original analysis files. The frozen `MVDIFFUSION_PAIRED_BOOTSTRAP.json`, summary, and panel report remain intact as historical records; this note and the adjacent recomputation outputs supersede their use as raw condition differences.

The combined panel contains 525 rows: seven conditions (`R0`, `G-FL`, `G-LHL`, `G-LLH`, `L-FIX`, `L-LHL`, `L-LLH`) over the same 75 objects. Each of the six scheduled-condition CSVs has 75 rows and matches its corresponding combined-panel values exactly. Although each run generated a 12-view output grid, the frozen metric manifest scores six target views per object. The five paired comparisons therefore each use 75 matched object pairs for all six finite metrics.

## Direction finding

The archived analysis script defines positive values as favoring the left-hand condition. For higher-is-better PSNR and SSIM it stores `A - B`; for lower-is-better FG-LPIPS, CIEDE2000, and GT-relative texture error it stores `B - A`. Those latter estimates are improvement-coded effects, not raw `A - B` differences. Their bootstrap intervals use the same coding. Converting them to raw differences reverses the signs and swaps the CI endpoints.

For the principal `L-LLH` versus `G-FL` comparison, the 75-object means are:

| Metric | L-LLH | G-FL | Raw L-LLH − G-FL (95% object-bootstrap CI) | Direction |
|---|---:|---:|---:|---|
| PSNR (dB) | 9.524981 | 9.978809 | −0.453828 [−0.752102, −0.160451] | Higher is better; favors G-FL |
| FG-SSIM | 0.295215 | 0.314607 | −0.019393 [−0.029361, −0.009856] | Higher is better; favors G-FL |
| Edge-SSIM | 0.192572 | 0.198513 | −0.005941 [−0.010305, −0.001382] | Higher is better; favors G-FL |
| FG-LPIPS | 0.206582 | 0.203837 | +0.002745 [−0.001808, +0.007632] | Lower is better; no separation |
| CIEDE2000 | 33.174413 | 31.801392 | **+1.373021 [+0.418244, +2.374678]** | **Lower is better; favors G-FL** |
| GT-relative texture error | 0.983991 | 1.066277 | −0.082286 [−0.145316, −0.020073] | Lower is better; favors L-LLH on this reference-statistic error only |

Thus, the previously presented `−1.373` is the benefit-coded value `G-FL − L-LLH` for CIEDE2000, not the raw `L-LLH − G-FL` difference. The layer-wise condition has higher, worse reference-color error in this comparison. The lower GT-relative texture-error value is a closer match to the recorded variation statistics; it does not establish texture fidelity.

## Recalculation and interpretation

The recomputation reads the frozen 525-row panel and all six scheduled per-object CSVs, checks their object sets and values, and reruns the 10,000-resample object bootstrap with seed `20260928`. It reproduces all 30 archived direction-coded means and percentile intervals to numerical precision. `MVDIFFUSION_RAW_CONTRASTS.csv` records raw `A - B`, its raw CI, the corresponding improvement-coded effect and CI, and the count of objects favoring A for every endpoint and comparison. `MVDIFFUSION_PANEL_MEANS.csv` records all seven condition means. `INPUTS_SHA256SUMS.txt` pins the input files.

The corrected raw table is included in Supplementary Table~S12. In `L-LLH − G-FL`, structure endpoints favor G-FL, CIEDE2000 favors G-FL, GT-relative texture error favors L-LLH, and FG-LPIPS does not separate. `L-LLH − G-LLH` and `L-LHL − G-LHL` show the same direction pattern. For the within-layer comparison `L-LLH − L-FIX`, only pointwise PSNR and Edge-SSIM intervals exclude zero. For P5, `G-LLH − G-LHL` raw FG-LPIPS is −0.001371 [−0.002642,−0.000141], so lower error favors G-LLH. The archived `CROSS_BACKBONE_VALIDATION_MVDIFFUSION.md` incorrectly says this P5 term favors G-LHL; that source report is preserved as a historical record, while this correction, `MVDIFFUSION_RAW_CONTRASTS.csv`, and manuscript Table S12 are authoritative. These are 30 unadjusted pointwise intervals and do not support family-wise claims, equivalence, or cross-backbone transfer.

The interface, chronology, compatibility-base, and native-mirror limitations are unchanged. This correction changes metric interpretation and reporting direction only; it does not upgrade the MVDiffusion panel into a matched second-backbone evaluation.
