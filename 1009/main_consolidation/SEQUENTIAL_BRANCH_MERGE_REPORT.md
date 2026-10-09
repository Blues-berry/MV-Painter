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

### 1A. codex/cg-01549-surgical-revision-20261008（私有远端归档 HEAD）

- 来源 HEAD：`dad08320625431acf439ed5bfb86c6a9252353a4`；来源归档引用：`refs/archive/codex/main-unification-20261009/mvpainter/heads/codex/cg-01549-surgical-revision-20261008`。同名本地历史分支 HEAD 为 `06cac81de23988aba94b5d7bfeaca93f6785f370`，不是同一条历史，已在上一节单独审核。
- `/tmp/MVPainter-cg01549-private-upload` 是干净的 detached worktree，停在该远端归档 HEAD；没有未提交的 tracked/untracked 改动。来源提交标题为 `docs(cg): record Fresh C figure revision delivery`。相对分支前 main `8f2282c12ec8a40af635d19f40eed92e45f520b4`，merge-base 为 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`；来源有 155 个独有提交、1,329 棵树、23,853 个 blob，未压缩 blob 合计 2,993,693,628 bytes；22 个独有 blob ≥5 MiB，最大 76,043,516 bytes。树差异约 27,231 项（A=26,220、M=46、D=676、R=289）。
- 整段历史不适合直接 merge：包含 25,376 项旧 `final/round2` 内容、旧投稿/论文候选、生成资产与归档快照。来源 `.gitignore` 会恢复大块旧 `final/` 树并削弱当前精确生成物规则，`.gitattributes` 也移除当前 PDF/PNG/ZIP 与冻结证据的精确规则。来源 GeoTex 候选把 `_skip_correction` 改为类级共享状态，并移除 pipeline 的实例逐项保存和 `try/finally` 恢复；异常或跨实例调用可泄漏状态。上述均在预合并检查中排除，不是实际 merge 冲突；没有启动整支 merge 试验。
- 该来源含旧论文/回复候选，本轮不以候选覆写当前 1008。独有且有用的内容是 Fresh B A3b 每对象指标、对应 dose 行、Generic 扩展每对象指标、保存的分析 JSON 与协议/完整性门记录。已将 13 文件、约 3.41 MB 的紧凑包选择性纳入 `1009/evidence/branch_audits/cg_01549_surgical_remote_20261008/fresh_b/`，提交 `107e1aa8f89d048df11393085da2b8cc8b7e2b37`。主表基线及 `layer_llh` comparator 复用 main 已有的逐对象记录；已存在的 A3b texture-extension CSV 未重复复制。预测图、GLB、checkpoint、cache、residual render log、历史 PDF 和完整 archive 均未导入。
- 复核结论保持边界：A3b 冻结的 residual-only calibration 未达到 ±20% 平衡目标，因此只是 bounded intervention map，不是 equal-dose/dose-normalized 结果；Generic 扩展复用已开放的 Fresh B cohort，属于 post-lock sensitivity，不是独立确认。抽取后 15 个 A3b 条件和 8 个 Generic 条件各覆盖相同的 150 个 UID，FG-PSNR/FG-LPIPS 均有限；main 的 baseline/comparator 行与来源 ledger 逐字段相同。重聚合 30 个主要均值对比与保存 JSON 的最大绝对差为 `2.61e-16`；A3b 的 FG-LPIPS `W=225.015, Holm p=5.37e-43`，FG-PSNR `W=525.700, Holm p=3.43e-107`，与当前 Supplement 一致。协议先于数据的顺序有 Git 记录支持，但 Git 不能证明仓库外的实际事件时间；早期 row exposure 和停止的重复启动保留为局限。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。没有执行 Git merge/cherry-pick，实际冲突为 `NO_CONFLICT`，0 个文件。`PAPER_IMPACT=DIRECT`：新增 per-object 证据直接支持当前 Supplement 已有 A3b 与 post-lock Generic 结果，但没有更改活动论文、图表、回复信或投稿目录；活动主文、Supplement、Response SHA 仍等于 Phase A 值，投稿包 SHA256SUMS 为 48/48。没有 TeX 修改，所以没有触发 LaTeX 重编译或投稿包重建。`SUBMISSION_APPROVED=NO`，没有推送。
- 选择性内容提交后 main 为 `107e1aa8f89d048df11393085da2b8cc8b7e2b37`；审计记录提交会另行推进 main。


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


### 3. codex/cg-round2-1008-revision-20261008

- 原 HEAD/WIP：`5e3e88e95c81e28200704988e4aaa7ef88239b1b`（既有保护提交，保留）；WIP 前 HEAD：`3e592037d5fdf1c01a5052780e6203ed3d373846`；来源引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/cg-round2-1008-revision-20261008`。merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。
- 相对处理前 main `e06104a0e6095d1dfffec3e00402dee77b3d8230`，有 142 个分支独有提交、1,279 棵树、23,767 个 blob，未压缩 blob 共 2,889,656,077 bytes；16 个独有 blob 不小于 5 MiB。树差异为 27,178 项（A=26,338、M=13、D=684、R100=143），约 24,927 个 JSON 路径变化。大对象包括 76,043,516-byte 旧投稿 ZIP、21,429,443-byte pilot JSON、旧投稿 PDF 和 8.9 MB 检查点。该分支 WIP 树删除当前 main 中的活动 1008 主文/投稿包等文件；完整历史不安全，未执行整支 merge。
- 原工作树 `/4T/CXY/MV-Painter-1008` 保持 detached HEAD；tracked 状态干净，只有 `1008/audits/figure_candidates/R1_3_N20_UNLIT_BASECOLOR_INTERNAL.png` 未跟踪。该内部候选图片未加入 Git。原始 Fresh C 数据仍位于 `/4T/CXY/MV-Painter/1006/data/fresh_c`，SHA-256 与审计中的 raw CSV hash `6967375a66a523beeab2089a9e51fbd68b756f2a07b13439d443078bd4482cd6` 相符；没有复制、移动或删除原始数据。
- 内容判定：主文与投稿包候选属于旧树/WIP 删除状态，不得覆盖当前认证稿。分支中的数值结论（C3 与 GFL/GFH/Generic Linear 的方向、N=300 配对、C3 定义、CAI/FAC/strict-276 限定）均已体现在当前主文、回复信、`1008/authority/CLAIM_LEDGER.csv` 和当前审计。旧视觉候选池含大量生成 panel，不取代 main 已选图及其来源/授权清单。全量历史拒绝。
- 选择性整合的唯一有效子集是 Fresh C C3−GFH 审计代码与机器结果，提交 `dc6f43ae522e230f368232b9dfba393daf724c43`：分析脚本、source-integrity JSON、7 行结果 CSV/JSON 和审计说明，合计约 43 KB。审计从原位置只读重算，23/23 source/pairing checks PASS（300 个 UID、1,200 行、配对条件输入/seed 相符，runner/checkpoint/metric 一致）；不含原始 per-object CSV、图像、embedding、模型或缓存。此项为 `SELECTIVE_CONTENT_MERGE`。
- 科学结果状态：该 reviewer-requested 比较是 post-hoc、非确认性，无 p 值。重新运行结果与当前论文 C3−GFH 点估计/方向一致；使用 seed 20261002 的 Edge-SSIM 95% CI 为 `[-0.020803,-0.016790]`，活动主文/回复信为 `[-0.02084,-0.01683]`。两者都完全小于零，定性结论相同；将这点记录为 bootstrap 区间来源/重采样差异，不把另一组区间替换进稿件。后续改文前需核对活动稿表格的确切 bootstrap 输出来源。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED`；`SOURCE_READY`（原有 WIP 快照保留；有效审计子集已选择性提交）。main 内容 SHA：`dc6f43ae522e230f368232b9dfba393daf724c43`。
- `PAPER_IMPACT=DIRECT`：候选直接涉及主文统计与图表；本次仅增加支撑审计文件，没有改变活动主文、Supplement、回复信、图表或投稿包。活动 TeX/回复 SHA 与 Phase A 相同，投稿包 SHA256SUMS 48/48 通过；未重编译、未更新投稿包。`SUBMISSION_APPROVED=NO`。
- 冲突：Git `NO_CONFLICT`（没有 merge/cherry-pick，未产生 Git 冲突）；统计区间差异已单独记录，不视为冲突文件。验证：审计重跑 23/23 PASS；投稿包 48/48 PASS；没有 GPU 或应用代码行为变化。

### 4. codex/paper-1006-20261006

- 原 WIP HEAD：34d15cab5f2d4312d75e6921efb60eaad62c53c2；WIP 前 HEAD：a9ac1459b3d6d4312dab8dbd17534403133fb922；归档引用：refs/archive/codex/main-unification-20261009/local/heads/codex/paper-1006-20261006；merge-base：34c77a4417eb3e037756ad483c70ef9e3f0c2bdb。既有 WIP commit 保留。
- 相对处理前 main f8525f060172905260e65b62cfe1e3acf3f98bd1，分支有 144 个独有提交、1,102 棵树、2,667 个 blob、875,932,057 字节未压缩 blob；22 个 blob ≥5 MiB。树差异 3,328 项（A=2,415、M=7、D=760、R100=146），含 1,340 个 JSON 路径和旧投稿包/图件/生成结果；完整历史不适合合并，未运行整支 merge。
- 经审查选择性提交 E6 停止记录和 geotex/eval_exploration.py 的启动路径/CUDA 防护，提交 57f316719a5c56c61d0e0fa4fc1e4c7173a94c43 与 b1ac2f7d353b4362a040037257a51b9bedf40ed8。旧主文、Supplement、回复、PDF、原始数据和模型结果没有导入。旧版类级共享 _skip_correction 与缺少 finally 恢复逻辑被排除；main 的实例级隔离与异常恢复保持。
- PAPER_IMPACT=DIRECT：1006 是过时论文/证据快照；其“Fresh C 尚未完成”状态被后来 N=300 结果取代。E6 是停止的开发候选，不作为论文结果。活动论文源文件未改，投稿包 48/48 校验通过；必要的 CPU 路径与防护检查通过，无 GPU/模型运行。
- 决定：SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY。没有执行 Git merge/cherry-pick，因此代码和论文均为 NO_CONFLICT，实际冲突数为 0。WIP commit 保留；SUBMISSION_APPROVED=NO。


### 5. codex/cg-ltcas-narrative-convergence-20261007

- 原 HEAD/WIP：`ecbb246b76cccf148dfbbdfa85515b53590aa584`（既有 WIP commit 保留）；WIP 前 HEAD：`bf1dc3d41edd597421c067a972c82abfb4b8fdf7`；来源引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/cg-ltcas-narrative-convergence-20261007`。merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。
- 来源工作树 `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence` 当前不存在。前一轮最终工作树处置记录为普通注销，注销时 tracked/untracked/ignored 文件均为 0；更早的 31 个 staged 路径由已保留的 WIP commit 捕获。此轮未对该路径做任何删除或恢复操作。
- 相对处理前 main `450eda30030fc5a1a37809e02242f0620791d29c`，有 142 个分支独有提交、1,023 棵树、2,429 个 blob，未压缩 blob 共 776,750,834 bytes；15 个独有 blob 不小于 5 MiB，最大 76,043,516 bytes。树差异为 3,160 项（A=2,244、M=8、D=908）。大量路径是旧投稿候选、历史代码快照和生成图/表；WIP 树删除当前 1008 稿件/投稿包及当前 1009 证据。完整历史不适合 merge，未启动整支 merge 试验。
- 候选 10/07 叙事和回复文稿经直接审阅。其主要边界与后来的 1008 一致：C3−GFL 为限定的 Fresh C 主结果；Generic Linear/GFH 为反例；Fresh B 时序结果、strict-276 和跨骨干结果分别限于各自 cohort/协议；不声称普适 schedule winner、等价性、等剂量机制、CAI 最优性、材料保真或普适跨接口转移。候选把 FAC 从修订稿移除；当前 1008 将其限定为 01549 历史结果并披露身份/证据缺口，回复信亦说明不作为 Fresh C 新结果。采用当前 1008 认证文本；不导入 `final/final_0903.tex`、Supplement、旧回复信、旧 PDF/投稿包或候选图片。
- 10/07 数值一致性审计有独立可复现价值，选择性保存至 `1009/evidence/branch_audits/cg_ltc_as_narrative_20261007/`（主文/包不改变）。内含原始 verifier、162 行数值权威 CSV、四个哈希固定的紧凑 per-object metric/delta CSV 及其分析/输出记录，共 4,055,726 bytes。重跑 42 项全部 PASS，容差 `2e-10`，输出 SHA-256 与原归档报告逐字节相同（`ae6a325f...1b7b4`）。此核验重聚合已保存指标，不重新生成图像；其中两个输入已在 1008 的 R2 审计目录逐字节存在，bundle 内重复仅为满足原验证器固定相对路径。该结果是旧 revision-authority 的历史复核，不替换当前 1008 claim ledger；C3−GFH interval provenance 的微小差异仍按分支 3 报告，不用此 bundle 改稿。
- 当前 claim ledger 引用的 `PUBLIC_HUMAN_DATA_DISPOSITION_20261007.md` 已按原 SHA `57fc15b1130d45ddffdb6ff7441d397bcc1005101cb2fa46933c09cfd462b4af` 恢复至 `1006/evidence/audits/`。此文件仅是历史公开风险处置，不含参与者答卷；明确 `PUBLIC_RAW_HUMAN_DATA=NO`。未复制或分析参与者级记录。
- 代码与仓库策略差异：分支候选再次把 `_skip_correction` 设为类级变量，并移除 main 的逐实例保存与 `finally` 恢复逻辑，故排除该核心实现。分支 `.gitignore` 删除了当前冻结证据/论文中间产物/实验生成目录的精细规则，`.gitattributes` 也移除 PDF/PNG/ZIP 二进制与源文件空白规则并加全局 CSV CR 规则，均不采用。`README.md`/`CLAUDE.md` 描述的是旧 `final/` 和旧训练/实验状态，不覆盖当前项目说明。其余代码脚本与分支 4 已整合的探索脚本相同或仅多一个尾部空行；未发现第二项必需运行时代码修改。
- 来源裁决：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED`；`SOURCE_READY`。选择性提交 `174431225cc5247170c35fec25bd39ef6649fc2e`（提交全 SHA 见 main 日志）；三个既有 WIP commit 均保留。
- `PAPER_IMPACT=DIRECT`：审阅了分支中的整套候选论文、回复、数值权威与图件；只增加历史数值复核和数据公开边界说明，没有改动活动 1008 主文、Supplement、回复、图或投稿包。活动 TeX/回复 SHA 与 Phase A 相同，48/48 投稿包校验通过；不需重编译或更新投稿包。`SUBMISSION_APPROVED=NO`。
- 冲突：`NO_CONFLICT`（未执行 Git merge/cherry-pick，因此没有产生或解决 Git 冲突）。验证：42 项重聚合 PASS 且 JSON 字节级匹配；公开处置文件 SHA 与当前 claim ledger 相符；活动主文、Supplement、Response SHA 未变；投稿包 48/48 PASS；`git diff --check` 通过。无模型推理、GPU 或期刊投稿。

### 6. codex/scientific-validation-v3-20261002

- 原 HEAD：`5c2c8829a1e19b42837761160dc4c14cf8f09045`；来源引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/scientific-validation-v3-20261002`；merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。
- 相对当时 main `e571bca0d5693450de5dd7d22280b73e407b0e79` 有 163 个来源独有提交、1,798 棵树、36,865 个 blob，未压缩 7,776,031,685 bytes；15 个独有 blob 不小于 5 MiB，最大 76,043,516 bytes。树差异 42,729 项（A=41,798、M=7、D=924）。旧树含约 40,196 项 V3 生成/实验输出，并删除当前 1008 文件及 116 项紧凑 V3 发布证据；不适合整支合并，未执行完整 merge。
- 旧工作树 `/4T/CXY/MV-Painter` 的 30 项已跟踪改动（26 项暂存删除、4 项文档修改）通过临时索引形成 WIP `23ba46e35ec9465d737b1d2e61116b9904bb9d4c`，保存在本地归档引用 `refs/archive/codex/main-unification-20261009/local/wip/codex/scientific-validation-v3-20261002`。原 HEAD、真实暂存区和工作树均未移动或清理。另有 581 个非忽略未跟踪路径，涵盖 1006 候选/证据、01549 备份与审稿文件；全部留在原目录。未枚举或哈希其中 ignored 大型数据。
- `1008` 中 Fresh C N=300 主结果和 1009 的 MV-Adapter 报告已在 main。选择性保留新增的 E1/E2 48-object 固定子集审计材料，以及 MVDiffusion 75-object 七条件逐对象指标、配置、分析和限定报告，合计约 0.83 MB，路径为 `1009/evidence/branch_audits/scientific_validation_v3_20261002/`。没有复制预测图片、残差轨迹、GLB、权重、检查点、缓存或参与者级答卷。选择性提交 `73e5b91c`；同时只为该目录的 CSV 增加 CRLF 行尾识别规则。
- E1 仅为既有 48-object cohort 上三固定 seed 的 realization sensitivity；E2 是静态尺度因子分析，不检验时间效应或等 realized dose。50 项 E1/E2 摘要、JSON 与逐对象均值核对通过。MVDiffusion 分析脚本从 7 组各 75 行指标表重算，panel CSV、paired-bootstrap JSON、Markdown 汇总 3/3 与原输出字节一致。无 GPU 或模型运行。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED`；`SOURCE_READY`（原 worktree 保留）。旧树中三个未提交科学总结涉及后续人类研究裁决；仅把其 WIP 保存在本地归档，待人类研究分支单独核查。当前 1008 主文、Supplement、回复信、图和投稿包未改，Phase A 三个活动文本 SHA 不变，投稿目录 48/48 校验通过。
- `PAPER_IMPACT=DIRECT`：MVDiffusion 指标补齐了当前主文已有的边界性结果支撑；E1/E2 为后续修订提供限界信息。更新的 V3 readiness 摘要另称 37 份有效人类答卷、8 个终点均未通过 Holm；该人类结果尚待专门来源审计，不据此改写当前论文。冲突：`NO_CONFLICT`（未执行 merge 或 cherry-pick，没有产生 Git 冲突）。验证：47 项包内 SHA256 校验通过、MVDiffusion 3/3 byte-exact、E1/E2 50 assertions、`git diff --check` 通过；主文/Supplement/回复信未变，因此本分支未触发 LaTeX 重编译。`SUBMISSION_APPROVED=NO`。

第一组论文分支及第一项科学证据分支已逐项审计。后续继续逐分支处理科学审计、证据闭合、稳健性、人类研究及保留实验分支；旧数据原件留在原工作树。


### 7. codex/evidence-closure-audit-20261005

- Source HEAD: 7e659c7e5695ecc7ea2a0fbd80f2110289b2804a; local archive ref: refs/archive/codex/main-unification-20261009/local/heads/codex/evidence-closure-audit-20261005; merge base: 34c77a4417eb3e037756ad483c70ef9e3f0c2bdb. The detached source worktree remains at that HEAD with no tracked changes. No source cleanup or WIP commit was needed.
- The full source has 161 unique commits, 1,780 trees, 36,806 blobs, 7,769,781,069 uncompressed unique blob bytes, and 15 unique blobs at least 5 MiB (maximum about 76 MB). Its tree delta is 42,742 paths (A=41,763, M=7, D=972), including 21,661 PNG and 19,054 JSON outputs and 160 GLBs. A full merge would remove current 1008 files and selected 1009 V3 evidence. It was not run.
- Main already summarized the Fresh Confirm 300 texture boundary in C13, but it did not contain these paired per-object inputs. The tracked 150-object Fresh Confirm B tables are a different cohort. The branch’s LLH and native-GFL source rows match all 300 frozen UIDs; manifests agree on object-list, checkpoint, runner, seed, sampler, resolution, steps, and six target views.
- Source decision reports also make stronger claims that are superseded or contradicted by current main: endpoint-matched-linear equivalence is not established; true-global comparisons do not identify an additive causal mechanism; historical seam claims are retired; and broad transfer claims exceed the tested scope. These texts and the generated image/GLB/residual artifacts were excluded.
- The unique, useful H5 inputs and conclusion were selectively committed as 0c62633f54f5aec84916bcf614f73840af38f8e5, in 1009/evidence/branch_audits/evidence_closure_audit_20261005/. The 74 KB compact CSV retains the paired FG-PSNR/FG-LPIPS values and five GT-only descriptors for 300 objects; it omits raw renders and machine-absolute paths.
- CPU-only reaggregation reproduced the source pairwise mean/CI exactly: LLH−GFL FG-PSNR +1.2877358 dB [0.9382723, 1.6345938]. The tie-aware Spearman reaggregation gives delta FG-PSNR versus GT HF energy −0.691388 [−0.745039, −0.625807]; the quartile means/win rates match the source to displayed precision (Q1 +4.14 dB/92% versus Q3 −0.087 dB and Q4 −0.029 dB). The compact analysis uses average ranks, 10,000 paired-object bootstrap resamples, and seed 20261002.
- The archived decision report states all 10 H5 tests reject after Holm. That is not supported by its saved result JSON: its FG-LPIPS/coverage tail probability is 0.0506, and it contains no Holm output. With a plus-one Monte Carlo correction and the locked ten-test Holm family, 9/10 tests reject; FG-LPIPS versus coverage has adjusted p=0.050795 and does not reject. The source script also labels positive FG-LPIPS deltas as “wins”; the compact reanalysis corrects the direction.
- PRIMARY_HYPOTHESES.md contains H5 in commit c1fb1b75814c91dc063aeab55007bbd66601fd3f (2026-10-02), before the archived result-bundle commit 7e3a8d4b (2026-10-04). Current main’s B_MULTIPLICITY_FAMILY_LOCK.md nevertheless classifies the family lock as retrospective after prior outcome exposure. Preserve this timing/status discrepancy; do not import the source report’s unrestricted confirmatory wording.
- Decision: SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY. PAPER_IMPACT=DIRECT: the active 1008 manuscript does not state this specific Fresh Confirm 300 boundary, so the result is a candidate for the later applicability/limitations revision. No paper files were changed in this branch audit.
- Git conflicts: NO_CONFLICT (no merge or cherry-pick was attempted). Validation: 300/300 cohort IDs and pairing checks pass; the pairwise values and quartile effects reproduce; the ten-test reaggregation yields 9 Holm rejections; git diff --check passes; the submission package remains 48/48; active TeX and response hashes are unchanged. No GPU or model inference.


### 8. codex/cg-revision-evidence-closure-20261007

- 原 HEAD：`d59c4606ad54239bf4df4f20067bcc54989404f7`；来源引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/cg-revision-evidence-closure-20261007`；merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。隔离 detached 工作树位于 `/tmp/mvpainter-cg-evidence-closure`，在该 HEAD 干净；无需整理提交，`SOURCE_READY`。原工作树、原始数据和归档引用均未移动或删除。
- 对当前 main `c1c087b2e7388fa171e185d5207f2fb336742704`，来源独有历史为 131 commits、971 trees、2,385 blobs、765,582,985 未压缩 blob bytes；14 个独有 blob 不小于 5 MiB，最大 76,043,516 bytes。树差异 3,231 项（A=2,245、M=8、D=978），包含对活动 1008 路径的删除以及过时的 `final/final_0903.tex` 候选。来源还跟踪了 `HUMAN_STUDY_RAW_RESPONSES.csv`；该参与者级文件未打开、未读取、未复制、未哈希，留待专门 human-study 分支审计。完整历史不适合 merge，未启动 merge 试验。
- 已核查代码差异：来源将 `_skip_correction` 改为类级共享状态，pipeline 也以共享标志切换且缺少 `try/finally` 恢复；这会破坏 main 的实例隔离，并在异常或并发时泄漏状态。来源还放宽二进制/源文件属性及精确生成物忽略规则。保留 main 版本；候选旧 README/CLAUDE 与 `final/` 稿件未导入。
- 有效的 Fresh C C3−GFH CSV 与 main 1008 审计 CSV 字节完全一致。对应结果 JSON 的统计内容相同；差异仅为 `source_integrity_path` 的临时绝对路径。来源完整性 JSON 的两个输出路径也是临时目录，且结果 JSON 哈希随该路径变化；不构成新统计证据。Fresh C 执行语义、GLB sampler、seam disposition、数值权威 CSV、图像 cohort 权利与 attribution 文件均已在 main 的审计路径逐字节存在。候选 20-panel 池、广泛 API 授权清单和旧论文/回复草稿不替代当前已选图及认证稿。
- 裁决：`ALREADY_IN_MAIN; FULL_MERGE_REJECTED; SOURCE_READY`。无选择性内容提交，因为没有发现需要新增的独有有效内容；没有空提交。
- `PAPER_IMPACT=DIRECT`：来源含旧候选主文、回复和投稿证据闭合材料，但均针对旧 `final/` 候选。未覆盖当前 1008 主文、Supplement、Response、图表、参考文献或投稿包。Phase A 活动 TeX/回复 SHA 保持不变；48/48 投稿包校验通过；未触发 LaTeX 重编译，也未投稿（`SUBMISSION_APPROVED=NO`）。
- 冲突：`NO_CONFLICT`。没有执行完整 merge 或 cherry-pick，因此没有实际 Git 冲突文件，也没有冲突解决提交。上述代码和候选论文差异是在预合并审查中排除，不标记为已解决的 merge conflict。
- 验证：来源工作树干净；对照确认 C3−GFH CSV 字节一致、结果 JSON 统计 payload 一致、相关来源报告在 main 已有等价版本；活动论文哈希未变；投稿包 48/48 PASS。没有代码进入 main，因此未运行运行时测试；未运行 GPU 或模型推理。
- 决策时 main 内容 SHA：`c1c087b2e7388fa171e185d5207f2fb336742704`；本条仅更新审计报告，后续报告提交会推进 main。



