# 48-hour R1 color-fidelity validation — final report

**Window:** started 2026-10-08 13:58 UTC (21:58 Beijing); completed early on 2026-10-08. The task deadline was 2026-10-10 13:30 UTC. This report closes the authorized experiment without waiting out the full window.

**Workspace / branch:** `/4T/CXY/MV-Painter-r1color`, `codex/r1-fidelity-validation-48h-20261008`, based on frozen start commit `7311b9446733637e0f0a8e85211cd7fc02c67810`.

## Executive finding

The evidence supports an average LLH advantage over GFL on both Fresh C (`n=300`) and the disjoint Fresh B holdout (`n=150`), but not a uniform color/detail guarantee. The independent Fresh B highest-texture quartile (`Q4`, `n=38`) has worse CIEDE2000 and FG-PSNR under LLH. The old 26-object set was deliberately assembled for visible failures; its 20 UIDs overlapping Fresh C have different saved prediction RGBs in all three conditions, so the two statistics are not repeated measurements of the same outputs. A cross-stack trace localizes the first observed numerical divergence for three locked objects to initial-latent scaling, but software-library versions changed together and the remaining 117 outputs were not tensor-traced.

The color-condition audit found no wrong-object input, stale embedding, changed vision asset, or preprocessing identity bug. A single selected appearance view plus one global embedding does not provide six per-view color targets; that is a plausible information limit, not a proven unique cause. The original Fig. 4 failure already appears without an adapter and remains under GFL/LLH. The ordinary GT VAE round-trip is much smaller than the generated mismatch and does not reproduce its direction. No specific color bug was identified; Phase D correctly stopped before another schedule/scale search. **No color fix is validated.**

For the paper, use **decision B**: preserve the tested schedule and properly paired average cohort results, while narrowing color/detail claims and stating the GT-defined high-texture boundary. Keep original Fig. 4/6 unchanged pending the paper agent's independent decision. The original six-view repeat issue is already corrected in the evaluation protocol; visible RGB color shifts occur before texture baking; the complete generation mechanism remains unresolved; the residual-gating prototype remains a negative result.

## Phase A — identity and apparent LLH/GFL conflict

### Source cohorts

| Source | Scope | Identity and comparability |
|---|---|---|
| strict-276 Core-7 | 276 objects × 7 conditions | Checkpoint matches. 50-step Euler / unique6 / seed `42 + index`. The retained package lacks canonical UID crosswalk for legacy labels, five older conditions lack per-object input tensor hashes, and per-object RGB/CIEDE images are absent. It supports separate method-performance context, not direct color comparison. LLH−GFL FG-PSNR is +3.2443 dB [2.9463, 3.5305]; LLH ranks first in 4/7 endpoints. |
| Fresh C | 300 objects; GFL from `c3_confirmation`, LLH from `revision_era_addendum` | Same checkpoint `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`, runner `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`, config `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`; all six logged GFL/LLH model input hashes agree on 300/300. Campaign inference package versions are not explicit in its run manifest. |
| Fresh B | 150 frozen objects; independent holdout | Same checkpoint/runner/config; all six logged GFL/LLH input hashes agree on 150/150. UID-disjoint from both Fresh C and diagnostic-26. PNGs match the pre-unblind manifest. Campaign inference package versions are not explicit in its run manifest. |
| Diagnostic-26 | 26 visually/forensically selected objects; No Adapter/GFL/LLH | Same checkpoint and base runner; saved RGB is a distinct generation instance from Fresh C for all 20 common UIDs × 3 conditions (60/60 hashes differ). It is not a random population sample. Its metric reload used Python 3.10.20 for PSNR/LPIPS and Python 3.13.5 for color/texture; its exact inference runtime is not fully pinned. |

Across Fresh C/B, the paired schedule is 50-step Euler at 256×256 with unique six-view order `[0,15,12,16,13,14]` and per-index seed policy. GFL's effective scales are deep/middle/shallow `1.25/1.25/0.80`. LLH uses `1.25/1.25/0.50` on steps 0–16 and 17–32, then `2.50/2.50/0.75` on steps 33–49. These are not equal-dose controls; requested and applied scales are recorded separately. Residual logs describe the applied schedule but are not treated as causal proof.

