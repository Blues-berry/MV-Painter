# MASTER_PROTOCOL_LOCK — Scientific Validation Phase III (Causal Evidence Closure)

- Date frozen: 2026-10-02
- Branch: `codex/scientific-validation-v3-20261002`
- Base HEAD: `29b3a0a6ec00f5848f1898ffda4fb8e787f81375`
- Target repository: Blues-berry/MV-Painter
- Status: **LOCKED** — protocol text below is authoritative for this phase.

## GOAL

Do NOT optimize the manuscript.
Do NOT defend the current narrative by wording.
The goal is to determine which scientific claims are actually supported
after removing budget, cap, stage-boundary, visual-selection, and
backbone-interface confounds.

This phase may add substantial experiments.
Manuscript text must remain frozen until the final scientific decision gate
(`SCIENTIFIC_VALIDATION_DECISION_REPORT.md`).

## HARD RULES

### Frozen files (must NOT be modified until decision gate)

- `final/round2/final_round2.tex`
- `final/round2/supplementary_round2.tex`
- `final/round2/response_letter_round2.md`

### Forbidden

- post-hoc schedule search on the formal confirmation cohort
- changing scale values after looking at formal outcomes
- changing window definitions after looking at formal outcomes
- replacing failed objects
- aesthetic/manual cherry-picking of figures
- combining numbers from capped and uncapped runners
- calling an already-observed cohort a "fresh holdout"
- silently dropping negative results
- claiming CAI predicts schedules unless prediction is prospectively tested

### Required provenance for all new runs

All new runs must save:

- per-object metrics
- per-view metrics
- all random seeds
- input hashes
- checkpoint hash
- code commit SHA
- actual requested scale per layer/per step
- actual effective scale after cap
- per-layer/per-step residual norm
- generated PNGs for every formal condition
- failure logs

## EXPERIMENT INDEX

| ID | Name | Deliverable |
|----|------|-------------|
| 1 | Fresh confirmatory cohort | `fresh_confirm_300.txt` / `_N`, manifest, disjointness audit, SHA256SUMS |
| A | Layer × Time causal intervention map | `LAYER_TIME_CAUSAL_MAP_REPORT.md` |
| B | Budget & cap confound removal | `BUDGET_AND_CAP_CAUSAL_AUDIT.md` |
| C | Generic schedules under authoritative runner | `AUTHORITATIVE_GENERIC_SCHEDULE_REPORT.md` |
| D | Formal qualitative archive | `FORMAL_VISUAL_EVIDENCE_AUDIT.md` |
| E | Failure-mode confirmation (texture boundary) | `TEXTURE_COMPLEXITY_FAILURE_BOUNDARY.md` |
| F | Unified same-draw 3D bake | `UNIFIED_COREDRAW_BAKE_REPORT.md` |
| G | Cross-backbone mechanism test (MV-Adapter) | `CROSS_BACKBONE_MECHANISM_REPORT.md` |

## KEY FROZEN CONSTANTS

### Experiment A base condition (layer-fixed-low)

- deep = 1.25, middle = 1.25, shallow = 0.50
- 50 Euler steps, five EXACTLY EQUAL windows:
  - W1 = steps 0–9, W2 = steps 10–19, W3 = steps 20–29, W4 = steps 30–39, W5 = steps 40–49
- Frozen high values: deep 1.25→2.50, middle 1.25→2.50, shallow 0.50→0.75
- 3 layers × 5 windows + 1 baseline = 16 formal conditions
- Preflight: 3 objects, instrumentation-only, never used for conclusions

### Experiment B exact constants (17/16/17 partition, 50 steps)

- LLH deep/middle mean: (17×1.25 + 16×1.25 + 17×2.50)/50 = **1.675**
- LLH shallow mean: (17×0.50 + 16×0.50 + 17×0.75)/50 = **0.585**
- LFM-EXACT: deep=1.675, middle=1.675, shallow=0.585, constant all 50 steps
- TRUE-GLOBAL diagnostics: 1.25 / 1.675 / 2.50 (cap bypassed, causal-only)
- Native capped controls kept separate: NATIVE-GFL, NATIVE-GFH, NATIVE-GC3

### Statistical discipline

- `PRIMARY_HYPOTHESES.md` written BEFORE formal runs
- Primary H1: dose-normalized Layer×Time interaction on FG-LPIPS
- Primary H2: LLH vs LFM-EXACT
- Primary H3: LLH vs HLL / LLL temporal-location contrast
- Primary H4: LLH vs predefined generic schedule family
- Primary H5: prospective texture-complexity failure relationship
- Paired object-level bootstrap, 10,000 resamples, fixed bootstrap seed
- Holm correction per predefined family
- Effect sizes + CIs (not p-values alone)
- No "equivalence" without predeclared margin
- Cohort selection seed: **20261002**

## STOP RULE

Do NOT modify the paper after obtaining only favorable partial results.
Only after `SCIENTIFIC_VALIDATION_DECISION_REPORT.md` is complete may
manuscript rewriting begin. If any major result contradicts the manuscript,
write `NARRATIVE_RESTRUCTURE_REQUIRED.md` instead of optimizing wording.
