# BUDGET_AND_CAP_CAUSAL_AUDIT — Experiment B

Cohort: FRESH_CONFIRM_300. Artifacts: formal/campaign_B1B2/ (LLH, LFM-EXACT,
LLL, HLL, LHL, LHH), formal/campaign_B3/ (TRUE-GLOBAL x3 uncapped, native
GFL/GFH/GC3, no_adapter), residual_budget_audit.json, HOLM_FAMILY_B1.json,
HOLM_FAMILY_B2.json, pairwise_*.json.

## Exact mean-matched control (B1, H2)

LFM-EXACT = constant (deep 1.675, middle 1.675, shallow 0.585) = the exact
17/16/17 means of LLH. Paired (n=300): LLH − LFM-EXACT = +0.435 dB
FG-PSNR [0.356, 0.516], −0.0045 FG-LPIPS [−0.0052, −0.0039]; Holm p = 0.0002.
Pre-registered equivalence NOT established (FG-PSNR CI upper 0.516 > 0.5).
Verdict: temporal variation contributes a small real advantage beyond budget.

## Equal-duration placement (B2, H3)

LLH > HLL +0.854 dB [0.658, 1.052]; LLH > LLL +0.840 dB [0.747, 0.934];
(descriptive LLH > LHL +0.647). Late-high placement with equal nominal
high-duration is genuinely better. Holm family B2: all p = 0.0004.

## TRUE-GLOBAL causal diagnostics (B3, claim 6)

Native capped vs uncapped uniform at the same nominal scale (paired, n=300):
  * native_gfl vs TRUE-GLOBAL-1.25: +1.60 dB [1.37, 1.82] — the shallow cap
    alone (0.8 vs 1.25 uncapped) is worth +1.6 dB
  * LFM-EXACT vs TRUE-GLOBAL-1.675: +2.99 dB [2.43, 3.55] — layer
    redistribution at IDENTICAL per-layer average budget
  * LLH vs TRUE-GLOBAL-1.675: +3.43 dB; GFH vs TRUE-GLOBAL-2.50: +4.66 dB
All FG-LPIPS deltas favor the layer-aware/native side. The decomposition is
additive: cap (+1.6) + layer redistribution (+3.0) + temporal (+0.4) explains
the total without an interaction residual.

Residual budgets (residual_budget_audit.json): log integrated-residual ratios
confirm the dose accounting; e.g., TRUE-GLOBAL-1.25 vs native_gfl deep/middle
log-ratio ≈ 0 (same dose by construction) while shallow differs by the cap.
Cap activation: native schedules cap shallow at 0.8 as documented; uncapped
diagnostics report zero cap events by construction. no_adapter has zero
residuals (excluded from ratios).

## Interpretation guards

TRUE-GLOBAL conditions are causal diagnostics only — unstable by design
(shallow uniform injection is destructive at matched dose: see A3 shallow
−6 dB) and NOT deployment recommendations. No capped/uncapped numbers are
pooled anywhere.