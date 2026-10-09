# 逐分支真实合并与论文影响报告

日期：2026-10-09  
仓库：Blues-berry/MVPainter  
活动工作树：/4T/MV-Painter-main  
处理方式：按分支逐项核查；历史数据工作树保持原位；本报告不代表所有分支已审核完成。

## Phase A：冻结基线

- 本地 main：93e079ac201d049d9bf36950c7f130ad369008ab
- 私有 mvpainter/main：93e079ac201d049d9bf36950c7f130ad369008ab
- 活动偏色分支 codex/r1-color-cast-repair-v2-20261009：32bb9106fa0ea6199e6a16f9279343c0b21581a6
- 活动跨骨干分支 codex/next-review-response-20260930：4f312566ed42a7b56fae9f11d91d4591d71fd1f2
- gh-pages：5f203f83e818ec9ae0b38f9b6c109b96866d6c7f
- 归档 HEAD 清单：BASELINE_ARCHIVED_HEADS_20261009.csv。该清单记录审计开始时的 41 个既有归档引用；本轮新建的 source-ready 本地归档引用另列在分支记录中。
- 必须保留的 WIP 提交：34d15cab5f2d4312d75e6921efb60eaad62c53c2、5e3e88e95c81e28200704988e4aaa7ef88239b1b、ecbb246b76cccf148dfbbdfa85515b53590aa584。

### 论文与投稿包基线 SHA-256

| 项目 | SHA-256 |
|---|---|
| 活动主文 manuscript_1008.tex | dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4 |
| 活动 Supplementary_1008.tex | 59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed |
| 活动 Response_to_Reviewers_1008.md | 1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb |
| 投稿包 Manuscript_1008.pdf | 8e231a2941a165de4c5c68b33ef087cc7f53a6550ad5e878eee742a575a08935 |
| 投稿包 Marked-up_Manuscript_1008.pdf | 143ecff586aa057e3e81c95cff09f749459b476ae23387890cfbbb5ac392c0b7 |
| 投稿包 Supplementary_1008.pdf | 79bd2cf57de7e94f62b82c1d7edefe03675427949578ad44fc8ab8b5470156db |
| 投稿包 Response_to_Reviewers_1008.pdf | c9cebb9dc8198ec9077d36f3dcf1dad084a9b064793bce9678303228a28d96a0 |
| 投稿包 LaTeX_Source_1008.zip | 348e42dc5663d4761ce0088e5e9af44b01af93b59a3e5cd1b031bd52d72115bd |
| 投稿包 SHA256SUMS.txt | 8f718a28eb24ee44220cc0f3cb8fe0c584d88b4b917e692e1eb7a66a11307ff5 |
| 投稿包 SUBMISSION_FILE_MANIFEST.csv | 8a46d7d70be726bfe5010ab63e17c81abf6d733ea032f7e01ce948fc35ffdab2 |

1008 投稿目录 SHA256SUMS.txt 共 48 项，逐项校验通过。投稿包内主文、补充材料和回复信 TeX/Markdown 与活动源文件字节一致。未执行投稿；SUBMISSION_APPROVED=NO。

## 顺序处理记录

### 1. codex/cg-01549-surgical-revision-20261008

- 原 HEAD：06cac81de23988aba94b5d7bfeaca93f6785f370
- 来源引用：refs/archive/codex/main-unification-20261009/local/heads/codex/cg-01549-surgical-revision-20261008
- merge-base：34c77a4417eb3e037756ad483c70ef9e3f0c2bdb
- 相对当前 main 独有提交：165；main 独有提交：22。
- 当前树对 main 的差异：34,797 个路径（33,975 A、43 M、779 D）。
- 独有 Git 对象：165 commits、1,651 trees、24,820 blobs，未压缩合计 3,628,919,412 bytes；45 个独有 blob 大于等于 5 MiB，最大为 178,306,395 bytes 的备份清单。
- 大型/生成内容抽查发现约 24,926 个 JSON 路径、7,215 个无扩展名路径、9 个 .pt 检查点，以及历史 PDF/ZIP、编译产物和研究归档。该历史不适合整支 merge；没有创建 merge 试验。
- 旧手术工作树有 53 个已跟踪文件变化：25 个字节内容已与当前 main 对应路径一致；27 个是旧投稿/候选包路径，当前 main 不存在；1 个候选 manuscript_1008.tex 与当前源不同。另有 18 个非忽略未跟踪文件，其中审稿轮次映射已与 main 中现有文件逐字一致，其他包括旧 build 输出、图片预览和 overlay 源。旧工作树及其 ignored 内容全部保留。
- 候选主文中恢复的 FAC 负结果和首轮偏好研究已由当前 1008 主文/回复信以明确历史范围和可复现性限制的口径保留。旧候选不能覆盖当前稿；旧投稿包不导入。
- source-ready 候选提交：deac8925d3bde92bae9ccb5d3ad92ea79ed69eae，仅整理该分支工作树中的审稿轮次映射。对应 SHA-256 f2a281decd51eed622e52db1cb222294e9428fe612c14906eedf24e0a6a82f3a，已与 main 同路径文件核对为字节相同；cherry-pick 为空并跳过，没有重复提交。此整理提交仅通过本地 refs/archive/codex/sequential-branch-audit-20261009/source-ready/paper-cg01549-surgical 保留，不推送。
- 决定：ALREADY_IN_MAIN；SOURCE_READY（仅指已审阅的选择性内容）；完整历史不合并。
- PAPER_IMPACT=DIRECT（分支含主文、补充和回复信候选改动）。逐项比较后没有把这些候选文本覆写到当前 1008；main 主文、Supplement、Response、PDF 和源包 SHA 全部不变并通过哈希核验。
- 冲突：NO_CONFLICT；完整 merge 未执行，因此没有制造或解决任何 Git 冲突。
- 验证：source-ready 文档 git diff --check 通过；活动 TeX 与投稿包源文件 SHA 匹配；48/48 投稿包 SHA 校验通过。由于没有主文或补充材料进入 main，本分支不触发重编译。没有应用代码改动，无运行时测试。
- 合并结果主内容 SHA：93e079ac201d049d9bf36950c7f130ad369008ab（报告提交会单独推进 main）。


