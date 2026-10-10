# Computers & Graphics 1008 二轮修订交付状态

**更新日期：** `2026-10-10` · **状态：** `AUTHOR_REVIEW_READY / DRAFT`  
**期刊投稿：** 未提交 · **投稿批准：** `SUBMISSION_APPROVED=NO`  
**本轮 main 起始基线：** `245bcafd41d6022aa529080d5a02fc8e1fdfedff`

## 本轮完成

- 重写活动主文，收窄 TCAS 的创新主张，定义 requested/applied/residual 语义，并同步 Supplement 与逐条回复信。
- 保留 Fresh C 的正向配对结果和 GFH、Generic Linear 均值反例；将 applied-scale 剂量差、strict-276 的 L–L–H 结果及其 post-inspection、dose 不匹配限制写入主文。
- 把偏色诊断、跨接口汇总、FAC/人评边界放入相应结果与限制；撤回 CAI 证明和最优性结论。
- 交付主文 16 页、标注稿 17 页、Supplement 13 页、回复信 PDF 6 页及一页风险/实验决策表。
- 45 项源码 ZIP 在空目录中重建三份 LaTeX PDF；页数和提取文本与审阅副本一致，引用无悬空。

## 尚未解决

- R1.1：没有通过门禁的 Fresh C 烘焙、seam 或 PBR 结果；颜色修复未验证，native-default 路径没有独立对照。
- R2.1：SSI 等工作已研究 layer/time scheduling，TCAS 仍有创新性充分性的编辑风险。
- R2.3：MV-Adapter 与 MVDiffusion 探索使用不同接口，没有匹配的跨骨干验证。
- 留存审稿 PDF 标为 initial submission；需作者对照二轮决定确认回复标题。历史 Figure 6 素材的授权及 panel map 仍需作者确认或替换。
- 题名页、作者/资助信息、利益声明和上传草稿仍需作者审核。

## 实验决策

没有启动 GPU 实验。若只能补一个实验，优先考虑 E1，但须先对未修改的原始输入通过 CPU preflight；门禁失败即停止，不替换资产或修复输入。E2、E3 当前均 no-go。

完整哈希、构建记录和逐项风险见 [`FINAL_CG_SUBMISSION_READINESS.md`](FINAL_CG_SUBMISSION_READINESS.md) 与 [`Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md`](Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md)。本地审阅包已组装，但不代表作者批准或实际投稿。

`SCIENTIFIC_EVIDENCE_FREEZE = YES`  
`REVIEWER_RESPONSE_READY = PARTIAL`  
`MANUSCRIPT_BUILD_PASSED = YES`  
`SUBMISSION_PACKAGE_COMPLETE = YES`  
`SUBMISSION_APPROVED = NO`
