# C3/TCAS schedule follow-up audit

Status: **development-only; no holdout promotion unless the pre-frozen gate passes**.

Integrity: **PASS**; objects: `24/24`; steps: `50`; seed: `42`.

## Means

| method | FG-LPIPS ↓ | PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-MAE ↓ | inference s/object |
|---|---:|---:|---:|---:|---:|---:|
| fixed_low | 0.217960 | 16.652503 | 0.360494 | 0.503078 | 1.080655 | 6.501 |
| C3_TCAS | 0.204955 | 18.181559 | 0.406371 | 0.521222 | 0.924045 | 6.470 |
| HLL_eq | 0.218471 | 16.255325 | 0.362287 | 0.502666 | 1.143201 | 6.461 |
| LLH_eq | 0.196588 | 18.444092 | 0.394925 | 0.533531 | 0.897389 | 6.463 |
| LLH_ramp_eq | 0.196482 | 18.166306 | 0.386901 | 0.535077 | 0.923677 | 6.472 |
| LLH_cosine_eq | 0.196964 | 18.091464 | 0.385718 | 0.534689 | 0.931291 | 6.477 |

## New-schedule paired gate

Raw delta is candidate minus comparator; negative is better for FG-LPIPS.

| candidate | comparator | mean Δ FG-LPIPS | 95% CI | win rate | gate |
|---|---|---:|---|---:|---|
| LLH_ramp_eq | fixed_low | -0.021478 | [-0.025040, -0.017970] | 100.0% | required |
| LLH_ramp_eq | C3_TCAS | -0.008473 | [-0.010576, -0.006458] | 100.0% | required |
| LLH_ramp_eq | LLH_eq | -0.000107 | [-0.000783, +0.000563] | 58.3% | diagnostic |
| LLH_cosine_eq | fixed_low | -0.020996 | [-0.024622, -0.017493] | 100.0% | required |
| LLH_cosine_eq | C3_TCAS | -0.007991 | [-0.010161, -0.005925] | 91.7% | required |
| LLH_cosine_eq | LLH_eq | +0.000375 | [-0.000495, +0.001256] | 45.8% | diagnostic |

## Decision

- `LLH_ramp_eq`: **eligible_for_later_validation**.
- `LLH_cosine_eq`: **eligible_for_later_validation**.

The existing LLH-eq condition remains a pre-existing development baseline; neither new schedule is labelled CAI-calibrated. Even a passing development gate would authorize only a separately recorded later validation, not a paper claim or a 276/76 holdout run by itself.

## Provenance

- Pilot SHA-256: `b1e3f8703d5e5f64f19858e73d2a45e4ad4a6a3c11b45fd8dc9b8bf64d36f14f`.
- Protocol SHA-256: `7cd79176fa775b7769cddc451b1955477246d61a6e354c20a0cc2f991b77a17c`.
- Controller SHA-256: `2d11700f40a7edd195471571a7a331171fca91bbd6da6a095b0df2708adfb5aa`.
- Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- No dataset, checkpoint, frozen C3/MV-Adapter result, manuscript or response letter was modified.
