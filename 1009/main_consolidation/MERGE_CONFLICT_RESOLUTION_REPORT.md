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


## codex/human-confirmatory-analysis-20261007

- Pre-merge outcome: `FULL_MERGE_REJECTED` before running a merge. The 3,646-path source tree deletes 253 current 1008 paths and 334 current 1009 paths, and adds 1,854 legacy `final/` plus 482 old `1006/` paths; 145 source-unique commits include 904,462,082 uncompressed blob bytes. No merge trial or cherry-pick was run.
- Actual Git conflict files: `NO_CONFLICT` (0). No claim is made that merge conflicts were resolved.
- Reviewed code differences, excluded before merge: source `GeoTexResnetWrapper._skip_correction` is class-level rather than per instance; its pipeline sets and clears the shared state without `try/finally`. Main's per-instance isolation and exception restoration remain. Source `.gitignore` drops precise current evidence/generated-output rules and reopens old `final/` content. These are unsafe source differences, not Git conflicts.
- No manuscript or response conflict was created: legacy `final/` candidates and the source tree's active 1008 deletions were not merged. The human endpoint results were selected as a separate aggregate-only evidence package; original response, assignment, object-map, pair-map, and private-key files were excluded. Source paths and file-level disposition are recorded in the sequential report and human-audit README.


## codex/round2-final-forensic-audit-20261001

- Source HEAD: `450389fb8232c0f03db0b79f21bdc998043a99e0`; archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/round2-final-forensic-audit-20261001`; merge-base: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`.
- `NO_CONFLICT`: no full merge, cherry-pick, or paper-file merge was attempted. The source tree's old `final_round2.tex` and related manuscript artifacts were reviewed against active 1008 but not applied. Differences in old statistics and wording were adjudicated as historical scope and evidence questions, not Git conflicts.
- No code or paper conflict was created or resolved. The archived R0 per-object delta CSV matches existing main inputs for 276 objects and 2,760 numeric cells exactly; the source's approximate budget decomposition was excluded because its contrasts do not isolate a pure allocation effect. Active manuscript and submission hashes remain unchanged; 48/48 package checks pass.
- Actual Git conflicts resolved for this branch: 0.

## codex/paper-1006-20261006

- Merge strategy decision: full-history merge rejected (144 unique commits, 2,667 unique blobs, 875,932,057 uncompressed bytes; 22 blobs >= 5 MiB; 3,328-path delta includes old submission outputs and generated material).
- Git merge or cherry-pick attempted: no. E6 audit files were added at a new path in main commit `57f316719a5c56c61d0e0fa4fc1e4c7173a94c43`; a reviewed startup-only script fix was committed as `b1ac2f7d353b4362a040037257a51b9bedf40ed8`.
- Code difference reviewed: archived `model_unet_geotex.py` uses a class-level `_skip_correction`; the paired pipeline does not restore prior state in `finally`. Current main uses per-instance values and exception-safe restoration. The old behavior was excluded due to cross-wrapper state sharing and exception-leak risk. The separate `geotex/eval_exploration.py` path/CUDA/import changes were selectively integrated and smoke-checked.
- Code conflict: `NO_CONFLICT` (no Git merge was attempted; the source difference above was audited, not mechanically conflict-resolved).
- Paper conflict: `NO_CONFLICT` (old manuscript/supplement candidates were not applied; active 1008 sources remain unchanged).
- Scientific difference: 1006's 10/06 readiness and narrative documents are earlier snapshots. Its bounded schedule, dose, CAI, strict-276, N=20 GLB, and open human-fidelity conclusions agree with the later 1008 source/claim ledger; its “Fresh C not yet confirmed” status predates the completed 300-object run. E6 was a stopped development candidate, not independent confirmation; only its explicit diagnostic and stop review were selected.
- Actual Git conflicts resolved: 0.


## codex/round2-evidence-integrated-20261001

- Pre-merge decision: `FULL_MERGE_REJECTED`; source archive HEAD `5a059b30eba959e69a2f36f484f06807e5c2c152` has 123 unique commits and a 2,640-path tree delta, deletes 253 active `1008/` and 353 active `1009/` paths, and contains 1,698 unique blobs / 675,119,677 uncompressed blob bytes. No merge or cherry-pick was run.
- Code differences were assessed before any merge: the archived source makes `_skip_correction` class-level shared state and removes main's `finally` restoration, and its `.gitignore` weakens precise evidence/generated-output rules. Main's instance-level exception-safe implementation and current ignore rules were retained. These are reviewed source differences, not merge conflicts.
- Historical Round-2 main text, Supplement, and response candidates were not imported. No Git merge conflict existed or was resolved: `NO_CONFLICT`, actual conflict files = 0.
- Only the compact B′ and M3 MV-Adapter mapping evidence package was selectively committed as `4b76ebc65387b3cbdc526b0ff8aff7ef01273be7`; its distinction and chronology caveats are recorded in the sequential audit. No active TeX, figure, response, bibliography, or submission file was merged.

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


## codex/evidence-closure-audit-20261005

