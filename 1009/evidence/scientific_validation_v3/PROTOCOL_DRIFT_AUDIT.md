# PROTOCOL_DRIFT_AUDIT — protocol freeze chronology, engineering-fix semantics, post-fix drift (2026-10-05)

## 1. Protocol-freeze chronology (git `log --follow`, all times UTC)

| File | First commit | Time | Modified after? | Verdict |
|---|---|---|---|---|
| MASTER_PROTOCOL_LOCK.md | d41f1c4 | 10-02 10:27 | never | protocol predates all outcomes (first formal data 16:32) |
| CLAIM_TEST_MATRIX.md | d41f1c4 | 10-02 10:27 | never | all claims PENDING at freeze; never edited post hoc |
| RUN_BUDGET.md | d41f1c4 | 10-02 10:27 | never | — |
| COHORT_FREEZE.md | d41f1c4→c1fb1b7→ac62fbe | 10:27→10:59→15:50 | only pipeline then freeze | 300-object freeze at 15:50, before A2 formal data (16:32) |
| PRIMARY_HYPOTHESES.md | c1fb1b7 | 10-02 10:59 | never | — |
| a3_normalization.json | a8fd82d | 10-02 11:32 | never | A3 high values frozen ~47 h before A3 results (10-04 10:50) |
| fresh_confirm_300.txt | c1fb1b7→ac62fbe | 10:59→15:50 | never after freeze | — |
| stratification/visualization_24 | ef1fb10 | 10-02 16:49 | never | GT-only, before A2 analysis (10-03 01:22) |

A3 normalization was estimated on the probe-24 dev baseline (mtime 11:28) with
`frozen_before_fresh_evaluation: true`; A2 analysis commits (086744b 10-03 01:22, 5baeedb
02:01) all postdate the protocol commits. Visualization-24 was selected at 16:49 on 10-02,
before any A2 outcome existed, from GT-only inputs. **No scientific parameter changed after
result inspection. Table of semantic changes: none found (every protocol file is
write-once).**

## 2. Engineering-fix semantics classification

| Fix | Commit(s) | Timing vs A2 formal (16:32→19:27 10-02) | Alters inputs/seeds/schedule/metrics? | Class |
|---|---|---|---|---|
| A. OpenMP/thread limit (MVP_NUM_THREADS=6) | 57bac28 | at run start | no — execution only | SEMANTICS_PRESERVING |
| B. MVP_DATA_ROOT override → fresh renders | 57bac28 (run_campaigns) ; a4c493f (texture tool) | run start | data source (by design, uniform across all conditions, hashes recorded) | SEMANTICS_PRESERVING (defines the cohort inputs; not a within-campaign change) |
| C. global_embeds precompute (506/507 objects) | 57bac28 | run start | deterministic cache replaces in-run compute; hash-checked in integrity guard | SEMANTICS_PRESERVING |
| D. CSV batched write (every 16 completions) | 5359dd7 | mid-run | no — storage only; ledger written per-row atomically | SEMANTICS_PRESERVING |
| E. ledger-first CSV rebuild | 5359dd7 ; 7e3a8d4 (B3 dedup) | mid-run / before B3 report | analysis plumbing only | SEMANTICS_PRESERVING |
| F. depth conversion (EXR→uint16) | c1fb1b7 | before A2 formal | preprocessing, uniform, logged (`depth_convert_log.json`), applied before any formal row | SEMANTICS_PRESERVING |
| G. GT/mask cache (`mask_gt_cache/`) | a4c493f | after A2 | **zero references** from the v3 runner/metric path (grep-verified) — vestigial, not in the loop | SEMANTICS_PRESERVING (no-op) |
| H. stdout suppression | a4c493f | after A2 | analysis-script print wrapping only; v3 runner unaffected | SEMANTICS_PRESERVING |

No fix is SEMANTICS_CHANGING; none is UNKNOWN. No UNKNOWN touches completed A2/A3 rows.

## 3. Post-fix protocol-drift check (empirical)

Requirement: reproduce pre-fix rows with the current runner and compare. Performed
2026-10-05 (scratch RUN_DIR; formal artifacts untouched):

- A2 baseline vs A3 `a3_baseline` (run 10-02 vs 10-03, different processes, after fixes B-H):
  **300/300 objects bit-identical on every metric field** (only the `uncapped` registration
  flag differs, which cannot act on a no-intervention baseline). This alone demonstrates the
  fix regimes produce identical outputs.
- Fresh live reproduction (current runner, all fixes active): 3 objects × 3 conditions →
  9/9 rows bit-identical to the 10-02 formal rows, **9/9 PNGs byte-identical**.
- B3's interrupted pass vs its resume rerun (different shards/processes): 1050/1050 duplicate
  pairs bit-identical.

**Implementation regimes: one.** No pooling hazard exists; nothing needs regime tagging.

## 4. Verdict

PROTOCOL_DRIFT: **PASS.** Freeze chronology is clean (write-once protocols, frozen before
outcomes), all engineering fixes are semantics-preserving, and empirical reproduction proves
bit-level invariance across regimes.
