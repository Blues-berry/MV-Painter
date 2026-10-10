# 下一阶段计划的论文视角评审与衔接建议

日期：2026-10-06  
用途：为正在执行的下一阶段计划提供论文论证层面的评审；不替代实验协议，也不修改执行计划。

## 一、判断摘要

计划的技术门槛总体严谨：固定条件、不按结果搜索、不把生成完成当成科学结论、保留负结果，并清楚限制 E1、E2、E3、E5 各自能够支持的推断。E5 目前只作为开发可行性诊断，也与“先收窄机制主张，不为显著性追加大实验”的路线一致。

需要调整的是论文证据的优先级和结果解释边界。用户提供的分析把 **唯一证据 authority、原始 C3 的 held-out 回答、已有 MVDiffusion 结果、人评 gate** 放在新 GPU 工作之前。计划虽然把 E0 标为 P0，但实际执行顺序先做 E1、再做 E2，且 E0 目前没有把这些 reviewer-specific 闭合项明确列成启动门槛。E1/E2 不是 schedule 搜索；它们可以回答预先限定的问题，但不能替代已有证据的重核，也不能自动解决论文创新性问题。

建议将当前论文定位为：

> 本文实证分析几何条件多视角扩散中 adapter scaling 如何把控制信号分配到网络深度和去噪时间。名义 scale 不足以描述实际干预；观测到的响应取决于 cap 与 residual dose、对象属性及 conditioning interface。研究中的配置是受控测试 profile，不是普适最优 schedule。

如果 E1/E2 后续支持更强的 depth-versus-time 区分，再把“深度分配的影响较稳定、时间分配的增益较小且异质”写成主结果；在这些结果完成并通过证据核查前，不把候选叙事写成已冻结结论。

## 二、证据应支持的主张边界

| 主题 | 可保留的科学问题 | 论文中应守住的边界 |
|---|---|---|
| 名义 scale 与实际干预 | cap、注入位置和 wrapper 语义如何改变有效 residual allocation？ | 报告 effective trace 和 implementation semantics；不要只按配置标签解释效果。 |
| 深度分配 | 指定的深浅配置是否改变结果？ | E2 将 deep/middle 联动，不能分离 deep 与 middle 各自效应；未匹配总实际剂量时，不能称为剂量之外的纯深度机制。 |
| 时间分配 | LLH 与 exact layer-mean 对照的额外收益多大、对象间如何变化？ | 统计可检测不等于实际收益大；Fresh B 的数值、CI 和冻结的 ±0.5 dB 实用界值须由唯一 authority 复核。 |
| Layer×Time | layer response 是否随 window 改变？ | A3b 的跨层共同 dose support 为 0/2250 时，剂量调整模型只能称参数化敏感性分析；不能写成已识别的 dose-independent interaction。 |
| 对象适用边界 | 哪些对象上的收益变弱或反向？ | 报告预先定义的分层、对象级区间和负向对象；不从结果中挑对象或重定义复杂度边界。 |
| 跨骨干 | 已测响应能否迁移到不同 conditioning interface？ | MV-Adapter 与 MVDiffusion 分开报告。现有 MVDiffusion 是负/混合边界证据，不证明 architecture causes the difference，也不证明所有异构骨干都不迁移。 |
| 3D 实用价值 | 二维差异是否对应当前 GLB 的未见视角表现？ | 保留 N=20、同对象配对和各指标 trade-off；不得将 LPIPS 单项改善改写成全面 3D texture fidelity。 |
| 人类感知 | 当前 LLH 是否有受试者偏好支持？ | 按冻结的 40 slot / 至少 36 valid 规则一次性分析；答卷未齐前保持 open，不做中途偏好判断。 |
| CAI 与分段 | CAI 能否预测阶段效用？三等分是否是自然阶段？ | 无前瞻预测证据时仅作描述性框架或移入补充；等三分是控制比较的离散化，不是发现的 phase boundary。 |

## 三、按 reviewer concern 排列的近期工作

### P0：建立唯一证据 authority

