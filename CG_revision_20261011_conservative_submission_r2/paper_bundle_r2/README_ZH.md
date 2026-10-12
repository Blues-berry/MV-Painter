# 论文与 FAC 交付汇总

本分支以 Round 015 已上传版本为基础，附加 2026-10-11 的保守投稿 r2 文档包。

## 当前投稿 r2

`paper_bundle_r2/` 包含正文、标记稿、补充材料、审稿回复的 TeX/Markdown 与成品 PDF/DOCX；LaTeX 样式、构建脚本及正文和补充材料直接引用的图也一并提供。未引用的备选图、原始实验图、实验结果、日志、模型权重、数据和视频不在本次新增文件中。图源和署名记录位于 `paper_bundle_r2/provenance/`。

在 `paper_bundle_r2/manuscript/` 中运行 `build_clean_conservative_submission_r2.sh`、`build_marked_conservative_submission_r2.sh` 和 `build_supplement_conservative_submission_r2.sh` 可分别构建正文、标记稿和补充材料；需要本地 TeX 工具链。

## Round 015 与 FAC

以下材料已包含在本分支的基础提交 `f310d3f77e3e63de9d6983d44c79b00375769804`：

- [Round 015 论文 PDF](../../1008/manuscript/iterations/round_015/deliverables/Manuscript_round_015.pdf) · [完整投稿包](../../1008/manuscript/iterations/round_015/submission_package/Submission_Files_round_015.zip)
- [第 15 轮风险与比较](../../1008/manuscript/iterations/round_015/02_RESULTS_RISKS_AND_COMPARISON.md)
- [第 13–15 轮总结](../../1008/manuscript/iterations/round_015/03_ROUNDS_013_015_SYNTHESIS_ZH.md)
- [恢复的 FAC 源码快照及入口差异](../../1008/manuscript/iterations/round_015/fac_code_snapshot/README.md)
- [三个离线组件配置的检查记录](../../1008/manuscript/iterations/round_015/data/gap_closure015/FAC_COMPONENT_VALIDATION.json)

FAC 检查覆盖 LTAG、LTAG+GSG、LTAG+GSG+FSC 的 CPU 组件 fixture，并核对有限输出/梯度与状态往返。早期训练入口默认允许更新基础 adapter 和 geometry encoder；后期入口只优化 controller。检查不恢复历史训练清单、随机种子、checkpoint 或完整训练运行身份。
