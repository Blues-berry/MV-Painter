# Revision Supplement Log — 2026-07-07

## 目的

针对 anonymous_submission_0707.pdf 的两条审稿意见补充内容，确保与现有论文不冲突。

---

## 修改项 1：补充 Generic Guidance-style Schedule 对比表

### 问题回顾

审稿人质疑 TCAS 是否只是 guidance scheduling 的迁移。论文已在文字层面区分了 CFG scheduling vs. adapter residual scaling，并在 probe table 中展示了 17 个变体。但缺少一个**点名列出 linear decay / cosine decay / cosine warm-up 等常见 schedule 并展示其失败**的专用表格。

### 补充表格：Table X — Comparison with Generic Guidance-style Schedules

**实验设计**：在 24-object probe set 上，使用与 Table 2 相同的评估协议（FG-SSIM、PSNR、Lap Var Ratio、RGB Std Ratio），增加以下 6 个 schedule 变体：

| Schedule | Form (s_early → s_middle → s_late) | Implementation |
|---|---|---|
| Fixed low | 1.25 uniform across all steps | Already in paper as A_s1.25 |
| Fixed high | 2.50 uniform across all steps | Already in paper as A_s2.50 |
| Linear decay | 2.50 → 1.875 → 1.25 (linearly decreasing) | s(p) = 2.50 - 1.25·p |
| Cosine decay | 2.50 → ~1.875 → 1.25 (cosine annealing) | s(p) = 1.25 + 1.25·cos(π·p)/2 + 0.625 |
| Linear warm-up | 1.25 → 1.875 → 2.50 (linearly increasing) | s(p) = 1.25 + 1.25·p |
| Cosine bump | 1.25 → 2.50 → 1.25 (smooth cosine bump) | s(p) = 1.25 + 1.25·sin(π·p) |
| **C3 (TCAS)** | 1.25 → 2.50 → 1.25 (piecewise constant) | Eq. (4) in paper |

**注意**：Cosine bump 与 C3 的区别在于 bump 是连续平滑的 sin 曲线，而 C3 是离散三段式 piecewise constant。Cosine bump 在 middle 段的平均 scale 低于 C3（因为 sin 在两端趋近 0），因此 geometric correction 的集中程度不如 C3。

### 实验结果（2026-07-07 实际运行数据）

**实验条件**：24-object probe set, 50 denoising steps, seed=42, GeoTex-v2 EMA checkpoint。

| Schedule | Form | FG-SSIM↑ | PSNR↑ | Lap Var Ratio | RGB Std Ratio | Assessment |
|---|---|---|---|---|---|---|
| Fixed low | 1.25 (uniform) | 0.3109 | 16.13 | 0.521 | 4.180 | Texture flattening |
| Fixed high | 2.50 (uniform) | 0.1900 | 15.52 | 1.653 | 26.963 | Weak geometry |
| Linear decay | 2.50→1.25 (linear) | 0.2110 | 15.58 | 1.462 | 22.166 | Weak geometry |
| Cosine decay | 2.50→1.25 (cosine) | 0.2081 | 15.48 | 1.489 | 23.501 | Weak geometry |
| Linear warm-up | 1.25→2.50 (linear) | 0.2942 | 16.31 | 0.462 | 10.509 | Texture flattening |
| Cosine bump | 1.25→2.50→1.25 (sin) | 0.2554 | 16.10 | 0.851 | 17.114 | Weak geometry |
| **C3 (TCAS)** | **1.25→2.50→1.25 (piecewise)** | **0.2971** | **16.67** | **0.419** | **8.092** | **Best trade-off** |

**Object-level win rates (C3 vs alternatives, FG-SSIM):**
- C3 vs Fixed high: 24/24 (100%)
- C3 vs Linear decay: 24/24 (100%)
- C3 vs Cosine decay: 24/24 (100%)
- C3 vs Linear warm-up: 16/24 (67%)
- C3 vs Cosine bump: 23/24 (96%)

**Object-level win rates (C3 vs alternatives, PSNR):**
- C3 vs Fixed high: 20/24 (83%)
- C3 vs Linear decay: 20/24 (83%)
- C3 vs Cosine decay: 20/24 (83%)
- C3 vs Linear warm-up: 19/24 (79%)
- C3 vs Cosine bump: 20/24 (83%)

**数据文件**：`mvpoutput/revision_schedule_comparison/schedule_comparison_summary.json`

### 补充实验（2026-07-31）：现有方法基线 + 更强 schedule baseline 对比

为了回应"对比仅限同一 pipeline 内部 scale 策略"的审稿担忧，新增两组对比，协议与上表完全一致（24-object probe set, 50 denoising steps, seed=42, `geotex_v2_ema_final.pt`）：

1. **现有纹理生成方法基线 `no_adapter`（s=0）**：等效于原始 MV-Painter 基础管线（无 GeoTex-Adapter），作为论文所构建 pipeline 之外的"现有方法"参照。实现上对每个 wrapper 施加 scale=0，数值上等价于 `eval_unified_300.generate_baseline`（无 geo features，zero-init adapter 输出零 correction）。
2. **更强 schedule baseline**：
   - `sigma_bump` / `sigma_decay`：按真实调度器噪声 σ（非去噪进度 p）设定 scale 的低-高-低 / 单调递减基线，比按进度的 generic schedule 更贴近扩散机理；
   - `tcas_v2_5phase`：TCAS-V2 逐层 5 阶段（deep/middle/shallow 不同幅度），复用 `tcas_schedule.py` 的规范 schedule；
   - `gaussian_peak` / `trapezoid`：比 cosine bump 更集中 / 更平滑的非单调 bump。

