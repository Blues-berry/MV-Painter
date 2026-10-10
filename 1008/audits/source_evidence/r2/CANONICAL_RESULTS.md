# 唯一采用的结果与边界

本页是本次归档的结果汇总。遇到旧版结果、不同 cohort 的估计或图表冲突时，按本页的证据等级和逐字副本中的来源哈希处理；不跨 cohort、runner、seed、cap 路径或端点合并排名。统计单位按原 protocol 保持为 object。

## 主结果：Fresh C 图像空间比较

- 冻结 N=300；四条件 `no_adapter / GFL / GFH / C3` 完成 1,200/1,200 行，完整性门禁 PASS。
- 唯一注册主端点为 C3−GFL FG-PSNR：均值 **+0.522 dB**，对象 bootstrap 95% CI **[+0.404, +0.641]**，68.7% 对象有利于 C3。
- 次要端点包括 FG-LPIPS −0.005345 [−0.006326, −0.004403]，Edge-SSIM +0.004494 [+0.003411, +0.005586]。端点应分别陈述；这些图像指标不能推出人类感知保真或总体 3D 质量。
- 结论限定为该冻结 cohort、当前 MVPainter 执行路径和图像空间指标。均值不代表典型对象一定获益，也不构成跨指标综合赢家。

## 同 cohort 修订附录：LLH 与 generic linear

- `layer_llh / gen_linear` 在同一冻结 N=300 上完成 600/600 行；独立完整性门禁 PASS。它与原四条件比较分开报告。
- LLH−C3：FG-PSNR +0.621 dB [0.391, 0.855]，但中位数 −0.153 dB、46.7% 对象有利于 LLH；FG-LPIPS −0.01214 [−0.01386, −0.01048]，75.0% 对象有利于 LLH。均值和对象分布并不一致。
- LLH−generic linear：FG-PSNR +0.0276 dB [−0.0148, +0.0698]，Holm p=0.201；只能说未检出差异，**不能称等效或非劣**。FG-LPIPS +0.001372 [+0.000762, +0.002081]；LPIPS 越低越好，因此该差值有利于 generic linear，六项主检验 Holm p=0.000114。
- C3−generic linear 的 FG-PSNR 均值为 −0.593 dB [−0.837, −0.351]，但中位数 +0.074 dB、51.7% 对象有利于 C3；FG-LPIPS 则均值方向有利于 linear。保留这种对象/端点异质性，不选单一“总冠军”。
- 独立方向复核逐项重算 28 项主/附录统计：全部一致，`SIGN_DIRECTION_ERROR=0`。

## 前序 schedule / dose 轮次

