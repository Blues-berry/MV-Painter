# 01549 第一轮修订 → 当前第二轮意见 → 1008 补充动作

## 历史基准与轮次

作者已确认：01549 是在第一轮审稿意见后完成修订、于 2026-09-07 正式提交的论文版本；本轮 Reviewer 1/2/3 是针对该版本的第二轮意见；1008 是第二轮修订。不得将 01549 称为初始投稿。

历史基准取自 0907 正式投稿包：Manuscript、Marked-up Manuscript、Response Letter、Supplement 和 latex.zip。包内回复信记载，此次提交回应上一投稿 CAG-D-26-00954；正式论文材料标为 CAG-S-26-01549。当前审稿文本文件名/导出页眉中的 “Initial submission” 不改变作者确认的轮次。审稿映射以 0907 回复信中的第一轮要求和完成事项，以及当前 CAG-D-26-00962 的第二轮 R1/R2/R3 意见为依据。

01549 的权威 TeX 为 final/submission_new_0907/latex.zip 内 final_0903.tex，与已认证的 source_01549/final_0903.tex 字节一致。历史 v1/v2 实验身份如实保留：01549 主表记录 v1 主 adapter；Section 4.7 与 FAC 使用 1,706-object strong-residual、per-layer-capped v2 adapter。

## 三层映射

| 第一轮要求 | 01549 第一轮已完成并提交的修改 | 当前第二轮意见 | 1008 补充动作 |
|---|---|---|---|
| R1：澄清训练/评测拆分、probe/holdout 重叠及 FAC 训练和评估；补全实现细节。 | 0907 回复信记录主 adapter 1,118 训练对象、Section 4.7/FAC 的独立 1,706-object adapter、300-object evaluation、24-object probe 与严格 disjoint 276-object holdout；补充 FAC 参数量、loss、optimizer、步数和 paired negative re-examination。 | 当前 R1.5 再问 FAC 可复现性并鼓励发布代码；R2 肯定 FAC 受控复查与实验严谨性。 | 保留 FAC 负结果和 01549 所报完整协议/剂量响应；披露本地恢复配置清单为 1,200 对正文所报 1,706 的归档冲突及缺失 run-bound seed/output manifest。说明这是已报告的第一轮结果，不伪称 1008 新复跑；不声称代码已公开。 |
| R1：补充具体 checkpoint、condition、resolution、scheduler、seed、metric 实现。 | 01549 增加 Implementation and Dataset Details 及补充复现表；第一轮回复逐项列出 pipeline、六视图、50 steps、seed、checkpoint 和 metric。 | 当前 R1.2 指出 Table 9 改用另一 adapter，要求同一 held-out protocol；R2 明确肯定此前 disjoint holdout 的严谨性。 | Fresh C N=300 独立于原 24-object probe。Fresh C 主 run 与同 cohort Generic Linear/LLH addendum 使用同一冻结 checkpoint、runner source、输入、metric、seed policy；配对主结果为 C3−GFL FG-PSNR +0.522352 dB，95% CI [+0.404160,+0.640669]。不设 Fresh C 必须与 01549 Table 4 checkpoint hash 相同的门禁。保留 v1/v2 历史差异，并说明 Fresh C 不是旧 +0.96 dB 数值的重现。 |
| R1/R3：处理偏好决策的 participant/object 聚类；写清实验设计、随机化和 paired/bootstrap 统计。 | 01549 报告 30 objects、24 participants、每指标 720 票，采用 participant/object 两层 bootstrap；C3 overall preference 58.1%，95% CI [50.1%,65.8%]。 | 当前 R1.3 要区分 texture variation 和 fidelity；R1.4 反对用跨零 CI 声称 equivalence/non-inferiority；R2 认可 cluster-aware 分析。 | 保留 01549 的聚类偏好结果和设计，但把它限定为三条件主观选择，不解释为 texture fidelity、Fresh C 结果或 3D 质量；Fresh C 的 Edge-SSIM trade-off 单独报告，不提出非劣效结论。 |
| R2：解释 adapter-dependent failure modes；R3：在线性 warm-up/cosine 等 schedule 上补充独立 holdout 结果。 | 01549 增加 adapter-dependence Section 4.7，并在 probe-disjoint 276 上报告 trapezoid、Gaussian peak、linear warm-up、cosine bump 对照。当前 R2 特别肯定这些 holdout 比较及其谨慎实验设计。 | 当前 R2.3 指出同架构内换 adapter 不等于跨 backbone；当前 R3 给出肯定评价，无新技术任务。 | 保留 Section 4.7 和第一轮 276-object schedule-transfer 表（移至 Supplement，仍明确其 v2 adapter 身份）；另外报告已有 MV-Adapter 与 MVDiffusion 跨接口实验及其样本数、统计结果、接口限制。不将其描述成统一接口下的 matched transfer，也不宣称普遍泛化。 |
| R2：阐明 C3 的时间调度参数和 CAI 阶段效用推导。 | 01549 新增 CAI 命题/证明及 C3 选择论证；该版本同时保留 TCAS 三阶段公式和 C3=(1.25,2.50,1.25)。 | 当前 R2.1 质疑 TCAS 超越现有 adapter schedule 的方法创新；R2.2 指出 CAI 可能只是对已选 schedule 的事后形式化。 | 加强 TCAS 在既有 GeoTex residual path 上的任务特定贡献与执行语义，正面讨论 SSI；保留 TCAS 方程、C3 和开发记录。只撤回 CAI 的独立推导、唯一最优与 selector 声称，不牵连有效的 TCAS 方法主体。 |
| 第一轮编辑要求：更新已发表版本引用、修正错误引用并补充 graphics 文献。 | 0907 回复信逐项记载 reference list 核对、发表版本替换及 C&G/TVCG/CGF 等新文献。 | 当前第二轮没有要求撤销这些修改。 | 原样保留已完成的引用和 related-work 修改；不因创新性重审而删掉第一轮文献修订。 |

