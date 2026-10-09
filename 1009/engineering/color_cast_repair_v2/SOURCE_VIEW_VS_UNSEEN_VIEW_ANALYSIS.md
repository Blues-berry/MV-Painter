# Source-view versus unseen-view color analysis

## Identity and measurement

The source view is confirmed from `MVPainter/src/data/mvpainter_dataset.py` and the locked unique6 order, not inferred from the displayed grid. It is tile 0: selected view 014 in the reverse branch and 000 otherwise. The condition image receives a condition-only random stretch/compress and canvas transform, while target RGB stays untransformed; the observed condition/target foreground-mask IoU is 0.3215–0.8053 on the four-object cohort. Therefore, color comparisons between the transformed condition and target use eroded robust foreground Lab medians, not pixel registration. GT-relative image metrics use the geometry foreground mask. The pre-locked magenta residual statistic is descriptive only.

## Phase A per-object readout

| Object | Source view | Condition median a*/b* | GT source median a*/b* | GFL source median a*/b* | GFL source ΔE00 | GFL unseen mean ΔE00 | GFL unseen magenta fraction |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fig. 4 row 1 (`eac4…`) | 014 | 19.48 / 15.36 | 20.08 / 15.58 | 17.51 / 15.94 | 18.20 | 19.15 | 3.92% |
| Fig. 4 row 2 (`ea760…`) | 014 | 4.79 / 9.04 | 4.76 / 9.07 | 13.61 / 19.95 | 18.39 | 19.05 | 0.05% |
| Normal (`c76a…`) | 000 | −0.08 / −0.13 | −0.00 / −0.14 | 8.45 / 15.63 | 21.56 | 24.08 | 1.03% |
| High texture (`8bd9…`) | 000 | 2.52 / 8.81 | 2.56 / 9.05 | 16.30 / 21.74 | 20.58 | 22.05 | 0.35% |

The frozen magenta fraction counts foreground pixels where output-minus-GT Δa* ≥ +5 and Δb* ≤ −5. It is low for several objects despite their large overall color error, so it is not a general perceptual cast detector. Per-view L*/a*/b*, chroma, hue, CIEDE, residuals and magenta fractions are in `runs/phase_b/A_PER_VIEW_COLOR_READOUT.csv`; source robust distributions and condition identities are in `A_SOURCE_COLOR_STATISTICS.csv`.

## Causal response and view split

VAE-only color perturbations did not reliably transfer source chroma into the output. Global-embedding-only a* perturbations produced the locked directional response on all four objects for both signs across tile 0 and the mean of five unseen views; global-embedding b* response was asymmetric (4/4 for +, 2/4 for −). This shows that the embedding path can move color in the source and unseen views. It does not show that either direction improves GT-relative error.

Under C1, the paired five-view mean FG-CIEDE2000 decreased on all four development objects (mean −1.5602, 95% paired object bootstrap CI [−2.2621, −0.6299]); source-view color metrics also improved numerically on average. However, the Fig. 4 row 1 visual change was not clear and the Fig. 4 row 2 candidate introduced a cyan/blue rim while retaining mismatch. Therefore, unseen-view numeric improvement in this small development cohort is not independent validation and does not establish a successful multi-view repair. The high-texture result is one development object only, not a cohort-level Q4 safety result.

## Source-cache discrepancy

Fresh B's input-only audit shows stored global embeddings do not match embeddings recomputed from either the exact condition tensor or raw selected source RGB for any of 150 objects. On selected-view-014 cases, the cache has a systematic view-000 correspondence signal. Refreshing the cache changes the two Fig. 4 failure outputs in opposite directions, while the normal and high-texture outputs remain pixel-identical. Thus cache provenance is a plausible object-dependent contributor, not a sufficient or reliably corrective explanation.

All development outputs and the relevant source/candidate SHA-256 identities are in the per-view and paired CSVs and in `C1_DEV_MANUAL_REVIEW.json`. Fresh B repair predictions and metrics remain sealed.
