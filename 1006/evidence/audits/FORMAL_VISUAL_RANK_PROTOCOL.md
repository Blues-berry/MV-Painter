# Formal visual rank-sampling rule

Frozen before per-object rank extraction on 2026-10-05.

The original Visualization-24 archive remains the outcome-independent visual
sample selected from GT-only properties before method metrics. The following
three added panels are rank-selected illustrations from those same 24
objects; they are not independent or population-level evidence.

## Exact ranking rule

- Comparator: `layer_llh` versus `native_gfl` from the same-draw formal
  FRESH_CONFIRM_300 campaigns.
- Rank metric: FG-PSNR, using the pre-registered H4 primary metric.
- Per-object score: `FG-PSNR(layer_llh) − FG-PSNR(native_gfl)`; higher favors
  LLH.
- Strongest win: largest score.
- Median effect: the object whose score is closest to the ordinary median of
  the 24 scores.
- Strongest loss: smallest score.
- Ties: lexicographically smallest object UID. Each rank may use a distinct
  object. Captions must state rank and score.
- No visual judgment, LPIPS, texture label, or rendered appearance enters
  selection.

The rule is applied only after this lock. The result examples illustrate
within-set extremes and the median; they do not alter the original 24-object
sample or support claims about how often those cases occur.
