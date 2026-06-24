你现在在 MV-Painter / GeoTex-Adapter 项目中执行一次 CAD/Graphics full paper 补证据任务。

总目标：
补齐论文中 TCAS 的核心证据闭环，重点解决以下审稿风险：

1. 300-object validation 只有 FG-SSIM / Edge-SSIM / PSNR / FG-LPIPS，缺少纹理保留指标；
2. C3=(1.25, 2.50, 1.25) 和 0.7/0.3 阶段边界容易被认为是拍脑袋；
3. 主定性图没有直接比较 GT / s=1.25 / s=2.50 / C3；
4. baseline 只比较 s=1.25、s=2.50、C3，full paper 说服力不够；
5. 缺少 per-object win rate、bootstrap CI、object-level scatter plot 等统计证据。

严格约束：

* 不训练模型。
* 不修改已有结果文件。
* 不删除任何文件。
* 优先复用已有 inference output、raw metrics、object list、mask、GT render。
* 如果必须补跑 inference，只允许推理，不允许训练，并且先生成 run plan 和缺口清单。
* 所有新脚本、表格、图和报告输出到新目录，不污染原目录。
* 不能用旧 markdown summary 作为统计输入；必须从 raw metrics 或图像结果重新计算。
* 如果发现路径、object list、mask 定义、GT 定义不一致，先停止并写明风险，不要强行混算。

输出根目录：
mvpoutput/geotex_refattn_v1/paper_readiness_audit/cadgraphics_fullpaper_patch_v1/

需要创建以下子目录：

* 00_inventory/
* 01_texture_closure_300/
* 02_boundary_ablation/
* 03_baseline_registry/
* 04_qualitative_main_figure/
* 05_statistics/
* 06_paper_insert_material/
* logs/

第一阶段：Inventory，不要直接跑实验
请先扫描项目，找到并记录以下内容：

1. 300-object validation set 的 object id list；
2. 24-object probe set 的 object id list；
3. 50-object scale sweep set 的 object id list，如果存在；
4. s=1.25、s=2.50、C3 的 300-object 输出图路径；
5. 对应 GT render 路径；
6. 对应 foreground mask / alpha / valid mask 路径；
7. 现有 raw metrics 路径，包括 FG-SSIM、Edge-SSIM、PSNR、FG-LPIPS；
8. 现有 17 个 variant 的输出或 raw metrics；
9. 是否存在 C2、C4、Default scale、No Adapter / Base MVPainter 的结果；
10. 当前代码中 TCAS 时间步方向和 boundary 语义，明确 0.7/0.3 对应的 early/middle/late 是如何实现的。

输出：
00_inventory/inventory_report.md
00_inventory/path_manifest.json
00_inventory/missing_items.json
00_inventory/risk_notes.md

如果关键路径缺失，不要直接猜路径。先用 find / grep / python glob 做路径发现，并把候选路径写入 inventory_report.md。

第二阶段：300-object 纹理指标闭环
目标：
在与 Table 3 相同的 300-object validation set 上，为 s=1.25、s=2.50、C3 重新计算纹理诊断指标。

必须计算的指标：

1. Laplacian Variance，记为 Lap Var ↑；
2. RGB Standard Deviation，记为 RGB Std ↑；
3. Gradient Magnitude，记为 Gradient Mag ↑；
4. Texture Loss Rate ↓；
5. 每个方法的 absolute metric；
6. 相对 s=1.25 的 delta 和 ratio；
7. C3 相对 s=2.50 的 per-object win rate。

指标计算要求：

