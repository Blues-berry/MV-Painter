# C&G 01549 下一轮修订计划

制定日期：2026-09-29。性质：基于实际论文、审稿文本、原交接文档与当前产物的执行计划；本文件不表示下列待办已经执行，也不授权投稿或公开发布。

## 目标与当前判断

下一轮目标是形成正文、补充材料、回复信、图表和复现包相互一致的可审阅修订版本。上一轮完成的是实验执行与阶段性放行；“实验完成”不等于原方法主张得到支持，也不等于科学问题只剩排版。

保留 TCAS 的推理时分阶段残差控制方法及其可检验的实证贡献，但不能预先承诺“机制研究”这个定位足以解决 Reviewer 2 的创新性质疑。阶段干预对输出的影响有证据；“中段几何对齐、末段纹理干扰”的内部因果解释仍需区别于观察结果。现有 LLH、fixed-low 和 MV-Adapter 反例必须影响摘要与贡献措辞。

本轮先完成 CPU/静态证据收尾，再编辑论文；GPU 队列暂不新增任务。C 可继续结构、协议及已核准事实的草稿编辑；涉及比较优劣和因果机制的最终表述须通过下述 E0/E1。

## 本次审阅确认的具体风险

1. `final_round2.tex` 的旧摘要被 `\iffalse` 屏蔽，不能把其中的 +0.96 dB 误报为当前可见摘要；但正文旧主表仍列出 17.90/18.86 dB 等旧值，设置段仍引用缺失的原始 v1 checkpoint，正文还声称中段在所有被测 regime 最优。活跃摘要中的“calibration framework”也要与 CAI 未定义结果对齐。
2. A-2 的 Full-SSIM 已有 PNG/raw-GT 后处理，其余指标主要来自 pre-save float-eval。混合来源必须显式标记；不得将它们包装为统一 PNG 全量复算。需要核验其他 SSIM/PSNR 受 dtype 与序列化影响的范围。
3. LLH 优势不限于 serialized Full-SSIM。现有 pre-save 表中，LHL 相对 LLH 的 Full PSNR 为 -0.26810 dB，FG PSNR 为 -0.17708 dB，Edge-SSIM 为 -0.03530，其余核心指标方向也偏向 LLH（LPIPS 按低者优定义）。尚不能据此宣称对所有纹理目标均占优；但必须检查“LHL 最佳平衡”的依据。
4. 50 步分段为 early/mid/late=17/16/17。LHL 的逐步平均 scale=1.650，HLL/LLH=1.675，fixed-mean=5/3。三段参数的算术均值一致，实际采样步平均不一致，实际 residual 能量更不等同。这个差异不能单凭大小认定足以解释结果，也不能忽略。
5. 12-object trace 脚本的 `C_full_ssim` 使用 `gt_reload`，A/B 使用原始 `gt_cpu`；它与最终 PNG prediction/raw-GT 定义并不完全相同。应使用已保存 tensor 做固定 GT 的分解，不能把两侧输入同时变化全部归因于 prediction PNG 量化。
6. 自动验收检查了记录与指标的基本完整性，但尚需 records、flat_rows、各 CSV、PNG、source UID 的交叉一致性及哈希冻结。276 个 atomic JSON 各含四条件，不能写成 1104 个独立 atomic 文件。
7. 回复信仍有旧阻塞、五视角 bake、DISTS、未接触 holdout 等表述；实际 bake 使用六 source views，DISTS 缺失，follow-up 已见过 clean-v2 结果。复现包仍标记 mixed geometry/缺失十个 GLB。协调状态和部分占位表也有滞后。
8. 旧 FAC、人类偏好、CLIP-IQA、17-variant sweep 的 cohort/checkpoint/图像版本需逐项追溯。不能因 clean-v2 已通过就把旧实验自动迁移为其证据。

## 阶段与验收门槛

| 阶段 | 负责人 / 资源 | 工作与输出 | 唯一放行条件 |
|---|---|---|---|
| E0-A：统一数值与溯源 | A + E，CPU | 七条件主表；全指标 paired 结果；实际 schedule 预算表；records/CSV/PNG/hash 对照；固定 GT 的 SSIM 分解 | 276 个 UID × 每个适用条件精确配对；来源与缺项明确；不存在静默拼表；不依赖有利方向选择指标 |
| E0-D：实用性证据 | D，CPU / 现有渲染 | 12-object 四条件完整 3D 指标表；完整物体与 unseen-view 展示；可播放视频；seam/coverage 有效性说明 | 48 个对象-条件与 528 个视角可追溯；六 source/十一 unseen 映射核准；案例选择和缺失指标披露 |
| E0-B：跨骨干封存 | B，CPU | 76-object 11 方法证据包；八组 LHL 比较；CAI 与 scale-family 说明 | 低者优指标方向正确；high=1.50/1.00 分开；明确 undefined 及预训练 UID 限制 |
| E0-P：旧证据与复现 | E / C，静态 | 旧主表、FAC、偏好研究、CLIP-IQA、补充材料和 release 的逐项证据索引 | 每项标注可保留/历史独立协议/不可核验；任何新主张有具体产物支持 |
| E1：贡献与表格冻结 | E，CPU | 全指标权衡表、审稿问题—证据映射、最终 C 改稿说明 | 正面贡献与反例同时呈现；方法贡献和实用性缺口均有明确处理；不得把完成实验等同于回应成功 |
| C1：论文整合 | C，文稿 | 正文、补充、回复信及自动生成表格 | 引用 E1 数字，整体协议一致；无旧 checkpoint、虚假盲测、普适中段最优或未完成实验承诺 |
| E2：交付验收 | E，静态 / 编译 | 编译稿、差异清单、逐项回复、复现包检查报告 | 所有数字可追溯；无未解释占位；图/视频可访问；无数据集或模型暗改；投稿需另行决定 |

