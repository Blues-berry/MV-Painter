# R1 紫色与纹理损伤：受控排查记录

## 结论摘要

在冻结的 26 个诊断对象上，粉紫/粉色偏移与细节损失已经能在 VAE 解码后的 RGB PNG 中直接观察到，早于 UV 投影、纹理烘焙和 GLB 导出。No Adapter 的外观误差最大；较强干预的 GFH 平均 CIEDE2000 高于 GFL，残差相对主干特征的幅度也更高。这些是相关证据，不足以证明残差是紫色问题的唯一根因。针对残差比例实现并实测的 feature-relative gate 未能在原始 Fig. 4/6 失败图上明显减轻粉紫外观，因此根因尚未解决。

还确认并修复了一项历史视角协议缺陷：旧评估路径的第四个参考 tile 重复第二个 tile。改为六个不同视角后，参考网格恢复正确；受控消融显示，六个历史对象的平均 CIEDE2000 只发生很小变化，因此该协议缺陷不能解释主要粉紫色和细节损伤。

## 冻结协议与范围

- 样本清单：`SAMPLE_FREEZE.json` / `SAMPLE_FREEZE.csv`。包含 6 个 01549 Fig. 4/6 原对象和 20 个已有 Fresh-C 正式视觉面板；样本经过筛选、曾被查看，是失败富集开发诊断集，不是独立确认集。
- 条件：No Adapter、GFL、GFH、C3、Generic Linear、LLH；同一当前 checkpoint、输入条件、对象种子、初始 latent、Euler 调度器、50 步、256 分辨率。
- checkpoint SHA-256：`0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`。
- 唯一视角顺序：`[0,15,12,16,13,14]`。RGB 网格为 3 行 × 2 列，单视角 256 × 256，完整 PNG 为 512 × 768。
- 主端点：对象内六个前景视角 CIEDE2000 等权平均；次端点 FG-PSNR、FG-LPIPS、Edge-SSIM。紫色 Lab 标志阈值保持冻结，但不替代连续指标和视觉检查。

## A. 颜色与数据路径

数据读取路径中，RGBA 图像由 OpenCV 的 BGRA 转 RGBA，除以 255 后以 alpha 合成到白色；法线由 BGR 转 RGB 并按 16-bit 范围归一化。目标 RGB 在训练时使用 `(x−0.5)/0.8` 输入 VAE；解码 RGB 的保存映射为 `0.8×decoded+0.5`，与该目标归一化相互对应。路径中没有单独的 sRGB↔linear 变换，训练与本轮推理沿用相同像素表示。`prepare_batch` 将目标、法线、深度和 alpha mask 以相同视角顺序重排为 3×2 网格。Normal/depth 作为几何编码器输入，不作为生成 RGB 图保存。

代码位置：`MVPainter/src/data/mvpainter_dataset.py` 的 `load_im` / `load_im_normal`，`geotex/data_utils.py` 的 `prepare_batch`。参考目标张量与冻结输入身份相符；历史六例的五个非重复 tile 与当前 unique6 参考逐像素相同。

发现的真实协议问题位于 `MVPainterData` 的默认 `target_view_mode='legacy_duplicate_top'`。旧 CLIP-IQA 评估未显式设置模式，导致第 4 个网格 tile 重复第 2 个 tile，而不是独立视角。修复限于评估入口：`geotex/eval_clipiqa.py` 现在显式设置 `unique6`；为复现旧产物仍保留数据集的 legacy 选项。它修正了目标视角，不是生成器的颜色修复。

在同一 checkpoint、同一六对象、同一六条件下，只切换 `unique6` / `legacy_duplicate_top` 的消融见 `VIEWMODE_ABLATION_COMPARISON.pdf` 与 `logs/VIEWMODE_ABLATION_SUMMARY.json`。旧模式六个对象的第四个 tile 均与第二个 tile 像素完全相同；GFL 平均 CIEDE2000 从 19.64 变为 19.80，C3 从 23.41 变为 23.53。差异很小且各对象方向不一致。结论：修复该协议缺陷可防止参考视角重复，但没有证据显示它是主要颜色损伤的根因。当前六视角 unique6 输出中没有明确观察到物体纹理图案重复；不能将重复参考视角与重复物体纹理混为一谈。

## B. 几何残差干预

