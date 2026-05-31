# MV-Painter 项目结构

**最后更新**: 2026-05-31

---

## 顶层目录

```
/4T/CXY/MV-Painter/
├── MVPainter/          # MV-Painter 核心代码（含 LoRA）
├── PBR/                # PBR 训练（独立）
├── mvpoutput/          # LoRA/MVPainter 所有输出产物
├── mvp-lora-script/    # LoRA 调试和实验脚本
├── checkpoints/        # 模型权重
├── data/               # 训练数据
├── data_process/       # 数据处理脚本
├── assets/             # 静态资源
├── blender-4.2.4-linux-x64/  # Blender
├── .claude/            # Claude 配置
└── .git/               # Git 仓库
```

---

## 1. MVPainter/ — 核心代码

### 1.1 模型代码

| 文件 | 说明 |
|------|------|
| `mvpainter/mvpainter_pipeline.py` | 主 pipeline（含 ReferenceOnlyAttnProc） |
| `mvpainter/model_unet.py` | 原始 UNet 训练模型 |
| `mvpainter/model_unet_lora.py` | LoRA 模型（attn1+attn2，有 bug） |
| `mvpainter/model_unet_lora_attn2.py` | **attn2-only LoRA 模型（修复版）** |
| `mvpainter/lora_utils.py` | 原始 LoRA 工具（有 bug） |
| `mvpainter/lora_utils_attn2.py` | **attn2-only LoRA 工具（修复版）** |
| `mvpainter/controlnet.py` | ControlNet 实现 |

### 1.2 训练配置

| 文件 | 说明 |
|------|------|
| `configs/mvpainter-lora-attn2-only-r4-lr1e5.yaml` | rank=4, 100 steps |
| `configs/mvpainter-lora-attn2-only-r4-lr1e5-250.yaml` | rank=4, 250 steps |
| `configs/mvpainter-lora-attn2-only-r4-lr1e5-500.yaml` | rank=4, 500 steps |
| `configs/mvpainter-lora-attn2-only-r8-lr1e5-250.yaml` | rank=8, 250 steps |
| `configs/mvpainter-lora-broken-r4-lr1e4-100.yaml` | broken (attn1+attn2) 对比用 |

### 1.3 训练日志和 Checkpoints

```
MVPainter/logs/
├── mvpainter-lora-attn2-only-r4-lr1e5-*/lora_checkpoints/
│   └── lora_step_0000100.safetensors
├── mvpainter-lora-attn2-only-r4-lr1e5-250-*/lora_checkpoints/
│   └── lora_step_0000250.safetensors
├── mvpainter-lora-attn2-only-r4-lr1e5-500-*/lora_checkpoints/
│   ├── lora_step_0000250.safetensors
│   └── lora_step_0000500.safetensors
├── mvpainter-lora-attn2-only-r8-lr1e5-250-*/lora_checkpoints/
│   └── lora_step_0000250.safetensors
└── mvpainter-lora-broken-r4-lr1e4-100-*/lora_checkpoints/
    └── lora_step_0000100.safetensors
```

### 1.4 其他文件

| 文件 | 说明 |
|------|------|
| `train.py` | 训练入口 |
| `train_pbr.py` | PBR 训练入口 |
| `infer_multiview.py` | 多视图推理 |
| `infer_pbr.py` | PBR 推理 |
| `src/data/mvpainter_dataset.py` | 数据集代码 |
| `datalist/test_objects.txt` | 测试集（10个对象） |
| `datalist/train_objects.txt` | 训练集（53个对象） |

---

## 2. mvpoutput/ — LoRA 输出产物

### 2.1 论文产物（paper_assets/）

| 文件 | 说明 |
|------|------|
| `paper_main_figure.png` | 主图（三路对比） |
| `steps_comparison.png` | 训练步数对比图 |
| `eval_vs_gt_table.md` | GT 评估表 |
| `checkpoint_inventory.txt` | Checkpoint 清单 |
| `FINAL_REPORT.md` | 最终报告 |
| `README.md` | 使用说明 |

### 2.2 实验结果