E0 应交付唯一的机器可读 claim ledger，并先完成历史结果的 authority 分类，再解释新结果。每项至少记录：claim、论文位置、comparison、cohort、对象数、seed、selection/registration 状态、实际 scale/cap、估计量与 CI、multiplicity family、artifact/source hash、当前 disposition、允许的论文措辞，以及被取代的历史措辞。

建议明确区分：

- **当前权威证据**：strict-276 Core-7 对 C3、GFL、GFH 的同协议比较；Fresh B150 的 LLH−LFM-EXACT；GLB-native N=20；MV-Adapter；MVDiffusion；锁定人评完成后的结果。
- **发现或开发证据**：A2/A3/A3b 中未预注册或用于开发的部分；其边界和用途按 protocol audit 标明。
- **历史背景或已被收窄的证据**：pooled-300 的旧 0.96 dB、Fresh300 的 +0.434 dB、旧 “STRONG temporal” 措辞等。若 Fresh B150 是最终 temporal authority，历史结果须明确标记为不能支撑当前主张，不能只靠顶部 overlay 让读者自行辨认。
- **跨 cohort 不可互换项**：旧 C3、strict-276 C3、Fresh300、Fresh B150、LLH 与 C3、二维与 GLB 结果分别建行；不得用一个 cohort 的平均值替另一 cohort 作对照。

**先完成现有材料的来源重核，再决定 E1/E2 是否会改变一项明确的稿件主张。** 已进行中的纯技术预检无需因此回滚；任何正式分析仍须等完整性 gate 通过，并遵守已冻结的比较与统计规则。

### R1：把 C3 held-out 和 fidelity 问题拆开处理

只读复算得到 strict-276 Core-7 的 GC3−GFL FG-PSNR **+1.207771 dB**，对象级名义 bootstrap 95% CI **[+1.116967,+1.294989]**，GC3 胜 259/276；七个 endpoint 的有利方向都对 GC3。GC3−GFH 则是 trade-off：FG-PSNR **−1.214235 dB**，但 Full-PSNR **+0.725229 dB**、Full-SSIM **+0.001229**；GFH 在其余五个 endpoint 更好。CI 为未作多重比较校正的区间。

这组结果适合作为**同协议补充重评价证据**，仍建议 R1.2 保留 `CLOSED_BY_CLAIM_REDUCTION`：strict-276 在修订期间已反复查看，Core-7 预注册比较未把 GC3−GFL / GC3−GFH 列为主要对比，且旧 GFL/GC3 条件缺少完整 276 对象输入 tensor-hash 链。三条件对象清单、checkpoint 和执行协议一致，但不能称为新的独立 confirmation，也不能称作旧 +0.96 dB 的复现。R1.2 的独立 held-out 回答须由真正新 cohort 的注册比较支持；strict-276 数字可用于解释当前 C3 的 endpoint trade-off。不能用 LLH 替代原来的 C3，也不能写成 C3 uniformly dominates aggressive fixed-high。

**对所附分析的一项事实校正：**分析文本称 strict-276 是“同 runner、同 realization”。当前可核对的 manifest 不支持这两个更强的说法：三组 CSV 的 runner 哈希不同；旧 GFL/GC3 也没有覆盖完整 276 对象的输入 tensor-hash 链。它们共用对象映射、checkpoint 与记录的协议版本，足以做逐对象的同 cohort 补充比较，但不能据此断言逐次生成输入完全相同。故建议把 strict-276 用作正面报告 C3 的补充复评，并同时披露比较未列入 Core-7 预注册主要对比；不要把 R1.2 改成“新独立 held-out 已确认”。

R1.1/R1.3 仍由另一组证据处理：GLB-native N=20 是 metric-dependent，视觉审计指出存在 material/color mismatch 与细节损失，人评尚未完成。因此 3D 文字应逐 endpoint 报告；人评结果只支持其预设比较、题目与样本范围内的判断。

### R2：让创新性和跨骨干证据进入同一论证链

当前 closure matrix 将 R2.3 的依据主要写成 MV-Adapter。应把已有 MVDiffusion 作为另一种 interface boundary 纳入证据树：主 backbone 是 positive characterization；MV-Adapter 是 partial/bounded response；MVDiffusion 是 substantially different conditioning interface 上的 negative/mixed result。三个结果只在 backbone 内比较，不汇总绝对指标，也不作 architecture-causal 解释。