- Git conflict status: NO_CONFLICT. No complete merge or cherry-pick was executed, so there were no Git conflict files.
- Scientific-claim reconciliation:
  - Source report’s endpoint-matched-linear equivalence claim was excluded; active 1008 says no equivalence margin was established.
  - Source report’s additive true-global mechanism wording was excluded; current dose/cap evidence does not isolate an additive causal decomposition.
  - Source unified-bake seam claim was excluded; main retires the historical seam measure and does not claim a seam improvement.
  - The texture-boundary measurements were independently reaggregated and selectively retained. Source decision report’s “10/10 Holm rejected” is corrected to 9/10; the FG-LPIPS/coverage test has adjusted p=0.050795.
- The H5 protocol file predates the archived result-bundle commit, while current main’s multiplicity-lock record labels the family lock retrospective after prior exposure. This is an evidence-status discrepancy, not a merge conflict; the conservative main status remains in force pending reconciliation.
- No active manuscript or response file conflict was created or resolved. The selected bundle records direct paper relevance without editing TeX.


## codex/cg-revision-evidence-closure-20261007

- 预合并审查决定 `FULL_MERGE_REJECTED`；未运行 Git merge 或 cherry-pick，因此 `NO_CONFLICT`，实际 Git 冲突文件数为 0。来源树会删除当前 1008 路径，并包含旧 `final/final_0903.tex` 候选及参与者级响应 CSV。
- 代码差异（不是 Git 冲突）：main 使用实例级 `_skip_correction` 状态并在 `finally` 中恢复；来源改为类级共享标志，pipeline 没有异常安全的 `finally` 恢复。依据是 main 的并发/异常隔离语义更强，来源旧逻辑可能跨实例泄漏状态；故来源版本未合入。来源对 `.gitattributes`、`.gitignore` 的放宽也被排除，以保留精确二进制处理和生成物规则。
- 论文差异（不是 Git 冲突）：来源候选属于旧 `final/` 修订，当前活动 1008 保持原样。已发现的 Fresh C C3−GFH CSV 和相关审计/来源材料在 main 已有等价内容，因此没有选择性补丁。
- 人类研究隐私：来源树内的 `HUMAN_STUDY_RAW_RESPONSES.csv` 未被打开或读取，不纳入本分支内容包；其原件按原地保留原则留在来源位置，后续仅由专门的人类研究来源审计决定是否需要聚合证据。
- 冲突影响论文：没有 merge conflict；候选文本未导入，活动主文、Supplement、回复及投稿文件均未改变。



## codex/final-evidence-freeze-20261001

- Pre-merge outcome: FULL_MERGE_REJECTED; the source deletes 247 active 1008 paths and 288 current 1009 paths while adding a 1,329-path historical final/ tree, generated assets, and stale paper candidates. No Git merge or cherry-pick was run: NO_CONFLICT, actual conflict files = 0.
- Code behavior reviewed and excluded (not a Git conflict): main keeps _skip_correction on each wrapper instance and restores previous state in finally; source uses a class-level shared flag and resets it only after the reference-write call. The source version can leak state after exceptions and across instances. Main's .gitattributes/.gitignore precision was also retained; source removes binary rules and exact generated-output ignores.
- Paper conflict: NO_CONFLICT. Old final/final_0903.tex, its Supplement/response, PDFs, and source package were not applied to the active 1008 package. Current TeX hashes were unchanged.
- Selective evidence: the compact Core-7 metrics/protocol/paired-statistics package was independently rerun and matched the source's aggregate, 49-row pair table, and row audit byte-for-byte. The C3−GFL Supplement row was separately reaggregated because it is absent from the source's saved 49- and 56-row pair tables. Current Core-7 retrospective limits were retained.
- Compiler note: built-in compile attempts were not successful because the standalone main source lacked project cag.sty and the standalone Supplement lacked its referenced figure asset; neither source file was modified.


## codex/main-backbone-robustness1-20260930

- Full-history merge was rejected before execution: 102 source-unique commits, 1,429 unique blobs / 665,718,360 uncompressed bytes, 14 blobs at least 5 MiB, and a 2,332-path direct tree delta. The old tree deletes 253 active `1008/` and 307 `1009/` paths while adding 1,052 old `final/` paths.
- Git merge or cherry-pick attempted: no. The compact R1 metrics, protocol/input audits, source scripts, and CPU reproducer were selectively added at `74b117fe05d834fb95b14ba136f15066d584f4f6`.
- Code conflict: `NO_CONFLICT`; no Git conflict was created. During pre-merge review, the source's class-level `_skip_correction` state and missing `finally` restoration were excluded in favor of main's per-instance, exception-safe behavior. This is a reviewed source difference, not a resolved merge conflict.
- Paper conflict: `NO_CONFLICT`; no TeX, figure, response, bibliography, or submission file was merged. The new result is recorded as indirect paper impact and remains outside active 1008 claims.
- Provenance caveat: source report claims the protocol lock predates R1 metrics, but Git first records both files in the same commit; the timing cannot be independently established from history. Accordingly, the result remains retrospective, not confirmed preregistered evidence.
- Actual Git conflicts resolved: 0.
