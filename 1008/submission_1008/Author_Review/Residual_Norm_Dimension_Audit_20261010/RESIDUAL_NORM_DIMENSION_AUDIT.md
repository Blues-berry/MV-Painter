# Residual-norm dimension audit — 2026-10-10

## Finding

The A3b report's **0/2,250 common-support** result is not a dimension-normalized cross-layer dose-support test. The frozen analysis combines the three wrapper $L_2$ norms within each layer and step as $\sqrt{\sum_i L_{2,i}^2}$, then sums that value over the active 10-step window. It compares those raw norms across deep, middle, and shallow groups. The trace records each correction's height and width, but not its channel count; in the inspected A3b traces the three wrappers in each group have spatial sizes 24×16 (deep), 48×32 (middle), and 96×64 (shallow). Thus the compared vectors have different feature dimensions, and raw $L_2$ can change with tensor size even when per-entry magnitudes are comparable. Raw $L_2$ remains a valid norm for each tensor, but these unnormalized values cannot establish that the groups lack common dose support. The central-90% intervals 56,359–79,927, 11,421–19,336, and 2,816–5,193 and their empty intersection must not be interpreted as evidence that the layer groups lack common realized-dose support.

The same limitation applies to the A3b linear/log sensitivity models that use the integrated raw $L_2$ as a covariate. They are post-outcome, post-treatment associations and do not identify a dose-independent layer-by-window effect. The manuscript and response therefore withdraw the numeric cross-layer support conclusion while preserving the observed response heterogeneity under the tested interventions and the conservative causal boundary.

## Development-phase calibration

The frozen probe-24 development calibration used the same cross-layer raw-$L_2$ construction to define a common increment target and choose A3b's fixed scale values. Its arithmetic is reproducible, but because the group tensors have different feature dimensions, the common-target and ±20% layer-balance labels are not dimension-validated. We therefore withdraw both the claim that the candidate is an equal-dose target and the claim that the candidate failed a valid cross-layer dose-balance gate. The recorded high values remain the settings used in the A3b map; the outcomes remain valid observations for those settings. No replacement target was tuned from the A3b outcomes.

## Per-entry magnitude sensitivity

As a descriptive check, `audit_residual_norm_dimension_sensitivity.py` reads the frozen A3b traces and, for each object/layer/window, sums over the 10 active steps the equal-wrapper mean of logged post-scale `mean_abs`. This statistic is normalized by each correction tensor's element count, avoiding the direct spatial-size multiplier in raw $L_2$. It is still a post-hoc summary, weights wrappers equally, and does not equalize feature semantics, hidden-state scale, or intervention dose. It is not a common-support gate or causal adjustment.

| Layer | Cell rows | 5th percentile | Median | 95th percentile |
|---|---:|---:|---:|---:|
| Deep | 750 | 24.6783 | 30.0431 | 36.9269 |
| Middle | 750 | 4.0965 | 6.1399 | 8.0581 |
| Shallow | 750 | 0.5157 | 0.8084 | 0.9273 |

The ranges also separate for this chosen scalar summary. This describes different per-entry correction amplitudes in the tested feature groups; because the summary was constructed after the fact and does not define an equal-dose intervention, it does not restore or refute valid cross-layer dose support.

## Fresh C table correction

Supplementary Table S4 now reports the median of wrapper-level per-entry mean absolute correction (`correction_mean_abs_median`) for its representative Fresh C rows. This avoids presenting raw $L_2$ values across differently sized feature maps as directly comparable. The table remains an implementation log summary, not an intervention-dose or quality estimate. Full raw $L_2$ values remain in the source accounting CSV for within-record traceability.

## Provenance

- Frozen A3b traces: `/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/formal/campaign_FRESH_CONFIRM_B_20261005/residual_logs/`; 2,250 selected object-condition JSON files. Canonical trace-manifest SHA-256: `b57fb821a0777bf1a30d64b88fe61b759714f9a003fa751170521bf823f161a5`.
- Original A3b aggregation script: `final/round2/scientific_validation_v3/audit_scripts/analyze_fresh_confirm_b_dose_sensitivity.py`, SHA-256 `97698347f0794f8bb60949ff3d6cdd12ce17e3dffda30d0f07da28fd138e4b6f`.
- Frozen wrapper implementation: `1006/code/reproducibility_release/MVPainter/mvpainter/model_unet_geotex.py`, SHA-256 `b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0`.
- Fresh C accounting table used by S4: `1008/audits/source_evidence/r2/accounting/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv`, SHA-256 `ef35c5abcc65a7a1e4b8a1fd89e6ad0fb23864c4288d273b6f1c8c619d71fff6`.
- Derived object/layer/window values: `A3B_PER_ENTRY_CORRECTION_SENSITIVITY.csv` and its machine-readable summary JSON are stored beside this report.

This is a CPU-only re-analysis of saved logs; it ran no model inference and changed no source evidence.
