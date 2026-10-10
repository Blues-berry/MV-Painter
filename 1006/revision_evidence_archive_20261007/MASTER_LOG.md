# 修订证据总日志

**归档完成：2026-10-07 01:52 UTC**  
**范围：非人工实验、审计、图件和审稿意见证据**  
**总状态：CORE_NONHUMAN_RESULTS=VERIFIED_WITH_ONE_UPSTREAM_LEDGER_HASH_GAP；CURRENT_CANDIDATE_REBUILD=FAIL；MANUSCRIPT_EDIT=NONE。**

## 1. 执行范围与保护条件

- 只整理/核验已有材料；没有启动 Fresh D、新 schedule search、新 backbone、E6 新运行、GPU inference 或 3D bake。
- 未改写、编译或覆盖 01549 主稿。15 个已冻结主稿/回复/评审文件的历史 hash 重新核对通过；本次 `git status` 对所查主稿路径为 0 项变更。
- 没有读取、复制或分析任何人工答卷文件；没有开展人工实验设计或招募。上传的审稿意见仅作为审稿原文来源被复制和映射。为核对历史 N=20 GLB 非人工指标，读取了混合范围的 `1006/evidence/audits/GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`（SHA-256：`3a28469e45efa89b677b8ed95d008e1707ce276d5b5c55744ff44ba67c28230c`）中的 GLB 指标段。原报告因含人工研究内容而未复制；只生成 `source/results/HISTORICAL_N20_GLBNATIVE_NONHUMAN_EXTRACT.md`，其余人工研究内容未纳入、分析或解释。
- 原目录中的实验日志、逐对象 UID 表、渲染和模型资产不移动、不删除、不覆盖；只把被选定的报告、聚合结果和已审查图件复制到新目录。

## 2. 多轮实验和审计时间线

| 日期/阶段 | 核验与结果状态 | 归档处理 |
|---|---|---|
| 2026-10-05：A2/A3/B 轮 | A2 的 layer×window 反应图属于探索性/native-dose 结果；发现旧 interaction bootstrap 零功效后改用经过验证的 cluster-Wald/GEE 作统计审计。B 的 4,500/4,500 行门禁 PASS；A3b 仍有实际剂量偏差与空共同支持。 | 采用经过修正的摘要，保留探索/部分状态，不把统计显著改写成剂量机制或唯一 schedule。
| 2026-10-05 至 10-06：generic schedule 与 strict-276 | B generic extension 是解盲后同 cohort sensitivity；strict-276 的 276 对象配对统计可重构，但 runner/input-tensor provenance 不完整。 | 保留结果，标注 post-lock / retrospective；不作为独立复制。
| 2026-10-06：E1/E2 | 两项 48-object、3 固定 seeds 的辅助实验 integrity gates 均 PASS；它们是固定子集的实现/seed sensitivity。 | 收录聚合报告、门禁和数值，不称独立对象泛化。
| 2026-10-06：Fresh C | N=300 的原四条件 1,200/1,200 PASS；LLH/linear addendum 600/600 PASS；单独 cohort/测试族；28 项方向/统计复核。 | 作为当前 image-space 主权威结果，连同两个 analysis JSON、两门禁和方向审计复制。
| 2026-10-06 至 10-07：跨接口、视觉、3D 与 rights | MV-Adapter/MVDiffusion 只支持接口边界解释；sampler synthetic 11/11 PASS，但 Fresh C 24-object native-UV/alpha 完整 gate FAIL，因此新 3D panel retired；seam claim retired。Figure D 20 个资产得到 CC BY 校验并有 attribution，其他不明资产排除。 | 仅保留限定范围报告和图件；没有把 synthetic sampler 通过扩大成实际 3D/seam 通过。
| 2026-10-07：归档独立复核 | 28 个 Fresh C 端点/对比统计量按现存 object-paired delta 表重新计算并与锁定 JSON 对照；另复核行门禁 hash、strict-276 行结构、E1/E2 gate、rights counts、sampler cases、manuscript hashes。 | 具体结果见 `VERIFICATION_REPORT.json`。核心数字核验通过；总账引用另有一个变化中的子账 hash 缺口，单独列为 PARTIAL。

