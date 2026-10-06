# 01549 与 1006 的最终改稿路线：同领域论文叙事与证据链对照

日期：2026-10-06
范围：只基于当前可核验的 01549 原稿、1006 证据包、已提供的 R1/R2/R3 意见和下列一手论文。本文是改稿决策备忘录，不是编辑决定，也不代表审稿人已接受任何 claim reduction。

## 决策

**推荐采用“以 01549 为科学主线、以 1006 为唯一证据权威的连续性修订”。** 不采用两种极端方案：不把 1006 的 `NARRATIVE_D` 候选稿直接当成一篇全新论文提交；也不在 01549 原稿后面只追加新实验、保留旧的胜出与机制结论。

这里的“连续性”只保留问题、介入对象和论文身份：几何条件多视角纹理生成中，adapter scale 如何影响结构与纹理表现；主实验仍是同一 MVPainter-style residual path；TCAS/C3 仍作为被检验的既有 profile。旧结论要按 1006 的证据状态重写。这样不会把修订包装成新方向，也不会让已被审计推翻或降级的结论回流正文。

1006 应承担三个角色：可追溯证据账本、审计后的数字和措辞 authority、补充分析及响应材料来源。它当前的 1006 论文候选稿适合作为严苛的“claim ceiling”参考，暂不作为最终文章的叙事蓝图。01549 的排版和基本问题链可以沿用，但不得把版式连续性误作科学结论连续性。

**重要保留意见：这条路线能降低“换方向”质疑，尚不能关闭 R2.1。** 类似期刊论文通常把较明确的新算法组件与消融、基线和输出端点评估相连。现有审计把贡献收窄成一条 MVPainter-style residual/cap path 的经验刻画；目前没有证据能保证这达到目标期刊的新颖性门槛。若目标仍是当前期刊且 R2.1 必须实质闭合，需在证据冻结前证明一个独立、可复现、非事后挑选的方法贡献；否则要接受该项仍是编辑判断，而不能声称已解决。

## 代表论文的叙事和证据链

这些论文不是影响力排名，也不是要求本稿复制其数据规模。选择标准是：CVPR/CVPRW/WACV 的 3D 纹理/扩散论文、Computer Graphics Forum/Computers & Graphics 的相关图形学论文，以及与本稿 schedule claim 直接重叠的一手先行工作。它们说明“什么主张需要什么证据”，不能替代本稿实验。