### 9. codex/final-evidence-freeze-20261001

- Source HEAD: 29b3a0a6ec00f5848f1898ffda4fb8e787f81375; archive ref: refs/archive/codex/main-unification-20261009/local/heads/codex/final-evidence-freeze-20261001; merge-base 34c77a4417eb3e037756ad483c70ef9e3f0c2bdb. No registered source worktree exists, so this decision is based on committed archive content; no claim is made about an uncommitted worktree state. The archived commit is SOURCE_READY for selective review; no source WIP commit was identified.
- Against main before this branch (8bdaf7bc2655abdc54d4de558088b665264f0dec), the source has 125 unique commits, 1,728 unique blobs / 675,604,787 uncompressed bytes, 14 blobs at least 5 MiB (maximum 76,043,516 bytes), and a 2,587-path tree delta (A=1,600, M=7, D=980). The source deletes 247 paths under 1008 and 288 under 1009, and adds 1,329 old final/ candidates and audit/generated paths. Full merge was rejected before execution.
- The source's Core-7 forensic script and saved outputs were reviewed because current 1008 Supplement cites retrospective 276-object condition means and paired contrasts. Main already had the exact 49-row CORE7_FINAL_AGGREGATES.csv and its C3-GFH calculation, but lacked the cited paired-statistics table, row audit, prior paired-bootstrap input, and source rows for five conditions. A 1.17 MB selective package now preserves seven 276-row condition CSVs, seven protocol manifests, the 56-row prior bootstrap table, the source script and a small reproducer at 1009/evidence/branch_audits/final_evidence_freeze_20261001/; canonical paired outputs are at 1008/audits/source_evidence/r2/core7/.
- CPU-only reproduction passed: 1,932 rows (7×276), exact object-index mapping, finite fields, and identical serialized GT descriptors; all three generated outputs match the archived output byte-for-byte. The 49-row paired output reconciles 42/56 shared prior rows with no mismatches. The seven condition means and current Supplement's LLH−GFH (+0.822292 dB, 95% CI [0.616795, 1.033035], 148/276) and LLH−C3 (+2.036527 dB, [1.806804, 2.260756], 227/276) rows match. The Supplement's C3−GFL row was not present in the saved pair tables; it was recomputed from the same indexed source rows: +1.207771 dB [1.116967, 1.294989], 259/276. The existing post-hoc C3−GFH rows also match.
- Decision: SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY (for archived committed content). The source's broad “same-runner” freeze narrative was not adopted: current 1008 correctly limits Core-7 to a retrospective diagnostic, notes condition-level runner/input-hash gaps, and keeps it distinct from Fresh C and the original 01549 estimate. Old seam and cross-backbone conclusions were not promoted.
- Code and ignore-rule review: the source changes main's instance-level _skip_correction into a class-level shared flag and removes the instance save/finally restore; it also removes binary attributes and precise generated-output ignores while adding old final/ content. These regressions and the source's stale TCAS/final manuscript documentation were excluded.
- PAPER_IMPACT=DIRECT: the selection supplies cited diagnostic statistics and row provenance, without changing active TeX, Supplement, figures, Response, or canonical submission files. The active manuscript SHA remains dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4; Supplement SHA remains 59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed. The submission package passes 48/48 checks. Built-in LaTeX compilation was attempted for both files: main compilation timed out with missing project cag.sty; Supplement compilation reached the project figure reference but failed because standalone compilation could not load figures/figS1_adverse_c3_gfl.png. No TeX edit or alternate PDF build was made. SUBMISSION_APPROVED=NO; no submission.
- Git conflicts: NO_CONFLICT; no merge or cherry-pick ran, so actual conflict files resolved: 0. Validation: source output byte matches 3/3; 42/56 prior pairs reconcile; manuscript table checks pass; git diff --cached --check passes with path-specific CRLF recognition; 48/48 submission checks pass.
- Selective content commit: 9a0b132c26495394e787016c6b7b8da8ee382cad; this section's report commit advances main separately.


