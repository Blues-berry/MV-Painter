# 01549 原稿与历史 9 页候选：结构、章节和图表差异

> 本文中的“当前候选”专指恢复前的 `revision_1008` 9 页候选快照，行号不适用于现活跃稿。最终 1008（11 页）逐节、逐图、逐表对照见 [`01549_FINAL_1008_STRUCTURE_DIFF.md`](01549_FINAL_1008_STRUCTURE_DIFF.md) 及 [`ORIGINAL_CONTENT_DISPOSITION.csv`](ORIGINAL_CONTENT_DISPOSITION.csv)。历史图对照副本在 `forensics_R2_1_20261008/HISTORICAL_1008_NINE_PAGE_CANDIDATE/`。


本文是 `01549_VS_CURRENT_MANUSCRIPT_FORENSIC_AUDIT.md` 的结构化附表。行号均来自唯一原稿与审计时保存的当前候选快照；页数来自相应 PDF。

## 宏观结构

| 元素 | 原始 01549 | 当前候选 | 差异 |
|---|---|---|---|
| 源 TeX 行数 | 698 | 430 | −268 行；主要的大段压缩发生在实验部分 |
| 主稿页数 | 15 页 | 9 页 | −6 页 |
| 主文 Figure 环境 | 7 | 3 | 原 Fig. 4–7 未被主稿引用 |
| 主文 Table 环境 | 9 | 2 | 原有 scale sweep、probe、texture、CLIP-IQA、人评、holdout 表均不再以原表形式出现 |
| 章节骨架 | Introduction → Related Work → Method → Experiments → Limitations → Conclusion | Introduction → Related Work → Method → Experiments → 新增 Discussion → Limitations → Conclusion | 主章节大体保留，Experiments 内容大幅替换/缩短，Discussion 为新增 |
| 图表资产目录 | `source_01549/fig1.pdf`–`fig7.pdf` | `revision_1008/fig1.pdf`–`fig7.pdf` 仍在，且逐个与原文件 SHA 相同 | 资产留存，但当前主文没有引用这些同号文件；主文改用新 `figures/` 资产 |

## 原始章节与当前去向

