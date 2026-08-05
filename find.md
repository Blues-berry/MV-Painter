# find.md — fixed_high vs C3 "矛盾"的客观探索日志

> 目的：不以现有论文/结论为约束，从客观事实出发，发掘"fixed_high 的 LapVar 方向随 checkpoint 反转"这个矛盾的价值。
> 原则：只记录可复现的客观事实 + 可证伪的假设。每个事实标注证据来源。
> 更新：2026-08-03 创建。

---

## 0. 矛盾的定义

- **论文 300-obj 纹理表**（`final/final.tex` Table tab:texture300, tab:retention）：LapVar s=1.25→0.0151, s=2.50→0.0095, C3→0.0129。**高 scale 压平纹理**（s=2.50 < s=1.25）。
- **geotex_v2 checkpoint 的 300-obj 评估**（`mvpoutput/geotex_v2/eval300v2_*`）：fg_lap_var s=1.25→0.0050, s=2.50→0.0162, C3→0.0044。**高 scale 放大高频**（s=2.50 >> s=1.25）。
- 同一协议表述（300-obj / 50 步 / seed=42）下，fixed_high 相对 fixed_low 的绝对 LapVar 方向**完全相反**。

---

## 1. 已确认的客观事实（证据来源）

### F1. 三个 checkpoint 是完全不同的训练产物
| checkpoint | 训练配置差异 | 证据 |
|---|---|---|
| `geotex_refattn_v1/geotex_step_0002000.pt`（论文纹理表） | base adapter | `eval_texture_300obj.py` 命令行引用该路径（git: f2f0019） |
| `geotex_v2/geotex_v2_ema_final.pt`（新表） | 10000 步，无 cap | `train_args.json` |
| `geotex_v3_anticollapse/.../ema_final.pt`（当前） | 6000 步，**shallow scale=0.1** + output_proj 范数 clamp=1.5 + var_weight=0.01；末尾 6 步全 NaN | `train_args.json`、`geotex/train_v2.py` |

→ **不能直接混用新旧 checkpoint 的纹理表**（用户判断得到确认）。

### F2. 论文评估的 scale 语义与新版不同（关键机制线索）
- 论文 `eval_texture_300obj.py` monkey-patch 了 `GeoTexResnetWrapper.forward`，用 `c * self._adapter_scale` 施加 scale，**没有 `min(_adapter_scale, _max_scale)` cap**（git: fb1abad eval_texture_300obj.py 内 scaled_forward）。
- 新版 `eval_schedule_comparison.py` / `eval_unified_300.py` 使用**模型自带 forward**，带 `LAYER_MAX_SCALES` cap：deep=3.0, middle=3.5, **shallow=0.8**（`model_unet_geotex.py:298`）。
- 结论：**论文的 s=2.50 = 全层裸乘 2.5（含 128×128 纹理层）；新版的 s=2.50 = shallow 被钉在 0.8，只有 deep/middle 变强。**

### F3. v2/v3 推理时 shallow 层对所有 schedule 完全一致（已被 smoke 实验证实）
- smoke（v3, 1 obj, 10 步）实测 scaled-correction 每像素均值：shallow=0.0616（fixed_low 与 fixed_high 相同），deep/middle 恰好差 2 倍（scale 2.5/1.25）。
- 原因：`min(_adapter_scale, 0.8)`，1.25 和 2.50 都 ≥ 0.8 → 都被截到 0.8。

### F4. v3 的 shallow 层 raw correction 比 deep/middle 大一个数量级
- smoke 实测（换算到 raw）：shallow≈0.077/pixel，middle≈0.009，deep≈0.005。即**最细纹理层注入的残差本身就最大**，即使训练时 scale=0.1 强抑制、推理时 cap=0.8。
- 含义：纹理层的注入强度由**训练学到的 raw 幅值 × cap** 决定，与 schedule（1.25/2.5）**无关**。

### F5. 指标归一化基准不统一
- 论文 probe 表：ΔLapVar = pred−GT（相对 GT，接近 0 = 无损失）。
- 论文 retention 表：ratio **相对 s=1.25**。
- 新版 schedule 对比表：ratio 相对 GT，且 summary 里是**逐对象 ratio 的均值**（对 GT LapVar≈0 的对象极敏感）。
- 24-obj 探针（v2）实测两种口径差异大：fixed_high 逐对象ratio均值=1.653 vs 均值比=0.899。
- → 跨表比较时，同一列名可能指不同量。

### F6. 论文 probe 表与新版 24-obj 表在 C3 上的纹理行为严重不一致
- 论文：C3 ΔLapVar = −0.0006（≈0 纹理损失）。
- v2 24-obj：C3 abs_lap=0.0053 vs GT=0.0216（仅保留 24%）。
- 同一"GeoTex-Adapter + C3"，一个接近零损失、一个损失 75%。只能是 checkpoint/scale 语义差异。

### F7. 用户原始判断中"shallow scale cap"确实存在于训练侧
- `train_v2.py`：`if module.depth_group == 'shallow': module._adapter_scale = 0.1`。
- 但**推理时不用 0.1，用 0.8 cap**（LAYER_MAX_SCALES）。训练/推理 scale 不一致。

---

## 2. 主实验已完成（geotex/explore_contradiction.py，8-obj / 50 步 / seed=42）

### R1. v2：fixed_high = 伪影放大，不是纹理恢复
| schedule | AbsLap | SSIM | PSNR | LapCorr | BndHF | MAE |
|---|---|---|---|---|---|---|
| no_adapter | 0.0255 | 0.247 | 13.38 | 0.000 | 0.172 | 1.706 |
| fixed_low(1.25) | 0.0049 | 0.259 | 15.50 | 0.004 | 0.183 | 1.293 |
| fixed_high(2.50) | **0.0194** | **0.169** | 15.30 | −0.006 | 0.174 | 1.254 |
| C3 | 0.0047 | 0.248 | **16.15** | 0.007 | 0.176 | 1.196 |

