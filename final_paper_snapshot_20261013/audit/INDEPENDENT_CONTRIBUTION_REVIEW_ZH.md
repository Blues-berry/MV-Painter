# 独立贡献充分性审查

审查日期：2026-10-12（北京时间）。只读审查第14/15版、1006科学裁决、main/1009历史审计及最终整合源码；没有修改原稿、运行模型训练、重新选择对象或调度。最后整合稿是本报告的推荐基底，先前裁决按时间与证据等级解释，不能机械覆盖新的限定。

## 独立裁决

**现有证据支持一篇边界清楚的受控实证研究，不支持把C3、CAI或layer×time调度作为已验证的新通用方法。** 研究不必拥有方法创新才有学术价值；但“有大量实验”也不能替代贡献论证。这里最有用的新知识是：较弱固定对照会改变调度收益的解释；同应用预算比较否定本队列中的中段优先建议；图像端点、烘焙端点和逐对象重复性提供不同结论。这些都是特定系统/协议下的实测事实，不是普遍理论。

推荐采用最终题名 **Geometry-Control Allocation in Multi-view Diffusion Texturing: A Controlled Empirical Study**。TCAS保留为既有残差接口的研究干预，C3保留为历史候选；新题名把研究问题放在方法名称之前，准确反映目前贡献。最终[主文](/4T/CXY/MV-Painter/final_paper_20261012/source/Manuscript_final.tex:27)已采用此定位。

