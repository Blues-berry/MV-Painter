# Reproduced core evidence table

| Cohort / contrast | Endpoint | N | Mean paired delta [95% bootstrap CI] | Favorable objects |
|---|---|---:|---:|---:|
| A2 discovery: middle W5 − baseline | FG-PSNR (dB) | 300 | 0.514546 [0.460981, 0.569517] | 84.0% |
| A2 discovery: middle W5 − baseline | FG-LPIPS | 300 | -0.00640491 [-0.00707501, -0.00573205] | 84.7% |
| FRESH_CONFIRM_B: LLH − LFM-EXACT | FG-PSNR (dB) | 150 | 0.325165 [0.209001, 0.445849] | 54.0% |
| FRESH_CONFIRM_B: LLH − LFM-EXACT | FG-LPIPS | 150 | -0.00460382 [-0.00562942, -0.00356787] | 76.0% |
| FRESH_CONFIRM_B: LLH − HLL | FG-PSNR (dB) | 150 | 0.686771 [0.403504, 0.981304] | 45.3% |
| FRESH_CONFIRM_B: LLH − HLL | FG-LPIPS | 150 | -0.0109816 [-0.0134913, -0.00850868] | 80.7% |
| FRESH_CONFIRM_B: LLH − LLL | FG-PSNR (dB) | 150 | 0.733945 [0.597358, 0.875424] | 79.3% |
| FRESH_CONFIRM_B: LLH − LLL | FG-LPIPS | 150 | -0.00844818 [-0.0102861, -0.00659269] | 82.0% |
| FRESH_CONFIRM_B: HLL − LLL (exploratory) | FG-PSNR (dB) | 150 | 0.0471744 [-0.119671, 0.208294] | 66.0% |
| FRESH_CONFIRM_B: HLL − LLL (exploratory) | FG-LPIPS | 150 | 0.00253346 [0.00155103, 0.00354302] | 40.0% |

All favorable-object rates are direction-adjusted. A2 uses condition minus baseline; B uses LLH minus LFM-EXACT. FG-PSNR is higher-is-better and FG-LPIPS is lower-is-better.

## Validated A2 interaction results

FG-LPIPS: object-cluster Wald χ²(8) = 481.081; p = 8.045e-99; interaction share = 43.5%; RMSE/cell = 0.00169509.
FG-PSNR: object-cluster Wald χ²(8) = 1879.963; p <1e-300; interaction share = 56.8%; RMSE/cell = 0.122154.

A2 is labeled discovery/exploratory; B is a separate frozen confirmation cohort. Bootstrap: 10,000 paired object resamples, seed 20261002. The LLH−LFM-EXACT intervals fall inside the frozen practical-equivalence margins (±0.5 dB PSNR; ±0.01 LPIPS). HLL−LLL was post-unblinding exploratory; its FG-PSNR interval crosses zero, so the full two-endpoint directional signature is not supported.
