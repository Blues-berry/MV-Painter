# Final Reviewer Readiness Report (final_audit_20261001)

Date: 2026-10-01. Branch `codex/round2-evidence-integrated-20261001`. **No manuscript
text was modified during this audit.** This report integrates all Phase 0–7 outcomes,
including the parallel task's delivered runs (Core-7) which were independently verified
rather than duplicated.

## 1. Reviewer 1 response readiness

| concern | status | evidence |
|---|---|---|
| Holdout integrity | **PASS** | Clean-v2 strict 276-object UID-disjoint holdout; per-object CSVs, manifests, SHAs frozen (`FINAL_REPRODUCIBILITY_MANIFEST.json`); full image set retained for the stage-placement panel |
| Statistics | **PASS** | Bitwise-reproducible analysis (rerun SHA identical, seed 20260930, 10k object-level percentile bootstrap); no direction errors (`metric_direction_audit.md`, `statistics_reproducibility_audit.md`); R0/R1 realization stability 27/28 STABLE_STRONG |
| "Different pipeline" confound | **CLOSED** | Core-7 same-runner matrix (verified): LLH best of 7 on FG-PSNR/FG-LPIPS/Full-PSNR/Full-SSIM; beats no_adapter +5.149* and global_fixed_high +0.822* FG-PSNR under identical runner/seed/realization/shared-input; GFL anchor bit-exact; 0/276 input mismatches |
| Texture concern | **STRENGTHENED** | Distance-to-GT framing on two independent surfaces: CIEDE2000 favors LLH vs all four stage-placement schedules (+2.79 vs fixed_mean, 271/275); all 4 probe distances vs global_fixed_low; Core-7 extension agrees; exceptions listed verbatim (hf_energy vs LFM/LHL, grad vs HLL) |
| Stochastic stability / LHL anomaly | **PASS + CLOSED** | R0/R1 seeded replication; realization mean-neutrality quantified (≈0.03 dB); archived LHL record excluded under Case B with forensic audit trail (`ARCHIVED_LHL_PROVENANCE_AUDIT.md`) |
| Practical quality (baking) | **ADEQUATE (case study)** | 12-object bake + new consistency descriptors: layer_llh best of 8 variants on seam ΔE00 (4.40) and cross-view stability (5.41/p90 13.75); stratified cohort, descriptive only |

## 2. Reviewer 2 response readiness

| concern | status | evidence |
|---|---|---|
| Novelty framing | **READY (at mechanism-study width)** | "Adapter residual allocation across depth and denoising stages as a controllable inference dimension; temporal placement and layer redistribution are separable factors" — supported on the main pipeline, bounded elsewhere |
| CAI | **BOUNDED** | Frozen CAI rule returned `undefined_set_valued` — no "automatic discovery" claim permitted; "diagnostic motivation" only |
| Cross-backbone transfer | **CLOSED (bounded)** | MV-Adapter 76-object panel: layer-wise SUPPORTED (PSNR/ΔE00/GT-texture CIs exclude zero; SSIM small reverse; LPIPS ns); MVDiffusion: NOT_REPLICATED (negative preserved) — architecture-dependent boundary stated |
| Mapping-choice robustness | **CLOSED (budget-neutral axis)** | Degenerate partition (1,2,1) ≡ frozen partition bitwise (arithmetic + 3-object identity); alternative partition (2,1,1) × 76: indistinguishable from frozen on 6/6 metrics; layer advantage replicates (ΔE00 +0.284*/+0.292*, GT-texture +0.277*/+0.252*); PSNR significance weakens (ns) — nuance reported |
| Temporal-position generality | **NOT CLAIMED** | MV-Adapter temporal NOT_SUPPORTED; correctly absent from all claim language |

## 3. Remaining risks

1. **M3 frozen-value mapping variant** (parallel task's protocol) not yet run; my
   budget-neutral B′ axis is closed, so this is completeness, not exposure. If M3
   later diverges, the difference is attributable to its total-budget shift (per-point
   mean 0.8065 ≠ 1) and must be reported as such.
2. **PSNR nuance under re-partition**: the layer-vs-global PSNR advantage is
   significant under partition C but not under B′. If a reviewer probes mapping
   robustness specifically on PSNR, the honest answer is the nuance sentence in
   `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md` §4.
3. **Archived-record mechanism**: Case B deliberately does not name a root cause; a
   discriminating experiment is defined by the parallel task (`lhl_forensics` stage-2)
   if a reviewer insists on mechanism. The exclusion itself is defensible without it.
4. **Cross-view descriptor convention**: bake cross-view metric uses vertex-colored
   rendering (environment limitation, documented); values are stability descriptors,
   not texture-fidelity metrics.
5. **Equal-budget pilot** rows (C3 development) still lack full checkpoint provenance —
   they remain outside paper-facing tables (unchanged policy).

## 4. Final claim boundaries (release rule)

A paper sentence may be written only inside these widths:

1. Fidelity: "best of seven same-runner conditions on the 276-object strict holdout"
   (FG-PSNR/FG-LPIPS/Full-PSNR/Full-SSIM) — Core-7 matrix.
2. Texture: "closest to GT statistics" (distance-to-GT framing) with the four
   enumerated exception cells.
3. Transfer: "one additional adapter architecture (MV-Adapter), layer redistribution
   supported, temporal placement not separated; not replicated on MVDiffusion".
4. Partition: "invariant to the exact layer partition (bitwise or statistically
   indistinguishable), with the PSNR-significance nuance".
5. Stability: "stable across two frozen realization sets".
6. Baking: "12-object stratified case study; layer_llh shows the lowest seam and
   cross-view discrepancies of the eight variants".
7. History: archived numbers never quoted; Case-B exclusion sentence only.

## 5. Required manuscript changes (next window; list only)

See `FINAL_NARRATIVE_RECOMMENDATION.md` §4 — seven items, headed by (a) the Case-B
wording replacing any residual "unseeded realization" causality, (b) replacing all
baseline-family numbers with the Core-7 same-runner matrix, (c) the three claim
downgrades (transfer/CAI/universal-optimum), (d) one mapping-invariance sentence,
(e) optional texture distance-to-GT row, (f) S9/S10 disclosure re-check, (g) bake
descriptors sourced from `baking_consistency_report.md`.

## 6. Additional experiments still recommended

1. M3 mapping run (3×76, parallel task's frozen protocol) — completeness.
2. LHL-forensics stage-2 discriminating run — only under reviewer pressure.
3. MVDiffusion depth-concat exploration — only under reviewer pressure.
4. Nothing else; the current claim set is fully evidenced.

## 7. Deliverable index (this directory)

`final_round2_evidence_inventory.md` · `FINAL_REPRODUCIBILITY_MANIFEST.json` ·
`claim_evidence_matrix.md` · `rescued_tmp_20261001/` (incl. SHA256_MANIFEST) ·
`ARCHIVED_LHL_PROVENANCE_AUDIT.md` · `archived_vs_current_runner_diff.md` ·
`historical_result_exclusion_reason.md` · `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`
(+ bootstrap JSON in mv_adapter) · `STRICT276_TEXTURE_FIDELITY_AUDIT.md` (+
texture_audit/) · `baking_consistency_report.md` (+ bake_consistency/) ·
`STRICT276_CORE7_MATRIX.md` · `metric_direction_audit.md` ·
`statistics_reproducibility_audit.md` · `FINAL_NARRATIVE_RECOMMENDATION.md` · this
report.
