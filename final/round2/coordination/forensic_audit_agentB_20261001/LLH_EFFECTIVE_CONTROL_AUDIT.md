# LLH_EFFECTIVE_CONTROL_AUDIT.md (Phase 1B — agent B)

Trigger: `TOO_CLEAN_RESULT_TRIGGER` — LLH ranks first on all seven headline
metrics in the same-runner matrix. Task doc: verify the win is not produced by
a larger effective residual budget, cap interactions, stage-length mismatches,
or a runner/table naming divergence.

Code paths verified (read-only):
- Schedule definitions: `geotex/layer_lhl_ablation_shared.py` L54–76 (dev) and `scripts/run_layer_confirmation_276_20260930.py` `SCHEDULES` + `protocol_manifest()` L151–152 (formal).
- Application + cap: `MVPainter/mvpainter/model_unet_geotex.py` `GeoTexResnetWrapper.forward` L326–368 — `effective_scale = min(_adapter_scale, _max_scale)`, `_last_correction` stores the **post-scale** correction.
- Caps: `LAYER_MAX_SCALES = {deep 3.0, middle 3.5, shallow 0.8}` (class attr, L298–302).
- Stage partition: `progress = step/49`; early/middle/late = **17/16/17** steps at 50 steps (documented in the formal manifest and re-derived here).
- The `eval_exploration.py` monkey-patched forward (no cap, L314–325) is inside its CLI `main()` only — **not active** in the formal runner path, which imports `ee` solely for `load_model`/`compute_metrics` and generates via `explore_contradiction.generate_with_schedule` on the native (capped) wrapper. No monkey-patch in `explore_contradiction.py`.

## Effective per-group scale table (requested → applied)

Requested stage scales (early/middle/late) and their time-averages under the
17/16/17 partition; "effective" applies the per-group cap. Script:
`phase1b15_effective_budget.py`; raw: `phase1b15_effective_budget_stats.json`.

| method | deep req→eff | middle req→eff | shallow req→eff | capped anywhere |
|---|---|---|---|---|
| no_adapter | 0 → 0 | 0 → 0 | 0 → 0 | – |
| global_fixed_low (GFL) | 1.25 → 1.25 | 1.25 → 1.25 | 1.25 → **0.80** | **shallow, always** |
| global_fixed_high (GFH) | 2.50 → 2.50 | 2.50 → 2.50 | 2.50 → **0.80** | **shallow, always** |
| global_fixed_mean (GFM) | 1.667 → 1.667 | 1.667 → 1.667 | 1.667 → **0.80** | **shallow, always** |
| global C3 | 1.65 → 1.65 | 1.65 → 1.65 | 1.65 → **0.80** | **shallow, always** |
| layer_llh | 1.25/1.25/2.50 → 1.675 | same | 0.50/0.50/0.75 → 0.585 | never |
| layer_lhl | 1.25/2.50/1.25 → 1.650 | same | 0.50/0.75/0.50 → 0.580 | never |
| layer_fixed_mean (LFM) | 1.65 → 1.65 | 1.65 → 1.65 | 0.58 → 0.58 | never |

Findings:

1. **The shallow cap (0.8) binds for every global schedule.** All "global"
   methods share an identical effective shallow budget (0.8 flat) regardless of
   their requested value. Consequence: global-vs-layer comparisons differ on
   shallow in *total effective budget* (0.8 vs 0.58–0.585), not just placement.
   This must be described in any "budget-neutral" wording.
2. **LLH never touches a cap** (max requested 2.50 < 3.0/3.5; shallow ≤ 0.75 <
   0.8). Its applied schedule equals its requested schedule; no hidden
   clipping shapes the LLH result.
3. **LLH does run a larger deep/middle budget than GFL** (time-mean 1.675 vs
   1.25, +34%) and a smaller shallow budget (0.585 vs 0.80). So the headline
   LLH−GFL +3.24 dB **cannot be read as a pure "when" effect** — see
   `RESIDUAL_BUDGET_CONFOUND_AUDIT.md` for the decomposition.
4. **Stage-length asymmetry (17/16/17) leaks ~1.5 % extra deep/middle budget
   into LLH vs LHL/LFM** (late band has 17 steps vs middle 16): LLH time-mean
   1.675 vs 1.65. The runner's own comment "Exact means under the 17/16/17
   partition" (value 1.65) matches the 16-step-late assumption; the actual
   partition makes LLH's mean 1.675. Quantified impact ≈ +0.11 dB (below).
5. **Runner/table naming consistency**: formal condition names
   (`layer_llh`, `global_fixed_low`, …) map 1:1 to the schedule definitions
   above; the Core-7 GFL anchor reproduced bit-exactly and shared-input audits
   found 0/276 input mismatches (`core7_same_runner_completion_20261001/SHARED_INPUT_AUDIT_CORE7.json`), so "the table says LLH but the runner did X" is
   excluded for the same-runner matrix.
6. **No per-step residual-norm logs exist for the formal runs** (the runner
   passes `residual_log={}`). The requested/effective table above is therefore
   the authoritative budget description; if reviewers ask for integrated
   residual norms, a logging probe would be needed (not paper-blocking).

## Gradient-energy sanity (mechanism note verification)

Independent recomputation of Σ(pred FG gradient)/Σ(GT FG gradient) from
per-object CSVs (GT columns bitwise-identical across runs):

| condition | ratio | source |
|---|---|---|
| no_adapter | 0.890 | core7 formal |
| global_fixed_high | **1.110** | core7 formal |
| layer_llh | 1.128 | confirmation |
| layer_fixed_mean | 1.201 | confirmation |
| layer_lhl | 1.254 | confirmation |
| global_fixed_low | 1.542 | robustness R1 copy |

Reproduces the 0.89 / 1.54 / 1.13 mechanism numbers. **One correction**:
`CORE7_SAME_RUNNER_REPORT.md` L86–88 calls layer_llh "closest" to GT gradient
energy; global_fixed_high at 1.11 is in fact marginally closer than LLH at
1.13. The mechanism sentence, if migrated to the paper, should not claim LLH is
the best gradient-energy-calibrated condition — GFH's good calibration despite
its FG-PSNR loss (−0.822 dB vs LLH) actually *supports* the claim that
allocation timing matters beyond total energy. (Report file belongs to the
parallel session; not edited here — flag for the erratum list.)

## Verdict

`VALIDATED_WITH_LIMITATIONS` — LLH's seven-for-seven first place is not a
labeling, cap, or runner artifact: its schedule is applied as requested, never
capped, and clearly distinguishable from every comparator (LLH−LHL Full-PSNR
wins 276/0). Limitation: LLH carries a +34 % deep/middle effective-budget
advantage over GFL and a ~1.5 % one over LHL/LFM (stage-length asymmetry);
claim language must separate "allocation effect" from "temporal placement
effect" accordingly.
