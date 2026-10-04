# NARRATIVE_RESTRUCTURE_REQUIRED

Status: TRIGGERED (2026-10-05). Per MASTER_PROTOCOL_LOCK.md STOP RULE: a major
result contradicts the current manuscript narrative; the paper must NOT be
edited until this document and the final decision report define the supported
story. This file states what the data actually support — it is not a wording
proposal.

## The contradiction

The current narrative is L-TCAS: layer- AND timestep-conditioned adapter
scaling, with 1/3 stage boundaries presented as empirically meaningful and
the layer x timestep structure as the method's core.

Phase III evidence (FRESH_CONFIRM_300, pre-registered, confirmatory):

1. **The layer x timestep interaction is NOT supported.**
   Raw map: p = 0.50. Dose-normalized map (the pre-registered primary H1):
   p = 1.0 — the observed cell structure is MORE additive than the bootstrap
   null. No test supports a specific interaction term.
2. **The 1/3 stage boundaries are heuristic, not empirical.** Responses are
   window-flat within each depth group at equal dose; nothing special occurs
   at steps 16/17 or 32/33.
3. **A simple per-layer linear warm-up equals LLH** (FG-PSNR +0.005 dB,
   Holm p = 0.81) under the authoritative runner. LLH does beat bump/trapezoid/
   Gaussian shapes and all budget-matched variants — the advantage is
   shape-dependent, not a general "L-TCAS beats schedules" law.
4. **What IS strongly supported:** layer-dependent effects. At equal residual
   dose: deep +0.55 dB, middle +0.29 dB, shallow −6.07 dB (FG-PSNR marginals);
   layer redistribution at equal budget beats uniform scaling by +3.0 dB; the
   shallow cap alone is worth +1.6 dB. The decomposition cap + layer +
   temporal is additive and explains all pairwise schedule effects without an
   interaction term.
5. **The LLH advantage is boundary-limited.** It is carried by texture-poor
   objects (+4.14 dB, 92% win in the lowest texture quartile) and REVERSES on
   texture-rich objects (Q3/Q4 negative; |rho| up to 0.69 against GT HF
   energy). Any deployment claim must state this boundary.

## What the data actually support

The scientifically defensible story is:

> **Depth-aware adapter scaling with a monotone late-increasing profile.**
> Adapter residual allocation across UNet depth groups is a first-order,
> large, reproducible effect (shallow protection is critical; deep/middle
> scaling helps geometry metrics). A late-increasing temporal profile adds a
> small, real benefit over a constant budget-matched scale (+0.4 dB), and a
> linear ramp captures it fully. There is no evidence for a layer x timestep
> interaction, and the 3-stage boundaries are a design heuristic, not an
> empirical discovery. The texture-rich failure boundary is systematic and
> GT-predictable.

This matches the protocol's anticipated reframing: "depth-aware adapter
scaling + temporal analysis" rather than a claim that timestep-conditioned
structure is a discovered mechanism.

## Required manuscript actions (after the decision gate)

- Reframe claims 2/3/4 per CLAIM_TEST_MATRIX verdicts (2 partial, 3 not
  supported, 4 heuristic only).
- Replace "learned/empirical stage boundaries" wording with design-heuristic
  wording; report the linear-ramp equivalence (H4) transparently.
- Present the A3 equal-dose map as the causal evidence that layer allocation
  dominates; keep TRUE-GLOBAL diagnostics as the cap/redistribution
  decomposition.
- State the texture-complexity failure boundary explicitly with the quartile
  table (E), including that the average advantage reverses on texture-rich
  objects.
- Do NOT claim novelty for the temporal structure beyond "monotone
  late-increasing profiles suffice"; do NOT claim the interaction exists.

## Pending before the gate

- G (MV-Adapter): interaction expected absent there too (pilot signals weak
  response); verdict will set claim 8 (layer-only transfer vs backbone-specific).
- F (unified bake): claim 9 scope.
