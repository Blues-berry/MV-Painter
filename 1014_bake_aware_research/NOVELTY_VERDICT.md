# Novelty verdict

## 判断

**本次没有形成可称为新方法的 BAVGC 实现。** 独立实现的六视角预算投影和 tile scaling 是一个接口/约束投影工具；它没有反馈策略，不产生方法证据。

潜在方法差异可以写成“烘焙后表面反馈驱动的 per-view geometry residual reallocation”。但要把它与已有方法区分开，必须同时证明：

1. 表面信号在对象外推中可靠预测实际未见 bake LPIPS；
2. 预测能给出具体每视角动作，而不只是挑选现成静态调度；
3. 在同预算、同计算量无反馈基线之上仍带来有意义质量收益；
4. 与 MD-ProjTex/TexFusion 的 UV 反馈融合、Scheduled Style Injection 的层/时间条件调度、RomanTex 的 3D-aware guidance 和 GeoDiffuser 的反馈闭环有明确运算差别。

这四项均未在本次建立。信号审计反而发现 UV 方差对主要感知端点近随机，组合信号更弱；因此当前的新颖性不能靠接口代码或名称成立。

## RomanTex 和 GeoDiffuser 的开放核查

本次依据可访问的摘要/元信息仅能确认 RomanTex 涉及 3D-aware positional encoding、多注意力和几何相关 CFG；未获得可检索的论文全文公式来确认是否有与 BAVGC 相同的方向投影，故不做等价断言。GeoDiffuser 的出版方全文也未能取得；其可见介绍与反馈闭环概念相邻，具体 operator 和成本需先读全文/代码。这个缺口增加不确定性，不能当成新颖性的正面证据。

## 建议用语

当前只可称为“对 bake-aware view-adaptive geometry control 的可行性审计和接口原型”，不宜描述为 BAVGC 方法、算法贡献或已验证的自适应控制。即便以后获得 GO，也仅表示值得开展独立确认，不等于适合并入当前论文或可以投稿。