* 所有指标只在 foreground / valid mask 区域计算。
* 如果生成结果是 6-view grid，要么沿用当前论文已有指标协议，要么按每个 view 分开计算再对 object 平均，必须在 report 中写清楚。
* 所有方法必须使用同一 object list、同一 GT、同一 mask、同一分辨率。
* Lap Var 建议在灰度前景区域上计算。
* RGB Std 建议在 foreground pixels 上计算，可以报告 RGB 三通道平均 std。
* Gradient Mag 建议用 Sobel 或 Scharr，在灰度图上计算 foreground mean。
* 对于 mask 边界，应尽量沿用已有 FG-SSIM 的 mask 协议；如果需要 erosion，必须同时报告 no-erosion 和 erosion 版本，默认主表使用与现有 FG 指标一致的协议。
* Texture Loss Rate 至少给出两个定义：
  A. Lap Var ratio < 1.0 的对象比例；
  B. Lap Var、RGB Std、Gradient Mag 至少两项低于 s=1.25 的对象比例。
* 如有必要，可额外给 threshold=0.95 的严格版本，避免极小波动造成误判。

需要输出的表：

1. absolute summary table：
   Method | FG-SSIM ↑ | Edge-SSIM ↑ | PSNR ↑ | FG-LPIPS ↓ | Lap Var ↑ | RGB Std ↑ | Gradient Mag ↑ | Texture Loss Rate ↓

2. relative texture table：
   Method | ΔFG-SSIM ↑ | ΔLap Var →0 | ΔRGB Std →0 | ΔGradient →0 | Lap Var Ratio | RGB Std Ratio | Gradient Ratio | Assessment

其中：

* s=2.50 的 assessment 应判断是否为 shape gain with texture loss；
* C3 的 assessment 应判断是否为 better trade-off；
* 不允许在结果不支持时强行写结论。若 C3 不优于 s=2.50，要如实标注。

需要输出文件：
01_texture_closure_300/per_object_texture_metrics.csv
01_texture_closure_300/summary_absolute.csv
01_texture_closure_300/summary_relative_to_s125.csv
01_texture_closure_300/texture_loss_rate.csv
01_texture_closure_300/texture_closure_report.md
01_texture_closure_300/texture_closure_table_for_paper.md

第三阶段：阶段边界消融
目标：
证明 C3 的 0.7/0.3 阶段边界不是拍脑袋。

优先使用 24-object probe set。若资源允许，再对 C3-0.6/0.4、C3-0.7/0.3、C3-0.8/0.2 在 50-object 或 100-object 上补充验证。

必须比较以下 5 组：

1. C3-0.6/0.4: early=1.25, middle=2.50, late=1.25, boundary=0.6/0.4
2. C3-0.7/0.3: early=1.25, middle=2.50, late=1.25, boundary=0.7/0.3
3. C3-0.8/0.2: early=1.25, middle=2.50, late=1.25, boundary=0.8/0.2
4. Early-high: early=2.50, middle=1.25, late=1.25, boundary=0.7/0.3
5. Late-high: early=1.25, middle=1.25, late=2.50, boundary=0.7/0.3

如果已有 C2、C4、B2、B6 等 17 variants 的 raw metrics，要把它们合并进附表，但主表至少保留上述 5 组。

计算指标：

* ΔFG-SSIM ↑
* ΔLap Var →0
* ΔRGB Std →0
* ΔGradient →0
* PSNR
* FG-LPIPS
* Texture Loss Rate
* Assessment / Comment

注意：

* Δ 的 baseline 必须和原论文 Table 2 协议一致。如果原协议是相对 no-adapter，就沿用 no-adapter；如果原协议是相对 s=1.25，就沿用 s=1.25。不要混用。
* 如果原协议不明确，先输出 protocol_check.md，并给出推荐协议，不要直接写死。

需要输出的主表：
Variant | Early | Middle | Late | Boundary | ΔFG-SSIM ↑ | ΔLap Var →0 | ΔRGB Std →0 | ΔGradient →0 | Comment

Comment 建议但必须由数据支持：

* C3-0.6/0.4: weak geometry 或 under-correction；
* C3-0.7/0.3: selected / balanced；
* C3-0.8/0.2: more texture loss 或 over-correction；
* Early-high: unstable；
* Late-high: texture trap。