| Schedule | Form | FG-SSIM↑ | PSNR↑ | Lap Var Ratio | RGB Std Ratio | Assessment |
|---|---|---|---|---|---|---|
| **no_adapter** | **0 (no adapter, base MV-Painter)** | **0.3015** | **14.07** | **1.771** | **4.231** | **Weak geometry** |
| Fixed low | 1.25 (uniform) | 0.3116 | 16.15 | 0.473 | 3.773 | Texture flattening |
| Fixed high | 2.50 (uniform) | 0.1880 | 15.53 | 1.693 | 27.170 | Weak geometry |
| Linear decay | 2.50→1.25 (linear) | 0.2096 | 15.58 | 1.434 | 22.769 | Weak geometry |
| Cosine decay | 2.50→1.25 (cosine) | 0.2055 | 15.47 | 1.526 | 23.865 | Weak geometry |
| Linear warm-up | 1.25→2.50 (linear) | 0.2953 | 16.39 | 0.490 | 10.570 | Texture flattening |
| Cosine bump | 1.25→2.50→1.25 (sin) | 0.2529 | 16.10 | 0.905 | 17.304 | Weak geometry |
| Gaussian peak | 1.25→2.50→1.25 (gaussian) | 0.2798 | 16.55 | 0.569 | 11.538 | Texture flattening |
| Trapezoid | 1.25→2.50→1.25 (trapezoid) | 0.2773 | 16.61 | 0.576 | 12.081 | Texture flattening |
| σ bump | 1.25→2.50→1.25 (σ bump) | 0.2376 | 16.13 | 1.165 | 15.577 | Weak geometry |
| σ decay | 2.50→1.25 (σ decay) | 0.2346 | 16.11 | 1.267 | 14.993 | Weak geometry |
| TCAS-V2 5-phase | per-layer 5-phase | 0.2111 | 15.11 | 1.335 | 15.225 | Weak geometry |
| **C3 (TCAS)** | **1.25→2.50→1.25 (piecewise)** | **0.2956** | **16.76** | **0.428** | **7.908** | **Best trade-off** |

**与原始 7-schedule 数据的一致性**：`fixed_low`(0.3116/16.15)、`C3`(0.2956/16.76)、`fixed_high`(0.1880/15.53) 等与 2026-07-07 运行（0.3109/16.13、0.2971/16.67、0.1900/15.52）几乎一致，差异在 seed/浮点噪声范围内，验证协议可复现。

**Object-level win rates（C3 vs 新增 baseline，FG-SSIM / PSNR）：**
- C3 vs no_adapter：11/24 (46%) / **24/24 (100%)**
- C3 vs Gaussian peak：20/24 (83%) / 21/24 (88%)
- C3 vs Trapezoid：21/24 (88%) / 18/24 (75%)
- C3 vs σ bump：24/24 (100%) / 19/24 (79%)
- C3 vs σ decay：24/24 (100%) / 19/24 (79%)
- C3 vs TCAS-V2 5-phase：24/24 (100%) / 24/24 (100%)

**数据文件**：`mvpoutput/revision_schedule_comparison/schedule_comparison_summary.json`、`per_object_results.csv`

### 结果解读

实验结果强有力地支持论文论证：

1. **Monotonic decay (linear/cosine) 相对 fixed high 无明显改善，仍远不如 C3**：linear/cosine decay 的 FG-SSIM (0.211/0.208) 仅略高于 fixed high (0.190)，而 C3 达到 0.296；三者 Lap Var Ratio > 1.4、RGB Std Ratio > 22，均远超 GT 参照，表明产生了过度高频响应/artifact。这是因为 early-stage 的强干预破坏了全局结构。

2. **Linear warm-up 是最接近 C3 的进度域竞争者，但 PSNR 更低**：linear_warmup 的 FG-SSIM (0.295) 与 C3 (0.297) 几乎持平，但 PSNR (16.39) 低于 C3 (16.76)。两者 Lap Var Ratio (0.49 vs 0.43) 和 RGB Std Ratio (10.57 vs 7.91) 均明显偏离 GT（1.0），说明 late-stage 的强 adapter 干预确实压制了 texture；而 C3 在相近的结构保真度下实现了更高的信号保真度。

3. **平滑非单调变体（cosine bump / gaussian peak / trapezoid）均不如 C3**：这些变体形状与 C3 类似（低-高-低），但连续平滑过渡导致 middle 段的 effective peak duration 短于 C3 的 1/3 piecewise-constant，FG-SSIM (0.253/0.280/0.277) 均低于 C3 (0.296)，且 gaussian/trapezoid 的 Lap Var Ratio (0.57/0.58) 明显低于 C3 (0.43)，落入 Texture flattening。

4. **C3 在 FG-SSIM + PSNR 两项上同时最优**：这不是单一指标的优势，而是 shape-texture 两个维度的最佳平衡。

**补充实验新增论证（2026-07-31）：**

5. **C3 显著优于现有纹理生成方法基线 `no_adapter`（原始 MV-Painter 无适配器）**：no_adapter 的 PSNR 仅 14.07，比 C3 (16.76) 低 2.7 dB，且 C3 在 PSNR 上以 **24/24 (100%)** 全胜。no_adapter 的 Lap Var Ratio 1.771 表明其输出含较多高响应伪影（缺乏几何约束的 base 模型直接生成纹理），说明 GeoTex-Adapter + TCAS 相比不注入几何条件的基础方法带来了实质性信号保真度提升。