### 10. codex/main-backbone-robustness1-20260930

- Source HEAD: `99d6c88f28050a3fb74a04d74f555ba30f27ff3e`; archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/main-backbone-robustness1-20260930`; merge-base: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`. No registered worktree is at this HEAD, so only committed archive content was assessed; no uncommitted-worktree claim is made. `SOURCE_READY` for archived content; no source WIP commit was found.
- Against main `221eda90848ac5698eba5e368037a4028f8ee23a`, the source has 102 unique commits, 573 trees, 1,429 blobs / 665,718,360 uncompressed bytes, and 14 blobs at least 5 MiB (maximum 76,043,516 bytes). The direct tree delta is 2,332 paths (A=1,312, M=7, D=1,013): it deletes 253 active `1008/` paths and 307 `1009/` paths while adding 1,052 old `final/` paths. Full merge was rejected before execution.
- Selective content commit `74b117fe05d834fb95b14ba136f15066d584f4f6` retains the combined 1,380-row R1 Core-5 metric CSV, protocol and shared-input audit records, reference-realization summary, original report, and historical runner/audit scripts. It reuses the five matching R0 metric CSVs already committed in main; four match the original `/4T/tmp` files byte-for-byte and R0 Global-C3 matches the archived matrix-completion CSV byte-for-byte. Duplicate `rows.json` and per-method R1 tables were omitted. Render PNGs, run/preflight/reference logs, old launcher, model/output trees, and the old `final/` tree were excluded. No original data was moved or duplicated.
- CPU reaggregation passed: all 1,380 R1 rows map to the same strict-276 IDs; the saved 28-cell table matches 28/28; aggregate means match 70/70; paired-result payloads match 56/56; and R0/R1 method rankings match on all seven metrics. Counts are 27 `STABLE_STRONG`, 1 `STABLE_DIRECTIONAL`, and 0 `UNSTABLE`. R1 primary LLH−GFL FG-PSNR is +3.233152 dB [2.928141, 3.526766], 241/276 wins. Source preflight records 0 pass1/pass2 and cross-method mismatches, plus 500/500 matching deterministic components and 150/150 changed reference-derived components.
- Protocol-timing limitation: although the source report says `PROTOCOL_LOCK.md` was written before observing R1, the lock and R1 metric CSV first appear in the same source commit `99d6c88f` (2026-10-01 00:33 UTC). Git cannot independently verify that chronology. The result remains a retrospective robustness diagnostic and is not promoted as independently verified preregistered or confirmatory evidence.
- Code review: the old source tree has a class-level `_skip_correction` flag and lacks main's per-instance restore in `finally`; those code changes were excluded before any merge. They are source differences, not Git conflicts. The selected helper is CPU-only and only reaggregates stored metrics.
- `PAPER_IMPACT=INDIRECT`: the R0/R1 result is absent from active 1008 and was not promoted into a claim. No TeX, figure, response, bibliography, or submission file changed; the frozen hashes remain unchanged and the canonical submission package passes 48/48 checks. No LaTeX compile was needed for this data-only addition. `SUBMISSION_APPROVED=NO`.
- Git conflicts: `NO_CONFLICT`; no merge or cherry-pick ran, so no Git conflict was created or resolved. Main content SHA after the selective commit: `74b117fe05d834fb95b14ba136f15066d584f4f6`; the report update is committed separately.


