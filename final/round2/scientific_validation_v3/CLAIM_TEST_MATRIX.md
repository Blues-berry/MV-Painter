# CLAIM_TEST_MATRIX — Phase III

Pre-registered mapping from manuscript claims to decisive experiments.
Verdict vocabulary: Supported / Partially supported / Unsupported / Refuted /
Heuristic only / Not replicated.

| Claim | Statement | Decisive experiment | Comparator | Cohort | Status |
|-------|-----------|---------------------|------------|--------|--------|
| 1 | Adapter scaling has a layer-dependent effect | B1 + TRUE-GLOBAL controls | LLH vs LFM-EXACT vs TRUE-GLOBAL-1.675 | FRESH_CONFIRM_N | PENDING |
| 2 | Adapter effect is timestep-dependent | A2/A3 temporal response curves | baseline vs window interventions | FRESH_CONFIRM_N | PENDING |
| 3 | Layer × timestep interaction | A3 dose-normalized two-factor analysis | Layer×Window interaction term | FRESH_CONFIRM_N | PENDING |
| 4 | 1/3 stage boundaries reflect empirical response | A3 response map vs frozen boundaries | W1–W5 response curves | FRESH_CONFIRM_N | PENDING |
| 5 | LLH gain is not explained by residual budget | B1 exact mean-matched control | LLH vs LFM-EXACT (budget-identical) | FRESH_CONFIRM_N | PENDING |
| 6 | Layer-wise allocation improves over truly uniform scaling | B3 TRUE-GLOBAL diagnostics | LLH vs TRUE-GLOBAL-{1.25,1.675,2.50} | FRESH_CONFIRM_N | PENDING |
| 7 | L-TCAS beats generic schedule families under authoritative protocol | C | LLH vs warm-up/cosine/trapezoid/Gaussian (endpoint- & budget-matched) | FRESH_CONFIRM_N | PENDING |
| 8 | Principle transfers to MV-Adapter | G | layer×time replication on MV-Adapter | MV-Adapter cohort (fresh if possible, else Exact-76 labeled as observed) | PENDING |
| 9 | Method improves practical 3D texturing | F unified same-draw bake | full condition set, one runner namespace | 24 stratified FRESH_CONFIRM objects | PENDING |
| 10 | Texture-rich objects define a systematic failure boundary | E prospective test | ΔFG-PSNR/LPIPS (LLH−GFL) vs GT texture stats | FRESH_CONFIRM_N | PENDING |

## Interpretation locks

- Claim 3 requires interaction to survive residual-dose normalization; otherwise
  do NOT claim a general layer×timestep interaction (raw map may be reported
  as descriptive).
- Claim 6: TRUE-GLOBAL is a causal diagnostic, never a deployment recommendation.
- Claim 7 verdict options: Supported / metric-dependent / unsupported.
- Claim 8 verdict options: interaction-level transfer / layer-only transfer /
  unsupported (framing decides backbone-specific vs general).
- Claim 9: no population-level 3D claim unless the unified bake supports it.