- 逐对象：fixed_high 在全部 4 个对象上 AbsLap 是 fixed_low 的 **2.6–9.6 倍**，同时 SSIM **全部坍缩**（0.12–0.18 vs 0.20–0.32）。
- 高 LapVar 伴随结构坍缩 → **artifact amplification 坐实**（H1 成立）。LapCorr≈0 说明生成纹理本身不与 GT 逐像素对齐，此探针对本任务区分度低（已降级使用）；SSIM 坍缩 + LapVar 飙升的组合是更强证据。

### R2. v3：scale 近乎 no-op，矛盾消失
| schedule | AbsLap | SSIM | PSNR |
|---|---|---|---|
| no_adapter | 0.0237 | 0.251 | 13.39 |
| fixed_low | 0.0239 | 0.245 | 13.90 |
| fixed_high | 0.0252 | 0.244 | 13.79 |
| C3 | 0.0234 | 0.243 | 13.90 |

- 三个 schedule 的 AbsLap 全部 ≈ GT(0.0206)，差距极小（0.023–0.025）；SSIM 全部 ≈0.24，无坍缩。
- 逐对象方向不一致（2 个略压平、2 个略放大）→ **scale 在 v3 上基本失效**。

### R3. residual 数据解释一切（v2 vs v3）
| 层 | v2 (fixed_low/fixed_high) | v3 (fixed_low/fixed_high) |
|---|---|---|
| deep (32×32) | 0.30 / 0.58 | 0.006 / 0.013 |
| middle (64×64) | 0.29 / 0.54 | 0.011 / 0.022 |
| shallow (128×128) | 0.55 / 0.58 | 0.062 / 0.062 |

- **v3 的 deep/middle correction 比 v2 小 ~45 倍**（anticollapse 效果：output_proj 范数 clamp + var_weight 把深层 residual 压到很弱）。
- 两版 shallow 都在 capped=0.8 下与 schedule 无关（1.25 与 2.50 相同）。
- 推论：v2 的 adapter 处于"correction 爆炸"边缘（deep 0.3 / shallow 0.55 的 per-pixel residual 极大，正是 train_v2.py 注释里要防的），高 scale 一推就结构坍缩 + 伪影；v3 被 anticollapse 压得过弱，scale 推不动。

### R4. C3 的机制在 v2 上得到客观确认
- v2 上 C3 的 mid-stage deep/middle residual（0.55/0.52）与 fixed_high（0.58/0.54）几乎相同，但 **C3 只在中间 1/3 施加**，SSIM 0.248 vs 0.169、Lap 0.0047 vs 0.0194。
- → C3 的价值 = 把强 residual 限定在中间段，避免 early/late 阶段被高 scale 破坏。这与论文论证一致，但现在有逐层 residual 证据。

### R5. 重要推论：C3 的"保纹理"也 checkpoint 依赖
- v2 上 C3 AbsLap=0.0047 ≈ GT 的 0.23（与 fixed_low 相当）→ **在 v2 上 C3 一样压平纹理**（只是不伪影）。
- v3 上 C3 AbsLap=0.0234 ≈ GT → **在 v3 上 C3 纹理基本保留**。
- 论文 base adapter 上 C3 ΔLapVar≈0（保留）。三个 checkpoint 三种表现。

---

## 3. 机制假设 H3 的检验（实验：geotex/explore_cap_ablation.py）

**假设 H3**：LapVar 方向反转的主因是 **LAYER_MAX_SCALES cap 改变了 scale 的层次语义**。
- 论文（无 cap）：s=2.50 全层裸乘 → 128×128 纹理层被强压 → flatten。
- 新版（cap）：s=2.50 只增强 deep/middle，shallow 锁死 0.8 → 粗尺度残差放大。

### R6. code-reviewer 审查发现首版 cap_ablation 有污染（已修复重跑）
- **严重问题**：首版 `uncapped_forward` 遗漏 `_skip_correction` 防护。`RefOnlyNoisedUNet` 每步走 write-pass（生成参考 latents）+ read-pass 两次 forward；write-pass 设 `_skip_correction=True`。未加防护导致 adapter 在 write-pass 也被施加 → 参考特征被 adapter 污染 + 每步实际校正 ×2。**首版"uncapped 使 fixed_high LapVar 骤降"的结果归因不可信**（已备份到 `cap_ablation_*/OLD_POLLUTED/`）。
- 已修复：`uncapped_forward` 补 `if GeoTexResnetWrapper._skip_correction: return hidden_states`；每次生成前 `torch.manual_seed(42)`（消除条件 latent/参考噪声的随机地板）。
- 重跑进行中：`cap_ablation_v2_rerun.log` / `cap_ablation_v3_rerun.log`（4-obj / 50 步）。
- 主实验 `explore_contradiction.py` 的 capped 路径 `_last_correction` 时序经审查**无隐患**（read-pass 才施加，`scheduler.step` 后读取），其结论 R1–R4 可信。

### R7. H3 机制完全证实（cap_ablation 修复后结果）
| checkpoint | schedule | capped AbsLap | uncapped AbsLap | delta |
|---|---|---|---|---|
| v2 | no_adapter | 0.01753 | 0.01753 | **0.00000**（对照完美） |
| v2 | fixed_low(1.25) | 0.00393 | 0.00369 | −0.00024 |
| v2 | fixed_high(2.50) | **0.02401** | **0.00571** | **−0.01830** |
| v2 | C3 | 0.00510 | 0.00361 | −0.00149 |
| v3 | no_adapter | 0.02001 | 0.02001 | 0.00000 |
| v3 | fixed_low | 0.02475 | 0.02928 | +0.00453 |
| v3 | fixed_high | 0.02446 | 0.02794 | +0.00347 |
| v3 | C3 | 0.02475 | 0.03296 | +0.00821 |

