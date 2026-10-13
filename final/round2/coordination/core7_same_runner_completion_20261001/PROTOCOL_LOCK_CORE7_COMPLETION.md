# PROTOCOL LOCK — Core-7 same-runner completion (2026-10-01)

Written BEFORE any no_adapter / global_fixed_high strict-276 metric was
observed in the R0 namespace. Branch `codex/round2-evidence-integrated-20261001`
(at `d30ed4f`). Task boundary: experiment + audit + experiment report ONLY.
No paper text, supplementary, or response-letter changes.

## Question this run answers

Reviewer 1's original request was "unmodified pipeline + competitive
fixed-scale baseline" under the same holdout protocol. The frozen strict-276
same-runner matrix (Core-5: GFL/GC3/LFM/LHL/LLH, R0 namespace) contains
neither the adapter-free condition nor the competitive fixed-HIGH scale.
This run completes the matrix to Core-7 so that all seven conditions are:
same cohort (strict-276 clean_v2) + same runner code path
(layer-confirmation-strict276-v1) + same realization (R0, object_seed =
42 + idx) + same initial latent (seed 42) + shared per-object inputs.

## Frozen candidate additions — NO additions beyond these two, NO re-selection

| ID | Runner name | Definition |
|---|---|---|
| NO-ADP | no_adapter | geo_feats=None passed to generate_with_schedule; wrappers never receive _current_geo_feats, so the adapter correction is skipped entirely = unmodified pipeline. Schedule function returns 0.0 (unused, kept for code-path identity). Semantics precedent: geotex/round2_main_eval.py SCHEDULES no_adapter (scale 0.0 + geo_feats None). |
| GFH | global_fixed_high | scale 2.50 constant (global, all depth groups). Effective = min(requested, cap) per wrapper: deep 2.5, middle 2.5, shallow 0.8. Precedent: round2_main_eval.py fixed_high scale 2.50; 2.50 is the frozen "high" grid value used by C3/LHL/LLH mid/late stages. |

Forbidden: any other schedule, any new controller, ANY post-hoc re-selection,
and any use of these rows to tune or re-derive schedules. This is a
confirmation surface only.

## Realization and protocol (byte-identical to the frozen R0 records)

Identical to PROTOCOL_LOCK.md in
final/round2/coordination/main_backbone_robustness1_20260930/, R0 namespace:

- Config /4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml
- Checkpoint mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt
  (SHA-256 0618d6b2...14c0)
- Object list final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt
  (SHA-256 a6aa8ab6...d044, 276 objects, order preserved)
- object_seed = 42 + object_idx for python random / numpy / torch before
  collate_batch; torch.manual_seed(42) before initial latent AND again
  immediately before generate_with_schedule
- unique6 views [0,15,12,16,13,14] @ 256x256; 50 steps Euler discrete;
  metric path geotex.eval_exploration.compute_metrics
