# Merge conflict and resolution report

Conflict totals below count only conflicts created by an actual Git merge or cherry-pick attempt. A pre-merge source difference is not reported as a resolved conflict.

## codex/cg-01549-surgical-revision-20261008

- Merge strategy decision: full-history merge rejected at preflight because the branch contributes 165 unique commits, 24,820 unique blobs, about 3.63 GB uncompressed objects, and a 34,797-path tree delta with historical/generated outputs.
- Git merge attempted: no.
- Code conflict: NO_CONFLICT (no merge executed; no conflict was generated).
- Paper conflict: NO_CONFLICT (no paper merge executed; no conflict was generated).
- Candidate source differences reviewed: historical 01549/1008 manuscript, Supplement, response, figures and package outputs differ from current main. The candidate TeX was not applied because current main has the later evidence-bounded 1008 content and matching package source.
- Source-ready review commit deac8925d3bde92bae9ccb5d3ad92ea79ed69eae contained only the review-round mapping. Its content was byte-identical to the existing main file, so cherry-pick was skipped as empty. No conflict was resolved or hidden.
- Actual conflicts resolved: 0.



## codex/cg-01549-unified-20261009

- Merge strategy decision: full-history merge rejected at preflight (166 unique commits, 23,948 unique blobs, 3,035,104,087 uncompressed bytes, 24 blobs >= 5 MiB, and a 27,292-path tree delta with historical/generated outputs).
- Git merge or cherry-pick attempted: no.
- Code conflict: `NO_CONFLICT` (no merge executed; no conflict was created).
- Paper conflict: `NO_CONFLICT` (the dirty branch worktree's manuscript and response wording was compared against current main; no merge was executed).
- Candidate TeX/response changes were reviewed. Current main already discloses that Fresh C's controlled-retraining checkpoint is not established as the historical 01549 main-table artifact, and preserves the bounded C3 result and counter-results. No candidate text was adopted.
- Thirteen of the 25 `1009/unification/` files are byte-identical at the same path in main; one additional frozen analysis script is byte-identical at its current main path. The other eleven files describe superseded repository/worktree/ref state and were excluded from current authority.
- Actual conflicts resolved: 0.


## codex/cg-round2-1008-revision-20261008

- Merge strategy decision: full-history merge rejected (142 unique commits, 23,767 unique blobs, 2,889,656,077 uncompressed blob bytes; 16 blobs >= 5 MiB; 27,178-path delta includes extensive outputs and deletes current main's active 1008 files).
- Git merge/cherry-pick attempted: no. The C3−GFH source audit was selectively added at a new path in commit `dc6f43ae522e230f368232b9dfba393daf724c43`.
- Code conflict: `NO_CONFLICT` (no source-code merge was attempted).
- Paper conflict: `NO_CONFLICT` (no manuscript merge was attempted; the active manuscript was not changed).
- Scientific-output discrepancy: the independently rerun 10,000-resample seed-20261002 audit gives Edge-SSIM CI `[-0.020803,-0.016790]`; the active manuscript uses `[-0.02084,-0.01683]`. The paired source, point estimate, and direction match; both intervals are wholly negative. This is recorded as a resampling-output provenance difference, not resolved by substituting one set of values. The active table's exact bootstrap output should be verified before later prose changes.
- The existing paper-branch candidate removes current-main 1008 source/package paths in its WIP tree; those deletions were not applied. Its untracked internal N20 candidate image was left in its original worktree.
- Actual Git conflicts resolved: 0.