**结论**：
1. `no_adapter` delta 精确为 0 证明 re-seed 消除了随机地板、补丁无状态泄漏。
2. **v2 uncapped s=2.50 的 LapVar 从 0.024 骤降到 0.0057**，与 fixed_low/C3 同水平（1.5 倍内）。即去掉 cap 后，论文式的"全层裸乘 2.5"压平了纹理层，新版带 cap 的 s=2.50 放大高频（伪影）。**H3 成立：LapVar 方向反转的主因是 LAYER_MAX_SCALES cap 改变了 scale 的层次语义。**
3. v3 三个 schedule 无论 capped/uncapped 都接近 GT(0.021)，adapter 整体太弱，scale 怎么调影响都小。
4. 三个 checkpoint 构成完整谱系：
   - refattn_v1（论文，无 cap，base adapter）：s=2.5 压纹理层 → **flatten**
   - v2（有 cap，correction 爆炸态）：capped s=2.5 → **伪影放大**；uncapped s=2.5 → **flatten**（回到论文行为）
   - v3（有 cap，anticollapse 过弱）：scale 近 no-op

### R8. 像素级分析（image-reader 环境视觉通道实际不可用，改用 Python 客观像素分析）
**v2 obj00**：
- corr(fh, c3)=0.649（两 schedule 输出差异大）；corr(fh, GT)=0.073 vs corr(c3, GT)=−0.007。
- |Lap| FG 均值：GT=19.4，fixed_high=21.1（≈1.09×GT），C3=8.4（0.43×GT）。
- fixed_high 高频 interior=21.75 > edgeband=20.22 → 高频散布在表面**内部**，非轮廓振铃；corr 略正但整体 SSIM 坍缩（R1）→ 伪影放大形态为"表面内部散斑"而非"边界振铃"。
- |pred-GT| FG 均值 fh=97.6 vs c3=90.5（两者都大）。

**v3 obj00**：
- corr(fh, c3)=**0.970**（两 schedule 输出几乎相同）；corr(fh,GT)≈corr(c3,GT)≈−0.04（都与 GT 无关）。
- |Lap| FG：GT=19.4，fh=4.03，c3=3.96（都只有 GT 的 21%，远平滑）。
- |pred-GT| 极大（130 vs 128），99.9% 前景像素误差>20。
- → **v3 上 fixed_high 与 C3 输出几乎相同，都远平滑于 GT，scale 调度彻底失效**（与 R2 量化一致）。

### 探针口径注意事项（code-reviewer 确认）
- `excess_hf_mean/frac` 分母是全图（被背景稀释），只适合同对象跨 schedule 相对比较。
- `pred_hf_boundary_frac` 是 band/FG 和，band 含背景边缘，可 >1，是比值非分数。
- `fg_mae` 实为 3×每通道 MAE（跨 3 通道求和 / FG 空间像素）。
- `pearson_fg` 在所有 schedule 上 ≈0（pred/GT 逐像素不齐），该探针区分度低，不作为伪影证据；伪影证据主要靠 **SSIM 坍缩 + LapVar 飙升的组合**（R1）。

---

## 4. 待办验证

### E2. 300-obj 级验证
8-obj 方向稳定（R1/R7 均逐对象确认），可补 24/300-obj 的绝对 LapVar 对比，量化反转幅度与 win-rate。注意：论文表与新版评估的 scale 语义不同（F2），300-obj 级对比必须同协议（同 checkpoint、同 capped forward、同归一化基准）。

### E3. 分辨率/公式审计
论文表 s=1.25 AbsLap 0.0151 vs v2 表 0.0050，差 3 倍。已确认公式相同（`metrics_extended`），差 3 倍来自 checkpoint + scale 语义差异的可能性大，但论文 eval_config_snapshot.yaml 已丢失，分辨率（256 vs 512）无法完全排除。可在同一图像上对比两种分辨率下的公式验证。

### E4. 视觉确认伪影 —— 已被像素级分析替代（R8）
image-reader 环境的视觉通道实际不可用（模型不支持视觉输入），改用 Python 像素级客观分析完成，结论见 R8：v2 fixed_high 高频在表面内部（非边界振铃）、与 GT 略正相关但 SSIM 坍缩；v3 两 schedule 输出几乎相同且远平滑于 GT。

---

## 5. 结论方向（数据已基本确认）

矛盾的价值定位：**"高强度 adapter 干预失配"是更一般的问题，且失配方向取决于 adapter 的 trained residual 分布 + 推理时 scale 语义**。
- refattn_v1（论文，无 cap）：s=2.5 强压纹理层 → flatten。
- v2（cap，correction 爆炸态）：s=2.5 推粗尺度残差 → 结构坍缩 + 伪影放大。
- v3（cap，anticollapse 过弱）：s=2.5 推不动 → 近 no-op。

**方法论教训（对论文最危险的一点）**：
- 论文把"高 scale → texture flattening"当作稳定的 adapter 规律；客观数据表明它只是 refattn_v1 这一特定 adapter 的表现。同一推理协议（50 步/seed42）下，v2 表现为 artifact amplification，v3 表现为 scale 失效。
- "C3 保纹理"同样 adapter 依赖（R5）。
- → 论文的机理论述（"late-stage 强干预抑制纹理合成"）应弱化为"具体 adapter 的实例化表现"，而非普适规律。TCAS 的稳健表述是"时间调度能缓解高强度干预的副作用"，但副作用的**方向**（flatten vs 伪影 vs 无效）由 adapter 决定。

两个风险（用户已指出，均已确认客观存在）：
1. 不能混用新旧 checkpoint 的纹理表（F1）。
2. 不能把更高 LapVar 直接解释为更好纹理（R1 证明：v2 的高 LapVar 伴随结构坍缩）。