还发现一篇当前稿未引用的直接相关先行工作：Kulkarni 的 *Scheduled Style Injection* 已被 arXiv 标记为接受至 CVPR NTIRE 2026。它在 training-free diffusion 中分别沿 decoder depth 和 denoising timestep 调整 StyleID 的注入参数，并在两个轴上测试 ControlNet depth-conditioning scale；代码也暴露 per-layer ControlNet scales at the first and last timestep。其任务是单图 style transfer，不是多视角 3D texturing；其 ControlNet schedule 结果很小（层/时间方向差约 0.009–0.153 ArtFID，schedule-shape 差在 ±0.020 ArtFID 内），而主要收益来自 StyleID 的 attention-mixing gamma schedule。它没有本稿的 GeoTex adapter cap/dose 记账、strict-276 3D object study 或 GLB evaluation，但足以否定“首次提出 layer×time 条件强度调度”或将训练-free/低开销本身作为核心新颖性。引用并比较该工作后，方法 novelty 应限定为**几何条件多视角 3D 纹理中、对实际 residual/cap 语义与对象/接口边界的系统实证辨析**；不能再把二维调度参数化本身包装成全新方法。

这能正面回应“是否在真正不同骨干上测过”这一问题，但不能单靠负结果消除 R2.1 的 novelty concern。E7 文献审计需要逐篇核对已引用的一手论文、实现和附录中的 scale/depth/time control、cap 语义、dose handling 与失败边界；若贡献仍被判断为 empirical characterization 而非新算法，应如实记录期刊适配风险。

**当前稿的直接改稿点（证据冻结后处理）：** `final_round2.tex` 的引言第 59 行和相关工作第 97 行把现有工作概括成没有处理所需的 layer/depth × timestep 条件强度分配；但 *Scheduled Style Injection* 已分别改变 decoder 层和去噪步上的 StyleID 参数，也测试了 ControlNet depth-conditioning scale 在两轴上的调度。稿件应承认这个控制维度已有先例，再明确区分问题和实施：前作针对单图风格迁移，StyleID 改的是注意力混合参数，ControlNet 深度信号的调度效果在其附录中很小；本文研究几何条件多视角 3D 纹理里的 adapter residual、cap/实现语义、对象异质性与跨接口边界。现稿 `Related Work` 未检出该论文引用，故 R2.1 不能只靠 cross-backbone 结果关闭，须在引用比较后重新评估贡献是否足以支撑目标期刊。

CAI 不应承担创新性或 schedule 推导的论证负担。C3 是原 TCAS profile，LLH 是本轮研究的另一种 allocation profile；它们各自对应自己的比较和 cohort，不要合并成同一个“方法身份”。

## 四、E1–E5 的论文解释规则

| 工作包 | 结果可增加的证据 | 不能据此声称 |
|---|---|---|
| E1 多生成 seed | 固定 48 个、已见过 B 的对象中，generation realization 稳定性或不稳定性。 | 新的 untouched-object confirmation，或 reference/object sampling 稳定性。 |
| E2 静态 2×2 | 四个指定静态配置在冻结 runner/cohort 下的因子效应和 interaction。 | 独立 deep 与 middle 效应、实际 dose 匹配、剂量之外的深度机制，或新的最优配置。 |
| E3 GLB | 当前 N=20 生成物在指定 UV、相机、base-color 与 sampler 评估范围内的 endpoint 结果。 | Full-PBR、全对象覆盖、全面 3D fidelity 胜利；工具未通过合成 seam audit 时也不能保留旧 seam 改善数字。 |
| E4 人评 | 冻结的人评问题、配对与人群下的外观保真/自然度偏好。 | GLB seam、unseen-view consistency 或剂量机制结论。 |
| E5 开发可行性 | 实际 δr/hidden 相对幅度能否被数值稳定地控制与记录。 | 图像质量效应或机制验证。没有 untouched cohort、共同支持和清晰稿件必要性时，不启动正式 2400 object-condition campaign。 |

