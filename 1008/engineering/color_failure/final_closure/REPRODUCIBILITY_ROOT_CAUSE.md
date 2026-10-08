# Fresh C 复现差异：根因定位

日期：2026-10-08

## 结论

Fresh C 的两组历史 RGB 身份分别由两套软件栈精确复现：Python 3.13 复现历史 `c3_confirmation` PNG；Python 3.10 复现此前 observer PNG。跨栈时，在输入张量完全一致的情况下，最早的已记录数值差异出现在第 0 个 UNet 调用之前：相同 FP16 初始 latent 乘以 scheduler 的 `init_noise_sigma` 后，所得 latent 不再逐元素相同。之后 UNet 输入、噪声预测、latent 轨迹、VAE 解码输入/输出和 RGB 图像均发生分歧。

因此，先前 120/120 图像不一致有可复现的软件栈差异解释；本次把计算差异定位到了首个发生变化的张量操作。由于 Python、PyTorch、Diffusers、Transformers 等版本同时变化，证据不能将原因唯一归到某一个库或底层 kernel，也没有对 120 个对象全部重跑。这个范围限制不影响以下三例上的逐层定位。

## 冻结对象与运行条件

对象在读取新输出之前按 `P0_REPRO_TRACE_LOCK.json` 锁定。全部为 Fresh C 的 `native_gfl`，每个条件均使用相同对象身份、几何/RGB 条件、初始 latent、seed、checkpoint、配置、runner 和六个互不重复的目标视角。

| 样本 | UID | 数据集索引 | 对象 seed | 选择层 |
|---|---|---:|---:|---|
| `freshc_panel_01` | `c76ac44df995482185077da81939b306` | 232 | 274 | 冻结 GFL FG-PSNR 最高 |
| `freshc_panel_03` | `ca887928bb664bcba121219f0af41293` | 236 | 278 | 冻结 GFL FG-PSNR 最低 |
| `freshc_panel_20` | `06fa4974f8cd4d4ea792e98fa1521457` | 10 | 52 | 冻结 GFL FG-LPIPS 最高 |

运行使用 50 步 `EulerDiscreteScheduler`、256×256 单视角输出、3×2 unique6 目标网格、一个 GPU shard；对象 seed 来自冻结 runner，初始 latent seed 为 42。P0 的 unique6 视角顺序为 `[0, 15, 12, 16, 13, 14]`。数据来自 `/4T/CXY/MV-Painter/1006/data/fresh_c/renders`。

