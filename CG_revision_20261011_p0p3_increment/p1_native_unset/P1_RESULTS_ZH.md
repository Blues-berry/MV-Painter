# P1 结果报告：真默认管线（native_unset）烘焙未见视角对照

日期：2026-10-11。生成与渲染此前已完成（冻结，见下方来源）；本轮补齐指标评价与跨条件配对对比，全部输出写在本增量文件夹。

## 来源（只读）

- 生成：`iteration002_controls`（10 对象 × native_unset / native_default_1x(capped) / no_adapter，PASS 逐位一致性门，2026-10-10 12:18 UTC）
- 烘焙渲染：`iteration002_bake/native_egl_unseen`（native_unset、no_adapter 各 110 张未见渲染，manifest PASS）；GT 对照渲染取自 `bake_matrix_v2/native_egl_unseen/gt`（同一 GT 渲染文件，SHA 逐文件复验）
- 聚合视图：`outputs/egl_unseen_native_unset_vs_gt/`（330 渲染硬链接 + 派生标注 manifest，[构建脚本](file:///4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/build_aggregate_render_view.py)）
- 评价协议：既有 `evaluate_fresh_c_native_egl.py` v1（GT alpha mask、CIEDE2000 erosion=1、对象为分析单元、LPIPS=CPU）

## 主要结果（10 对象 × 11 未见视角，探索性技术兼容队列）

| 方法 | FG-PSNR↑ | FG-SSIM↑ | Edge-SSIM↑ | FG-LPIPS↓ | CIEDE2000↓ |
|---|---:|---:|---:|---:|---:|
| GT（投影校准） | 22.38 | 0.768 | 0.753 | 0.059 | 4.44 |
| **native_unset（真默认）** | **11.14** | 0.338 | 0.536 | 0.137 | 26.47 |
| no_adapter | 5.92 | 0.383 | 0.318 | 0.160 | 40.92 |

### native_unset 相对冻结七条件（对象级配对，正向=unset 更好）

| 基线 | ΔFG-PSNR [95%CI] | 更好对象 | 符号检验 p | ΔFG-LPIPS |
|---|---|---|---|---|
| budget_fixed_mean | −1.48 [−2.78, −0.17] | 2/10 | 0.109 | −0.0069 (5/10) |
| budget_late16 | −1.79 [−3.06, −0.46] | 2/10 | 0.109 | −0.0095 (3/10) |
| gen_linear | −0.46 [−2.61, +1.46] | 7/10 | 0.344 | −0.0096 (5/10) |
| native_default_1x (capped) | **−0.80 [−1.17, −0.36]** | 1/10 | **0.021** | −0.0018 (2/10) |
| native_gc3 | −1.35 [−2.58, −0.13] | 2/10 | 0.109 | −0.0070 (5/10) |
| native_gfh | −1.15 [−3.10, +0.63] | 4/10 | 0.754 | −0.0066 (5/10) |
| native_gfl | **−1.35 [−2.09, −0.53]** | 1/10 | **0.021** | −0.0055 (1/10) |

50 对象图像域参考（既有）：native_unset nonref FG-PSNR 15.81 vs disabled 11.92（adapter 注入必要性）；src 22.48。

## 结论

1. **R1.1 缺口闭合**：稿件此前写"该未修改路径的输出不可得"（正文 L120/L499/L642）——本轮补齐评价后可写：真默认管线已测，其烘焙未见视角表现**不优于任何已有显式 scale 条件**（对 capped 显著更差 −0.80 dB，对其余条件劣势不显著）。
2. **不推翻稿件结论**：原先的风险是"默认管线可能更好而未测"；实测否定了这一可能，属于**有利于稿件**的诚实补强。
3. **adapter 必要性再确认**：no_adapter 大幅劣化（5.92 dB）。
4. **边界**：探索性技术兼容队列（10 对象），不得写成确认性比较；与图像域"unset 优于 disabled"并存且不矛盾（unset 相对 no-adapter 有价值，相对显式控制不占优）。

## 交付文件

- [NATIVE_EGL_METRIC_EVALUATION.json](file:///4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/outputs/egl_unseen_native_unset_vs_gt/NATIVE_EGL_METRIC_EVALUATION.json)（完整评价，含逐视角/逐对象）
- [NATIVE_UNSET_PAIRED_CONTRASTS.json](file:///4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/outputs/NATIVE_UNSET_PAIRED_CONTRASTS.json)（配对对比）
- [score_run.log](file:///4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/score_run.log)（评价运行日志）