需要输出文件：
02_boundary_ablation/boundary_ablation_results.csv
02_boundary_ablation/boundary_ablation_table_for_paper.md
02_boundary_ablation/boundary_ablation_report.md
02_boundary_ablation/boundary_ablation_plot.svg
02_boundary_ablation/boundary_ablation_plot.pdf
02_boundary_ablation/boundary_ablation_plot.png

第四阶段：baseline registry 和主表扩展
目标：
检查是否能把 full paper 的主表从 s=1.25 / s=2.50 / C3 扩展为更合理 baseline。

需要检查并尽量纳入：

1. No Adapter / Base MVPainter；
2. Default MVPainter scale；
3. Uniform s=1.25；
4. Uniform s=2.50；
5. C2 / alternative timestep schedule；
6. C4 / late-stage high scale；
7. C3 / TCAS。

输出 baseline availability table：
Baseline | Exists? | Output Path | Metrics Path | Same 300 Objects? | Same Seed? | Can Be Used in Main Table? | Notes

如果某个 baseline 不存在，不要伪造，不要用不同 object set 混入主表。可以放到 missing baseline list。

需要输出：
03_baseline_registry/baseline_availability.md
03_baseline_registry/baseline_availability.csv
03_baseline_registry/main_table_candidates.md
03_baseline_registry/missing_baselines.md

第五阶段：统计显著性和对象级分布
目标：
让论文从“展示平均值”变成“对象级统计可信”。

至少计算：

1. C3 vs s=2.50 的 PSNR per-object win rate；
2. C3 vs s=2.50 的 Lap Var retention win rate；
3. C3 vs s=2.50 的 RGB Std retention win rate；
4. C3 vs s=2.50 的 Gradient retention win rate；
5. C3 的 FG-SSIM 是否不低于 s=2.50 的对象比例；
6. C3 的 FG-SSIM 是否在 s=2.50 的 0.005 或 0.01 tolerance 内的对象比例；
7. bootstrap 95% CI：

   * mean PSNR(C3 - s=2.50)
   * mean FG-SSIM(C3 - s=2.50)
   * mean Lap Var ratio difference
   * mean RGB Std ratio difference
   * mean Gradient ratio difference

Bootstrap 要求：

* object-level bootstrap；
* 10000 resamples；
* 固定随机种子；
* 输出 mean、median、95% CI、p-value 或 sign-test 结果，如果方便。

需要图：

1. scatter plot：x = ΔFG-SSIM，y = ΔLap Var，标出 s=2.50 和 C3 的分布；
2. scatter plot：x = ΔFG-SSIM，y = ΔGradient；
3. optional histogram：C3 - s=2.50 的 PSNR per-object difference；
4. optional histogram：C3 - s=2.50 的 Lap Var retention difference。

需要输出：
05_statistics/win_rate_summary.csv
05_statistics/bootstrap_ci.csv
05_statistics/statistical_report.md
05_statistics/scatter_fgssim_lapvar.svg
05_statistics/scatter_fgssim_lapvar.pdf
05_statistics/scatter_fgssim_lapvar.png
05_statistics/scatter_fgssim_gradient.svg
05_statistics/scatter_fgssim_gradient.pdf
05_statistics/scatter_fgssim_gradient.png

第六阶段：主定性图 GT / s=1.25 / s=2.50 / C3 / zoom-in
目标：
重做论文核心定性图，直接展示 C3 相对 uniform high scale 的纹理保留优势。

图结构：
Object | GT | s=1.25 | s=2.50 | C3 | Zoom: s=2.50 vs C3

选 2–3 个对象即可，但必须是最有说服力的案例。

选例标准：

