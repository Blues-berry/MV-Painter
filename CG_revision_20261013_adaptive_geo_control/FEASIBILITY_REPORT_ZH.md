# 自适应几何控制支线：预研与停止门

日期：2026-10-13（Asia/Shanghai）  
结论：**当前代码路径不进入新算法实现；保留一个更窄、可证伪的后续研究方向。**

## 任务范围

核查“按时间、层和表面区域，根据几何可信度、参考外观偏离和跨视角对应可信度调节几何残差”是否能在现有 GeoTex/MV-Painter 推理路径中实现，并判断它是否区别于已有方法和实验。

本轮只读检查了模型、数据和已归档实验。没有改动模型、修回件或旧实验，没有启动 GPU 任务。主线工作区原有的 manuscript 修改状态保持不变。

## 关键假设核验

| 信号 | 现有路径可否直接提供 | 核验结果 |
|---|---|---|
| 几何可信度 `c_geo` | 部分可以 | adapter 当前接收由 normal、depth、mask 构成的五通道几何输入，可以据此建立可见性或边缘等几何代理；它们尚不等于经过校准的表面可信度。 |
| 参考外观偏离 `c_app` | 不可以 | `GeoTexResnetWrapper` 只持有几何特征、层组和残差缩放；参考图特征由另一条 reference-attention 路径写入缓存，没有传到 adapter 控制器。要得到合法的局部偏离信号，至少还需暴露参考特征、构造参考移除分支，或把当前预测解码并与投影后的参考外观对齐。 |
| 跨视角表面对应 `c_view` | 不可以 | 六个视角的 normal/depth/mask 被拼成图像网格，但相机矩阵、UV/世界位置图或共享表面索引没有随几何特征传入 adapter。仅按图像网格逐像素调节不能保证对应到同一 3D 表面，也不能保证烘焙接缝处一致。 |

