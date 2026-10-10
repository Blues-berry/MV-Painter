# 第九轮计划

1. 核实两rank2000行、梯度/损失有限、实际drop比例、对象曝光、最终权重哈希及完整状态；不看500/1000/1500步效果来选权重。
2. 保留两开发对象的native-disabled与新unscaled残差检查；在看新生成结果前冻结最多50个新native对象，按Fresh C UID顺序排除两开发和10个旧烘焙对象，仅按输入门槛筛选。全部失败入账。
3. 条件固定disabled、native_unset、native_gfl、native_gfh、budget_fixed_mean、native_gc3、budget_late16、gen_linear。原生512、50步、CFG2、相同对象/seed42/geometry。C3历史定义和shallow cap保持，native_unset不等于尺度1，不能称全默认ControlNet管线。
4. 主要比较预先冻结：新native_unset对disabled的对象级FG-LPIPS；第二主要比较Late-high对Fixed Mean的FG-LPIPS，两比较Holm校正。其他PSNR/SSIM/DeltaE及C3比较作完整次要族校正。GT目标位置、颜色空间和mask校准先通过，视角不当独立样本。
5. 先判断新checkpoint外观是否失效；输入/执行无效可修并重跑，负质量不能删。有效图像证据后再裁决真实烘焙扩展优先级，避免继续无收益扫参。
6. 本轮完成第七至第九轮总结，更新独立TeX/补充/回复/可复算记录，披露改变多个训练因素及Fresh研究暴露限制。

## 看新输出之前的统计细化

冻结50对象、两项主要FG-LPIPS比较Holm2；18项具名次要比较Holm18。每对象主要指标为五个非参考视角的算术均值，首个参考视角和全部六视角均值另外描述，不混入主要检验。配对bootstrap20000、sign-flip200000、seed20261010，以对象为单位。mask按旧EGL评价二值化GT alpha>0.5。GT自身与指标、50×6非空mask和相机名义方向校准通过；投影/极点roll与生成视角本身不由此证明。

已启动有条件自动衔接：只在现有训练完整2000步且通过实际CSV/权重核验、两GPU无其他进程后，运行全部50对象的disabled与native_unset两条件，并评价实际输出。后六条件仍为冻结计划，须根据有效新证据裁决，不能将当前阶段当作完整八条件实验。若原进程消失或训练失败，只记录失败，不自动重启或换对象。
