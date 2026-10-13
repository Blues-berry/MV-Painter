# Results and failures

## 总览

| 组件 | 结果 | 解释 |
|---|---|---|
| UV 跨视角 texel 方差 | 主 FG-LPIPS 对象内 rho +0.054，95% CI [−0.454,+0.557]；5/10 对象方向为正；pairwise accuracy 0.529 | 对 LPIPS 选 schedule 近似随机。它与 SSIM loss 有较强相关（rho +0.829），更像结构/分歧度量而非感知保真质量量。 |
| 已知来源图前景 RGB MAE | FG-LPIPS rho +0.486 [0.179,0.746]，8/10 为正，pairwise accuracy 0.700；腐蚀边界后接近相同 | 有限、可解释的对象级诊断/静态 profile 选择关系；还没有说明每个视角如何调整几何残差。 |
| UV + 来源 RGB MAE | LOO-UO 主端点 rho +0.232 [−0.211,0.636]，准确率 0.610，LPIPS regret 0.00459 | 联合没有改善；不支持把两信号简单组合。 |
| view-budget helper | 11 项合成测试通过 | 只通过了预算与 tile 张量映射。没有第一遍反馈特征、动作策略、扩散调用或质量评估。 |
| GPU/图像实验 | 未运行 | Phase A/B 方法门槛没有通过；本次无新生成、无 GPU 作业。 |

## 主要负结果

1. UV 方差最低选择器的平均 LPIPS regret 为 0.00543，明显大于来源 RGB MAE selector 的 0.00172，且 UV-only 的对象排序近随机。
2. UV 方差与 SSIM/接缝信号相关，却不能代表 LPIPS/颜色 fidelity。这与恒定错误颜色 UV 方差为 0 的合成反例一致。
3. 来源图 MAE 的 leave-one-object-out 预测仍只在相同七种静态控制之间排序。它不能从对象级 score 推导六个视角不同的尺度方向，也不能区分某个未见表面区域应该增加还是减少 geometry residual。
4. UV+参考联合特征表现比参考 RGB MAE 单特征差，说明多信号组合没有自然变成更好的控制器。
5. Round012 参考图 projection 结果显示 source-view improvement 可能伴随其他生成视角回退；参考图 MAE 不能单独当成未见视角质量替代指标。
6. 低层 tile 控制接口可以实现，但“能够改变每视角尺度”只是执行能力，不是控制依据或质量收益。

## 未执行项目和未覆盖风险

- 未人为置换相机顺序、注入无效可见区域或错误遮挡；本次只审计当前 handoff 的相机/掩码映射。
- 未单独合成 blur 纹理测试过平滑风险；恒定黑色仅展示高度一致可能完全错误。
- 未执行 Phase C，不存在 BAVGC 纹理图、训练/推理速度、显存、完整日志或源码运行 hash。
- 未获取 RomanTex/GeoDiffuser 可逐式核查的全文。故本次不能做排除式的新颖性断言。
- Phase A 的 10 对象是已暴露研究对象，不是新对象确认集；控制 profile 也是已知配置，可能有选择/测量噪声。
