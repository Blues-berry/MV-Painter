# CROSS_RUNNER_SCALE_SEMANTICS_AUDIT.md (agent B — Phase 2/3 escalation)

**Headline finding: the paper mixes two scale-application regimes across its
panels, and the magnitude of the resulting cross-panel shift (up to 7.7 dB
FG-PSNR, with an ordering flip) is far larger than the 0.00395 Full-SSIM
example the manuscript uses to justify non-pooling.**

## 1. Two code regimes (verified by file diff)

The repo wrapper (`MVPainter/mvpainter/model_unet_geotex.py`, since commit
eb1a0a5, July) applies per-depth-group caps:
`effective_scale = min(_adapter_scale, LAYER_MAX_SCALES)` with
deep 3.0 / middle 3.5 / **shallow 0.8**.

The `/tmp/mv_main_rerun` copy (the code tree that executed the clean-v2
four-condition run and the stage-placement run — its
`create_stage_placement_protocol.py` names
`evaluation_code: /tmp/mv_main_rerun/geotex/eval_exploration.py`) contains the
LEGACY wrapper: `correction = correction * self._adapter_scale` — **uncapped,
no depth groups**. Configs are otherwise byte-identical (verified by diff:
only the object-list/view-mode lines differ); checkpoint is the same
(0618d6b2…); cond preprocessing shows no preprocessing-range differences.

## 2. Empirical signature (same condition, same objects, same checkpoint)

Per-object comparison of global scale 1.25 ("fixed_low") across the two
regimes, strict-276: confirmation (capped) minus clean-v2 (uncapped) FG-PSNR:
mean **+3.70 dB**, median +3.71, range [−2.77, +6.86], only 0.7 % of objects
within 0.5 dB — a uniform pipeline-level shift, not a realization effect
(R0/R1 realization drift is ≈0.03 dB by the robustness audit).

| condition | uncapped panel (tab:strict276 / stage276) | capped frozen protocol | Δ FG-PSNR |
|---|---:|---:|---:|
| no_adapter | 8.776 | 8.826 (core7) | +0.05 ✓ (no correction → regime-independent) |
| fixed_low | 7.030 | 10.731 | **+3.70** |
| fixed_high | 5.410 | 13.153 (core7) | **+7.74** |
| C3 | 6.763 | 11.939 (r0_completion) | **+5.18** |

Stage-placement global schedules (tab:stage276: fixed_mean 6.257, HLL 5.583,
LHL 6.760, LLH 6.937) are likewise uncapped-era numbers.

The no-adapter row's invariance (+0.05 dB) is the control that isolates the
wrapper change: everything with an active correction shifts, exactly in
proportion to its uncapped shallow exposure (fixed_high 2.5 → largest shift).

## 3. Consequences

1. **Ordering flip.** Under caps, fixed_high beats fixed_low on FG-PSNR
   (+2.42 dB) and every other headline metric; in the uncapped panel
   fixed_low beats fixed_high. The clean-v2 panel's "non-dominance"
   paragraph (final_round2.tex L464–468: "fixed-low has higher Full-PSNR,
   FG-PSNR, and FG-SSIM") is an **artifact of the uncapped regime** and is
   reversed under the paper's own documented method (the method figure shows
   per-group caps).
2. **The No-Adapter FG paradox is an uncapped artifact.** In tab:strict276,
   no_adapter FG-PSNR (8.776) exceeds fixed_low (7.030) — under caps it does
   not (8.826 vs 10.731). The real, regime-independent no-adapter signature
   is background collapse (bg_psnr 11.0 vs 20–26) plus the FG-SSIM blur
   pseudo-advantage (0.480, first of seven; gradient energy 0.89× GT).
3. **Affected paper tables:** tab:strict276, tab:stage276, tab:serialized276,
   and every cross-panel absolute comparison involving global schedules. The
   layer-wise confirmation tables (LLH/LHL/LFM ± GFL/GFH/no_adapter, Core-7)
   are **capped-era, internally paired, and unaffected**: layer schedules
   never touch the caps (max requested 2.5 < 3.0/3.5; shallow ≤ 0.75 < 0.8),
   so capped and uncapped wrappers produce identical layer-schedule injections
   — the caps only bind for global schedules.
4. **Claim survival check.** The paper's load-bearing same-runner
   comparisons (LLH vs GFL/GFH/no_adapter/LHL/LFM; stage-placement global
   LLH vs LHL/HLL/fixed_mean within their own uncapped run) each remain
   internally valid. What does NOT survive is any absolute cross-panel
   reading and the clean-v2 non-dominance narrative.
5. **A capped four-condition table already exists in artifacts** (this file,
   §2 column 3): no_adapter/GFH from Core-7, GFL from the confirmation,
   C3 from `r0_completion_global_c3` — all the frozen protocol, strict-276,
   R0 seeds, cross-process input-identity verified (GFL anchor bit-exact).
   The revision window can replace tab:strict276's numbers with these (or
   re-run one runner instance if a single-process table is demanded).

## 4. Required manuscript actions (revision window; listed only)

1. Replace tab:strict276 with capped-protocol values (or add an explicit
   caption stating the uncapped legacy semantics of the original run).
2. Rewrite the non-dominance paragraph (L464–468) — under the documented
   method, fixed-low does not dominate fixed-high.
3. Upgrade the cross-panel disclosure (L436–444): state the wrapper-regime
   difference (caps) as the cause, and the dB-level magnitude, not only the
   0.00395 SSIM example.
4. Mark tab:stage276/tab:serialized276 as legacy-semantics global-schedule
   panels (internally paired; conclusions about placement direction survive,
   absolute levels are regime-specific).
5. No historical number needs quarantine beyond what Case B already excludes;
   the uncapped panels stay usable as within-panel paired evidence with the
   disclosure above.

## Verdict

`QUARANTINED` for cross-panel absolute use of uncapped global-schedule
numbers; `VALIDATED` for all within-panel paired conclusions and for the
capped frozen-protocol evidence chain.
