# Statistics Reproducibility Audit (final_audit_20261001, Phase 6.2)

Audit date: 2026-10-01. Scope: analysis-only rerun (zero inference) of the strict-276
confirmation statistics, plus verification of the bootstrap convention against the
published confirmations.

## 1. Rerun result — bitwise reproduction

`scripts/analyze_layer_confirmation_20260930.py` was re-executed as-is (inputs: the
frozen `*_rows.json` files, still on disk and independently rescued under
`rescued_tmp_20261001/layer_confirmation_20260930/`).

| Check | Result |
|---|---|
| SHA-256 of `/4T/tmp/mvpainter-layer-confirmation-20260930/confirmation_analysis.json` before rerun | `d308f6a957db121f96abba7d879c9cd56d092d040f0baa659314089b32322a1b` |
| SHA-256 after rerun | `d308f6a957db121f96abba7d879c9cd56d092d040f0baa659314089b32322a1b` (identical) |
| Parsed-JSON equality vs the rescued audit copy | True |

The published analysis JSON is **bitwise reproducible** from the frozen per-object rows.

## 2. Bootstrap convention (verified in code)

- Seed: `random.Random(20260930)` (hardcoded `BOOT_SEED = 20260930`).
- Resamples: 10,000 (`BOOT_N = 10000`).
- Unit: object-level — resampling with replacement over the 276 per-object paired
  differences (`rng.choice(diffs)`), not per-metric or per-view.
- Percentile method: empirical quantiles of the sorted resample means, indices
  `[250, 9750]` (i.e., the 2.5th/97.5th percentile positions, no interpolation).
- Sign handling: benefit-oriented `BETTER` map before differencing (see
  `metric_direction_audit.md`).

## 3. Cross-document consistency of the headline numbers

The rerun reproduces, digit for digit:

| Comparison | Metric | mean diff | 95% CI | win rate |
|---|---|---:|---|---|
| layer_llh − global_fixed_low | fg_psnr | +3.244298437367315 | [2.93626980289169, 3.54243165988853] | 242/276 |
| layer_llh − layer_fixed_mean | fg_psnr | +0.8750078190064084 | [0.7687482086644657, 0.9817908639493196] | 240/276 |
| layer_llh − layer_lhl | fg_psnr | +1.0007615409035613 | [0.9068509893140931, 1.0968791315521018] | 261/276 |

These equal the numbers in `R0_R1_STABILITY_SUMMARY.json` (R0 block) and in
`STRICT276_GLOBAL_FIXED_LOW_CONFIRMATION.md`: the R0 block of the robustness summary is
numerically identical to the confirmation analysis (same frozen rows, consistent
provenance); the R1 block is the independent realization rerun (seed 10042+idx) whose
paired deltas agree with R0 to ≈0.01 dB on every metric.

## 4. Bootstrap implementations in the evidence base

Two implementations exist, both seed 20260930, both object-level percentile:

1. `analyze_layer_confirmation_20260930.py` — Python `random.choice` loop, sorted-sum
   quantiles.
2. `analyze_robustness1_20260930.py` / `analyze_layerwise_panel_20260930.py` /
   `analyze_mvdiffusion_panel_20260930.py` — `np.random.default_rng(seed)` integer-index
   resampling with `np.quantile`.

Different RNG streams mean their CI endpoints are not expected to be identical across
implementations for the same data; within each document, numbers are internally
consistent and reproducible. The R0 block identity in §3 holds because it originates
from the same computation as (1), not by coincidence.

## 5. Verdict

The confirmation statistics are deterministic, seed-fixed, object-level, and bitwise
reproducible. Combined with `metric_direction_audit.md` (no direction errors), the
statistical layer of the Round-2 evidence base passes the reproducibility audit.
