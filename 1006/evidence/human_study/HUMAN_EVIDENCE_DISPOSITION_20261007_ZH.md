# 人工证据定位与冻结门槛修订 — 2026-10-07

> **当前分类：** 2026-10-07，研究负责人确认 40-slot 答卷是确认性人评。按预先冻结的八端点家族作确认性分析，并完整披露执行偏离。此前的敏感性/非确认性分类见归档文件 [`HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md`](HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md)，已由现行裁决 supersede；其原始统计和偏离审计事实仍用于追溯。

## 裁决

人工证据不再是 `SCIENTIFIC_EVIDENCE_FREEZE` 的独立阻塞门。保留两项研究各自的适用范围：

- **01549 原有 3AFC：正文中的主要补充感知证据。** 它支持原 C3/TCAS 与两个统一 scale 基线之间的感知偏好权衡，不验证后来形成的 LLH，不是对参考材质的直接 fidelity 判断，也不检验未见视角、烘焙 3D、PBR 或接缝。
- **2026-10-06 上传的 40-slot 数据：确认性人评端点分析，伴随已披露的执行偏离。** 研究负责人确认这批答卷是确认性研究；四个比较、两项问题、八端点家族和统计规则在收集前已有冻结方案。将其作为确认性结果完整报告，不降为敏感性或探索性分析。数据及答卷映射通过重建核验；预定端点不因执行偏离而删减或改写。八项估计均高于 0.5，但无一通过 Holm 校正，因此结论是未检测到 LLH 的校正后偏好优势。
- **不追加人评或为该研究重建缺失的历史随机化/刺激记录作为冻结前提。** 当前证据等级按已完成的确认性端点分析记录；执行偏离另列为协议符合性与溯源限制。若未来要主张随机化流程完全符合原锁定、参与者端刺激字节独立验证、LLH 感知优越、绝对参考保真或 3D 感知优势，需要相应证据；当前数据不支持这些更强结论。

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

## 40-slot 确认性端点分析与执行偏离

原始输入来自 GitHub commit `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` 的四个 CSV。行级输入与 assignment、对象 UID、左右方法映射 **960/960 对齐**；40 个槽位均出现于导出，按表内完整性和理解检查保留 37 人（排除 2 个理解检查失败、1 个未完成/缺答），覆盖 24 个对象与 LLH 对 GFL、GFH、GC3、generic linear 的 8 个“比较×问题”端点。每端点有 222 次判断。分析不把 222 次判断当作独立样本：先在对象内计分、对象等权；平局记 0.5；对参与者和对象双向 bootstrap 10,000 次、固定 seed 20261005，使用逐端点 95% CI 和冻结的双侧 bootstrap tail rule；8 个端点统一做 Holm 校正。

所有八个点估计都高于 0.5，但**没有任何端点通过 Holm 校正**。外观保真估计范围为 0.540–0.591；纹理自然度为 0.539–0.647。两个较低的未校正 p 值出现在 LLH 对 GFL 的纹理自然度（0.647，CI [0.528, 0.755]，raw p=0.0123，Holm p=0.0984）和 LLH 对 GC3 的纹理自然度（0.632，CI [0.521, 0.741]，raw p=0.0183，Holm p=0.1281），均未过家族校正。LLH 对 generic linear 的外观端点为 0.540 [0.412, 0.667]，纹理端点为 0.539 [0.420, 0.653]；这既没有检测到有利偏好，也**不构成等效或非劣证据**。

执行偏离必须随结果说明：上传的 40 个任务表与冻结包的 assignment schedule 匹配数为 0/40；96/96 个对象×比较单元在参与者之间采用固定左右次序；导出没有随机种子、题序、理解检查原始答案或 stimulus alias 到冻结 PNG hash 的对应表；coordinator closeout 表仍为 pending。该研究仍按预先指定的端点家族作确认性分析；这些事实界定可解释范围和协议符合性，不会把已完成研究追溯改称敏感性分析，也不改变观测到的答卷结果。参与者级治理和图像权利仍须在公开发布/投稿门禁单独处理。

当前权威八端点表、森林图、源 hash 和分析脚本：

- [确认性端点统计表](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_CONFIRMATORY_ENDPOINT_RESULTS_20261007.csv)
- [确认性森林图](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_CONFIRMATORY_FORESTPLOT_20261007.png)
- [当前端点复算 provenance](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_CONFIRMATORY_PROVENANCE_20261007.json)
- [可复算脚本](/4T/CXY/MV-Painter/1006/evidence/human_study/analyze_confirmatory_human_study_20261007.py)
- [冻结分配偏离审计（含私钥哈希）](/4T/CXY/MV-Painter/1006/evidence/human_study/HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json)
- [确认性数据权威门禁](/4T/CXY/MV-Painter/1006/gates/HUMAN_STUDY_GATE_VERDICT_20261007.md)

## 当前允许的结果表述

正文保留旧研究，但限定对象和结论：

> “In the original 24-participant, 30-object 3AFC study, C3 received 58.1% of overall-quality choices (95% participant-and-object cluster-bootstrap CI [50.1%, 65.8%]). The two uniform-scale baselines led on texture naturalness and shape consistency, respectively. This study supports a perceptually preferred balance among the three original conditions; it does not establish universal perceptual superiority or validate the later LLH profile.”

40-slot 结果按确认性端点分析报告，同时披露执行偏离：

> “The prespecified confirmatory human-preference analysis included 37 valid participants evaluating 24 objects across four LLH comparisons and two separate questions. All eight equal-object point estimates favored LLH descriptively, but none survived the prespecified Holm correction. The response export did not reproduce the frozen per-slot assignment schedules, side order was fixed within object-by-comparison cells, and stimulus hashes could not be independently verified. We therefore report the planned endpoint family as confirmatory with documented execution deviations; it supports no adjusted LLH preference advantage, equivalence, non-inferiority, or absolute reference-fidelity claim.”

不要把“确认性”误写成“完全遵循锁定协议”；不要将旧 C3 3AFC 写成对 LLH 的验证；不要将任一 2D 研究当作未见视角、mesh、UV seam 或完整材质 fidelity 的证明。