| 目录 | 说明 |
|------|------|
| `three_way_comparison/` | 三路对比图（5个样本） |
| `attn2_lora_test/` | attn2-only 推理测试 |
| `zeroshot_audit/` | Zero-shot 审计（20个样本） |
| `scale_sweep/` | Scale sweep 结果 |
| `eval_vs_gt/` | GT 评估结果 |
| `experiment_results/` | 实验报告汇总 |

### 2.3 诊断报告

| 文件 | 说明 |
|------|------|
| `COMPREHENSIVE_REPORT.md` | 综合报告 |
| `VERIFICATION_REPORT.md` | 验证报告 |
| `research_decision_report.md` | 决策报告 |
| `lora_layer_report/` | LoRA 层分析 |
| `lora_weight_health_report/` | 权重健康检查 |
| `lora_loading_sanity_check/` | Loading sanity check |
| `pipeline_consistency_report/` | Pipeline 一致性检查 |

### 2.4 日志

| 文件 | 说明 |
|------|------|
| `logs/lora-attn2-only-*.log` | 训练日志 |
| `logs/lora-broken-*.log` | Broken LoRA 训练日志 |
| `logs/three_way_comparison.log` | 三路对比日志 |
| `logs/eval_vs_gt.log` | GT 评估日志 |
| `logs/steps_comparison.log` | 步数对比日志 |

---

## 3. mvp-lora-script/ — 调试脚本

| 脚本 | 用途 |
|------|------|
| `zeroshot_audit.py` | Phase 1: Zero-shot 审计 |
| `pipeline_consistency_check.py` | Phase 2: Pipeline 一致性 |
| `lora_layer_analysis.py` | Phase 3: LoRA 层分析 |
| `lora_weight_health_check.py` | Phase 4: 权重健康检查 |
| `lora_loading_sanity_check.py` | Phase 5: Loading sanity |
| `scale_sweep.py` | Scale sweep 测试 |
| `three_way_comparison.py` | 三路对比（论文用） |
| `eval_vs_gt.py` | GT 评估（论文用） |
| `steps_comparison.py` | 步数对比（论文用） |
| `test_attn2_lora_inference.py` | attn2-only 推理测试 |
| `test_trained_lora.py` | 训练后 LoRA 测试 |
| `debug_merge_identity.py` | Merge identity 调试 |
| `test_merge_identity_pipeline.py` | Pipeline 级别 merge 测试 |

---

## 4. PBR/ — PBR 训练（独立）

| 内容 | 说明 |
|------|------|
| `COMPREHENSIVE_REPORT.md` | PBR 综合报告 |
| `checkpoints/` | PBR checkpoints |
| `configs/` | PBR 配置 |
| `data/` | PBR 数据 |
| `datalist/` | PBR 数据列表 |
| `docs/` | PBR 文档 |
| `logs/` | PBR 训练日志 |
| `loss_curves_*.png` | Loss 曲线图 |
| `metrics_comparison.png` | 指标对比图 |

---

## 5. 关键路径速查

### 5.1 训练

```bash
# attn2-only LoRA 训练
cd /4T/CXY/MV-Painter/MVPainter
source activate mvpainter
CUDA_VISIBLE_DEVICES=0 python train.py \
    -b configs/mvpainter-lora-attn2-only-r4-lr1e5-250.yaml \
    -n lora-attn2-only-r4-lr1e5-250 \
    --gpus 0,
```

### 5.2 推理

```python
# attn2-only LoRA 推理
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only
merge_lora_into_unet_attn2_only(pipeline.unet, lora_path, rank=4, alpha=1)
```

### 5.3 论文产物

```
/4T/CXY/MV-Painter/mvpoutput/paper_assets/
```

---

## 6. 核心发现

**LoRA 灾难性退化的根因**: LoRA 应用到 attn1 破坏 reference attention 机制。

**解决方案**: 只对 attn2 应用 LoRA，保留 attn1 不变。

| 配置 | PSNR vs Original |
|------|------------------|
| attn1+attn2 LoRA | 19-36 dB ❌ |
| attn2-only LoRA | 43-59 dB ✅ |
