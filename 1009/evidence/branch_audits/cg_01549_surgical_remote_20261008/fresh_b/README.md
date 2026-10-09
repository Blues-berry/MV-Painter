# Fresh B selected evidence from the private remote surgical-revision snapshot

Source archive HEAD: `dad08320625431acf439ed5bfb86c6a9252353a4` (`refs/archive/codex/main-unification-20261009/mvpainter/heads/codex/cg-01549-surgical-revision-20261008`). The clean source worktree was detached at this SHA. The local same-named branch is a different HEAD (`06cac81de23988aba94b5d7bfeaca93f6785f370`) and is audited separately in the sequential report.

This compact package closes a specific evidence gap for results already summarized in the active 1008 Supplement and current evidence reports. It contains the A3b per-object intervention rows, the corresponding per-object dose rows, and the eight post-lock generic-schedule rows plus their saved analyses and protocol/gate records.

## Scope and reuse

- `A3B_PER_OBJECT_METRICS.csv`: 2,250 rows, 15 layer/window conditions × 150 objects. The `a3_baseline` comparator is reused from `1009/evidence/scientific_validation_v3/reproducibility_release/data/campaign_B/a3_baseline_per_object_metrics.csv`; every field and UID matched the source combined ledger exactly.
- `A3B_DOSE_OBJECT_CELL_DATA.csv`: 2,250 rows for the same A3b conditions; supports the reported lack of three-layer dose common support.
- `FRESH_CONFIRM_B_GENERIC_EXTENSION_PER_OBJECT_METRICS.csv`: 1,200 rows, eight generic schedules × 150 objects. The `layer_llh` comparator is reused from the existing main release, with exact field/value equality to the source combined ledger.
- The existing `1008/audits/source_evidence/r2/fresh_b/a3b_texture_extension_per_object.csv` is byte-identical to the source texture-extension table, so it was not duplicated here.
- The saved A3b and generic-extension JSON outputs are preserved exactly. Their current bounded/post-lock interpretation remains in `1009/evidence/scientific_validation_v3/A3B_BOUNDED_LAYER_TIME_REPORT.md` and `FINAL_GENERIC_SCHEDULE_COMPARISON.md`.

## Scientific limits

A3b is a bounded intervention map. Its frozen residual-only calibration missed the ±20% balance target (deep −20.01%, middle −20.20%, shallow +98.98%); the A3b result is not equal-dose or dose-normalized. The generic extension reuses the already-open Fresh B cohort and is explicitly post-lock sensitivity evidence, not independent confirmation. Its early row exposure and stopped duplicate launch are preserved in the included note. Fresh C remains the separate independent comparison.

The lock text records a pre-output freeze for A3b and for the cap/budget campaign. Git first records those lock files in source commit `12da08c7056f5f0c36677668d640477bfb249454` (2026-10-06 00:52 UTC); the compact Fresh B metrics and A3b/generic analysis outputs were added to the source archive in `20dff3e7` (2026-10-07 13:58 UTC). This repository chronology supports the recorded sequence but cannot independently prove events outside Git.

## Validation performed

- Source combined ledger: 4,500 unique object-condition rows, 30 conditions, 150 UIDs; the extracted A3b and generic subsets each have complete 150-object coverage and finite FG-PSNR/FG-LPIPS values.
- Existing main `a3_baseline` and `layer_llh` rows match the combined source ledger field-for-field.
- Reaggregated all 30 primary mean contrasts from the selected rows and reused baselines; maximum absolute difference from the saved JSON means: `2.61e-16`.
- The saved A3b interaction summaries match the current Supplement: FG-LPIPS `W=225.015`, Holm `p=5.37e-43`; FG-PSNR `W=525.700`, Holm `p=3.43e-107`.

No predictions, render images, GLBs, checkpoints, caches, residual logs, or historical manuscript/PDF files were copied. The remaining branch history is still recoverable through the local archive references.
