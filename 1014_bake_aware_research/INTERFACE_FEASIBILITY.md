# Phase B: interface feasibility

## 现有接口

- `MVPainter/mvpainter/model_unet_geotex.py` 的 `GeoTexResnetWrapper` 在各 Adapter 层计算 geometry correction，并应用 `_adapter_scale` 这一全局/按阶段的静态标量以及 native per-layer cap。原接口没有相机 ID、UV 坐标、可见性权重或来源视角身份，Adapter 内部也没有足够信息安全推断表面对应关系。
- `prepare_batch_data` 把六个视角用 `rearrange(..., x=3, y=2)` 拼成 3×2 feature mosaic；图像、法线、深度和 mask 采用相同拼法。已知拼接顺序可作为张量映射，但必须与 `target_view_mapping` 对齐。
- pipeline 有 reference-write 和 target-read 两个 UNet pass；reference-write pass 会禁用 adapter correction，target-read pass 才应用 geometry correction。没有确认一个可在单次 sampler 运行中途安全暂停、写 UV bake、再恢复的缓存边界。因此标准的第一次生成—反馈—重新生成候选会增加一轮完整生成成本；本次没有实际测量额外延迟或显存。

## 独立实验切片

在 `/4T/tmp/MV-Painter-bavgc-phase-b` 的隔离分支 `codex/bavgc-phase-b-20261013` 中，尝试了最低复杂度张量接口：

- `view_budget.py` 将六视角请求偏移投影回 native cap、每视角最大偏移和保持六视角总尺度和的可行域；无效反馈恢复统一基础尺度。
- wrapper 可将绝对尺度按 3×2 tile 应用到 correction，并记录每个 tile 的实际残差幅度。
- 接口不改变 adapter 参数，也不触碰主工作树代码；代码未提交、未合并。

## 合成接口测试

`tests/test_bavgc_view_budget.py` **11/11 通过**，覆盖：零尺度恒等、无反馈回基础值、预算守恒、native cap 饱和、视角置换等变、tile 顺序与错误分辨率 fail closed、FP16/FP32、realized residual 统计、native scalar 与统一六视角 scale 等价，以及真实 wrapper 的默认与错误映射路径。

通过这些测试只说明张量接口按设计映射，不代表已证明：

1. UV feedback 能唯一映射到正确视角；
2. 扰动尺度与目标烘焙质量的变化方向已知；
3. 两次扩散比等计算量无反馈策略更好；
4. 端到端 runtime、显存、真实 checkpoint 行为或图像输出正确。

当前 Phase A 未选出有效 UV 主信号，所以没有实现或测试一个从反馈张量到六视角请求偏移的策略。把任意手工方向塞进这个接口会把未验证假设伪装成方法，故在这里停止。

## 可行性判断

**低层接口：通过合成测试。科学/算法接口：未通过。** Phase B 的主要门槛不是能否缩放六个 tile，而是能否从合法反馈产生可解释、可复现并能改善真实 bake 的控制动作。本次没有这样的动作，也没有理由启动 GPU。