## R1.2 Fresh C 口径冻结

- Fresh C 的 R1.2 证据单位为对象，N=300；UID 与 01549 原 24-object probe、原 300 evaluation、原训练列表及 clean-v2 evaluation 均不重叠。
- 主四条件为 No Adapter、GFL、GFH、C3（1,200/1,200 行）；Generic Linear/LLH 是相同 300-object cohort 上的 addendum（600/600 行），不是独立队列。
- 冻结 checkpoint SHA-256：0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0；runner source SHA-256：e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3。
- 对各条件共享输入、metric implementation、目标视图和 seed policy；object seed 为 42 + object_idx。同一对象的配对条件共享该 seed 和初始 latent。
- scale cap 以 Fresh C 实测语义报告：deep 3.0、middle 3.5、shallow 0.8；requested scale、applied scale、residual correction 不混为一谈。C3 的 shallow request 1.25 实际被 cap 到 0.8。
- 主 endpoint 结果原样保留：C3−GFL FG-PSNR = +0.522352 dB，95% CI [+0.404160,+0.640669]。GFH、Generic Linear、LLH 的负结果与 endpoint trade-off 均继续列出。
- 不要求 Fresh C 的 checkpoint hash 等同于 01549 历史 Table 4。旧版 v1/v2 checkpoint 差异是历史事实，仍独立陈述；不把它扩大成 Fresh C 配对结果的阻塞项。

## Reviewer 状态与执行

- 当前 R1.2：以 Fresh C 的同 checkpoint、同 runner、同 cohort/输入/seed/metric 配对证据作答；旧 Table 4 的 +0.96 dB 不声称被数值重现。
- 当前 R2.1：保留并强化 TCAS 方法主体；创新充分性仍是编辑判断，不夸大为通用 schedule 算法。
- 当前 R2.2：移除 CAI 无效推导和最优性，不删除 TCAS/C3。
- 当前 R2.3：报告已有跨 backbone/interface 试验和界限；不把同架构 adapter 变化当成 cross-backbone。
- 当前 R3：正面感谢；无新技术修改或实验要求。

本文件取代此前把 01549 当作初始投稿、把 CAG-D-26-00962 轮次映射标为开放、或把 Fresh C 必须复现 Table 4 checkpoint hash 作为 R1.2 阻塞项的分析口径。它不修改 01549 原始材料。
