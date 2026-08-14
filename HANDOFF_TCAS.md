# TCAS 接手记录

更新时间：2026-08-13

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
- 之前报告中的“复审 PASS”不能直接视为当前主稿状态，必须结合当前文件重新核对。

## 当前关键问题

存在两个论文源文件：

- `final/final_submit.tex`（2026-08-11）：当前较新的候选稿，已移除 FAC，并使用 CAI/adapter-dependence 叙事；未发现 FAC 引用。
- `final/final.tex`（2026-08-05）：旧稿，仍包含 FAC 摘要/图注/方法/实验/表格/结论以及已作废的 19.28、0.4830、81.3%/72.0% 数字。

在确认哪个文件是正式编辑源之前，不要修改论文或用旧稿重新编译发布版本。`CLAUDE.md` 仍把 `final/final.tex` 写作主论文入口，这与当前文件时间和内容不一致。

## 研究结论约束

- 不得混用 refattn_v1、v2、v3 checkpoint 的结果。
- 不得单独把 Laplacian variance 解释为纹理质量；必须结合 FG-SSIM、PSNR、伪影/感知证据。
- C3 是在 24-object probe 上选出后冻结，再迁移到 300-object；不能在验证集重新搜索。
- C3 的副作用缓解方向具有结构性，但 failure mode、强度和危险阶段依赖 adapter residual 与推理 scale 语义。
- CAI 是当前理论主线；FAC 已删除，不应恢复旧的正向叙事或合成数字。

## 下一步

1. 先由用户或后续审计确认 `final_submit.tex` 是否正式替代 `final.tex`。
2. 将论文、补充材料、表格和 CSV 的数字在正式源文件上做一次定向一致性检查。
3. A1/A2 结果已写入 `final/revision_supplement_0707.md`，主稿候选 `final/final_submit.tex` 已加入谨慎的稳健性论证；不要把 A1 的 2.75 微小 PSNR 优势夸大为新方法。
4. 论文编辑前形成“证据—结论—修改位置”映射；代码修改后运行 `py_compile`、引用检查、相关 smoke test，并执行论文/代码双角色复审。

## 推荐接手 prompt

```text
接手当前 /4T/CXY/MV-Painter 工作区。历史项目名是 tcas-experiment-cleanup。
先只读审计，不修改文件、不运行长实验：检查 git status/diff，阅读 CLAUDE.md、find.md，核对 final/final.tex、final/final_submit.tex、revision_supplement_0707.md、probe_warmstart_ckpt.py 和已有 300-object CSV。重点确认哪个 TeX 是正式编辑源，并检查 FAC 删除及数字一致性。保留所有未提交改动，不要 reset、checkout、清理、提交或推送。
输出当前真实状态、已完成/未完成事项、论文冲突、A1/A2 必要性和最小下一步。
```
