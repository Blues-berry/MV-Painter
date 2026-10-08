# 颜色异常因果诊断

日期：2026-10-08

## 范围与身份

本次只回答颜色问题是否来自基础生成、Adapter、LLH、去噪后段或 VAE。没有继续搜索 Gate 阈值、Adapter Scale 或时间步组合，也没有用 GT 对输出做颜色校正。

P1 主对照是冻结的 26 对象诊断集：6 个原 Fig. 4/6 对象和 20 个已有 Fresh C 面板。条件为 No Adapter、GFL、LLH，共 78 个同对象条件行；相同对象 seed、条件图像、几何输入、checkpoint 和 unique6 目标视角。该集合是已筛选的失败诊断集，不是独立随机确认集。checkpoint SHA-256 为 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`，base runner SHA-256 为 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`，配置 SHA-256 为 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`。对象、GT PNG、前景 mask、输出 PNG 的身份逐行列在 `COLOR_FIDELITY_PAIRED_RESULTS.csv`；视觉标签和原始对象条件见 `OBJECT_FAILURE_TABLE.csv` 与 `SAMPLE_FREEZE.csv`。

CIEDE2000 / Δa* / Δb* 由 `build_paired_color_results.py` 对逐行 SHA 标记的 RGB PNG 重算，六个 mask 前景 tile 等权。Laplace、梯度、高频能量、颜色熵和 RGB 标准差由 `geotex.metrics_extended.compute_all_extended` 对同一批 PNG 和冻结 mask 重算；这两组后处理使用 Python 3.13.5、torch 2.7.1、numpy 2.2.6、scikit-image 0.26.0、Pillow 12.2.0。FG-PSNR、FG-LPIPS、Edge-SSIM 来自 `logs/RGB_RELOADED_METRICS.csv`，由 Python 3.10.20、torch 2.7.0、torchvision 0.22.0 在 CUDA:0 对已保存 PNG 重算，AlexNet LPIPS weights SHA-256 为 `df73285e35b22355a2df87cdb6b70b343713b667eddbda73e1977e0c860835c0`。该表逐行保存 prediction/reference/mask PNG SHA，P1 生成配对表时强制校验哈希，且重新生成的 dataset mask 与冻结 mask PNG 逐像素相同。统计以对象为单位配对，bootstrap 20,000 次、seed 61008；均值差、95% paired bootstrap CI、Cohen's dz、获胜对象数见 `P1_PAIRED_SUMMARY.csv`。完整 SHA 链记录在身份 JSON 和 `SHA256SUMS.txt`。

## A. No Adapter 是否已经有相同偏色？

是。两个原 Fig. 4 对象在 No Adapter 输出中已被视觉复核标注为粉色/粉紫色偏；GFL 和 LLH 中同样能看到色相偏移。No Adapter 的平均 CIEDE2000 最大，且在 13/26 对象上出现可见结构/身份损伤。这说明同一类视觉失败在没有 Adapter 时就存在，不能简单归因于 Adapter 单独制造偏色。

| 对象 | 条件 | CIEDE2000 | Δa* | Δb* | FG-PSNR | FG-LPIPS | 视觉标签 |
|---|---|---:|---:|---:|---:|---:|---|
| Fig. 4 row 1, idx 4 / seed 46 | No Adapter | 55.157 | −15.531 | −11.382 | 3.639 | 0.329 | 粉色偏、细节损失、结构损伤 |
|  | GFL | 22.032 | +1.977 | −0.639 | 11.587 | 0.230 | 粉色偏、细节损失 |
|  | LLH | 32.262 | −2.659 | −1.968 | 8.975 | 0.250 | 粉色偏、细节损失 |
| Fig. 4 row 3, idx 12 / seed 54 | No Adapter | 49.357 | −11.102 | +19.189 | 4.543 | 0.309 | 粉色偏、细节损失、结构损伤 |
|  | GFL | 25.765 | +1.543 | +13.701 | 11.809 | 0.274 | 粉色偏、细节损失 |
|  | LLH | 33.236 | −1.876 | +16.765 | 9.771 | 0.275 | 粉色偏、细节损失 |

视觉粉色偏标签来自冻结的完整六视角复核；连续 Lab 标量和视觉标签描述不同现象。严格 Lab “紫色”旗标为 0/26，未能捕捉被看到的粉色偏，因此不把该旗标为零解释为没有色相异常。

## B. Adapter 是否系统性增加色差？

不是。GFL − No Adapter 的对象级平均 CIEDE2000 为 −19.654，95% CI `[−26.370, −13.248]`，Cohen's dz `−1.135`；24/26 对象色差下降。FG-PSNR 平均增加 6.646 dB `[5.556, 7.635]`，25/26 对象更高；FG-LPIPS 平均降低 0.0325 `[−0.0536, −0.0107]`，18/26 对象更低。整体上 GFL 改善了相对 GT 的重建匹配，但两例粉色偏在 GFL 下依旧可见。

Adapter 改变了色差向量：GFL − No Adapter 的平均 Δa* 为 +4.561 `[3.003, 6.379]`、Δb* 为 +3.057 `[0.860, 5.615]`。这表示色差方向改变，不代表所有对象色相向量都改善。两个失败对象在 GFL 下仍有明显偏差；不能据整体均值宣称颜色保真已经解决。

## C. LLH 相对于 GFL 改善了什么？

主要变化是纹理/细节压低，不是结构改善或颜色修复。

- LLH − GFL 的平均 CIEDE2000 为 `+3.583`，95% CI `[+0.462, +6.712]`，即平均颜色误差更高；只有 9/26 对象的 CIEDE2000 更低。
- FG-PSNR 差 `−0.197 dB`，CI `[−1.562, +1.297]`；Edge-SSIM 差 `−0.0008`，CI `[−0.0078, +0.0066]`。没有稳定结构收益。
- FG-LPIPS 差 `−0.0129`，CI `[−0.0274, +0.0007]`，区间触及零；该小幅变化不足以证明可靠的感知改善。
- Laplacian variance 差 `−0.00406`，CI `[−0.00535, −0.00291]`，0/26 对象更高；梯度差 `−0.06772`，CI `[−0.08132, −0.05494]`，0/26 更高；高频能量差 `−0.00887`，CI `[−0.01091, −0.00672]`，1/26 更高；颜色熵差 `−0.598`，CI `[−0.703, −0.502]`，0/26 更高。

所以 LLH 的主要、稳定效应是减少细节和局部颜色变化；它没有形成颜色准确度或结构质量上的净改善。

## D. 色偏最早在哪个阶段出现？

在 Fig. 4 row 1 的同环境逐步解码中间图里，GFL 在 scheduler update 40 已出现可辨识的粉红表面。update 25 和 33 的高噪声解码图还不具备可靠的物体外观，因此只能把现象定位到采样后段，不能声称确切首次 latent step。该轨迹的 update 40 / 45 / 49 平均 CIEDE2000 分别为 37.446 / 30.325 / 22.032，Δa* 分别为 +7.917 / +10.500 / +1.977；最后一张和 P1 保存 PNG 逐字节相同。

“在解码后的 RGB 中看到颜色偏差”不是“VAE 解码器是根因”。该 RGB 经 VAE 从最终 latent 解码后、经白底映射并保存，位于纹理烘焙和 GLB 导出之前；中间轨迹显示颜色结构在最终解码前已经可见于 latent 的解码快照。这表明问题属于生成路径的后段，但不能仅凭残差相关性或解码图像本身断言 Adapter 残差或 VAE 单独导致偏色。

## E. 参考颜色条件够不够？偏差属于什么性质？

条件更接近“单张外观图 + 几何”，不是为每个目标视角提供密集颜色 ground truth。数据集在每个对象中选 `000.png` 或 `014.png` 作为一张 `cond_imgs`，并读取对象级 `global_embeds.npy`；随后生成六张唯一目标视角。代码位置为 `MVPainter/src/data/mvpainter_dataset.py:460–496, 576–590`。目标六视角 PNG 用作诊断参考，不是生成器逐像素直接复制的条件。因此评价量描述的是相对于渲染 GT 的重建误差；单张 RGB 条件不能证明目标视角颜色被充分约束。

对两例原 Fig. 4 对象，RGB 与 GT 的明显偏差既是可测重建误差，也是视觉复核认为不自然的色相偏移。由于没有色卡、实物测量或独立材质颜色标准，本报告不能把渲染 GT 等同真实世界绝对颜色，也不能把所有 CIEDE 差异都定义为物理上“不可能”的颜色伪影。适当表述是“相对于参考渲染的颜色不匹配；两个例子另有可见的非预期粉色/粉紫偏色”。

## VAE encode–decode 隔离对照

同一个 Fig. 4 row 1 的六视角 GT RGB 直接经 VAE encode–decode，不经扩散去噪或 Adapter。输入映射 `(RGB_0_1 − 0.5)/0.8`，解码映射 `0.8×decoded + 0.5`；对 posterior mode 和固定 seed 42 posterior sample 各做一次。前景平均 CIEDE2000 为 4.086 / 4.087，平均 Δa* 约 −1.35；GT round-trip 没有复现 GFL 输出的偏色方向和量级。对齐的 GFL final RGB 为 CIEDE2000 22.032、Δa* +1.977。

这排除“同一 VAE 的普通 GT 往返误差足以解释全部粉色偏差”这一简单解释，但没有排除 decoder 对生成 latent 的分布依赖，也没有单独替换 decoder、比较 latent 解码或检验不同色彩空间。VAE 可带来轻微颜色变化；目前证据不支持将它认定为完整根因。

## P2 修复实验决策

**没有启动新的修复候选。** P1 没有找到可以独立操纵并能解释偏色的明确颜色因果点：No Adapter 已出现同样的视觉偏色；GFL 在整体上降低色差但不能修复两个显眼个例；LLH 主要压低细节；VAE round trip 只说明普通 VAE 转换不是充分解释。继续改 Gate、Scale 或时间步调度将变成参数搜索，不能作为受证据支持的唯一修复实验。

此前唯一的 feature-relative residual gate 原型是负结果：C3+gate 相对 C3 在 26 对象上 CIEDE2000 增加 1.35，历史 6 个 Fig. 4/6 对象增加 3.18，且没有视觉上明确减少粉色偏。Linear+gate 虽优于 Generic Linear，但相对 GFL 仍高 3.30 CIEDE2000，原 Fig. 4/6 也没有明确颜色修复。该证据不得包装成解决颜色问题的新方法。

## 图像、指标及复核路径

- 78 个原始 RGB 指标行和每行对象/GT/mask/PNG/checkpoint/runner 哈希：`COLOR_FIDELITY_PAIRED_RESULTS.csv`。
- 对象配对效果、bootstrap CI、Cohen's dz、逐对象获胜数：`P1_PAIRED_SUMMARY.csv`。
- 评价身份与版本：`P1_PAIRED_RESULTS_IDENTITY.json`。
- 早期/中期/后段中间 RGB 和指标：`P1_STAGE_TRAJECTORY.csv`；轨迹图片都在 `evidence_rgb/stage_fig4_row1_gfl/`。
- GT、No Adapter、GFL、LLH、VAE mode/sample 原始 RGB：`evidence_rgb/p1/` 与 `evidence_rgb/vae_fig4_row1/`。
- VAE isolate 的对象、参数、逐视角指标和图像 SHA：`VAE_ISOLATION_RESULTS.json`。
- 逐图 SHA 与 checkpoint/runner/config、原始条件身份：`SHA256SUMS.txt`、`P0_REPRO_TRACE_LOCK.json`、`P1_PAIRED_RESULTS_IDENTITY.json`。