| 原始段落/研究问题 | 原稿 TeX 行号 | 当前 TeX 行号 | 当前变化与处置 |
|---|---:|---:|---|
| Abstract、关键词 | 18–43 | 21–40 | 将旧 pooled 300-object headline 改为 Fresh C；列明 GFH/Generic Linear 的反结果及 image-space scope。`LOCAL_REWRITE` |
| Introduction：几何控制强度与纹理/结构冲突 | 45–61 | 42–52 | 核心任务问题保留；论证压缩为适配器残差推理控制，增加 SSI 与 scope caveat。`LOCAL_REWRITE` |
| Introduction：四项贡献 | 62–70 | 53–59 | 旧纹理 flattening 百分比及普遍 schedule 优势移除，改为固定 TCAS、stage placement、Fresh C paired validation。`LOCAL_REWRITE` |
| Related Work：3D 纹理、adapter、guidance scheduling | 72–97 | 61–87 | 保留主题与若干原段；加入 SSI 的直接 prior-art 承认，去掉固定 coarse/semantic/detail 阶段定律。`LOCAL_REWRITE` |
| Method：Task/基础 pipeline 与 Fig. 1 | 101–123 | 92–121 | 同一 adapter/几何条件和隐藏状态残差关系保留；公式扩成 per-depth requested/applied cap；Fig. 1 图稿整体替换。`LOCAL_REWRITE` |
| Method：Shape-texture diagnostic metrics | 125–134 | 123–126 | 原 FG/Crop-SSIM、Laplacian、RGB std、gradient 的广义诊断定义和公式，改为 Fresh C 四个图像空间指标的窄定义。`REPLACE_EVIDENCE` |
| Method：TCAS 分段和 C3 profile | 136–153 | 128–147 | C3 数值、分段定义保留；阶段功能说明降为 testable hypothesis，增加 cap/step 实现事实。`LOCAL_REWRITE` |
| CAI 选择器、Proposition、Proof、Remarks | 154–172 | 无 | 完全移除；实际交互/剂量缺乏支撑，推导无法证明 C3 的最优选择。`REMOVE` |
| GeoTex adapter 与 FAC 扩展 | 174–183 | GeoTex residual path 146–147；FAC 无 | GeoTex 结构简述保留；FAC 方法和训练贡献移除。`LOCAL_REWRITE`（GeoTex）/`REMOVE`（FAC） |
| Experimental Setup：4 个 cohort、指标、checkpoints、采样细节 | 188–217 | 152–161 | 改为 Fresh C 同 cohort/protocol、requested-scale sums、object-bootstrap 和 separate addendum。旧 run 细节没有直接迁移到新运行。`REPLACE_EVIDENCE` |
| 13-scale sweep：50 objects、趋势与对象差异 | 218–266 | 163–168 | 当前只承认作为 submitted development history；旧数字表、Fig. 2 曲线、Fig. 3 heatmap 删除。需恢复/重验数据后再定量使用。`REPLACE_EVIDENCE` |
| 26-object texture audit：纹理变化案例与 92% 结论 | 267–289 | 166 | 仅剩历史计数说明；原 Fig. 4/5 未引用。图片可保留为 selected diagnostic，proxy 不能称为 fidelity，百分比需可复算。`REPLACE_EVIDENCE` |
| 24-object / 17-variant development probe 和 C3 选择 | 290–367 | 170–173；另有 247–250 与 Supplement S5 | 当前保留 C3 是历史 development choice；CAI optimality 删除；原 probe 表、Fig. 6 定性对比、Fig. 7 schedule plane 未进入当前主文。Supplement strict-276 不是 probe 的等价替代。`LOCAL_REWRITE` |
| 300-object pooled metrics、纹理 retention、CLIP-IQA、3AFC | 368–481 | 175–247；Discussion 252–261 | 旧 +0.96 dB headline、texture-fidelity/CLIP-IQA/人评优势移除；Fresh C 两表及新视觉 panels 替换部分图像空间比较，并加入 Generic Linear/GFH 反结果。不是原完整 300-object 章节的逐项复刻。`REPLACE_EVIDENCE`；无 authority 的扩张结论 `REMOVE` |
| FAC controlled study | 482–494 | 无 | 当前 evidence index 标记 provenance/控制问题；不作为贡献或正结果。`REMOVE` |
| Adapter-dependence、residual-magnitude、276 holdout、Table 9 | 495–526 | 247–250、255–270；Supplement S3–S5（部分且不同实验） | A2/A3b、Fresh B、Core-7、cross-interface/stage-placement 被作为支持分析与边界陈述，不能替代原强残差 adapter 数据。旧“C3 在所有 regime 最佳”被删除。`MOVE`（部分/不等价） |
| Limitations | 529–538 | 263–272 | adapter/profile、数据范围、指标和 3D 评估限制重新组织，增加 Fresh C failed-bake 与 dose support 边界。`LOCAL_REWRITE` |
| Conclusion | 541–550 | 274–279 | 更新为 Fresh C 的限定结果、Generic Linear/GFH counter-result 和不支持普遍最优的结论。`LOCAL_REWRITE` |
| 数据可用性、利益声明、参考文献 | 552–698 | 281–425 | 声明更新；参考文献主体留存并新增 SSI。`LOCAL_REWRITE` / `KEEP` |

## 原始九张表的映射

