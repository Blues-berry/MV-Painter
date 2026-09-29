# C3/TCAS full baseline audit

Date: 2026-09-29 UTC

## Decision

The existing C3 evidence is frozen as the complete baseline available in this workspace. No C3 inference was repeated and no frozen result was overwritten. The main-adapter 276-object evidence and MV-Adapter Exact-76 evidence remain separate.

Audit errors: **0**.

## Main adapter: clean-v2 strict 276

- Records: `1104` = `276 objects × 4 schedules`.
- Schedules: `fixed_mean, hll, llh, c3_lhl`.
- Formal stage metrics finite: **True**.
- Serialized Full-SSIM metrics finite: **True**.
- Local verified original GLBs represented in the strict-276 provenance join: `10/276`.
- CIEDE2000 and GT-relative texture error are not fields in this main-adapter stage CSV; they are not inferred from other metrics.
- The main cohort is therefore labelled clean-v2 source-stratified, not all-Exact-Mesh.

### Main paired comparisons

All deltas are C3/LHL minus comparator; lower-is-better metrics use a direction-aware win rate.

| comparator | metric | mean delta | 95% CI | win rate |
|---|---|---:|---|---:|
| fixed_mean | full_psnr | +0.556369 | [+0.525520, +0.589220] | 98.2% |
| fixed_mean | fg_psnr | +0.502875 | [+0.462018, +0.542244] | 95.3% |
| fixed_mean | fg_ssim | +0.032083 | [+0.028966, +0.035172] | 89.1% |
| fixed_mean | edge_ssim | +0.001696 | [+0.000611, +0.002782] | 51.1% |
| fixed_mean | fg_lpips | -0.003797 | [-0.004341, -0.003260] | 77.5% |
| fixed_mean | full_lpips | +0.001420 | [+0.000778, +0.002072] | 38.8% |
| hll | full_psnr | +1.470777 | [+1.407973, +1.539201] | 100.0% |
| hll | fg_psnr | +1.176507 | [+1.111167, +1.242206] | 99.3% |
| hll | fg_ssim | +0.089354 | [+0.083319, +0.095423] | 98.9% |
| hll | edge_ssim | +0.036698 | [+0.034684, +0.038705] | 99.6% |
| hll | fg_lpips | -0.010155 | [-0.011075, -0.009251] | 90.6% |
| hll | full_lpips | -0.012541 | [-0.013309, -0.011795] | 97.1% |
| llh | full_psnr | -0.268100 | [-0.311101, -0.227797] | 14.9% |
| llh | fg_psnr | -0.177084 | [-0.230539, -0.130784] | 28.6% |
| llh | fg_ssim | -0.008851 | [-0.011455, -0.006291] | 36.6% |
| llh | edge_ssim | -0.035301 | [-0.036581, -0.034031] | 0.0% |
| llh | fg_lpips | +0.001896 | [+0.001205, +0.002578] | 33.7% |
| llh | full_lpips | +0.008658 | [+0.007465, +0.009831] | 21.7% |

Serialized Full-SSIM is kept as a separate saved-artifact branch; it is not mixed with the formal pre-save metric column.

| comparator | saved-artifact Full-SSIM mean delta | 95% CI | win rate |
|---|---:|---|---:|
| fixed_mean | +0.007486 | [+0.006736, +0.008262] | 90.6% |
| hll | +0.021508 | [+0.019845, +0.023185] | 99.6% |
| llh | -0.001697 | [-0.002047, -0.001340] | 19.9% |

## MV-Adapter: Exact 76

- Unified rows: `11` methods, each with 76 Exact objects and six requested metrics.
- Exact calibration/holdout checks: `calibration_exact_24, calibration_exact_selected_pair_24, direct_lhl_shape_transfer, equal_budget_follow_up, historical_exact_holdout, matched_range_follow_up`.
- Recovered GLB records in the manifest: `10/10` Exact.
- Detailed paired bootstrap remains in `final/round2/mv_adapter/MV_ADAPTER_PAIRED_COMPARISONS.json`.
- CAI remains undefined/set-valued; no C3/LHL holdout result is renamed CAI-calibrated.

## 24-object pilot gate

### TRB_TCAS

- Integrity checks: `True`; FG-LPIPS present: `True`; calibration timing present: `True`.
- Decision: **do_not_promote**.

| comparator | mean Δ FG-LPIPS | 95% CI | win rate favoring candidate |
|---|---:|---|---:|
| fixed_low | -0.005508 | [-0.007830, -0.003391] | 83.3% |
| C3_TCAS | +0.001302 | [+0.000092, +0.002538] | 41.7% |

- Promotion gate passed: **False**. No strict-276 TRB holdout is authorized.

### TRB2_TCAS

- Integrity checks: `True`; FG-LPIPS present: `True`; calibration timing present: `True`.
- Decision: **do_not_promote**.

| comparator | mean Δ FG-LPIPS | 95% CI | win rate favoring candidate |
|---|---:|---|---:|
| fixed_low | -0.006856 | [-0.009790, -0.004125] | 87.5% |
| C3_TCAS | -0.000045 | [-0.000827, +0.000670] | 45.8% |

- Promotion gate passed: **False**. No strict-276 TRB holdout is authorized.

## Evidence boundaries

- Exact Mesh provenance is satisfied for the MV-Adapter 24/76 cohort; it is not automatically satisfied for the main clean-v2 276 stage table.
- Calibration/holdout disjointness is established for MV-Adapter Exact 24/76; main 276 is a strict holdout relative to the clean-v2 probe list but not a second-bone Exact-Mesh claim.
- Official MV-Adapter pretraining UID disjointness remains unknown.
- Stage effects are supported by paired tables; they do not establish a unique CAI schedule or a universal cross-backbone gain.
- No absolute PSNR comparison is made between the two backbones.

## New schedule status

The independent schedule-only development protocol is frozen in `C3_TCAS_NEW_SCHEDULE_PROTOCOL_20260929.json/.md`. It is limited to the 24-object development cohort and does not authorize holdout inference until its gate is evaluated.