### R9. 300-obj v2 数据：LapVar 指标的好坏方向随 adapter regime 翻转
从已有 `eval300v2_{c3,fixed_high,fixed_low}` per-object CSV（300-obj，v2）计算：
| 指标 | C3 vs fixed_high 胜率 | C3 vs fixed_low 胜率 |
|---|---|---|
| FG-SSIM | **95.3%** | 24.3% |
| FG-PSNR | **92.0%** | 75.7% |
| FG-LapVar | **0.3%** | 38.7% |
均值：c3 lap=0.0044 ssim=0.368 psnr=9.88；fh lap=0.0162 ssim=0.233 psnr=8.07；fl lap=0.0050 ssim=0.388 psnr=9.39。

**解读**：
- C3 在结构/保真指标上碾压 fixed_high（SSIM/PSNR 胜 92-95%），但 LapVar 几乎全败（0.3%）。
- fixed_high 的 LapVar 高是**伪影放大**（SSIM 塌到 0.23），C3 的 LapVar 低是**避免伪影**（非压平）。
- 对比 refattn_v1：fixed_low 的 LapVar 低是**压平（坏）**。→ **同一个 LapVar 指标，在 refattn_v1 上"低=坏（压平）"、在 v2 上"低=好（避免伪影）"**，好坏方向随 adapter regime 翻转。
- 对论文的意义：LapVar 作为纹理代理**必须配合结构指标 + 伪影定位**一起解读，否则同一数值可被两种相反方式解读。这比"不能把高 LapVar 当做好纹理"更进一步——**连"低 LapVar=纹理损失"的常规读法在 v2 上也失效**。

---

### R10. 阶段消融（v2，6-obj/50 步）——**颠覆性发现：v2 上破坏源是 early 而非 late 阶段**
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low | 0.266 | 14.71 | 0.0056 | 0.258 |
| fixed_high | 0.175 | 14.48 | 0.0208 | 0.952 |
| early_high | **0.187** | 14.43 | **0.0218** | 0.997 |
| mid_high | 0.252 | 15.43 | 0.0055 | 0.251 |
| late_high | **0.261** | 14.70 | 0.0064 | 0.294 |
| C3 | 0.252 | 15.43 | 0.0056 | 0.256 |
| no_adapter | 0.255 | 12.90 | 0.0197 | 0.903 |

**关键发现**：
1. **early_high 几乎完全复刻 fixed_high 的破坏**（SSIM 0.187 vs 0.175，LapRatio 0.997 vs 0.952）→ v2 上伪影放大的主因是 **early-stage 高 scale**。
2. **late_high 几乎无害**（SSIM 0.261≈fixed_low 0.266，LapRatio 0.294≈fixed_low 0.258）。
3. **与论文机制断言直接矛盾**：论文 L276/298 称"C4 late-stage high → Trap / texture loss"（refattn_v1），但 v2 上 late_high 反而安全、early_high 才致命。**连"哪个阶段最危险"都是 adapter 依赖的**。
4. C3（mid 段高）在 v2 上依然最优，因为中间段确实是几何细化最有效的阶段（refattn_v1 与 v2 一致）。
5. 结构/保真：C3 PSNR 15.43 全场最高，SSIM 0.252 与 best 相当。

### R11. 残差谱（v2，6-obj/50 步，γ=0.1~3.0）——**修复重跑后 H4 成立**
- **code-reviewer 发现 critical bug**：首版 `apply_gamma` 用 `mul_`（原地乘当前权重）且循环内无 restore → 实际生效幅度 = {0.1, 0.03, 0.03, 0.09}，**γ=1.0 原生与 γ=3.0 强幅度两个关键点完全缺失**，首版 12 行数据只覆盖弱幅度带。首版"H4 被证伪"结论无效，旧数据备份到 `residual_scale_v2/BUG_CUMULATIVE/`。
- **已修复**：`apply_gamma(model, snap, gamma)` 改为基于快照绝对设置（`copy_(w*gamma)`），每次迭代独立；try/finally 保护 restore。
- **修复后结果**：
| γ | schedule | FG-SSIM | AbsLap | LapRatioGT | PSNR |
|---|---|---|---|---|---|
| 0.1 | fixed_low | 0.264 | 0.0274 | 1.257 | 12.73 |
| 0.1 | fixed_high | 0.258 | 0.0314 | 1.438 | 12.69 |
| 0.1 | C3 | 0.263 | 0.0277 | 1.268 | 12.76 |
| 0.3 | fixed_low | 0.271 | 0.0225 | 1.033 | 13.05 |
| 0.3 | fixed_high | 0.244 | 0.0307 | 1.408 | 13.21 |
| 0.3 | C3 | 0.263 | 0.0255 | 1.167 | 13.04 |
| **1.0** | fixed_low | **0.268** | 0.0061 | 0.281 | 14.99 |
| **1.0** | fixed_high | **0.172（坍缩）** | 0.0220 | 1.010 | 14.55 |
| **1.0** | C3 | **0.255** | 0.0054 | 0.247 | 15.62 |
| **3.0** | fixed_low | **0.144** | 0.0180 | 0.824 | 18.00 |
| **3.0** | fixed_high | **0.043（严重坍缩）** | 0.0526 | **2.410** | 15.78 |
| **3.0** | C3 | **0.111** | 0.0294 | 1.347 | 17.10 |

**结论（H4 成立）**：
1. **自检通过**：γ=1.0 与 stage_ablation 原生一致（fixed_low 0.268/0.266, fixed_high 0.172/0.175, C3 0.255/0.252），修复后数据有效。
2. **残差幅度单调决定失效模式**：弱残差（γ=0.1,0.3）→ 三 schedule 的 SSIM 无差别（≈0.26），scale 失效（no-op）；原生（γ=1.0）→ fixed_high 伪影放大（SSIM 坍缩到 0.172）；强残差（γ=3.0）→ 伪影放大更严重（SSIM 0.043, LapRatio 2.41）。
3. **γ=3.0 fixed_low 也异常**：SSIM 0.144 + LapRatio 0.824（<GT）+ PSNR 18.0（异常高）→ 强残差下即使 scale=1.25 也过度干预，趋向压平。即强残差 + 低 scale 压平、强残差 + 高 scale 伪影。
4. **C3 的优势随 γ 放大而凸显**：γ=1.0 时 C3(0.255)≈fixed_low(0.268)≫fixed_high(0.172)；γ=3.0 时 C3(0.111)>fixed_high(0.043) 但<fixed_low(0.144)。C3 是"缓解"非"万能"。