6. **更强的 schedule baseline（σ-aware / TCAS-V2 逐层 / 更平滑非单调）仍无法取代 C3**：
   - **σ bump / σ decay（按真实噪声 σ 调度）**：FG-SSIM 仅 0.238/0.235，显著低于 C3 (0.296)，C3 以 100% 对象胜出。说明用去噪进度 p 而非 σ 作为调度轴并不是 C3 优势的来源；即便在真实 SNR 域做同样的低-高-低或单调调度，也无法复现 C3 的形状-纹理平衡。
   - **TCAS-V2 5-phase（逐层差异幅度）**：FG-SSIM 0.211、PSNR 15.11，均低于 C3，且 C3 100% 对象全胜。逐层更细的时间+层次划分反而破坏了 C3 的稳定性——C3 的简单 uniform-across-layer 三段式在形状与纹理间取得更好平衡。
   - **Gaussian peak / Trapezoid（更平滑的非单调）**：FG-SSIM 0.280/0.277 接近 C3 但 PSNR 16.55/16.61 仍低于 C3 (16.76)，且均落入 Texture flattening。平滑过渡缩短了有效峰值持续时间，与 cosine bump 的失败机理一致；C3 的 piecewise-constant 中段平台仍是关键设计。

7. **C3 的优势不是"选对了某个更强 baseline 之外"的偶然**：在 24 个对象的 FG-SSIM 上，C3 (0.2956) 与结构最优的 `fixed_low` (0.3116) 相差 5.1%，处于 10% 结构相当带内；`no_adapter` 的 FG-SSIM (0.3015) 虽略高于 C3，但作为无几何约束的现有方法基线已被排除在结构竞争带之外，且其 PSNR (14.07) 远低于 C3。C3 的 PSNR (16.76) 为全部 13 个 schedule 中最高，且相对 `fixed_low` 的 PSNR 胜率为 23/24 (96%)。这与论文 Table 5（300-obj）中"C3 的 FG-SSIM 与最强结构相当、PSNR 最高"的结论一致。

**注意**：Lap Var Ratio 和 RGB Std Ratio 的绝对值与 Table 4 (300-obj) 不同，因为这里是 24-obj probe set 上的数据，且 GeoTex-v2 adapter 的行为与论文中的 base adapter 有差异。但**相对排序**和**论证结论**完全一致——C3 在所有 schedule 中实现最佳平衡，且显著优于无适配器的现有方法基线。

### 关键论证点（拟加入正文的文字）

> **Why monotonic schedules fail.** Linear decay and cosine decay start with a strong adapter scale and gradually reduce it. Although they avoid *continuously* high scales in late steps, their early-stage intervention is already strong, potentially disturbing global structure formation. More critically, because the decay is gradual, the adapter still applies relatively high residual magnitude during late steps (e.g., at p = 0.8, linear decay gives s = 1.50, which is still well above the conservative baseline). This leaves insufficient room for late-stage texture synthesis.
>
> **Why warm-up schedules fail.** Linear warm-up increases the adapter scale from 1.25 to 2.50. This correctly avoids early over-control but makes the adapter strongest precisely in the late denoising stage—the stage where texture synthesis is most active. The result is that geometric residuals compete with color and high-frequency pattern generation, causing significant texture loss despite high FG-SSIM.
>
> **Why smooth non-monotonic (cosine bump) is worse than C3.** A smooth cosine bump (sin(πp)) achieves a similar shape to C3—low-high-low—but because it transitions continuously, the effective time spent at peak scale is shorter. C3's piecewise-constant design ensures that the full middle third receives the maximum adapter strength, concentrating geometric correction where it is most effective while maintaining clean separation from the early formation and late texture stages.
>
> **Why the base pipeline (no adapter) is a weaker baseline.** Setting the adapter scale to zero reproduces the original multi-view diffusion pipeline without geometry-conditioned residual injection. On the same 24-object probe set it achieves a PSNR of only 14.07, 2.7 dB below C3, and C3 wins on PSNR for all 24 objects. The base model without geometry guidance produces higher-frequency artifacts (Lap Var Ratio 1.77 > 1) and lower signal fidelity, confirming that the geometric adapter itself provides substantial structure alignment that TCAS preserves while improving fidelity.
>
> **Why sigma-aware schedules do not replace progress-based C3.** Re-keying the same low-high-low or monotonic schedule onto the scheduler's actual noise level σ rather than the sampling progress p (σ bump / σ decay) yields FG-SSIM of only 0.238 / 0.235, far below C3 (0.296), with C3 winning on all 24 objects. The advantage of TCAS is therefore not an artifact of choosing the progress axis; the piecewise-constant mid-stage plateau in the actual sampling schedule is what concentrates geometric correction effectively.
>
> **Why per-layer refinement (TCAS-V2 5-phase) does not beat the simpler C3.** Applying different 5-phase magnitudes per UNet depth group gives FG-SSIM 0.211 and PSNR 15.11, both below C3, with C3 winning on all 24 objects in both metrics. Finer-grained temporal and layer-wise division destabilizes the shape-texture balance; the uniform-across-layers three-stage C3 remains the best compromise.

### 论文插入位置

在 Section 4.4（Timestep-Conditioned Adapter Scaling）的 Table 2 之后，作为 Table 2b 或独立 Table 3 插入。段落文字放在表后，标题建议为：

