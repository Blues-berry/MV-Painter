# Metric Direction Audit (final_audit_20261001, Phase 6.1)

Audit date: 2026-10-01. Scope: every analysis surface that produces deltas, win rates,
CIs, or rankings for paper-facing Round-2 evidence. Convention under audit:
**benefit-oriented deltas — for higher-better metrics delta = A − B, for lower-better
metrics delta = B − A, so positive always means "the first-named condition is better".**

| Surface | Implementation (verified in code) | Convention | Verdict |
|---|---|---|---|
| Strict-276 confirmation analysis | `scripts/analyze_layer_confirmation_20260930.py` L25-31 `BETTER` map (psnr/ssim +1, lpips −1), L45 `diffs = sign*(a-b)`; win rate counts `d > 0` | positive favors the left (first-named) condition on all 7 metrics | PASS |
| Robustness R0/R1 | `scripts/analyze_robustness1_20260930.py` benefit transform; formalized in `main_backbone_robustness1_20260930/METRIC_SIGN_CONVENTION_ERRATUM.md` (2026-10-01): reported deltas are direction-adjusted, NOT raw arithmetic differences (example: "LLH − GFL FG-LPIPS = +0.0308" means LLH's LPIPS is 0.0308 lower) | positive favors the first-named condition | PASS (erratum on file) |
| Core-7 completion | `core7_same_runner_completion_20261001/paired_bootstrap_core7.json` header: "raw delta = first-named minus second; NO sign reversal; direction column states metric direction"; the report annotates direction per comparison (e.g. FG-LPIPS −0.0449* = LLH better) | raw arithmetic delta with explicit per-metric direction annotation | PASS (different presentation from the benefit-oriented surfaces — readers must not mix the two; raw and benefit-oriented deltas agree in sign for higher-better metrics and differ for lower-better) |
| MV-Adapter 76 panel | `final/round2/mv_adapter/analyze_layerwise_panel_20260930.py` L22 `LOWER_BETTER = {fg_lpips, ciede2000, gt_relative_texture_error}`, L85 `delta = (a-b) if not lower else (b-a)`, L98 `"direction": "positive_favors_left"` | positive favors the left condition | PASS |
| MVDiffusion 75 panel | `scripts/analyze_mvdiffusion_panel_20260930.py` L25/L90/L104 — same `LOWER_BETTER` pattern | positive favors the left condition | PASS |
| Texture audit (this round, `scripts/audit_strict276_texture_20261001.py`) | `paired_table`: higher-better → a−b, lower-better (CIEDE2000, symmetric log errors, GT-relative probe distances) → b−a | positive favors `layer_llh`/base condition | PASS |
| Archived OFFICIAL_LAYER_LHL_REPORT.md | L4: raw arithmetic deltas in tables, direction-corrected win rates | **mixed** | N/A — document is Case-B excluded; never cite its delta signs |

## Findings

1. **All active surfaces share one convention.** Any "delta" in the active evidence base
   reads as: *positive = the first-named/left condition is better on that metric*,
   regardless of the metric's native direction. Win rates, stability labels, and rankings
   apply the same transform (verified in each script listed above).
2. **Reading hazard (documented, not an error):** direction-adjusted deltas must not be
   read as raw metric arithmetic. The most exposed instance is FG-LPIPS: a table entry
   `+0.0308` corresponds to a raw LPIPS difference of `−0.0308`. The robustness erratum
   states this explicitly; this audit extends the statement to every active surface.
3. **CI and bootstrap consistency:** CIs are computed on the same direction-adjusted
   per-object deltas as the means and win rates in every audited script — no surface
   mixes adjusted means with unadjusted CIs.
4. **Lower-better sets differ, correctly, per metric surface:** the confirmation set has
   no CIEDE2000/GT-texture columns, so its `BETTER` map covers only the 7 runtime
   metrics; the cross-backbone panels add `ciede2000` and
   `gt_relative_texture_error` to the lower-better set. No metric is classified
   inconsistently between surfaces (FG-/Full-/Edge-SSIM and PSNR higher-better
   everywhere; LPIPS/ΔE00/GT-texture lower-better everywhere).
5. No direction error was found. No correction is required.