**C&G修回可以保留，但必须公开方向变化。** 研究对象、干预和应用问题连续，完整对照修正了原来的推荐，不是另一套未解释的新论文。正文和回复应同时明确“原C3优势建议被新证据收窄/改变”。最终回复开头及R2.1已经这样做。C&G官方范围包含图形研究与应用，故不能预设只有新算法才合格；期刊契合也不能保证编辑认为该实证贡献充分。[C&G官方介绍](https://shop.elsevier.com/journals/computers-and-graphics/0097-8493)。R2.1仍是价值判断风险，没有校准的接收概率。

## 对先例的正面比较

SSI直接研究按层、按时间改变注入强度，还调度ControlNet几何条件；“首次layer×time”“给scale加入time就是新方法”不成立。SSI §3.2–3.3也比较方向/形状，不能把固定对照、调度方向或多骨干比较本身当本稿独有知识。这里可区分的是GeoTex capped residual的实测预算、配对效果及实际多视图烘焙结果，不能仅靠换任务名主张方法新颖。[SSI原论文](https://arxiv.org/html/2605.26538v1)。

MVPainter已经建立几何条件多视图纹理生成及烘焙系统，本稿没有创建这个系统。当前控制门复用现有adapter缩放接口；没有新训练分支或策略选择器。[MVPainter原论文](https://arxiv.org/abs/2505.12635)。CFG、ControlNet/T2I-Adapter与SSI的控制算子有区别，但算子不同不自动成为方法创新。

| 最终贡献 | 已有先例 | 本稿新增且受数据支持的知识 | 主证据与反例 | 裁决 |
|---|---|---|---|---|
| 强度与时间分配的受控评估 | 已有inference scaling、interval guidance、SSI时间/层调度 | 在冻结GeoTex里区分requested、capped applied和trajectory-dependent correction；等每组标量和后，中段候选不优于合理固定/末段条件 | Fresh C300：C3−GFL +0.522dB；Middle−Mean −0.133dB；Middle−Late −0.564dB；原Middle−mean(Early,Late) −0.0339dB、区间跨0 | 核心实证贡献；不是等实现剂量机制或最优策略 |
| 应用端点与指标边界 | 纹理系统早已评价图像及烘焙输出，指标与真实保真区别也非新概念 | 实际原UV烘焙测量小的局部收益及另一协议的非检出；原276重训显示同一对比全帧/前景PSNR方向相反 | Bake10 −0.002652 LPIPS；GSO20 +0.000084未检出；original276 raw PSNR +1.699但FG −1.314dB | 核心应用知识；没有跨系统材料排行榜、接缝/PBR验证 |
| 接口/协议/重复性边界 | 不同骨干与seed sensitivity为常见评价 | 原生MV-Adapter两个中段主问题均未检出收益；保留MVDiffusion不利结果；小组均值不能提供每对象重复改善 | Native50 +0.029dB未检出；GSO100 −0.014dB未检出；GSO100末段PSNR三seed均值正但仅27/100对象全正；GSO20烘焙仅1/20全seed有利 | 核心边界刻画；接口与域/权重/采样混杂不允许architecture因果归因 |

三项一起提供关于实践选择的量化知识，但每项都很窄。其意义来自对原推荐的实证修正及部署判断的约束，不能把审计档案、检验次数或极小p值写成独立科学创新。

## 决定性证据与保留次序

1. **原同预算主问题必须置前。** 最终[主文235行](/4T/CXY/MV-Painter/final_paper_20261012/source/Manuscript_final.tex:235)恢复Middle−对象内mean(Early,Late)：均值−0.0338775dB，95% CI [−0.117170,+0.051422]，p=0.432378，119/300正。它既不支持中段优势，也不证明等效。随后才报告Middle−Mean及Middle−Late；不得把后验all-pair重算中的raw Middle−Mean叫原主检验。原内部冻结在已有Fresh C暴露之后，仍是同队列回顾性addendum。
2. **强固定和Generic Linear必须保留。** 四图像端点均值均优于C3，不能因预算不同而排除实践强对照；不同预算只限制其“timing-only”解释。Late-high也不普遍支配：Mean有更高FG-SSIM，Linear的烘焙LPIPS均值略更低但PSNR更低。
3. **真实烘焙正反结果并列。** Bake10是300输入中10个兼容资产的pilot，11 unseen views嵌套对象；−0.002652约2%相对LPIPS改变，仅填补Mean与GT-256差距的3.7%。GSO20完整12条件×3seed加GT是740 meshes/8,140 views，但只有20独立对象，且校准改动后验。非检出不是同协议复制失败、等效或“不存在效应”。
4. **original276新发现必须降为request-slot技术敏感性。** 记录列表由1118去掉79交集到1039，与276请求UID列表零交集；新seed/new checkpoint不是恢复v1。随后运行日志进一步证明obj_0046请求UID输入失败，loader随机替换未知实际UID。这已经不只是“缺少hash”，而是一次确知的identity偏离。我按LF物理行独立读取[实际日志](/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_original276_leaveout_20261012/logs/evaluation.log:623)：623行空输入min错误，624行是请求UID f7ef602b19214debb0b350db9af55ff2的wrong path。因此1,104行是276请求槽位×四条件，不是已认证的276唯一实际对象，也不是严格留出确认。未知替换对象可能进入训练列表或与另一槽位重复，不能把槽位bootstrap/signflip当对象总体推断。全帧PSNR+1.699与FG-PSNR−1.314、FG-LPIPS+0.01127及SSIM损失仍可作为保留记录的技术端点示例；剔除已知失败槽位后275槽位的+1.6965/−1.3110dB及LPIPS+0.011272保持方向。但排除一个已知fault不自动认证其余实际UID，也不能事后把275叫新主分析。四条件无Mean/移动窗口/Linear，且队列既有暴露，不可承担timing-only、纯新holdout、独立对象总体效应或历史+0.96复现。根任务已据此修改摘要/表/正文/补充/回复的主要措辞；最终以request-slot技术敏感性限定为准，回复其余旧“276-object”字样也须统一。
5. **固定seed、dominance及incoming-UV诊断保留次要。** 270/300被其他条件四端点弱支配是已测点估计描述，非每对象显著优劣或材料失败率。黑色恒定错误图仍能零方差，说明incoming consistency不足以证明保真；80值重放证明实现/数值一致，不证明seam质量。三固定seed不能估计训练随机性。

## CAI、A2/A3b及FAC的裁决

CAI无独立前瞻预测，不唯一推出C3；撤去独立推导、proposition及optimality是合适关闭方式，而非证明CAI正确。最终主动稿件不再由CAI承载结论。

A2/A3/A3b保留为受测干预下的响应异质性。A2为探索；A3为同队列高剂量压力测试；A3b/Fresh B是受控但冻结时间无法由Git认证的回顾性敏感性。极小p不等于机制强或应用重要；A3 PSNR interaction share仅0.8%，A3b cell RMSE是0.0205dB/0.000342 LPIPS。MV-Adapter无经校正全局交互支持。

**旧1006审计的raw-L2 common-support范围及0/2250必须继续撤回。** 各层特征图空间尺寸不同且通道数未保存，不能作为跨层剂量支持反证。最终[补充182行附近](/4T/CXY/MV-Painter/final_paper_20261012/source/Supplementary_final.tex:182)保留撤回；正确结论是本设计没有建立等实现剂量、剂量独立机制，而不是“用有效common-support检验证明不重叠”。

FAC的旧1006裁决为从当时修回稿移除；第14/15版重新保留为明确标注的历史负结果并交付恢复代码。这是证据处置时间差，不能把旧REMOVED裁决说成当前内容。84文件、两个入口、三种唯一CPU fixture能验证恢复组件前向/梯度/state-roundtrip；controller源码同字节，不能计为六种独立验证。早入口默认可训base，后入口仅controller；FSC实际FFT且初始非恒等。1706 vs1200、历史seed、checkpoint、执行CLI与输出绑定未闭合，故不声称完整FAC训练复现。历史不利数值可留补充，不能证明学习自适应一般失败或TCAS方法成功。

## 第15版与最终稿的文本审查

第15版已明确实证定位，摘要、主文和回复核心数值没有发现实质冲突；但强调C3弱对照+0.52在前、遗漏原Middle−avg主检验，容易继续造成方法优势印象。最终题名、摘要33行、主文235行和回复R2.1已修正。

第15版Supplement940行称12对象untrained FAC控制“described in main text”，正文已无该描述；最终补充943行改成历史段落下文，正确。

最终主文、补充、回复公开v2恢复不能替代v1；“三份MD5相同”仅三份同一artifact备份，不是三模型或v1认证。最终新增original276以全帧/前景反向呈现，避免只选有利端点。随后确认一次未知UID随机replacement，构成必须处理的重大限定：不得再称276真实独立对象或严格留出，必须明确一失败槽位以及275槽位排除敏感性；最新摘要、正文254/268行、补充1135/1137行与R1.2回复已经降级。**研究的Fresh C/bake/native核心实证仍可保留，original276仅能承担技术敏感性。**

尚有实际限制：原276一实际随机替换身份未知且其余actual UID不闭合、历史v1/FAC完整复现未成、兼容烘焙样本范围小、接缝/PBR无有效量化、seed与后验诊断只是有限刻画。这些不是靠措辞即可“关闭”的问题；最终稿以明确限制交付，不能以审计PASS自动变成科学全关闭。

## 独立轻量复算与PDF/构建检查

我独立读取第15版CSV并使用不同seed20261012复算：Middle−mean(Early,Late)精确均值−0.0338774820，50,000对象bootstrap区间约[−0.117370,+0.050741]，100,000 sign-flip p约0.433086；与最终原规则−0.0338775、原CI/p相符。独立重算四端点dominance得到270、Fixed High单独173、C3反向16；Bake10 Late−Mean精确均值−0.0026516549，10/10有利，全部2^10 sign flips得到p=0.001953125。另确认16×2.5+34×1.25=50×1.65=82.5，浅层50×0.8=40。

第15版[PDF](/4T/CXY/MV-Painter-cg-revision-20261010/1008/manuscript/iterations/round_015/deliverables/Manuscript_round_015.pdf)抽取文本与源码的摘要、三项贡献及限定一致；原验证14页主文/64页补充/6页回复。独立审查未重新认证每张图视觉布局，最终新增后的PDF须由根任务完成构建与引用/排版检查。本报告不把第15版验证自动移植给改过的最终PDF。

第15版可用构建为 `build_round_015.py`（三遍pdflatex，读取vendor/fonts/figures/tables/sections）；统计入口`source/scripts/build_evidence.py`原实现对主矩阵、native50、bake10、GSO100/20配对均值与Holm复算。新增原主检验/原276必须由最终独立脚本额外核验，不能只沿用父版本PASS。标记稿需继续对认证原投稿source比对，不能只标对第15版的diff。

推荐最后版本保留主文强对照表、原timing primary、original276端点表、Bake10/GSO20并列表、native50表、跨协议effect图、完整对象/共同ROI/真实烘焙图；A2/A3b、全对比、seed细表、UV controls、失败修复、训练/v29/成本和历史FAC置补充。全帧与前景、生成与烘焙、UV输入一致性与保真之间的差别必须在图例里明确。
