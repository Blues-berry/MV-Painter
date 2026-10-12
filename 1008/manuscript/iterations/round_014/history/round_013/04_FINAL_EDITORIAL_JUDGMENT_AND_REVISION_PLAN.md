# 最后修改的专家判断与可执行方案

依据：第二轮审稿原文、第13版主文与补充、历轮科学审计和第10–12轮最终总结、已完成的GSO100/20对象数据及独立复核。本文件更新第13版最初分析中“外部烘焙未完成”的判断；它是终稿分析及可用改写文本，尚未形成新的第14版TeX。

## 1. 最终判断

现有证据最适合支持一篇有定量发现的图形学应用实证研究：几何控制强度与阶段分配，在什么条件下影响生成视图指标，这些影响在实际烘焙和不同条件接口上还剩多少。TCAS是研究干预，C3是沿用的历史候选。论文的价值应由实验回答的问题决定，而不再由C3是否获胜决定。

这条路线有实际发表先例。Elsevier对C&G的介绍强调计算机图形学研究与应用；该刊的《Evaluating graphical perception capabilities of Vision Transformers》以现有模型的受控评价和应用局限为贡献，而非提出新架构。从这些材料推断，实证路线符合可能的期刊选题方向。它们不证明本稿已经达到贡献门槛，也不改变R2对本稿方法贡献不足的实际意见。

