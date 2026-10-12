# P0 评价预案（队列完成后执行；本轮不启动）

## 触发条件

`PERSISTENT_QUEUE_STATUS.json` 状态变为 `COMPLETE_FROZEN_CHAIN`（四监督器全部 COMPLETE）。
任一 FAILED 则停止并人工审查（保留失败，不自动重试——继承队列规则）。

## 已冻结的评价对象

| 阶段 | 数据 | 评价内容 |
|---|---|---|
| dev32 基线+候选 | `development32_{native,grid_projection,view_projection}_seed{42,2026,31415}_rank{0,1}` 与 `development32_interaction_projection_seed{...}_rank{...}` | 每条件 32 对象 × 6 视角；对象为分析单元（视图内均值，不做独立样本） |
| MV-Adapter 第二骨干 | `mvadapter_development32_seed{...}_rank{...}`（native/grid/view/interaction 四条件 × 3 seeds） | 同协议；与 MVPainter 结果分集呈现，禁止跨骨干配对池化 |
| APG 恒等门 | `apg_native_identity_seed42_attempt01` | 仅核验 disabled-APG 像素恒等（PASS/FAIL），不参与质量比较 |

## 统计协议（对齐既有冻结约定）

1. 主比较：`interaction_projection − native`（每骨干、每种子分别报告），对象级配对差值 + 50k bootstrap 95% CI + 精确符号检验（2 侧枚举）。
2. 辅助比较：`view_projection − native`、`grid_projection − native`，同协议；报告全部指标（fg_psnr/fg_ssim/fg_lpips/ciede2000），不挑选。
3. 分层报告：source 视角与非未见视角分开（P2 诊断的 H1 预测作用于 source 视角外观）。
4. 三种子合并仅在方向一致时作为"跨种子一致"陈述，不合成更大样本。
5. 全部结论标注 `development32 frozen cohort, preoutput-frozen protocol`；不得声称确认性优势。
6. 评价脚本从 `probe_condition_interference012.py` 的输出结构直接读图（PNG 六视角拼接），评分复用 `evaluate_fresh_c_native_egl.py` 的 metric 实现（LPIPS 可用 CPU 以免干扰后续队列）。

## 验收门

- 每个 run 目录 `RUN_IDENTITY.json` 状态 `COMPLETE_*` 且 `execution_source.py` SHA 与冻结记录一致。
- 输出计数 = 冻结 uid 数 × 6 视角；逐文件 SHA 记录。
- 评价 JSON 写入本增量文件夹 `p0_queue_watch/outputs/`；不改 iteration012 内任何文件。

## 结果分支（联动 P3）

- **interaction_projection 跨 3 种子在 source 视角外观指标改善且未见视角不显著变差**：按 P3 分支 A 升级稿件叙事。
- **方向不一致或无分离**：按 P3 分支 B 保持实证定位，报告为探索性负/中性结果。
- **MV-Adapter 第二骨干方向与 MVPainter 一致**：叙事可提"跨接口方向一致（开发证据）"；不一致则如实分层陈述。