- Per-object-per-method code path: verbatim copy of the frozen
  scripts/run_layer_confirmation_276_20260930.py block (identical to the
  R1 runner's verbatim block).

## Shared-input integrity (stronger than the R0 runs)

Each formal row records SHA-256 of: cond_imgs, target_imgs, normal(depth)
imgs, real_depth imgs, global_embeds, init_latent. Post-hoc audit must show:

1. cross-method: within each GPU process, hashes identical across that
   process's schedule(s);
2. cross-process: no_adapter (GPU0) vs global_fixed_high (GPU1) hashes
   identical per object;
3. anchor: preflight GFL rows must be bit-exact vs the frozen R0
   global_fixed_low_rows.json metrics (all metric columns, full float
   precision), which anchors the namespace reproduction.

Aborts: any in-run hash mismatch aborts the formal run immediately
(raise + no row written).

## Preflight gate (mandatory before the formal 552)

10 fixed strict-276 objects — random.Random(20260930).sample(range(276),10)
= indices [11,25,113,141,157,207,214,236,239,256] (the canonical frozen
sample; identical to the executed JSON sample of BOTH prior audits —
SHARED_INPUT_DETERMINISM_AUDIT and ROBUSTNESS1_SHARED_INPUT_AUDIT. Note:
the inline lists "[3,23,45,...]" printed in those two documents' MD text
are transcription errors; their JSONs used exactly this canonical sample —
see PROTOCOL_LOCK_SAMPLE_INDICES_ERRATUM.md) — x 3 methods (no_adapter,
global_fixed_high, and global_fixed_low as the R0 anchor), run in TWO
independent processes:

- PASS-a: GFL anchor metrics bit-exact vs frozen R0 rows (excluding
  elapsed_seconds);
- PASS-b: input hashes identical across the 3 methods within each process;
- PASS-c: input hashes identical across the two processes.

If any gate fails: STOP. No formal rows may be produced until fixed.

## Frozen run matrix

| Block | Device | Methods | Rows |
|---|---|---|---|
| Formal | cuda:0 | no_adapter | 276 |
| Formal | cuda:1 | global_fixed_high | 276 |
| Preflight | either | no_adapter + global_fixed_high + global_fixed_low | 10 x 3 |

## Statistics plan (fixed before any Core-7 metric was seen)

Per (comparison, metric): paired object-level deltas over the 276 common
objects. Sign convention: raw delta = first-named condition minus second;
NO sign reversal; every metric is labelled with its direction
(higher-is-better for psnr/ssim/fscore/corr/entropy, lower-is-better for
lpips and the GT-relative texture errors). 95% percentile bootstrap,
10,000 resamples, seed 20260930, object as sampling unit; mean + median
delta, CI, win rate (ties counted as 0.5).

Primary pairwise family (fixed):
- layer_llh - no_adapter (Reviewer-1 "unmodified pipeline" gate)
- layer_llh - global_fixed_high (Reviewer-1 "competitive fixed baseline" gate)
- no_adapter - global_fixed_low (does the adapter help at all, same runner)
- global_fixed_high - global_fixed_low (fixed-scale direction, same runner)

Secondary (descriptive, same bootstrap): layer_llh vs each of the other
six conditions on the 7 core metrics (fg/full psnr/ssim/lpips + edge_ssim)
and the four GT-relative texture diagnostics.

GT-relative texture diagnostics (offline, from the per-object CSVs; same
definitions as the cross-backbone texture panel where applicable):

- grad_err   = abs(fg_grad_mag - gt_fg_grad_mag) / gt_fg_grad_mag
- lap_err    = abs(fg_lap_var - gt_fg_lap_var) / gt_fg_lap_var
- rgbstd_err = abs(fg_rgb_std - gt_fg_rgb_std) / gt_fg_rgb_std
- hf_err     = abs(fg_hf_energy - gt_fg_hf_energy) / gt_fg_hf_energy

Lower is better. Computed per object, then paired deltas.

Core-7 ranking table: all seven conditions sorted per metric on R0 rows
(5 frozen + 2 new); rankings reported, not graded.

## Output contract

All artifacts under
final/round2/coordination/core7_same_runner_completion_20261001/:
this PROTOCOL_LOCK, RUN_MANIFEST.json, preflight/ (logs + JSON),
formal_no_adapter/, formal_global_fixed_high/ (rows.json + per-method CSVs),
SHARED_INPUT_AUDIT_CORE7.{md,json}, per_object_metrics.csv (combined 552),
aggregate_metrics_core7.csv, paired_bootstrap_core7.json,
CORE7_SAME_RUNNER_REPORT.md, ARTIFACT_SHA256SUMS.txt.
Existing frozen outputs are read-only.

## Status

- [x] Protocol frozen before any no_adapter / fixed_high observation
- [x] Preflight gate: PASS-a GFL anchor bit-exact vs frozen R0 (0 mismatches); PASS-b cross-method 0; PASS-c cross-process 0 + cross-pass metrics identical (preflight/pass1, pass2)
- [x] Formal 276 x 2 = 552/552 (in-run integrity 0 aborts)
- [x] Shared-input audit: 0 cross-process mismatches / 276 objects
- [x] Analysis + report (aggregate_metrics_core7.csv, paired_bootstrap_core7.json, CORE7_SAME_RUNNER_REPORT.md)