若 E1/E2 尚未正式启动，只有在 E0 已为其指定一项仍未回答的论文问题后才进入正式生成。若已按冻结协议启动，则完成技术 gate 后照协议报告，不因中途趋势更改条件、统计或论文终点。

## 五、建议的论文组织

1. **问题重述**：多视角几何条件下，scale 是如何实际控制 adapter residual 的；单个全局标量为什么不足以描述不同注入点与时间窗口。
2. **可复现的控制定义**：明确 wrapper、cap、有效尺度 trace、参照和实际 residual 记录；把 C3 与 LLH 作为不同 profile 定义。
3. **受控归因结果**：先报 global/depth allocation，再报 exact layer-mean 下的额外 temporal contrast；区分估计精度、实际效应大小和实际 dose 支持。
4. **适用边界**：对象复杂度与失败/反向对象；避免只展示总体均值。
5. **跨骨干边界**：primary、MV-Adapter、MVDiffusion 分层呈现，并明确哪些接口相似、哪些不同。
6. **实际质量证据**：GLB-native 多指标结果与人评分开呈现；视觉变化、metric fidelity 和 human preference 不互相代替。
7. **讨论与限制**：CAI 描述性降级；没有普适 LLH、时间规则、dose-independent interaction 或 architecture-causal law 的证据。

建议将旧稿叙事从“TCAS schedule → CAI 推导 → C3/LLH 胜出”改为“有效控制语义 → 深度与时间分配的实证辨析 → 作用异质性 → interface/对象边界 → 有限、可复现的实践建议”。最终顺序应由冻结 ledger 的实际结果决定。

## 六、工作区和来源状态说明

本地当前 checkout 的 HEAD 是 `codex/scientific-validation-v3-20261002` / `5c2c8829`；本地 `codex/scientific-validation-v3-20261006` 指向附件所述 `12da08c7`。计划文件位于本地 `next_stage_20261006/`，不在 `12da08c7` commit 中，且被根 `.gitignore` 的 `final/*` 规则排除。应在任务结束时为实际执行的协议/版本建立可追溯的纳入与哈希记录。

当前工作树的 `FINAL_REVIEWER_CLOSURE_MATRIX.md` 已记录用户提供的 `第二轮审稿意见.txt`，列出 SHA256，并说明 substantive R1/R2/R3 内容与归档副本匹配；因此附件分析中“第二轮来源尚未进入 evidence tree”的问题在**当前本地工作副本**已解决。这个来源映射只关闭“审稿意见来源是否齐全”，不会关闭 R1/R2 的实质证据问题。该矩阵仍将 R1.2 标为 `CLOSED_BY_CLAIM_REDUCTION`，且 R2.3 的摘要尚未列入 MVDiffusion；这两点仍需与上文的证据路线核对。

`CLAIM_EVIDENCE_CLOSURE_MATRIX.md` 已有 Fresh B150 对旧 Fresh300 的当前决定 overlay，但较早的逐项说明仍留有 C3 `STRONG` / “advantage stands” 和 `+0.4 dB` 结论。统一权威表应把这些旧段落显式标为 `SUPERSEDED_FOR_FINAL_CLAIM`，并记录替代 authority、替代数字和允许措辞；只在文件顶部写 overlay 仍给后续取数或改稿留下误读入口。下一阶段 E0 的 ledger 最好承担这条显式 supersession 链。

## 参考文件

- `final/round2/scientific_validation_v3/next_stage_20261006/NEXT_EXECUTION_PLAN_ZH.md`
- `final/round2/scientific_validation_v3/FINAL_REVIEWER_CLOSURE_MATRIX.md`
- `final/round2/scientific_validation_v3/CROSS_BACKBONE_MECHANISM_REPORT.md`
- `CROSS_BACKBONE_VALIDATION_MVDIFFUSION.md`
- Kulkarni, *Scheduled Style Injection*, arXiv:2605.26538 (CVPR NTIRE 2026): <https://arxiv.org/abs/2605.26538>；official implementation: <https://github.com/ameyskulkarni/scheduled_style_injection>
- `第二轮审稿意见.txt`
- 用户提供的分析文本：`/home/ubuntu/.codex/attachments/8491f8ab-c035-46d4-adde-b2a8250ec4bb/已粘贴的文本.txt`
