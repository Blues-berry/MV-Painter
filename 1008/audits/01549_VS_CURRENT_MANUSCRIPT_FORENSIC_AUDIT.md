# 01549 投稿底稿与当前候选稿取证审计

> **版本范围说明：** 前文取证对象是 `revision_1008/final_0903.tex` 的历史 9 页候选快照，该候选保存在 `forensics_R2_1_20261008/HISTORICAL_1008_NINE_PAGE_CANDIDATE/`，未被覆盖。当前交付稿是从认证 01549 源恢复并修订的 `revision_01549_restored/manuscript_1008.tex`，成套副本位于 `submission_1008_final/`；最新处置与行号见 [`submission_1008_final/01549_TO_1008_CHANGELOG.md`](../submission_1008_final/01549_TO_1008_CHANGELOG.md)、[`ORIGINAL_CONTENT_DISPOSITION.csv`](ORIGINAL_CONTENT_DISPOSITION.csv) 和 [`01549_FIGURE_PRESERVATION_REVIEW.md`](01549_FIGURE_PRESERVATION_REVIEW.md)。本文前半部分只审计历史 9 页候选，不能将其旧行号或结论套用于当前 1008。


**审计日期：** 2026-10-08  
**历史审计范围：** 核实 9 页历史候选的来源、章节/图表连续性与结构删除；本报告中针对 `revision_1008/` 的旧行号只适用于被归档的候选快照。恢复稿的执行结果在下文补记。

## 结论摘要