### 11. codex/round2-final-forensic-audit-20261001

- Source HEAD: `450389fb8232c0f03db0b79f21bdc998043a99e0`; archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/round2-final-forensic-audit-20261001`; merge-base: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`. No registered worktree is at this HEAD and no uncommitted WIP state is available; the committed archive is the reviewed source.
- Against main `abd9827dd84d7c75d9512ac935fb70c7c823df34`, the source has 119 unique commits, 716 trees, 1,695 blobs / 674,977,791 uncompressed bytes, and 14 blobs at least 5 MiB (maximum 76,043,516 bytes). Its 2,621-path tree delta is A=1,581, M=7, D=1,033; it deletes 253 active `1008/` paths and 334 `1009/` paths while adding 1,312 old `final/` paths. The history also contains 865 JSON and 154 PNG additions. Full merge was rejected before execution; no merge trial was run.
- The branch's `phase1a_llh_gfl_per_object_deltas.csv` was checked against the already retained R0 `layer_llh` and `global_fixed_low` per-object tables in `1009/evidence/branch_audits/final_evidence_freeze_20261001/inputs/`. All 276 object IDs and all 2,760 numeric cells across the seven deltas, two FG-PSNR source scores, and crop area match exactly (maximum absolute difference 0). Its R0/R1 sensitivity is already covered by branch 10. No unique valid result needs another copy in main.
- The source's approximate additive residual-budget/placement decomposition is not adopted: it combines contrasts with different endpoints and does not identify a pure allocation effect. The source's old `final_round2.tex`, Supplement, response, figures, and outdated strict-276/LHL/figure-selection/gradient claims are not current 1008 evidence. The active manuscript separately labels the post-inspection strict-276 follow-up and retrospective Core-7 scope, and does not claim equal-realized-dose causality or an optimal schedule. A dated scope note was appended to the V3 closure matrix without rewriting its historical rows.
- Decision: `ALREADY_IN_MAIN; FULL_MERGE_REJECTED`; `SOURCE_READY` for committed archive review only. No source-ready commit, cherry-pick, or merge was needed; no unique content was added for this branch. `PAPER_IMPACT=DIRECT` because historical manuscript candidates and result interpretations were reviewed, but none were adopted.
- Conflicts: `NO_CONFLICT`; no Git merge/cherry-pick was attempted, so no conflict was created or resolved. Validation: exact per-object comparison above; active manuscript, Supplement, and response SHA-256 remain `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; the submission package verifies 48/48. No active TeX changed, so no LaTeX rebuild was needed. `SUBMISSION_APPROVED=NO`.


### 12. codex/human-confirmatory-analysis-20261007

- Source HEAD: `86292c8b5822533e52a1621cc04e6c076dbdc153`; archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/human-confirmatory-analysis-20261007`; merge-base: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`. The registered source worktree `/tmp/MV-Painter-human-confirmatory-20261007` is detached and clean at source HEAD. No source WIP commit or uncommitted tracked/untracked change was identified. `SOURCE_READY`; source worktree and its ignored local files were left in place.
- Against main `1121554911c7d587c0421389bdabab648f990c92`, the source has 145 unique commits, 1,117 trees, 2,721 blobs / 904,462,082 uncompressed blob bytes, and 23 blobs at least 5 MiB (maximum 76,043,516 bytes). Its 3,646-path tree delta is A=2,607, M=7, D=1,032; it deletes 253 active `1008/` and 334 `1009/` paths while adding 1,854 old `final/` and 482 `1006/` paths. Full-history merge was rejected before execution; no merge trial was run.
- Seven modified source paths were reviewed. `.gitignore` drops main's precise V3 evidence exceptions and generated-output rules while restoring historical `final/` content. `model_unet_geotex.py` changes `_skip_correction` from instance state to a class variable; `mvpainter_pipeline.py` removes main's per-instance save and `try/finally` restoration, then resets shared state only after the reference-write call. This can leak state after exceptions and across wrapper instances; main's behavior was retained. The two `geotex` changes add only a terminal newline. No source code or ignore-rule change was selected.
- The source's 2026-10-07 classification override designates the eight pre-specified endpoints as confirmatory with documented execution deviations. The lock fixes four comparisons × two separate questions, equal-object estimates, a 10,000-resample participant/object bootstrap (seed 20261005), plus-one two-sided tests, and one eight-endpoint Holm family. The owner classification occurred after the response export; it does not waive execution deviations or establish complete protocol adherence.
- Results represent 40 slots, 37 valid participants (2 comprehension failures; 1 incomplete/missing), 24 objects, and 222 judgments per endpoint. All eight point estimates exceed 0.5, but 0/8 survive Holm correction. GFL texture is 0.647 [0.528, 0.755] (raw p=.0123, Holm p=.0984); GC3 texture is 0.632 [0.521, 0.741] (raw p=.0183, Holm p=.1281). No preference advantage, equivalence, or non-inferiority is established. The prior hashed schedule audit records 0/40 same-slot and 0/40 any-slot matches; the new analyzer marks private-key audit unavailable. All 96 object×comparison cells use fixed left/right orientation, balanced 12/12 across objects per comparator. Seed, question order, raw comprehension answers, stimulus-hash crosswalk, coordinator closeout, and consent/ethics documentation are absent.
- Selective content commit `77820ab7eeb6fce5b4c5dc299e2b806ac8c5eb60` preserves the aggregate-only human audit, frozen pair lock, gate validation/verdict, classification override, adapted safe reproducer, and aggregate forest plot under `1009/evidence/branch_audits/human_confirmatory_analysis_20261007/`. Participant-level response/assignment/object/pair files and the coordinator key were not copied. The reproducer reads the archived source rows into memory, never checks a private-key path, and emits only aggregate outputs. Its CSV and provenance JSON regenerated byte-for-byte; no participant-level rows were written or printed.
- The same commit retains the compact E5 technical feasibility report, protocol, sanitized lock, and aggregate gate/cap summaries under `1009/evidence/candidate_methods/e5_residual_dose_20261006/`. Its lock's machine-specific absolute paths were normalized to repository-relative paths; the source lock SHA is recorded in the README. The record reports 4,860 finite wrapper-step traces and shallow cap exceedance at tested alphas, but no quality metrics; ignored raw traces and model assets were not copied. This development-only evidence does not support a quality or dose-independent mechanism claim.
- Decision: `SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`. No Git merge or cherry-pick ran. Actual conflicts: `NO_CONFLICT` (0 files); the unsafe source code changes were rejected during pre-merge review, not “resolved” as merge conflicts.
- `PAPER_IMPACT=DIRECT`: the new human evidence could inform a bounded R1 response, but shows no multiplicity-adjusted LLH advantage and does not close absolute-fidelity or 3D concerns. The current 1008 manuscript, Supplement, and Response remain unchanged; the original 01549 3AFC scope remains separate. Consent/ethics, coordinator closeout, and participant-data governance remain open. The active TeX hashes remain `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; canonical submission checks pass 48/48. No TeX changed, so no LaTeX rebuild was needed. `SUBMISSION_APPROVED=NO`; no push or journal submission.


### 13. codex/round2-evidence-integrated-20261001