逐层、逐步记录的 pre-adapter 特征幅度、已缩放残差、实际应用尺度和异常比例位于 `runs/fig4_fig6_observer/residual_logs/` 与 `runs/fresh_c_observer/residual_logs/`；汇总位于 `logs/OBJECT_RESIDUAL_FEATURE_PHASE_SUMMARY.csv` 和 `logs/OBJECT_RESIDUAL_FEATURE_AGGREGATE.csv`。

在 26 对象上的描述性平均值：GFL 残差 RMS / 特征 RMS 为 0.368，GFH 为 0.599，C3 为 0.448，Generic Linear 为 0.491，LLH 为 0.445。与它们配对的前景 CIEDE2000 分别为 17.00、21.92、18.78、21.58、20.59。适配条件的逐对象/逐方法残差比与 CIEDE2000 的 Spearman 相关为 ρ=0.181；对象与方法重复，p 值仅作描述，不作为独立推断。

同输入条件对照显示 No Adapter 平均 CIEDE2000 为 36.66，明显高于所有 Adapter 方法；因此基础生成结果本身并未解决外观匹配问题，不能把损伤简单归因于几何分支。历史例中较强 GFH 通常比 GFL 更洗白、细节更少；GFL/C3 保留更多结构，但 Fig. 4 的部分原始对象仍有可见粉色/粉紫偏色和纹理损失。连续色差比冻结的严格紫色向量阈值更敏感；严格 Lab 紫色标志在本诊断集上为 0/26。视觉复核中把明显粉色/粉紫称为可见 hue cast，不把它等同于严格 Lab 阈值通过。

这些结果支持残差幅度是可测试的干预因素，但尚未证明某个层或时间窗独自造成偏色。受控视角对照也表明，改正重复视角后输出外观变化很小。Stage 2 的唯一候选是使用冻结的 feature-relative residual envelope，直接限制每层当步残差相对主干特征的幅度；方法和结果见下方补充。

## C. 基础生成模型

六条件完整 RGB 结果见 `BASELINE_COMPARISON.pdf` 和 `raw_rgb/`。No Adapter 在部分样本中产生结构或语义不匹配；低到中等 Adapter 干预改善了整体对象匹配。高强度干预与更高的相对残差比、较高的连续颜色误差和可见的细节损失同时出现。该诊断只支持有限的强度相关结论，不能说明所有对象、所有视角都按同一方向变化。

## D. 纹理烘焙

本次保留的预测是 `generate_with_schedule` 返回的 VAE 解码 RGB，并直接由 `save_image` 保存；VAE 解码和 RGB 反归一化位于 `geotex/explore_contradiction.py` 的 `generate_with_schedule` 末尾。它们不是 normal/depth 可视化，也没有经过 UV 投影、烘焙、GLB 导出或最终渲染。因此本次确认的粉紫色和细节损伤已经存在于烘焙前 RGB，烘焙不能解释这些 PNG 中的问题。烘焙阶段仍未在这组实验中独立审计。

## Fresh-C 图像复现差异

历史图库中的 120 张 Fresh-C PNG 与本次同声明身份重跑图像全部不逐字节相同。冻结的声明输入 hash 匹配；一个无 observer hook 的 GFL 探针，其输入 hash 与冻结值逐项一致，输出又与 observer 重跑完全相同。差异的更深层原因仍未确定，不推断为特定库、硬件或隐藏状态所致。此次 Fresh-C 对照使用当前重跑图和配套 observer 日志；旧图库图像和旧指标未混入本表。证据见 `logs/FRESHC_OUTPUT_REPRODUCIBILITY.json`、`logs/FRESHC_OBSERVER_OUTPUT_IDENTITY.csv` 与 `logs/FRESHC_REPRO_PROBE_LOCK.json`。

## Stage 2：feature-relative residual envelope

候选方法在原始 TCAS 包装代码之外实现：`geotex/residual_gate.py` 与 `scripts/run_residual_gate_experiment.py`。对已按原层上限缩放的残差 `r` 和 pre-adapter 特征 `h`，计算

`q = RMS(r) / (RMS(h) + eps)`, `g = min(1, tau_depth / (q + eps))`, `h_out = h + g r`。