The shared checkpoint SHA above identifies the model/adapter weights. All three campaigns point to the same `a3_normalization.json` spec (SHA-256 `fdf2987b7931f71e15efa47f2012148e5509cfde25cf85169329b48e884b6c4b`); the runner manifest also records condition-specific scale traces and caps. The base runner SHA is shared. Thus the named control arms vary the adapter application/schedule, not the checkpoint weights.

### Paired RGB results

All intervals below are two-sided 95% percentile intervals from 10,000 paired object bootstrap draws. Lower is better for CIEDE2000, LPIPS and GT-relative Laplacian error; higher is better for PSNR/SSIM. Cohorts are not pooled.

| Cohort | LLH−GFL CIEDE2000 | FG-PSNR | FG-LPIPS | GT-relative Laplacian error |
|---|---:|---:|---:|---:|
| Fresh C `n=300` | −2.232 [−3.137, −1.338], favorable 187/300 | +1.143 dB [+0.814, +1.480], 169/300 | −0.01748 [−0.02003, −0.01496], 221/300 | −0.01786 [−0.01866, −0.01709], 300/300 |
| Fresh C excluding diagnostic-overlap UIDs `n=280` | −2.188 [−3.120, −1.274] | +1.097 dB [+0.768, +1.431] | −0.01732 [−0.01977, −0.01490] | −0.01779 [−0.01856, −0.01702] |
| Fresh B disjoint holdout `n=150` | −1.905 [−3.262, −0.529], 85/150 | +1.030 dB [+0.577, +1.493], 77/150 | −0.01556 [−0.01920, −0.01192], 111/150 | −0.01871 [−0.02016, −0.01743], 150/150 |
| Diagnostic-26 forensic set `n=26` | +3.583 [+0.544, +6.619], 9/26 favorable | −0.197 dB [−1.562, +1.304], 7/26 | −0.01294 [−0.02708, +0.00025], 13/26 | −0.00879 [−0.01109, −0.00669], 26/26 |

The diagnostic-26 outcome does not directly contradict the large-cohort estimate: selection is failure-focused, runtime lineage is not fully pinned, and overlapping UIDs have different generated PNGs. In the new Fresh C outputs for those 20 same UIDs, LLH−GFL CIEDE2000 is −2.838 [−7.833, +2.090], with 14/20 lower; this interval is wide and does not reproduce the old output-instance result. The conflict is only **partially explained** because the exact share attributable to selection versus stack/output-instance drift is unresolved.

### GT-defined complexity boundary

Fresh B quartile cut points were fixed from GT Laplacian variance before inspecting generated outcomes: `0.00685639`, `0.01771007`, and `0.03139245`; quartile counts are 38/37/37/38. Fresh B Q1 LLH−GFL is −8.756 CIEDE2000 [−10.805, −6.569], +3.646 dB PSNR [+2.761, +4.471], and −0.03768 LPIPS [−0.04295, −0.03250]. In Q4 it is +3.624 CIEDE2000 [+1.907, +5.303], −0.770 dB PSNR [−1.165, −0.315], and −0.00008 LPIPS [−0.00562, +0.00519]. Only 10/38 Q4 objects improve CIEDE2000 and 7/38 improve PSNR. Fresh C Q4 using the same fixed cuts trends in the same direction, but is exploratory and not a substitute for Fresh B.

This supports a real high-texture limitation alongside average improvement. The exploratory Spearman association between GT HF energy and LLH−GFL CIEDE delta is 0.629 in Fresh C and 0.672 in Fresh B; this is descriptive association, not a causal mechanism.

## Phase B — validation protocol and image audit

The locked primary contrast is `LLH − GFL`, paired by object UID within each cohort. CIEDE2000 is recomputed from SHA-verified saved uint8 RGB, with six per-view foreground means equally weighted to match the frozen R1 diagnostic metric. Target panels reproduce the frozen white alpha composite, unique6 order, necessary reverse-view rotations, antialiased bicubic resize and round-to-nearest serialization. FG-PSNR/LPIPS/SSIM are the original per-object campaign rows; GT-relative Laplacian error is recomputed from the same saved RGB, target, and eroded GT foreground mask. Fresh B's reconstructed GT texture values agree with all 150 official values within `3e-7`.

