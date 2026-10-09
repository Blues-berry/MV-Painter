# 01549 投稿稿到恢复修订稿：逐节与实验链差异

> **历史中间稿记录，已由当前 1008 交付取代。** 本文件记录早期 10 页候选稿，包含后来更正的图表和偏好/FAC 处置；不要用作当前投稿结构或证据口径。当前稿以 2026-09-07 第一轮修订版为基准，见 `submission_1008_final/01549_TO_1008_CHANGELOG.md`、`REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv` 和 `SUBMISSION_BUILD_REPORT.md`。

**比较对象：** 认证投稿源 `1008/manuscript/source_01549/final_0903.tex`（698 行、15 页）与当前活跃恢复稿 `1008/manuscript/revision_01549_restored/final_0903.tex`（当前 TeX SHA-256 `eda3ee762ca0484481722ec5f1dda968be9ba990a628c9ac967fc1d660f715d7`）。行号均为对应 TeX 源码行；论文页码来自当前编译的 10 页 PDF。恢复稿不是对历史 9 页候选作补图修补，而是从认证原稿重新生成后选择性移植经核验证据。

## 章节与论证段落处置

| 原始段落 / 研究问题 | 原稿行号 | 恢复稿行号 / 去向 | 状态 | 具体差异与依据 |
|---|---:|---|---|---|
| 标题、摘要、关键词 | 1–44 | 1–40，p.1 | `LOCAL_REWRITE` | 题目和 TCAS 身份不变；摘要把旧 pooled +0.96 dB 换为 Fresh C 主对比，同时报告 GFH/Generic Linear 反结果、历史 C3 选择的 provenance 限制及 image-space 边界。 |
| Introduction：几何约束强度与纹理外观 | 45–70 | 44–69，pp.1–2 | `LOCAL_REWRITE` | 原始问题链保留；把“强度必然导致纹理压平”等未核实普遍表述改为 adapter/wrapper/residual 依赖。贡献中保留原 fixed-scale 和 C3 开发问题，加入 Fresh C 和反结果。 |
| Related Work：3D texture、adapter、guidance schedule | 72–97 | 71–91，p.2 | `LOCAL_REWRITE` | 原相关领域保留；加入 SSI 对 layer×time 与 geometry-conditioned ControlNet scaling 的直接先例，明确不主张通用调度首创。 |
| Method：任务、流程、原 Figure 1 | 101–123 | 96–118，pp.3–4 | `LOCAL_REWRITE` | 原 GeoTex residual → UNet feature injection 和六视角图像生成 / projection-baking 流程保留；公式显式区分 requested/applied scale、native cap 和 residual magnitude。Fig.1 只移除 FAC 子模块、局部标注未纳入 FAC；Fresh C 不验证 baking。 |
| Method：Shape/texture metrics 与 Laplacian 指标 | 125–134 | 120–129，p.3 | `REPLACE_EVIDENCE` | 定义当前 image-space 指标和纹理变化代理；写明 Laplacian/RGB/gradient 增大不能自动等同更高 fidelity。旧 proxy 不作为确认性端点。 |
| Method：TCAS 三阶段、C3 及 CAI 命题/证明 | 136–172 | TCAS 131–150，pp.3–4；CAI 删除 | `LOCAL_REWRITE` | C3=(1.25,2.50,1.25)、sampling-progress 三段和 training-free residual control 保留；阶段语义被限定为假设。CAI additivity、Proposition、Proof 被删除，因为推导前提未通过机制/剂量验证且不能证明 C3 最优。 |
| Method：GeoTex adapter 与 FAC 扩展 | 174–183 | GeoTex 152–157，p.4；FAC 成功叙事删除 | `LOCAL_REWRITE` | adapter 基础结构保留；FAC 不再作为有效方法或正向结果，依据是 provenance 与 controlled-reproduction audit。 |
| Experiments：设置、协议、队列和统计 | 188–217 | 162–186，pp.4–5 | `REPLACE_EVIDENCE` | 当前实验细节只陈述 Fresh C 和独立 addendum 的队列、inputs、views、seed、对象级 bootstrap；不把 Fresh C wrapper 或 protocol 倒推为历史 50/24-object run 设置。 |
| 50-object × 13-scale 固定尺度扫描、Fig.2 曲线、Fig.3 heatmap | 218–266 | 188–235，pp.5–6 | `KEEP` | 原 Table 1 与原 Fig.2–3 恢复到 fixed-scale 研究问题。表格、曲线和热图均标注为原投稿历史诊断；底层对象行/运行清单不完整，所以不称当前重算或确认性结果。 |
| 26-object texture audit、旧 Fig.4/5 与 92% flattening | 267–289 | 237–254，pp.5–7；撤回说明 line 240–242 | `REPLACE_EVIDENCE` | 原局部纹理图位改为 Fresh C matched full-object panels，涵盖近中位、不利 C3–GFL、Generic Linear 反例。旧 RGB/gradient 比率图和 92% prevalence 移除：IDs、subset rule、raw rows 与 metric definition 无法追溯，proxy 不代表 fidelity。 |
| 24-object / 17-variant C3 开发选择、CAI 结论 | 290–367 | 256–315，pp.6–9 | `LOCAL_REWRITE` | 原 Table 2 开发摘要和 17-variant 图保留为 history；Fig.7 最终编号为 Fig.6，只局部改内部标签。原 C3-vs-fixed qualitative slot（原 Fig.6）由 Fresh C 全物体 matched panel 接替；CAI 最优性和 probe-based unique winner 删除。 |
| 原 pooled 300-object Table 4 与 texture Tables 5–6 | 368–430 | 317–369，pp.8–9 | `REPLACE_EVIDENCE` | Table 4/旧 +0.96 headline 换成 Fresh C 新 Tables 3–4；原 texture-retention 表无直接等价新测量，因证据与解释缺陷移除。C3–GFL 正向同时保留 GFH、Generic Linear 的反结果、LLH 端点取舍和非 probe-disjoint 限制。 |
| CLIP-IQA、30-object/participant human preference Tables 7–8 | 437–475 | 撤回说明 lines 489–493，p.9；无当前表格 | `REMOVE` | 不再声称 CLIP-IQA/人评优越。当前 authorized evidence 中缺乏可作为本次确认性质量结论的完整 source/metric/participant authorization；没有用图像指标冒充人评。 |
| FAC controlled extension | 482–494 | FAC 边界 lines 152–157、489–493；无结果小节 | `REMOVE` | FAC positive result 与训练扩展不再属于当前主文结果；根因及证据门禁见 root cause audit。 |
| Adapter-dependence、strong-residual strict-276、Table 9 | 495–526 | 主文 bounded summary 371–378；Supplement S3–S5 / Table S7；原 Table 9 → Table S9 | `MOVE` | A2/A3b、Fresh B、Core-7、stage placement、MV-Adapter/MVDiffusion 各按 run/cohort/adapter 分开，不能称原 Table9 的等价复现。原 Table9 数字保留为历史转录、明确 provenance 不全。 |
| Limitations | 529–540 | 380–390，pp.8–9 | `LOCAL_REWRITE` | 增加 main-adapter probe-disjoint 缺失、Fresh C 不是 full 3D validation、unseen-view N=20 限制、no PBR/seam/human claims、realized dose and A3b common-support limits。 |
| Conclusion | 541–551 | 391–399，p.9 | `LOCAL_REWRITE` | 收束到 TCAS residual scaling 和 Fresh C 有界 image-space 结果；GFH / Generic Linear 反结果保留；不宣称全局调度最优或烘焙纹理质量改善。 |
| Data availability、声明、references | 552–698 | 400 起，pp.9–10 | `LOCAL_REWRITE` / `KEEP` | 声明更新；参考文献主体保留并添加 SSI 引用。 |