| 原表 | 原稿行号/内容 | 当前去向 | 状态与提醒 |
|---|---|---|---|
| Table 1 | 223–249：13-scale uniform sweep | 无对应主文表；历史说明见 166 | 原数值不应直接作为新审计结论；恢复须先核对源数据 |
| Table 2 | 297–321：24-object shape-texture probe | 历史 C3 说明见 173；无逐候选表 | 不得用新的 Fresh C 或 S7 代替 24×17 发展集记录 |
| Table 3 | 346–366：扩展 texture metrics | 无对应主文表 | proxy 结果与历史来源待核验 |
| Table 4 | 373–389：pooled 300-object absolute metrics | 当前 Table 1，180–200：Fresh C means | 新旧运行/数据定义不同；旧数据不能与 Fresh C 混写 |
| Table 5 | 395–410：300-object texture metrics | 无对应主文表 | 原 texture-fidelity 解释已撤；只有 proxy 证据可以恢复 |
| Table 6 | 414–430：retention ratios/win rates | 无对应主文表 | 样本、计算权威需确认 |
| Table 7 | 440–454：50-object CLIP-IQA | 无对应主文表 | 当前 evidence gate 不支持旧 perceptual claim |
| Table 8 | 461–475：30-object/24-participant 3AFC | 无对应主文表 | 不把旧研究的有限问题扩展为当前方法的人类偏好/3D 结论 |
| Table 9 | 510–526：strong-residual adapter 的 276 transfer | Supplement S5 有不同 strict-276 stage placement 证据 | cohort、adapter/run、comparison 不同，不能称为迁移复刻 |

当前主稿仅有 Table 1（Fresh C 条件均值，TeX 180–200）与 Table 2（Fresh C paired contrasts，202–220）。补充材料 Table S7 是另一个 strict-276 stage-placement run；Table S8 是独立历史 N=20 unseen-view summary。二者均不能作为上表任意旧表的简单改号替代。

## 原始七图与当前引用关系

| 原图 | 原稿位置 | 当前主文替代项 | 当前状态 |
|---|---:|---|---|
| Fig. 1 整体 pipeline | 106–111 | `figures/fig1_tcas_pipeline_1008.pdf`，97–102 | 新架构图取代原布局；FAC 被移除，但 bake/output chain 也从图中消失 |
| Fig. 2 固定 scale 曲线 | 251–257 | Fresh C selected panels，TeX 223–233 | 研究问题改变；不是 scale curve 的替代 |
| Fig. 3 50×13 对象响应 heatmap | 260–266 | Fresh C trade-off panels，237–245 | 研究问题改变；不是 per-object scale heatmap 的替代 |
| Fig. 4 texture 视觉 audit | 272–278 | 无 | 源 asset 留存但未引用 |
| Fig. 5 26-object texture proxy ratios | 281–287 | 无 | 源 asset 留存但未引用 |
| Fig. 6 C3 vs fixed-scale qualitative | 324–330 | Fresh C panels 部分覆盖对照，223–247 | 不同 cohort、条件和问题；非逐项替换 |
| Fig. 7 17-variant development trade-off | 333–339 | 无 | 文件留存但未引用；C3 的 development 选择图因此缺席 |

具体图像、哈希、论证功能和保留建议见 [`01549_FIGURE_PRESERVATION_REVIEW.md`](01549_FIGURE_PRESERVATION_REVIEW.md)。

## 篇幅减少原因

当前 9 页来自实质内容精简，而非标题/字体等技术差异。Git 中 `0aaefc86` 对主文实验段作 304 行删除、43 行增加：删除了 50-object × 13-scale 的结果表和两张图、26-object 纹理审计图表、24×17 probe 结果和 C3 图、旧 300-object pooled 与 texture-retention 表、CLIP-IQA 与 3AFC、FAC 复核及 adapter-dependence/276 表；将这部分收缩为历史说明和 Fresh C 新证据。后续摘要/讨论/限制部分又被压缩和重写。是否恢复每项取决于其原始数据可复核性，不能以达到 15 页为目标，也不应默认 9 页结构正确。

## 审计结论

该候选稿在历史上可追溯到真正 01549 的副本，但当前结构已把原论文的主要诊断链大幅换成更窄的 Fresh C 结果。它没有被证据证明是 1007/round2 文稿的复制品；也不能因源文件名、保留 TCAS 标题或目录中留有 7 个 PDF 而称为“原 01549 结构完整”。恢复方案应从已核验唯一源文件创建新的隔离副本，并把当前有效修订按证据块移植，详见 [`01549_RESTORATION_MINIMAL_PLAN.md`](01549_RESTORATION_MINIMAL_PLAN.md)。
