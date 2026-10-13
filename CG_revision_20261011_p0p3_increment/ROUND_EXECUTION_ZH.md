# P0–P3 增量轮执行记录

日期：2026-10-11（北京时间）。执行者：Trae agent（GLM）。规则：全程只读既有文件，全部新增写本文件夹；未触碰在途队列、conservative_final 交付与任何实验目录内容。

## 已完成

### P1 native_unset 默认对照评分（完成）
- 发现实验侧生成/渲染此前已完成但稿件未纳入：`iteration002_controls` PASS（10 对象）、`native_egl_unseen` 110 张未见渲染齐全、50 对象图像域评分已有，唯缺烘焙未见视角指标评价。
- 构建派生聚合渲染视图（gt←bake_matrix_v2，native_unset/no_adapter←iteration002_bake；逐文件 SHA 复验，硬链接，派生关系透明标注）。
- 用既有评价脚本（协议不变，LPIPS=CPU）完成评分；做与冻结七条件的对象级配对对比（50k bootstrap + 精确符号检验）。
- 结果：native_unset 烘焙未见 PSNR 11.14（GT 22.38）；对全部生成条件不占优（capped −0.80 dB p=0.021、gfl −1.35 p=0.021 显著劣，其余不显著）；no_adapter 5.92。**闭合 R1.1 默认对照缺口，方向有利于稿件。**
- 产出：[P1_RESULTS_ZH.md](../p1_native_unset/P1_RESULTS_ZH.md)、NATIVE_EGL_METRIC_EVALUATION.json、NATIVE_UNSET_PAIRED_CONTRASTS.json。

### P2 棕色化只读诊断（完成）
- 排除项：VAE 编解码往返、cond_lat 训练/推理路径、CFG 负分支、checkpoint 加载——全部一致（此前审计 PASS）。
- 决定性证据：①6/6 观测步几何控制噪声与参考外观方向负 cosine（均值 −0.585，反向能量 36%）；②训练先验 34.6% 暖棕主导；③10 对象生成输出收敛到亮暖灰带（7/10 暖棕 vs 参考 4/10）。
- 因果图景 H1：几何-参考干涉 → 先验回归（棕色重复纹理）；与 seed42 view_projection source +2.92 dB 方向一致；native_unset 不消除失效。
- 产出：[P2_DIAGNOSIS_ZH.md](../p2_appearance_diagnosis/P2_DIAGNOSIS_ZH.md)、P2_DIAGNOSIS_EVIDENCE.json。

### P0 监控与评价预案（完成，等队列）
- 只读监控器 `watch_queue.py` 已启动（每 120s 快照；在途 monitor 保持权威，不重启不干预）。当前快照：RUNNING_PERSISTENT_CHAIN，dev32 进度 14/16 cell。
- 评价预案 [P0_EVALUATION_PREPLAN_ZH.md](../p0_queue_watch/P0_EVALUATION_PREPLAN_ZH.md)：统计协议、验收门、结果分支已冻结成文；队列 COMPLETE 后按预案执行。

### P3 整合预案（完成，待 P0 选分支）
- 已锁定内容：native_unset 进正文/S22 闭合 R1.1；棕色化机制句进 Discussion（"consistent with" 措辞红线）。
- 分支 A/B 叙事已预先界定（投影有效→干涉管理框架；无效→探索性负结果），见 [P3_INTEGRATION_PLAN_ZH.md](../p3_integration_plan/P3_INTEGRATION_PLAN_ZH.md)。

## 未做（按规则不做）

- 未启动任何新 GPU 生成（避免干扰在途队列）。
- 未修改 MVPainter 源码（P2 为只读诊断；修复决定留给作者，且会破坏冻结比较）。
- 未整合稿件（等 P0 结果选分支后在新目录执行）。
- 未把任何结果写成确认性结论（10 对象探索性 + 6 行开发观察的证据边界已在各文档标注）。

## 对中稿概率的影响路径

1. P1 闭合 R1.1 三个 PARTIAL 中最明确的一个（默认对照）→ 回复信完成度表可升级。
2. P2 给 R1 的最大视觉顾虑（棕色化）提供机制解释，把"未定位失败"转为"有证据的机制 + 边界"。
3. P0 的 iteration012 结果决定 R2.1 是否从 UNRESOLVED 移动——这是中稿概率的下一个跳变点（见本轮分析：现状 ~30–40%；分支 A 成立约 55–70%）。
