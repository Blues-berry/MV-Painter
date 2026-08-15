# TCAS 接手记录

更新时间：2026-08-15

## 当前目标

继续 TCAS（Timestep-Conditioned Adapter Scaling）论文修订和实验补强。历史项目名为 `tcas-experiment-cleanup`；当前事实以本地工作区、Git 差异、论文源文件和已有实验产物为准。

## 已确认状态

- 工作区存在未提交修改和新增脚本/产物，接手时必须保留；禁止 reset、checkout、清理、提交或推送，除非用户明确要求。
- `CLAUDE.md` 是项目入口说明，`find.md` 记录了 adapter/checkpoint/scale 语义差异、C3 机制和已有消融结果。
- FAC v3 的 300-object 结果是真实负结果：LTAG 16.97/0.3487，LTAG+GSG 16.21/0.3163，Full FAC 16.11/0.3204；对应产物在 `mvpoutput/fac_v3/`。
- `final/revision_supplement_0707.md` 已将 FAC 标为删除，并同步了 v2 的 300-object 数字和 warm-start 结论。
- `geotex/probe_warmstart_ckpt.py` 已包含真实 scheduler 配置、C3 边界和 LTAG-only 断言；现有 warm-start 输出为 12-object 对照。
- A1 已完成：`mvpoutput/revision_c3_sensitivity/`，24-object、15 个窗口/峰值候选。
- A2 已完成：`mvpoutput/revision_top2_300/`，300-object 的 C3/trapezoid/gaussian_peak 对照；C3 在 PSNR 和 FG-SSIM 上均显著领先两个 probe top-2 非 C3 候选。
- 最新阶段效用重跑已完成：`mvpoutput/explore_contradiction/stage_ablation_v2_24obj_rerun/`，24 objects、50 steps、seed=42；early/middle/late PSNR utilities 为 -0.788/+0.574/+0.077 dB，并保存逐对象 CSV 与 95% CI 分析。
- residual-normalized 最小判别实验已完成：`mvpoutput/explore_contradiction/norm_schedule_v2_strength_match_6obj/`；`norm_flat` 与 `fixed_low_weak=1.0` 逐对象完全等价，归一化不作为第二方法。
- `TCAS_EVIDENCE_LEDGER.md` 是当前最小证据—结论—路径映射；`final/final_submit.tex` 是本轮正式编辑源。
- 之前报告中的“复审 PASS”不能直接视为当前主稿状态，必须结合当前文件重新核对。

## 当前关键问题

存在两个论文源文件：

- `final/final_submit.tex`（2026-08-11）：当前较新的候选稿，已移除 FAC，并使用 CAI/adapter-dependence 叙事；未发现 FAC 引用。
- `final/final.tex`（2026-08-05）：旧稿，仍包含 FAC 摘要/图注/方法/实验/表格/结论以及已作废的 19.28、0.4830、81.3%/72.0% 数字。

`final/final.tex` 保留为旧稿，仅供历史追溯；不得用它重新编译发布版本。当前正式编辑源为 `final/final_submit.tex`。

## 研究结论约束

- 不得混用 refattn_v1、v2、v3 checkpoint 的结果。
- 不得单独把 Laplacian variance 解释为纹理质量；必须结合 FG-SSIM、PSNR、伪影/感知证据。
- C3 是在 24-object probe 上选出后冻结，再迁移到 300-object；不能在验证集重新搜索。
- C3 的副作用缓解方向具有结构性，但 failure mode、强度和危险阶段依赖 adapter residual 与推理 scale 语义。
- CAI 是当前理论主线；FAC 已删除，不应恢复旧的正向叙事或合成数字。

## 下一步

1. 保持 `final/final_submit.tex` 为唯一发布源，旧 `final/final.tex` 不参与编译。
2. A1/A2 和最新 stage utility 结果必须沿用 `TCAS_EVIDENCE_LEDGER.md` 的 provenance；不要把 A1 的 2.75 微小 PSNR 优势夸大为新方法。
3. residual normalization 只保留为 `min(scale, cap) × raw_norm` 机制诊断，不扩展到 24/300 objects。
4. 代码编辑后运行 `py_compile`、schedule 边界检查、引用检查、完整 LaTeX 编译，并执行论文/代码双角色复审。

## 推荐接手 prompt

```text
接手当前 /4T/CXY/MV-Painter 工作区。历史项目名是 tcas-experiment-cleanup。
先只读审计，不修改文件、不运行长实验：检查 git status/diff，阅读 CLAUDE.md、find.md，核对 final/final.tex、final/final_submit.tex、revision_supplement_0707.md、probe_warmstart_ckpt.py 和已有 300-object CSV。重点确认哪个 TeX 是正式编辑源，并检查 FAC 删除及数字一致性。保留所有未提交改动，不要 reset、checkout、清理、提交或推送。
输出当前真实状态、已完成/未完成事项、论文冲突、A1/A2 必要性和最小下一步。
```