### 2. codex/cg-01549-unified-20261009

- 原 HEAD：`284cd252b8b3bd5200aa61db7b7d37e443acd7b6`；来源引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/cg-01549-unified-20261009`；merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。
- 相对本次处理前 main（审计基线提交 `45964bb822a246787daeaeb0be66283117683dee`）：166 个分支独有提交、1,389 棵树、23,948 个 blob，未压缩共 3,035,104,087 bytes；24 个独有 blob 不小于 5 MiB。树差异为 27,292 路径（A=26,524、M=39、D=729），包括约 24,925 个 JSON 和大量无扩展名实验输出；独有大对象含约 76 MB 的旧投稿 ZIP、旧 PDF、统计 JSON 与模型检查点。完整历史不适合 merge；未启动 merge 试验。
- 旧工作树 `/4T/MV-Painter-01549-unified-20261009` 仍为 detached HEAD，原地保留；有 9 个 tracked 文件未提交变化：修订完整性 CSV、主文 TeX 与两份 PDF、回复信，以及 author-review 副本中的主文、回复信和两份 PDF。`git diff --check` 通过。没有在原工作树切换分支、提交或覆盖文件。
- 候选修订直接触及论文，候选主文和回复信确有措辞变化。检查结果：当前 main 已明确 Fresh C 使用同一研究内的冻结 checkpoint，但不声称它就是 01549 历史主表权重或旧 +0.96 dB 数值复现；也已保留 C3 定义、N=300、+0.522352 dB、GFH/Generic Linear 反例、Core-7 回顾性限定及 CAI/偏色限制。分支候选中没有需要替代当前认证文本的缺失科学主张。候选编译 PDF 与旧 author-review 副本不导入。
- 内容逐项比对：25 个 `1009/unification/` 文件中，13 个与 main 同路径同字节，1 个源码脚本在 main 的新路径下同字节；其余 11 个是记录旧 SHA、分支、工作树或对象状态的管理报告，不作为当前状态权威。Core-7 证据文件 5/5 和 R2 分析脚本 9/9 与当前 main 同路径同字节。该分支的审稿轮次映射也已在 main；没有发现需另建 source-ready 提交的有效唯一内容。
- 裁决：`ALREADY_IN_MAIN; FULL_MERGE_REJECTED`；`SOURCE_READY`（已完成内容审查；没有新内容需提交）。未 cherry-pick、未执行 merge，也没有空提交。
- `PAPER_IMPACT=DIRECT`：候选主文/回复信有差异，但当前论文文件未修改。活动 TeX、Supplement、Response 与投稿包仍与 Phase A SHA 相同，48/48 投稿包校验通过；因此不重编译、不更新投稿包。`SUBMISSION_APPROVED=NO`。
- 冲突：`NO_CONFLICT`（没有执行 Git merge/cherry-pick，因此没有产生或解决冲突）。测试：无应用代码改变；候选 tracked diff 的空白检查通过，当前论文与投稿包哈希复核通过。
- main 内容 SHA：`45964bb822a246787daeaeb0be66283117683dee`；本节审计记录的提交会单独推进 main。

后续论文分支、科学/证据分支、早期实现分支和两个保留实验分支尚未审计。后续分支必须按同一流程逐个追加矩阵和影响记录；在完成对应分支审查前，不依据旧清理结论删除或恢复任何普通分支引用。
