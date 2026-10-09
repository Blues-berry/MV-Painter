# Computers & Graphics 1008 二轮投稿最终验收

**状态：** `DRAFT / AUTHOR REVIEW READY`  
**投稿批准：** `SUBMISSION_APPROVED=NO`  
**投稿状态：** 尚未向期刊上传  
**验收日期：** 2026-10-09 UTC

本文以 2026-09-07 已完成第一轮修订的正式稿 01549 为基线，处理当前第二轮 R1/R2/R3。01549 原始 TeX 保持不变。

## 修订后的研究主线

论文保留 **TCAS（Timestep-Conditioned Adapter Scaling）**，将 C3 `(1.25, 2.50, 1.25)` 定位为现有 GeoTex-Adapter 残差上的任务特定、免训练推理干预。Fresh C 的 300 个配对对象中，C3 相对 GFL 的 FG-PSNR 差为 `+0.522352 dB`，对象级 bootstrap 95% 区间为 `[+0.404160, +0.640669]`。同时，GFH 与 Generic Linear 在四项展示队列均值上均优于 C3；C3/GFL 的 deep 与 middle 累积 applied scale 也不同（各为 `82.5` 对 `62.5`），因此该比较不能单独解释为纯时间调度效应。

独立阶段位置跟踪实验中，Temporal L–L–H 在六项正式端点上均优于 C3；C3 相对 Fixed 的平均 FG-PSNR 为 `+0.502875 dB`，相对 Temporal L–L–H 则为 `−0.177084 dB`。这些结果支持有限的时间位置敏感性，不支持 C3 是普遍或剂量匹配条件下的最优控制。论文把纹理变化指标限定为变化诊断，不把它们称为纹理保真，也不声称已解决图像到 3D 材质的颜色与接缝问题。TCAS 与 SSI 的比较承认一般性 layer/time scheduling 并非新问题，贡献范围限于该任务、残差接口及其配对图像空间分析。

## 第二轮逐项状态

| 意见 | 状态 | 处理与剩余边界 |
|---|---|---|
| R1.1 | `PARTIAL` | Fig. 4/5 已改为真实的 Reference、GFL、GFH、C3、固定尺度与 Generic Linear 对照；完整多条件图留在 Supplement。原生默认 Adapter 路径没有 Fresh C 输出；有效 Fresh C bake、seam、PBR 结果缺失，颜色/纹理保真问题仍开放。 |
| R1.2 | `ADDRESSED WITH LIMITS` | Fresh C N=300 为同协议配对图像空间验证并报告强基线反例；它不是历史 `+0.96 dB` 结果的数值复现。Core-7 只作为回溯性 Supplement 诊断。 |
| R1.3 | `ADDRESSED WITH LIMITS` | 文中区分纹理变化与纹理保真；旧 3AFC 仅保留为其原条件下的主观偏好证据，不升级为 Fresh C、参考保真或 3D 质量证据。 |
| R1.4 | `PARTIAL` | 表 4 报告配对区间及 C3–GFH Edge-SSIM 取舍；未预设非劣效界值，因此不声称等效或非劣。 |
| R1.5 | `PARTIAL; FIRST-ROUND RESULT RETAINED` | 保留 01549 第一轮 FAC 负结果并披露来源限制。恢复的配置清单指向 1,200 而非正文所述 1,706 个训练对象，且 seed、输出和运行时未由单一 manifest 绑定；没有声称本轮重跑或公开发布代码。 |
| R2.1 | `PARTIAL; NOVELTY RISK` | 明确 SSI 与 TCAS 的任务及残差接口差异，撤回一般性新调度算法的暗示，并承认任务特定贡献能否达到期刊创新门槛仍由编辑判断。 |
| R2.2 | `ADDRESSED` | 删除 CAI 的 selector、命题、证明与最优性主张；保留 TCAS 和标注为历史开发证据的 C3 记录。 |
| R2.3 | `NOT FULLY ANSWERED` | 删除无效的 production additive-residual bootstrap 推断；报告事后 exploratory object-cluster robust Wald 分析和四指标 Holm 校正。结果不证明交互不存在；MV-Adapter 与 MVDiffusion 路径不是共享接口的匹配跨骨干验证。 |
| R3 | `ACKNOWLEDGED` | 致谢正面评价；未虚构新增技术要求。 |

