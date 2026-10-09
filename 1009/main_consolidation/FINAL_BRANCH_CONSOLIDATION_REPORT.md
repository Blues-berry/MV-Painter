# 最终分支归集报告 — MV-Painter / Computers & Graphics 1009

**捕获时间：** `2026-10-09T07:15:50Z` UTC  
**目标仓库：** 私有 `Blues-berry/MVPainter`  
**唯一授权推送目标：** `mvpainter/main`  
**活动工作树：** `/4T/MV-Painter-main`  
**本轮开始时 main 与远端完整 SHA：** `8cf02b797c5d467db764d05ea4940937c207fe96`  
**投稿批准：** `NO`；未向期刊提交。

## 收束结果

基线 1,831 条处置记录中，先逐项处理 117 条 `NEEDS_AUTHOR_DECISION`，再把基线后新发现的 192 个忽略文件登记为独立 `POST_SNAPSHOT` 行。最终 `FINAL_LOCAL_CHANGE_DISPOSITION.csv` 有 2,023 行，未处理项为 0：

| 范围 | 处置 | 数量 |
|---|---|---:|
| 原 117 条待裁决项 | `MERGED_MAIN` | 48 |
| 原 117 条待裁决项 | `ARCHIVED_LOCAL_VERIFIED` | 61 |
| 原 117 条待裁决项 | `ALREADY_PRESENT` | 5 |
| 原 117 条待裁决项 | `SUPERSEDED` | 2 |
| 原 117 条待裁决项 | `INVALID_EVIDENCE` | 1 |
| 117 条合计 | 已处置 | 117 |
| 另行登记的快照后文件 | `POST_SNAPSHOT` / 本地保留并逐项 SHA-256 | 192 |

全量 2,023 行状态计数：49 `MERGED_MAIN`、253 `ARCHIVED_LOCAL_VERIFIED`、1,611 `ARCHIVED_LOCAL`、31 `ALREADY_PRESENT`、78 `SUPERSEDED`、1 `INVALID_EVIDENCE`。253 条已核验本地归档中包括上表 61 条及 192 条快照后来源；它们保留在源工作树，没有整体导入 main。

## 已归集内容

- 从固定于 `32bb9106fa0ea6199e6a16f9279343c0b21581a6` 的 r1color 工作树选择 53 个经内容审阅的小型结果、协议、审计和 verdict 文件；另从 V3 本地结果取 5 个 strict-276 协议、审计及对象级摘要文件。58 个 payload 文件共 9,583,666 bytes，逐个核对来源/目标 SHA-256，并登记在 `MAIN_INTEGRATION_COPY_MANIFEST.csv`。两个目录另有 README 摘要。没有 merge 整个分支。
- r1color 结论进入 `COLOR_REPAIR_CAMPAIGN_REVIEW.md`：global-appearance embedding 在四个选定样例中控制 chroma；缓存/来源不一致是合理但未证实的贡献因素。C1 数值门通过（mean unseen ΔFG-CIEDE2000 −1.5602，95% CI [−2.2621, −0.6299]），但锁定视觉门失败；B2 完成 8 次生成、4 对象×6 视角，baseline reproducibility 为 4/4，但均值变化为 +0.172906（95% CI [−0.204353, +0.681015]），仅 1/4 改善，未达预设数值门，视觉上也无明确修正。没有独立 Fresh B 修复验证。未把候选写入默认推理路径。
- strict-276 作为开发后的补充分析归档：276 对象×6 schedules，共 1,656 行；eval loader 设为 `model.unet.eval()` 且 VAE eval。`LLH_ramp_eq − LLH_eq` FG-LPIPS 均值 −0.0003384，95% CI [−0.000605, −0.000063]，165/276 获胜。它不是独立队列复现，不替代 MAIN-STAGE-276；checkpoint provenance 仍标为 audit needed。stash 中 train-mode D19 576-row factorial 与这次 eval-mode 结果区分，前者不作有效推断。
- 1008 活动稿和回复信依据上述证据定向收窄 R1.1 限制，没有新增实验，没有改变 TCAS 方法或推理代码。

