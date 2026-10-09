# Selected evidence from `codex/final-evidence-freeze-20261001`

Source HEAD: `29b3a0a6ec00f5848f1898ffda4fb8e787f81375` (local archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/final-evidence-freeze-20261001`).

## Why this subset is retained

The current 1008 Supplement describes a retrospective strict-276 Core-7 table and cites a separate paired-statistics file. The aggregate table and C3/GFH calculation were already in main, but the cited paired table, its row audit, and several source-condition rows were missing. This package restores only the compact metric rows and protocols needed to reproduce that evidence. It does not adopt the branch's old manuscript, release verdict, broader narrative, or stale repository state.

## Contents and reproduction

- `inputs/`: seven 276-row per-object metric CSVs, their seven protocol manifests, and the prior 56-row paired-bootstrap table used for cross-checking.
- `scripts/final_core7_forensic_stats_20261001.py`: byte-preserved source analysis script.
- `scripts/reproduce_core7.py`: stages those small inputs into a temporary legacy path layout, runs the original script, and compares all three generated outputs byte-for-byte with the canonical files under `1008/audits/source_evidence/r2/core7/`. Run with `python 1009/evidence/branch_audits/final_evidence_freeze_20261001/scripts/reproduce_core7.py`.
- Canonical outputs: `1008/audits/source_evidence/r2/core7/CORE7_FINAL_AGGREGATES.csv` (already present and unchanged), `CORE7_FINAL_PAIRED_STATISTICS.csv`, `CORE7_ROW_AUDIT.json`, and the input table `PAIRED_BOOTSTRAP_CORE7.csv`.
- `1008/audits/source_evidence/r2/core7/recompute_core7_c3_gfl.py` and `CORE7_C3_GFL_RECALCULATED.csv` independently reproduce the Supplement's post-hoc C3−GFL row, which is not one of the prior table's saved comparisons.

## Validation and limits

The original CPU script verified 1,932 rows (276 objects × 7 conditions), exact object-index coverage and labels, finite metrics, and identical serialized GT descriptor columns. It regenerated `CORE7_FINAL_AGGREGATES.csv`, the 49-row `CORE7_FINAL_PAIRED_STATISTICS.csv`, and `CORE7_ROW_AUDIT.json` byte-for-byte. Its comparison with the prior bootstrap table matched 42 of 56 pair/metric rows with no mismatches. The current Supplement's seven condition means, LLH−GFH FG-PSNR (+0.822292 dB, 95% CI [0.616795, 1.033035], 148/276), LLH−C3 FG-PSNR (+2.036527 dB, [1.806804, 2.260756], 227/276), and post-hoc C3−GFL FG-PSNR (+1.207771 dB, [1.116967, 1.294989], 259/276) were checked against these rows. The existing C3−GFH calculation also matches its two published table rows.

These are retrospective diagnostics on the clean-v2 276-object cohort, not an independent replication of Fresh C or the original 01549 estimate. The seven conditions do not establish one common runner or complete shared tensor inputs; five older Core-5 conditions lack per-object input-tensor hashes. Keep the current Supplement's non-confirmatory, post-hoc limits. This package contains no images, GLBs, checkpoints, render outputs, or participant-level human responses, and required no model inference or GPU work.

All old `final/` manuscript candidates, generated figure pools, GLBs, logs, caches, and the source branch's deletion of current 1008/1009 files remain excluded.