## 七图与九表的显式映射

完整状态、原始哈希、最终资产哈希、活动 TeX 行号和 PDF 页码见 [`ORIGINAL_CONTENT_DISPOSITION.csv`](ORIGINAL_CONTENT_DISPOSITION.csv) 与 [逐图资产 manifest](forensics_R2_1_20261008/RESTORED_FIGURE_ASSET_MANIFEST.csv)。摘要如下：

- **七图：** 原 Fig.1 → 局部恢复 Fig.1；原 Figs.2–3 → 原样保留为历史诊断；原 Fig.4 → Fresh C 全物体 Fig.4；原 Fig.5 → 因 proxy 溯源缺陷移除；原 Fig.6 → Fresh C 原问题对照 Fig.5；原 Fig.7 → 局部改标签的开发图 Fig.6。
- **九表：** 原 Tables 1–2 保留为历史诊断；Table 3 移除；Table 4 由 Fresh C 新 Tables 3–4 替换；Tables 5–8 依据 source/metric/authorization 限制移除；Table 9 移入 Supplement S9 并注明不同 adapter/run、逐行 provenance 不足。
- `UNJUSTIFIED_STRUCTURAL_DELETION_COUNT = 0`：被删除或迁移的论证都在 disposition ledger 中逐项给出证据/解释理由。历史数据不充分时，保留可成立的研究问题和诊断用途，不将缺失原始行伪装成已核实结果。

## 页数变化

| 版本 | 主文页数 | 主文图 | 主文表 | TeX 行数 /身份 |
|---|---:|---:|---:|---|
| authenticated 01549 submission | 15 | 7 | 9 | 698；ZIP member 与 source TeX byte-identical |
| historical `revision_1008` candidate | 9 | 3 | 2 | 430 行历史候选；内容来源正确但过度重写 |
| active `revision_01549_restored` | 10 | 6 | 4 | 从认证源重建；旧结论撤回、历史诊断明确标注 |

恢复稿较原稿短 5 页不是以 9 页为目标造成。主要篇幅差来自 26-object quantitative proxy audit、旧 pooled texture Tables 5–6、CLIP-IQA Table 7、人评 Table 8、FAC section，以及不等价 adapter/run 细节从主文移到 Supplement 或退出主张。有效的 fixed-scale 和 C3 development 论证没有随失效结论一起删除。原始 Fig.5 quantitative proxy chart 仍未恢复，因为当前数据缺口无法支持；这是明确的证据性删除而非排版选择。

## 连续性结论

活跃主文从 authenticated ZIP 的原始 `final_0903.tex` 确定性重建；将其输出到临时路径可与当前 active TeX 做逐字节比较。它保留 TCAS、C3、GeoTex residual path 和原固定尺度/开发集问题，并以证据限定来代替失效结论。`01549_IDENTITY_PRESERVED` 不是只由标题或编译判断，而由来源哈希、重建一致性、逐图/表台账和逐节 diff 共同支持。详细门禁状态见 `01549_REVISION_CONTINUITY_ACCEPTANCE.md`。