## 未合并且保留的价值

历史代码、未提交修改和大型实验输出没有按分支机械合并。旧状态按路径、来源、状态、SHA 和理由记录在 `FINAL_LOCAL_CHANGE_DISPOSITION.csv`、`LOCAL_CHANGE_SOURCE_MANIFEST.csv`、`WORKTREE_DISPOSITION.csv`、`STASH_SOURCE_AUDIT.csv` 与备份清单。大规模 RGB、GLB、checkpoint、cache、embedding、临时生成 JSON 和运行日志仍留在各源位置。没有删除数据、stash、branch ref，也没有运行 `git clean` 或强制 worktree 操作。

### 两个 stash

- `stash@{0}`（robustness1 / D19）：CODEX_B_STATUS 的有效 strict-276 后续证据已摘要进入 main；同一 stash 中历史 D19 train-mode factorial 被标为无效证据，旧 handoff 被后续审计取代。stash 原件仍保留。
- `stash@{1}`（v2-era-repro experiment）：历史 v2 训练配置、模型和 `train_v2.py` 与当前 1008 推理主张无关，保留本地且未合入。

## Worktree 与分支收尾

指定日常开发树为 `/4T/MV-Painter-main` 的 `main`。14 个 worktree 仍登记，编辑器实际根目录无法通过本工具切换，因此 `MAIN_SINGLE_EDITING_AUTHORITY=PARTIAL`。下表的每棵树状态数字来自 07:12 的最终 follow-up 快照，时间早于撰写本报告和重新组装投稿包；此后新增的报告与包文件仅位于指定 main 工作树，并随交付提交。已有三棵零 tracked/untracked/ignored 状态的树已在前序 handover 中普通注销：`/4T/CXY/MV-Painter-01549-merge-audit-f8ff09d2-20261009`、`/tmp/MV-Painter-v3-publish`、`/tmp/cg-closure-clean-final`；其 branch refs 仍保留。当前 14 棵如下：

| Worktree | 当前用途/状态 | 处理 |
|---|---|---|
| `/4T/CXY/MV-Painter` | V3；30 tracked 改动、581 untracked，330,633 ignored / 394,882,142,333 bytes | 保留本地结果与快照 |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | 53 tracked 改动、18 untracked、241 ignored / 120,977,297 bytes | 保留审稿修改与本地资料 |
| `/4T/CXY/MV-Painter-1006-wt` | 26 staged（含 25 deletions）、11 ignored | 不同步历史删除，保留 |
| `/4T/CXY/MV-Painter-1008` | 27 staged（含 22 deletions）、1 untracked image | 保留未裁决历史状态 |
| `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence` | 31 staged（含 25 deletions） | 保留 |
| `/4T/CXY/MV-Painter-r1color` | 固定 HEAD `32bb9106…`；1 untracked test；1,048 ignored / 2,379,764,671 bytes | 保留全部开发数据 |
| `/4T/MV-Painter-01549-unified-20261009` | 9 tracked 改动、17 ignored / 12,256,121 bytes | 保留 |
| `/4T/MV-Painter-main` | 唯一指定 main；本次 29 tracked 改动、60 untracked payload/README，随交付提交收束 | 唯一日常编辑入口 |
| `/4T/tmp/01549-clean-checkout-20261008` | detached；2 tracked 改动、17 ignored / 20,917,123 bytes | 保留 |
| `/tmp/MV-Painter-evidence-closure` | 2 ignored | 保留本地审计资源 |
| `/tmp/MV-Painter-human-confirmatory-20261007` | 10 ignored | 保留构建输出 |
| `/tmp/MVPainter-cg01549-private-upload` | 38 ignored | 保留构建输出 |
| `/tmp/cg-closure-clean-audit` | 4 ignored | 保留 C&G class/style |
| `/tmp/mvpainter-cg-evidence-closure` | 6 ignored | 保留 class/style 和 PDF |