- 来源本地归档 HEAD 为 `ce4831f40c723631e395f86268dca13afe9d07e9`；归档私有远端 HEAD 为 `5a059b30eba959e69a2f36f484f06807e5c2c152`，比本地 HEAD 多 5 个提交。远端新增的 5 个提交只修改 `final/round2/final_round2.tex`、`final/round2/supplementary_round2.tex`、`final/round2/response_letter_round2.md`。没有注册的来源工作树，也没有 WIP 提交或未提交状态可审；`SOURCE_READY` 仅针对归档提交内容。
- 相对分支前 main `0f05831d7ae1f853aead2083de8d2409842bd19b`，merge-base 是 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`；来源有 123 个独有提交、726 棵树、1,698 个 blob、675,119,677 字节未压缩 blob 内容，14 个 blob ≥5 MiB（最大 76,043,516 字节）。树差异 2,640 项（A=1,581、M=7、D=1,052），删除当前 253 项 `1008/` 与 353 项 `1009/`，新增 1,256 项旧 `final/round2/` 内容。完整历史不适合合并，未运行 merge 试验。
- 来源 `.gitignore` 会丢失 main 的精确证据/生成物规则；旧 `model_unet_geotex.py` 将 `_skip_correction` 改为类级共享状态，pipeline 也移除 main 的实例状态保存与 `finally` 恢复。保留 main 版本；这些是合并前审查发现的来源差异，不是 Git 冲突。
- 唯一需要保留的独有证据是 MV-Adapter 映射敏感性结果，选择性提交为 `4b76ebc65387b3cbdc526b0ff8aff7ef01273be7`（完整 SHA 见 main 历史），存放在 `1009/evidence/branch_audits/round2_evidence_integrated_20261001/mvadapter_mapping/`。包内 35 条源文件记录逐项映射归档路径及源/目标 SHA-256，另有覆盖 37 个包文件的 `SHA256SUMS.txt`。偏预算中性的 B′（每点倍率均值为 1）结果是混合的：对测试的 global controls，CIEDE2000 与 GT-relative texture interval 有利于 B′，PSNR interval 跨零，FG-SSIM 反向，LPIPS 未定；B′ 与 C 没有指标区分。协议提交先于结果行提交，但它不是独立重复实验。
- 另存的 M3 把每点向量改为 `[0.41953, 0.41953, 1.19349, 1.19349]`、平均总倍率约 0.8065，故同时改变总 residual budget 与分组。协议与结果最早在同一提交出现，预注册时间不能由 Git 独立确认；来源报告的 16/18 稳定分类只能作为回顾性、有限敏感性结果，不与 B′ 混合，也不能支持预算中性映射鲁棒性。适配后的分析器仅读取逐对象 CSV，不运行推理。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。内容提交 `4b76ebc65387b3cbdc526b0ff8aff7ef01273be7` 含 40 个文件（含针对该包 CRLF CSV 的精确 `.gitattributes` 规则）；没有 cherry-pick 或 merge。B′ bootstrap JSON、M3 bootstrap JSON 与 36 行比较 CSV 均与保留的来源输出逐字节一致；3 对象预检中 C 等于 M1，D 与 C 等值。包内 hash 校验、JSON/脚本解析、`git diff --cached --check` 均通过；canonical 1008 submission package 为 48/48。
- `PAPER_IMPACT=DIRECT`：完整历史的远端增量带有旧 Round-2 主文、Supplement 和回复候选，均逐项审阅但没有导入或覆盖当前 1008。新增映射证据不支持普适接口结论，活动稿也没有映射不变性主张。活动主文、Supplement、Response SHA 仍为 Phase A 值 `dd7cb925…73ff4`、`59f0809b…e7ed`、`1fadfc57…974cdb`；活动 LaTeX 与投稿包未改变，因此未重新编译或重建投稿包。`SUBMISSION_APPROVED=NO`，未推送、未投稿。
- Git 冲突：`NO_CONFLICT`，未执行 merge/cherry-pick，实际冲突文件为 0。内容提交后 main 为 `4b76ebc65387b3cbdc526b0ff8aff7ef01273be7`；报告更新将另行提交。


### 14. codex/scientific-validation-v3-20261006

- 来源 HEAD：`12da08c7056f5f0c36677668d640477bfb249454`；archive ref：`refs/archive/codex/main-unification-20261009/local/heads/codex/scientific-validation-v3-20261006`；父提交为已审计的 `codex/final-evidence-freeze-20261001` HEAD `29b3a0a6ec00f5848f1898ffda4fb8e787f81375`。没有注册工作树或可检查的未提交/WIP 状态；`SOURCE_READY` 仅针对归档 HEAD。
- 相对分支前 main `d4277da2dc039c2c3477ca595a8c091df6d4bb1e`，merge-base 是 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`；来源有 126 个独有提交、935 棵树、2,252 个 blob、714,531,802 字节未压缩 blob 内容；14 个 blob ≥5 MiB（最大 76,043,516 字节）。树差异 3,222 项（A=2,125、M=7、D=1,090），删除活动 `1008/` 的 253 项、`1009/` 的 392 项，新增 1,854 项旧 `final/` 内容。完整历史不适合 merge，未运行合并试验。
- 来源最新提交在 `final/round2/scientific_validation_v3/` 下新增 525 个文件、38,943,044 字节；整个发布快照没有被复制。独有且直接支持当前 Supplement A3 交互统计的 4,800 行源指标此前不在 main，因此将其中最小可重现包选择性保存到 `1009/evidence/branch_audits/scientific_validation_v3_20261006/a3_interaction/`。包含 16 个条件 CSV（每项 N=300）、4 个脱敏运行 manifest、归一化规格、校正后 Wald 输出、适配 CSV 输入的 CPU 复现脚本和来源/包内 SHA-256 清单；未复制重复合并总表、图像、GLB、残差日志、模型检查点或其余 503 项快照文件。
- 复核通过：16×300 的对象/条件键完整且无非有限值；条件拆分文件可还原来源 4,800 行 ledger；A3 baseline 与 main 已有 A2 baseline 的 300 个对象非运行时间指标逐项相同，最大差为 0。复算的 cluster-robust Wald 与来源输出所有字段匹配：FG-LPIPS `W=657.237, p=1.1444555792962468e-136`；FG-PSNR `W=1389.118, p=1.2756891492864911e-294`。本包 23 项来源映射和 26 文件 SHA 清单通过。旧 `layermap_dosenorm*.json` 的 zero-power bootstrap 未采用；继续保留 main 已有深层确认、中层近似诊断、浅层 stress-only 的边界。
- 来源代码差异：完整旧树仍将 `_skip_correction` 改为类级共享状态，并移除 pipeline 的实例状态保存与 `finally` 恢复；`.gitignore`/`.gitattributes` 也弱化 main 的精确规则。保留 main 代码/规则；这些是来源审查发现，不是 Git 冲突。实际 Git merge/cherry-pick 均未执行：`NO_CONFLICT`，0 个冲突文件。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。内容提交 `11d39e228ed971ed47493f6c77d43bb391035961` 含 28 个文件（含 A3 数据包与 CRLF 识别规则）。
- `PAPER_IMPACT=DIRECT`：这批原始指标直接复核当前 1008 Supplement 已列的 A3 交互统计；没有发现需要改写结果或限定的差异。活动主文、Supplement、Response、图表与投稿目录均未修改；SHA 仍为 Phase A 三值，canonical 1008 package 48/48。没有 TeX 改动，因此未触发重编译/投稿包重建；`SUBMISSION_APPROVED=NO`，没有 GPU、推送或期刊投稿。
- 报告提交稍后单独生成；内容提交后 main 为 `11d39e228ed971ed47493f6c77d43bb391035961`。


### 15. codex/r1-fidelity-validation-48h-20261008

- 来源 HEAD：`46e741180a2fd539a43234c51f4f3019e346424e`；归档引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/r1-fidelity-validation-48h-20261008`；父提交：`5349b1ce043127eee805fed058f5e0ebdab2454b`。归档 HEAD 没有对应的注册工作树；`/4T/CXY/MV-Painter-r1color` 当前在独立保留的活动 color-cast 分支，未切换或改动。`SOURCE_READY` 仅针对已提交快照；快照记录的历史 untracked 输出不是 WIP commit，未在本轮清理或搬动。
- 相对分支前 main `52a1816e79da82ea0c341416cd3a9bfd4695e7ac`，merge-base 为 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`；来源有 146 个独有提交、996 棵树、3,309 个 blob，未压缩 blob 合计 1,033,343,303 bytes；19 个独有 blob ≥5 MiB，最大 76,043,516 bytes。关闭 rename detection 后，当前树差异为 4,454 个路径（A=3,317、M=7、D=1,130）。来源树带有 2,747 项旧 `final/` 内容，并删除当前活动 1008 主文/Supplement/回复、投稿包及大量 1009 审计文件；完整历史不适合 merge，未启动 merge 试验。
- 来源同时删改当前 `.gitattributes`/`.gitignore` 规则，并包含旧 GeoTex 类级 `_skip_correction` 状态和缺少实例状态 `finally` 恢复的实现；保留 main 的精确忽略/二进制规则和实例级异常安全行为。这些是合并前代码审查差异，不是 Git 冲突。旧 `final_0903` 论文候选和基于它的 R1 回复草稿没有应用。
- 64 文件的来源 48h 包合计 32,239,157 bytes；原始 63 项 SHA-256 清单逐项验证 63/63。仅将 41 个紧凑结果、身份/协议文件和 CPU 分析脚本选择性保存至 `1009/evidence/branch_audits/r1_fidelity_validation_48h_20261008/`，源文件合计 4,779,117 bytes，提交为 `b2c4761afd832cb6f56f2f6826b877ed2b790a30`。新包 43 项哈希检查通过。没有复制 RGB/GT/mask 图像、画廊 PDF、casebook、checkpoint、模型输出或 21,027,044-byte 逐步 residual 表；已明确标为 superseded 的 pixel-pooled CSV也未纳入。旧 color failure 图像集未重复复制；当前 C1/B2 负结果仍由 main 现存的 color-cast 审计和回复信记录。
- Fresh B 每对象表的 150 个 UID 与 main 冻结 UID 列表集合完全相等，和 diagnostic-26 UID 不重叠；150/150 配对行的六类输入张量哈希相等，checkpoint/runner/config 在 cohort 内一致。来源 LLH 行的 PSNR、LPIPS、SSIM、Edge-SSIM 与 main 的 150 个 `layer_llh` 行逐值完全相同。来源 `native_gfl` 与 main 的 `a3_baseline` 不是等价控制，逐对象指标不同，未用后者替代。
- 从已保存对象行复算，Fresh B `LLH-native_gfl` 的 CIEDE2000 为 −1.905396（95% CI [−3.262021, −0.528993]；85/150 更低），FG-PSNR +1.030130 dB（[+0.577497,+1.492532]；77/150 更高），FG-LPIPS −0.015557（[−0.019196,−0.011921]；111/150 更低），GT-relative Laplacian error −0.018712（[−0.020156,−0.017434]；150/150 更低）。GT-defined Q4 `N=38` 的 CIEDE2000 为 +3.624043（[+1.906729,+5.303152]；10/38 更低），FG-PSNR 为 −0.769594 dB（[−1.165334,−0.315401]；7/38 更高），LPIPS 区间跨零。四个 Fresh B 总体指标和三个 Q4 指标的均值、bootstrap CI、方向胜数共 7/7 与保存输出重合；没有重跑图像指标或模型。
- 证据等级限制：`B_VALIDATION_PROTOCOL.json` 写 `locked_at_utc=2026-10-08T22:20:00Z`，但 Git 首次在同一提交 `8f6de4b9…` 中记录协议和全部分析结果的时间是 14:52:59Z，来源称约 14:55Z 已完成。时间记录相互矛盾，Git 不能证明分析锁先于结果检查。因此 Fresh C/B 新 RGB 指标及 Fresh B Q4 结果按回顾性敏感性重分析保存，不视作预注册确认。协议称 bootstrap 固定 seed `20261008`，而脚本/输出按统计项递增种子（Fresh B 总体指标为 `20261028`、`29`、`30`、`33`；Q4 的三项为 `20261250`–`52`）；按保存种子复算区间一致。campaign manifest 也未记录推理包版本。首轮 pixel-pooled 输出明确 superseded，不采用。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY_FOR_ARCHIVED_CONTENT`。没有执行 Git merge/cherry-pick；实际冲突为 `NO_CONFLICT`（0 个文件）。`PAPER_IMPACT=DIRECT`：这批 LLH 与 native-GFL 的 RGB 分析可供 R1 色彩/细节限制讨论，但不是 C3–GFL 结果，也不能证明等剂量效应、普适 schedule winner、物理颜色准确或颜色修复成功。现行 1008 主文、Supplement、Response、图和投稿包未改；源哈希仍等于 Phase A，投稿包为 48/48。没有 TeX 变化，不需重编译。`SUBMISSION_APPROVED=NO`；没有 GPU、历史分支推送或期刊投稿。
- 选择性内容提交后 main 为 `b2c4761afd832cb6f56f2f6826b877ed2b790a30`；本分支审计行将由独立报告提交记录。


### 16. codex/cg-01549-unified-audit-f8ff09d2-20261009

- 来源 HEAD：`f8ff09d26f8214a2eace50e3b568d91a6292576f`，归档引用 `refs/archive/codex/main-unification-20261009/local/heads/codex/cg-01549-unified-audit-f8ff09d2-20261009`。没有注册工作树位于该 HEAD，也没有可恢复的未提交/WIP 状态；`SOURCE_READY` 仅针对归档 Git 树。
- 相对本分支前 main `8f7e82b126f7bec8a511394baa220566c8fce4fb`，merge-base 为 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。来源有 179 个独有提交、24,901 个独有 blob、3,695,897,857 bytes 未压缩对象内容；49 个 blob ≥5 MiB，最大 178,306,395 bytes。关闭 rename detection 后的树差异为 35,050 个路径（A=33,980、M=45、D=1,025），包括 25,548 个旧 `final/` 文件、147 个 `mvpoutput/`、271 个 `archive/` 文件，以及 8,045 项 `1008/` 增加；来源还会删除 main 中 476 项 `1009/` 证据。完整历史不适合 merge，未对当前 main 执行 merge 试验。
- 可复用科研内容已逐项核对：来源的 `FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv`、数值权威重聚合 JSON 和 Fresh B C3−GFH supporting CSV，与 main 中 `cg-ltcas-narrative-convergence` 审计包对应文件 SHA-256 均相同；认证的 01549 `final_0903.tex` 也与 main 的来源文件一致（官方源 SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`）。没有需要再次复制或另建选择性提交的有效唯一结果。
- 来源包含另一版 1008 主文、Supplement、回复信和 author-review PDFs。其 claim matrix 把 Core-7 标成 `CONFIRMATORY / CORE7-SAME-RUNNER`，而现行 main 根据逐条件 runner/input 身份记录将其定为 `RETROSPECTIVE_DIAGNOSTIC`，并明确 runner 与 input-tensor 来源不完整。来源回复信还复述生产 additive-residual bootstrap 的 `p=0.6523`，没有保留该零假设无效、不得用于交互推断的裁决。当前证据矩阵、回复信和受限解释优先；旧候选正文/PDF不导入。`1008` 也含经审阅的旧图件和权利记录，但不替代当前已锁定包。
- 决定：`ALREADY_IN_MAIN; FULL_MERGE_REJECTED; SOURCE_READY_FOR_ARCHIVED_CONTENT`。未 cherry-pick、未执行新的 merge；无新合并冲突。已有来源合并提交 `f8ff09d2` 本身的 11 个历史文件冲突另见冲突报告，不能记作本轮新解决的冲突。未提交源工作树、移动或复制任何原始数据。
- `PAPER_IMPACT=DIRECT`：旧 1008 候选与当前认证版本存在正文/限定/回复差异，但活动主文、Supplement、Response 均未改，SHA-256 仍为 `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`、`59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`、`1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`。当前 `1008/submission_1008/SHA256SUMS.txt` 的 48 项全部通过。未改 TeX、图表或投稿包，因此无需编译/重建；`SUBMISSION_APPROVED=NO`。
- 分支决策后的内容 SHA 仍为 `8f7e82b126f7bec8a511394baa220566c8fce4fb`；本次审计报告提交另行记录。


