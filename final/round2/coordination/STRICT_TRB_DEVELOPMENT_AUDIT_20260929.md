# Strict TRB development audit

Status: **NOT PROMOTED — no holdout authorized**.

Pilot: `/4T/tmp/mvpainter-adaptive-control/outputs/trb_clean_v2_dev24_seed42_lpips_r1/pilot_results.json`
Protocol: clean-v2 24-object development set, unique6, 50 steps, shared object latent, paired object bootstrap.
The audit is an evidence gate; it does not turn this development pilot into a paper result.

## Integrity

- Integrity checks: **PASS**.
- Maps: `168/168`; budgets: `24/24`.
- Checkpoint/object-list hashes and shared object sets: **verified**.

## Method means

| condition | FG-LPIPS ↓ | PSNR (normalized) | FG-SSIM | Edge-SSIM | FG-MAE ↓ | inference s | total s |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_low | 0.140398 | 22.261 | 0.573284 | 0.589674 | 0.578212 | 6.145 | 6.145 |
| C3_TCAS | 0.133587 | 22.971 | 0.589576 | 0.595492 | 0.539827 | 6.075 | 6.075 |
| HLL_eq | 0.148141 | 21.111 | 0.572931 | 0.587958 | 0.677750 | 6.065 | 6.065 |
| LLH_eq | 0.123080 | 24.369 | 0.598650 | 0.614905 | 0.475143 | 6.099 | 6.099 |
| TRB_TCAS | 0.134890 | 22.700 | 0.590196 | 0.594956 | 0.559827 | 6.260 | 12.342 |

## Primary paired gate

Raw delta is `TRB − comparator`; negative is better for FG-LPIPS.

| comparator | mean Δ FG-LPIPS | 95% CI | win rate | stable improvement |
|---|---:|---:|---:|---|
| fixed_low | -0.005508 | [-0.007830, -0.003391] | 83.3% | yes |
| C3_TCAS | +0.001302 | [+0.000092, +0.002538] | 41.7% | no |

Gate decision: **fail**. A CI crossing zero is treated as uncertainty, not equivalence.

## Calibration cost

Mean calibration time: `6.082` s/object. TRB total mean: `12.342` s/object; fixed-low inference mean: `6.145` s/object; ratio: `2.01×`.

Secondary-metric caveat: The pilot's psnr field is the normalized-image PSNR emitted by compute_probes, not a foreground-masked FG-PSNR; it was not used for the promotion gate.

## Interpretation

The development result is a method-screening result. It can authorize at most one locked holdout only when the integrity checks pass and the primary FG-LPIPS CI is strictly better than both fixed-low and C3_TCAS. It does not establish a universal backbone-transfer claim or a CAI winner.