| 论文 | 叙事主轴 | 论文把主张连到哪些证据 | 对本稿的直接启示 |
|---|---|---|---|
| [Paint3D, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Zeng_Paint3D_Paint_Anything_3D_with_Lighting-Less_Texture_Diffusion_Models_CVPR_2024_paper.html) | 两阶段、形状感知的 UV 纹理扩散，目标是完整、无烘焙光照且细节丰富的纹理。 | 与 Latent-Paint、TEXTure、Text2Tex 对比；报告 FID/KID；用户研究从 60 个 mesh/prompt 中抽样，30 名参与者以 360° 旋转观察，分别评价总体质量和文本匹配。 | 一旦声称 3D 外观或 fidelity，证据须让人看到完整对象，并直接测所声称的感知维度。PSNR、LPIPS、Laplacian variance 不能代替“材料忠实”。旧 01549 人评只能支持被实际比较的 s=1.25、s=2.50、C3 条件及当时的问题，不能迁移到 LLH、新 schedule 或未见视角 fidelity。 |
| [MVPaint, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Cheng_MVPaint_Synchronized_Multi-View_Diffusion_for_Painting_Anything_3D_CVPR_2025_paper.html) | 将同步多视图生成、空间感知 inpainting、UV refinement 三个模块分别对应一致性、完整性和 seam 问题。 | Objaverse 与 GSO 两个 T2T benchmark；与 TEXTure、Paint3D、SyncMVD 比较；16 个固定视角的 FID/KID/CLIP；10 名参与者可自由查看模型并对 overall quality、seam visibility、consistency 评分；另有模块消融。 | 对每个贡献都应有它自己的对照：不能用 2D metric 代替 baked 3D/seam，也不能用一张视觉图代替因果消融。MVPaint 是端到端系统，规模不是本稿必须追平的门槛；可借鉴其 claim-to-test 对齐。 |
| [Make-A-Texture, WACV 2025](https://openaccess.thecvf.com/content/WACV2025/html/Gorelik_Make-A-Texture_Fast_Shape-Aware_3D_Texture_Generation_in_3_Seconds_WACV_2025_paper.html) | 速度与输出质量并列，主张是秒级纹理生成。 | 同一 prompt 比较；每个 mesh 渲染 20 个视角，报告 FID/KID；用户通过 360° 视频做成对质量和文本对齐选择；另按 A100/H100 报告运行时间。 | 指标随主张变化：若主张省时就报端到端耗时；若主张 fidelity 就用有参照的 fidelity 终点；若主张可视质量就让参与者看到可旋转 3D 资产。不能拿一个方向的好指标代替整体赢。 |
| [Im2SurfTex, Computer Graphics Forum 2025](https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.70191) | 一个可插入既有纹理管线的 learned backprojection 模块，以跨视角 attention 和表面位置、法线、测地距离聚合 texel 颜色。 | 在 410 个 Objaverse 测试 mesh、225 类上评估；所有对照共用 UV/表面参数化；20 个固定视角；在 Paint3D 与 MatAtlas 两种 backbone 上替换 backprojection；消融邻域大小、位置编码、测地距离、视图数。论文也承认测地项的数值收益小、预设视角有限，并报告过度平滑风险。 | 这是与目标图形学期刊最接近的证据范例：新组件被放进两个已有管线里单独替换，搭配共享数据/UV 的公平对照与组件消融。相比之下，“说明 schedule 与指标有关”本身较难承担 R2.1；本稿应突出并实测残差/cap 语义的实际技术价值，不能只靠 claim 收窄。 |
| [UniTex, Computers & Graphics 137 (2026)](https://www.sciencedirect.com/science/article/abs/pii/S0097849326000701) | 从多视图观测恢复单 chart、可复用纹理，分别提出 color-aware cut、扩散视图补全和物理可微渲染的材质/光照分离。 | 目标 venue 的近期论文把“production-ready”与单 chart 输出、避免显著图案区域切缝、补充遮挡视图、材质/光照解耦这些明确模块相连；问题与本稿不同，因此这里只作 venue-level 叙事参照。 | 期刊适配的论点需要一个清楚的技术对象和可审计输出效用。若本稿最后只是一份 schedule leaderboard，不能假定新增几十页审计就会构成方法贡献。 |
| [Scheduled Style Injection, CVPRW NTIRE 2026](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf) | 训练无关的 style-content 调度；逐层/逐步改变 StyleID 参数，并试验几何 ControlNet scale 在 depth/time 两轴上的 schedule。 | 除 35 个以上配置和超过 28,000 张生成图外，它分别比较 layer/time 轴、schedule 正反方向、线性与多种非线性形状、ControlNet 与 gamma 的组合，并用 ArtFID、FID、LPIPS、CFSD 四项指标测量；还在 SD 1.4/1.5/2.1 上检查排序。作者明确将其定位为既有模型上的系统经验研究，而非新架构。它不是 T2T 论文，也不使用本稿同一 adapter residual；但与“layer × time 调度是新控制空间”的普遍性 claim 直接重叠。 | 撤回“首次提出 layer-time allocation/control space”。任务与注入路径差异可以限定本文贡献，却不会自动产生足够新颖性。SSI 的控制变量和系统扫查比本稿已有证据更完整；本稿必须把独特价值落在可核验的 MVPainter residual/cap 执行语义和真实纹理输出，并由本稿证据证明，而不能只靠更多小样本显著性或改名。 |

### 从先例抽出的共同结构

较强的 3D 纹理论文常沿着这条链组织正文：**具体失效模式 → 对应技术介入 → 能隔离该介入的基线/消融 → 与 claim 对齐的 2D/3D 终点 → 失败与适用边界**。涉及人类可见属性时，通常把完整对象/多视角呈现给评估者；涉及一个新模块时，消融直接去掉或替换该模块；涉及实际流程价值时，另测运行时间或产物可用性。

本稿不需要复制大型 benchmark、重新训练完整纹理系统或把所有指标塞进主文。它需要把现有较小而异质的证据诚实连接起来：同一 main adapter 的比较、对象级差异、限制过的 3D 端点、已有的人评范围、以及明确的 residual/cap 实施定义。每条结论要停在它自己的 endpoint 和 cohort 上。

### 对 R2.1 的直接判定

SSI 不是“任务完全相同”的 baseline，因此不能据此断言本稿没有任何增量价值；但它已经覆盖了最宽的机制表述——在预训练扩散模型中沿网络层和去噪步改变注入/条件强度，并系统比较调度方向和形状。当前修订可以可靠地区分应用任务、adapter residual 路径、原生 cap 和多视角纹理终点，却还没有证明这些差异构成足够强的新方法贡献。E5 又表明预定的浅层 dose perturbation 在原生 cap 下不可行，不能把它写成已验证的 dose-aware 技术。

因此，本轮可做且应做的是完成独立 Fresh C3/GFL 比较、把 SSI 与几篇 3D 纹理论文的证据逻辑写入相关工作/响应、对缺失的人评和 seam 证据如实降界，并完成干净可复核的交付包。这会加强 R1 和可审计性，但不应预测它会自动关闭 R2.1。若编辑明确要求方法贡献，唯一诚实的补救是另立一个方法问题：先在开发数据上提出可执行且 cap-feasible 的规则，再锁定、用未触碰对象做独立检验，并与固定尺度及 SSI 所代表的通用 schedule 思路区分；当前不把这一未来研究塞进本次 revision，也不以第三骨干或额外 schedule 排行替代它。

## 两条路线的评估

| 路线 | 好处 | 主要风险 | 决定 |
|---|---|---|---|
| 直接以最新 1006 候选稿替换 01549 | 与当前审计结果一致，数字、统计和边界最容易保持一致。 | 文章主轴会从 TCAS/C3 的条件 scale 干预转成广泛的“测量 residual/cap effects”；LLH 结果不是唯一赢家，且 B 的 safeguards 发生在先前 outcome exposure 之后。读者可能把它看作贡献换向；新主张又仍缺 method novelty。 | 不作为最终主稿路径；继续把它当审计后的 claim ceiling、证据来源和反方压力测试。 |
| 在 01549 上只增补 1006 实验 | 读者熟悉原问题；响应看起来连贯，能复用格式、结构和已做的人评。 | 会把新的正结果拼到旧的 +0.96 dB、independent held-out、唯一 C3/CAI 和跨骨干叙事上；其中有些被 cohort/provenance/dose 审计降级或否定。简单增量很可能给审稿人“选择性报喜”印象。 | 不采用 append-only。 |
| 以 01549 科学问题为骨架，按 1006 authority 重写 claim 与证据顺序 | 保持研究对象和方法身份连续，同时能诚实撤销失效推断。 | R1.2 仍缺真正预注册的同 main-adapter 新对象确认；R1.1 人类/缝合/完整 3D fidelity 仍有未闭合项；R2.1 贡献充分性不是统计显著性可解决。 | **推荐。** 在所有新增比较明确标记为 revision-era evidence 的前提下实施；证据未冻结前不改 01549 原文。 |

## 以 01549 为主线的建议叙事

建议使用一个连续但更窄的问题：**在一个具体 geometry-adapter residual path 中，固定全局强度、C3 低–高–低和其他已定义 profiles 对参考结构/纹理指标、对象差异和实际导出纹理分别有什么影响？caps 改变了请求 scale 与实际注入之间的关系吗？** 这与 01549 保持同一任务和介入对象；它不再预设 C3 是普遍最优或机制已被证明。

建议论文结构与 01549 相近，但结果优先级调整如下：

1. **Introduction：** 保留“几何条件强度有结构–纹理取舍”问题；加入 SSI 作为直接相关先行工作，说明本文不主张 schedule 轴本身新颖；将差异限定到 MVPainter residual、layer caps、实际校正量和 3D texture 输出。
2. **Method：** 精确定义 scale 请求、wrapper/cap、有效 scale trace、post-scale residual norm；把 TCAS/C3 写成受检 profile，不写成 CAI 推导的最优解。若 CAI 保留，只能放补充材料并称描述性诊断。
3. **Protocol：** 一张 cohort/runner/provenance 表，分别列 probe-24、旧 pooled-300、strict-276、Fresh B-150、GLB-N20、MV-Adapter-98、MVDiffusion-75；标清发现/回顾性/注册/探索性质，避免不同 cohort 互相替代。
4. **Primary results：** 首先给真正同 main adapter、未见 object cohort 的 C3 vs 预先指定 fixed-scale controls。如果没有新的合格 cohort，就把 strict-276 和 B C3−GFL 保持为 retrospective supplemental evidence，清楚说明 R1.2 仍部分开放；不能把 LLH 当 C3 的 held-out answer。
5. **Human/3D results：** 旧人评只支持当时实际呈现的 s=1.25、s=2.50、C3 和所问的偏好维度；若新冻结问卷收到答卷，可对 LLH/GFL/GFH/GC3/linear 按 protocol 单独分析，不能和旧人评合并。GLB-N20 报各 endpoint trade-off、四个 no-UV 排除和 base-color 限制；删除 seam 与 full-PBR 胜利 claim。
6. **Additional diagnostics：** B 的四个 temporal contrasts、E1 seeds、E2 static factorial、A2/A3b 和两个异构 interface 放在有明确标签的次级结果/补充材料。不得让大样本 p 值替代效应大小、实际剂量支持或可迁移性。
7. **Conclusion：** 结论限于所测 adapter、wrapper、objects、renderer 和 metrics。可说“scale profiles affect measured outcomes and responses are heterogeneous”；不可说“C3 universal optimum”“LLH temporal law”“dose-independent Layer × Window mechanism”或“transfers across backbones”。

标题宜保留任务与介入对象，但降掉 winner 暗示。候选方向为 **“Geometry-Adapter Scale Profiles for Multi-view Texture Generation: A Controlled Evaluation”**。只有当最终保留并强调的贡献真是一个新 timing method 且其核心效应经合格确认时，才继续用 “Timestep-Conditioned Adapter Scaling” 作主标题；不要只为维持旧名而暗示 schedule 优越性已确认。

## 审稿人问题到证据链的逐项闭合

| 审稿点 | 已有可靠证据 | 还缺什么/可接受边界 | 正文动作 |
|---|---|---|---|
| R1.1 外观差异、完整对象、unmodified/fixed baseline、未见视角、seam | 24-object GT-stratified comparison panel；存储 GLB 的 sampler-conformant N=20 × 8 conditions × 11 unseen views；多项 metric 的对象 bootstrap。 | 4 个 no-UV 未覆盖；当前为 unlit base-color 而非 full PBR；旧 seam analyzer 无效；LLH 没有人工答卷。若不补相应实验，只能限制应用 claim，seam 和人类材料 fidelity 不得声称闭合。 | 图表同时展示完整对象与失败例；报告所有不同方向的 endpoints；明确输出/UV/renderer exclusions。 |
| R1.2 main-adapter 同协议 holdout | strict-276 GC3−GFL：FG-PSNR +1.208 dB，nominal CI [+1.117,+1.295]，259/276 favorable；Fresh-B C3−GFL +0.502 dB，CI [+0.342,+0.663]。 | strict-276 的 legacy tensor hashes/common-runner 不完整，且该配对非 Core-7 registered primary；B 配对在 unblind 后选定。二者都不能称新独立或前瞻确认。若编辑严格要求，应从新对象来源冻结新 cohort、先注册 C3/GFL/GFH 对比、统一 runner/input hashes 后运行。 | 旧 +0.96 dB 撤回为 independent evidence；strict276/B 数字只能标 retrospective。若做不到新 cohort，response 明确承认该要求只部分满足。 |
| R1.3 variation vs fidelity | variation proxies 与 reference metrics、人评、3D rendering 已区分；视觉 audit 记录 18/24 color/material mismatch、21/24 detail loss。 | 目前没有新 LLH responses；variation 指标不能作 fidelity。旧人评只对旧三个 profile 和其题目有效。 | 不把 texture richness/频率能量直接称真实度；新问卷没有完整答卷则撤回 LLH 感知 claim。 |
| R1.4 CI 与 Edge-SSIM 取舍 | strict276 两组 GC3 对比报告 paired intervals 与 Edge-SSIM；B margins 只限冻结的 LLH−LFM-exact 两 endpoint。 | 回顾性区间未校正；0-crossing 不能解释为等效。 | 不写 broad noninferiority/equivalence；报告方向与 margin 来源。 |
| R1.5 FAC reproducibility | 当前 1006 主稿不将 FAC 作为方法或正向证据。 | 如保留 FAC，需完整训练 provenance 和 clean-clone reconstruction；现阶段不需要恢复。 | scope reduction，方法主文删去 FAC 优越性。 |
| R2.1 novelty beyond schedule selection | SSI 已让通用 layer/time scheduling novelty 失去依据；几何纹理先例表明技术模块通常用可隔离消融/多 benchmark 证明。 | 当前 audit 没有独立的新算法/预测性规则。若期刊要求方法创新，仅增加统计和审计不能解决。需要一个在开发集冻结、在新的 untouched cohort 验证的技术方法；候选可探索 cap-aware realized-residual calibration，但必须先证明可操作、与 SSI/既有 scale scheduling 有明确差异，并通过 prospective control。若它做不到，不应硬加成 claim。 | 写直接对比 SSI；移除“first/general control space”；R2.1 保持明确 open 或通过真实新方法证据闭合，不能靠措辞标 closed。 |
| R2.2 CAI post hoc | CAI 没有独立预测或 prospective derivation evidence。 | 不能仅靠公式自洽说明它先于 schedule 选择。 | 从 contribution 和最优策略推导中移除；若留，显式作为 descriptive post-hoc analysis。 |
| R2.3 cross-backbone | MV-Adapter N=98 与 MVDiffusion N=75 的各自接口结果可报告。 | 干预、cohort、scale semantics 不同；不能归因于 architecture 或证明普遍迁移失败/成功。 | 两组拆开报告为 tested-interface boundaries；撤回 broad transfer claim。 |

## 下一步 go/no-go 阶段

### G1：锁定主结论和一手 provenance（不消耗 GPU）

- 使用 1006 ledger 固化唯一数据 authority、cohort 关系、superseded claims、统计族、CI 和正文允许措辞。
- 明确原稿每一处 `+0.96 dB`、held-out、human preference、CAI 和 transfer 结论分别由什么新证据替代，保留原文字节哈希；不得用新的 LLH 结果覆盖旧 C3 estimand。
- 完成一手文献矩阵：至少纳入上述 5 篇 3D texture/graphics paper 与 SSI；核对完整论文/补充/代码的实际干预，而不只比较 abstract。

### G2：唯一值得考虑的新 GPU 确认

只在 R1.2 仍要求 direct confirmation 且能合法提供足量新对象时，运行一次新的预注册 C3 验证：新对象 cohort 不与 probe、strict-276、Fresh300 或 Fresh B 重叠；C3、GFL 和 GFH 的 main-adapter runner/checkpoint/input conditioning/latents 共享定义并完整哈希；主 endpoint、paired object estimator、multiplicity family 和样本量在生成前冻结。先基于历史对象方差作固定样本量/功效计划，不做中途停或 schedule 搜索。若没有新合格 cohort，则明确将 R1.2 标记 `PARTIAL`，不要重复跑 276/B 并包装为独立确认。

这次运行只回答“原 TCAS/C3 是否在新对象上有可重复的 endpoint-specific effect 和 trade-off”，不重测 30 条 schedules，不因结果更改 grouping、scale、window 或 metric。不同 endpoint 的方向须完整报告，且 3D 输出、人评要用对应同条件样本。

### G3：R2.1 方法贡献 gate

在任何大规模新训练/生成前，写出不超过一页的 candidate method spec 和区别表。若试验 cap-aware realized-residual calibration，应预先定义校准数据、转换规则、目标剂量、不可行条件、baseline、主要终点和独立确认对象；校准集不可复用 test cohort。先做很小的 feasibility pilot，只检查 scale→residual 映射能否按协议实现，不按质量挑 schedule。若规则不能在新对象和可兼容 interface 上稳定执行或没有预定的实践价值，停止把它包装为方法贡献，转为更窄的 evaluation paper 并重新判断 venue。

这是解决 R2.1 的方法门槛，不是当前证据已经证明的发现，也不是批准无限增加实验。新技术方法必须在论文修订前被实际实现和验证。

### G4：人类与实际输出 gate

- 不联系或分发参与者。等用户提供冻结问卷答卷后，一次性运行既有 checker/analyzer；检查 40 slot 全部解析且至少 36 valid 后才作结果判断。
- 如果无答卷，正文保留旧 C3 人评的窄结论并声明它不评价 LLH、材质真实性或 seam；撤回任何新 schedule 的人类 preference/fidelity claim。
- 3D endpoint 按 GLB-N20 sampler-conformant authority 报告；不复用旧 clamp renderer 和 seam CSV 作正证据。N=24 coverage 在四个 no-UV 原因解决前不声称。

### G5： manuscript freeze 与交付

满足以下条件后才编辑/冻结最终主文：G1 权威账本无冲突；G2 要么通过、要么 response 明示部分未满足；G3 对 target venue 有正面方法决策或明确 venue risk；G4 的人类结果到位或相应 claims 已删；asset license、clean-clone、图表重建和 response page-line 检查通过。随后以 01549 格式复用模板，按 final text 重建所有 figure/table/bib，做四方 reviewer + reproducibility pass；所有 `BLOCKING` 均须关掉或由作者明确接受 venue risk。

## 当前不可声称的事项

- “已经符合审稿人全部要求 / 可直接 upload”——当前 final gate 为 HOLD。
- “新独立 held-out 结果确认旧 +0.96 dB”——strict-276 provenance 和注册状态不支持。
- “C3/LLH 是唯一或通用最优 schedule”——多端点 trade-off、对象异质性及 generic schedule 比较不支持。
- “dose-independent Layer × Window mechanism”——A3b three-layer common support 为 0/2,250。
- “layer × time schedule 是通用新控制空间”——SSI 已有直接先例。
- “人类确认 LLH fidelity”“seam 改善”“full PBR 质量”“跨 adapter 广泛泛化”——对应数据或可比设计不存在。

## 一手来源

1. Zeng et al. *Paint3D: Paint Anything 3D with Lighting-Less Texture Diffusion Models*. CVPR 2024. [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2024/html/Zeng_Paint3D_Paint_Anything_3D_with_Lighting-Less_Texture_Diffusion_Models_CVPR_2024_paper.html).
2. Cheng et al. *MVPaint: Synchronized Multi-View Diffusion for Painting Anything 3D*. CVPR 2025. [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2025/html/Cheng_MVPaint_Synchronized_Multi-View_Diffusion_for_Painting_Anything_3D_CVPR_2025_paper.html).
3. Gorelik et al. *Make-A-Texture: Fast Shape-Aware 3D Texture Generation in 3 Seconds*. WACV 2025. [CVF Open Access](https://openaccess.thecvf.com/content/WACV2025/html/Gorelik_Make-A-Texture_Fast_Shape-Aware_3D_Texture_Generation_in_3_Seconds_WACV_2025_paper.html).
4. Georgiou et al. *Im2SurfTex: Surface Texture Generation via Neural Backprojection of Multi-View Images*. Computer Graphics Forum 44 (2025), e70191. [Wiley full text](https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.70191).
5. Li et al. *UniTex: Single-chart texture reconstruction from multi-view images*. Computers & Graphics 137 (2026), 104599. [ScienceDirect record](https://www.sciencedirect.com/science/article/abs/pii/S0097849326000701).
6. Kulkarni. *Scheduled Style Injection: Expanding the Style-Content Pareto Frontier in Training-Free Diffusion-Based Style Transfer*. CVPRW NTIRE 2026. [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf).

文献描述已与各自的 CVF、Eurographics/Wiley 或 Elsevier 一手页面核对。不同任务、venue 和数据规模的可比性有限；上述对照用于证据逻辑，不用于直接排名方法。