### 17. detached/cg-closure-clean-audit (`cg-closure-clean-audit`)

- 来源 HEAD：`e267b2d59bbb722827ca5ad72f7ca4475b13c8f1`；归档引用 `refs/archive/codex/main-unification-20261009/detached/cg-closure-clean-audit`。原工作树 `/tmp/cg-closure-clean-audit` 仍 detached 在此 HEAD，tracked/untracked 状态干净，`git diff --check` 通过；没有 WIP 变更，目录未切换或清理。
- 相对分支前 main `1a2b752bce95802aa3c7eab4f6dcdce99e19d708`，merge-base 为 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。来源有 130 个独有提交、966 棵树、2,379 个 blob，未压缩 blob 合计 765,543,177 bytes；14 个 blob ≥5 MiB，最大 76,043,516 bytes。关闭 rename detection 后树差异为 3,425 路径（A=2,245、M=8、D=1,172）：新增 1,858 个旧 `final/` 文件和 116 个 `1006/` 文件，同时删除活动 1008 的 253 项与 main `1009/` 的 476 项。完整历史不适合 merge，未启动 merge 试验。
- 来源 `.gitattributes` 只留 `*.csv` 行尾规则；`.gitignore` 删除当前精选 V3 输入例外及实验生成物精确排除规则，并会恢复旧 `final/` 树。旧 `MVPainter` 还把 `_skip_correction` 改为类级共享变量，并删除实例级状态保存与 `try/finally` 恢复；main 保留隔离的实例标志和异常恢复。这些是预合并代码/规则差异，不是 Git 冲突，均未应用。
- 1006 树中 117 个文件与 main 有 1 个同路径同 blob、另有 31 个 blob 在 main 的其他路径精确存在；包括数值权威、Fresh B/C3−GFH 输出、视觉报告与已选图件。唯一有价值且尚未在 main 保存的记录是 149 条 R1.3 逐句保真措辞审计。已将原 CSV、README 与 SHA 清单选择性纳入 `1009/evidence/branch_audits/cg_closure_clean_audit_20261007/fidelity_language/`，提交 `a92a0bf228181ff4c7ed9c093f4edf24d610ca9c`。149 条分为 132 `REWRITE`、9 `KEEP`、8 `REMOVE`；这是人工证据分类，不是新增实验结果。没有复制源 PDF、候选图像池、最终论文/回复草稿或训练/渲染产物。
- 该逐句审计的 122 条 `final_0903.tex` 引用 SHA 与当前认证 TeX 相同；7 条 Supplement TeX 引用未独立核验。其 20 条辅助 PDF 引用哈希 `5de31993…` 与 main 认证投稿 PDF `fc9cf793…` 不同，因此该 CSV 只作为历史文字审计线索，不作为 PDF 身份或正文权威。当前 1008 已明确变化代理不代表纹理保真；未依据该表改写论文。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。新包 SHA 为 `c8a95e79917e46b365aef6a212c39a054f5fcc08ae61bae837cdaa821b11363f`，149 行和 disposition 计数通过，包内 SHA 清单通过；main 中匹配的权威数值文件逐 blob 核对。没有执行 merge/cherry-pick，因此实际冲突 `NO_CONFLICT`，0 个新冲突；没有运行 GPU 或应用模型代码。
- `PAPER_IMPACT=DIRECT`：旧 1006 主文/回复候选与审计表涉及 R1.3 解释，但都未覆盖认证的 1008。活动主文、Supplement、Response SHA 仍为 Phase A 三值，canonical submission 校验 48/48；没有 TeX/图表/投稿包修改，不需重编译。`SUBMISSION_APPROVED=NO`。
- 内容提交后 main 为 `a92a0bf228181ff4c7ed9c093f4edf24d610ca9c`；分支审计报告提交会另行推进 main。


### 18. detached/01549-clean-checkout-20261008

- 原 HEAD：fb0b24cba203549c28e6287996ad76f4dff61a79；归档引用：refs/archive/codex/main-unification-20261009/detached/01549-clean-checkout-20261008；merge-base：34c77a4417eb3e037756ad483c70ef9e3f0c2bdb。登记工作树 /4T/tmp/01549-clean-checkout-20261008 仍 detached 于该 HEAD；仅有两份被修改的编译 PDF，另有 17 个 ignored 路径（约 20.9 MB）。原件和修改均保留，未清理、移动或复制。没有尚未提交的有效源码；SOURCE_READY 仅针对归档 HEAD。
- 来源历史有 156 个独有提交、1,608 棵树、24,765 个 blob，未压缩 blob 共 3,467,579,504 bytes；36 个 blob ≥5 MiB，最大 178,306,395 bytes。相对处理前 main 6569295e43d1d423299ceb1d9fda22b030206007，树差异为 35,016 项（A=33,912、M=32、D=1,072），包含旧 final/、生成输出及删除当前 1008/1009 路径。完整历史合并被拒绝，未运行 merge 试验。
- 最新来源提交新增 9 项：四份旧恢复审计/计划文档、内容处置表、一个旧 Fig. 1 候选 PDF/PNG 和生成脚本。没有新增有效实验结果或运行时模型修复。旧审稿意见的大部分有效限制已由 main 的 Reviewer 2 对抗审查、01549 reviewer reanalysis、回复信和投稿包覆盖。
- 科学核对纠正了一处来源审稿意见：它称 Fresh C 未与历史 24-object development probe 隔离；当前 Response 与 Supplement 均明确 Fresh C 的 300 个 UID 与原 24-object probe 及原 300-object evaluation 不重叠。当前稿也没有声称 Fresh C 复现旧 checkpoint 的 +0.96 dB 结果。来源关于 SSI 新颖性风险、人工选择 C3、缺少外部复现包及 3D/PBR 证据边界的其余警示，与 main 一致。
- 来源图审阅提出移除 FAC 支路并重画 Fig. 1；当前认证审阅选择保留 SHA 认证的原 Fig. 1 和 FAC 辅助扩展，并通过图注限定 Fresh C 不验证烘焙网格。来源候选图及旧编译 PDF 均未覆盖当前图或投稿包。
- 决定：ALREADY_IN_MAIN; FULL_MERGE_REJECTED; SOURCE_READY_FOR_ARCHIVED_CONTENT。未执行 merge/cherry-pick；代码和论文均为 NO_CONFLICT，实际冲突数 0。无新增内容提交，main 内容仍为 6569295e43d1d423299ceb1d9fda22b030206007。
- PAPER_IMPACT=DIRECT（候选审计与图件被直接审阅，但没有采用或改动活动论文）。主文、Supplement、Response SHA-256 分别为 dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4、59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed、1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb；投稿目录 48/48 校验通过。无 TeX 改动，不需重编译；SUBMISSION_APPROVED=NO。


### 19. codex/cg-round2-1008-public-sanitized-20261008