R1.1、R2.1 和 R2.3 仍有可能影响录用的开放问题；以上状态不表示审稿人已接受这些答复。

## 科学限制与本地颜色诊断

当前稿仍披露紫色/冷色偏移、重复或不匹配纹理、缺少原生默认 Adapter 对照、未通过的 Fresh C 烘焙入口，以及没有有效 Fresh C bake、seam、PBR 结果。Fresh C 未提供可验证的跨骨干统一接口比较；C3 与 GFL 的应用剂量不同；C3 创新性仍有编辑风险。

r1color 工作树中的四对象 Phase B/C 开发诊断与 C1 候选未用于论文结论。已知 C1 的数值门通过、但两个偏色失败案例未通过预先锁定的人工视觉门，因此没有进入 Fresh B。随后完成的 CPU-only 输入身份核对显示 Fresh B 条件输入与既有生成输入在 150/150 对象上匹配，而缓存 embedding 在 0/150 上匹配；四个开发对象的锁定 magenta-residual 比率均值为 GFL 源视角 1.24%、未见视角 1.34%。GFL 对 GT 的对象级颜色分布差异仍较大，但这些小样本、未配准分布读数不能定位偏色发生环节，也不能证明感知保真或完整根因，未改变论文结论。相关运行、图像与诊断保留在本地 r1color 工作树，不随投稿包或主分支上传；完整处置见仓库的 `1009/main_consolidation/COLOR_REPAIR_CAMPAIGN_REVIEW.md`。

后续锁定的 B2 raw-source embedding 提案计划在四个开发对象上进行八次调用。先前记录的三次启动尝试均在扩散生成前停止。其后，另一并发工作流把 r1color 分支推进并推送了两笔 handoff 提交，HEAD 从 `bd9d436c2f13c00de36a64cb42e807da558ef5c4` 变为 `32bb9106fa0ea6199e6a16f9279343c0b21581a6`，共涉及 18 个变更路径（其中 6 个此前未列入分支提交清单）。本次验收未读取这些提交内容。提交的 `.gitignore` 规则下，先前清单中 856 个未跟踪路径（166,583,423 字节）现在被识别为 ignored；逐项确认这些文件仍存在且字节与上一份 SHA-256 清单一致，其中包括 B2 attempt/evidence 命名文件。本次验收只核对路径、Git 状态和哈希，没有打开其中的指标、图像或 verdict；当前调用数、完成状态和结果均未核实，也未用于论文或回复信结论。相关文件留在本地 r1color 工作树，颜色修复仍未通过本次验收。

第二轮 reviewer 原始文本存在来源缺口：定向核查了保留的 unified、surgical、color、V3 和 round-two evidence 分支；审稿 TXT 与 PDF 在 23 个本地分支引用中内容一致，PDF 明确标注为初始投稿评审（PDF SHA-256 `fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb`，TXT SHA-256 `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5`），不是已认证的第二轮 R1/R2/R3 原文。因此，逐项回复和页面定位已按当前审稿要求矩阵及修订证据核对，但第二轮意见的逐字来源认证仍未完成。

## 构建与文件验收