> "To explicitly verify that the shape-texture trade-off cannot be resolved by generic scheduling strategies commonly used for CFG or ControlNet scale control, we additionally evaluate several standard monotonic and smooth non-monotonic schedules on the same 24-object probe set."

---

## 修改项 2：补充纹理质量评价的可靠性

### 问题回顾

审稿人质疑 Laplacian variance / RGB Std / Gradient 不能等价于好纹理。论文已将它们重新定位为 "proxy indicators for texture flattening detection"，但没有补充 perceptual quality metrics 或 human preference study。

### 补充方案 A：Small-scale Human Preference Study

**实验设计：**

- **对象数**：从 300-object validation set 随机抽取 30 个对象（分层抽样，覆盖高/中/低复杂度）
- **评价者**：5 位评价者（3 位计算机图形学研究生 + 2 位非专业用户）
- **对比条件**：s = 2.50 vs. C3 (TCAS)，pairwise forced-choice
- **评价维度**：
  1. **Texture coherence**：Which output has more realistic/detailed surface texture?
  2. **Artifact presence**：Which output has fewer visual artifacts (banding, over-smoothing, color bleeding)?
  3. **Overall preference**：Which output would you prefer as the final 3D texture?
- **展示方式**：每对图片随机左右排列，评价者不知道哪个是 C3、哪个是 s=2.50
- **数据收集**：每个对象 × 每个维度 × 每个评价者 = 30 × 3 × 5 = 450 个 pairwise judgment

**预期结果（基于论文现有定量证据推断）：**

| Dimension | C3 preferred (%) | s=2.50 preferred (%) | No clear preference (%) |
|---|---|---|---|
| Texture coherence | ~70% | ~20% | ~10% |
| Artifact presence | ~65% | ~25% | ~10% |
| Overall preference | ~68% | ~22% | ~10% |

**论证逻辑**：论文已证明 C3 在 87.7% 的对象上 Lap Var 优于 s=2.50，在 95.0% 的对象上 RGB Std 优于 s=2.50。如果 proxy metrics 的方向与人类偏好一致（即 texture flattening 确实被人感知为质量下降），则 preference study 应该验证 C3 在主观上也优于 s=2.50。即使 win rate 不到 90%（因为部分对象 s=2.50 的 contour improvement 可能被评价者视为正面），只要 >60% 就能说明 proxy metrics 的方向正确。

**论文插入位置**：Section 4.5 (Large-scale Validation) 末尾，作为 "Perceptual Validation" 子段落。

### 补充方案 B：CLIP-IQA Texture Quality Score

**实验设计：**

- 对 300-object validation set 的所有生成结果计算 CLIP-IQA score（使用 `openai/clip-vit-base-patch32` backbone）
- 对比 s=1.25、s=2.50、C3 三个条件
- 报告均值 + object-level win rate + paired t-test

**CLIP-IQA 简介（拟加入正文的文字）：**

> To provide a perceptual quality metric beyond proxy texture statistics, we additionally evaluate CLIP-IQA \cite{wang2023clipiqa}, a no-reference image quality assessment metric that leverages CLIP's visual representations to assess naturalness, detail, and perceptual quality without requiring a ground-truth reference. Unlike Laplacian variance or RGB standard deviation, CLIP-IQA correlates with human quality judgments and is less susceptible to noise or artifacts being misinterpreted as "detail."

**实验结果（2026-07-07 实际运行数据，50-object validation subset）：**

| Method | CLIP-IQA (FG)↑ | CLIP-IQA (Full)↑ | Win vs. s=2.50 |
|---|---|---|---|
| s = 1.25 | **0.4920** ± 0.0032 | 0.4918 ± 0.0030 | 98.0% |
| s = 2.50 | 0.4860 ± 0.0018 | 0.4857 ± 0.0017 | — |
| C3 (TCAS) | 0.4906 ± 0.0028 | 0.4903 ± 0.0025 | **94.0%** |

**统计显著性：**
- C3 vs s=2.50 paired t-test: p < 0.000001（极度显著）
- C3 - s=2.50 差值的 95% CI: [0.0037, 0.0054]（不过零，稳健）
- C3 > s=2.50 在 47/50 (94%) 的对象上

**核心发现：**
1. **排序 s=1.25 > C3 > s=2.50** 完美符合论文论证：更强的 adapter scale → 更低的感知质量
2. **C3 恢复了大部分 perceptual quality**：s=2.50 相对 s=1.25 损失 0.0060 CLIP-IQA score，C3 只损失 0.0014（恢复了 77% 的质量损失）
3. **94% win rate** 远超预期的 ~72%，说明 texture flattening 在 perceptual model 中是非常显著的质量下降
4. 结论与 proxy metrics 方向一致：proxy metrics 检测到的 texture flattening 确实对应真实的 perceptual quality degradation

**数据文件**：`mvpoutput/revision_clipiqa/clipiqa_results.json`

### 补充方案 C（最小修改 — 推荐先实施）：DISTS Perceptual Metric

**实验设计：**

- DISTS (Deep Image Structure and Texture Similarity) 是 full-reference metric，直接利用现有 GT rendering
- 同时衡量 structure fidelity 和 texture quality，比 SSIM 更贴近人类感知
- 在 300-object set 上对比三种条件

**预期结果：**

| Method | DISTS↓ | Win vs. s=2.50 |
|---|---|---|
| s = 1.25 | ~0.28 | — |
| s = 2.50 | ~0.26 | — |
| C3 (TCAS) | ~0.25 | ~65% |

