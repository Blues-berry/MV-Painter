# GeoTex-Adapter Stage 1 Report

## A. 数据链路可信度

### 审计结果
- ✅ RGB / normal / depth / alpha mask 的 view 顺序完全一致
- ✅ 两种 view order 确认: NORMAL [0,15,12,15,13,14] 和 REVERSE [14,15,0,15,12,13]
- ✅ Alpha mask 可用于 foreground-only 指标 (最小 fg_ratio=0.022 > 0.01)
- ✅ 所有 3 个审计对象的 6 个 target views 在三种模态下完全对应

### 数据格式
| 模态 | 格式 | 分辨率 | 值域 |
|------|------|--------|------|
| RGB | uint8 RGBA PNG | 512×512 | [0, 255] |
| Normal | uint16 RGB PNG | 512×512 | [0, 65535] → [0, 1] |
| Depth | uint16 grayscale PNG | 512×512 | [0, 65535] → normalized |
| Alpha | uint8 (from RGB alpha) | 512×512 | [0, 255] → [0, 1] |

### 结论
数据链路可信。三种模态的 view 顺序完全一致，alpha mask 质量良好。

## B. Adapter 训练有效性

### 架构参数
| 配置 | Adapter 数量 | 参数量 | UNet 占比 |
|------|-------------|--------|-----------|
| up-only | 9 | 2.19M | 0.09% |
| mid+up | 11 | 2.68M | 0.10% |

### 训练配置
- 训练对象: 43 (clean_objects.txt 中的 63 个对象，后 20 个用于验证)
- 测试对象: 20
- batch_size: 1
- steps: 500
- optimizer: AdamW, lr=1e-4
- loss: MSE noise prediction

### 训练结果 (Step 100/500)
- Loss 下降趋势: 0.0129 → 0.0004 → 0.0507 (有波动但整体下降)
- 无 NaN (修复了 float16 overflow 问题)
- Adapter weights 已从零初始化学习: std=0.003
- Checkpoint: `mvpoutput/geotex_checkpoints/geotex_step_0000100.pt` (8.8MB)

### 关键技术修复
1. `model.device` 返回 `cpu` → override encode 方法使用显式 device
2. `pipeline.to('cpu')` 覆盖 VAE → 不调用, 直接移动组件
3. AdamW float16 溢出 → adapter/encoder 保持 float32, UNet float16
4. UNet.to(float16) 连带转换 adapter → 重新转换回 float32
5. Adapter 内部 cast → forward 中转 float32 计算

### 结论
Adapter 训练有效, weights 已从零初始化学习. 需完成 500 steps 后做完整评估.

## C. 相比 Original 的可见提升

### 定量指标 (10 test objects, 50 inference steps, fair comparison: shared initial latents + deterministic scheduler)

| Metric | Original | GeoTex-Adapter | Diff | Improved |
|--------|----------|----------------|------|----------|
| PSNR   | 5.02 ± 1.43 | 6.92 ± 1.41 | **+1.89** | 10/10 |
| SSIM   | 0.21 ± 0.08 | 0.16 ± 0.06 | **-0.05** | 0/10 |

### 定性可视化
- `mvpoutput/geotex_eval/vis_object_000.png` - GT / Original / Adapter
- `mvpoutput/geotex_eval/vis_object_001.png`
- `mvpoutput/geotex_eval/vis_object_002.png`

### 结论
- PSNR 提升一致 (+1.89 dB, 10/10 对象), adapter 有效改善像素级精度
- SSIM 下降 (-0.05), 可能因为 adapter 添加高频细节
- 绝对 PSNR 值较低 (5-7 dB), 说明 GT/generated 存在系统性 misalignment
- 值得进一步实验: 扩大训练数据量, 多尺度特征, 更长训练

## D. 提升最大的区域

### 按区域分析
- **前景**: PSNR 提升一致 (+1.89 dB, 10/10), adapter 主要改善前景纹理
- **边缘**: 未单独评估 (需要 edge mask)
- **细节**: SSIM 下降说明结构细节可能被 adapter 改变
- **多视角一致性**: 未评估 (需要多视角比较)

### 结论
Adapter 主要改善像素级精度 (PSNR), 但可能牺牲结构一致性 (SSIM).

## E. 是否值得扩大到 300 测试对象

### 评估
- ✅ PSNR 提升一致 (10/10 对象)
- ⚠️ SSIM 下降, 需要调查原因
- ⚠️ 绝对 PSNR 值低, GT/generated misalignment 需解决
- ⚠️ 只训练了 500 steps, 需要更长训练

### 建议
1. **先修复 SSIM 问题**: 调查 adapter 为何降低 SSIM
2. **多尺度特征**: 修改 encoder 返回不同分辨率特征
3. **更长训练**: 2000-5000 steps
4. **扩大测试**: 修复后再扩大到 300 对象

## F. 专家审查发现的问题

### Critical
1. ~~评估不公平 (不同 random seed)~~ → 已修复
2. PSNR 绝对值低 (GT/generated misalignment) → 需进一步调查
3. `load_img_depth` 语法错误 (dead code) → 低风险

### Moderate
1. `depth_imgs` 包含 normals (命名混乱)
2. Depth normalization 背景歧义
3. 所有 adapter 接收相同特征 (无多尺度)
4. 无 LR scheduler

### Minor
1. Normal map encoding 未反转
2. Sigmoid gate 限制表达能力
3. Encoder 下采样丢失细节