The initial pixel-pooled CIEDE pass is explicitly superseded and excluded. `ANALYSIS_METHOD_CHANGELOG.md` records why the final aggregation follows the prior R1 per-view rule. Every object-level row retains image and input hashes. `B_FAILURE_AND_SUCCESS_GALLERY.pdf` displays GT/GFL/LLH for GT-only median-nearest Q1/Q3/Q4 Fresh B examples; selection did not use generated outputs. The existing ten-page diagnostic casebook separately includes the selected No Adapter/GFL/LLH failures.

## Phase C — color-condition cause

### Causal contrasts

Fresh C No Adapter/GFL share all six logged inputs on 300/300 objects, and prediction PNGs match run-manifest hashes. GFL−No Adapter averages −11.228 CIEDE2000 [−12.929, −9.540], +4.330 dB PSNR [+3.958, +4.689], and −0.02370 LPIPS [−0.02860, −0.01882]. Its GT-relative Laplacian error changes by +0.01876 [+0.01636, +0.02122], and mean absolute a*/b* residual magnitudes rise by +2.389 [+1.747, +3.002] and +1.199 [+0.500, +1.884]. These endpoints are mixed: adding GFL does not systematically increase CIEDE2000, but it also does not guarantee every color channel moves closer to GT. In the original Fig. 4 diagnostic cases, the visible pink/purple shift is present in No Adapter and remains under GFL and LLH.

### Condition, stage, and VAE evidence

The Fresh C audit verifies the selected `000/014` source PNG, deterministic white-composited 512×512 RGB tensor, per-object embedding bytes/tensor, use-site hash, code, and vision assets for 300/300 objects. The selected source view has varied foreground colors, but one view plus one global embedding is not six view-specific RGB targets. This makes insufficient view-specific appearance information plausible; no unique cause is proved and no preprocessing correction is supported.

For the original Fig. 4 row 1, a pink surface is visible in the GFL decoded snapshot by scheduler update 40. The artifact is in generated RGB before baking and GLB export. Earlier noisy snapshots do not establish the exact first latent step. The paired GT VAE mode round trip has foreground CIEDE2000 about 4.086, while GFL is 22.032; ordinary GT encode/decode alone is therefore insufficient to explain the generated shift. A decoder interaction with generated latents remains possible. Residual/metric correlation is not used as causal evidence.

The measured RGB discrepancies are relative to rendered GT views. There is no calibrated physical-color chart in this evidence; only the visually reviewed pink/purple cases should be called visibly undesirable color shifts, not every numeric mismatch physically impossible.

## Phase D — repair gate

No single input, color-space, VAE, or adapter bug was established. The condition identities pass and the ordinary VAE round trip is not sufficient to explain the reviewed mismatch. A new Gate threshold, adapter-scale, or timestep search would not be a repair of a proven defect. Phase D was skipped by its precondition; `D_PAIRED_VALIDATION.csv` records one no-go row. No GT-guided recoloring or post-processing was performed. `COLOR_FIX_VALIDATED = NO`.

The prior residual-gating prototype remains negative: it did not materially reduce the reviewed cast, and its CIEDE endpoint worsened relative to C3 in the selected set. It must not be presented as a validated color method.

## Phase E — manuscript/reviewer evidence

The original reviewer requests (a) full-object comparisons including the unmodified and fixed-scale baseline, (b) baked unseen views and seams/cross-view consistency, and (c) a distinction between texture variation and texture fidelity. This packet supports the color/detail response with broad paired Fresh C/B RGB statistics and condition/hash audits, plus the fixed-rule Fresh B gallery and 26-object forensic casebook. It does **not** itself close baked unseen-view or seam evaluation; those concerns require separately identity-linked bake/render evidence.

Recommended manuscript action is decision B. Keep original Fig. 4/6 files unchanged; clarify their local illustrative scope; narrow any broad color/texture fidelity language; state that average results do not hold uniformly in high-texture objects; explain that the root cause and a validated color repair remain unresolved. Add a limitation that the condition chain uses one selected appearance view plus a global embedding, not per-target-view color GT. Do not turn texture magnitude into fidelity or the residual-gating negative into innovation.

