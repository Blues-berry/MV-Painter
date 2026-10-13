# TRB Quality-Improvement Audit

Date: 2026-09-29 UTC  
Scope: 24-object development only. No 276-object holdout inference was run.

## Decision

The original strict `TRB_TCAS` pilot does **not** pass the promotion gate:
it improves FG-LPIPS over fixed-low, but is worse than C3 on the primary
metric. The budget-preserving repair `TRB2_TCAS` removes the identified
under-dosing defect and reaches essentially the same FG-LPIPS as C3, but it
still does not produce a statistically stable improvement over C3. The 276
holdout therefore remains locked.

The result is useful method diagnosis, not a paper-level quality claim.

## Completed strict TRB pilot

Artifact:
`outputs/trb_clean_v2_dev24_seed42_lpips_r1/pilot_results.json`

Protocol checks passed: 24 objects, `unique6`, seed 42, 50 steps, fixed
checkpoint, shared object conditions, finite metrics, and explicit calibration
timing. The primary metric is FG-LPIPS, lower is better.

| Condition | FG-LPIPS | PSNR | FG-SSIM | Edge-SSIM | FG-MAE |
|---|---:|---:|---:|---:|---:|
| Fixed-low | 0.140398 | 22.261096 | 0.573284 | 0.589674 | 0.578212 |
| C3-TCAS | 0.133587 | 22.970906 | 0.589576 | 0.595492 | 0.539827 |
| HLL-eq | 0.148141 | 21.110972 | 0.572931 | 0.587958 | 0.677750 |
| LLH-eq | 0.123080 | 24.369059 | 0.598650 | 0.614905 | 0.475143 |
| TRB-TCAS | 0.134890 | 22.699791 | 0.590196 | 0.594956 | 0.559827 |

Object-level paired bootstrap: 10,000 resamples, seed `20260929`, percentile
95% CI.

| Contrast | FG-LPIPS delta (TRB minus comparator) | Win rate favoring TRB |
|---|---:|---:|
| TRB vs fixed-low | -0.005508 `[-0.007830,-0.003391]` | 20/24 = 83.3% |
| TRB vs C3 | +0.001302 `[+0.000079,+0.002549]` | 10/24 = 41.7% |
| TRB vs HLL-eq | -0.013251 `[-0.017533,-0.009256]` | 24/24 = 100.0% |
| TRB vs LLH-eq | +0.011810 `[+0.009277,+0.014311]` | 0/24 = 0.0% |

The original TRB passes the fixed-low comparison but fails the required
fixed-low **and** C3 gate. It also does not dominate the equal-budget LLH
condition.

## Calibration cost

The original TRB calibration pass took a mean `6.082 s/object` and exactly 50
additional denoising steps. Its mean inference time was `6.260 s/object`, so
the controller total was `12.342 s/object`, approximately `+103.2%` wall-clock
relative to the C3 inference pass. The robust protocol-level cost statement is
one extra 50-step pass per object; wall-clock values are host-load dependent.

The pilot was run while another GPU process was present, so the step count is
the primary cost accounting and the measured wall-clock is retained as an
observed run value rather than a hardware-independent benchmark.

## TRB2 repair

Protocol: `STRICT_TRB2_PILOT_PROTOCOL_20260929.md`  
Artifact: `outputs/trb2_clean_v2_dev24_seed42/pilot_results.json`

TRB2 changes only the diagnosed budget path:

- calibrates actual post-cap residual RMS rather than raw RMS multiplied by a
  nominal scale;
- weights residual energy by element count;
- starts at the C3 scale and attenuates only when current residual exceeds the
  calibrated budget;
- does not increase above C3 and preserves the fixed-low floor.

| Condition | FG-LPIPS | PSNR | FG-SSIM | Edge-SSIM | FG-MAE |
|---|---:|---:|---:|---:|---:|
| Fixed-low | 0.140398 | 22.261096 | 0.573284 | 0.589674 | 0.578212 |
| C3-TCAS | 0.133587 | 22.970906 | 0.589576 | 0.595492 | 0.539827 |
| HLL-eq | 0.148141 | 21.110972 | 0.572931 | 0.587958 | 0.677750 |
| LLH-eq | 0.123080 | 24.369059 | 0.598650 | 0.614905 | 0.475143 |
| TRB2-TCAS | 0.133542 | 22.871493 | 0.591021 | 0.595396 | 0.545040 |

| Contrast | FG-LPIPS delta (TRB2 minus comparator) | Win rate favoring TRB2 |
|---|---:|---:|
| TRB2 vs fixed-low | -0.006856 `[-0.009790,-0.004125]` | 21/24 = 87.5% |
| TRB2 vs C3 | -0.000045 `[-0.000827,+0.000670]` | 11/24 = 45.8% |
| TRB2 vs HLL-eq | -0.014598 `[-0.019578,-0.009895]` | 23/24 = 95.8% |
| TRB2 vs LLH-eq | +0.010463 `[+0.007900,+0.012786]` | 1/24 = 4.2% |

TRB2 is effectively tied with C3 on FG-LPIPS, not a stable improvement. It
also has lower PSNR than C3 by `-0.0994 dB`, CI
`[-0.1547,-0.0464]`, and higher FG-MAE by `+0.00521`, CI
`[+0.00080,+0.00993]`. The repair corrected the accounting defect but did not
create a practical-quality gain.

TRB2 calibration cost was `6.835 s/object` and its inference time was
`7.074 s/object`, for `13.909 s/object` total. This is approximately `+105.1%`
relative to C3 wall-clock and still requires one extra 50-step pass.

## Interpretation

The experiments separate three statements:

1. Residual-aware control can improve fixed-low on this 24-object probe.
2. The original TRB controller did not improve the already strong C3 baseline;
   its apparent difference was partly caused by implicit under-dosing.
3. Correcting that under-dosing makes TRB2 nearly match C3, but does not make it
   better, while LLH-eq is the strongest observed condition on this probe for
   FG-LPIPS, PSNR, Edge-SSIM and FG-MAE.

Therefore, no further TRB variant or 276-object lock is justified under the
current finite-pilot authorization. Selecting LLH after observing this pilot
would be a post-hoc schedule choice, not CAI calibration. The numbers remain
internal development evidence and must not be added to the paper as a new
positive result.

## Reproducibility

The TRB2 audit passed all of the following: 24 rows per condition, five
conditions, finite primary and secondary metrics, `unique6`, seed 42, 50
steps, object-list hash, checkpoint hash, per-object calibration records and
progress checkpoint. The implementation changes are in the experimental
branch copy of `geotex/residual_budget_pilot.py`; the main worktree was not
modified.
