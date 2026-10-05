# NARRATIVE_RESTRUCTURE_REQUIRED

Status: TRIGGERED (2026-10-05). Per MASTER_PROTOCOL_LOCK.md STOP RULE: a major
result contradicts the current manuscript narrative; the paper must NOT be
edited until this document and the final decision report define the supported
story. This file states what the data actually support — it is not a wording
proposal.

**AMENDED 2026-10-05 (P0-1 closure):** point 1, point 4 and the supported
story are restated because the production interaction test had zero power
(`PRE_ACCEPTANCE_AUDIT_20261005.md` P0-1); the authoritative interaction
result is now the validated cluster-robust Wald test
(`audit_scripts/AUDIT_INTERACTION_VALID_TEST.json`).

## The contradiction

The current narrative is L-TCAS: layer- AND timestep-conditioned adapter
scaling, with 1/3 stage boundaries presented as empirically meaningful and
the layer x timestep structure as the method's core.

Phase III map designs and several contrasts were frozen on FRESH_CONFIRM_300
before its campaign outputs. The replacement Wald interaction statistic was
chosen after the zero-power bootstrap defect was found, so that same-cohort
interaction reanalysis is exploratory pending fresh bounded-dose confirmation.

1. **[AMENDED P0-1] The layer x timestep interaction is REAL, but its
   magnitude is dose-dependent.** Valid cluster-robust Wald test: native-dose
   A2 map — FG-LPIPS W = 481.1 (p = 8.0e-99), interaction SS share 43.5%;
   FG-PSNR W = 1880 (p ≈ 0), share 56.8%. Dose-normalized A3 map — still
   significant (FG-LPIPS p = 1.1e-136, share 11.9%; FG-PSNR share 0.8%) but
   the time-structure variance share collapses at matched dose (exact only
   for the deep row; middle approximate; shallow stress-only). The earlier
   "p = 0.50 / p = 1.0, NOT SUPPORTED" statements were artifacts of a
   zero-power test and are retracted. The Wald reanalysis is not a fresh
   confirmatory test; A3b on FRESH_CONFIRM_B is still required.
2. **The 1/3 stage boundaries are heuristic, not empirical.** The valid A2
   map shows a smooth positional response (deep early→late sign flip);
   nothing special occurs at steps 16/17 or 32/33. The A3 "window-flat at
   equal dose" reading is fully valid only for the deep row (middle
   approximate, shallow stress-only).
3. **A simple per-layer linear warm-up equals LLH** (FG-PSNR +0.005 dB,
   Holm p = 0.81) under the authoritative runner. LLH does beat bump/trapezoid/
   Gaussian shapes and all budget-matched variants — the advantage is
   shape-dependent, not a general "L-TCAS beats schedules" law.
4. **[AMENDED P0-1] What is supported:** layer-dependent effects on the
   primary backbone. A3 deep is the valid local-dose row (FG-PSNR marginal
   +0.55 dB); middle is approximate (+0.29 dB); shallow −6.07 dB is a stress-
   regime result, not local-dose confirmation. In B3, GFL−TGU-1.25 is a cap
   contrast (+1.60 dB), and LFM-EXACT−TGU-1.675 is a shallow-exposure contrast
   (+2.99 dB); these have different baselines and are not additive components
   of LLH−GFL. The same-endpoint LLH−GFL difference is +1.288 dB, of which
   +0.435 dB is isolated by LLH−LFM-EXACT; the remaining +0.853 dB combines
   layer doses and shallow-cap state. Do not present a cap + layer + temporal
   causal decomposition.
5. **The LLH advantage is boundary-limited.** It is carried by texture-poor
   objects (+4.14 dB, 92% win in the lowest texture quartile) and REVERSES on
   texture-rich objects (Q3/Q4 negative; |rho| up to 0.69 against GT HF
   energy). Any deployment claim must state this boundary.

## What the data actually support

The scientifically defensible story is:

> **[AMENDED P0-1] Depth-aware adapter scaling with a monotone
> late-increasing profile; a native-dose layer × time interaction is
> suggested by exploratory reanalysis and awaits fresh bounded-dose
> confirmation.**
> Adapter residual allocation across UNet depth groups is a first-order,
> large, reproducible effect (shallow protection is critical; deep/middle
> scaling helps geometry metrics). A late-increasing temporal profile adds a
> small, real benefit over a constant per-layer-mean-matched scale (+0.4 dB),
> and a linear ramp matches LLH on FG-PSNR. The same-cohort Wald reanalysis
> found a large native-dose variance share and a smaller A3 share (FG-PSNR
> 56.8% -> 0.8%; FG-LPIPS 43.5% -> 11.9%); it is exploratory because the
> replacement test followed discovery of the original test defect. A3b must
> establish whether a bounded local-dose interaction persists on
> FRESH_CONFIRM_B. The two-axis S=[s_l,k] remains a useful description, but
> deployment-level necessity is unestablished. The
> 3-stage boundaries are a design heuristic, not an empirical discovery. The texture-rich failure boundary is systematic and
> GT-predictable.

This matches the protocol's anticipated reframing: "depth-aware adapter
scaling + temporal analysis" rather than a claim that timestep-conditioned
structure is a discovered mechanism.

## Required manuscript actions (after the decision gate)

- [AMENDED P0-1] Reframe claims 2/3/4 per CLAIM_TEST_MATRIX verdicts
  (2 partial, 3 SUPPORTED WITH QUALIFICATION - interaction real,
  dose-dependent variance share; 4 heuristic only).
- Replace "learned/empirical stage boundaries" wording with design-heuristic
  wording; report the linear-ramp equivalence (H4) transparently.
- Present A3 deep as valid local-dose evidence, middle as approximate, and
  shallow as stress-only. Keep TRUE-GLOBAL diagnostics as separate named
  cap/exposure contrasts; do not call them an additive decomposition.
- State the texture-complexity failure boundary explicitly with the quartile
  table (E), including that the average advantage reverses on texture-rich
  objects.
- [AMENDED P0-1] Do NOT claim novelty for the temporal structure beyond
  "monotone late-increasing profiles suffice"; do NOT claim "no interaction"
  either - report the interaction with its dose-dependent variance share and
  the validated test; do NOT present the 2D matrix as a practical necessity.

## Pending before the gate

- [UPDATED] G (MV-Adapter): completion added 17/18 missing objects; one
  frozen path-only GLB remains a documented loader exclusion. The completed
  analysis is n = 98/99 planned and supports only a bounded result in the
  frozen scale range. Primary FG-LPIPS interaction reanalysis is exploratory
  and non-significant; no confirmatory no-interaction statement is allowed.
- [RESOLVED] F (unified bake): claim 9 = bounded support (n = 20).
- OPEN: V3 protocol steps 3-16
  (FRESH_CONFIRM_B freeze, A3b, boundary test, formal visual
  classification, CAI decision doc, human-study decision).