- 主文 PDF：13 页；Supplement：11 页；Response：5 页；marked-up manuscript：13 页；Response 加主文便览 PDF：18 页。
- 主文与 Supplement 的活动 TeX、作者审阅副本和源 ZIP 成员逐字节一致。源 ZIP 有 44 个条目并通过 CRC；不含 JSON、NPZ、checkpoint 或 GLB 数据。
- 从空目录解压源 ZIP 后重新构建主文、Supplement 和 marked-up PDF，分别为 13、11、13 页；提取文本与交付 PDF 在忽略排版换行后相符。LaTeX 日志无致命错误、未解析引用或文献。
- 页面复核：主文表 3/4 在第 7 页，Fig. 4/5 在第 11/12 页；Supplement Fig. S1 在第 9 页。审稿回复位置映射见包内 `Author_Review/REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv`。
- 详细 TeX 哈希、PDF 哈希、源 ZIP 哈希及干净解压重建记录见 `1008/submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md`。新增本验收报告后，包内 `SHA256SUMS.txt` 与 `SUBMISSION_FILE_MANIFEST.csv` 一并刷新。

## 作者确认事项

以下文件仍是草稿或 0907 沿用材料，上传前必须由作者核实：题名页中的作者及联系信息、基金和致谢、利益声明；Cover Letter、Research Highlights、Graphical Abstract；0907 会议稿附件是否仍要求提交；当前期刊对图形摘要及演示媒体的格式要求；最终 manuscript ID 与编辑部说明。0907 行政材料在目录中单独标记为 carry-over，没有当作新批准声明。

## 可打开的交付文件

- 活动主文 TeX：`1008/manuscript/revision_01549_restored/manuscript_1008.tex`
- 活动 Supplement TeX：`1008/manuscript/revision_01549_restored/Supplementary_1008.tex`
- 主文 PDF：`1008/submission_1008/Manuscript_1008.pdf`
- Supplement PDF：`1008/submission_1008/Supplementary_1008.pdf`
- Response PDF：`1008/submission_1008/Response_to_Reviewers_1008.pdf`
- 完整本地投稿目录：`1008/submission_1008/`
- 私有 GitHub 投稿目录：[Blues-berry/MVPainter — 1008 submission](https://github.com/Blues-berry/MVPainter/tree/main/1008/submission_1008)

## 最终状态门

| 状态门 | 结果 | 说明 |
|---|---|---|
| `MAIN_SINGLE_EDITING_AUTHORITY` | `PARTIAL` | `/4T/MV-Painter-main` 是指定的日常编辑树；旧工作树保留，无法检查编辑器当前打开目录，需在编辑器打开该路径。 |
| `UNIQUE_LOCAL_CHANGES_ACCOUNTED_FOR` | `YES` | 非 main 脏/未跟踪状态按路径、状态、SHA-256 和来源逐项记录；旧数据目录保留。 |
| `VALUABLE_SOURCES_INTEGRATED` | `PARTIAL` | 准确的 unified Response 段落已用于重写；冻结 V3 来源已在 main；尚无通过视觉门的颜色修复，其他历史实验未整支合并。 |
| `BULK_DATA_PRESERVED` | `YES` | 没有删除旧工作树、原始实验数据或 stash；没有把大规模实验图像、缓存或 checkpoint 加入本投稿包。 |
| `REVIEWER_RESPONSE_CONSISTENT` | `PARTIAL` | PDF 页码和现有图表已核对；第二轮 reviewer 原文未完成逐字认证。 |
| `SCIENTIFIC_DIRECTION_ERRORS_FIXED` | `YES` | 已纠正阶段位置方向，Fig. 4/5 描述按真实内容改写，撤回无效 `p=0.6523` bootstrap 推断。 |
| `LATEX_BUILD_PASSED` | `YES` | 活动 PDF 与干净源 ZIP 解压重建均通过，页数及文本一致性已记录。 |
| `SUBMISSION_PACKAGE_COMPLETE` | `YES` | 主文、Supplement、回复、标注稿、图像、源 ZIP、行政 carry-over、作者审阅材料、清单与校验和均在包内。 |
| `PRIVATE_MAIN_SYNCED` | `YES` | 内容按授权以普通快进推送至私有 `mvpainter/main`；当前完整 SHA 在本次交付说明中报告。 |
| `SUBMISSION_APPROVED` | `NO` | 尚未获得作者投稿批准；没有向期刊上传。 |
