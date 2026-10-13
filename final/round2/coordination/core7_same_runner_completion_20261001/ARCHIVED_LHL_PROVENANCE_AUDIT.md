# FORENSIC AUDIT — Archived layer-LHL strict-276 record (14.78 dB): root-cause investigation and quarantine upgrade (2026-10-01)

Trigger: external review. The previous explanation for the archived-LHL vs
seeded-replica gap (archived FG-PSNR 14.78 vs 12.97 seeded, r = 0.66) was
"unseeded reference preprocessing realization". The new Robustness-1
evidence (R0 vs R1: realizations shift means by only 0.03-0.04 dB,
per-object r = 0.996) refutes that explanation: preprocessing randomness
CANNOT produce a 1.8 dB gap. This audit therefore (A) reconstructs the
archived record's provenance by file/code forensics, (B) decomposes the
gap with the archived predictions that survive on disk, and (C) upgrades
the quarantine wording accordingly.

## A. Provenance reconstruction (what can and cannot be established)

### A.1 What the archived record is

- Location: /4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/
  - layer_official/            (v1 partial run, 141 rows, idx 0-140, CSV mtime 09-29 12:36)
  - layer_official_v2_head/    (138 rows, idx 0-137)
  - layer_official_v2_tail/    (138 rows, idx 138-275)
  - layer_official_v2_merged/  (276 rows; OFFICIAL_LAYER_LHL_REPORT.md,
    official_comparisons.json; CSV/report mtimes 09-29 12:59-13:00)
- Runner script (on disk, outside the repo): run_layer_official.py —
  same CONFIG / CHECKPOINT / OBJECT_LIST / latent protocol / metric path
  (ee.compute_metrics) / data_utils collate path as the later frozen
  runner; seeding policy differs (see A.3). Head+tail ran as two PARALLEL
  processes, both pinned to cuda:0 (CSV mtimes 12:59:12 and 12:59:28).
- v1 vs v2 on 141 shared objects: mean|diff| 0.044 dB, max 0.52 dB,
  r = 0.9999 -> the archived protocol was internally STABLE across
  processes; it is not run-to-run chaos.

### A.2 Data and config state: UNCHANGED since before the archived run

- clean_holdout.yaml mtime 09-29 11:08 (< 12:36); object list 09-28 16:35;
  checkpoint 09-28 12:53.
- rendered_full/{uid}/ under data/train_data: image/, depth/, normal/,
  camera/, embeddings/, meta.npy ALL mtimes 06-01..06-09 — every modality
  of every holdout object is byte-state unchanged since June. The
  "different data state" hypothesis is refuted for the rendered inputs.

### A.3 Code state: PARTIALLY UNVERIFIABLE (the provenance hole)

- The repo had NO commits between 09-08 and 09-29 15:45 (78c871f), yet the
  archived runner sets validation.params.target_view_mode='unique6' — a
  dataset parameter that exists only in the 78c871f dataset code. The
  archived run therefore executed an UNCOMMITTED working tree.
- No snapshot, diff, or hash of the working tree at 09-29 12:36-12:59
  exists. Any transient edit between 12:36 and 15:45 (commit time) is
  UNFALSIFIABLE from git. This is the decisive provenance gap.
- The GT protocol of the archived run, however, IS verifiable from its own
  artifacts: the archived GT PNG (predictions/ground_truth/obj_0024.png)
  matches the CURRENT unique6 GT tile-by-tile (mean|diff| 1.6e-4 = PNG
  quantization) and does NOT match the legacy duplicate-top protocol
  (max|diff| 0.77). Archived GT statistics columns (gt_fg_*, crop_area)
  are BIT-IDENTICAL to the seeded replica's rows on all 276 objects.

### A.4 Metric path: verified consistent

Recomputing ee.compute_metrics from the archived PREDICTION PNGs (which
survive for all 276 objects: head/tail predictions/layer_LHL/) against the
current GT/mask/edge path reproduces the archived rows to +/-0.011 dB
(PNG quantization) on a 12-object stratified sample
(lhl_forensics/stage1_recompute.json). The archived rows are
metric-consistent with the current protocol; the gap is 100% in the
PREDICTED PIXELS, not in GT, masks, or metric implementation.

## B. Gap decomposition

### B.1 The "position-dependent drift" is a binning artifact

Windowed (archived - seeded) deltas decay +5.6 -> 0 over idx 0-140, but
object SOURCE GROUPS are ordered along the index (hex-UID assets first,
abo/objaverse later). Group-wise:

