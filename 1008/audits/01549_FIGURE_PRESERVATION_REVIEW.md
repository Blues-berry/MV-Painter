# 01549 原图与恢复修订图审阅

**审阅对象：** 经 SHA-256 认证的 01549 投稿图 `source_01549/fig1.pdf`–`fig7.pdf`，与当前交付稿 `revision_01549_restored/manuscript_1008.tex` 实际引用的图像。历史 9 页候选稿另存为归档，不作为本次右栏版本。

**实际预览：** [七图左右对照内部 PDF](forensics_R2_1_20261008/01549_original_vs_current_figures_internal.pdf)，共 7 页，每页左侧原图、右侧最终恢复稿实际引用的图或明确的“已移除”状态卡，并附论证功能、审稿质疑、建议保留方式、改动和证据限制。 [完整七图预览图](forensics_R2_1_20261008/renders/restored/all_figures_restored_preview.png) 和逐项资产哈希在 [RESTORED_FIGURE_ASSET_MANIFEST.csv](forensics_R2_1_20261008/RESTORED_FIGURE_ASSET_MANIFEST.csv)。全部原图和最终映射均已渲染检查；Fig. 1、Fig. 5（原 Fig. 7 的局部标签版）及移除的 Fig. 5 对照页另作高分辨率检查。

## 最终映射

| 原图 | 原稿论证功能 | 恢复稿实际图位 | 状态 | 依据与边界 |
|---|---|---|---|---|
| **Fig. 1** | Reference/geometry → frozen multi-view diffusion → GeoTex residual/TCAS → optional FAC → projection/baking/mesh 的全流程。 | **Fig. 1**, 主文 p. 4，TeX 101–105；与认证原图字节一致的 `figures/fig1_01549_original.pdf`。 | `KEEP_ORIGINAL_LOCAL_CAPTION_EDIT` | 原始整图设计、FAC 支路和 projection/baking 链原样保留。图注只说明 FAC 是已报告的辅助扩展并指向负向受控复查；Fresh C 不验证 baked mesh。 |
| **Fig. 2** | 13 个固定尺度下 FG-SSIM/Crop-SSIM 曲线，提出单一结构指标是否足够的问题。 | **Fig. 2**, p. 6，TeX 223–225；`fig2.pdf` 与原图字节相同。 | `KEEP` | 保留原图位与图形，标为 01549 历史诊断。底层对象行、完整运行配置和 metric 实现未能在当前权威档案复核，因此不作为新确认性结果。 |
| **Fig. 3** | 50-object × 13-scale 的对象响应热力图，显示已提交的异质性图示。 | **Fig. 3**, p. 6，TeX 232–234；`fig3.pdf` 与原图字节相同。 | `KEEP` | 原热力图恢复为历史诊断；不据此推断当前人口分布或新效应。 |
| **Fig. 4** | 固定尺度变化的选定纹理例子。 | **Fig. 4**, p. 7，TeX 247–253；3 张 Fresh C 匹配目标视角全物体图。 | `REPLACE_EVIDENCE` | 以可溯源全物体 Fresh C 图替换旧局部裁剪：近 cohort 中位数、C3–GFL 不利例、Generic Linear 反例；每张涵盖 reference 和七个推理条件。面板按结果选取，只是示例，不估计发生率，也不是烘焙网格/未见视角 PBR 证据。 |
| **Fig. 5** | 26-object RGB 标准差与梯度变化 proxy 排序，用来支持高尺度纹理压平结论。 | **无活跃对应图**；主文 p. 5–6 明确解释移除（TeX 237–242、315）。 | `REMOVE` | 对象 IDs、子集选择轨迹、原始行和可执行指标定义不可追溯；这些 proxy 只描述变化，不能证明纹理保真。右侧 PDF 显示“无活跃对应图”状态卡；Fig. 4 是不同 Fresh C 视觉证据，不冒充替代比率图。 |
| **Fig. 6** | GT / 固定低尺度 / 固定高尺度 / C3 的定性比较，连接 24-object C3 选择问题。 | **Fig. 5**, p. 8，TeX 301–305；两张 Fresh C 同对象匹配视角图。 | `REPLACE_EVIDENCE` | 保留“C3 与固定尺度比较”的研究问题，以 C3-favorable 选例和 C3–GFH endpoint trade-off 展示；对象级定量比较仍由 Fresh C Tables 3–4 承担。图中不声称总体获胜，也不是原 probe 的等价复现。 |
| **Fig. 7** | 24-object development set 上 17 个 schedule variant 的 shape–texture 图，展示 C3 来源。 | **Fig. 6**, p. 9，TeX 310–312；局部编辑资产 `figures/fig7_c3_development.pdf`。 | `LOCAL_REWRITE` | 所有点位、坐标、图例和设计风格来自原图；仅将 “Promising zone” 改为 “Development region”、将 “C3 (ours)” 改为 “C3 (probe)”。图注明确 N=24、17 variants、development-only，且原始逐点数据未复核。认证的原 PDF 保持未改。 |

## 图像和论证审阅结论

- 恢复稿主文有 **6 张图**：原 Fig. 1、2、3、7 保持各自图位/设计（Fig. 1 与 Fig. 7 仅局部处理）；原 Fig. 4 和 Fig. 6 的视觉研究问题由 Fresh C 全物体图组更新；原 Fig. 5 proxy chart 因数据可追溯性和指标含义问题明确退出。
- 原 Fig. 2/3 是提交版历史图，当前底层数据不够做新的确认性复算；保留图形和科学问题，不保留未经核实的广义结论。
- Fig. 4、5 的新图都包含竞争条件和不利例，但其对象是结果选例。Fresh C 的对象级配对表才承担频率/汇总估计。颜色偏移和重复图案示例见主 Fig. 4 与补充 Fig. S1；不得据精选面板估算失败率。
- Fig. 7 的两个评估性词组已局部改写，不改变散点数据。原图哈希与最终图哈希均在资产 manifest 中；修改脚本只读取原图并输出恢复目录新文件。
- 图中保留 projection/baking 是 pipeline 语境，不代表恢复稿验证了烘焙质量。Fresh C 烘焙输入门未通过；历史 N=20 只支持有限 unlit base-color unseen-view 观察，seam、PBR、跨视角材料质量和人评均未确立。

原图的逐文件 SHA-256、当前资产 SHA-256、主文 TeX 行号和 PDF 页码见 [资产清单](forensics_R2_1_20261008/RESTORED_FIGURE_ASSET_MANIFEST.csv)。逐节、逐表的完整内容处置见 [`ORIGINAL_CONTENT_DISPOSITION.csv`](ORIGINAL_CONTENT_DISPOSITION.csv)。