- [C&G出版社介绍](https://shop.elsevier.com/journals/computers-and-graphics/0097-8493)
- [C&G已发表的受控评价研究](https://www.sciencedirect.com/science/article/abs/pii/S0097849325002997)

R2原文确实质疑超出调度选择的方法贡献，也要求真正不同骨干的评价；原文没有把“各骨干均稳定胜出”列为条件。因此，真实负结果可以回应评价缺失，却不能自动解决方法贡献不足。SSI已经研究层、时间以及ControlNet几何条件强度调度，不能再用这些轴的存在本身主张创新。[SSI原文](https://arxiv.org/html/2605.26538v1)

最有用的最后工作是重新组织完整证据、修正过时描述和有偏重的摘要，并提供可追溯的实际应用判断。当前没有必要继续扩大生成矩阵或开发方法。只有发现会影响现有结论的有效性错误时，才需要修复和重算。

## 2. 可以承担贡献的三个发现

### 发现一：弱固定对照的收益不能识别纯时间分配收益

Fresh C300中，C3相对固定低FG-PSNR提高0.522 dB，但深/中层应用尺度总和也由62.5提高到82.5。相同组预算下，C3比固定均值低约0.13 dB、比晚段高强度低约0.56 dB。这是具体、可复算且会改变原部署建议的实证发现。

不能把这个结果改写成“调度没有作用”：同预算移动高强度阶段，确实改变了该冻结管线的输出。不能改写成“晚段最好”：晚段与固定均值仍有FG-SSIM等指标权衡，强固定或线性控制也有更好的具名端点。所识别的是阶段分配总效果；变化中的残差幅度限制进一步的机制归因，不否定总效果比较。

### 发现二：阶段效果有明确的接口、采样协议和端点边界

| 证据 | 已完成结果 | 终稿应如何使用 |
|---|---|---|
| Fresh C300，等预算 | C3−Mean约−0.13 dB；C3−Late约−0.56 dB | 核心时间分配研究；同一冻结管线内有效，追加比较是已看过结果后的同队列研究 |
| 原生MV-Adapter50 | Middle−Mean PSNR +0.029 dB，95% CI [−0.019,+0.081]，p=0.281 | 真正第二骨干评价；没有检测到主要中段优势，不能据此声称等效 |
| GSO100/MV-Adapter，3种子 | Middle−Mean PSNR −0.01366 dB，CI [−0.03056,+0.00352]，p=0.122 | 已暴露输入队列上的外部敏感性研究；新增条件执行前冻结，不能称原始独立确认 |
| 同GSO100次要比较 | Late−Mean PSNR +0.04459 dB，CI [+0.02449,+0.06516]，Holm83 p=0.00335；SSIM +0.001339，Holm83 p=0.000415 | 小而可检测的图像端点变化；明确次要比较与效应量，不放大成全面胜出 |
| 同GSO100非参考LPIPS | Late−Mean −0.0000863，CI [−0.000551,+0.000413]，Holm21 p=1 | 不支持相应非参考外观收益，不能用PSNR显著性替代 |
| 完整参考条件的新训练checkpoint50，S27–S28 | Late−Mean非参考PSNR −1.1838 dB；LPIPS +0.00266，CI含0，校正p=0.0804；C3没有校正后的强对照优势 | 作为同家族、不同checkpoint/采样条件的敏感性反例；不包装成第二骨干，也不与Fresh C合并 |
| 历史MVDiffusion75 | PSNR、结构、颜色存在负/混合结果；干预缩放对应注意力块，未缩放拼接深度 | 第三接口的历史边界；不能称GeoTex操作的严格复制，也不能把一对象镜像身份检验说成75对象重跑 |

不同管线之间，同时变化的输入、训练、算子和采样设置阻止单因素因果解释。可以报告观察到的组合边界，不能声称已经证明“某个骨干造成失败”或建立普遍早/中/晚阶段规律。

### 发现三：实际烘焙限定了图像收益的应用含义

| 应用证据 | 结果 | 允许的解释 |
|---|---|---|
| Fresh C10兼容性筛选烘焙 | Late−Mean未见视角LPIPS −0.00265，CI [−0.00414,−0.00137]，10/10有利 | 具名、小样本、同协议约2%的改善；仅缩小与GT参考烘焙差距约3.7%，明显外观误差仍在 |
| GSO20独立报告的烘焙队列 | Late−Mean LPIPS +0.00008379，CI [−0.00010305,+0.00028592]，原比较族Holm p=0.78765 | 没有检测到该收益；与十对象的骨干、域及投影协议不同，不是同协议直接复现，也不能省略 |
| GSO20，12方法排序 | 平均对象内Spearman 0.6014，原区间[0.4402,0.7332] | 整体排序正相关，不能声称生成指标普遍失效 |
| 同20对象，原有7尺度/时间控制敏感性 | 平均Spearman 0.3964，描述性对象bootstrap CI [0.1750,0.5821]；11/20对象LPIPS最小均值条件改变 | 正相关仍在；最优点估计依赖评价域。此项为本次后验重算，不能升级为预先冻结的主发现或统计显著的最优者检验 |

12方法集合包括整体更差的投影候选；它与仅7个尺度/时间控制的相关性不是同一个量。补入7条件敏感性可以避免把容易区分的差方法抬高的整体相关性直接解释成细小调度差异同样稳定。全部20对象保留，没有按方向删样。

新增重算的脚本和完整对象记录位于本版data/final_editorial_analysis。12方法本次bootstrap的上界与原分析略有不同，因为重采样种子不同；原投稿结果继续使用原区间。11/20或12/20的赢家变化描述均值最小条件，不表示各条件的质量差异已经在统计上分离。

## 3. 第13版必须先修正的地方

1. 摘要第32行仍以十对象小幅烘焙收益作应用中心，没有呈现GSO100与GSO20对主问题的最新结果。引言第53行、贡献第59行和结论第480行也仍以十对象为主。四处必须统一呈现完整证据。
2. 主文第426行把新增GSO100与完整烘焙放在“Additional condition-correction stress test”长段落中，调度问题的新结果被旧投影开发遮住。拆成“原生第二接口：50对象”和“外部输入敏感性：GSO100及20对象烘焙”；投影/APG仅留一句完整负结果摘要，并链接Supplement。
3. S31开头仍写外部烘焙未完成，结尾仍断言没有完整20对象比较或交付包。S33已经报告完成，两者冲突。S31必须改为“原始attempt01失败的历史记录”，准确说明后来按透明校准附录完成相同20对象，保留原始失败和375记录。
4. Highlights第三条只宣传小幅pilot收益，应同时表达第二应用队列没有检测到同样收益。
5. Reviewer response的R1.1、R2.1应同时报告GSO20零结果；R2.3区分原2400单元投影/APG研究和新增1200单元尺度/时间研究，总计3600唯一单元。不能用2400描述整个当前矩阵。
6. ROUND_MANIFEST状态已是完成，但evidence字段仍写external bake incomplete。DRAFT_VALIDATION保留的是初始运行中快照，应明确历史时间点并另提供当前最终索引。01分析中的待运行状态和02交接材料也必须有清楚的历史标签，避免不同文件自相矛盾。
7. 主文第一段不要把“保留稿件身份”“这轮新增”“01549”“1008”“反例归档”作为科学叙事。方法只保留读者理解结果所需的样本、checkpoint、采样、缩放位置及统计协议，档案身份和修回历史集中到补充与回复。
8. Fresh C采用256像素、conditional-only、缓存图像特征，完整原管线采用不同分辨率、CFG及预处理。此差异必须在主文设计表中清楚出现。Constant 1.0 (capped)、Native residual within controlled sampler、原生MV-Adapter、完整v29的具名设置不能共用“unmodified pipeline”标签。

这些是会影响可信度的终稿问题，优先于润色、增加图表数量或追加实验。

## 4. 建议的文章主线与结构

引言围绕一个实际决策展开：使用几何条件生成纹理时，如何判断一个强度分配设置在竞争性固定控制之外还有多大作用，以及这点作用是否具有实际烘焙价值。原来的“强度越大必然损害纹理，所以C3解决平衡”只能保留为历史动机，当前数据不能把它当普遍已验证规律。

正文按问题组织：

- 问题与贡献：研究强度、阶段、图像和烘焙端点的关系。
- 相关工作：承认SSI等调度先例，指出其没有提供这里的GeoTex应用尺度核算、具名对照与实际UV烘焙证据。这个区别是研究内容差别，不等于新调度算法。
- 研究设计：一张队列表交代Fresh C300、第二接口50、GSO100、两套烘焙10/20、历史第三接口75的算子、采样、选择方式、种子和证据等级。视角与种子嵌套于对象，不能相加宣传独立样本量。
- 结果一：竞争性控制改变了原C3判断；配对效应和均值/中位数分歧。
- 结果二：等应用尺度预算后的阶段分配总效果；避免把预算差当时间优势。
- 结果三：实际烘焙中的小幅收益、未检测到的收益、GT自烘焙损失和可见失败；10与20并排，不合并。
- 结果四：原生第二接口与外部输入研究；历史第三接口用一段概述、详细结果进补充。
- 讨论：给出具体的控制选择含义、作用边界、历史复现与训练档案限制。

旧人类偏好保留一段及补充完整表，说明它支持原刺激的整体偏好；FAC保留一段及补充归档，不以当前训练替代FAC。轻量模块约23%延迟收益和质量损失、投影开发及APG负结果完整保留到附录/复现附件，不承担本文主贡献，也不能删除对核心结论有影响的反例。

Supplement按科学问题重排，并添加一页索引：协议与默认路径；核心配对数据；应用烘焙校准及失败；跨接口；历史开发与训练/成本探索。原始图表和失败记录可以移入编号清晰的历史档案，保留来源与处置理由，不需要把每一轮过程都写成投稿Supplement的新章节。

## 5. 图表和实际应用结论

主表建议集中为：队列/协议表；Fresh C竞争性控制与等预算表；两个原生MV-Adapter队列的具名配对效应；两套实际烘焙队列并排报告。绝对分数不跨管线作优劣排名。显示指标方向、对象数、区间是pointwise还是同时、主/次/后验及校正族。

一张配对效应图可以按队列分面呈现Middle−Mean和Late−Mean，但PSNR与LPIPS分别成图，不能混成总分。仅用实际记录绘制；不同队列不用统一绝对分数判断骨干好坏。

主文需要真实、完整对象与一致视角展示。保留有利、一般和失败例及选择规则，并让核心图包含强固定控制。已有完整原管线/v29输出只有在注明其实际权重、步数、CFG和预处理后才能展示为具名部署对照，不能改标签伪装成与Frozen Fresh C完全相同的配置。R1要求的是可信应用比较，单独的原生路径身份校验不能替代质量展示。

接缝没有经过充分验证的定量指标，保留真实局部图和诊断。GSO20固定20对象平均未见前景的完整双线性足迹覆盖约78.7%；这是覆盖诊断，不是删除未覆盖像素后的质量分数。GT自烘焙FG-LPIPS约0.0602、PSNR约19.36 dB表明投影本身存在损失。GT烘焙不能称理论质量上限，也不应从方法误差中减去。

最终部署含义应足够具体：

- 在该GeoTex冻结图像协议内，C3不是推荐的统一默认值；GFH与Generic Linear分别在具名端点更有竞争力，同预算晚段与均值存在端点权衡。
- 原生MV-Adapter没有建立中段强度优势；GSO的晚段PSNR优势很小，不能推出未见烘焙外观收益或自动替换原生设置。
- 生成视图评估仍提供信息，但不能用单个赢家或纹理变化统计替代实际烘焙和参考外观核查。

不要把这些判断再包装为自动选择器、Pareto最优控制、新benchmark或跨骨干因果定律。

## 6. 可以直接采用的英文改写

### 标题

推荐在原标题后加研究定位，保持修回身份：

Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: A Controlled Empirical Study

若作者决定完全按最终贡献命名，可采用Geometry-Control Allocation in Multi-view Diffusion Texturing: A Controlled Empirical Study；标题变化必须在正文、补充、回复和提交元数据中同步。它不能替代对原方法主张的回应。

### 摘要候选

Geometry-conditioned multi-view diffusion provides an inference-time strength control, but its practical effect depends on temporal allocation, the conditioning interface, and the evaluated output. We conduct a controlled empirical study of Timestep-Conditioned Adapter Scaling (TCAS), carrying forward the historical middle-high profile C3 without further schedule selection. On 300 held-out objects with a frozen retrained GeoTex checkpoint, C3 improves foreground PSNR by 0.52 dB over fixed low, while competitive fixed and linear controls have better means on all four image endpoints. Matching applied-scale budgets changes the interpretation: C3 is 0.13 dB below fixed mean and 0.56 dB below late-high. Native MV-Adapter studies on 50 Fresh C inputs and 100 GSO objects detect endpoint-specific stage effects but do not detect the primary middle-window benefit over fixed mean. A ten-object native-UV bake pilot finds a small late-high LPIPS reduction of 0.00265 on unseen views; a separate twenty-object GSO evaluation with revised calibration does not detect this benefit. Generated-view and baked-output method rankings remain positively associated, although the preferred point estimates often differ. These findings quantify the effects and limits of geometry-control allocation and provide application-specific evidence for evaluating operating points. They support neither a universally preferred schedule nor physically faithful materials.

### 引言核心段落

The contribution of this study is an empirical answer to a graphics deployment question: how much does temporal geometry-control allocation add beyond competitive fixed settings, and how much of that effect remains after texture baking? Prior scheduling work establishes that conditioning strength can vary across time and layers. It does not determine the effect of the capped residual interface, sampling protocol, or baked appearance evaluated here. We therefore compare applied budgets within each interface, evaluate actual textured meshes under unseen cameras, and report both detectable effects and their limits. C3 is a retained historical operating point rather than the conclusion of the study.

### 三项贡献候选

1. We quantify strength and temporal-allocation effects through matched comparisons with competitive fixed and linear controls, showing why C3's advantage over fixed low does not identify a preferred timing rule.
2. We evaluate actual native-UV baked meshes with matched reference bakes and unseen cameras, measuring small local improvements, persistent appearance errors, and changes in the preferred operating point.
3. We test related allocation questions on distinct conditioning interfaces and input cohorts, identifying endpoint-specific effects and limits to transfer while retaining valid adverse results.

Object-level data and runnable analyses support these findings; the existence of an audit archive is not itself a claim of methodological novelty.

### 结论候选

Geometry-control allocation changes generated-view agreement, but its effects depend on the tested interface, protocol and endpoint. The matched 300-object study shows that C3's gain over fixed low combines increased strength with timing; equal-budget fixed mean and late-high outperform the historical middle window. Native MV-Adapter studies do not detect the primary middle-window advantage, while some secondary image effects are small but measurable. Actual baking yields a limited late-high benefit on ten compatible GeoTex objects and no detected LPIPS benefit on a separate twenty-object GSO cohort. Method rankings are broadly associated across image and baked evaluation, yet their preferred operating points often differ. Competitive controls and application-level evaluation are therefore necessary when choosing a setting within a deployed pipeline. The results do not identify a universally preferred schedule or establish faithful material reproduction.

### Highlights候选

- Matched budgets separate temporal allocation from increased control strength.
- Strong fixed and linear controls challenge the historical C3 choice.
- A small bake benefit is not detected in a separate twenty-object cohort.
- Native interface studies reveal endpoint-specific allocation effects.

## 7. 回复审稿人的最后写法

开头用一个段落解释修订后的问题、有效新证据、原结论哪些已改变。不要按第几轮探索组织，不用实验数量或GPU工作量请求接受。

R1.1：指出主文的完整对象、统一裁剪、强控制和真实未见烘焙；同时报告10对象小收益与20对象零结果。明确图像误差仍明显，接缝仅诊断、无PBR结论。给出可播放真实视频和确切图表位置。

R1.2：准确承认原checkpoint没有恢复，Fresh C是相同新checkpoint内的有效留出比较，不是历史+0.96 dB的精确复现。撤下历史数字作为当前headline，给出300对象、零UID重叠、共享输入/种子/指标。既有审计中“作者确认不把checkpoint哈希当门槛”的解释不能证明审稿人的要求已完全满足。

R1.3–1.4：解释各端点和variation/fidelity的区别，给出配对区间与结构损失；不把跨零区间称等效，不后选非劣界。

R1.5：列出实际交付的推理/统计/配置；FAC训练manifest、seed和权重身份缺口仍在。不要用后续1090对象新训练实验替代历史FAC的复现。

R2.1：先明确一般调度概念已有先例，再列出三个具体发现：更强控制改变C3判断；等应用预算阶段分配的效果量；实际烘焙与不同原生接口限定其应用含义。不要只写“我们更透明、更可复现”；这些是可信度条件，无法独自承担新贡献。

R2.2：独立推导、命题与最优性含义撤除；保留可执行操作与比较逻辑。CAI旧内容若保留在历史档案，必须标记不作为现稿理论支持。

R2.3：区分MV-Adapter50、GSO100原生尺度矩阵、MVDiffusion75历史部分对应块干预，给出零/混合结果和身份检查范围。已完成的是不同骨干评价，不是稳定泛化成功。

R3：说明对已支持发表版本做了哪些必要更新，不借R3意见判断多数票或要求压过R2。

每条回复最终要有“已改什么—证据及限制—正文/补充位置”。作者审核后冻结行号，不能用本分析中的旧行号当终稿位置。

## 8. 最后一轮的执行顺序和验收

1. 从第13版完成源文件创建第14版检查点，记录继承来源；保留第13版与全部原失败记录。
2. 先修S31/S33及状态字段矛盾，再重写摘要、引言、贡献、GSO段和结论；让所有核心结果拥有相当的可见性。
3. 合并重复主表，增加协议/证据等级表；保留关键真实图与反例。补充按问题重排，历史档案保留索引及处置说明。
4. 用同一份冻结结果索引更新正文、Supplement、Highlights、Reviewer Response和说明文件；不同证据队列绝不混报。
5. 主表逐对象复算；检查效应方向、原比较族和pointwise区间。新排序敏感性明确后验，不能代换原主终点。
6. 两遍编译与页面视觉检查；核对所有图号、来源、样本数、标题和回复位置；检查视频、ZIP与统计脚本。建立当前最终验证文件，保留初始快照为历史证据。
7. 制作clean/marked版本、补充、回复、视频、实际可交付代码与数据说明。差异稿应对照认证投稿版，而不仅是第13版；如另提供13→14差异，必须标清对象。

最终验收不是“C3恢复最优”，而是：任何主结论均能指出对应对象级数据和协议；任何影响核心结论的反例在主文得到体现；稿件各处没有未完成/已完成的冲突；默认管线、历史身份与实验参数准确；实际交付与复现声明一致。

## 9. 相对上一版与剩余风险

这次修改会提升完整性、公平呈现和可读性，并减少R1/R2容易抓到的范围混淆。加入GSO20和完整协议反例会削弱“小幅应用收益可迁移”的印象，这是必要的科学修正。它不会增加方法创新，也不保证编辑愿意把方法稿重新评估为实证贡献。

最可能的攻击点仍是：实证内容是否足够超出已有调度研究；核心Fresh C采用修改后的采样协议；原adapter同身份留出复现未恢复；实际烘焙样本便利筛选且较小；GSO校准后验修改；骨干/域/训练混杂；FAC与旧刺激的档案限制。准确披露并减少不受支持主张可以降低这些风险，无法把它们变成已解决事项。

我会建议完成上述第14版再做最终投稿判断，当前第13版不宜直接作为终稿。如果R2坚持只认可方法性创新，现有证据仍不足；若编辑认可定量、受控且有应用意义的实证研究，此方案是当前材料最合理的修回方向。没有校准资料可把这一判断可靠换算成中稿百分比，更无依据声称90%以上。

## 10. 核查依据

- 审稿原文：1008/audits/source_evidence/r2/reviewer_materials/SECOND_ROUND_REVIEWER_COMMENTS.txt。
- 主文核查：round_013/manuscript_round_013.tex，摘要32、引言53–61、跨接口426、讨论466–480。
- 旧描述核查：round_013/sections/development_round012.tex；新结果：sections/completed_supplement013.tex。
- 完成结果：round_013/03_COMPLETED_RESULTS_AND_RISK.md及round_012/20_FINAL_ROUNDS_010_012_SYNTHESIS.md。
- 原始对象级结果：GSO自动链analysis/TEMPORAL100_COMPARISONS.json、BAKE20_COMPARISONS.json；21600生成视角与8140烘焙视角的独立复核记录。
- 本次新增的是既有排序记录的描述性重算：data/final_editorial_analysis/recompute_rank_sensitivity.py与PAIRED_RANK_SENSITIVITY.json，源文件哈希已记录。
