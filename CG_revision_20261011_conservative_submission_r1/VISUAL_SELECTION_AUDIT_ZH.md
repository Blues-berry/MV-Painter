# Figure 8 代表图选择与图文对照核查

## 冻结评分口径

GeoTex Fresh C runner 将六张 256×256 目标视角排成 3 行×2 列拼图，对每个拼图整体调用冻结 evaluator。主表是每对象一个复合图像分数。脚本另行提取 view 0 计算单视角诊断，不能用它替代对象级指标。

## 选例规则和结果

候选仅限于五个此前已经有来源和 CC BY 许可记录的 Fresh C 插图对象。要求 C3 相对 Fixed Low 在对象级六视角复合 FG-PSNR、FG-LPIPS、FG-SSIM 三项均有利，并且当前展示的 view 0 三项也同向有利。该规则筛出：

| 对象 | 六视角复合差值 C3−Fixed Low | view 0 差值 C3−Fixed Low |
|---|---|---|
| Cube 01 | PSNR +1.793 dB；LPIPS −0.02430；SSIM +0.1851 | PSNR +1.817 dB；LPIPS −0.01934；SSIM +0.2073 |
| E5-5-2 | PSNR +1.265 dB；LPIPS −0.03271；SSIM +0.1615 | PSNR +1.821 dB；LPIPS −0.02523；SSIM +0.1865 |

图中每行给出完整 view 0，Reference/Fixed Low/C3 共用同一局部 ROI 并放大显示。Figure 8 是按指标方向选取的实例图，不表示总体频率；总体证据来自 300 对象完整差值图和配对统计表。Boat 不利案例仍保留在 Supplementary Figure S1。

## 复算和来源

只读取既有 PNG 输出，没有运行模型。原始 PNG 经冻结 evaluator 复算的拼图分数与浮点冻结行存在微小量化差异，分别记录在 `evidence/FRESH_C_DISPLAYED_VIEW_AUDIT.json` 和 `manuscript/figures/FIG7_METRIC_FAVORABLE_PROVENANCE.json`；冻结表与 cohort 统计均未被替换。输出、输入、UID、view、ROI、checkpoint、runner、seed 和许可信息记录在相应来源 manifest 与 `FIGURE_ASSET_CREDITS.csv` 中，Supp. Table S1 含完整署名。
