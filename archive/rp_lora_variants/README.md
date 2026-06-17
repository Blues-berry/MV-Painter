# RP-LoRA Variants Archive

## 历史背景

这些文件是 **RP-LoRA (Reference-Preserving LoRA)** 研究的实验产物，用于验证"attn1 会破坏 reference attention"这一发现。

**注意：这些文件不代表当前项目重点。** 当前项目重点是 **GeoTex-Adapter**。

## 研究发现（已完成）

| 配置 | PSNR | 状态 |
|------|------|------|
| attn1+attn2 LoRA (rank 8) | 8.52 dB | ❌ 崩溃 |
| attn2-only LoRA (rank 4, 500 steps) | 32.33 dB | ✅ 成功 |

**核心结论**：MV-Painter 的 LoRA 微调必须只应用于 attn2 (cross-attention)，不能应用于 attn1 (self-attention)。

## 文件说明

### 基础文件
- `model_unet_lora.py` - 基础 LoRA UNet 模型（被变体依赖）
- `lora_utils.py` - 基础 LoRA 工具函数

### attn2-only（研究结论推荐）
- `model_unet_lora_attn2.py` - attn2-only LoRA 模型
- `lora_utils_attn2.py` - attn2-only LoRA 工具函数

### 消融实验变体
- `model_unet_lora_attn1.py` - attn1-only LoRA 模型
- `lora_utils_attn1.py` - attn1-only LoRA 工具函数
- `model_unet_lora_ffn.py` - FFN-only LoRA 模型
- `model_unet_lora_full.py` - Full LoRA 模型（对比基线）

### 对比实验脚本
- `run_comparison.py` - zero-shot vs LoRA 对比
- `run_fixed_comparison.py` - 修复版对比脚本
- `quick_scale_test.py` - scale 参数快速测试
- `infer_multiview.py` - 多视图推理脚本
- `run_inference_comparison.py` - 推理对比脚本

## 当前项目重点

**GeoTex-Adapter**：基于几何感知的纹理适配器，用于多视图扩散模型。
- 模型文件：`MVPainter/mvpainter/model_unet_geotex.py`
- 训练脚本：`geotex_scripts/`
- 配置文件：`MVPainter/configs/mvpainter-geotex-*.yaml`

## 相关论文

RP-LoRA 研究已形成论文草稿，见：
- `mvpoutput/paper_draft/` - 论文各章节
- `mvpoutput/paper_assets/` - 图表和评估数据

---

**归档日期**：2026-06-17
**归档原因**：避免外部智能体误判项目重点为 attn2-only LoRA
