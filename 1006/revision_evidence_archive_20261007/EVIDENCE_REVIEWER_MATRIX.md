# 证据状态与审稿意见对照表

依据 `source/reviewer/reviewer_comments_supplied.txt`。审稿人原文的日期和 “Initial submission” 标签按原样保留；本表不推断额外的审稿轮次。状态表示本次**非人工**证据归档后的证据情况，不表示主稿已经完成修改。

| 审稿意见 | 对应的已核验非人工证据 | 当前状态 | 后续主张边界（本次不改主稿） |
|---|---|---|---|
| R1.1 全物体外观、unmodified/fixed-scale baseline、unseen baked views、seams | Fresh C 20 组/300-object 图像比较索引；N=24 GLB claim 已退休；历史 N=20 仅 unlit base-color；seam claim 已退休。 | **部分回应 / 需收窄** | 限定为图像空间对照图和指标；不声称新 N=24 3D、PBR、seam 或人类感知优越。
| R1.2 probe-disjoint 276 上验证 main adapter | 新 Fresh C N=300 四条件主比较支持 C3−GFL FG-PSNR +0.522 dB；strict-276 C3−GFL +1.208 dB 是回溯性支持，但旧输入/runner lineage 不完整。 | **部分回应 / 仅限回溯** | 不把 strict-276 写成独立确认，不称旧 pooled +0.96 dB 获得了严格独立复制。Fresh C 明确标为 revision-era 新 cohort。
| R1.3 texture variation 不等于 texture fidelity | 已有图像复杂度/纹理指标与 visual audit 只能说明这些指标的响应；它们不能验证感知保真。人工答卷及其分析不在本次范围。 | **未闭合的 claim boundary** | 只说指标变化/纹理复杂度；从本阶段证据中不推出 faithful texture 或人类偏好。
| R1.4 CI 跨零不能证明等效；报告 Edge-SSIM trade-off | Fresh C 主/附录的 endpoint-specific intervals、favorability 和 Holm 家族已逐项复核；无非劣效界值。 | **可按 claim reduction 回应** | 报配对区间和指标取舍；不能把不显著写成等效/非劣。
| R1.5 FAC 可复现性与代码开放 | 历史 compact bundle 的分析/排版 rebuild 只在已包含范围通过；当前最终候选没有通过 clean-checkout 重建。 | **未闭合** | 不宣称当前 submission package 已可重现或已发布；需先有干净候选和完整重建记录。
| R2.1 方法贡献有限、schedule selection novelty | R2.1 adversarial audit 将 SSI 作为 layer/time scheduling 先例；Fresh C 和执行账本支持的是 MVPainter 实现范围的测量结果。 | **OPEN / VENUE RISK** | 贡献限定为实现感知的实证刻画；不主张首创 schedule/control space 或已证最优算法。
| R2.2 CAI 后验解释 | CAI audit：无 prospective prediction test、无唯一 selector。 | **可按 claim reduction 回应** | CAI 仅 descriptive vocabulary，或移出核心贡献。
| R2.3 缺少跨 backbone 泛化 | MV-Adapter、MVDiffusion 各自有边界数据，但 cohort/接口不同且结果不支持普遍迁移。 | **有限补充 / 不支持广泛泛化** | 分开报告接口特定结果；不池化、不推断 architecture causality，也不再扩第三骨干。
| R3 修订稿看起来适合发表 | R3 原文为正向评价。 | **无新增可执行问题** | 该意见不替代 R1/R2 未闭合项。

## 统一结论

R1 的 3D/seam/感知保真主张需要收窄；R1.5 当前 clean rebuild 仍未闭合；R2.1 是主要 venue risk。CAI 和跨骨干结论均只能按限定范围回应。此矩阵是证据映射，不是最终回复信，也不是主稿修订。
