# Phase A: feedback signal audit

## 数据和验证边界

- 冻结来源：`final_paper_20261012/source/data/gap_closure015/BAKE_INPUT_HANDOFF_V3.json` 和 `source/data/primary_studies/BAKE10_OBJECT_METRICS.csv`。
- 单位：10 个此前已暴露对象；每对象 7 个冻结控制；每个 object×control 使用一条归档 bake realization。所有控制的图像行先在对象内比较，再以对象做 bootstrap 单位（50,000 次，seed 20261013）。
- 可用推理信号：①已有跨视角 UV texel 方差；②本次新增的已知来源参考视角前景 RGB MAE。对第②项同时用原前景掩码和 2 px 腐蚀掩码计算。
- 目标 GT 只用于离线评估已有的 FG-LPIPS、PSNR、SSIM、CIEDE2000 和 bake 质量。控制信号没有读取未见评价相机或完整目标纹理。
- 来源相机验证：生成 tile 0 与 handoff 中 `target_view_mapping[0]` 一一对应；原相机索引仅为 0 或 14；未旋转；参考 RGBA 和前景 mask 来自 handoff 同一相机。原图为 512×512，tile 为 256×256；RGB 采用 bicubic 缩放、mask 采用 nearest。相机/slot 校验不等于故障注入实验。
- 同一对象七种条件的 UV coverage 相同；对象间 coverage 约 0.0587–0.3247。因而对象内 schedule 排序不由条件间覆盖率变化驱动。

## 对象内预测结果

信号方向已统一为“值越大表示越差”，质量端点也转换为 loss 方向。`rho` 是每对象七个条件之间的 Spearman 相关；95% 区间是对 10 个对象重采样所得，不能按七个配置或 110 个视角计算独立样本量。

| 无 GT 信号 | 烘焙端点 | 平均对象内 Spearman（95% 对象 bootstrap CI） | 对象方向 | pairwise 排序准确率 | 最低信号选择的平均 LPIPS regret |
|---|---|---:|---:|---:|---:|
| UV 跨视角 texel 方差 | FG-LPIPS loss | +0.054 [−0.454, +0.557] | 5/10 正 | 0.529 | 0.00543 |
| 来源前景 RGB MAE | FG-LPIPS loss | +0.486 [+0.179, +0.746] | 8/10 正 | 0.700 | 0.00172 |
| 腐蚀 2 px 来源前景 RGB MAE | FG-LPIPS loss | +0.489 [+0.179, +0.750] | 8/10 正 | 0.705 | 0.00140 |
| UV 方差 | SSIM loss | +0.829 [+0.607, +0.982] | 10/10 正 | 0.895 | — |
| 来源前景 RGB MAE | PSNR loss | +0.796 [+0.650, +0.914] | 10/10 正 | 0.852 | — |
| 来源前景 RGB MAE | CIEDE2000 | +0.718 [+0.496, +0.904] | 10/10 正 | 0.819 | — |

UV 方差和结构损失/接缝差异相关，但不能据此选择较好的感知纹理：最低 UV 方差规则平均选择 `native_gfh`，在主 FG-LPIPS 上接近随机，平均 regret 0.00543。来源图 MAE 对静态 profile 的对象内 LPIPS 排序有较稳定的有限预测关系，且腐蚀掩码后数值近似不变；这说明该关系不只来自边界像素，但不说明它能导出正确的六视角控制动作。

## 留一对象外推检查

为每次完全留出一个对象，以另外 9 个对象拟合固定的线性排序器，再在留出对象的同七种静态 profile 中排序。结果：

| 特征 | 预测留出对象 FG-LPIPS 的平均 rho（95% CI） | 排序准确率 | 平均选择 regret |
|---|---:|---:|---:|
| 来源 RGB MAE | +0.486 [+0.175, +0.746] | 0.700 | 0.00172 |
| UV 方差 | +0.054 [−0.461, +0.550] | 0.529 | 0.00543 |
| 两者联合 | +0.232 [−0.211, +0.636] | 0.610 | 0.00459 |

这是按对象留出的探索性检查，但对象仍来自同一个已暴露 cohort，控制身份仍是相同的七个已知 profile。它评估“选哪一个静态 profile”，不是新方法泛化或每视角反馈因果验证；联合特征还比来源 MAE 单特征差。

## 反例清单

| 反例/风险 | 本次实际证据 | 判断与缺口 |
|---|---|---|
| 恒定颜色但外观错误 | Round015 `CROSS_VIEW_VALIDATION.json` 中 `constant_black_all_views` 的 UV 方差为 0；不同相机灰色方差约 0.125–0.127。含 80 replay rows 和四个已知颜色控制 | 已直接验证“一致性不代表保真度”。这是实现/合成控制，不是 PBR 完整质量测试。 |
| 过度平滑但高度一致 | 没有单独构造 blur/过平滑生成物；恒定黑色是极端一致性反例 | 不能声称平滑反例已单独通过。需要保留纹理频率/细节指标，单一分歧指标不够。 |
| 错误相机顺序 | Phase A 对全部 handoff 行做 slot/raw-camera/ref/mask 一致性校验；没有人为打乱 camera index 后运行烘焙 | 只验证当前数据映射正确，不是错误顺序的反例注入。映射不确定时应 fail closed。 |
| UV 岛边界、重复 UV、aliasing | 既有两对象 audit 显示标注 footprint 覆盖了被检查的 100% 高误差像素；256/512/1024 误差有变化 | 说明边界/分辨率敏感；样本很小，不能推成通用纠错器，也未测任意拓扑。 |
| 无效可见区域/遮挡错判 | 本次来源图/mask 与 camera 对齐；冻结 baker 使用 z-buffer 和 foreground mask。未注入空 mask、遮挡错误或失效相机 | 当前样本的数据入口经过审计，但对无效可见性的 fail-safe 还没有端到端故障实验。 |
| 参考视角变好、其他视角变差 | Round012 confirmation64 的 `view_projection`：参考 FG-PSNR +4.2827 dB、CIEDE −2.2299；非参考 FG-LPIPS +0.000269（95% CI 跨 0），未证明非劣。既有 APG/GSO20 与 20-object bake 对照亦未证明整体 LPIPS 提升 | 参考图改善不能代替 11 个未见 bake 视角。该结果不是本次 UV 控制的质量验证。 |

## Phase A 结论

信号层为 **LIMITED**：来源图偏差值得保留为校准/诊断量；跨视角 UV 方差没有通过主要感知端点的选择门槛，两个信号合用也没有改善排序。现有证据不足以决定应给哪一个视角、在哪个阶段增加或减少几何 Adapter 残差。因而没有可冻结的状态条件控制规则；Phase A 不足以支持 Phase C。
