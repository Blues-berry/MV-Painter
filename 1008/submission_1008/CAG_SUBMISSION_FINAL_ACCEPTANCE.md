# Computers & Graphics 1008 二轮修订交付状态

**更新日期：** `2026-10-10` · **状态：** `AUTHOR_REVIEW_READY / DRAFT`  
**期刊投稿：** 未提交 · **投稿批准：** `SUBMISSION_APPROVED=NO`  
**本轮 main 起始基线：** `815ab0f70bf408e2d3e2a1b76ce366ec5829c41f`

## 本轮完成

- 重写活动主文，收窄 TCAS 的创新主张，定义 requested/applied/residual 语义，并同步 Supplement 与逐条回复信。
- 重绘 Figure 1 为可复现的矢量控制路径图，直观显示 requested scale 经 native cap 后缩放 GeoTex residual 并注入 frozen UNet；01549 原图仍原样保存在 source baseline。
- 保留 Fresh C 的正向配对结果和 GFH、Generic Linear 均值反例；将 applied-scale 剂量差、strict-276 的 L–L–H 结果及其 post-inspection、dose 不匹配限制写入主文。
- 把偏色诊断、跨接口汇总、FAC/人评边界放入相应结果与限制；撤回 CAI 证明和最优性结论。新增的 76-object MV-Adapter layer/time 面板按回顾性接口敏感性处理；MVDiffusion native-mirror 检查仅覆盖一个对象，不代表完整面板重跑。
- 交付主文 16 页、标注稿 16 页、Supplement 15 页、回复信 PDF 4 页及横向一页风险/实验决策表。
- 62 项确定性源码 ZIP 在空目录中重建三份 LaTeX PDF；页数和提取文本与审阅副本一致，最终日志无悬空引用。

## 尚未解决

- R1.1：没有通过门禁的 Fresh C 烘焙、seam 或 PBR 结果；颜色修复未验证，native-default 路径没有独立对照。
- R2.1：SSI 等工作已研究 layer/time scheduling，TCAS 仍有创新性充分性的编辑风险。
- R2.3：MV-Adapter 与 MVDiffusion 探索使用不同接口；76-object layer/time 面板的方案与结果同 commit 首次出现，MVDiffusion mirror 检查仅覆盖一个对象，仍没有匹配的跨骨干验证。
- 留存审稿 PDF 标为 initial submission；需作者对照二轮决定确认回复标题。现用 Figure 6 的 CC BY 4.0 授权、UID、样本选择记录和图像哈希已核验；旧历史图仅保留在 01549 源文件中。
- 题名页、作者/资助信息、利益声明和上传草稿仍需作者审核。

## 实验决策

没有启动 GPU 实验。单独的 applied-budget CPU preflight 通过了 50 步配置算术检查，但等 applied-scale 总和不等于 realized residual dose；GPU 空闲门禁失败，未运行推理，历史 base-model 目录也没有内容哈希。快照仅供作者审计，见 `Author_Review/Applied_Budget_Preflight_20261010/`。若只能补一个实验，优先考虑 E1，但须先对未修改的原始输入通过 CPU preflight；门禁失败即停止，不替换资产或修复输入。E2、E3 当前均 no-go。

完整哈希、构建记录和逐项风险见 [`FINAL_CG_SUBMISSION_READINESS.md`](FINAL_CG_SUBMISSION_READINESS.md) 与 [`Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md`](Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md)。本地审阅包已组装，但不代表作者批准或实际投稿。

`SCIENTIFIC_EVIDENCE_FREEZE = YES`  
`REVIEWER_RESPONSE_READY = PARTIAL`  
`MANUSCRIPT_BUILD_PASSED = YES`  
`SUBMISSION_PACKAGE_COMPLETE = YES`  
`SUBMISSION_APPROVED = NO`
