# 代码修改总结

## 1. 核心修改

### 1.1 MV Consistency Loss (`train_pbr.py`)
**位置**: 训练循环中的 loss 计算部分

**修改内容**:
```python
# 新增：多视图一致性 loss
mv_consistency_loss = torch.tensor(0.0, device=model_pred.device)
if mode == 'multi' and cfg.mv_consistency_weight > 0 and Nv > 1:
    pred_reshaped = model_pred.view(B, Nv, Nd, *model_pred.shape[1:])
    view_diff = pred_reshaped[:, 0] - pred_reshaped[:, 1]
    mv_consistency_loss = (view_diff ** 2).mean()

# 修改：加入主 loss
if cfg.mv_consistency_weight > 0:
    loss = loss + cfg.mv_consistency_weight * mv_consistency_loss
```

**配置参数**:
```yaml
mv_consistency_weight: 0.1  # 在 config 中添加
```

### 1.2 PBR 数据集支持 (`pbr/data/mv_dataset_arbobjaverse.py`)

**新增数据类型**: `mvpainter`

**新增函数**:
- `get_mv_info()` 中添加 `mvpainter` 分支
- `load_normal_mvpainter()` - 加载 uint16 法线图
- `load_mr_mvpainter()` - 加载 metallic + roughness
- `load_c2w_mvpainter()` - 加载 .npy 相机参数
- `__fetch_data()` 中添加 `mvpainter` 分支

### 1.3 diffusers 兼容性 (`attention_processor.py`)

**修改**: 给 `AttnProcessor.__call__` 和 `AttnProcessor2_0.__call__` 添加 `**kwargs`

```python
def __call__(self, attn, hidden_states, ..., **kwargs):  # 添加 **kwargs
```

**原因**: IDArb 模型传递 `num_d` 参数，diffusers 0.20.2 不支持

### 1.4 相对导入修复 (`pbr/utils/metrics.py`)

```python
# 修改前
from utils.misc import rgb_to_srgb as _tonemap_srgb
# 修改后
from pbr.utils.misc import rgb_to_srgb as _tonemap_srgb
```

---

## 2. 新增文件

### 2.1 推理脚本 (`inference_pbr.py`)
- 加载训练好的 checkpoint
- 运行 PBR 推理
- 保存预测结果和 GT 对比

### 2.2 预计算脚本 (`precompute_embeddings.py`)
- 预计算 vision encoder embedding
- 避免训练时加载大型 vision encoder
- 节省 ~4 GB VRAM

### 2.3 配置文件
- `configs/mvpainter-pbr-baseline-*.yaml` - Baseline 配置
- `configs/mvpainter-pbr-ours-*.yaml` - Ours 配置
- `configs/acc/1gpu_pbr.yaml` - 单 GPU accelerate 配置

---

## 3. 训练脚本修改

### 3.1 `train.py` (MVPainter 多视图训练)
- 修改 precision: `32-true` → `16-mixed`
- 修改 strategy: `DDPStrategy` → `DeepSpeedStrategy`
- 修改 `mvpainter/model_unet.py`:
  - 添加梯度检查点
  - 添加 8-bit Adam 优化器
  - 添加预计算 embedding 支持

### 3.2 `train_pbr.py` (PBR 训练)
- 添加 MV Consistency Loss
- 添加 loss 日志记录
- 配置参数 `mv_consistency_weight`

---

## 4. 数据处理脚本修改

### 4.1 `data_process/blender_script.py`
- 修复 `merge_vertices=True` 参数问题
- 修复 `elif` 缩进错误
- 处理 `_clean.obj` 不存在的情况

### 4.2 `data_process/run_blender.py`
- 添加 `.hdr` 文件支持

### 4.3 `data_process/depth_exr_to_png.py`
- 修改深度通道从 'R' 到 'V'

---

## 5. 环境修复

### 5.1 Blender GLTF Bug
- 文件: `blender-4.2.4-linux-x64/4.2/scripts/addons_core/io_scene_gltf2/__init__.py`
- 修复 `set_debug_log()` 返回 None 的问题

### 5.2 自定义扩展
- `custom_rasterizer` - 需要设置 `LD_LIBRARY_PATH`
- `mesh_processor` - 正常工作

---

## 6. 关键配置参数

### 6.1 PBR 训练配置
```yaml
# 核心参数
train_batch_size: 1
gradient_accumulation_steps: 1  # 减少内存
gradient_checkpointing: true
mixed_precision: "fp16"
use_ema: false  # 节省显存
mv_consistency_weight: 0.1  # Ours 使用
mv_consistency_weight: 0.0  # Baseline 使用

# 数据参数
img_wh: [256, 256]  # 降低分辨率
num_views: 2  # 减少视图数
dataloader_num_workers: 0  # 减少内存
```

### 6.2 训练命令
```bash
# 设置环境
export CUDA_VISIBLE_DEVICES=1
export LD_LIBRARY_PATH=/home/ubuntu/ssd_work/conda_envs/mvpainter/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH

# 训练
accelerate launch --num_processes=1 --mixed_precision fp16 train_pbr.py \
  --config configs/mvpainter-pbr-ours-73.yaml
```