1. s=2.50 的 FG-SSIM 高于或接近 s=1.25；
2. s=2.50 的 Lap Var / RGB Std / Gradient 明显低于 s=1.25；
3. C3 的 FG-SSIM 接近 s=2.50；
4. C3 的 Lap Var / RGB Std / Gradient 明显优于 s=2.50；
5. 视觉上能看出 s=2.50 颜色收敛、表面平滑或高频细节消失；
6. C3 能保留更多局部颜色变化、材质细节或边缘纹理；
7. 避免选择 GT 本身过差、mask 错误、渲染失败、背景异常的对象。

Zoom-in 要求：

* 每个对象至少一个局部放大区域；
* zoom 区域应覆盖纹理退化最明显的位置；
* 可以手动或自动选择。若自动选择，优先选择 s=2.50 相对 s=1.25 gradient loss 最大、且 C3 有恢复的位置；
* 输出 selected_cases.json，记录 object id、view id、crop box、选择理由、对应指标。

图像输出要求：

* 必须输出 svg、pdf 和高分辨率 png；
* 图中文字、边框、箭头尽量矢量；
* 不要用截图；
* png 至少 600 dpi 或长边 ≥ 4000 px；
* 颜色边框可以用：

  * s=1.25：green
  * s=2.50：red
  * C3：blue 或 orange
    但要保证图例清楚；
* 图注中明确说明 uniform high-scale adapter injection 会改善结构但压制局部颜色变化和高频细节，TCAS 在保持类似结构对齐的同时减少 late-stage texture over-smoothing。

建议英文图注：
While uniform high-scale adapter injection improves structural alignment, it tends to suppress local color variations and high-frequency texture details. TCAS preserves comparable foreground structure while reducing late-stage texture over-smoothing.

需要输出：
04_qualitative_main_figure/main_qualitative_gt_s125_s250_c3.svg
04_qualitative_main_figure/main_qualitative_gt_s125_s250_c3.pdf
04_qualitative_main_figure/main_qualitative_gt_s125_s250_c3.png
04_qualitative_main_figure/selected_cases.json
04_qualitative_main_figure/figure_caption_en.txt
04_qualitative_main_figure/figure_caption_zh.txt
04_qualitative_main_figure/qualitative_selection_report.md

第七阶段：生成论文可直接插入材料
最后整理所有结果，输出一个 paper_insert_material.md，包含：

1. 300-object texture closure table；
2. boundary ablation table；
3. extended baseline table，如果数据可靠；
4. per-object win rate 和 bootstrap CI 的文字总结；
5. 主定性图图注；
6. 可直接粘贴进论文的英文段落，包括：

   * Large-scale texture validation paragraph；
   * Boundary ablation paragraph；
   * Statistical reliability paragraph；
   * Qualitative comparison paragraph；
7. 风险说明：

   * 哪些结果强；
   * 哪些结果弱；
   * 哪些 baseline 缺失；
   * 哪些结论不能写太满。

要求：

* 不允许夸大结果。
* 如果某项结果不支持 C3，必须如实写。
* 所有数值必须来自 CSV/JSON raw outputs。
* Markdown 表格必须和 CSV 一致。
* 在报告最后写一个 final checklist：

  * 300 texture closure: PASS / PARTIAL / FAIL
  * boundary ablation: PASS / PARTIAL / FAIL
  * qualitative figure: PASS / PARTIAL / FAIL
  * baseline comparison: PASS / PARTIAL / FAIL
  * statistical evidence: PASS / PARTIAL / FAIL

最终需要输出：
06_paper_insert_material/paper_insert_material.md
06_paper_insert_material/final_checklist.md
06_paper_insert_material/all_outputs_manifest.json

执行顺序：

1. 先做 inventory；
2. 再做 300-object texture closure；
3. 再做 statistics；
4. 再做 boundary ablation；
5. 再做 baseline registry；
6. 再做 qualitative main figure；
7. 最后整理 paper_insert_material。

请开始执行。先不要跑新的大规模 inference。先完成 inventory，并给出缺失项和下一步计划。
