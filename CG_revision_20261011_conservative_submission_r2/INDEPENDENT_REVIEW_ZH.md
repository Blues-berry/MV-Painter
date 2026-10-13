# 保守提交版 r1 独立复核

本复核对应 `conservative_submission_r1` 源文件；较早审查文本保存在 `INDEPENDENT_REVIEW_pre_r1_ZH.md`，其中的“待修”状态不代表 r1 当前状态。

## 本轮修正和复核

- 主文按问题、TCAS、量化/偏好结果、下游烘焙和第二接口结果组织，减少重复的档案核验叙述。结论仍与比较对象和端点一一对应。
- 历史 +0.96 dB 在主文保留一处，并说明原 checkpoint、C3 对 Fixed High、原 300 对象 pooled full-image PSNR、开发对象重叠以及缺失配对行。Fresh C 的 +0.522 dB 是另一 checkpoint/UID 队列/foreground FG-PSNR 下的 C3–GFL 对照，不称为复现。
- Fresh C 展示指标是在每对象 3×2 六视角拼图上计算。Figure 8 的两个案例通过五个预先授权的既有候选筛选，均在完整拼图和 view 0 上对 Fixed Low 同向改善 FG-PSNR、FG-LPIPS 和 FG-SSIM；共同 ROI 相同。目标渲染本身是低变化图像，因此图注明确它只对应图像指标方向，不代表纹理保真。逐对象范围及 PNG 量化复算已分开留档，主统计未替换。
- Figure 5 展示 300 个对象差值和具名比较；Figure 6 的定性固定/线性对照、Figure 7 的颜色诊断、Figure 8 的指标正例、Figure 9 的烘焙、Figure 10 的 MV-Adapter 图序与正文源码顺序一致。Supplement、署名表和回复位置同步修正。
- 配对效应、图像素材、图源哈希及授权来源保持可追溯。matched-budget 表中的 1,800 个 seed 从已有 UID lookup 补齐并验证各对象六个条件共用同一个 seed；所有指标值保持不变。
- 300 对象 Fresh C、十对象烘焙、50 对象 MV-Adapter 的数值仍按各自队列和预先/事后状态分开。MV-Adapter 主比较的区间包括零；烘焙正向结论限于未见视角 FG-LPIPS。

## 仍未解决的科学边界

R1.1 仍部分回应：缺 GeoTex unset-scale 原生默认输出、经验证的 seam 指标和 PBR/重光照结果。烘焙集合受材质/UV/相机兼容性筛选，图像中可见生成外观与来源仍有差异。R1.2 不能由 Fresh C 证明原 checkpoint 的 +0.96 dB；R1.5 仍缺 FAC 的 run-bound 训练清单和权重。R2.1 是最大风险：TCAS 的调度形式已有先例，当前贡献需由任务内的控制定义、受控比较、偏好和应用验证支撑。R2.3 新增 native N=50，有效缩小第二接口检验缺口，但主要比较未分离，不能据此宣称架构普遍迁移。

图像展示说明具名案例，不能替代完整队列；本轮未新增推理来修复质量表现，也未从指标中剔除不利样本。
