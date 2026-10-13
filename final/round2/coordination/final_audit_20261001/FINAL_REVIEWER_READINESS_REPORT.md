# Final Reviewer Readiness Report (final_audit_20261001)

Date: 2026-10-01. Branch `codex/round2-evidence-integrated-20261001`. **No manuscript
text was modified during this audit.** This report integrates all Phase 0–7 outcomes,
including the parallel task's delivered runs (Core-7) which were independently verified
rather than duplicated.

> **Re-issue (2026-10-01, evidence convergence).** After the initial issue of this
> report, the parallel task's M3 mapping runs (3 × 76, committed at `75a4068`) and
> LHL-forensics stage-2 run (`lhl_forensics/`) were found to be already merged into
> this branch's tree. Sections 2, 3, 4, 5 and 6 below are updated accordingly; no
> earlier conclusion is reversed — M3 strengthens the mapping-robustness statement and
> stage-2 strengthens the Case-B exclusion. The authoritative inventory is
> `final_round2_evidence_inventory.md` (re-issued at the convergence commit). Status
> after convergence: **all mandatory audit phases are closed for the frozen claim
> set**; no experiment remains mandatory.

## 1. Reviewer 1 response readiness

| concern | status | evidence |
|---|---|---|
| Holdout integrity | **PASS** | Clean-v2 strict 276-object UID-disjoint holdout; per-object CSVs, manifests, SHAs frozen (`FINAL_REPRODUCIBILITY_MANIFEST.json`); full image set retained for the stage-placement panel |
| Statistics | **PASS** | Bitwise-reproducible analysis (rerun SHA identical, seed 20260930, 10k object-level percentile bootstrap); no direction errors (`metric_direction_audit.md`, `statistics_reproducibility_audit.md`); R0/R1 realization stability 27/28 STABLE_STRONG |
| "Different pipeline" confound | **CLOSED** | Core-7 same-runner matrix (verified): LLH best of 7 on FG-PSNR/FG-LPIPS/Full-PSNR/Full-SSIM; beats no_adapter +5.149* and global_fixed_high +0.822* FG-PSNR under identical runner/seed/realization/shared-input; GFL anchor bit-exact; 0/276 input mismatches |
| Texture concern | **STRENGTHENED** | Distance-to-GT framing on two independent surfaces: CIEDE2000 favors LLH vs all four stage-placement schedules (+2.79 vs fixed_mean, 271/275); all 4 probe distances vs global_fixed_low; Core-7 extension agrees; exceptions listed verbatim (hf_energy vs LFM/LHL, grad vs HLL) |
| Stochastic stability / LHL anomaly | **PASS + CLOSED** | R0/R1 seeded replication; realization mean-neutrality quantified (≈0.03 dB); archived LHL record excluded under Case B with forensic audit trail (`ARCHIVED_LHL_PROVENANCE_AUDIT.md`) |
| Practical quality (baking) | **ADEQUATE (case study)** | 12-object bake + new consistency descriptors: layer_llh best of 8 variants on seam ΔE00 (4.40) and on the render-time cross-view color-stability descriptor (5.41/p90 13.75); stratified cohort, descriptive only; cross-view values are render-time stability descriptors, not texture-fidelity metrics |

## 2. Reviewer 2 response readiness

| concern | status | evidence |
|---|---|---|
| Novelty framing | **READY (at mechanism-study width)** | "Adapter residual allocation across depth and denoising stages as a controllable inference dimension; temporal placement and layer redistribution are separable factors" — supported on the main pipeline, bounded elsewhere |
| CAI | **BOUNDED** | Frozen CAI rule returned `undefined_set_valued` — no "automatic discovery" claim permitted; "diagnostic motivation" only |
| Cross-backbone transfer | **CLOSED (bounded)** | MV-Adapter 76-object panel: layer-wise SUPPORTED (PSNR/ΔE00/GT-texture CIs exclude zero; SSIM small reverse; LPIPS ns); MVDiffusion: NOT_REPLICATED (negative preserved) — architecture-dependent boundary stated |
| Mapping-choice robustness | **CLOSED (both tested axes)** | Axis 1 (budget-neutral re-assignment): degenerate partition (1,2,1) ≡ frozen partition bitwise; alternative partition (2,1,1) × 76: indistinguishable from frozen on 6/6 metrics; layer advantage replicates (ΔE00 +0.284*/+0.292*, GT-texture +0.277*/+0.252*); PSNR significance weakens (ns) — nuance reported. Axis 2 (frozen-value M3, committed at `75a4068`): 3 × 76 = 228 rows, 16/18 MAPPING_STABLE, primary effects slightly stronger (P1 PSNR +0.10 → +0.15, ΔE00 +0.34 → +0.48, GT-texture +0.31 → +0.41). Wording width: robust to the tested contiguous layer partitions — not "invariant" |
| Temporal-position generality | **NOT CLAIMED** | MV-Adapter temporal NOT_SUPPORTED; correctly absent from all claim language |

