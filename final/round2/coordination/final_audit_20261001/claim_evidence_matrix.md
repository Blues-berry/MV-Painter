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
| Global-vs-layer schedule choice is not a pipeline artifact | **RESOLVED.** Core-7 completion verified this audit: same runner/seed/realization/shared-input (GFL anchor bit-exact; 0/276 cross-process input mismatches; means + primary paired CI independently recomputed digit-for-digit). LLH beats no_adapter +5.149* FG-PSNR and global_fixed_high +0.822* FG-PSNR / +2.585* Full-PSNR | **strong** | low — honest residue: FG-SSIM favors no_adapter (blur), GFH leads Full-LPIPS by 0.002 / Edge-SSIM by 0.006 |
| Schedule conclusion is robust to layer-grouping choice | **RESOLVED.** Mapping sensitivity: D=(1,2,1) ≡ C bitwise (arithmetic + 3-object identity check); B'=(2,1,1) budget-neutral × 76: B'−C not separated on any of 6 metrics; layer-vs-global advantage replicates under B' (ΔE00 +0.284*/+0.292*, GT-texture +0.277*/+0.252*, FG-SSIM small reverse, PSNR direction-consistent but ns) | **strong** for ΔE00/GT-texture partition-independence | low at that width; medium if widened to all metrics (PSNR nuance) |
| Texture statistics of generations are faithful to GT (distance-to-GT framing) | **RESOLVED.** Texture audit: LLH significantly closest to GT on CIEDE2000 vs all four stage-placement schedules (+2.79 vs fixed_mean, 271/275) and on all 4 probe distances vs global_fixed_low; vs layer alternatives mixed (LFM/LHL keep small hf_energy advantage; rgb_std vs LHL ns); Core-7 extension: LLH beats GFL on all 4 GT-relative errors | **medium-strong** | low at distance-to-GT width; no smoothness/preference claim permitted |
| Baked products are practically usable and surface-consistent | 12-object CPU bake + bake-consistency audit (UV-seam ΔE00 vs adjacent-texel baseline; 8-view reprojection ΔE00) → `baking_consistency_report.md` | **medium** (case-study, descriptive) | medium — 12-object stratified cohort, no population claim |
| Stochastic stability of conclusions under reference-preprocessing randomness | R0/R1 seeded replication (276×2, seeds 42+idx / 10042+idx); realization-difference quantification; unseeded-stretch hazard frozen by object_seed rule | **strong** | low |
| Historical +0.96 dB / archived LHL 14.78 FG-PSNR results | **RESOLVED (Case B).** Provenance forensics: record is a head/tail merge diverging +3.23/+0.38 dB from the frozen protocol on the same objects with 3.3×/2.1× lower generated texture variance; GT-side stats bitwise identical; realization lottery mean-neutral (R0/R1 ≈0.03 dB) excludes randomness as cause; exact execution state unreconstructible → excluded because complete provenance cannot be guaranteed (`historical_result_exclusion_reason.md`) | — (excluded) | high if reused; zero when exclusion is documented |
| Method contribution is defensible after Round-2 | Mechanism study: training-free temporal stage-utility control with bounded transfer evidence (one additional adapter architecture) and explicit failure case (MVDiffusion) | **medium-strong** (as mechanism study) | low at this width; high if widened |

## Width rule (carried from ledger)

A row may support paper language only at or below its listed strength; any claim
requiring more width (all-backbones, universal optimality, automatic discovery,
population-level 3D advantage) is forbidden until new evidence lands. This matrix is
re-issued at the end of Phases 2–5 with the pending rows resolved.