1. 唯一投稿底稿已通过 SHA-256 和投稿压缩包成员双重核验。指定源文件与 `final/submission_new_0907/latex.zip` 中的 `final_0903.tex` 逐字节相同，SHA-256 均为 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`。两个压缩包本身也逐字节相同，SHA-256 为 `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`。
2. 当前候选稿已先行只读备份；审计开始时 SHA-256 为 `2d260f6f21557a02be097eb0864c5886ca449f05f3da5b8a190c3af24dac089e`。备份位于 [`forensics_R2_1_20261008/current_final_0903_before_audit.tex`](forensics_R2_1_20261008/current_final_0903_before_audit.tex)，对应哈希记录位于 [`current_candidate.sha256`](forensics_R2_1_20261008/current_candidate.sha256)。原候选稿仍在原路径，未覆盖。
3. **来源链不是 1007/round2 文件移植。** 可见 Git 历史中，实验压缩前的候选稿位于 `0aaefc86` 的父提交，677 行，SHA-256 `4e95a0ef9bfaaa96f8b837de9060ccd9985a9561b9e57fbc7a7653eb6bb19249`；去掉参考文献后，与真正 01549 正文的 token 序列相似度为 0.891。相同度量下，它与被排除的 `final/final_0903.tex` 为 0.156，与 `final/round2/final_round2.tex` 为 0.334。该祖先副本保存于 [`revision_candidate_at_pre_compression_commit.tex`](forensics_R2_1_20261008/revision_candidate_at_pre_compression_commit.tex)。证据支持“从真正 01549 副本开始”，不支持“主体来自 1007/round2”。
4. **但当前候选已不是外科式局部修订稿。** `0aaefc86` 的提交说明为 “revise experiments and result tables”，对主文一次性作出 304 行删除、43 行增加；后续叙事和图稿提交继续重写。当前文件为 430 行、9 页，原始为 698 行、15 页。当前主文只引用 3 个 figure 环境和 2 个 table 环境，原始主文有 7 个 figure 环境和 9 个 table 环境。篇幅下降主要来自实验段落、表和图的成批移除，不是单纯排版或编译差异。
5. **图像文件留存不等于图仍在论文中。** 当前 `revision_1008/fig1.pdf`–`fig7.pdf` 与投稿源文件的同号 PDF 全部字节相同；但当前 TeX 实际只引用一个重绘的 Figure 1 PDF 和四张 Fresh C PNG（组成 Figure 2、3）。Figure 4–7 的同号 PDF 虽仍在文件夹，却没有被当前主文引用。

## 底稿身份与文件校验

| 文件/快照 | 行数或大小 | SHA-256 / 比较 | 判断 |
|---|---:|---|---|
| 唯一原稿 `1008/manuscript/source_01549/final_0903.tex` | 698 行 | `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` | 身份基准 |
| 投稿包内 `final_0903.tex` | — | 与唯一原稿字节相同；SHA 同上 | 独立交叉核验通过 |
| `final/submission_new_0907/latex.zip` | 3,166,364 bytes | 与 `source_01549/01549_latex.zip` 字节相同；SHA `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a` | 包级交叉核验通过 |
| 当前候选 `revision_1008/final_0903.tex` | 430 行 | `2d260f6f21557a02be097eb0864c5886ca449f05f3da5b8a190c3af24dac089e` | 审计时快照，未覆盖 |
| 压缩前候选（`0aaefc86` 父提交） | 677 行 | `4e95a0ef9bfaaa96f8b837de9060ccd9985a9561b9e57fbc7a7653eb6bb19249` | 正文 token 序列与唯一原稿相似度 0.891 |
| `final/final_0903.tex`（排除版本） | 384 行 | 与压缩前候选正文 token 相似度 0.156 | 不作为底稿 |
| `final/round2/final_round2.tex`（排除版本） | 923 行 | 与压缩前候选正文 token 相似度 0.334 | 不作为底稿 |

相似度是去除 `thebibliography` 后的小写词/数字 token 序列 `SequenceMatcher` 比率，只用于辅助追踪文本来源，不作原创性或学术质量指标。压缩前候选副本的 Git 父提交是本次来源核验的关键：它在主要实验压缩提交之前保留了与真正投稿稿高度一致的结构和正文。

## 逐节保留与去向判断

下表逐项给出原稿行号、当前候选行号及当前处置。`MOVE` 只表示存在相邻证据迁入补充材料，不代表旧结论已被同等证据替代。

| 原稿章节/内容 | 原稿行号 | 当前候选行号/去向 | 状态 | 取证判断与审稿/证据理由 |
|---|---:|---|---|---|
| 标题、摘要、关键词与版式前导 | 1–44 | 1–41 | `LOCAL_REWRITE` | 标题和投稿身份字段保留；摘要改为 Fresh C、Generic Linear/GFH 反结果和图像空间边界。仅保留题名不能证明身份，但 Git 祖先快照证实其从投稿源副本演变。 |
| Introduction | 45–70 | 42–59 | `LOCAL_REWRITE` | 保留“几何适配器强度是推理期控制”的问题；删除旧 300 pooled +0.96 dB、92% 纹理、未证实人评等贡献陈述，换成 Fresh C 与受限贡献。旧主结果缺少统一可追溯 authority；需恢复原问题链而非旧结论。 |
| Related Work | 72–97 | 61–87 | `LOCAL_REWRITE` | 保留 3D 纹理、Adapter/ControlNet、CFG 主题；加入 SSI 直接先例，明确不主张通用 layer×time 调度新颖性；删除固定语义阶段分工。此处是有审稿依据的局部扩写/纠偏。 |
| Task / pipeline 与残差公式 | 101–123 | 92–121 | `LOCAL_REWRITE` | 原始 `h'_t=h_t+s(p_t)Aφ(h_t,G)` 改为按深度组定义 requested scale、native cap 和 applied residual；这是基于代码的准确化。Figure 1 也被替换，见图审阅报告。 |
| 原形状/纹理指标定义与 Laplacian 公式 | 125–134 | 123–126 | `REPLACE_EVIDENCE` | 当前仅定义 Fresh C 四项图像空间端点；纹理代理指标、公式和“变化即保真”的解释被移除。理由是不得从 PSNR/SSIM 推断纹理保真，但原纹理诊断可在恢复其源数据和限定 proxy 含义后单独保留。 |
| TCAS 时间分段与 C3 | 136–153 | 128–147 | `LOCAL_REWRITE` | 精确保留 1/3 分段和 C3=(1.25,2.50,1.25)，补充 50 步和 per-layer cap 语义；把早/中/晚的确定性语义改为可检验假设。 |
| CAI stage-utility、命题、证明及最优性解释 | 154–172 | 无 | `REMOVE` | 已有机制/数学审计指出 additivity 和独立 stage utility 不受实际交互及剂量支持验证，证明不能推出实验中的 C3 优选。移除此不损害方法身份，不能恢复为 C3 推导/保证。 |
| GeoTex 与 FAC 方法扩展 | 174–183 | GeoTex 残差路径 146–147；FAC 无 | `REMOVE`（FAC）/`LOCAL_REWRITE`（GeoTex） | GeoTex 输入和残差路径保留。FAC 的训练模块、贡献和结果因 provenance 不足及受控复核为负而退出当前主张，审计档案仍在；不应恢复 FAC 成功结论。 |
| Experimental setup、数据集与原始 4 cohort 设计 | 188–217 | 152–161 | `REPLACE_EVIDENCE` | 新版聚焦 Fresh C matched inputs、对象级 bootstrap 和 separate addendum。旧数据/模型/训练池描述不能自动移植到不同 run；需要逐运行 manifest 核对后再恢复可复现设置细节。 |
| 13-scale / 50-object fixed-scale sweep（Table 1、Figs. 2–3） | 218–266 | 163–168，仅历史说明 | `REPLACE_EVIDENCE` | 原数值表、曲线、heatmap 均从当前主文删除。实验登记审计称未找到与行级结果相联的 protocol/config、UID、checkpoint 和日志，故不能作为当前已审计定量证据；但不能因此抹掉其研究问题或图像，建议核验后恢复为历史/开发诊断。 |
| 26-object texture audit（Figs. 4–5、92% 与 proxy 解释） | 267–289 | 166 的历史计数说明 | `REPLACE_EVIDENCE` | 原量化结论与图均不在当前主文。证据登记未找到完整源行、子集规则和 run identity；同时 RGB/gradient/Laplacian 是变化代理，不等价于纹理保真。视觉案例可作有边界的例子；92% 需独立审计后才可提及。 |
| 24-object / 17-variant C3 selection（Table 2、Table 3、Figs. 6–7） | 290–367 | 170–173 仅保留历史选择；276-placement 在 250/Supp. S5 | `LOCAL_REWRITE` | 当前明确 C3 是历史 development choice，不是独立排名或最优；但原 probe 比较表、四条件 Figure 6、17 variant Figure 7 都未进主文。S7 是不同的 strict-276 run，不能作为 probe 图表替身。建议先核验原 probe source，保留发展集角色并降级过强语句。 |
| 原 300-object pooled 表格、纹理 retention、CLIP-IQA、人评 | 368–481（Tables 4–8） | 175–247 Fresh C；仅 2 张新表与 Figures 2–3 | `REPLACE_EVIDENCE`（旧主结果）/`REMOVE`（无法支持的扩展结论） | 用 revision-era Fresh C 取代旧 +0.96 dB pooled headline；Generic Linear/GFH 反结果现在保留。旧纹理保真、CLIP-IQA 及 3AFC 的广泛结论无足够可复核 authority，移除是审稿边界。现有 Fresh C 不回答所有原章节问题。 |
| FAC controlled extension | 482–494 | 无 | `REMOVE` | Evidence index 将 FAC 标为 provenance 不足并要求不恢复；无必要为篇幅保留其历史成功叙事。 |
| Adapter-dependence / strong-residual / holdout analysis（Table 9） | 495–526 | 247–261 的支持分析与限度；Supplement S3–S5 部分不同实验 | `MOVE`（仅支持性/不等价） | 当前 A2/A3b、Fresh B、Core-7 和跨接口内容在补充材料中作为边界；它们不是原 strong-residual 24/276 研究的等价迁移。旧的“各 regime C3 最佳”需保持删除，除非旧 run 可逐项复核。 |
| Limitations | 529–540 | 263–272 | `LOCAL_REWRITE` | 保留单 adapter/单 profile、proxy、无跨骨干验证的限制；增加图像空间、failed bake、剂量与输出边界。原“各 regime C3 最佳”语句删除有证据边界理由。 |
| Conclusion | 541–551 | 274–279 | `LOCAL_REWRITE` | 用 Fresh C 结果、Generic Linear/GFH 反结果和 stage placement 限定替换旧 +0.96/纹理优势/ FAC 延伸结论。 |
| Data availability / competing interests / references | 552–698 | 281–425 | `LOCAL_REWRITE` / `KEEP` | 声明更新了可公开边界；参考文献主体完整保留并增补 SSI。当前候选与原稿 562–696 的 bibliography 区间逐行匹配；这一长匹配不能当正文连续性的证据。 |

