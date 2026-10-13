# 保守版本图像迭代

版本 conservative_visuals 从已冻结的最终保守版独立复制。Figure 7 以Building 03和Cube 01展示Fresh C中C3相对Fixed Low的代表性正向指标结果。选图条件是三项对象均值方向一致：FG-PSNR更高、FG-LPIPS更低、FG-SSIM更高；图注同时报告Edge-SSIM，含Cube 01的轻微下降。所有对象指标都是六个生成视角的均值，例图只展示同一视角。

例图服务于展示明确的正向案例，全体结果仍由300对象表格呈现；Boat对照保留在Supplementary Figure S1，烘焙主图继续呈现下游外观误差。没有新增实验，数据表与图像原始来源未改。素材许可和署名在Supplementary Table S1，选择规则和逐对象指标、来源哈希见 `manuscript/figures/FIG4_METRIC_FAVORABLE_PROVENANCE.json`。

交付目录为 `delivery_conservative_visuals`。在 `manuscript` 下运行带 `conservative_visuals` 后缀的 clean、supplement 和 marked 构建脚本。