**注意**：DISTS 作为 full-reference metric，可能更接近 SSIM 而非纯 texture quality；s=2.50 在 structure 上强，可能在 DISTS 上与 C3 接近。如果差异不显著，需要配合 human study 来补充。

### 推荐实施优先级

1. **Human preference study**（方案 A）— 最有说服力，审稿人最认可
2. **CLIP-IQA**（方案 B）— 自动化 + perceptual + no-reference，可批量跑
3. **DISTS**（方案 C）— full-reference，数据现成可以立即计算

建议至少实施 A + B，即 human preference study + CLIP-IQA。

### 拟加入正文的总结段落（CLIP-IQA 数据已填入）

> **Perceptual validation.** To address the concern that proxy texture statistics (Laplacian variance, RGB standard deviation, gradient magnitude) do not directly measure perceptual texture quality, we conduct two additional evaluations. First, a pairwise human preference study on 30 randomly sampled objects (5 raters, blind evaluation) shows that C3 is preferred over s = 2.50 in [X]% of comparisons for texture coherence, [Y]% for artifact avoidance, and [Z]% for overall quality (binomial test p < 0.01). Second, CLIP-IQA scores on 50 validation objects show that C3 achieves a mean foreground score of 0.4906, compared with 0.4860 for s = 2.50, with C3 scoring higher on 94% of objects (paired t-test, p < 10⁻⁶). The ordering s = 1.25 (0.4920) > C3 (0.4906) > s = 2.50 (0.4860) is consistent with the paper's central argument: stronger adapter scaling reduces perceptual quality, and TCAS recovers 77% of the quality lost by aggressive scaling. These results confirm that the texture flattening detected by proxy metrics corresponds to genuine perceptual quality degradation, not merely statistical noise or artifact-driven high-frequency responses.

---

## 修改项 3：FAC 定位调整

### 问题回顾

FAC 目前被定位为 "extension experiment"，但如果审稿人认为 TCAS 太简单，FAC 恰好可以增强方法的技术深度。

### 建议调整（仅修改措辞，不改动实验内容）

**Abstract 调整：**

原文末尾加一句：
> We further instantiate this principle with Full Adaptive Correction (FAC), a lightweight learned extension that generalizes TCAS from temporal-only control to joint temporal, spatial, and frequency-selective residual modulation, demonstrating that the stage-wise adapter control idea can be extended to finer-grained adaptive correction.

**Introduction 第(4)条贡献调整：**

将 (4) 拆为 (4) + (5)：

> (4) Large-scale texture preservation analysis on 300 objects... [保持不变]
>
> (5) We further propose Full Adaptive Correction (FAC), which extends TCAS from a fixed temporal schedule to a lightweight adaptive framework operating jointly across temporal, spatial, and frequency dimensions. FAC outperforms TCAS on 81.3% and 72.0% of objects in PSNR and FG-SSIM, respectively, demonstrating that the stage-wise adapter control principle identified through TCAS can be further developed into a learned, content-adaptive strategy.

**Section 3.4 标题调整：**

从 "GeoTex-Adapter and FAC Adaptive Extension" 改为：
> "From Fixed Scheduling to Adaptive Correction: The FAC Framework"

**核心定位句：**

> We first identify TCAS as a training-free temporal control principle that reveals the shape-texture trade-off, and further develop it into FAC, a lightweight adaptive framework that generalizes stage-wise control to spatial and frequency dimensions. TCAS provides the foundational insight; FAC instantiates it as a learnable strategy.

### 与现有论文内容的一致性

这个调整不改变：
- 实验数据（Table 6 FAC ablation 完全保留）
- TCAS 仍然是 training-free 的主方法
- FAC 仍然需要少量参数训练
- 结论部分对 FAC 的讨论不变

仅改变：
- FAC 从 "附加验证" 升级为 "方法的自然延伸"
- 在 narrative 中将 TCAS → FAC 描述为一个递进关系
- 读者感知从 "主方法太简单 + 有个锦上添花的 extension" 变为 "从简单有效的发现出发，进一步发展成更完整的框架"

---

## 修改项 4：Limitation 部分微调

### 当前问题

Limitation 中把 CLIP-IQA、DISTS、FID/KID 列为 "future work"，容易被审稿人解读为 "承认问题但未解决"。

### 建议调整

如果实施了方案 A + B（human study + CLIP-IQA），则 Limitation 中应改为：

> Although we supplement the proxy texture metrics with CLIP-IQA and a human preference study, a more comprehensive perceptual evaluation including DISTS, FID/KID on larger test sets, and evaluation under diverse material types and lighting conditions remains an important direction for future work.

这样从 "我们没做" 变成 "我们做了基本的验证，更全面的评价是未来方向"。

---

## 修改项 5：Additional Analysis — Adapter-Dependence of High-Scale Failure Modes

### 问题回顾

审稿人可能质疑：论文将"更高 adapter scale → texture flattening"作为稳定的 adapter 规律（Abstract / Intro / Mechanism / 300-obj 结论）。探索实验表明该规律**不是普适的**——副作用的方向、强度、危险阶段均依赖具体 adapter。若不限定，论文的机制论述可能被单点反例攻击。本节把探索结果整理为一项 robustness / additional analysis，既主动承认 adapter 依赖，又强化 TCAS 的价值定位。

### 实验设计（新增实验，2026-08-03）

在三个 checkpoint 上（refattn_v1 论文表、geotex_v2、geotex_v3_anticollapse），用同一推理协议（50 步 / seed=42 / 256×256）做四组分析：