| source group | n | idx range | drift mean | sd |
|---|---|---|---|---|
| hex-UID      | 90 | 0-159 | **+4.94 dB** | 2.83 |
| abo          | 76 | 89-273 | +0.15 dB | 1.55 |
| objaverse    | 100 | 150-275 | +0.43 dB | 1.60 |
| other        | 10 | 149-272 | -0.11 dB | 0.63 |

Within hex-UID the drift stays large in both halves (+5.51 / +4.36); the
apparent smooth decay is the group interleaving. corr(drift, gt_grad_mag)
= -0.47; corr(drift, crop_area) = +0.01.

### B.2 Candidate mechanisms and their status

| candidate | status |
|---|---|
| reference-preprocessing realization randomness | REFUTED by R0/R1 (0.03-0.04 dB) |
| different GT / views / masks | REFUTED (A.3, A.4: GT bit-identical, unique6 confirmed) |
| metric implementation drift | REFUTED (A.4: archived rows reproduced by current metric path) |
| different data files | REFUTED (A.2: all input mtimes predate the run; June state) |
| GPU nondeterminism | INSUFFICIENT (v1-v2 diff 0.044 dB mean) |
| uncommitted code-state difference affecting generation (e.g. cond-augmentation path active/inactive, or another transient edit between 12:36 and 15:45) | CONSISTENT with all evidence and UNFALSIFIABLE from git; discriminating experiment defined in B.3 |
| schedule/checkpoint difference | REFUTED (same LHL schedule function, same checkpoint file, SHA unchanged) |

### B.3 Discriminating experiment (stage 2; GPU) — EXECUTED 2026-10-01

scripts/forensic_lhl_drift_20261001.py --regen regenerated the 12 stratified
objects under (a) the frozen seeded protocol with schedule layer_lhl, and
(b) the same protocol with the cond augmentation path disabled
(random_stretch_or_compress and random_resize replaced by identity on the
runtime dataset module). Artifacts: lhl_forensics/stage2_regen.json,
stage2.log, pred_aug{ON,OFF}_obj_*.png.

Results (FG-PSNR, dB):

1. augON regen reproduces the frozen seeded rows BIT-EXACT
   (regen - seeded = +0.000 on all 12 objects) — independent re-validation
   of the seeded protocol's determinism.
2. augOFF does NOT reproduce the archived record: mean regen - archived =
   -2.57 dB overall and -6.96 dB on the hexuid group (vs -6.94 dB with
   augmentation ON). Disabling the cond augmentation moves hexuid results
   by only -0.02 to -0.16 dB.
3. Therefore the "cond-augmentation path state" hypothesis is REFUTED, on
   top of the earlier refutations (preprocessing randomness, GT/mask/metric
   drift, data-file drift). The archived record was generated under a
   THIRD, unidentifiable runner-time code state; with no commits between
   09-08 and 09-29 15:45 and no working-tree snapshot, that state is not
   recoverable from git.

Conclusion of B: the root cause is bounded to an unidentifiable transient
code/state difference at archived-run time. Both plausible benign
explanations (augmentation randomness, augmentation disabled/enabled) are
now experimentally EXCLUDED. This strengthens, not weakens, the quarantine.

## C. Quarantine upgrade (decision)

The archived record's earlier framing — "did not seed the Python RNG, so
its reference draws were irreproducible" — is no longer defensible as the
gap explanation, and the record cannot be assigned a complete reproducible
provenance (uncommitted working tree, A.3). DECISION, independent of the
stage-2 outcome:

1. The archived layer-LHL record (and its companion conditions in
   layer_official_v2_merged) is EXCLUDED from all quantitative claims,
   comparisons, and tables — already the de-facto state since the 0930
   freeze; this audit makes it the permanent, stated state.
2. Correct mechanism wording for any future text:
   "This historical record cannot be assigned a complete reproducible
   provenance: it was produced by an uncommitted, unrecoverable runner-time
   code state (its discrepancy is generator-side and concentrated in one
   asset source group; preprocessing randomness, the cond-augmentation
   path, GT/mask/metric drift, and data-file drift are each experimentally
   excluded). It is excluded from all quantitative claims. All current
   evidence comes from seeded, same-runner, provenance-hashed records."
   The old wording must NOT attribute the gap to augmentation randomness
   (contradicted by Robustness-1) nor leave "unseeded realization" as the
   standalone cause (contradicted by stage 2 of this audit).
3. No paper/supplementary/letter text is edited in this task; the wording
   above is recorded here for the next paper-edit window.

## Artifacts

- lhl_forensics/stage1_recompute.json (CPU recomputation, 12 objects)
- v1/v2/merged CSVs, predictions, manifests under
  /4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/ (read-only)