`tau_depth` 在新图像生成前，按冻结 GFL 日志中各深度组 `q` 的第 95 百分位一次性校准；不使用颜色、感知或人工视觉结果。阈值见 `config/feature_ratio_gate.json` 和 `logs/FEATURE_RATIO_GATE_LOCK.json`。候选条件限于 C3 + gate 和 Generic Linear + 同一 gate；`MVP_GATE_ENABLED=0` 可作为关闭门控的推理消融。方法无需训练，不增加网络前向或 VAE 解码，只增加每层 RMS、标量门控和乘法。52 次门控推理记录的每条件平均墙钟时间为 7.50–7.55 秒（CUDA:0）；没有同进程、同对象的非门控计时，故不把它解读为实测额外开销。单元测试位于 `geotex/tests/test_residual_gate.py`。

Stage 2 已在同一 26 个冻结对象上完成。两组门控使用同一预先锁定阈值：deep 1.4753、middle 0.9886、shallow 0.2609。C3 + gate 相对 C3 的总体 CIEDE2000 增加 1.35（9/26 改善、17/26 变差）；历史六例增加 3.18（0/6 改善），FG-PSNR 与 Edge-SSIM 也分别下降 1.15 和 0.0106。门控在 8.44% 的 layer-step 调用中实际衰减残差。该组合判定失败。

Linear + gate 相对 Generic Linear 在 26 个对象上改善：CIEDE2000 −1.28（24/26 改善）、FG-LPIPS −0.0013、FG-PSNR +0.345、Edge-SSIM +0.0070；20 个 Fresh-C 面板上的对应变化为 −1.12、−0.0017、+0.341、+0.0075。它在 15.04% 的 layer-step 调用中衰减残差。但相对 GFL，其 CIEDE2000 仍高 3.30，且 17/26 个对象更差；FG-PSNR 低 0.122。原始 Fig. 4/6 六例的门控视觉对比没有显示明确的粉紫减少；Fig. 4 代表例仍保留可见粉色/粉紫偏移。Fresh-C 页面中也没有稳定、明显的色彩修复信号。当前独特视角网格中未明确看到新的重复纹理；图像仍有平滑化和细节丢失。严格 Lab 紫色标志在各条件均为 0/26，说明该阈值未能捕捉已观察到的粉色偏移。

视觉标签按冻结的六视角完整网格复核：至少两个视角清楚可见才标为 present。26 个对象中，Fig. 4 的两个历史对象在多个条件中有粉色/粉紫偏移；0 个对象被标为明确的重复物体纹理；19 个对象有可见细节损失。No Adapter 在 13 个对象上有可见结构/身份不匹配；门控候选没有新增的明确结构破坏。标签及判据位于 `logs/VISUAL_REVIEW_TAGS.json`，对象-方法表位于 `OBJECT_FAILURE_TABLE.csv`。`not_observed` 只表示在当前审阅尺度下未明确看到，不证明绝对不存在；该单人复核为描述性开发集检查。

因此候选只证明对 Generic Linear 的若干离线指标有改善，未证明可以解决 R1 的视觉失败，也没有超过 GFL 主端点。按预先的阶段规则在开发集止损，不启动 Stage 3，不把该控制机制宣称为已验证的新颖方法。代码、配置、测试、完整 PNG 与配对结果仍保留供技术复核。

## 当前结论与限制

本轮确认的是两件不同的事：一是目标视角构造中有重复 tile，现已在 CLIP-IQA 评估入口明确切换到 `unique6`；二是图像在 VAE RGB 解码后已经存在可见色彩/细节偏差，因此纹理烘焙不是这些 PNG 偏色的来源。当前数据路径检查未发现 RGB/BGR、alpha 合成、normal/depth 混入 RGB 可视化等可解释这些输出的实现错误。feature-relative gate 的受控试验不支持把它当作有效修复。由此，紫色/粉色偏移的完整技术根因仍未确定，重复物体纹理也未在当前 26 个 unique6 网格中被明确复现。

另一个重要可比性限制是：冻结基线 checkpoint SHA 为 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`。早期 `revision_clipiqa` 中 `obj_0004` 的深紫色 PNG 来自不同 checkpoint（旧工件记录的 SHA 前缀为 `d27…`），且为解码后、烘焙前图像。本轮没有用旧 checkpoint 重跑完整条件矩阵，因此不能把本轮指标称为该旧工件的修复前后对照，也不能断言两次输出可直接比较。Fresh-C 的原图库图像与本轮 observer 重跑亦有 120/120 字节差异，深层原因未明；本表使用同一轮配对重跑图及其日志，排除旧图库指标。
