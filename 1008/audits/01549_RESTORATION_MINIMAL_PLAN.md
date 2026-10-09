# 01549 恢复修订最小执行计划与完成记录

**状态：** 已执行。此记录对应 C&G 1008 第二轮修订，不是等待批准的方案。

## 基准与版本关系

- `CAG-S-26-01549` 是完成第一轮修改后于 2026-09-07 提交的版本；当前 R1/R2/R3 是该版本的第二轮意见，1008 是第二轮修订。
- 历史基准为 `final/submission_new_0907/` 正式包中的 Manuscript、Marked-up Manuscript、Response Letter、Supplement 和 `latex.zip`。
- 原始 TeX `1008/manuscript/source_01549/final_0903.tex` 的 SHA-256 为 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`，与 ZIP 内 `final_0903.tex` 字节相同。
- 旧 `1008/manuscript/revision_1008/` 候选保留原样；活跃第二轮源为 `1008/manuscript/revision_01549_restored/manuscript_1008.tex`，作者审阅包在 `1008/submission_1008_final/`。

## 最小执行步骤与结果

1. **锁定 01549。** 校验源 TeX 哈希、官方 ZIP 成员、15 页提交 PDF 和七张原图哈希。`verify_baseline_lock.py` 全部通过。
2. **从原稿恢复。** 从正式 ZIP 成员建立新的修订源，选择性移植第二轮已核验的新证据；不覆盖旧候选。
3. **保留有效主体与第一轮成果。** 保留 TCAS 方程、三阶段 profile、C3、fixed-scale 扫描、24-object development probe、first-round disjoint-holdout 和 adapter-dependence 分析。FAC 负向复查保留为此前报告的辅助结果并披露归档差异；30-object/24-participant 3AFC 汇总保留为原研究范围内的主观偏好结果。
4. **只修正第二轮剩余问题。** R1.2 使用 Fresh C N=300 单冻结 checkpoint/同 runner/seed policy/同 cohort 与输入、视图、指标、实际 cap 语义的配对结果：C3−GFL FG-PSNR `+0.522352 dB`，95% CI `[+0.404160,+0.640669]`。不要求其 checkpoint 哈希等同历史 Table 4；保留 v1/v2 历史差异且不声称重现旧 `+0.96 dB`。同时呈现 GFH、Generic Linear 和 LLH 端点反结果。R2.1 保留 TCAS 并明确任务范围与 prior art；R2.2 仅撤回 CAI 推导/证明/selector/optimality；R2.3 报告真实跨接口检查及边界；R3 无新技术要求。
5. **保留和更换图表。** 原 Fig. 1 全图及 FAC 支路不变，原 Fig. 2–3 恢复，原 Fig. 7 只修正局部文字并限定为开发集；原 Fig. 4/6 改为 Fresh C 全物体 matched 视觉证据；原 Fig. 5 proxy 结果因无法复核退出。历史 Table 3/9 等依证据边界移入 Supplement；保留原 3AFC 汇总，Fresh C 表替换过时 pooled headline。
6. **构建交付包。** 主文 PDF 11 页，Supplement PDF 10 页，marked-up PDF 20 页，Response Letter PDF 3 页；另含 TeX、变更日志、reviewer traceability、source ZIP。主文和 Supplement 本地编译通过。编辑器内置编译工具被调用两次但均超过两分钟未返回诊断，编辑器端结果记为未核实。

## 交付路径

- `1008/submission_1008_final/Manuscript_1008.tex` / `.pdf`
- `1008/submission_1008_final/Marked-up_Manuscript_1008.pdf`
- `1008/submission_1008_final/Supplementary_1008.tex` / `.pdf`
- `1008/submission_1008_final/Response_to_Reviewers_1008.md` / `.pdf`
- `1008/submission_1008_final/01549_TO_1008_CHANGELOG.md`
- `1008/submission_1008_final/SUBMISSION_BUILD_REPORT.md`

详细图像比较见 `1008/audits/01549_FIGURE_PRESERVATION_REVIEW.md` 与 `1008/audits/forensics_R2_1_20261008/01549_original_vs_current_figures_internal.pdf`。