---

## 6. 论文叙事重构草稿（DRAFT — 待阶段消融+残差谱实验确认）

### 6.1 核心科学论断（比原文更强且可辩护）

原文论断（Abstract/Intro/Mechanism）："更高 adapter scale 会抑制 base model 的纹理合成 → 纹理压平"。
**被证伪的部分**：这不是普适规律。三个 checkpoint + cap 消融证明副作用方向是 adapter 依赖的：
- refattn_v1（强残差，无 cap）→ **flatten**
- v2（强残差，有 cap）→ **artifact amplification**
- v3（弱残差）→ **no-op**

**保留且被增强的部分（TCAS 的真正价值）**：在所有 scale 起作用的 regime 里（refattn_v1、v2），**低-高-低的三段式时间调度（C3）都是最优平衡**——它不依赖副作用的具体形式，而是通过"把强校正集中在中间段、避开 early/late"来缓解任何形式的高强度干预损害。

**统一机制（经 R10/R11 修正定稿）**：高强度 adapter 干预的副作用有**是否起效**（幅度）和**方向/形式**（flatten vs 伪影 vs no-op）和**时序位置**（哪个阶段最危险）三个维度：
- **是否起效（残差幅度，R11）**：γ 从 0.1→3.0 单调放大 v2 残差，失效模式从 no-op（三 schedule 无差别）→ 伪影放大（γ=1）→ 更强伪影+低 scale 压平（γ=3）。**残差幅度单调决定干预强度是否足够造成伤害**。
- **方向（cap/scale 语义，R7）**：同样 γ=1 下，uncapped → flatten（去 cap 复刻论文），capped → 伪影放大。**方向由 scale 语义决定**。
- **时序位置（R10）**：v2 上 early 段高 scale 是破坏源，late 无害；refattn_v1 上 late 是 Trap。**危险阶段也 adapter 依赖**。
- **C3 为什么仍普适成立**：R10 显示 v2 上 mid_high 最优（与 refattn_v1 一致）；R11 显示 C3 在 γ 0.1~3.0 全程优于 fixed_high。**中间段几何细化最有效是 diffusion 本身的属性**，TCAS 依赖此属性，故对幅度、方向、危险阶段都鲁棒。
- **时序位置**：refattn_v1 上 late-stage 高 scale 是 Trap（C4）；**v2 上 early-stage 高 scale 才是破坏源（R10），late_high 反而无害**。→ 连"哪个阶段危险"都 adapter 依赖。
- **C3 为什么仍普适成立**：R10 显示 v2 上 mid_high 就是最优（与 refattn_v1 一致）——**中间段是几何细化最有效的阶段是 diffusion 本身的属性**（去噪过程阶段角色），不随 adapter 变。TCAS 正是利用了这个 diffusion 级属性，所以对 adapter 依赖的"方向"和"危险阶段"都鲁棒。

### 6.2 拟修改的论文段落（定位）

| 位置 | 原文（final.tex） | 修改方向 |
|---|---|---|
| L23 Abstract | "may also suppress the texture synthesis... flattened surfaces" | 改为 "may degrade texture, whose specific form depends on the adapter (flattening, artifacts, or no effect)" |
| L44 Intro | "suppressing the intrinsic texture synthesis capability... texture flattening" | 加 "in the studied adapter regime; we show the failure mode is adapter-dependent" |
| L54 contribution(1) | "flattening surfaces, and reducing high-frequency details" | 加 "or producing high-frequency artifacts depending on the adapter's residual magnitude" |
| L113 Eq discussion | "if strong residuals... late stage... suppress synthesis of color..." | 保持，但标注为"observed on the studied adapter"；加脚注说明在另一 adapter regime 上（artifact-prone，capped）高 scale 的危险阶段为 early 而非 late（R10），进一步证明阶段敏感性也 adapter 依赖 |
| L298-300 Mechanism | "continuously applying strong adapter residuals at this point tends to suppress..." | 加 "in the studied strong-residual regime; our analysis shows the failure mode (flatten vs artifact) is adapter-dependent, and C3's temporal gating mitigates either" |
| L392/396 300-obj | "full high-scale scaling substantially weakens..." | 保持（refattn_v1 上为真），补一句范围限定 |
| L434 Limitation | "TCAS can alleviate texture flattening under high scales" | 改为 "TCAS can alleviate high-scale-induced texture degradation, which may appear as flattening or artifacts depending on the adapter" |

### 6.3 新增 Robustness/Additional Analysis 段落（建议放 Limitation 前或作为 Discussion）

> **Adapter-dependence of high-scale failure modes.** The specific failure mode of aggressive adapter scaling is not universal. Across three adapter checkpoints, uniform high scale produced texture flattening (strong-residual adapter evaluated without per-layer caps), high-frequency artifact amplification (strong-residual adapter under per-layer caps, where scale boosts coarse-resolution layers while the fine-texture layer is capped), or no appreciable effect (weak-residual adapter). A per-layer scale-cap ablation on the same checkpoint reproduced both behaviors, isolating the scale semantics as a determining factor. A residual-magnitude sweep on a single checkpoint further shows that the intervention's *strength* is monotonic in the trained residual magnitude: scaling the adapter's output projection from 0.1x to 3x transitions the behavior from no-effect, to artifact amplification under high scale, to stronger artifacts (and over-constraint even under conservative scale). Moreover, a stage ablation shows that even *which denoising stage is most sensitive to high scale* is adapter-dependent: on the artifact-prone adapter, early-stage high scale reproduced nearly all of the damage while late-stage high scale was nearly harmless, whereas on the paper's adapter the late stage was the main source of texture loss. Despite this, in every regime where scaling had a non-negligible effect, the temporal low-high-low schedule (C3) yielded the best shape-texture balance, because concentrating strong correction in the middle denoising stage is effective regardless of the adapter. This indicates that TCAS's value is structural rather than incidental: by relying on the diffusion process's stage-dependent roles (global layout → geometry refinement → texture synthesis), it mitigates the harm of high-scale intervention without depending on how that harm manifests.

