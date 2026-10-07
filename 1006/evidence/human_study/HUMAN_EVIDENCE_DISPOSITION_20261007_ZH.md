# 人工证据定位与冻结门槛修订 — 2026-10-07

> **分类修订：** 2026-10-07，研究负责人确认 40-slot 答卷是确认性人评。当前权威裁决见 [`HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md`](HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md)：按预先冻结的八端点家族作确认性分析，并完整披露具体执行偏离。下文的“敏感性分析/非确认性”是此前的保守分类快照，统计结果和偏离审计仍有效，但分类已 supersede。

## 裁决

人工证据不再是 `SCIENTIFIC_EVIDENCE_FREEZE` 的独立阻塞门。保留两项研究各自的适用范围：

- **01549 原有 3AFC：正文中的主要补充感知证据。** 它支持原 C3/TCAS 与两个统一 scale 基线之间的感知偏好权衡，不验证后来形成的 LLH，不是对参考材质的直接 fidelity 判断，也不检验未见视角、烘焙 3D、PBR 或接缝。
- **2026-10-06 上传的 40-slot 数据：已完成的敏感性分析。** 可以在补充材料中按协议偏离敏感性结果报告；不能称为确认性人评，不能用来证明 LLH 优势、等效性或人类保真。
- **不再追加人评或为 40-slot 数据恢复旧 assignment、blind key、逐图 hash 才允许冻结。** 若后续要主张 LLH 的人类偏好、参考保真或 3D 感知优势，需另立研究；当前论文不作这些主张。

这项门槛变更只影响科学证据冻结。伦理/同意、参与者级数据的公开处理和图像授权仍属于最终投稿/发布检查，不由统计结果替代。

## 01549 的原有 3AFC

已提交的 01549 文稿记录：24 名参与者、30 个对象、三个匿名并列条件（统一 scale 1.25、统一 scale 2.50、C3/TCAS），每人完成全部 30 个对象的纹理自然度、形状一致性和整体质量判断；每个标准有 720 票，条件左右顺序按 trial 随机。文稿报告参与者与对象双向 cluster bootstrap、10,000 次重采样。

| 评价标准 | scale 1.25 | scale 2.50 | C3 / TCAS |
|---|---:|---:|---:|
| 纹理自然度 | **46.1%** (332/720) | 14.4% (104/720) | 39.4% (284/720) |
| 形状一致性 | 13.3% (96/720) | **46.0%** (331/720) | 40.7% (293/720) |
| 整体质量 | 24.4% (176/720) | 17.5% (126/720) | **58.1%** (418/720), 95% CI **[50.1%, 65.8%]** |

允许的结论是：在这项 3AFC 及其三个旧条件中，C3 获得最高整体质量偏好，同时两个统一 scale 基线各自在不同标准上有优势；这支持“感知上偏好的折中”，不支持“所有维度普遍更优”。问卷比较的是生成条件之间的相对选择，没有把 GT 作为一个需匹配的选择条件，因此不应称作直接的人类参考保真测试。

来源与复核边界：完整设计、计数和置信区间可在提交稿 [01549 PDF](/4T/CXY/MV-Painter/1006/manuscript/source_format/01549_submitted_manuscript_0907.pdf) 与原稿 [final_0903.tex](/4T/CXY/MV-Painter/final/final_0903.tex) 中核对；cluster bootstrap 实现保存在 [cluster_bootstrap_preference.py](/4T/CXY/MV-Painter/geotex/cluster_bootstrap_preference.py)。当前工作区未找到这项旧研究的逐票 CSV，因此这里保留已提交稿报告的结果，不声称本次从原始答卷独立重算。不得把这项结果转移给 LLH、generic linear、no-adapter、新输出 cohort、未见视角或 3D 烘焙。

## 40-slot 敏感性分析

原始输入来自 GitHub commit `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` 的四个 CSV。行级输入与 assignment、对象 UID、左右方法映射 **960/960 对齐**；40 个槽位均出现于导出，按表内完整性和理解检查保留 37 人（排除 2 个理解检查失败、1 个未完成/缺答），覆盖 24 个对象与 LLH 对 GFL、GFH、GC3、generic linear 的 8 个“比较×问题”端点。每端点有 222 次判断。分析不把 222 次判断当作独立样本：先在对象内计分、对象等权；平局记 0.5；对参与者和对象双向 bootstrap 10,000 次、固定 seed 20261005，使用逐端点 95% CI 和冻结的双侧 bootstrap tail rule；8 个端点统一做 Holm 校正。

所有八个点估计都高于 0.5，但**没有任何端点通过 Holm 校正**。外观保真估计范围为 0.540–0.591；纹理自然度为 0.539–0.647。两个较低的未校正 p 值出现在 LLH 对 GFL 的纹理自然度（0.647，CI [0.528, 0.755]，raw p=0.0123，Holm p=0.0984）和 LLH 对 GC3 的纹理自然度（0.632，CI [0.521, 0.741]，raw p=0.0183，Holm p=0.1281），均未过家族校正。LLH 对 generic linear 的外观端点为 0.540 [0.412, 0.667]，纹理端点为 0.539 [0.420, 0.653]；这既没有检测到有利偏好，也**不构成等效或非劣证据**。

协议偏离仍须随结果说明：上传的 40 个任务表与冻结包的 assignment schedule 匹配数为 0/40；96/96 个对象×比较单元在参与者之间采用固定左右次序；导出没有随机种子、题序、理解检查原始答案或 stimulus alias 到冻结 PNG hash 的对应表；coordinator closeout 表仍为 pending。因此结果分类维持 `PROTOCOL_DEVIATION_SENSITIVITY_ANALYSIS_NOT_CONFIRMATORY`。这些限制决定其证据等级，但不再阻塞当前受限论文主张的科学冻结。

完整八端点表、森林图、源 hash 和分析脚本：

- [端点统计表](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_ENDPOINT_RESULTS_20261006.csv)
- [敏感性森林图](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_SENSITIVITY_FORESTPLOT_20261006.png)
- [分析 provenance](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json)
- [复算脚本](/4T/CXY/MV-Painter/1006/evidence/human_study/analyze_uploaded_human_responses.py)
- [接收与偏离审计](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md)

## 建议写入论文的表述

正文保留旧研究，但限定对象和结论：

> “In the original 24-participant, 30-object 3AFC study, C3 received 58.1% of overall-quality choices (95% participant-and-object cluster-bootstrap CI [50.1%, 65.8%]). The two uniform-scale baselines led on texture naturalness and shape consistency, respectively. This study supports a perceptually preferred balance among the three original conditions; it does not establish universal perceptual superiority or validate the later LLH profile.”

若保留 40-slot 分析，仅放在 Supplementary，并标明非确认性：

> “We additionally report a protocol-deviation sensitivity analysis of a user-supplied 40-slot response export. All eight point estimates favored LLH, but none survived Holm correction. Assignment schedules did not match the frozen package, within-cell left/right order was fixed, and stimulus hashes could not be verified; we therefore treat these estimates as exploratory and do not infer preference, equivalence, non-inferiority, or reference fidelity.”

不要将 40-slot 结果改写为“确认性 human evaluation”；不要将旧 C3 3AFC 写成对 LLH 的验证；不要将任一 2D 研究当作未见视角、mesh、UV seam 或完整材质 fidelity 的证明。