身份基准：checkpoint SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`；推理配置 SHA-256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`；基础 runner `/4T/CXY/MV-Painter/scripts/run_validation_v3_experiment.py` SHA-256 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`。`P0_REPRO_TRACE_LOCK.json` 保存对象、输入、输出对照和比较规则。

## 运行环境

| 本次追踪 | Python | PyTorch / torchvision | Diffusers / Transformers | GPU 与精度 |
|---|---|---|---|---|
| Python 3.13 repeat 1/2 | 3.13.5 | 2.7.1+cu128 / 0.22.1+cu128 | 0.37.0 / 4.57.6 | RTX 5090，CUDA 12.8；UNet/VAE FP16，adapter 与几何编码器 FP32 |
| Python 3.10 | 3.10.20 | 2.7.0+cu128 / 0.22.0+cu128 | 0.20.2 / 4.40.2 | RTX 5090，CUDA 12.8；UNet/VAE FP16，adapter 与几何编码器 FP32 |

本次两组追踪都记录 driver `570.172.08`、`ReferenceOnlyAttnProc`、TF32 matmul 关闭、cuDNN TF32 开启、FP32 matmul precision `highest`、cuDNN benchmark 关闭；deterministic algorithms 未启用。历史 archive 日志记录 Python 3.13.5、torch 2.7.1、Diffusers 0.37.0 等版本和 RTX 5090，但没有记录历史 driver，因此不把历史 driver 视为已核实。完整 precision、后端标志、runner 和 trace script SHA 均见 `P0_RUNTIME_ENVIRONMENTS.csv`。

## 首个差异及传播

| 比较点 | Python 3.13 repeat 1 vs 2 | Python 3.13 vs 3.10 |
|---|---|---|
| batch 条件、初始 latent、几何 encoder 特征、VAE 条件 latent、prompt embedding | 全部逐元素相同 | 全部逐元素相同 |
| scheduler 有效 sigma 数值 | 重复运行相同 | 数值相同；序列化默认字段和 timestep dtype 不同（float32 / float64） |
| `init_noise_sigma` | 相同 | 均为 25.146116256713867 |
| 首个数值差异 | 无；所有捕获张量相同 | `scheduler_input_latent_step00 = initial_latent × init_noise_sigma` |
| 首差异量 | — | max abs 0.0625；RMSE 0.00965683；改变元素占 0.323242 |
| 首次 UNet 输入 | — | max abs 0.00390625；RMSE 0.00056162；改变元素占 0.498698 |
| 第 0 步噪声预测 | — | max abs 0.00390625；RMSE 0.00058547；改变元素占 0.596029 |
| VAE 解码输入 | — | max abs 20.0625；RMSE 1.89082；改变元素占 0.996908 |
| 最终 RGB 张量 | — | max abs 0.851807；RMSE 0.079739；改变元素占 0.960134 |

这里的“首个差异”是按完整捕获顺序比较张量后的首个已观察变化，不代表已隔离到某个 PyTorch kernel。P3.13 repeat 1/2 的所有已捕获值和最终 RGB 均完全相同，证明当前 P3.13 栈内这三例可复现；它不证明所有机器、驱动或其他对象都完全确定。

## RGB 与评价指标差异

P0 输出表将每个输出分别与其同一生成实例的 archive、observer 身份比对。三例中 P3.13 输出 SHA 均等于历史 archive；P3.10 输出 SHA 均等于此前 observer 输出。跨版本像素差异如下：

| 样本 | archive ↔ P3.10 RGB MAE /255 | RMSE /255 | 改变像素占比 | 同一 P3.13 评价器的 CIEDE2000：archive → P3.10 |
|---|---:|---:|---:|---:|
| Fresh C 01 | 8.761 | 20.347 | 0.999835 | 23.659 → 13.523（−10.136） |
| Fresh C 03 | 13.174 | 28.037 | 0.999672 | 28.001 → 8.219（−19.782） |
| Fresh C 20 | 12.647 | 23.696 | 0.514674 | 20.627 → 10.682（−9.945） |

“较早 observer”图像和“历史 archive”图像不可混成同一条件结果。本表的旧/新图像质量差异使用 `P0_CANONICAL_EVALUATION_METRICS.csv`，由 Python 3.13.5 / torch 2.7.1 / Diffusers 0.37.0 对各自 RGB 重新评分。以 Fresh C 01 为例，同一评价器得 archive / P3.10 FG-PSNR 12.697 / 16.224 dB、FG-LPIPS 0.2264 / 0.1769、Edge-SSIM 0.6908 / 0.7170。指标变化很大，故不同运行栈之间的变化不能解释为模型方法的效果。

图像路径及 SHA-256 在 `P0_OUTPUT_DIFFERENCE_TABLE.csv` 与病例册 P0 页面中逐项给出。三对象已复制到 `evidence_rgb/reproducibility/`；复制前后 SHA 相同。Tensor 级原始追踪位于本地 `repro/python313_trace_repeat1/`、`python313_trace_repeat2/` 和 `python310_trace/`，逐张量差异汇总在 `P0_TENSOR_DIFFERENCE_TABLE.csv`。

## 结论与未关闭的技术细节

1. 120/120 的图像身份不一致不是相同计算过程的输出。三例中两组输出分别按软件栈精确归回 archive 与此前 observer；首个数值差异位于 FP16 latent scaling，而不是输入 hash。
2. 同栈重复追踪逐张量一致，三例 archive 身份在 P3.13 栈精确复现；另一组 P3.10 栈精确复现此前 observer 身份。
3. Python、torch、torchvision、Diffusers、Transformers 同时变更。虽然最早差异出现在 PyTorch 标量乘法边界，当前证据不能断言单一库或 kernel 是唯一底层原因。
4. 只对按规则预先锁定的三个代表对象做了完整 tensor trace，没有把 120 个对象全部重算。原始 2GB 级 tensor trace 不上传；摘要 CSV、trace 脚本、运行环境和所有病例图像留存并逐项校验。

该复现缺口按“输出族与首个差异点均有可重复证据”关闭；它不表示 Fresh C 的跨版本图像可以混合比较，也不表示已完成 120 对象的逐张量审计。

## 审计文件

- 对象与 trace 协议：`P0_REPRO_TRACE_LOCK.json`。
- 张量差异：`P0_TENSOR_DIFFERENCE_TABLE.csv`、`P0_FIRST_DIVERGENCE.csv`。
- 图像及旧指标身份：`P0_OUTPUT_DIFFERENCE_TABLE.csv`、`P0_CANONICAL_EVALUATION_METRICS.csv`。
- 环境和后端配置：`P0_RUNTIME_ENVIRONMENTS.csv`。
- 可复现程序：`scripts/trace_freshc_repro.py`、`scripts/compare_repro_traces.py`、`scripts/compute_canonical_repro_metrics.py`。
- 所有已提交图像、脚本和表格的 SHA-256 在 `SHA256SUMS.txt`；未上传的大型 tensor trace 也在该清单内单独标注。