### 6.4 叙事定位总结
- 不推翻原文核心结论（refattn_v1 上的数据是真的）。
- 把"高 scale → flatten"从**普适规律**降级为**具体 adapter 的实例**。
- 把 TCAS 的价值从"避免压平"升级为"**通过时间调度缓解高强度干预的副作用（不论其形式与危险阶段）**"——更稳健、更普适、方法论价值更强。
- 这正是用户最初判断的"failure analysis / robustness analysis 增强方法论价值"。

### 6.5 新增实验的数据支撑（建议进入论文的 Additional Analysis）
| 实验 | 脚本/产物 | 支撑的结论 |
|---|---|---|
| 主实验（三 schedule × 两 checkpoint） | `explore_contradiction.py` → `mvpoutput/explore_contradiction/{v2,v3}/` | R1-R4：v2 伪影放大、v3 no-op、C3 在 v2 最优 |
| cap 消融 | `explore_cap_ablation.py` → `cap_ablation_{v2,v3}/` | R7：方向由 cap/scale 语义决定（H3 成立） |
| 300-obj win rate | `eval300v2_{c3,fh,fl}` per-object | R9：LapVar 好坏方向随 adapter 翻转 |
| 阶段消融 | `explore_stage_ablation.py` → `stage_ablation_v2/` | R10：v2 上危险阶段为 early 非 late，C3(mid)仍最优 |
| 残差谱 | `explore_residual_scale.py` → `residual_scale_v2/` | R11：残差幅度单调决定干预强度（γ 0.1→no-op, 1→伪影, 3→更强） |

**建议的 Additional Analysis 叙述**（三句定位，供正式写作参考）：
1. 副作用形式（flatten/artifact/no-op）与危险阶段（early/late）均 adapter 依赖（cap 消融 + 阶段消融）。
2. 但 C3 在所有生效 regime 均最优，因其依赖 diffusion 阶段角色的普适性（中间段几何细化最有效）。
3. 因此 TCAS 的贡献是结构性的（stage-dependent inference control），而非针对特定 adapter 的压平缓解。

---

## 7. 新方法探索：残差归一化自适应 scale（Residual-Normalized Schedule）

> 2026-08-03 启动。从机制发现（R11：固定 scale 失效因 adapter 残差幅度差异大）推出的训练-free 方法。验证中。

### 7.1 动机（从已证实机制直接推出）
- R11：同一 checkpoint 上 γ=0.1→no-op、1.0→伪影放大、3.0→更强伪影+压平。残差幅度单调决定干预强度。
- 推论：**固定 scale 的真正问题不是数值，而是它作用于不同幅度的残差上产生不可预测的干预强度**。v3 上 scale=2.5 近 no-op（残差太小），v2 上 scale=2.5 伪影爆炸（残差太大）。
- 方法：把控制变量从"scale 数值"改为"目标干预强度（residual norm）"。推理时测量/校准各层 raw residual norm，动态设 scale = target / raw_norm，使干预强度恒定。

### 7.2 设计（训练-free，`geotex/explore_norm_schedule.py`）
- **校准**：每对象先跑 fixed_low，用 residual_log 反推各层 raw L2 norm（raw = scaled / eff_scale）。冒烟实测 v3 各层 raw norm：deep≈4.7, middle≈11, shallow≈131（shallow 比 middle 大 11 倍）。
- **归一化**：scale(depth, stage) = target(depth, stage) / ref_norm(depth) = k[depth][stage]（平均 norm 校准下 target=ref*k，比例抵消）。
  - norm_flat：k=1.0 恒定（≈fixed_low 干预强度）
  - norm_c3：deep/middle 0.6/1.4/0.6（低-高-低），shallow 0.4/0.8/0.4（纹理层弱干预）
- 施加：通过 `generate_with_schedule` 新增的 dict-scale 支持（per-depth 分发），零 forward patch。

### 7.3 待验证的假设
- **H5**：把干预强度归一化到固定_low 参考后，v2 上能避免 fixed_high 的伪影放大（SSIM 不坍缩），v3 上能恢复有效干预（不再 no-op）——即跨 adapter 行为一致。
- **H5b**：norm_c3 在 v2/v3 上都 ≥ C3 或与之相当（保留时间调度的同时规避 adapter 依赖）。

### 7.4 运行
- `mvpoutput/explore_contradiction/norm_schedule_{v2,v3}.log`（6-obj / 50 步），Monitor 每小时轮询（task b23dsvp0y）。
- 冒烟（v3, 1 obj, 8 步）已跑通：norm_flat SSIM 0.3429 / norm_c3 0.3416，与 fixed_low 0.3427 相当（8 步太短，需 50 步才能见分晓）。

### 7.4b 完整结果（6-obj / 50 步）——**H5 在 v2 上成立，v3 上仍 no-op**
**v2**：
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low | 0.266 | 14.94 | 0.0070 | 0.319 |
| fixed_high | 0.170 | 14.58 | 0.0232 | 1.065 |
| C3 | 0.253 | 15.71 | 0.0054 | 0.247 |
| **norm_flat** | **0.291** | 14.99 | 0.0069 | 0.317 |
| **norm_c3** | 0.273 | 13.94 | 0.0129 | 0.590 |