## 3. 独立核验清单

| 项目 | 结果 | 说明 |
|---|---|---|
| Fresh C 主 run | PASS | 1,200/1,200；combined CSV hash 对齐完整性 gate。
| Fresh C 附录 | PASS | 600/600；combined CSV hash 对齐完整性 gate。
| Fresh C 统计/方向 | PASS | 从配对差值重新计算 28 项均值、中位数、对象 bootstrap CI、paired p、Holm p 和有利对象比例；与分析 JSON 一致；0 个方向错误。
| strict-276 | PASS / RETROSPECTIVE | 552 个 object-contrast rows，两个对比各 276 个对象，14 个摘要；旧 runner/input lineage 限制仍在。
| E1 / E2 | PASS / BOUNDED | integrity gate 分别确认 576 新行；E2 有 576 logical rows（480 新行 + 96 reuse）。
| rights | PASS WITH EXCLUSIONS | 300 行分类计数 20/271/9；Figure D 20 行 attribution。
| synthetic glTF sampler | PASS 11/11 | 只验证 synthetic geometry；N=24 实际 bake/render gate 仍失败。
| seam synthetic gate | NUMERIC-ONLY | 不是生产 endpoint，真实资产改善未测试；最终 seam claim retired。
| manuscript preservation | PASS | 15/15 文件的已有 SHA-256 复核通过。
| current clean-checkout candidate | FAIL | 没有可从干净提交检出的当前 closure candidate；旧 compact package 的通过不替代本状态。

## 4. 总账 hash 缺口（不可忽略）

旧版 `FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json` 指向 `1006/evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`，声明 SHA-256 为 `ca3b9f52ecc0e890caeec65d496e4ba0fcf1490d85fb407601e33ba7e3450ce8`。只做元数据/哈希核对时，子账文件在本次审计的连续读取中出现多个不同哈希（`97ffb95a…`、`3fb9031b…`、`5e1ab700…`），且文件大小也变化；最后稳定读取为 `5e1ab7006a8cf36c22007a4797944637a51bd2b36d108ce1fc96b7ffb6231a75`。

该子账属于混合范围且本阶段排除人工研究结果，所以没有打开其正文或复制；5 条含人工研究路径的来源引用亦未检查。其余 149 条非人工哈希引用通过，1 条子账引用不匹配。旧版验证记录中的 PASS 只证明当时校验的快照，不能覆盖当前文件变化。本包因此将**当前非人工数字**作为唯一可用结果汇总，同时把 paper-wide/claim-ledger authority chain 标成 PARTIAL；未自行覆盖旧 ledger，也未伪造新的总账 PASS。

## 5. 来源状态与工作树

- 本地分支：`codex/scientific-validation-v3-20261002`；HEAD：`5c2c8829a1e19b42837761160dc4c14cf8f09045`。
- 审计时已有 7,207 条 tracked status 行；大量文件在审计开始前就已 staged/dirty。本次不 reset、不 stage、不 commit、不 push，原状态保留。归档建在既有未跟踪 `1006/` 树下。
- 之前 reconciliation 报告记录的公开分支状态没有在本次重新联网抓取；本归档不声称远端已更新。
- `source/` 中的逐字复制均由 `ARTIFACT_MANIFEST.csv` 记录源路径、源 SHA-256、归档 SHA-256 和字节数。所有归档文件另列在 `SHA256SUMS.txt`（校验文件自身除外）。

## 6. 最终处置

此目录提供可以继续讨论和审查的单一非人工证据视图；它不是已冻结的公开复现包，也不授权主稿修改或提交。后续若要完成 paper-wide authority closure，需在不混入人工结果的单独版本中解决上述源子账版本/哈希问题，再重新审查 current candidate clean-checkout rebuild。