实现位置说明：`GeoTexResnetWrapper` 的当前输入与缩放路径见 [`model_unet_geotex.py`](../MVPainter/mvpainter/model_unet_geotex.py#L284)；五通道输入构造见同文件的 `prepare_batch_data`；六视图加载和相机选择见 [`mvpainter_dataset.py`](../MVPainter/src/data/mvpainter_dataset.py#L424)；reference 写入/读取发生在 [`mvpainter_pipeline.py`](../MVPainter/mvpainter/mvpainter_pipeline.py#L163)。数据工具虽读取了六视图 mask、normal、depth，但没有将相机或表面坐标并入 adapter 输入，见 [`data_utils.py`](../geotex/data_utils.py#L7)。

这说明当前缺口不是“再找一个门控公式”，而是控制器拿不到公式要求的两个关键局部状态。通过直接比较每个 UNet 像素的残差方向可以造出局部投影，但在没有表面坐标的情况下，它只是屏幕空间的局部 CFG/残差投影，不能支持“表面区域自适应”或烘焙一致的主张。

## 与已有研究和内部证据的重叠

最接近的先例是 RomanTex（ICCV 2025）：它明确处理参考图和几何条件冲突，使用几何相关 CFG，并投影参考条件项以在几何与外观之间切换。Scheduled Style Injection 已覆盖层与时间步上的注入调度；APG 已对扩散引导向量做平行/正交分解与投影；MVPaint 已将同步多视图生成、3D 空间补全和 UV 接缝修整组合进纹理流程。因此，“局部化一个冲突投影”本身不足以形成清楚的新方法差异。见文末论文链接。

仓库已有 `round012` 的全局/逐视角 conflict projection 证据：

- `view_projection` 在确认队列 64 个对象、3 个种子上，参考视角 FG-PSNR 均值差为 **+4.2827 dB**（95% CI `[+3.4089,+5.2052]`），CIEDE2000 差为 **−2.2299**（95% CI `[−3.0609,−1.5630]`）。
- 其他视角 FG-PSNR 均值差为 **−0.2824 dB**（CI `[−0.6722,+0.1022]`），FG-LPIPS 差为 **+0.00027**（CI `[−0.00153,+0.00207]`）。区间没有证明整体非劣；这也不是未见烘焙纹理的确认结果。对象曾在 Fresh C 工作中暴露过，不能称为完全新对象确认。
- 开发集上 `view_projection`、`interaction_projection` 与 APG projection 的非参考视角 LPIPS 差异均未明确分离。MV-Adapter 32 对象开发比较也没有证明候选稳定优于原生条件。
- 另有一个只读的小样本方向诊断（2 对象 × 3 步）显示冲突会随视角明显变化：逐视角反向平行能量比例在 **0.044–0.832** 之间；两个对象的第 24 步六视角范围分别为 **0.294–0.827** 和 **0.202–0.832**。这支持“不同视角不应被一个全局量完全概括”，但它没有像素级或 UV 表面级图，因此不能证明同一视角内的局部 gate 有用。文件：`/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/iteration012_condition_interference/full_v29_development_attempt01/INTERACTION_ROWS.json`。

来源及数字边界见 [`CONFIRMATION64_TEST.md`](../CG_revision_20261011_conservative_submission_r2/evidence/round012/confirmation64/CONFIRMATION64_TEST.md)、[`APG_REPORT.md`](../CG_revision_20261011_conservative_submission_r2/evidence/round012/apg/APG_REPORT.md) 和 [`MVA_REPORT.md`](../CG_revision_20261011_conservative_submission_r2/evidence/round012/mvadapter/MVA_REPORT.md)。这些结果支持“参考视角有收益迹象、其他视角需保守解读”，不支持把全局投影改成局部后就推断最终纹理会改善。

## 停止决定

**本轮 no-go：不在当前 GeoTex adapter 上加局部 gate，也不启动新生成矩阵。**理由是：

1. `c_app` 和 `c_view` 尚未进入 adapter 控制接口，直接实现会退化为未经表面配准的屏幕空间启发式。
2. 最近的图像/几何冲突投影方法已存在于 RomanTex，内部也已有全局和逐视角投影；仅增加空间索引或模块名称不能回应方法贡献质疑。
3. 已有候选的参考视角改善还没有转化为已见外视角或真实烘焙质量的可靠改善，当前没有理由扩大实验面。

这是对**当前实现接口和这次受控支线**的停止判断，不是证明 3D 表面自适应控制方向永远不可行。

## 若以后重启，什么才算不同的候选

候选必须在共同的 UV/世界表面坐标上工作，而不是只在二维网格或每视角标量上投影：

1. 从已知 mesh、相机和深度生成合法的表面坐标/可见性图，并与 latent 网格对齐；对同一 texel 的多视角样本共享控制状态。
2. 从 reference-attention 中间状态或无目标图的条件分支中取得局部外观信号；不得用测试对象 target RGB 选择控制强度。
3. 冻结一个无搜索参数的控制规则，例如只在表面对应可信且局部几何干预与可靠参考证据冲突时限制该区域的几何残差；无参考证据的区域维持几何约束。
4. 先用少量开发对象验证信号能否预测失败区域，再冻结对象与方向，至少对比 C3、Fixed High、Generic Linear、Late-high、现有 view/interaction projection 和适配到同一管线的 APG；通过门槛后才做独立对象、真实 UV 烘焙和未见视角评价。

在这些输入可以被明确读取和校准以前，不应把此候选描述为已实现或已具备新颖性的算法。

## 相关论文（截至 2026-10-13 核对）

- RomanTex, ICCV 2025： [官方论文页](https://openaccess.thecvf.com/content/ICCV2025/html/Feng_RomanTex_Decoupling_3D-aware_Rotary_Positional_Embedded_Multi-Attention_Network_for_Texture_Synthesis_ICCV_2025_paper.html)
- Scheduled Style Injection, CVPR 2026 NTIRE Workshop： [官方 CVF 论文 PDF](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf)
- Adaptive Projected Guidance： [arXiv 论文](https://arxiv.org/abs/2410.02416)
- MVPaint, CVPR 2025： [官方论文 PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Cheng_MVPaint_Synchronized_Multi-View_Diffusion_for_Painting_Anything_3D_CVPR_2025_paper.pdf)

## 审计来源哈希

代码与内部结果的 SHA-256 记录见 [`SOURCE_HASHES.json`](SOURCE_HASHES.json)。
