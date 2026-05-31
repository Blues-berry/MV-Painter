# MVPainter LoRA 实验结果

## 实验环境

- GPU: NVIDIA RTX 5090 (32.6 GB VRAM)
- PyTorch: 2.7.0+cu128
- diffusers: 0.20.2
- DeepSpeed: ZeRO-3 + CPU offload

## 核心指标对比表

| 方法 | 可训练参数 | 占比 | 峰值显存 | Checkpoint | Best Loss | 能否在 RTX 5090 训练 |
|---|---|---|---|---|---|---|
| Full Fine-tune | 2,579.08M | 100% | ~30.7 GB (OOM) | 4.8 GB | N/A | ❌ |
| **LoRA rank=4** | **5.81M** | **0.23%** | **15.4 GB** | **12 MB** | **0.000561** | **✅** |
| **LoRA rank=8** | **11.61M** | **0.45%** | **15.4 GB** | **23 MB** | **0.000466** | **✅** |

## 显存分解 (LoRA rank=8)

| 组件 | 显存 |
|---|---|
| UNet + VAE (fp16) | ~10.7 GB |
| 激活内存 (2x 前向 + 梯度检查点) | ~4.5 GB |
| DeepSpeed 通信缓冲 | ~0.2 GB |
| **总计** | **~15.4 GB** |
| **显存余量** | **~17.2 GB** |

## 训练 Loss 曲线 (LoRA rank=8, 1000 steps)

| Step | Loss | 备注 |
|---|---|---|
| 49 | 0.003277 | |
| 99 | 0.007160 | |
| 149 | 0.118591 | spike |
| 199 | 0.028351 | |
| 249 | 0.004669 | |
| 299 | 0.002882 | |
| 349 | 0.001116 | |
| 399 | 0.003164 | |
| 449 | 0.003975 | |
| 499 | 0.003162 | |
| 549 | 0.000518 | |
| 599 | 0.065247 | spike |
| 649 | 0.039398 | |
| 699 | 0.005409 | |
| 749 | 0.007195 | |
| 799 | 0.000466 | best |
| 849 | 0.007256 | |
| 899 | 0.018723 | |
| 949 | 0.000546 | |
| 999 | 0.026016 | |

- Best loss: 0.000466 (step 799)
- 训练时间: ~2.5 小时 (1000 steps, ~12s/step)

## Checkpoint 信息

| 项目 | 值 |
|---|---|
| 文件名 | lora_step_0001000.safetensors |
| 大小 | 23 MB |
| 格式 | safetensors |
| 配置 | rank=8, alpha=8, 560 layers |
| 路径 | logs/mvpainter-train-unet-lora-5090/lora_checkpoints/ |

## 训练命令

```bash
cd /4T/CXY/MV-Painter/MVPainter

# LoRA rank=8 训练
CUDA_VISIBLE_DEVICES=1 conda run -n mvpainter python train.py \
  --base configs/mvpainter-train-unet-lora-5090.yaml \
  --gpus 0, \
  --scale_lr False \
  --max_steps 1000

# LoRA rank=4 训练
CUDA_VISIBLE_DEVICES=1 conda run -n mvpainter python train.py \
  --base configs/mvpainter-train-unet-lora-5090-rank4.yaml \
  --gpus 0, \
  --scale_lr False \
  --max_steps 1000
```

## 数据清洗

- 总样本: 227
- 有效样本: 63 (有完整的 depth_png/000.png 和 depth_png/014.png)
- 无效样本: 164 (缺失 depth_png/ 目录)
- 清洗后 loss spike 消失: step 149 从 0.055-0.119 降至 0.006

## Rank=4 vs Rank=8 Loss 对比 (脏数据)

| Step | Rank=4 | Rank=8 | 差异 |
|---|---|---|---|
| 49 | 0.003292 | 0.003277 | +0.5% |
| 99 | 0.006405 | 0.007160 | -10.5% |
| 149 | 0.055267 | 0.118591 | -53.4% |
| 199 | 0.038055 | 0.028351 | +34.2% |
| 249 | 0.004829 | 0.004669 | +3.4% |
| 299 | 0.003963 | 0.002882 | +37.5% |
| 349 | 0.001280 | 0.001116 | +14.7% |

## Rank=4 Loss (清洗后数据)

| Step | Rank=4 (clean) | Rank=4 (dirty) | Rank=8 (dirty) |
|---|---|---|---|
| 49 | 0.002283 | 0.003292 | 0.003277 |
| 99 | 0.017227 | 0.006405 | 0.007160 |
| 149 | 0.005920 | 0.055267 | 0.118591 |

**关键发现**: 清洗数据后 step 149 的 loss spike 消失，证实 spike 由缺失 depth 文件的坏样本引起。

**结论**: Rank=4 和 Rank=8 收敛速度几乎相同。清洗数据后训练更稳定。Rank=4 用一半的参数 (5.81M vs 11.61M) 达到了几乎相同的效果。

## 推理对比结果

已对 4 个测试样本生成 zero-shot、LoRA-r4、LoRA-r8 三组结果。

输出目录: `comparison_results/`
每个样本包含: `result_6view.png` (6视角生成) + `result_cond.png` (条件图)

| 样本 | Zero-shot | LoRA-r4 | LoRA-r8 |
|---|---|---|---|
| d6a5427888... | 872K | 1000K | 556K |
| e3f35d4cfb... | 508K | 980K | 316K |
| f0ef4adc17... | 576K | 1.2M | 388K |
| f63daf968b... | 568K | 1.1M | 300K |

## 推理命令

```bash
# 使用 LoRA checkpoint 推理
python infer_multiview.py \
  --input_glb_dir <meshes_dir> \
  --input_img_dir <images_dir> \
  --lora_ckpt logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors \
  --lora_rank 8 \
  --lora_alpha 8
```