- 来源 HEAD：`1f2448358537e2b038980496c10a6bb3de532b0f`；归档引用：`refs/archive/codex/main-unification-20261009/local/heads/codex/cg-round2-1008-public-sanitized-20261008`；父提交：`9d5e4ba3ded92e063bb24b036d1b1fd28974feae`；merge-base：`34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。归档 HEAD 没有独立注册工作树。原 scientific-validation 工作树 `/4T/CXY/MV-Painter` 仍在 `5c2c8829a1e19b42837761160dc4c14cf8f09045`，其约 7,212 个已有变化保持原位，本轮未切换、清理、复制或哈希大型数据。
- 相对本分支前 main `73749e74a52b4f0254fd7619fb4d5cae17476985`，来源有 131 个独有提交、1,211 棵树、23,696 个 blob、2,873,713,814 字节未压缩 blob；14 个独有 blob ≥5 MiB，最大 76,043,516 字节。树差异 27,606 项（A=26,443、M=12、D=1,151），其中 25,544 项来自旧 `final/`，745 项在 `1008/`，479 项在 `1009/`；旧 `final/` 快照含 25,324 项历史/生成输出。完整历史不适合 merge，未启动整支 merge 试验。
- 来源 `.gitignore` 会重新放行整个旧 `final/round2` Fresh B campaign 和历史归档树，包含 596,128,347 字节的 5,824 项非图像记录，并弱化 main 当前精确忽略规则；来源树同时删除 1,151 个 main 路径。拒绝整支 merge，也不 cherry-pick 引入全量导入提交。来源 public-sanitized 树不含四份 participant-level CSV；引入这些文件的 `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` 不是来源祖先，相关参与者文件路径在该树中为零。没有改动 public/private 远端引用。
- 审计文档差异也支持保留 main：来源的 `CLAIM_CEILING_REFERENCE.md` 是 2026-10-07 的 d59 版本，早于作者确认的 10-08 轮次/证据修正；其版本把 FAC 从当前修订移除。来源还删掉 01549 手术计划上的“已被 10-08 取代”提示，并缺少 main 10-09 对 aggregate-only human audit 的更新。相关旧说法没有回写；活动 manuscript 与 submission 树在来源版本中也被删除。
- 内容逐项核对：来源 4,500 行 Fresh B 长表与 main 中 `cg_ltc_as_narrative` 数值输入逐字节相同；四个 150 行 late-onset CSV 都是该表的精确条件子集；1,200 行 Generic extension 与 main 现有表按对象/条件键逐字段相同。Fresh B A3b、dose、boundary、Generic 和残差预算的有效总结均已由 main 的已有证据包/报告覆盖，不重复复制。
- 发现一份尚未在 main 保存的 boundary CIEDE per-object 输入。来源完整扩展 CSV 的 CIEDE 列有 150 个配对对象；四个 profile-minus-baseline 均值与来源 `BOUNDARY_SENSITIVITY_ANALYSIS.json` 的差异最大为 `6.7e-16`。同一源 CSV 内的 1,800 个 `logerr_*` 单元与分析定义不一致；来源分析器不读取这些列，而是从已在 main 的长表按 `symmetric_log_error` 重新计算。仅保留分析实际读取且已核验的 CIEDE 列；原 CSV 未改，仍可由归档源引用恢复。
- 选择性证据和逐路径导入清单已提交：`045b4427b9d8bdab4577a4193d4c07b4d32b7a20`，路径为 `1009/evidence/branch_audits/cg_round2_1008_public_sanitized_20261008/`。包含 150 对象的 baseline/四 profile CIEDE 值、边界统计 JSON 和 11,524 行来源导入清单（5,824 copied、5,700 omitted）。清单本身约 3.92 MB；未导入 596 MB campaign、5,700 张图、残差日志、检查点或旧论文/投稿快照。该来源清单明确为 outcome disclosure 后的回顾性完整性记录，不是预先锁定证明。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。实际 Git merge/cherry-pick 均未执行；`NO_CONFLICT`，0 个实际冲突文件。`.gitattributes` 只新增该 CRLF 清单的精确行尾识别规则。选择性提交后 main 内容 SHA：`045b4427b9d8bdab4577a4193d4c07b4d32b7a20`。
- `PAPER_IMPACT=DIRECT`：分支含旧 1008 正文/回复候选和 Fresh B 结果，但当前 C&G 主文、Supplement、Response、图表和投稿包均未更改；现有 boundary report 已包含这些经核验的统计结论。活动三份文本 SHA 仍为 Phase A 值，canonical 1008 投稿包 48/48 校验通过；未改 TeX，无需编译或重建投稿包。数据清单内部计数/路径/哈希格式通过，CIEDE 4/4 profile 均值核验通过，main 现有指标和 Generic 行复用核验通过；无 GPU、无投稿。`SUBMISSION_APPROVED=NO`。


### 20. codex/public-round2-evidence

- 归档来源 HEAD：`78c871ffb4a9906b86b3a0c801d8286607799e3d`；父提交 `d9379fe93e51a5dbf28cc1bfce9bd72b80bdbc48`；归档引用 `refs/archive/codex/main-unification-20261009/local/heads/codex/public-round2-evidence`；merge-base `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`。这是旧 public 仓库曾用的 `origin/main`，没有对应来源工作树；未恢复或改写 public/private 远端引用。`SOURCE_READY` 仅针对归档 HEAD，无新 WIP 或未提交状态。
- 相对本分支前 main `63abee2e9bfb9f0b6076e01240e0e65ecb94db42`，来源有 80 个独有提交、548 棵树、1,282 个 blob、650,449,134 字节未压缩 blob；14 个独有 blob ≥5 MiB，最大 76,043,516 字节。树差异 2,395 项（A=1,194、M=7、D=1,194）；来源新增 945 个旧 `final/` 路径，并删除 253 个活动 `1008/` 和 484 个 `1009/` 路径。来源 `.gitignore` 移除了 main 的精确生成物/证据规则，`.gitattributes` 整份删除。完整历史不适合 merge，预合并阶段拒绝整支 merge。
- 旧 GeoTex 实现将 `_skip_correction` 改成类级共享状态，pipeline 不使用 `try/finally`，也不恢复先前状态；异常或并发调用可能泄漏状态。main 的实例级、异常安全实现保留。`MVPainter/src/data/mvpainter_dataset.py` 与 main 等价；未导入运行时代码。
- 该分支有一套当前 1008 稿件直接使用的 MAIN-STAGE-276 阶段位置结果。对来源记录和 1,104 行统一 CSV 检查后，逐对象值与四份拆分 CSV 及 276 个 JSON 记录完全一致；55,200 个实际残差步骤有限。固定 seed `20260928` 的 10,000 次 paired bootstrap 可从逐对象行精确复现。当前 Supplement S7 的 12 个正式均值/区间均逐项匹配；单独的 PNG 回读 Full-SSIM 汇总也精确复现。来源 acceptance 对 LPIPS 使用有利方向符号，而 Supplement 报告原始 C3−比较组差值；已从逐对象行按 Supplement 方向复核。
- 选择性证据已提交为 `d51834ee65f601d6045dfff3254c0750c666c16b`，位于 `1009/evidence/branch_audits/public_round2_evidence_20260929/`。保存了 276×4 正式逐对象指标、协议/完成/接受记录、PNG 回读 Full-SSIM 数据及统计、来源基线审计，以及覆盖来源阶段目录全部 294 项和来源审计报告共 295 条的逐路径处置清单。省略 8 份精确可还原的 per-schedule 分表、276 份生成 runner JSON 和 3 份短期状态标记；这些来源对象仍可由本地归档引用恢复，没有复制图片、预测、checkpoint 或工作树。
- 当前主文和 Supplement 已将此结果限定为 post-inspection 的同队列辅助分析：C3−temporal L–L–H FG-PSNR 为 `−0.177084 dB`（95% CI `[−0.230539, −0.130784]`），六项正式 endpoint 均有利于 L–L–H；C3−fixed-mean 为 `+0.502875 dB`。未发现需要改写的数值；Core-7 其他记录属于不同收集过程，不与这份 276 运行混合，也不替换 Table S7。此结果不证明等残差剂量因果效应或最优 schedule。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。未运行 Git merge/cherry-pick，因此实际冲突 `NO_CONFLICT`，0 个冲突文件。`.gitattributes` 仅增加新证据目录 CSV 的精确 `whitespace=cr-at-eol` 规则；包内 10 项 SHA-256 全通过。活动主文/Supplement/Response SHA-256 仍为 `dd7cb925…73ff4`、`59f0809…2e7ed`、`1fadfc57…974cdb`；canonical 投稿包 48/48。未改 TeX 或投稿文件，不需编译/重建；`SUBMISSION_APPROVED=NO`。

#### 本次状态刷新

处理前 main 为 `63abee2e9bfb9f0b6076e01240e0e65ecb94db42`，证据内容提交后为 `d51834ee65f601d6045dfff3254c0750c666c16b`。读取 `mvpainter/main` 并执行只读远端查询得到的实际私有远端 main 均为 `52a1816e79da82ea0c341416cd3a9bfd4695e7ac`；补充任务记载的 `93e079ac201d049d9bf36950c7f130ad369008ab` 存在于本地历史且是当前本地 main 的祖先，但当前远端引用没有指向它。远端 `52a1816e` 是 `93e079ac` 的祖先，也是本地 main 的祖先；当前 main 可正常快进远端，但本轮尚未推送。后续按分组收束要求再同步。未删除旧 `gc.log`、未运行 prune/GC；Git 自动维护提示未导致后台 GC 进程。


### 21. backup/geotex-before-cleanup

- 归档来源 HEAD：`61f628bb6a137abab3856a7232cd953770755870`；父提交 `0f892f385c9c5b773e6de341cfc55881f4561816`；归档引用 `refs/archive/codex/main-unification-20261009/local/heads/backup/geotex-before-cleanup`。HEAD 是处理前 main `f959905a90019def362a2a097a75828050d13f0f` 的祖先；merge-base 等于来源 HEAD，main 比来源多 73 个提交，来源独有提交为 0。没有该 HEAD 的注册工作树，因此没有可恢复的未提交/WIP 状态；归档引用和原始数据位置均保留。
- 来源旧树与当前 main 有 1,310 个路径差异（禁用 rename 检测：A=156、M=5、D=1,149），但这是祖先快照与后续 main 树的时间差，不是来源分叉改动。来源独有 Git 对象为 0；没有额外历史 blob 需要导入。旧 GeoTex/PBR 论文与图件、旧训练/评测脚本和配置以及过时源码没有从旧快照重新覆盖当前树。
- 代码核对：来源快照的 `model_unet_geotex.py` / `mvpainter_pipeline.py` 尚无 reference-write 阶段的 skip 状态控制。main 后续版本改为每个 wrapper 独立保存状态，并在 `finally` 中恢复；这一后续实现已经在当前 main，故没有代码补丁需要选择性导入。该具体来源 HEAD 本身没有类级共享 `_skip_correction` 状态；勿与 V3 复现包中另存的旧代码快照混为一谈。
- 决定：`ALREADY_IN_MAIN`；不执行 merge/cherry-pick，不生成空提交。报告前后 main 内容 SHA 均为 `f959905a90019def362a2a097a75828050d13f0f`。实际 Git 冲突数为 0，记为 `NO_CONFLICT`；没有声称冲突已解决。
- `PAPER_IMPACT=INDIRECT`：来源是 GeoTex 实现历史，但不含当前 1008 论文特有的代码或证据改动。当前稿件已把 Fresh C 限定为其冻结 runner/checkpoint 下的受控重训，并明确不把它说成对历史 01549 Table 4 的精确复现；现有 runner/身份审计也将原实现等价性列为部分或未验证。主文、Supplement、Response、图表和投稿包均未改；源文件 SHA 仍为 Phase A 值，投稿包 48/48。无 TeX 变化，不需重编译；未运行模型/GPU。


### 22. new0528

- 归档来源 HEAD：`3f5202cf5ab0846c48dd51e733ee2ae8aa88d359`；父提交 `67c9186cf3a8c9bb8629643b0c622246724e216e`；归档引用 `refs/archive/codex/main-unification-20261009/local/heads/new0528`。该 HEAD 是处理前 main `a91aa45bf8889ee3cbe30ec4db2b16653a5598fd` 的祖先，merge-base 等于来源 HEAD；main 比来源多 91 个提交，来源独有提交为 0。没有对应注册工作树或未提交/WIP 状态。
- 来源 tip 的提交只改了根目录 README：将 Star History 展示段落改为 HTML 注释（2 行增、2 行删）。当前 main 已包含该提交及其后续历史；不需重复补丁。旧快照与当前 main 的 1,264 路径差异（A=21、M=37、D=1,206）属于后续历史演进，不是分叉独有内容；来源独有 Git 对象为 0。
- 决定：`ALREADY_IN_MAIN`；不运行 merge/cherry-pick，不生成空提交。处理前后 main 内容 SHA 均为 `a91aa45bf8889ee3cbe30ec4db2b16653a5598fd`。无代码或论文冲突，均记为 `NO_CONFLICT`；实际冲突文件数 0。
- `PAPER_IMPACT=NONE`：该 tip 只改 README 展示注释，不触及实现、数据、论文、图表或结果生成脚本。活动 TeX/Response 与投稿包未改；无需重编译。


### 23. new0529

- 归档来源 HEAD：`d9379fe93e51a5dbf28cc1bfce9bd72b80bdbc48`；父提交 `50e3248a400eabc6db2bbcf214630c19afadea6a`；归档引用 `refs/archive/codex/main-unification-20261009/local/heads/new0529`。来源没有对应注册工作树或未提交/WIP 状态。相对处理前 main `361c69a5...`，来源有 79 个独有提交、294 棵树、559 个 blob，blob 未压缩合计 584,814,707 bytes；12 个独有 blob ≥5 MiB，最大 76,043,516 bytes。树差异为 1,491 项（A=261、M=7、D=1,223），完整历史不适合 merge。
- 来源最终提交修订了 0907 标记稿：把全量 latexdiff 删除标记转换为 add-only，并替换投稿包中的标记稿 PDF。逐字节核对发现，来源 clean `final_0903.tex` 与 main 已存的 `1008/manuscript/source_01549/final_0903.tex` 同 SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`；来源最终 0907 标记稿 PDF 与 main 已保存的官方 PDF 同 SHA-256 `191d7f379102408852fef5a506f02a3137f32c09781c2489f63650ef243d7aa3`。PDF 未重复复制。
- 从归档对象隔离提取并运行 `strip_difdel.py`：删除组数为 94，正文花括号平衡为 0，输出与来源 `final_0903_marked_addonly.tex` 逐字节一致，SHA-256 `bf6855bc2115564793c979a7c0cd65fb2a7b4994d867f1f37a051a4795616c28`。选择性内容提交 `c46bdac3e5988a9f0103a135a0aba26c3a602833` 在 `1008/manuscript/source_01549/` 保存 full-diff 输入 TeX、add-only 输出 TeX、转换脚本及 SHA/来源说明，合计三项源码 225,986 bytes；没有改 clean 原文、当前 1008 稿件或投稿 PDF。
- 排除 79 个提交的其余历史树和 584.8 MB blob 历史，包括 76,043,516-byte 旧 zip、9 个训练 checkpoint、旧论文 PDF、全量删除标记 PDF及旧生成输出；所有源对象仍可经本地 archive ref 恢复。
- 决定：`SELECTIVE_CONTENT_MERGE; FULL_MERGE_REJECTED; SOURCE_READY`。没有执行 merge/cherry-pick，因此实际代码/论文冲突均为 `NO_CONFLICT`，冲突文件数 0。新存的 historical source 只服务于已认证的 0907 标记稿；不把它覆盖到 1008。新 add-only TeX 保留源字节，Git whitespace 检查标出其中 3 行原有尾随空格，未为保持 hash 而做格式改写；其余提交文件通过检查。投稿目录 SHA256SUMS 48/48，活动三份源文件哈希不变；不需重编译、无 GPU、无投稿。`SUBMISSION_APPROVED=NO`。


