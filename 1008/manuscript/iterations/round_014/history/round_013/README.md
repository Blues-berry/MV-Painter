# 第13版实证叙事草稿

基于round012，不开发新算法，不新增GPU实验。原标题和TCAS/C3身份保留，主文围绕控制比较、实际烘焙和跨接口边界重组，原历史图表及辅助实验移入补充S32而不删除。

- 主文：manuscript_round_013.tex；build/manuscript_round_013.pdf
- 补充：Supplementary_round_013.tex；build/Supplementary_round_013.pdf
- 中文分析：01_EVIDENCE_CHAIN_AND_NARRATIVE.md
- 回复：Response_to_Reviewers_round_013.md
- 新外部数据：data/GSO100_VIEW_METRICS.csv；14400视角行、2400唯一单元
- 离线检查：python recompute_external_tables.py；不需要模型或GPU
- PDF重建：bash build_round_013.sh；从../../source_01549读取已保存的期刊模板

目前为作者审阅草稿。GSO20烘焙仍在校准门槛处中断；本文明确报告其未完成，不将15对象替代完整确认。不声称原adapter的+0.96直接复现或FAC完全恢复。旧300/50/10等数据与冻结脚本沿用round012和既有证据目录；当前目录不是包含所有权重/原始模型资产的完整推理包。

用户随后授权在实证叙事下补现有方法实验；当前真实进度以02_EXISTING_METHOD_SUPPLEMENT_HANDOFF.md及服务器STATUS为准。初稿“不新增GPU实验”描述的是创建时的编辑阶段，后续已开展现有方法补充验证。

Supplementary chain completed: fixedGSO100 existing-profile extension, GSO20 all740 bakes, posthocGT calibration explicitly disclosed, original375 records reproduce exactly. See sections/completed_supplement013.tex and server delivery evidence for current status.
