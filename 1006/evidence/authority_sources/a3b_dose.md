# A3b dose-feasibility audit

Date: 2026-10-05. This is an analysis of the frozen probe-24 residual
statistics only; no FRESH_CONFIRM_300 metric outcome was used to set these
values.

## Constraint from the frozen native operating range

The frozen A3 calibration has baseline scales
deep=1.25, middle=1.25, shallow=0.50; native caps are
deep=3.0, middle=3.5, shallow=0.8. Probe-24 baseline window magnitudes are
deep=65,636.47, middle=14,688.96, and shallow=2,746.08. Under the frozen
linear dose rule, an equal incremental target C requires
delta_l=C/mean(M_l).

To remain inside the shallow cap, the largest possible shallow increment is
0.30. The largest common target is therefore

    Cmax = 0.30 × 2,746.0849 = 823.8255

This yields proposed A3b highs:

| Group | Baseline | Delta | High | Cap |
|---|---:|---:|---:|---:|
| Deep | 1.25 | 0.012551 | 1.262551 | 3.0 |
| Middle | 1.25 | 0.056085 | 1.306085 | 3.5 |
| Shallow | 0.50 | 0.300000 | 0.800000 | 0.8 |

The common target is only 1.004% of A3's frozen C=82,045.59, which kept the
deep increment at the native A2 value 1.25. This is the maximum equal-dose
increment allowed by the frozen shallow operating cap; increasing the common
target would require shallow scale >0.8 and would violate the A3b restriction.

## Interpretation and next step

The equal-dose and native-range constraints sharply limit the size of a full
three-layer intervention. A development-only residual calibration was run
before formal FRESH_CONFIRM_B outputs; it inspected only post-scale residual
logs, not predictions or image metrics.

### Frozen residual-only calibration result

Candidate highs remain unchanged at deep=1.262551, middle=1.306085, and
shallow=0.800000. Across 24 development objects and five 10-step windows, the
mean proxy increment was 658.98 (deep), 657.41 (middle), and 1,639.28
(shallow), against the frozen target 823.83. Relative errors are −20.01%,
−20.20%, and +98.98%, respectively. The predeclared criterion requires every
layer to lie within ±20%; therefore the candidate is **not approximately
layer-balanced**. The deep estimate misses the threshold by a small amount,
but the shallow estimate is nearly twice the target and makes the overall
failure material.

| Layer | W1 | W2 | W3 | W4 | W5 | Mean over windows | Relative error to target |
|---|---:|---:|---:|---:|---:|---:|---:|
| Deep | 770.52 | 706.70 | 632.37 | 614.10 | 571.23 | 658.98 | −20.01% |
| Middle | 611.87 | 703.19 | 780.81 | 677.16 | 514.01 | 657.41 | −20.20% |
| Shallow | 1,117.31 | 1,769.21 | 1,915.81 | 1,902.03 | 1,492.03 | 1,639.28 | +98.98% |

The candidate highs are retained without retuning. A3b is classified as a
**bounded-dose layer-window map**, not an equal-dose experiment. Its fresh
cohort interaction result may describe the observed bounded intervention, but
cannot by itself establish a dose-independent or equal-dose Layer×Time
mechanism. This qualification is frozen in `A3B_PROTOCOL_LOCK.md` before
FRESH_CONFIRM_B outputs.

### Provenance and duplication check

The initial residual-only pass wrote a live-file hash at process completion,
after the runner had subsequently been extended. It is not used as the
authoritative provenance record. A byte-pinned copy of the runner
(`audit_scripts/frozen_a3b_residual_runner.py`, SHA256
`bcf49f4bdb3995ae80c0e2bd70b04c31936a2fb3347dd9642172b19f27b9c0ae`) was
rerun on the same 24-object list and candidate spec. All 360 per-object,
layer-window residual logs match the first pass byte-for-byte; both shard
manifests are complete; prediction count and metric-row count are zero. The
pinned run is authoritative for this calibration decision.

The A3b primary test remains FG-LPIPS with FG-PSNR secondary. This feasibility
finding does not resolve the interaction claim; it defines the only
cap-compliant equal-dose scale family currently justified by the frozen
development residuals.