## 图表与篇幅的直接原因

- 原稿 PDF：15 页；当前候选 PDF：9 页。两者均为同一 Elsevier/C&G 页面尺寸。
- 原稿：7 个 Figure 环境、9 个 Table 环境。当前：3 个 Figure 环境、2 个 Table 环境。当前主文引用的 Figure 1–3 与源稿同号图 2–3 的论证不同；原 Figure 4–7 未被引用。
- 表格减少主要来自 13-scale 结果、24-object probe/extended metrics、旧 300-object pooled/texture retention、CLIP-IQA、人评和 adapter-dependence 表；图减少来自固定 scale sweep、纹理 audit、C3 vs fixed-scale 与 schedule-selection 图。对应去向见 [`01549_ORIGINAL_CURRENT_STRUCTURE_DIFF.md`](01549_ORIGINAL_CURRENT_STRUCTURE_DIFF.md) 与 [`01549_FIGURE_PRESERVATION_REVIEW.md`](01549_FIGURE_PRESERVATION_REVIEW.md)。
- 正文从 698 行压至 430 行，主要由 `0aaefc86` 的 304 行删除/43 行增加开始；因此不能把 6 页减少归因于版面微调。

## 历史 9 页候选审计的停止点

以上逐节、逐表和篇幅分析只描述被归档的 `revision_1008/final_0903.tex` 候选快照。后续已依作者授权从官方 0907 投稿包恢复工作副本并完成第二轮修订；旧候选未被覆盖，也不是当前投稿基准。

