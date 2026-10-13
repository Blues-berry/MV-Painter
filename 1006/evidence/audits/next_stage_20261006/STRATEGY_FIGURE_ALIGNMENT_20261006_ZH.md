# 策略比较与证据边界图件记录 — 2026-10-06

本记录登记从既有对象级来源重新生成、逐图检查过的证据对齐图。图件用于解释已完成 cohort 的差异和边界，不改变分析计划、不选择人工评测对象，也不替代 Fresh C 的锁定比较。逐图来源哈希见 `1006/figures/evidence_alignment/FIGURE_SOURCE_MANIFEST.json`；可重建命令为 `python 1006/scripts/generate_evidence_alignment_figures.py`。

## 图件与允许解释

| 图件 | Cohort / 单位 | 图中内容 | 可支持的解释与限制 |
|---|---|---|---|
| `fresh_b_strategy_endpoint_tradeoffs.png` | FRESH_CONFIRM_B；150 个对象/对比 | LLH−LFM-exact、LLH−HLL、LLH−LLL、HLL−LLL 的对象级 FG-PSNR 与 FG-LPIPS 配对差值；HLL−LLL 明确标作 exploratory | 说明对象响应与跨指标权衡；单点不是显著性检验，不能用点云或均值组合宣布跨指标赢家。区间和校正 p 值仍以冻结分析报告为准。 |
| `historical_campaign_c_llh_linear_tradeoff.png` | 历史 Campaign B1B2 与 C 的相同 300 个 UID | LLH−linear 的配对端点散点，附 Holm 校正结果 | 是同 cohort 回顾性复评，不是独立确认。300/300 行 UID、种子、对象索引和六项输入哈希匹配；旧 manifest 缺少 config hash。LLH−linear 的 FG-LPIPS 为正，因此按低值较优应判为有利于 linear。 |
| `fresh_b_gt_texture_complexity_heterogeneity.png` | FRESH_CONFIRM_B；150 个对象 | GT 前景 Laplacian variance 与 LLH−GFL 的 PSNR/LPIPS 对象差值；复核已存 Spearman ρ 与区间 | 表示探索性关联和效应异质性；不定义复杂度阈值，不主张因果边界，也不进行事后子组筛选。 |
| `mvadapter_fg_lpips_interface_boundary.png` | MV-Adapter G complete；98 个对象 | 三层组×五时间窗相对 baseline 的 FG-LPIPS 效应与 16 项家族校正值 | 浅层 W3–W5 的局部效应通过 Holm；全局交互未得到确认（cluster-bootstrap p=0.6523；探索性有限样本 Wald p=0.1012，四指标 Holm p=0.3037）。单格效应不能升级为全局 Layer×Window interaction。正的 treatment−baseline LPIPS 表示该处理变差。 |
| `mvdiffusion_interface_boundary.png` | MVDiffusion depth/text interface；75 个对象/对比 | 五个接口配对在 interop FG-PSNR 和 sign-reversed interop FG-LPIPS 上的对象 bootstrap 均值与名义 95% CI | 正向统一表示左侧方法有利；LPIPS 已反号以便方向一致。配对是独立 correspondence-aware interface 诊断，无跨比较校正或跨骨干合并，不识别架构因果。 |

同目录的 PDF 为可排版版本。逐点数据写入 `1006/data/derived/evidence_alignment/`，保留 UID、原始差值方向与 cohort 标签。Fresh B 散点图不在单个对象上绘制显著性；Historical C 由原始 shard JSON 重建，并与方向审计中的均值和 Holm 结果核对；MVDiffusion 图从逐对象表重建并与保存的均值及 bootstrap 区间逐项核对。

1006 原有主图也已重新生成，Fresh B 森林图现在分别标清 PSNR 正向和 LPIPS 负向有利；`b_profiles`、E1 seed 敏感性、E2 静态因子以及 GLB endpoint 图继续保持独立用途。`cap_scale_semantics` 只画请求值与原生 cap 后 scale；texture-rich failure sheet 是对象案例展示，不是独立统计证据。GLB 图的范围仍是 20 个 UV 合格对象上的 unlit base-color、固定未见视角结果。生产 glTF seam 指标尚未通过采样器/拓扑验证，因此未补 seam 改善图或相关主张。

## 新增 Fresh C 对比图的门禁

Fresh C 的比较图、效应排序、20 个对象组图只在原四条件和独立 LLH/linear 附录各自完整通过完整性门禁后生成。样例对象按已冻结的四个对比平衡抽取；每组图必须同时显示参考、GFL、GFH、no-adapter、C3、LLH、linear 的同一 UID/同一视角。对象差异排序不产生对象级显著性，也不得用于挑选人工评测刺激。Fresh C 未过门禁时，本文件中历史图件与其隔离，不填补或代替新 cohort 结果。

## 复核记录

- 对照参考图的 PSNR/LPIPS 轴方向均已写明；低 LPIPS 有利。
- Campaign C 的旧方向更正以源行和方向审计为准，旧摘要保留为 superseded 历史记录。
- MV-Adapter cell 的校正家族及两个不同全局检验均分开标注，没有把局部显著性称作交互。
- MVDiffusion 明示 lower-is-better 指标已反向，并保留名义区间与独立接口范围。
- 01549 提交版正文未修改，Fresh D 未启动，未生成或分发人工评测刺激包。