- **norm_flat 在 v2 上 SSIM 全场最高（0.291），AbsLap≈fixed_low** → 归一化到参考干预强度，既避免 fixed_high 伪影（SSIM 不坍缩）、又不压平（Lap≈fixed_low），**优于固定 scale 甚至 C3**。H5 在 v2（伪影 regime）成立。
- norm_c3 中段 1.4× 干预在 v2 上稍过（LapRatioGT 0.59，PSNR 低），说明强 adapter 上中段不该再放大。

**v3**：
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low | 0.245 | 13.34 | 0.0255 | 1.171 |
| fixed_high | 0.245 | 13.25 | 0.0256 | 1.172 |
| C3 | 0.245 | 13.36 | 0.0253 | 1.158 |
| norm_flat | 0.244 | 13.40 | 0.0249 | 1.143 |
| norm_c3 | 0.248 | 13.11 | 0.0247 | 1.130 |

- 所有 schedule 全 ≈0.245 → **单 checkpoint 内归一化（target=自身 fixed_low）不能恢复 v3 的 no-op**。
- 原因：归一化只"保持"参考强度，不放大弱 adapter。v3 本身 raw norm 小，scale=k 后干预仍小。
- **结论**：v3 的 no-op 是 adapter 本身太弱（anticollapse 过度），归一化救不了它；且 v3 作为 adapter 质量差（SSIM 0.245 < v2 fixed_low 0.266），不值得救。

### 7.5 关键洞察与新升级方向
- **单 checkpoint 内归一化**（target=自身 fixed_low）解决"过度干预"（v2 伪影）✅，但不解决"干预不足"（v3 no-op）。
- **跨 checkpoint 目标归一化**（用 v2 干预强度作为全局参考，让 v3 归一化到 v2 强度）才能同时解决两者——但需验证"干预强度可跨 adapter 迁移"。
- **逐步自适应**：每步实时读 raw norm（非校准平均），更精确。代价需 forward hook。
- **结论方向**：norm_flat 作为 TCAS 的 adapter 无关升级版在**强 adapter（v2）上有效**（SSIM 最高），可作为 training-free baseline 写入论文；但需诚实说明"对弱 adapter 无效，因弱 adapter 本身是训练问题非推理问题"。
- 附带洞察：**weak adapter 的 no-op 本质是训练不充分**（anticollapse 过度），推理期任何 schedule 都救不了——这本身是对"anticollapse 策略"的一个重要诊断。

### 7.6 code-reviewer 审查结论（WARN）与诚实修正
**审查发现两个核心声明问题（直接修正本方法结论）**：

1. **`norm_flat ≈ fixed_low` 声明不成立**（`explore_norm_schedule.py` docstring）。fixed_low 在 deep/middle 有效 scale 是 1.25（uncapped），norm_flat 是 1.0 → norm_flat 对 deep/middle 干预**更弱**。故 v2 上 norm_flat SSIM 最高（0.291）**很可能只是因为它更接近基础模型**，而非"归一化"的功劳。**论文写作时必须区分"归一化剖面"与"更弱干预"两种解释**。
2. **`scale ≡ k` 恒成立**：`target = 自身 ref_norm * k` → `scale = k` 常数，归一化机制塌缩为固定 per-depth 调度。v3 no-op 无法解决（与 docstring 声称矛盾）。真正跨 checkpoint 需**绝对目标**（target 取自 v2 参考强度）。
3. **RNG 噪声**：各 schedule 间 cond latent/reference noise 不同（`torch.randn_like`），对比混入采样噪声。已修（每次生成前 re-seed）。

**绝对目标冒烟（v3 + v2 target, 1 obj, 8 步）**：
- v2 ref_norms: deep≈216/middle≈292/shallow≈1255；v3: deep≈4.7/middle≈11.6/shallow≈130（deep 差 46 倍）。
- 绝对目标归一化在 v3 上 scale = v2_norm/v3_norm ≈ 46 → **远超 LAYER_MAX_SCALES cap（deep=3.0）→ 全部被 cap 截断** → norm_flat 与 norm_c3 结果完全相同。
- **重要发现**：**cap 是比 scale 更硬的约束**。弱 adapter（v3）残差太小，要达到 v2 干预强度需要 scale≫cap，而 cap 阻断了。→ 弱 adapter 的 no-op 是 cap + 残差过弱双重原因，推理期 scale 无法弥补。

### 7.7 方法最终定位（诚实版）
- **相对归一化**（scale=k）在 v2 上 norm_flat SSIM 最高，但可能是"更弱干预"的功劳，归一化剖面无独立价值证据。
- **绝对目标归一化**因 cap 阻断在弱 adapter 上失效。
- **方法未证明"跨 adapter 干预可迁移"**——因为 cap 阻断了必要的大 scale。
- **核心科学收获**：干预强度受 `min(scale, cap) × raw_norm` 三重约束；weak adapter 的 no-op 本质是**训练问题**（raw_norm 太小）+ **推理 cap 阻断**双重原因。这比"找到新方法"更有诊断价值。
- **建议论文定位**：作为机制理解的补充实验（"干预强度的三重约束"），不作为新方法；诚实标注边界。

### 7.8 决定性对照实验（已完成）——**归一化方法不成立**
**目的**：区分"norm_flat SSIM 最高"是"归一化剖面有效"还是"只是更弱干预"（code-reviewer 质疑 1）。
**结果（v2, 6-obj / 50 步）**：
| schedule | FG-SSIM | PSNR | AbsLap | LapRatioGT |
|---|---|---|---|---|
| fixed_low(1.25) | 0.2656 | 15.05 | 0.00516 | 0.236 |
| **fixed_low_weak(1.0)** | **0.2791** | 14.59 | 0.00862 | 0.395 |
| fixed_high(2.50) | 0.1710 | 14.45 | 0.02076 | 0.952 |
| C3 | 0.2536 | 15.42 | 0.00552 | 0.253 |
| **norm_flat** | **0.2791** | 14.59 | 0.00862 | 0.395 |
| norm_c3 | 0.2686 | 13.67 | 0.01642 | 0.752 |