28 个本地 branch refs 均未删除。清理清单（须作者明确批准后才删除 refs）：

`backup/geotex-before-cleanup`, `codex/cg-01549-surgical-revision-20261008`, `codex/cg-01549-surgical-upload-20261008`, `codex/cg-01549-unified-20261009`, `codex/cg-01549-unified-audit-f8ff09d2-20261009`, `codex/cg-ltcas-narrative-convergence-20261007`, `codex/cg-revision-evidence-closure-20261007`, `codex/cg-round2-1008-public-sanitized-20261008`, `codex/cg-round2-1008-revision-20261008`, `codex/evidence-closure-audit-20261005`, `codex/final-evidence-freeze-20261001`, `codex/human-confirmatory-analysis-20261007`, `codex/main-backbone-robustness1-20260930`, `codex/next-review-response-20260930`, `codex/paper-1006-20261006`, `codex/public-round2-evidence`, `codex/r1-color-cast-repair-v2-20261009`, `codex/r1-color-root-cause-20261008`, `codex/r1-color-root-cause-20261008-local-history`, `codex/r1-fidelity-validation-48h-20261008`, `codex/round2-evidence-integrated-20261001`, `codex/round2-final-forensic-audit-20261001`, `codex/scientific-validation-v3-20261002`, `codex/scientific-validation-v3-20261006`, `gh-pages`, `main`, `new0528`, `new0529`. Both stash entries remain. `gh-pages` is an independent publishing branch and excluded from cleanup.

No remaining worktree was removed in this pass: each has dirty/staged/ignored artifacts or provenance not safely inventoried for deletion. The `/tmp` worktrees are clean in tracked status but retained because ignored files exist.

## Author follow-up required

1. In the editor, Open Folder `/4T/MV-Painter-main` and verify Source Control shows `main`; that is the remaining blocker to `MAIN_SINGLE_EDITING_AUTHORITY=YES`.
2. Before physical cleanup, review `WORKTREE_DISPOSITION.csv`; separately approve branch-ref/stash deletion. No cleanup deletion is performed here.
3. Review novelty and evidence boundaries in `1008/submission_1008/FINAL_CG_SUBMISSION_READINESS.md`.

## Final gates

`MAIN_SINGLE_EDITING_AUTHORITY = PARTIAL`  
`ALL_RELEVANT_BRANCH_CONTENT_REVIEWED = YES`  
`UNIQUE_VALUABLE_SOURCES_ACCOUNTED_FOR = YES`  
`PENDING_117_DISPOSITIONS_RESOLVED_OR_EXPLICITLY_BLOCKED = YES`  
`BULK_EXPERIMENT_DATA_PRESERVED = YES`  
`UNSAFE_MERGES_AVOIDED = YES`  
`SCIENTIFIC_CLAIMS_CONSISTENT = YES`  
`REVIEW_RESPONSE_MATCHES_PAPER = YES`  
`LATEX_BUILD_PASSED = YES`  
`PRIVATE_MAIN_SYNCED = YES`  
`SUBMISSION_APPROVED = NO`

See [`LOCAL_DATA_RETENTION_MANIFEST.md`](LOCAL_DATA_RETENTION_MANIFEST.md), [`FINAL_LOCAL_CHANGE_DISPOSITION.csv`](FINAL_LOCAL_CHANGE_DISPOSITION.csv), [`MAIN_INTEGRATION_COPY_MANIFEST.csv`](MAIN_INTEGRATION_COPY_MANIFEST.csv), and [`WORKTREE_CLOSURE_AND_VSCODE_HANDOVER.md`](WORKTREE_CLOSURE_AND_VSCODE_HANDOVER.md) for hashes and source records.
