# Final Narrative Recommendation (final_audit_20261001, Phase 7)

Date: 2026-10-01. **No manuscript text has been modified** — this document only
recommends. All evidence referenced is verified in this audit directory and its
companion reports.

## 1. Recommended main-contribution framing

NOT:

> "We discover an optimal LLH schedule."

Recommended:

> "We analyze adapter residual allocation across network depth and denoising stages,
> showing that temporal placement and layer redistribution are separate factors. The
> proposed layer-wise stage-aware control improves fidelity under the main MVPainter
> pipeline, transfers partially to one additional adapter architecture, and reveals
> architecture-dependent applicability boundaries."

This framing is exactly what the evidence now supports:

| pillar | evidence |
|---|---|
| Separate factors | Main backbone: layer effect strong (same-runner, 7/7 metrics) AND temporal effect present (Core-7/C3 panel); MV-Adapter: layer effect present (P1/P2/P4), temporal NOT_SUPPORTED; MVDiffusion: layer NOT_REPLICATED |
| Main-pipeline improvement | Core-7 same-runner matrix: LLH best of 7 conditions on FG-PSNR/FG-LPIPS/Full-PSNR/Full-SSIM; beats no_adapter (+5.149* FG-PSNR) and global_fixed_high (+0.822*/+2.585*) |
| Partial transfer | MV-Adapter 76-object panel: layer-wise SUPPORTED on PSNR/dE00/GT-texture, small SSIM reverse, LPIPS ns; mapping-robust (Phase 2) |
| Boundary | MVDiffusion: layer-wise NOT_REPLICATED (negative preserved); MV-Adapter temporal NOT_SUPPORTED |

## 2. Claim downgrade rules (mandatory rewrites for the next paper window)

| Do NOT say | Say instead | Because |
|---|---|---|
| "generalizes across backbones" | "shows transferability across one additional adapter architecture (MV-Adapter), and does not replicate on a third architecture (MVDiffusion)" | MVDiffusion negative result; PARTIAL alpha interface |
| "CAI automatically discovers the schedule" | "CAI provides diagnostic motivation; the frozen CAI selection rule is set-valued and did not uniquely select a schedule" | Ledger row NOT_SUPPORTED (undefined_set_valued) |
| "universal optimal schedule" / "the optimal LLH" | "an architecture-dependent effective residual allocation pattern; on the main pipeline the late-stage-high/low-shallow profile is best of seven same-runner conditions" | MV-Adapter temporal ns; MVDiffusion negative; factorial direction flips |
| "improves texture quality" (unqualified) | "yields generated texture statistics closest to GT (distance-to-GT framing: CIEDE2000 and Laplacian/gradient variance distances), with listed exceptions" | Texture audit; hf_energy cells favor LFM/LHL; grad favors HLL |
| "robust to arbitrary layer grouping" | "robust to the tested contiguous layer partitions: the budget-neutral re-partition is statistically indistinguishable (6/6 metrics), the degenerate partition bitwise identical, and the frozen-value re-assignment (M3) preserves the direction with slightly stronger primary effects; PSNR significance weakens under the budget-neutral re-partition" | Mapping-sensitivity reports (B′ + M3, both committed) |
| "robust to reference-preprocessing randomness" alone (as LHL anomaly explanation) | "the archived historical record is excluded because complete provenance cannot be guaranteed" — never attribute the gap to augmentation randomness | Case-B forensics: realization lottery is mean-neutral (0.03 dB); unseeded-realization wording retired |
| "+0.96 dB" / archived 14.78 numbers | never quote; all baselines come from the Core-7 same-runner table | Case-B exclusion + UID overlap |
| "robust/stable conclusions" (blanket) | "conclusions stable across two frozen realization sets (R0/R1): all paired deltas STABLE_STRONG on 27/28 cells, 1 STABLE_DIRECTIONAL" | Robustness-1 summary |

## 3. What to KEEP at current width (already defensible)

1. **Headline fidelity result**: strict-276 same-runner Core-7 matrix; LLH best of
   seven conditions on primary fidelity metrics. (Reviewer-1)
2. **Stochastic stability**: R0/R1 realizations; realization mean-neutrality now
   quantified (0.03 dB).
3. **Texture response**: distance-to-GT framing, two independent metric surfaces.
4. **Cross-backbone**: MV-Adapter layer-wise SUPPORTED with robustness across the
   tested contiguous layer partitions (budget-neutral B′ indistinguishable; frozen-value
   M3 direction-preserving and slightly stronger); the
   temporal dimension separates across backbones; MVDiffusion as a stated negative.
5. **Bake**: 12-object case study with seam/cross-view consistency descriptors
   (descriptive only).

## 4. Required manuscript changes (next window; LIST ONLY — not done here)

1. Replace any residual "unseeded realization" causality for the archived record with
   the Case-B sentence (`historical_result_exclusion_reason.md` section C wording).
2. Ensure no table/figure cites archived or cross-runner numbers for the baseline
   family — the Core-7 matrix replaces them.
3. Downgrade the three claim wordings in section 2 rows 1-3 wherever they appear
   (check intro/conclusion/limitations).
4. Add one sentence on mapping-robustness (MV-Adapter) where the cross-backbone
   transfer is claimed — at the tested-partition width (B′ + M3), never "invariant to
   the exact layer partition".
5. Add the texture distance-to-GT summary (one row: CIEDE2000 + one probe) if the
   texture concern response needs strengthening; keep the exceptions.
6. Verify Supplementary disclosure still matches the frozen realization protocol
   (S9/S10 wording — unchanged by this audit).
7. If the 3D-baking paragraph cites seam/consistency behavior, cite
   `baking_consistency_report.md` descriptors, not the removed DISTS claims. Name the
   cross-view metric a *render-time cross-view color-stability descriptor* (supplementary
   grade); only the UV-seam ΔE00 metric is direct texture-space evidence.

## 5. Additional experiments (post-audit status, updated at evidence convergence)

1. ~~**M3 mapping run**~~ — **DONE**: committed at `75a4068` (3 × 76 = 228 rows;
   16/18 MAPPING_STABLE; primary effects slightly stronger). Incorporated into
   `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md` and this document.
2. ~~**LHL-forensics stage-2**~~ — **DONE**: committed at `75a4068`
   (`core7_same_runner_completion_20261001/lhl_forensics/`); aug-ON regen bit-exact,
   aug-OFF still −6.96 dB on hexuid → cond-augmentation hypothesis refuted; Case B
   unchanged and strengthened.
3. **MVDiffusion depth-concat variant** exploration: only if a reviewer demands a
   positive cross-backbone result; current boundary framing is sufficient and honest.
4. No further GPU runs are required for the current claim set. **The experiment phase
   is frozen: no fourth backbone, no schedule search, no strict-276 seed expansion, no
   bake enlargement without an explicit reviewer requirement.**