E0-A、E0-D、E0-B、E0-P 可并行，写入各自新增输出目录；由 E 单独维护四份协调总表。C 单独编辑论文文件，避免多人并发覆盖。已有独立会话不可直接调度时，由本协调线程承担对应工作，或分派边界明确的子任务，不创建重复实验。

## E0-A：最先执行的数值闭环

- 主表覆盖 no-adapter、fixed-low、fixed-high、fixed-mean、HLL、LHL、LLH。先核验 no-adapter 的代码语义，不能未经核实称其为原版完整 MVPainter。
- 检查原 clean-v2 C3 与 A-2 C3 的重复条件是否同配置、同对象、同 PNG/数值；不相等时查明差异，分别标注批次，不能把不同批次当作一个统一结果。
- 对已有 PNG 与原始 GT 采用预先冻结的 CPU 评价路径；优先补齐 Full/FG PSNR、Full/FG SSIM、Edge-SSIM。LPIPS 若沿用原值，必须独立标注为 pre-save，不能称“全部 PNG recomputed”；需要统一表时对全部条件同样执行 CPU LPIPS，并先做小规模耗时估计。
- 汇总现成 prediction/GT 的 RGB、梯度、Laplacian 统计，按已有冻结定义生成 GT-relative error；评价的是统计匹配，不能单独等同于忠实纹理。先检查定义/epsilon/对象覆盖，避免仅选有利指标。
- 对 C3 vs low/high/mean/HLL/LLH 使用对象级配对均值、95% CI、方向明确的 win rate。保留 seed=20260928、10000 次 bootstrap；分别列 raw delta 与 improvement，避免 LPIPS 符号误读。
- 全面展示多指标比较，不新增事后综合分数选 winner；主要比较与探索性多重比较明确区分。对象 bootstrap 只反映该固定 checkpoint/生成 seed 下的对象差异，不能声称跨 seed 或跨训练重复稳定性。
- 固定 GT 做 saved A/B/C tensor 的 SSIM 对照，分离 prediction dtype、PNG 量化以及 GT reload 的影响；此步骤不需要模型重跑。
- 报告 17/16/17 分段、逐步 scale 总和/平方和，以及实际 residual L2/RMS 分阶段统计。日志能支持有效强度差异的描述，但仅靠 norm 不能证明 residual 的方向对齐或内部因果机制。
- 独立核对 records.rows / flat_rows / per-method CSV / combined CSV；检查所有数值列的 finite 状态与允许缺失项，而非只校验七个指标。记录输入 PNG、manifest、脚本和导出表 SHA-256。

## E0-D：将已经生成的 3D 产物转化成审稿证据

对 12 个对象保留四方法完整展示，主文给出预先定义的代表性子集，补充材料提供全部对象及失败案例。原 cohort 按 C3-vs-high 分层选出；不可改称随机样本或残差 quartile 抽样。

既有 unseen rows 先在每个对象内对 11 视角聚合，再做方法间配对；不能以 528 为独立样本数。若给 CI，必须注明其只描述已选案例集，不能外推 276 个对象。

核验 uv_seam_discontinuity 的零值是没有可评价边、退化定义还是实际低误差；报告参与统计的 seam 数/长度、coverage 的分母、原始和填补后覆盖率。缺测用 NA，不能用 0 替代。将两个对象 GT-to-GT sanity 与 12-object generated bake 分开。

R1 指出的紫色色偏、重复纹理、reference 不一致需在完整物体和相同 unseen camera 下展示。仅文件存在不足以回应实际质量。现有图片可生成视频和定性版面；先验证播放器、相机、曝光/色彩处理一致，不增跑 bake。

## E1：如何保留清晰贡献

推荐保留 TCAS 为一个具体、低成本的推理时阶段控制方法，把贡献写成：控制变量明确的阶段干预、与强竞争固定尺度的全指标比较、跨骨干差异及真实 bake 的适用边界。SSIM 审计是可信度修复，不宜充当主要方法创新。

必须回答两个问题：

1. 相对 fixed-low / fixed-mean，TCAS 在什么明确指标或用途上提供可验证收益，代价是什么？
2. 对 LLH 的全指标比较是否存在可支持 LHL 的纹理忠实度或实际 3D 权衡？如果没有，应承认当前 C3 不具最佳性能依据；不能临时改用 LLH 并称它由 CAI 预测。

