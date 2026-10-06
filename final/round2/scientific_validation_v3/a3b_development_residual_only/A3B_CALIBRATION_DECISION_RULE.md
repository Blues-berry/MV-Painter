# A3b development calibration decision rule

Frozen before reading any candidate-high residual log values, 2026-10-05 UTC.

- The fixed candidate highs and target are those in
  `A3B_CANDIDATE_HIGHS.json`; no scale may be tuned from the candidate-high
  run.
- For each object, layer, and active 10-step window, compute the integrated
  multiplier increment as `(high - baseline) × sum(unscaled residual norm)`.
  The unscaled norm is recovered from the post-scale per-point log by dividing
  by that step's actual effective scale. Average first over the 24 development
  objects and then over the five windows for each layer.
- Call the layer-averaged increments approximately balanced only if each of
  the three layer means is within ±20% of the frozen common target
  823.8254719987887. Report all 15 layer-by-window means and the net paired
  post-scale residual-norm change from the baseline logs, regardless of this
  decision.
- This criterion is a feasibility label, not a significance test. If any
  layer fails it, preserve the candidate highs without retuning and treat
  A3b as a bounded-scale layer-window map with the measured dose imbalance.
  No probe image metrics are inspected for this decision.