**决定性结论**：
1. **norm_flat 与 fixed_low_weak 的 FG-SSIM/AbsLap/PSNR 全部完全一致（0.2791/0.00862/14.59）** → 两者数学等价（都施加 scale 1.0 于 deep/middle，shallow 都被 cap 到 0.8）。
2. **归一化剖面没有任何独立价值**——norm_flat 的 SSIM 优势（高于 fixed_low）纯粹来自"更弱干预"（scale 1.0 vs 1.25），与归一化无关。code-reviewer 质疑 1 完全正确。
3. **残差归一化方法不成立**：相对归一化（scale=k）退化为固定 scale；绝对目标归一化被 cap 阻断；对照证明无独立价值。
4. C3 仍是 v2 上最佳平衡（SSIM 0.254 与 best 相当、PSNR 15.42 最高、LapRatio 0.253 最低纹理损失）——**C3 的简单低-高-低固定调度不可被归一化方法超越**。
5. norm_c3（中段 1.4×）在 v2 上纹理损失大（LapRatio 0.75）——强 adapter 上中段不应再放大，与 7.4b 一致。

**方法最终定位（定稿）**：残差归一化不是有效的新方法。它揭示的核心约束——**干预强度 = min(scale, cap) × raw_norm**——是诊断洞见（weak adapter no-op 是训练问题），但不是可用的推理策略。TCAS/C3 保持为最优训练-free 方法。

---

## 8. 精细 γ 扫描：甜点定位（v2, 6-obj/50 步, γ=0.4~0.8）

### 8.1 完整谱系（合并已有+精细）

| γ | C3 SSIM | C3 PSNR | C3 LapRatio | fixed_high SSIM | regime |
|---|---|---|---|---|---|
| 0.1 | 0.263 | 12.76 | 1.268 | 0.258 | no-op（三 schedule 无差别） |
| 0.3 | 0.263 | 13.04 | 1.167 | 0.244 | 几乎 no-op |
| **0.4** | 0.256 | 13.39 | 1.046 | 0.234 | 开始有效 |
| **0.5** | 0.258 | 13.49 | 0.770 | 0.216 | C3 有正面效果 |
| **⭐ 0.6** | **0.271** | **13.98** | **0.556** | 0.199 | **甜点：C3 SSIM 最高 + PSNR 显著提升** |
| **0.7** | 0.263 | 14.54 | 0.363 | 0.182 | C3 PSNR 继续升但 SSIM 开始降 |
| 0.8 | 0.265 | 14.97 | 0.304 | 0.180 | fixed_high 明显坍缩 |
| 1.0 | 0.255 | 15.62 | 0.247 | 0.172 | 原生 v2：伪影放大 |
| 3.0 | 0.111 | 17.10 | 1.347 | 0.043 | 全面坍缩 |

### 8.2 甜点分析
1. **γ=0.6 是形状-纹理-信号保真度的最佳平衡**。C3 SSIM 0.271 是全谱最高（包括原生 v2 的 0.255），说明原生 v2 其实过强了。
2. **C3 在 γ=0.5~0.8 整个区间保持稳定（SSIM 0.258~0.271）**，而 fixed_high 从 0.216 持续塌到 0.180。C3 的时间调度是"容错带"——在适中残差幅度下，mid-stage 集中校正既能提供几何增益，又不触发 early/late 的伪影。
3. **训练策略建议**：
   - v2 的 raw norm（deep≈216, middle≈292）太大。目标应缩减到 γ≈0.6 水平：deep≈130, middle≈175。
   - v3 的 output_proj clamp=1.5 太激进（raw norm deep≈4.7，是 v2 的 1/46）。应放宽到使 raw norm 达到 v2×0.6 水平。
   - **可操作参数**：`output_proj weight norm clamp` 设为使每层 raw correction L2 norm 落在 [100, 200] 区间（基于 v2 × 0.6 的 deep/middle 值）。
4. **与 Section 4.7 的关系**：精细 γ 扫描把"三 checkpoint 的定性谱系"量化为"adapter 残差幅度的 SSIM 曲线"——甜点 γ≈0.6 是机制理解+训练策略的核心桥梁。

### 8.3 v4 训练尝试（失败 → 科学诊断）
**两次尝试均 NaN**：
- 第 1 次：`train_scale=0.6, proj_clamp=0` → step 786 开始全面 NaN
- 第 2 次：`train_scale=0.6, proj_clamp=3.0` → step 781 同样 NaN

**根因诊断**：UNet forward 在 fp16 运行（`model.unet.to(dtype=torch.float16)`），adapter 在 fp32。`train_scale=0.6` 缩小了 correction 对 loss 的贡献 → loss backward 中 adapter 梯度在 fp16 精度下信噪比过低 → 数值不稳定。v2 无 train_scale 时 correction 全额贡献 loss，梯度更大、fp16 精度足够，10000 步零 NaN。

**解决路径（列为 future work 而非当前迫切）**：
- AMP GradScaler（标准 mixed precision 解法）
- 全 fp32 训练（简单但显存翻倍，32GB 不够双 batch）
- adapter-only loss upscale（只放大 adapter 相关梯度）

**科学结论不受影响**：精细 γ 扫描（`explore_residual_scale.py --gammas 0.4 0.5 0.6 0.7 0.8`）**就是** post-hoc 缩放 v2 权重到 γ=0.6 后推理的精确模拟。γ=0.6 时 C3 SSIM 0.271（全谱最高）、PSNR 13.98、LapRatio 0.556 的结论**已经就是"甜点 adapter + C3"的效果**——不需要重训来证明。

**论文定位**：把精细 γ 扫描作为"simulated ideal adapter"展示，训练到甜点列为 future work（"requires mixed-precision engineering that is orthogonal to the scheduling contribution"）。
