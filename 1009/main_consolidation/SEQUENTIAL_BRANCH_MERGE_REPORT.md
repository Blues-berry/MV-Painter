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
