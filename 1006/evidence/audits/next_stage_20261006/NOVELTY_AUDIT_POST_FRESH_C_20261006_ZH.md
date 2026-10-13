# R2.1 新颖性与贡献风险复审（Fresh C 后的阶段性审查）

**状态：INTERIM；不是最终 adversarial review。** Fresh C 图像空间证据已完成；真实人工答卷、新的有效 3D 烘焙/未见视角证据尚未完成，素材许可也未全清。因此按用户冻结条件，R2.1 最终审查仍须等 R1 保真范围正式决定后执行。当前判断为 `R2.1 = OPEN / VENUE_RISK`。

## Fresh C 改变了什么

原四条件 Fresh C 在 N=300 上通过完整性门禁，注册的 `C3−GFL` FG-PSNR 均值差为 +0.522 dB，95% 对象 bootstrap CI [+0.404, +0.641]，68.7% 对象有利于 C3。独立的同 cohort addendum 将 LLH 与 generic linear 正面比较：LLH−linear FG-PSNR 的区间跨零且没有等效界值；LLH−linear FG-LPIPS 为 +0.001372 [ +0.000762, +0.002081 ]，Holm p=0.000114，正差因 LPIPS 越低越好而有利于 linear。LLH−C3 的 PSNR 均值为正，但中位数和有利对象比例显示明显异质性。结果排除了“跨指标唯一赢家”的安全叙事，却没有验证一条普遍的 layer×time 定律。

Fresh C 的 C3/GFL/GFH 请求 profile 与实际 cap 后 profile 在 shallow group 上确有差别；实际 residual 日志存在且已由对应完整性门禁检查。因而可以说请求强度不总等于执行强度，但不可将“有 cap clipping”扩展成“等 realized residual 下的因果质量效应”：本轮未设置实现剂量匹配的同剂量对照。

## 最近先行工作的对抗性比较

| 工作 | 与本稿的重叠 | 本稿可保留的边界 |
|---|---|---|
| Scheduled Style Injection (SSI) | 直接沿网络深度和去噪时间调度风格注入，也测试 ControlNet 几何条件在两轴上的调度。它使“首次 layer×time scheduling”或“新控制空间”不可辩护。 | 只能主张对本任务所测几何 adapter residual/cap 执行语义和其对象/指标结果的限定刻画；还需解释这份知识对纹理输出评估带来的实质价值。 |
| MVPainter | 已有多视角扩散、几何 ControlNet 条件、烘焙/PBR 与人类对齐评测，是问题域和系统背景。 | 本工作不是新的多视角纹理生成器；必须限于原路径上的 scale/residual/cap 证据。 |
| MV-Adapter、MVDiffusion | 多视角条件注入接口不同；当前分别测过，但不同接口不是同一个干预，也不能用“一显著、一不显著”证明架构因果。 | 只报告各自测试接口内的边界，不作普遍迁移结论。 |
| Paint3D、MVPaint、Im2SurfTex | 相关工作已涉及 UV 纹理生成、融合、烘焙和 seam/coherence。 | 目前本稿没有新的、通过 sampler/topology 验证的 seam 证据；不主张 3D seam 或材质质量贡献。 |
| APG 与有限区间 guidance | 与强度调节/归一化相关，但其干预对象是 classifier-free guidance 更新，不等同于本项目的几何 adapter residual 注入路径。 | 可用于界定相关方法，不足以把 E6 的 cap-aware 校准包装成已验证贡献；E6 已停在负向方法价值门。 |

## Contribution A/B/C 判定

| 候选经验贡献 | 当前判定 | 允许措辞与缺口 |
|---|---|---|
| A. requested scale 不足以唯一描述实际干预，native layer cap 改变 applied scale | **在具体实现/profile 范围内支持。** Fresh C shallow 请求值高于 0.8 cap，清单记录了请求/应用差异；残差日志也存在。 | 写成“在已测试配置中，cap 将 shallow scale 截至 0.8，故名义请求与应用 scale 不同”。不要泛化到所有 adapter 或把 scale clipping 等同于真实 residual 剂量。 |
| B. requested/applied/realized residual 是不同量，且该区分实质改变 texture quality | **不成立为已验证的质量机制。** 实现残差有记录，但 E5 未采集质量端点且 shallow dose match 失败；E6 在独立质量价值门停止。Fresh C 没有 equal-realized-residual 对照。 | 把三个量分开记录可以作为方法透明度；不得说该区分已证明造成匹配剂量下的质量改善。不得为本轮补做 E6 或新剂量搜索。 |
| C. depth/time 效应依赖端点、对象与接口，简单 schedule 不必等价或普遍劣于候选 schedule | **有限支持。** Fresh C 显示对象/端点异质性，并在 FG-LPIPS 上显示 generic linear 优于 LLH；其他历史接口结果各自独立。 | 限定为命名 cohort、端点、原生 cap 与所测接口的比较。不声称普遍 superiority、equivalence 或 architecture causality。 |

## 编辑风险与处置

即使 A 与 C 的窄化陈述都成立，R2.1 仍可能认为其方法贡献低于 Computers & Graphics 的门槛。当前没有“新的算法模块”可补救，且新方法搜索明确停止。因此建议在最终稿中：

1. 将贡献写成一项受控实证研究，不称新 schedule 框架或优化算法；
2. 把 C3、LLH、linear 视为被测策略与强对照，按指标和对象异质性报告；
3. 将 A2/A3/A3b、E5/E6、跨接口结果降为边界或补充材料，避免挤到 texture 输出结果之前；
4. 在投稿适配决策中明确保留 `R2.1 OPEN / VENUE_RISK`，不靠显著性、改名或措辞宣布关闭。

SSI 一手来源：[CVPRW/NTIRE 2026 正式论文](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf)；[arXiv 记录](https://arxiv.org/abs/2605.26538)；[作者实现](https://github.com/ameyskulkarni/scheduled_style_injection)。其他一手对照：[MVPainter](https://arxiv.org/abs/2505.12635)、[MV-Adapter](https://openaccess.thecvf.com/content/ICCV2025/html/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.html)、[MVDiffusion](https://arxiv.org/abs/2307.01097)、[Paint3D](https://arxiv.org/abs/2312.13913)、[MVPaint](https://arxiv.org/abs/2411.02336)、[Im2SurfTex](https://doi.org/10.1111/cgf.70191)、[APG](https://arxiv.org/abs/2410.02416)、[Applying Guidance in a Limited Interval](https://arxiv.org/abs/2404.07724)。
