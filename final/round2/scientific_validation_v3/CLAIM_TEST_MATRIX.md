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


---

## Status addendum — 2026-10-05 (post-campaign; P0-1 re-derivation)

The pre-registered table above is frozen and left untouched. Verdicts after
campaign completion and the P0-1 interaction re-derivation (validated Wald
test; `PRE_ACCEPTANCE_ISSUE_CLOSURE.md`):

- Claim 1: **Supported** (deep row confirmatory; middle approximate; shallow
  stress-test-only) — B3 decomposition decisive.
- Claim 2: **Partially supported** (small real temporal effect; B2 placement
  contrasts decisive).
- Claim 3: **Supported with qualification [RE-DERIVED]** — interaction real
  (A2 Wald W=481.1/1880; SS shares 43.5%/56.8%); at matched dose still
  significant but variance share collapses (11.9%/0.8%); dose normalization
  exact only for the deep row. Interpretation lock satisfied in its letter
  (the interaction DOES survive residual-dose normalization statistically),
  but the practical 2D structure is bounded: the endpoint-matched linear
  ramp was not detectably different on FG-PSNR, with no registered margin to
  establish equivalence.
- Claim 4: **Heuristic only** (pending §8 boundary test for any stronger
  wording).
- Claim 5: **Supported (small)** — +0.435 dB [0.356, 0.516] over exact
  budget-matched constant; pre-registered equivalence margins not met.
- Claim 6: **Descriptive support for named cap/exposure contrasts only**.
  The former “additive cap + layer + temporal decomposition” is withdrawn:
  the cited pairwise contrasts use different endpoints. FRESH_CONFIRM_B
  TGU-0.80 remains needed to complete the specified diagnostic family.
- Claim 7: **Metric-dependent / partial** (linear warm-up was not detectably
  different on FG-PSNR; no equivalence margin was registered).
- Claim 8: **Broad transfer unconfirmed; bounded MV-Adapter result** — G now
  covers 98/99 planned objects after 17 missing-object completions; the
  remaining frozen GLB is path-only and cannot be processed as a surface
  mesh. The exploratory Wald reanalysis gives primary FG-LPIPS p = 0.101,
  PSNR p = 0.434; the FG-SSIM signal does not survive four-metric Holm
  correction. Small shallow W3–W5 LPIPS harms survive the registered cell
  family. Do not state universal backbone insensitivity or confirmed
  interaction absence.
- Claim 9: **Bounded support** (adapter level large; schedule level
  perceptual + seam only, n = 20).
- Claim 10: **Replicated** (prospective, all 10 Holm tests rejected).

## Status addendum — 2026-10-06 (GLB-native renderer reconciliation)

The pre-registered table and its prior status addendum remain unchanged.
Claim 9's old CPU/seam effects stay historical. The saved 20-object/eight-
condition GLBs were rendered at all 11 frozen unseen views with their
embedded repeat/mipmap sampler. `layer_llh − native_gfl` has mixed results:
FG-PSNR −0.422 dB [−1.361, +0.652], FG-LPIPS −0.01175 [−0.01988, −0.00564],
and CIEDE2000 +2.563 [−1.007, +5.893]. Claim 9 is now **bounded/partial** for
the supported 20-object base-color scope; it does not support unique schedule
superiority, full PBR, human fidelity, or strict all-24 coverage. See
`GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`.