## 当前 01549-first 第二轮交付

当前源稿 `revision_01549_restored/manuscript_1008.tex` 从认证源 `source_01549/final_0903.tex`（SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`）恢复。该认证源与 `final/submission_new_0907/latex.zip` 中的 `final_0903.tex` 字节一致；历史身份以官方 0907 Manuscript、Marked-up Manuscript、Response Letter、Supplement 和源 ZIP 为准。

已保留第一轮完成且第二轮认可的 fixed-scale 与 C3 development 证据、probe-disjoint 分析、FAC 负向受控复查和聚类感知 3AFC 结果。FAC 仍是此前报告的辅助证据；披露恢复配置列出 1,200 对 01549 所报 1,706 的不一致及缺少 run-bound seed/output manifest。3AFC 只按原问题报告主观选择的汇总结果，不外推至 Fresh C、纹理保真或 3D 质量。

Fresh C 的主要 R1.2 比较按同一冻结 checkpoint、runner、seed policy、cohort、输入、视图、指标和实际记录的 scale caps 配对解释。C3−GFL FG-PSNR 为 `+0.522352 dB`，95% CI `[+0.404160,+0.640669]`。不要求该 checkpoint 哈希匹配 01549 历史 Table 4；历史 v1/v2 实验差异如实保留，且不声称 Fresh C 重现旧 `+0.96 dB`。Generic Linear、GFH 和 LLH 的端点反结果仍在主文/补充材料呈现。

图像处置逐项如下：原 Fig. 1 以字节相同资产保留完整流程和 FAC 支路，图注仅限定其已报告状态；原 Fig. 2–3 保留作历史固定尺度诊断；原 Fig. 7 的点位/坐标保留，只局部修正评价标签，并限定为 24-object development probe；原 Fig. 4、Fig. 6 的研究问题由 matched Fresh C 全物体图组更新；原 Fig. 5 的 26-object proxy 图因记录和指标含义无法核验而退出。七张图的实际图像对照与源/当前哈希见 [`01549_FIGURE_PRESERVATION_REVIEW.md`](01549_FIGURE_PRESERVATION_REVIEW.md)、[内部七页 PDF](forensics_R2_1_20261008/01549_original_vs_current_figures_internal.pdf) 与资产清单。

当前交付为主文 11 页、主文 6 图/5 表、Supplement 10 页，以及相对认证 01549 的 marked-up PDF 20 页；按证据原因退出或移入 Supplement 的内容逐项列于 [`ORIGINAL_CONTENT_DISPOSITION.csv`](ORIGINAL_CONTENT_DISPOSITION.csv) 和 [`01549_TO_1008_CHANGELOG.md`](../submission_1008_final/01549_TO_1008_CHANGELOG.md)。页面变化来自不可追溯的 26-object proxy 与 texture-retention 结论、CLIP-IQA 结果退出，以及历史 Table 3/9 的移位和主表替换；不是为了压至 9 页。有效的 fixed-scale、C3 development、FAC 负结果和 first-round preference 结果仍保留在各自适当位置。

主文和 Supplement 的本地 TeX Live 构建成功，最终稿无未解析引用/交叉引用；in-app 编译器两次超过两分钟未返回诊断，故编辑器端结果未核实。marked-up PDF 中未解析引用仅出现在已删除的旧段落内，最终主文和 Supplement 不受影响。完整构建状态见 [`SUBMISSION_BUILD_REPORT.md`](../submission_1008_final/SUBMISSION_BUILD_REPORT.md)。