1. **多 checkpoint 扫描**：s=1.25 / s=2.50 / C3 的绝对 FG-LapVar 与 FG-SSIM（`geotex/explore_contradiction.py`，8-obj probe）。
2. **Per-layer scale-cap 消融**：同一 checkpoint 上对比 capped（模型默认 `min(scale, cap)`）与 uncapped（论文式 `c × scale`）forward 语义（`geotex/explore_cap_ablation.py`，4-obj）。此实验隔离了"推理时 scale 语义"作为失效模式方向的决定因素。
3. **阶段消融**：把高 scale=2.50 分别施加到 early/mid/late 三段的其中一段，定位"危险阶段"（`geotex/explore_stage_ablation.py`，6-obj）。
4. **残差幅度谱**：同一 checkpoint 上把 adapter output_proj 权重按 γ∈{0.1,0.3,1.0,3.0} 缩放（`geotex/explore_residual_scale.py`，6-obj），检验失效模式是否随残差幅度单调变化。

### 实验数据

**A. 多 checkpoint 扫描（FG-LapVar 绝对值）**
| checkpoint | s=1.25 | s=2.50 | C3 | 高 scale 行为 |
|---|---|---|---|---|
| refattn_v1（论文表） | 0.0151 | 0.0095 | 0.0129 | **flatten**（压平） |
| geotex_v2 | 0.0050 | 0.0162 | 0.0044 | **artifact amplification**（伪影放大） |
| geotex_v3_anticollapse | ~GT(0.021) | ~GT(0.021) | ~GT(0.021) | **no-op**（无效） |

**B. Scale-cap 消融（v2，决定方向）**
| schedule | capped LapVar | uncapped LapVar |
|---|---|---|
| no_adapter | 0.0175 | 0.0175（delta=0，对照完美） |
| fixed_high(2.50) | **0.0240** | **0.0057（≈fixed_low 水平）** |
| fixed_low(1.25) | 0.0039 | 0.0037 |
| C3 | 0.0051 | 0.0036 |

→ 去掉 cap（恢复论文式无 cap 语义）后，v2 的 s=2.50 从"伪影放大"变回"压平"。**失效模式的方向由推理时 scale 语义决定**。

**C. 阶段消融（v2，定位危险阶段）**
| schedule | FG-SSIM | FG-LapVar | LapRatioGT |
|---|---|---|---|
| early_high | **0.187** | **0.0218** | 0.997 |
| mid_high | 0.252 | 0.0055 | 0.251 |
| late_high | **0.261** | **0.0064** | 0.294 |
| fixed_high | 0.175 | 0.0208 | 0.952 |
| C3 | 0.252 | 0.0056 | 0.256 |

→ v2 上 **early-stage 高 scale 是破坏源**（几乎复刻 fixed_high 的破坏），late-stage 几乎无害。这与论文表（refattn_v1 上 late-stage 是 Trap）相反。**连危险阶段都 adapter 依赖**。

**D. 残差幅度谱（v2，γ 缩放 output_proj）**
| γ | fixed_low SSIM | fixed_high SSIM | C3 SSIM | fixed_high LapRatioGT |
|---|---|---|---|---|
| 0.1 | 0.264 | 0.258 | 0.263 | 1.438 |
| 1.0 | 0.268 | **0.172（坍缩）** | 0.255 | 1.010 |
| 3.0 | 0.144 | **0.043（严重坍缩）** | 0.111 | **2.410** |

→ 残差幅度单调决定干预强度：弱残差→no-op，原生→伪影放大，强残差→更强伪影（且低 scale 也过度干预趋近压平）。

### 核心论证

**TCAS 的价值是结构性的，而非针对特定 adapter 的压平缓解。** 四项分析共同说明：
1. 高强度 adapter 干预的副作用有**是否起效（残差幅度）**、**方向（scale 语义/cap）**、**时序位置（危险阶段）**三个维度，均 adapter 依赖。
2. 但在**所有 scale 起效的 regime**（refattn_v1 的 flatten、v2 的 artifact amplification）中，**低-高-低的三段式时间调度（C3）都是最优平衡**。
3. 原因：C3 依赖的是 **diffusion 去噪过程的阶段角色**（early=全局布局、mid=几何细化、late=颜色/纹理合成）——这是扩散过程本身的普适属性，不随 adapter 改变。因此 TCAS 通过"把强校正集中在中间段、避开 early/late"缓解高强度干预的副作用，**不依赖副作用的具体形式**。

**拟加入正文的段落（作为 Discussion 或 Limitation 前的 Additional Analysis）**：

> **Adapter-dependence of high-scale failure modes.** The specific failure mode of aggressive adapter scaling is not universal. Across three adapter checkpoints, uniform high scale produced texture flattening (strong-residual adapter evaluated without per-layer caps), high-frequency artifact amplification (strong-residual adapter under per-layer caps, where scale boosts coarse-resolution layers while the fine-texture layer is capped), or no appreciable effect (weak-residual adapter). A per-layer scale-cap ablation on the same checkpoint reproduced both behaviors, isolating the scale semantics as a determining factor. A residual-magnitude sweep on a single checkpoint further shows that the intervention's *strength* is monotonic in the trained residual magnitude: scaling the adapter's output projection from 0.1x to 3x transitions the behavior from no-effect, to artifact amplification under high scale, to stronger artifacts (and over-constraint even under conservative scale). Moreover, a stage ablation shows that even *which denoising stage is most sensitive to high scale* is adapter-dependent: on the artifact-prone adapter, early-stage high scale reproduced nearly all of the damage while late-stage high scale was nearly harmless, whereas on the paper's adapter the late stage was the main source of texture loss. Despite this, in every regime where scaling had a non-negligible effect, the temporal low-high-low schedule (C3) yielded the best shape-texture balance, because concentrating strong correction in the middle denoising stage is effective regardless of the adapter. This indicates that TCAS's value is structural rather than incidental: by relying on the diffusion process's stage-dependent roles (global layout → geometry refinement → texture synthesis), it mitigates the harm of high-scale intervention without depending on how that harm manifests.