| 轮次 | 已核验结论 | 可用范围 |
|---|---|---|
| A2 | 300 对象、15 个 layer-window cell 的探索性/native-dose response map 显示异质性；早期 production interaction bootstrap 有零功效缺陷，后续以经验证的 cluster-Wald/GEE 重新审计。 | 仅探索性描述；不能证明 dose-independent 交互、最优 schedule 或确认性复制。
| FRESH_CONFIRM_B / B2 | N=150、4,500/4,500 行门禁通过。LLH−LFM-EXACT：FG-PSNR +0.325 dB [+0.209,+0.446]，FG-LPIPS −0.00460 [−0.00563,−0.00357]；两项区间都落在预先设定的 practical margins 内。 | 同 cohort、按锁定比较解释；边际差异不等于普适或剂量独立机制。HLL−LLL 的方向不支持跨端点“early-high hurts”结论。
| B generic extension | 八个 schedule 扩展条件通过行完整性门禁；在 B 解盲后的同 cohort sensitivity。 | 后锁定敏感性，不是独立确认；实际 residual-dose 的共同支持不足以建立剂量调整后的胜者。
| A3b | 15 个有界 layer×window intervention；统计交互可检出。此前发展期“等剂量校准”和 0/2,250 common-support 结论都使用跨不同特征维度的 raw L2，现不作跨层剂量解释。 | `PARTIAL`。保留为测试干预下的响应异质性；未识别 equal-dose 或 dose-independent 控制律。
| strict-276 | 276 对象、14 个 endpoint/contrast 汇总。C3−GFL FG-PSNR +1.207771 dB，名义 95% CI [+1.116967,+1.294989]，259/276 有利。 | 回溯性 same-cohort 支持；旧 runner/input-tensor provenance 不完整，不能称独立确认或复制。
| E1 multi-seed | 固定 48-object 子集、3 个固定 generation seeds；576 新行 gate PASS。LPIPS 对 GFL、C3、LFM-exact 有支持，PSNR 混合。 | 实现随机种子敏感性；不是独立对象确认，也不是随机种群 seed inference。
| E2 static 2×2 | 同 48-object/3-seed 子集；576 个 logical rows gate PASS。Deep+middle 同步提高在两个主图像端点上有支持；shallow LPIPS 变差，FG-PSNR 有 deep+middle×shallow interaction。 | 固定 seed 的静态尺度敏感性；没有时间变化测试，不支持 equal-realized-dose 或 dose-free interaction。
| MV-Adapter / MVDiffusion | 除 98/99 probe 外，MV-Adapter 新增 76-object 七条件 layer/time 面板（228 个 layer-wise 输出），端点对比混合，方案与结果在同一保留 commit 首次出现；30 个区间均为未校正 pointwise bootstrap。MVDiffusion 75-object 面板在 compatibility base 上完成；525 行为 7 条件 × 75 个对象，每个 12-view 输出网格有 6 个冻结目标视图参与指标计算。原 archive 对低值更优指标使用 improvement-coded delta。按 raw A−B 复算后，L−LLH vs G−FL 的 CIEDE2000 为 +1.373 [+0.418,+2.375]（L−LLH 颜色误差更高），GT-relative variation-statistic error 为 −0.0823；30 个方向编码均值与区间均可复现。native-mirror 检查仅验证 1,552/1,552 个载入张量和单对象 12/12 视图，完整面板未重跑。 | 分开作为回顾性接口边界，不合并分数、不推断 architecture causality、texture fidelity、等效或普适跨骨干迁移；P5 的 raw G-LLH−G-LHL FG-LPIPS 为 −0.001371 [−0.002642,−0.000141]，仅此一个点位区间排除零并有利于 G-LLH；旧报告把方向写反。原分析文件保留作历史记录，阅读时以 raw-direction correction note 为准。

## 3D、seam、CAI、复现与发布

- Fresh C 新 24-object GLB bake/render 主张为 **RETIRED**：11/11 synthetic sampler cases 通过，但完整 gate 因原生 UV 语义和 BLEND alpha 支持不足失败；没有生成最终 24-object 结果。禁止把合成采样通过当作真实资产 seam/3D 通过。
- 历史 N=20 仅保留为 unlit base-color unseen-view 有界结果，端点方向混合；唯一采用的指标及来源范围见 [`HISTORICAL_N20_GLBNATIVE_NONHUMAN_EXTRACT.md`](source/results/HISTORICAL_N20_GLBNATIVE_NONHUMAN_EXTRACT.md)。它不支持总体 3D 胜出，不等于 full PBR。Seam claim **RETIRED**。
- CAI **DESCRIPTIVE_ONLY**：没有 prospective predictor 验证、没有唯一 schedule selector。R2.1 仍为 **OPEN / VENUE RISK**；不得主张 layer×timestep scheduling 的普遍新颖性或 C3 为已证最优。
- Figure D 的当前 20 个候选图像有 20/20 当前 CC BY 校验和逐项 attribution。300-object 权利清单为 20 `FIGURE_ONLY`、271 `METRICS_ONLY`、9 `UNKNOWN`；未知资产和源 GLB 排除。
- 旧 compact package 的有限 clean-checkout rebuild 曾 PASS；这不等于当前 submission candidate 通过。当前 candidate 缺少 clean committed snapshot / clean rebuild，故 `REPRODUCIBILITY=FAIL`、`PUBLIC_RELEASE=FAIL`。
- 当前作者审阅稿已纳入上述回顾性跨接口证据；它不改变 Fresh C 主结果或本页证据等级，也不构成跨骨干迁移结论。

## 本阶段排除

人工实验的设计、招募、答卷、答卷分析和结果解释不进入此汇总。没有检查、复制或复算人工答卷。任何依赖人工偏好/感知保真的主张都不由本归档背书。
