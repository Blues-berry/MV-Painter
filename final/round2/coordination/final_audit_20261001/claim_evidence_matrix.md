# Claim–Evidence Matrix (final_audit_20261001)

Audit date: 2026-10-01. Derived from `coordination/CLAIM_EVIDENCE_LEDGER.md` (2026-09-29
release gate) and integrated with all evidence completed after that date (same-runner
confirmation, robustness R0/R1, MV-Adapter 76 panel, MVDiffusion 75 panel, Core-7
protocol). Columns: **Strength** = how strongly current evidence supports the claim for a
reviewer; **Risk** = reviewer-attack exposure if the claim is stated at the given width.
Rows marked `→ Phase N` are updated by this audit.

| Claim | Evidence | Strength | Risk |
|---|---|---|---|
| Layer-wise adapter-residual allocation improves view fidelity on the main pipeline | Strict-276 same-runner confirmation (rescued): LLH vs global-fixed-low 7/7 metrics with CIs excluding zero (FG-PSNR +3.244 [+2.936,+3.542], 242/276 objects); LLH vs layer-fixed-mean 7/7; LLH vs layer-LHL rerun 7/7; corroborated by stage-placement A-2 panel | **strong** | low — same runner, same checkpoint, pre-registered protocol |
| Layer redistribution transfers to one additional adapter architecture (MV-Adapter) | MV-Adapter 76-object panel: L-LLH vs G-FL / G-LLH and L-LHL vs G-LHL (P1/P2/P4) favor layer-wise on PSNR, ΔE00, GT-texture (CIs exclude zero); FG-/Edge-SSIM slightly favor global; FG-LPIPS not separated | **medium** (effect real but metric-dependent) | medium — direction is metric-dependent; must not be phrased as uniform improvement |
| Temporal stage placement and layer redistribution are separable factors | Main backbone: temporal placement changes outcomes (A-2 four schedules, paired CIs; confirmation). MV-Adapter: temporal effect NOT_SUPPORTED within frozen scales (P3/P5 not separated). MVDiffusion: layer-wise NOT_REPLICATED → architecture-dependent | **medium** ("separable dimension" framing) | medium — separability holds on main pipeline only; MV-Adapter/MVDiffusion bound the generality |
| "LLH is the universal optimal schedule" | **Refuted internally**: MV-Adapter temporal not separated; MVDiffusion negative; factorial probe shows LHL non-optimal and direction flips between probes; only robust directions claimed | — (must NOT be claimed) | high if claimed; zero if replaced by "architecture-dependent effective residual allocation" |
| "TCAS/CAI automatically discovers the schedule" | Frozen CAI selection rule returned `undefined_set_valued` (no legal unique winner); LHL was a direct transfer diagnostic | — (must NOT be claimed) | high if claimed; replace with "CAI provides diagnostic motivation" |
| Global-vs-layer schedule choice is not a pipeline artifact | Core-7 completion (no_adapter + global_fixed_high) running under a verbatim copy of the same frozen runner/seed namespace → `→ Phase 5` matrix | **pending** | R2 confound closes when matrix lands |
| Schedule conclusion is robust to layer-grouping choice | `→ Phase 2` mapping sensitivity: non-degenerate partition (2,1,1) × 76 objects + degenerate-partition identity proof | **pending** | R2 mapping-choice attack closes with report |
| Texture statistics of generations are faithful to GT (distance-to-GT framing) | `→ Phase 3` offline audit on retained 276 images (CIEDE2000, Laplacian/RGB-variance/gradient-magnitude GT-relative errors) | **pending** | R1 texture concern; must avoid "higher variance = better" framing |
| Baked products are practically usable and surface-consistent | 12-object CPU bake with GLBs + unseen-view renders; ledger limits to case-study; `→ Phase 4` adds UV-seam ΔE and cross-view reprojection consistency (descriptive) | **medium** (case-study only) | medium — 12-object stratified cohort, no population claim |
| Stochastic stability of conclusions under reference-preprocessing randomness | R0/R1 seeded replication (276×2, seeds 42+idx / 10042+idx); realization-difference quantification; unseeded-stretch hazard frozen by object_seed rule | **strong** | low |
| Historical +0.96 dB / archived LHL 14.78 FG-PSNR results | Historical pool UID overlap; original v1 checkpoint missing; archived LHL not reproducible under frozen protocol (12.97 seeded) — excluded from quantitative claims → `→ Phase 1` exclusion document | — (excluded) | high if reused; zero when exclusion is documented |
| Method contribution is defensible after Round-2 | Mechanism study: training-free temporal stage-utility control with bounded transfer evidence (one additional adapter architecture) and explicit failure case (MVDiffusion) | **medium-strong** (as mechanism study) | low at this width; high if widened |

## Width rule (carried from ledger)

A row may support paper language only at or below its listed strength; any claim
requiring more width (all-backbones, universal optimality, automatic discovery,
population-level 3D advantage) is forbidden until new evidence lands. This matrix is
re-issued at the end of Phases 2–5 with the pending rows resolved.