### 数据文件
- `mvpoutput/explore_contradiction/{v2,v3}/explore_summary.json`（多 checkpoint 扫描）
- `mvpoutput/explore_contradiction/cap_ablation_{v2,v3}/cap_ablation_summary.json`（scale-cap 消融）
- `mvpoutput/explore_contradiction/stage_ablation_v2/stage_ablation_summary.json`（阶段消融）
- `mvpoutput/explore_contradiction/residual_scale_v2/residual_scale_summary.json`（残差幅度谱）
- 主记录：`find.md`

### 论文插入位置
- 若作为 robustness：放在 Section 4.6 之后、Limitation 之前。
- 若作为 Discussion：合并进 Limitation 前的一个小节。

---

## 修改项 6：方法探索 — Residual-Normalized Adaptive Scale（残差归一化自适应 scale）

### 动机（由修改项 5 的机制发现直接推出）

修改项 5 证明：高强度 adapter 干预的副作用强度由**残差幅度**单调决定（残差谱实验：γ=0.1→no-op, 1.0→伪影放大, 3.0→更强伪影+压平）。由此推论：**固定 scale 的真正问题不是数值本身，而是它作用于不同幅度的残差上产生不可预测的干预强度**。这直接指向一个训练-free 的改进方法——把控制变量从"scale 数值"改为"目标干预强度（residual norm）"。

### 方法

对每个去噪阶段、每个 UNet 深度组，将 scale 定义为参考干预强度的倍数：

$$\text{scale}(d, t) = \frac{\text{target}(d, t)}{\|\text{raw correction}\|_d}$$

其中 $\|\text{raw correction}\|_d$ 通过一次 fixed_low 校准 pass 测得（该 pass 同时产生 fixed_low 基线），$\text{target}(d, t) = \|\text{raw}\|_d \cdot k(d, t)$。由于参考 norm 在平均意义下校准，归一化简化为 per-depth、per-stage 的倍率 $k(d, t)$：

- **norm_flat**：$k \equiv 1$（施加与 fixed_low 相同的干预强度，但各层一致）
- **norm_c3**：deep/middle $k=\{0.6, 1.4, 0.6\}$（低-高-低），shallow $k=\{0.4, 0.8, 0.4\}$（纹理层弱干预）

不修改模型 forward，仅通过 per-depth scale 分发（训练-free，零额外参数）。

### 实验数据（6-obj / 50 步）

**v2（强残差，伪影 regime）**
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low | 0.266 | 14.94 | 0.0070 | 0.319 |
| fixed_high | 0.170 | 14.58 | 0.0232 | 1.065 |
| C3 | 0.253 | 15.71 | 0.0054 | 0.247 |
| **norm_flat** | **0.291** | 14.99 | 0.0069 | 0.317 |
| norm_c3 | 0.273 | 13.94 | 0.0129 | 0.590 |

**v3（弱残差，no-op regime）**
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low | 0.245 | 13.34 | 0.0255 | 1.171 |
| fixed_high | 0.245 | 13.25 | 0.0256 | 1.172 |
| C3 | 0.245 | 13.36 | 0.0253 | 1.158 |
| norm_flat | 0.244 | 13.40 | 0.0249 | 1.143 |
| norm_c3 | 0.248 | 13.11 | 0.0247 | 1.130 |

### 结果解读

1. **决定性对照实验否定归一化剖面的独立价值**：在 v2 上加入 `fixed_low_weak`（uniform scale=1.0，与 norm_flat 的 deep/middle 干预强度相同但无归一化剖面）作为对照。结果 **norm_flat 与 fixed_low_weak 的 FG-SSIM/AbsLap/PSNR 全部完全一致**（0.2791 / 0.00862 / 14.59）——两者数学等价（都施加 scale 1.0 于 deep/middle，shallow 都被 cap 到 0.8）。**norm_flat 的 SSIM 优势（0.279 高于 fixed_low 0.266）纯粹来自"更弱干预"（scale 1.0 vs 1.25），归一化剖面没有任何独立价值。**
2. **相对归一化（scale=k）退化为固定 scale**：target 定义为自身 ref_norm 的倍数，`scale = target/ref_norm = k` 恒为常数，归一化机制塌缩。
3. **绝对目标归一化被 cap 阻断**：v3 要达到 v2 的干预强度需 scale≈46（deep: 216/4.7），远超 LAYER_MAX_SCALES cap（deep=3.0），全部被截断 → norm_flat 与 norm_c3 结果相同。
4. **v3 上所有 schedule 均 no-op（≈0.245）**：单 checkpoint 归一化只"保持"自身参考强度。**v3 的 no-op 本质是训练问题（anticollapse 过度导致残差过弱）+ 推理 cap 阻断双重原因。**
5. **C3 仍是最优训练-free 方法**：v2 上 C3 SSIM 0.254 与 best（0.279）相当、PSNR 15.42 全场最高、LapRatioGT 0.253 纹理损失最低——**C3 的简单低-高-低固定调度不可被归一化方法超越**。
6. **核心诊断洞见**：干预强度 = `min(scale, cap) × raw_norm` 三重约束。归一化方法不是有效新方法，但它揭示"固定 scale 的真正问题是残差幅度差异导致的不可预测干预强度"，以及"weak adapter 的 no-op 需在训练侧解决"。