### 24. codex/round2-evidence-integrated-20261001 — local ancestor snapshot

- 本地归档来源 HEAD：`ce4831f40c723631e395f86268dca13afe9d07e9`；父提交 `2618d15099092312922d87420fad4bf545c71d73`；引用 `refs/archive/codex/main-unification-20261009/local/heads/codex/round2-evidence-integrated-20261001`。该归档 tip 无注册工作树或 WIP。其 merge-base 为 `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`，有 118 个来源独有提交、711 棵树、1,693 个 blob、674,959,480 bytes 未压缩 blob；14 个 blob ≥5 MiB，最大 76,043,516 bytes。与当前 main 的树差异为 2,787 项（A=1,581、M=7、D=1,199）。
- 该 HEAD 是已审的私有远端同名归档 HEAD `5a059b30eba959e69a2f36f484f06807e5c2c152` 的直接祖先；后者只比本地 tip 多 5 个提交，且这 5 个提交只修改旧 `final/round2/` 的主文、Supplement 和回复信候选。后者的全量来源及这些旧论文版本已在第 13 项逐项审阅；独有审计文件在后继提交中未改。
- B′ 与 M3 的有效协议、结果、reproducer 和校验包已由后继来源选择性提交 `4b76ebc65387b3cbdc526b0ff8aff7ef01273be7` 纳入当前 main；其回顾性协议锁边界和 M3 预算变化限制仍适用。该本地祖先引用无额外内容需要再次导入；旧论文/回复树和生成结果沿用后继来源处置，不整支合并。
- 决定：`ALREADY_AUDITED_AS_ANCESTOR`；不重复 merge/cherry-pick、不造空提交。处理前后 main 内容 SHA 均为 `384e3f66c3cfaca6a9073481b63618093117c12a`。实际代码/论文冲突均为 `NO_CONFLICT`，0 个文件；当前 1008 文本和投稿包未改。
- `PAPER_IMPACT=DIRECT`：来源树中有历史论文候选，已由其后继归档审查并排除；当前 1008 主文、Supplement、Response 和 canonical submission 保持不变，投稿包 48/48。无新的数值/代码证据需改变结论；不需重编译。


### 25. codex/cg-01549-surgical-upload-20261008 — identical archived HEAD

- 本地归档引用 `refs/archive/codex/main-unification-20261009/local/heads/codex/cg-01549-surgical-upload-20261008` 指向 `dad08320625431acf439ed5bfb86c6a9252353a4`，与第 1 项已审 private-remote surgical-revision 来源 HEAD 完全相同。对应 detached 工作树 `/tmp/MVPainter-cg01549-private-upload` 的 tracked/untracked 状态干净；既有处置记录中的 38 个 ignored 项仍在原位，本轮未改动。
- 因为是完全相同的提交对象，其 155 个独有提交、1,329 棵树、23,853 个 blob、2,993,693,628 bytes 和 22 个 ≥5 MiB blob，均已包含在第 1 项审计范围内。针对 A3b/dose 与 Generic extension 选择的内容提交 `107e1aa8f89d048df11393085da2b8cc8b7e2b37` 已在 main；历史论文候选、生成产物与类级共享状态实现沿用该项的排除裁决。
- 决定：`ALIAS_OF_AUDITED_SOURCE`；无新增选择、无重复合并。处理前后 main 内容 SHA 均为 `89acc6de9552d378eebd9e5f88e7a440662565f3`。无新的代码或论文冲突，记为 `NO_CONFLICT`；当前 1008 论文和投稿包不变。
- `PAPER_IMPACT=DIRECT`，但完全继承已审 surgical-revision 来源的论文裁决；没有独立论文改动需要应用。

### 27. codex/next-review-response-20260930（活动跨骨干实验分支，只读）

- 来源 HEAD：4f312566ed42a7b56fae9f11d91d4591d71fd1f2；本地活动分支和私有远端分支当前均指向该 SHA。归档引用包括 local 与 mvpainter 两个别名。该来源没有登记的工作树，也没有可由该 ref 恢复的 WIP；SOURCE_READY 仅指归档 HEAD，活动分支按第四组继续保留，不退出或改写。
- 相对 merge-base 34c77a4417eb3e037756ad483c70ef9e3f0c2bdb，来源有 102 个独有提交；独有对象为 590 棵树、1,440 个 blob、656,629,803 bytes，14 个 blob ≥5 MiB，最大 76,043,516 bytes。关闭 rename detection 的树差异为 2,535 项（A=1,322、M=7、D=1,206）。有较大的历史模型/生成资产，因此不执行整支 merge；更直接的原因是它仍是需要独立使用的活动实验分支。
- MV-Adapter 的预注册 layer-wise 76-object 试验新增 228 条 L-FIX/L-LHL/L-LLH 记录。三份逐对象 CSV 与 main 已保存的 M1 输入逐字节相同：L-FIX SHA-256 99e7ff4f639b75fe618be839cd329e03f11081ae8c0f0c4eb368d841d0aeff6e，L-LHL 1846eb6578d442b145894d123bc13d125608119443ab774b50776a57c7e16e87，L-LLH 0e4f80e478e344fe5d27af894f2867a66f91bf96de593d551a9feab27d52d14a。main 的 M1/B′/M3 审计包已保留这些 M1 原始行及不同映射的后续敏感性；该来源原始预注册方案、layer profile、完整 P1–P5 bootstrap 和 76-object 结果报告仍作为活动来源保留，不重复导入。
- MVDiffusion 75-object panel 的审计、结果 CSV、paired bootstrap、报告及六个条件逐对象 CSV 已在 main 有逐字节相同版本。来源独有的 SD2-depth mirror 下载/来源记录不改变 75-object 面板数值；不复制大型模型资产或输出。
- 决定：KEEP_ACTIVE_READ_ONLY；不执行 merge/cherry-pick，不更改当前分支及私有远端引用。没有清理、移动或复制任何工作树或科研数据。该分支的 layer-wise 结果报告为指标依赖的组间差异（PSNR、dE00、GT-texture 支持 layer-wise，FG/Edge-SSIM 略支持 global，LPIPS 未分离）；冻结尺度下 temporal-position effect 未获支持。MVDiffusion 的 layer-wise 结果为混合/负向，且不进行跨骨干绝对分数合并。
- 冲突：代码和论文均为 NO_CONFLICT；因为本分支按要求只读，未执行 merge/cherry-pick，因此实际 Git 冲突为 0，没有冲突被“解决”。
- PAPER_IMPACT=DIRECT：该 76-object MV-Adapter layer-wise 分析对跨骨干范围有直接参考价值；当前 1008 正文写有原 98/99-object MV-Adapter probe 和 MVDiffusion 75-object probe，但没有报告这组 76-object layer-wise 面板。它支持指标依赖的 MV-Adapter 内部响应，不支持普遍增益或唯一时间位置。当前稿“未建立一般跨骨干改进”的边界仍成立，但若后续论文纳入跨骨干层级调制结果，应对这组结果作针对性审阅；活动实验分支未收束前不改稿。
- 验证：main 中三份 M1 原始 CSV 的 SHA-256 与分支完全相同；MVDiffusion 核心面板文件逐字节一致。活动主文 SHA-256 为 dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4；Supplement/Response 与 Phase A 值一致；投稿包 SHA256SUMS 48/48 通过。未改 TeX、图表或投稿包，不需重编译；未运行 GPU 实验。SUBMISSION_APPROVED=NO。