## 3. Remaining risks

1. **M3 frozen-value mapping variant** — **RESOLVED at convergence.** The runs had
   already been committed at `75a4068` (`results/holdout_exact_mapM3_*_76/`, 3 × 76 =
   228 rows) with a pre-registered protocol; this re-issue incorporates them
   (`MAPPING_SENSITIVITY_REPORT.md` in `core7_same_runner_completion_20261001/`):
   16/18 MAPPING_STABLE, primary metrics slightly stronger under M3. Because M3 shifts
   the total budget (per-point mean 0.8065 ≠ 1), any M3-vs-M1 difference must be
   attributed to the budget shift as well as the assignment — stated in the report.
2. **PSNR nuance under re-partition**: the layer-vs-global PSNR advantage is
   significant under partition C (and under M3), but not under budget-neutral B′. If a
   reviewer probes mapping robustness specifically on PSNR, the honest answer is the
   nuance sentence in `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md` §4.
3. **Archived-record mechanism** — **RESOLVED at convergence.** The parallel task's
   LHL-forensics stage-2 discriminating run has been executed and committed
   (`core7_same_runner_completion_20261001/lhl_forensics/`, 12 objects): aug-ON
   regeneration reproduces the frozen seeded rows bit-exactly, while aug-OFF still
   misses the archived record (−6.96 dB on the hexuid group). The cond-augmentation
   hypothesis is thereby experimentally refuted, on top of the earlier exclusions;
   Case B (root cause unreconstructible → record excluded) is unchanged and now
   stronger. No further mechanism experiment is anticipated.
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
4. Partition: "robust to the tested contiguous layer partitions (bitwise-degenerate or
   statistically indistinguishable; budget-neutral and frozen-value axes both tested),
   with the PSNR-significance nuance" — never "invariant to the exact layer partition".
5. Stability: "stable across two frozen realization sets".
6. Baking: "12-object stratified case study; layer_llh shows the lowest seam and
   cross-view discrepancies of the eight variants" — cross-view values presented only
   as render-time color-stability descriptors (vertex-colored rendering), never as
   direct multi-view texture fidelity.
7. History: archived numbers never quoted; Case-B exclusion sentence only.

## 5. Required manuscript changes (next window; list only)

See `FINAL_NARRATIVE_RECOMMENDATION.md` §4 — seven items, headed by (a) the Case-B
wording replacing any residual "unseeded realization" causality, (b) replacing all
baseline-family numbers with the Core-7 same-runner matrix, (c) the three claim
downgrades (transfer/CAI/universal-optimum), (d) one mapping-robustness sentence
(tested-partition width, never "invariant"),
(e) optional texture distance-to-GT row, (f) S9/S10 disclosure re-check, (g) bake
descriptors sourced from `baking_consistency_report.md`, with the cross-view metric
named a render-time stability descriptor.

## 6. Additional experiments still recommended

1. ~~M3 mapping run~~ — **DONE at convergence** (committed at `75a4068`; incorporated
   in this re-issue).
2. ~~LHL-forensics stage-2 discriminating run~~ — **DONE at convergence**
   (`lhl_forensics/`); cond-augmentation hypothesis refuted; Case B stands.
3. MVDiffusion depth-concat exploration — only under reviewer pressure.
4. Nothing else; the current claim set is fully evidenced. **The experiment phase is
   frozen.**

## 7. Deliverable index (this directory)

`final_round2_evidence_inventory.md` · `FINAL_REPRODUCIBILITY_MANIFEST.json` ·
`claim_evidence_matrix.md` · `MANUSCRIPT_RELEASE_GATE.md` ·
`rescued_tmp_20261001/` (incl. SHA256_MANIFEST) ·
`ARCHIVED_LHL_PROVENANCE_AUDIT.md` · `archived_vs_current_runner_diff.md` ·
`historical_result_exclusion_reason.md` · `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`
(+ bootstrap JSON in mv_adapter) · `STRICT276_TEXTURE_FIDELITY_AUDIT.md` (+
texture_audit/) · `baking_consistency_report.md` (+ bake_consistency/) ·
`STRICT276_CORE7_MATRIX.md` · `metric_direction_audit.md` ·
`statistics_reproducibility_audit.md` · `FINAL_NARRATIVE_RECOMMENDATION.md` · this
report.
