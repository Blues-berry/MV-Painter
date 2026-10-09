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