若只有“阶段位置影响输出”的证据，Reviewer 2 的创新性担忧仍未充分解决。最终稿可以如实呈现有方法实现和受控证据的实证研究，但不能保证该定位足够录用，也不能用“适配器相关”替代对反例的解释。

CAI 保留为经验分析/诊断，并完整说明 set-valued/undefined 结果。不得宣称已验证可迁移的唯一选择算法。中段功能对齐/末段纹理竞争使用假设性语言，除非另有直接证据。

## C1：按章节改稿顺序

1. 先改实验设置与数据来源：controlled retraining 的真实路径/hash、1118 train 与 clean-v2、199/101 来源分层、unique6/reversal、主干各自 seed/resolution、实际评价是 panel 还是逐视角均值。
2. 再改 Results：主表以 strict-276 为主；pooled-300 为补充；阶段位置、第二骨干、真实 baking 三组证据分别展示。旧数值移除或作为明确隔离的历史协议记录，不能混入新主表。
3. Method：保留分段残差控制公式与实现，准确描述离散步边界、名义均值和实际预算。CAI 推导/最优性承诺与 undefined 结果保持一致。
4. Figures / supplement：完整物体、competitive low、LLH 反例、unseen bake、全部 12 案例、来源分层与配对统计。图注把纹理 variation 与 fidelity 分开。
5. 审核旧用户研究与 FAC：参与者原始记录、展示图像、checkpoint、训练 UID、评估脚本不能核验的结果不用于 clean-v2 新主张；旧数据可核验则作为单独历史协议证据。FAC 负结果不能推导“加 envelope 约束就会成功”。补齐 FAC 复现配置/命令而不追加训练。
6. 最后改 Introduction / Abstract / Discussion / Conclusion：依据冻结的多指标结论重写贡献，不提前承诺 LHL 最优、结构保持或纹理忠实度普遍提升。
7. 逐条重写回复信：每条 reviewer concern 对应修改位置、真实结果和限制。纠正五 source views、DISTS、未部署 B、旧 checkpoint 恢复中、holdout untouched 等旧文字。
8. 同步复现包：移除 mixed-proxy/缺失十个 GLB 等过时说明；统一 manifest、版本、hash、模型来源、依赖、CSV→表格命令。先完成本地可复核包，公开发布和投稿不在本计划自动执行范围。

## GPU、扩展实验及自动运行规则

- 默认 GPU 新任务数为零。优先通过现有 tensors、PNG、records、GLB 和 renders 解决上述问题。
- 只有当稿件确实要保留“严格等步数预算下的位置效应”或“跨随机种子稳定”等更强结论、且 CPU 审核无法回答时，才另列最小实验方案。届时预先冻结问题、cohort、尺度和验收条件，限定为 follow-up，不做大规模调参。当前不启动该实验，也不修改已运行的尺度定义。
- 大规模 3D bake、多 checkpoint 重训、新 CAI tie-break、全新 backbone 均不属于当前默认队列。
- 长任务继续使用独立进程、run_id/PID/日志、status/final manifest/DONE/FAILED；完成事件或明确绝对时间仅检查一次，未完成就写明下一次检查时间并结束当轮。训练窗口无模型轮询。
- 不把 ready marker 写出等同于已唤醒 C；使用实际可用的调度接口，缺少接口时保持可恢复任务文件并如实报告。上一轮已结束的 ETA dispatcher 不再轮询。

## 本轮交付标准

一套可供作者审阅的正文与补充 PDF、逐条回复信、可追溯图表/视频、复现包与 E 的最终核验记录。方法的有效范围、未成功的主张、实验限制均与数据一致。论文接收与投稿授权是另外的决定，不能由 PASS_WITH_LIMITATIONS 推定。

立即执行的下一任务：E0-A 的跨文件一致性、离散预算和统一评价口径核验；E0-D/E0-B/E0-P 可并行准备。完成后由 E1 触发 C1，避免在核心数值仍需核验时反复改摘要。

## 2026-09-29 execution override

上述“默认 GPU 新任务数为零”是上一轮风险控制建议，已被作者本轮明确
覆盖。当前按两周窗口执行：允许一次有限、预注册的 TRB 修正 pilot，
先运行 24-object development，再依据停止条件决定是否锁定 holdout；旧稿、
旧结果和独立实验分支全部保留。pilot 不得替代 clean-v2 主证据，也不得
在控制协议通过前承担论文结论。

## Provenance handling adjustment — 2026-09-29

按作者对 CAG-S-26-01549 返修方式的要求，旧数据集、旧脚本和本地缺失
文件的问题只记录，不再反复阻塞返修。新增实验只需保证新增比较本身的
条件、对象、随机因素、指标和输出可追溯；只有会改变新增比较解释的缺陷
才需要暂停。后续优先推进方法证据、跨骨干增量证据和审稿意见对应的表述
修改，不再重新审计所有已经由多方验证的历史结论。
