# C3/TCAS schedule strict-276 follow-up audit

Status: **COMPLETE**; rows per method: `276`.

This is a targeted post-development follow-up on the already-used clean-v2 strict-276 cohort. It is not relabelled as the original confirmatory protocol and does not alter CAI.

## Means

| method | FG-LPIPS ↓ | PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-MAE ↓ |
|---|---:|---:|---:|---:|---:|
| fixed_low | 0.201793 | 17.858528 | 0.303861 | 0.498511 | 0.995810 |
| C3_TCAS | 0.192777 | 18.961306 | 0.346272 | 0.510099 | 0.872187 |
| HLL_eq | 0.199828 | 17.791060 | 0.316350 | 0.499504 | 1.012692 |
| LLH_eq | 0.188731 | 19.236493 | 0.337635 | 0.521079 | 0.848940 |
| LLH_ramp_eq | 0.188393 | 19.180278 | 0.331625 | 0.522790 | 0.853984 |
| LLH_cosine_eq | 0.188627 | 19.142921 | 0.330362 | 0.522693 | 0.857658 |

## New schedules: paired FG-LPIPS

Negative candidate-minus-comparator delta is favorable.

| candidate | comparator | mean delta | 95% CI | win rate |
|---|---|---:|---|---:|
| LLH_ramp_eq | fixed_low | -0.013400 | [-0.014557, -0.012284] | 91.7% |
| LLH_ramp_eq | C3_TCAS | -0.004384 | [-0.005317, -0.003445] | 74.3% |
| LLH_ramp_eq | LLH_eq | -0.000338 | [-0.000605, -0.000063] | 59.8% |
| LLH_cosine_eq | fixed_low | -0.013166 | [-0.014308, -0.012060] | 91.3% |
| LLH_cosine_eq | C3_TCAS | -0.004150 | [-0.005090, -0.003204] | 72.1% |
| LLH_cosine_eq | LLH_eq | -0.000104 | [-0.000397, +0.000193] | 55.8% |

## Boundaries

- Both candidates were fixed before strict-276 inference; neither is selected from strict-276 outcomes.
- The result is schedule-only evidence for the main adapter. It is not MV-Adapter evidence and does not establish cross-backbone generalization.
- No CIEDE2000 or GT-relative texture error is claimed for this main-adapter runner because those fields are not emitted here.
- No manuscript, response letter, checkpoint, dataset or historical result was modified.