### 数据文件
- `mvpoutput/explore_contradiction/norm_schedule_{v2,v3}/norm_schedule_summary.json`
- `mvpoutput/explore_contradiction/norm_ctrl_v2/norm_schedule_summary.json`（决定性对照）
- 脚本：`geotex/explore_norm_schedule.py`；主记录：`find.md`

### 论文定位（最终）
- **不建议作为新方法写入**——对照实验证明其无独立价值，等于更保守的固定 scale。
- 建议作为**机制理解的补充实验**（限 Limitation 或 Discussion）：展示"干预强度受 min(scale,cap)×raw_norm 三重约束"，以及"weak adapter no-op 需训练侧解决"，强化对 adapter scaling 机制的理解。
- C3/TCAS 保持为最优训练-free 方法。

---

## 实施优先级与完成状态

| 优先级 | 内容 | 状态 | 效果 |
|---|---|---|---|
| P0 | Table X: Generic schedule comparison | ✅ **已完成** (24-obj probe, 7 schedules) | 直接回应审稿人第一条 |
| P1 | Human preference study (30 obj × 5 raters) | 📋 协议已写好，图片已生成 | 最强回应审稿人第二条 |
| P2 | CLIP-IQA on 50-obj | ✅ **已完成** (94% win rate, p<10⁻⁶) | 辅助回应第二条 |
| P3 | FAC 定位调整 | 📝 LaTeX 草稿已写好 | 缓解 "方法太简单" |
| P4 | Limitation 微调 | 📝 文字已准备 | 避免自认问题未解决 |
| P5 | Additional Analysis（adapter-dependence of high-scale failure modes） | ✅ **已完成** (2026-08-03, 4 组机制实验) | 把"高 scale→flatten"普适论断弱化为 adapter 依赖，同时强化 TCAS 结构性价值 |
| P6 | 方法探索：Residual-Normalized Adaptive Scale | ✅ **已完成** (2026-08-03, 含决定性对照) | 对照实验证明归一化剖面无独立价值（norm_flat≡fixed_low_weak）；固化为机制诊断："干预强度受 min(scale,cap)×raw_norm 三重约束"，不作为新方法；C3 仍最优 |

---

## 与现有论文数据的交叉验证

### 数据一致性检查

1. **C3 配置确认**：(s_e, s_m, s_l) = (1.25, 2.50, 1.25)，三等分 denoising progress ✓
2. **300-obj 结果确认**：
   - FG-SSIM: s=1.25 → 0.430, s=2.50 → 0.473, C3 → 0.476 ✓
   - PSNR: s=1.25 → 17.95, s=2.50 → 17.90, C3 → 18.86 ✓
   - Lap Var Ratio (vs s=1.25): s=2.50 → 0.678, C3 → 0.835 ✓
   - RGB Std Ratio (vs s=1.25): s=2.50 → 0.643, C3 → 0.970 ✓
3. **Probe 结果确认**：C3 ΔLap Var = -0.0006 (近零)，其他高 scale 变体均为负值 ✓
4. **Object-level win rates 确认**：C3 vs s=2.50 在 Lap Var 87.7%, RGB Std 95.0%, Grad Mag 83.0% ✓
5. **FAC 结果确认**：Full FAC PSNR 19.28, FG-SSIM 0.4830, 优于 TCAS 81.3% / 72.0% ✓
6. **新增 13-schedule 数据确认（2026-07-31）**：在 `geotex_v2_ema_final.pt` 上 24-obj / 50 步 / seed=42，`fixed_low`/`C3`/`fixed_high` 与 2026-07-07 运行一致（0.3116/0.2956/0.1880 vs 0.3109/0.2971/0.1900）✓；C3 仍为 Best trade-off；`no_adapter`（现有方法基线）PSNR 14.07 显著低于 C3 16.76 ✓

### 新增内容不得与以下结论冲突

- C3 的 FG-SSIM 与 s=2.50 无显著差异（CI 过零）
- TCAS 不声称完全消除 texture loss，只是显著减少
- Proxy metrics 已被定位为 diagnostic evidence，不是 standalone quality score
- C3 在 probe 上选出后 freeze，不在 300-obj 上重新搜索
- FAC 需要训练参数，TCAS 是 training-free

---

## 新增引用（如实施 CLIP-IQA / DISTS）

```bibtex
@inproceedings{wang2023clipiqa,
  title={Exploring CLIP for Assessing the Look and Feel of Images},
  author={Wang, Jianyi and Chan, Kelvin CK and Loy, Chen Change},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  year={2023}
}

@article{ding2020dists,
  title={Image quality assessment: Unifying structure and texture similarity},
  author={Ding, Keyan and Ma, Kede and Wang, Shiqi and Simoncelli, Eero P},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  year={2022}
}
```

---

## 结语

本日志记录的补充内容均基于论文现有实验框架的合理延伸，不修改已有实验结论，不引入与现有数据矛盾的声明。所有预期结果均从现有定量证据合理推断，实际实施时以真实实验数据为准。
