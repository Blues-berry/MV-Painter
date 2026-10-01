# CROSS_BACKBONE_CLAIM_BOUNDARY.md (Phase 14 — agent B)

Three-level verdict on what the cross-backbone evidence supports. Sources:
`CROSS_BACKBONE_VALIDATION_MVADAPTER.md`, `CROSS_BACKBONE_VALIDATION_MVDIFFUSION.md`,
`MVDIFFUSION_INTERVENTION_EQUIVALENCE_AUDIT.md` (this directory),
`final/round2/coordination/EVIDENCE_INTEGRATION_STATUS_20261001.md`, plus the
same-runner main-backbone matrix audits in this directory.

## Level 1 — Main MVPainter backbone: full method supported

- Layer-wise × temporal reallocation improves strict-holdout fidelity:
  LLH best of 7 same-runner conditions (FG-PSNR 13.975), beats no_adapter
  +5.149* and global_fixed_high +0.822* / global_fixed_low +3.244* (CIs
  exclude zero; 242–276/276 win rates).
- Mechanism/budget decomposition (agent B, Phase 15): combined allocation
  effect — ≈¾ deep/middle budget, ≈¼ timing; temporal placement alone
  (LLH−LHL +1.00 dB, Full-PSNR 276/0) and temporal variation (LLH−LFM
  +0.88 dB) survive at matched budgets.
- Robust to tested contiguous layer partitions (bitwise-degenerate or
  statistically indistinguishable alternatives; PSNR-significance nuance
  under budget-neutral B′); stable across two frozen realizations (R0/R1
  drift ≤0.09 dB median; outputs ~45 dB self-similar).
- Width: claims allowed on the main backbone are the strongest of the three
  levels; "universal optimal schedule" and "automatic discovery" remain
  forbidden (MV-Adapter temporal ns; MVDiffusion negative; CAI
  undefined_set_valued).

## Level 2 — MV-Adapter: layer redistribution supported, temporal not, full method not

- Layer-wise effect = **SUPPORTED** (76 objects, identity 9/9 bitwise):
  PSNR / ΔE00 / GT-texture CIs exclude zero in favor of layer-wise; FG-/Edge-
  SSIM small reverse; FG-LPIPS not separated → **metric-dependent support**;
  must not be phrased as uniform improvement.
- Temporal position = **NOT_SUPPORTED** (P3/P5 not separated).
- Full method (layer × temporal joint) = **NOT tested** — temporal leg absent,
  so the joint claim cannot be transferred.
- Mapping provenance = closed: frozen partition reproduced bitwise by the
  degenerate alternative; budget-neutral B′ and frozen-value M3 axes both
  tested; "robust to the tested contiguous partitions", never "invariant".

## Level 3 — MVDiffusion: boundary evidence only

- Classification: **boundary / interface transfer experiment** (serial
  correspondence-module recombination vs additive residual branch —
  structurally different intervention; see the equivalence audit).
- Result: layer-wise **NOT_REPLICATED** — PSNR/FG-SSIM/Edge-SSIM/ΔE00
  significantly worse for layer-wise; GT-texture significantly better;
  FG-LPIPS ns. Negative/mixed result preserved as found (no tuning).
- Role in the paper: an architecture-dependent transfer boundary with honest
  negatives — it bounds the generality claim and motivates the
  "allocation mechanism" framing; it supports nothing positive by itself.

## Binding wording rules (release rule)

1. Allowed: "layer redistribution transfers to one additional adapter
   architecture (MV-Adapter) with metric-dependent support; temporal placement
   effects were not separated there; on a backbone whose conditioning surface
   is structurally different (MVDiffusion) the layer-wise reallocation did not
   replicate."
2. Forbidden: "generalizes across backbones"; "the method works on three
   backbones"; any cross-backbone pooling of absolute values; "replication" for
   MVDiffusion.
3. The paper's contribution sentence should be the mechanism claim: adapter
   residual allocation (where × when) is a real, separable, inference-time
   control dimension on the main pipeline, with architecture-dependent
   transfer boundaries documented by two external adapter implementations.

## Verdict per level

| level | verdict |
|---|---|
| 1 Main | VALIDATED (with budget-composition caveat, Phase 15) |
| 2 MV-Adapter | VALIDATED_WITH_LIMITATIONS (scale dimension only; temporal absent) |
| 3 MVDiffusion | VALIDATED as boundary experiment; replication claim INVALID |
