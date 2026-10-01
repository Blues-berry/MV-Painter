# Archived LHL Provenance Audit (final_audit_20261001, Phase 1.1)

Audit date: 2026-10-01. Subject: the archived "official layer-LHL" strict-276 record
(FG-PSNR mean 14.7763), rescued from `/4T/tmp/mvpainter-recovery-HLzm9O/` into
`rescued_tmp_20261001/official_lhl_v2_merged/` and `official_lhl_v2_split/`.
Method: every claim below is derived from rescued artifacts, recorded hashes, on-disk
file timestamps, and recomputation from the rescued CSVs. No mechanism is asserted where
the artifacts cannot prove one.

## 1. What the record claims about itself

From `handoff_verification.json` (status PASS) and `official_comparisons.json`:

| Field | Value |
|---|---|
| Checkpoint | `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`, SHA `0618d6b2…` (verified identical to the frozen confirmation checkpoint this audit) |
| Object list | `strict_holdout_objects_276_clean_v2.txt`, SHA `a6aa8ab6…` (identical to frozen) |
| Seed / steps / views | seed 42, 50 steps, `unique6`, target views [0,15,12,16,13,14] |
| Layer schedule | deep [1.25, 2.50, 1.25], middle [1.25, 2.50, 1.25], shallow [0.50, 0.75, 0.50] |
| Row counts | head_raw 138 + tail_raw 138 = merged 276, all `layer_LHL` |
| Recorded source SHAs | `geotex_explore_contradiction` = `5da7fff2…`, `geotex_eval_exploration` = `adb31747…`, `model_unet_geotex` = `b6464225…` |

## 2. Source-code identity vs the current tree

All three recorded source files hash-identical to the current working tree:

| Recorded | Current file | Match |
|---|---|---|
| `5da7fff2…` | `geotex/explore_contradiction.py` | identical |
| `adb31747…` | `geotex/eval_exploration.py` | identical |
| `b6464225…` | `MVPainter/mvpainter/model_unet_geotex.py` | identical |

The evaluation kernel and generation path are therefore code-identical to the frozen
protocol. The data module (`MVPainter/src/data/mvpainter_dataset.py`) was NOT hashed in
the archived record.

## 3. Execution structure (reconstructed from timestamps)

On 2026-09-29 the recovery directory shows: v1 run `layer_official/rows.json` 12:36:04,
merged 12:41:45; runner `run_layer_official.py` last modified 12:44:09; v2 head CSV
finished 12:59:12 and v2 tail CSV finished 12:59:28 — i.e. the v2 record is a merge of
two concurrent single-GPU processes (head = objects obj_0024–0161, tail = obj_0162–0299),
16 seconds apart. The dataset commit `78c871f` (target-view change `7→16` and
`target_view_mode` parameter, both required by the runner's `unique6` setting) was
committed at 15:45 the same day, AFTER these runs — so the archived run used a same-day
working-tree state that git cannot reconstruct beyond the later commit.

## 4. Internal consistency of the record

Recomputed from the rescued merged CSV:

| Block | n | FG-PSNR mean | vs frozen confirmation LHL (same objects) | fg_lap_var (gen) vs confirm | fg_rgb_std (gen) vs confirm |
|---|---|---:|---:|---:|---:|
| head (0–137) | 138 | 16.5593 | **+3.2252** (confirm 13.3341), r=0.62 | 0.00303 vs 0.00987 (3.3× lower) | 0.0264 vs 0.0743 (2.8× lower) |
| tail (138–275) | 138 | 12.9933 | **+0.3787** (confirm 12.6146), r=0.79 | 0.00490 vs 0.01052 (2.1× lower) | 0.0376 vs 0.0807 (2.1× lower) |
| merged | 276 | 14.7763 | +1.8020 (confirm 12.9743), r=0.66 | — | — |

Per-object examples (head block): obj_0024 20.299 vs 13.141 (+7.16 dB), obj_0025 17.594
vs 9.814 (+7.78 dB).

## 5. What the record rules out

1. **Targets / masks / view order**: GT-side statistics (`gt_fg_rgb_std`,
   `gt_fg_lap_var`, `gt_fg_grad_mag`) are bitwise identical between the archived record
   and the frozen confirmation for every object sampled (obj_0024, 0025, 0100, 0200).
   The target branch of the data path was identical.
2. **Evaluation-kernel code drift**: SHA-identical (Section 2).
3. **Checkpoint / object list**: SHA-identical (Section 1).
4. **Reference-preprocessing randomness as the cause of the mean gap**: the R0/R1
   robustness pair (276×5 schedules, seeds 42+idx vs 10042+idx) changes every stretch
   realization and moves absolute schedule means by only ≈0.03 dB (LHL 12.9743 R0 vs
   12.9456 R1) while leaving all paired deltas stable. Realization lottery is
   mean-neutral and cannot produce +1.8 dB (let alone the +3.23 dB head block).

## 6. What the record cannot establish

- Why the head process produced systematically smoother generations (3.3× lower
  Laplacian variance) and +3.23 dB higher FG-PSNR than the frozen protocol on the same
  objects, and why the tail process differs by a smaller but same-signed amount.
- The exact data-path and runner working-tree state at run time (same-day unrecorded
  modifications; the only surviving runner copy is the 12:44 version; no per-object
  realization, scale, or residual log was persisted — `residual_log` was created and
  discarded per object).

## 7. Ruling

Forensic facts 5.1–5.4 exclude targets, metrics code, checkpoint, cohort, and
realization randomness as explanations for the discrepancy; Section 6 shows the
remaining causes are unreconstructible from any surviving artifact. This record is
therefore handled under **Case B** of the audit plan — see
`historical_result_exclusion_reason.md`. The frozen same-runner layer-LHL replica
(rescued, mean 12.9743, seeded `object_seed=42+idx`) is the only admissible layer-LHL
reference for quantitative claims. Note this refines, without weakening, the earlier
EVAL_AUGMENTATION_AUDIT wording: unseeded realization explains cross-restart
irreproducibility (r=0.66 scatter), not the mean-level gap.

## 8. Update (2026-10-01 evidence convergence): stage-2 discriminating run EXECUTED

The parallel task's stage-2 GPU experiment (defined as optional here) has since been
executed and committed at `75a4068`
(`core7_same_runner_completion_20261001/lhl_forensics/stage2_regen.json`, `stage2.log`,
12 stratified objects; full write-up in
`core7_same_runner_completion_20261001/ARCHIVED_LHL_PROVENANCE_AUDIT.md` §B.3):

1. aug-ON regeneration reproduces the frozen seeded rows **bit-exactly** (+0.000 dB on
   all 12 objects) — independent re-validation of the frozen protocol's determinism.
2. aug-OFF regeneration still misses the archived record by −2.57 dB overall and
   **−6.96 dB on the hexuid group** (aug-ON: −6.94 dB) — disabling the cond
   augmentation moves results by only −0.02 to −0.16 dB.

Consequence: the "cond-augmentation path state" hypothesis is **experimentally
refuted**, joining the excluded causes in §5. The Case-B ruling and the exclusion are
**unchanged and strengthened**: both plausible benign explanations are now excluded by
direct experiment, and the root cause remains bounded to an unreconstructible
runner-time code state. No further mechanism experiment is anticipated.