Response-letter wording and source-specific manuscript recommendations are in `R1_RESPONSE_READY_TEXT.md` and `MANUSCRIPT_CHANGE_RECOMMENDATIONS.md`. Figure/UID/caption/hash information is in `FIGURE_SELECTION_AND_CAPTIONS.md`. Numeric claims are mapped to source cohort manifests, metric implementations, raw image hashes and result files in `EVIDENCE_AUTHORITY_MAP.csv`.

## Runtime, experiments, and delivery scope

- New diffusion inference runs: **0**. New color-fix runs: **0**. GPU time: **0**. The task reused frozen RGB and reports; all new calculations were CPU analyses and hash/identity audits.
- Main analysis scope: Fresh C 300 GFL/LLH; Fresh B 150 GFL/LLH; Fresh C 300 No Adapter/GFL; diagnostic-26 as separate forensic rows; strict-276 as separate non-RGB context; condition/hash audit 300; all-pair identity audit 450; residual-log identity/step audit. The previous root-cause trace remains a separate three-object, three-stack trace and was not rerun here.
- Checkpoint/runner/config: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` / `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` / `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Analysis environment recorded in `INITIAL_STATE.json`: Python 3.13.5, torch 2.7.1+cu128, torchvision 0.22.1+cu128, Diffusers 0.37.0, Transformers 4.57.6, NumPy 2.2.6, scikit-image 0.26.0, Pillow 12.2.0. This is the CPU analysis/reconstruction environment; do not infer it was the omitted Fresh C/B campaign inference runtime.
- The new delivery directory is about 32 MB before the checksum manifest. No individual artifact approaches GitHub's 100 MB file limit. The 2 GB-class tensor traces and thousands of source cohort PNGs remain in their existing local source-of-truth worktrees; they were not duplicated. Compact tensor-difference tables, run/source manifests, row-level PNG SHA identities, and selected case images are included instead. The frozen prior casebook is referenced, not modified or duplicated.
- Original submitted TeX, Fig. 4/6 PDFs, and the paper agent worktree were read-only. No manuscript or official figure was changed.
- Every file in this package will be listed in `SHA256SUMS.txt` (excluding the checksum file itself); row-level source identity is retained in the CSVs. The final branch/commit and push outcome are reported in `FINAL_READINESS_VERDICT.md` and the completion message.

## Primary package index

- Protocol and comparison: `A_PROTOCOL_COMPARABILITY.md`, `B_VALIDATION_PROTOCOL.json`, `A_CONTRADICTION_VERDICT.md`, `B_PAIRED_STATISTICS.md`.
- Object-level evidence: `A_COHORT_HETEROGENEITY.csv`, `B_OBJECT_LEVEL_RESULTS.csv`, `DIAGNOSTIC26_REANALYSIS.csv`, `C_CAUSAL_PROBE_RESULTS.csv`, `PAIRED_BOOTSTRAP_STATISTICS.csv`, `A_QUARTILE_EFFECTS.csv`.
- Input and output provenance: `RGB_HASH_AND_INPUT_AUDIT.csv`, `ALL_COHORT_INPUT_PAIR_AUDIT.csv`, `C_APPEARANCE_CONDITION_OBJECT_AUDIT.csv`, `RESIDUAL_LOG_IDENTITY_AUDIT.csv`, `RESIDUAL_LOG_STEP_PAIRED.csv`, `RESIDUAL_LOG_STEP_SUMMARY.csv`.
- Gallery and paper handoff: `B_FAILURE_AND_SUCCESS_GALLERY.pdf`, `CASE_IMAGES/FIG4_ROW1/`, `R1_RESPONSE_READY_TEXT.md`, `MANUSCRIPT_CHANGE_RECOMMENDATIONS.md`, `FIGURE_SELECTION_AND_CAPTIONS.md`, `EVIDENCE_AUTHORITY_MAP.csv`.
- Phase D: `D_FIX_CANDIDATE.md`, `D_PAIRED_VALIDATION.csv`, `D_FIX_GO_NO_GO.md`.
