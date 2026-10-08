# Analysis Method Changelog

## 2026-10-08 — CIEDE aggregation aligned to frozen R1 diagnostic code

A first CPU pass computed CIEDE2000 as one pooled foreground-pixel mean over all six tiles. Before inferential summaries were generated, source review of `final_closure/scripts/build_paired_color_results.py` showed that the frozen R1 diagnostic endpoint is the arithmetic mean of six per-view foreground means. The final protocol now uses the frozen six-view equal-weight rule for CIEDE2000 and signed Lab shifts, and quantizes the reconstructed target panel with the same round-to-nearest 8-bit serialization before computing color metrics.

The initial pooled-pixel output is retained as `RGB_RECOMPUTED_CONDITION_METRICS.superseded_pixel_weighted.csv` for audit only. It is excluded from all paired statistics and conclusions. The final analysis script overwrote `RGB_RECOMPUTED_CONDITION_METRICS.csv` using the frozen per-view rule; all reported paired statistics use that final file. This change follows the existing metric implementation, not a result-based choice.

## 2026-10-08 — LLH stage-step boundary corrected from runner semantics

The run manifests explicitly encode `step/49; early<1/3, middle<2/3 => 17/16/17`. The locked schedule description was corrected to use zero-based stage ranges 0–16, 17–32, and 33–49. Thus LLH uses its high deep/middle values on steps 33–49 inclusive (17 steps), yielding requested arithmetic means 1.675 for deep/middle and 0.585 for shallow over 50 steps. This correction is from manifest/runner source inspection and was made before inferential statistics.
