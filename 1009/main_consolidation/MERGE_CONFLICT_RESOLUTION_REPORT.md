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

## codex/paper-1006-20261006

- Merge strategy decision: full-history merge rejected (144 unique commits, 2,667 unique blobs, 875,932,057 uncompressed bytes; 22 blobs >= 5 MiB; 3,328-path delta includes old submission outputs and generated material).
- Git merge or cherry-pick attempted: no. E6 audit files were added at a new path in main commit `57f316719a5c56c61d0e0fa4fc1e4c7173a94c43`; a reviewed startup-only script fix was committed as `b1ac2f7d353b4362a040037257a51b9bedf40ed8`.
- Code difference reviewed: archived `model_unet_geotex.py` uses a class-level `_skip_correction`; the paired pipeline does not restore prior state in `finally`. Current main uses per-instance values and exception-safe restoration. The old behavior was excluded due to cross-wrapper state sharing and exception-leak risk. The separate `geotex/eval_exploration.py` path/CUDA/import changes were selectively integrated and smoke-checked.
- Code conflict: `NO_CONFLICT` (no Git merge was attempted; the source difference above was audited, not mechanically conflict-resolved).
- Paper conflict: `NO_CONFLICT` (old manuscript/supplement candidates were not applied; active 1008 sources remain unchanged).
- Scientific difference: 1006's 10/06 readiness and narrative documents are earlier snapshots. Its bounded schedule, dose, CAI, strict-276, N=20 GLB, and open human-fidelity conclusions agree with the later 1008 source/claim ledger; its “Fresh C not yet confirmed” status predates the completed 300-object run. E6 was a stopped development candidate, not independent confirmation; only its explicit diagnostic and stop review were selected.
- Actual Git conflicts resolved: 0.

## codex/cg-ltcas-narrative-convergence-20261007

- Merge strategy decision: full-history merge rejected (142 unique commits, 2,429 unique blobs, 776,750,834 uncompressed bytes; 15 blobs >= 5 MiB; 3,160-path delta; WIP tree deletes current 1008/1009 content).
- Git merge or cherry-pick attempted: no. A compact 42-row numerical authority reaggregation and the sanitized human-data publication disposition were selectively added in commit `174431225cc5247170c35fec25bd39ef6649fc2e`; no candidate manuscript/package was overlaid.
- Code difference reviewed: old class-level `_skip_correction` and no-`finally` restoration were rejected; current main's instance-level state restoration remains. The branch's `.gitignore`/`.gitattributes` changes would remove current artifact/binary-diff controls and were rejected.
- Code conflict: `NO_CONFLICT` (no Git merge was attempted; source differences were audited, not mechanically resolved).
- Paper conflict: `NO_CONFLICT` (10/07 candidate removes FAC, while active 1008 keeps only its bounded historical disposition; candidate final_0903 manuscript and PDFs were not merged).
- Scientific-output note: the 42-row verifier passed on exact hash-pinned inputs. Its output is a historical authority reaggregation and does not replace active 1008 values; the previously recorded C3−GFH bootstrap-interval provenance difference remains explicit.
- Actual Git conflicts resolved: 0.

## codex/scientific-validation-v3-20261002

- Full-history merge was rejected before execution: 163 source-unique commits, 36,865 blobs, 7,776,031,685 uncompressed bytes, and a 42,729-path tree delta; its tree deletes the active 1008 files and compact V3 release.
- No Git merge or cherry-pick was attempted. The bounded E1/E2 and MVDiffusion evidence selection was committed at `73e5b91c`; the old 0907 deletions and readiness-note edits were captured separately in local WIP ref `23ba46e35ec9465d737b1d2e61116b9904bb9d4c`.
- Code conflict: `NO_CONFLICT`. No application code behavior was changed; included analysis scripts remain report-scoped.
- Paper conflict: `NO_CONFLICT`. The active 1008 text and package were not overlaid. The later human-study summary remains pending its dedicated branch audit.
- Actual Git conflicts resolved: 0.
