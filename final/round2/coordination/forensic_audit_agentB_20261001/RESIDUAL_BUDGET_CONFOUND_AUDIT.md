# RESIDUAL_BUDGET_CONFOUND_AUDIT.md (Phase 15 — agent B)

Question (task doc): does LLH win because of **when** the residual is applied,
or because **more effective residual** is applied? All numbers below are
benefit-oriented (positive = first method better) and recomputed from
`final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv` (same-runner,
strict-276) in `phase1b15_effective_budget.py`.

## Pairwise same-runner deltas (benefit-oriented)

| pair | FG-PSNR | Full-PSNR | FG-LPIPS | notes |
|---|---|---|---|---|
| LLH − GFL | **+3.244** (242/34) | +2.599 (249/27) | +0.0308 | headline |
| LFM − GFL | **+2.369** (245/31) | +1.288 (225/51) | – | constant scales, higher deep/mid budget |
| LLH − LHL | **+1.001** (261/15) | **+1.193 (276/0)** | +0.0110 | temporal placement pair |
| LLH − LFM | **+0.875** (240/36) | +1.311 (275/1) | +0.0089 | temporal-variation pair |

Full-SSIM/Edge-SSIM for LLH − LHL: −0.0028 / +0.0203; FG-SSIM for LLH − LFM:
+0.0070 (175/101, weak).

## Effective-budget differences between these pairs

From `LLH_EFFECTIVE_CONTROL_AUDIT.md` (deep/middle and shallow time-means):

| pair | Δ deep/middle budget | Δ shallow budget |
|---|---|---|
| LLH − GFL | +0.425 (+34 %) | −0.215 |
| LFM − GFL | +0.400 (+32 %) | −0.220 |
| LLH − LHL | +0.025 (+1.5 %, stage-length asymmetry) | +0.005 |
| LLH − LFM | +0.025 (+1.5 %) | +0.005 |

## Budget-response slope anchor

GFM−GFL would isolate +0.417 deep/middle budget at *identical* (capped 0.8)
shallow budget, but no GFM rows exist in the same-runner RAW. The available
anchor is LFM−GFL (+2.369 dB FG-PSNR for +0.400 deep/mid, shallow −0.22): under
a linear response, **≈ +5.7 dB per unit deep/middle scale** (0.071 dB per +1 %
budget). The shallow term is bounded by the LFM−GFL residual after subtracting
the deep/mid component: ≈ +0.10 dB (≲ +0.3 dB allowing nonlinearity) — small.

## Decomposition of the headline LLH − GFL +3.24 dB

| component | estimate | basis |
|---|---|---|
| deep/middle effective budget ↑ (1.25 → 1.675) | **≈ +2.4 dB** | linear anchor (LFM−GFL slope scaled to +0.425) |
| shallow effective budget ↓ (0.80 → 0.585) | ≈ +0.1 dB | residual bound above |
| temporal placement (LLH vs LHL at ~equal budget) | **≈ +0.9 dB** | observed +1.001 minus ≈0.11 predicted budget component |
| temporal variation vs constant (LLH vs LFM at ~equal budget) | **≈ +0.77 dB** | observed +0.875 minus ≈0.11 |

The temporal-placement budget contamination is +0.071 dB/% × 1.5 % ≈
**+0.107 dB** against an observed LLH−LHL gap of +1.001 dB → **≈ 89 % of the
placement effect is not budget**. Caveat: the slope is linearized from one
+32 % anchor; interactions are ignored; the decomposition is approximate and
must not be quoted to two significant digits.

## Consequences for the paper narrative (binding)

1. **"LLH beats global-fixed-low" is a combined allocation effect**: roughly
   ¾ budget (deep/middle ↑) + ¼ timing (placement + variation). The paper must
   NOT present +3.24 dB as a pure temporal-scheduling effect.
2. The clean temporal statements are the ~budget-matched pairs:
   **LLH−LHL +1.00 dB FG-PSNR / +1.19 dB Full-PSNR (276/0 wins)** and
   **LLH−LFM +0.88 dB / +1.31 dB (275/1)** — "at matched per-group budgets,
   late-stage concentration and temporal variation each contribute ≈0.8–1 dB".
3. Global-vs-layer contrasts (all global schedules shallow-capped to 0.8) mix
   budget and distribution; if the paper keeps any global comparator, the cap
   semantics must be stated.
4. The equal-budget pilot (no checkpoint provenance) remains outside
   paper-facing evidence (unchanged policy); this audit's matched pairs (LHL,
   LFM) supply the budget-controlled comparisons instead.
5. Claim width: "layer-wise × temporal reallocation improves fidelity" is
   supported; "temporal placement alone explains the 3 dB" is refuted by our
   own decomposition.
