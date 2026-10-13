# 最终论文先例与创新边界审查

审查日期：2026-10-12。审查对象为 `round_015/manuscript_round_015.tex` 的相关工作、方法定位与参考文献，结合已联网核实的一手论文、作者代码、固定版本官方文档。本报告不重新核算本地实验，也不改动既有稿件。来源及版本见同目录 `PRIOR_ART_SOURCES.json`；`VERIFIED_REFERENCES.bib` 仅给出建议新增的三个必要引用，不重复现稿已经存在的文献。

## 结论

最终方向应是 **Geometry-Control Allocation in Multi-view Diffusion Texturing: A Controlled Empirical Study**。已有先例覆盖推理时几何条件强度控制、按层加权、按采样时间启停，以及同时沿层和时间调度几何条件。TCAS 的调度函数、三阶段形状、免训练或几行代码本身均不足以构成新的方法贡献。可保留的贡献是特定多视图纹理任务中可审计、受控、包含反结果的经验知识，而非一种普遍优于固定尺度的新算法。这是根据下列先例和现稿证据边界作出的定位建议。

显著性是对指定比较的不确定性描述，不能证明新颖性；阴性结果不代表等价。也不能因本次检索未找到完全相同的实验，就写成“首个研究”。

## SSI 已明确识别，不能将其当作不相干的风格迁移工作

现稿 `kulkarni2026ssi` 指的是 Amey Sunil Kulkarni 的 **Scheduled Style Injection: Expanding the Style-Content Pareto Frontier in Training-Free Diffusion-based Style Transfer**，CVPR Workshops 2026 NTIRE；arXiv:2605.26538，首次提交 2026-05-26。作者、标题、工作坊与作者代码均有一手来源支持。[CVF 官方论文](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf)、[arXiv 完整文本](https://arxiv.org/html/2605.26538v1)、[作者代码](https://github.com/ameyskulkarni/scheduled_style_injection)。

SSI 在 StyleID 上调度 query 混合参数 γ，同时另行调度 ControlNet 的几何条件尺度，明确研究层、时间、方向及函数形状。其 §3.3、Table 2 和补充 Tables S5–S7 涵盖 ControlNet 几何调度，而不仅是 attention 风格注入。固定 CN=0.25 与 CN 时间调度在 Table 2 的 ArtFID 为 29.111 与 29.032；LPIPS 为 0.496 与 0.498，后者略差。因此，“几何调度相对固定控制的收益较小且依赖端点”是合理表述，“SSI 证明几何时间调度普遍改善内容保真”则不成立。其补充时间表存在小数值不一致（29.035 对主表 29.032），最终稿没有必要复述这些数值。

本项目可以说明：SSI 调度的是 StyleID attention mixing 与另加的 ControlNet branch；本地主要试验调度的是已存在 GeoTex 残差，并受到 wrapper caps 约束，任务、相机、条件和端点不同。这些区别说明为何需要本地受控评估，不能被改写成“时间/层调度首次出现”。也不能把 SSI 的 γ 方向结论外推为所有几何残差的普遍规律。

## 更早的工程先例已经覆盖层权重与时间窗口

ControlNet 作者仓库的深度演示代码在 2023-02-20 的固定提交已经使用 13 层 `control_scales`：普通模式统一加权，guess mode 使用随层变化的几何序列。它证明逐层 conditioning residual 权重是已有操作；并不证明某个层配置在本地纹理任务最佳。[固定提交代码，第 54 行](https://github.com/lllyasviel/ControlNet/blob/f2e1bc38dc8d925fb542be4c138c46013ace1988/gradio_depth2image.py#L54)。

Diffusers v0.21.0 于 2023-09-13 发布，其固定版本 ControlNet 接口已经公开 `controlnet_conditioning_scale` 与 `control_guidance_start/end`。前者在注入 UNet residual 前乘尺度，后两者指定采样期间开始和停止应用 ControlNet 的比例。其启停是时间门控先例，不能等同于任意连续函数或本项目具体三阶段配置，但足以否定“首次提供几何条件采样时间控制”的广义主张。[v0.21.0 官方文档](https://huggingface.co/docs/diffusers/v0.21.0/api/pipelines/controlnet)、[固定代码版本](https://github.com/huggingface/diffusers/blob/29f15673ed5c14e4843d7c837890910207f72129/src/diffusers/pipelines/controlnet/pipeline_controlnet.py)、[官方版本发布日期](https://github.com/huggingface/diffusers/releases/tag/v0.21.0)。

## 主要相关工作与本项目的准确关系

| 已核实先例 | 已有技术或知识 | 本项目可以增加的内容 | 不宜采用的论断 |
|---|---|---|---|
| MVPainter，arXiv:2505.12635，2025 | 参考图与已知几何下生成六视图；Union ControlNet 融合 normal/depth；RGB 烘焙及独立 PBR 属性提取模块 | 特定本地 GeoTex 实现和冻结 checkpoint 下的尺度配置受控比较 | “新提出几何控制架构”；或把本地重训小模型写成官方 MVPainter 原始 checkpoint 的复现 |
| MV-Adapter，ICCV 2025，arXiv:2412.03632 | 统一条件编码器，以及继承预训练注意力先验的 parallel multi-view/image attention adapter | 其本地 native condition-guider 接口中的时间配置与端点结果 | 将其同名尺度视为 GeoTex 的同等残差剂量；或者作为架构一致复制 |
| MVDiffusion，NeurIPS 2023 | correspondence-aware attention 传播跨视图信息，以相机、深度构成的对应关系支持场景多视图生成 | 本地部分 correspondence-block 干预的迁移边界 | 将 correspondence scaling 等同于所有 depth conditioning 的缩放 |
| StyleID，CVPR 2024 | 以 style K/V 替换、query preservation、attention temperature 和 latent AdaIN 做免训练风格迁移 | 为与 SSI 的 attention 操作作精确区分提供基础文献 | 将 γ 直接解释成几何残差尺度 |
| SSI，CVPRW 2026 NTIRE | 层/时间 γ 调度与 ControlNet 几何尺度调度，并分析组合配置 | 同接口竞争对照、逐层 applied budget 控制及本地生成/烘焙/颜色端点 | “首个 geometry-conditioning schedule”；用任务不同规避实质先例 |
| Limited-interval guidance，NeurIPS 2024 | 在指定噪声区间启用 CFG，测试质量/分布影响 | 几何残差三阶段配置在另一个任务中的不同结论 | 将 CFG 中段收益当成 adapter 中段必优的机制证明 |
| Adaptive Guidance，AAAI 2025 | 根据采样收敛特征省略 CFG 网络评估，主要目标是推理效率 | 与残差强度分配区别清楚的背景说明 | 把它直接称为通过调节几何条件幅度提升纹理保真的工作 |
| APG，ICLR 2025，arXiv:2410.02416 | 对 CFG conditional/unconditional 更新作平行/正交分解，并配合重标定和 momentum 减少高 guidance 饱和问题 | 与本地已测试 APG 基线比较；交代投影候选失败及适用接口 | 把投影、正交分解或 guidance normalization 本身列为本项目原创；将 APG 默认视为 GeoTex residual 的同一算子 |

论文来源：[MVPainter §2.2–2.3](https://arxiv.org/html/2505.12635v1)、[MV-Adapter 官方论文](https://openaccess.thecvf.com/content/ICCV2025/papers/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.pdf)、[MVDiffusion 官方论文页面](https://papers.nips.cc/paper_files/paper/2023/hash/a0da690a47b2f52faa63f6fe054057b5-Abstract-Conference.html)、[StyleID 官方论文](https://openaccess.thecvf.com/content/CVPR2024/papers/Chung_Style_Injection_in_Diffusion_A_Training-free_Approach_for_Adapting_Large-scale_CVPR_2024_paper.pdf)、[limited-interval 官方论文页面](https://proceedings.neurips.cc/paper_files/paper/2024/hash/dd540e1c8d26687d56d296e64d35949f-Abstract-Conference.html)、[Adaptive Guidance 官方论文页面](https://ojs.aaai.org/index.php/AAAI/article/view/32192)、[APG 作者页面与正式 BibTeX](https://ait.ethz.ch/apg)。

## 建议保留的受控经验贡献

1. **强竞争对照改变历史结论。** 现稿的 Fresh C 300 对象中，历史 C3 相对 Fixed Low 的收益不能证明中段配置优越；同一主要试验里 Fixed High、Generic Linear 有更优平均端点，匹配 applied-scale sums 后 Fixed Mean 与 Late-high 又优于 C3。贡献在于排除弱基线解释并报告边界，不在于给 Late-high 换一个方法名称。
2. **把 request、实际应用的尺度和生成中的残差分开记录。** wrapper caps 会使相同请求产生不同实际配置；每层 applied-scale sum 匹配提供特定 scalar-budget 下的配置比较，但不等于 evolving residual dose 匹配，更不能据此声称已分离纯粹的时间因果机制。跨层未经维度归一化的 L2 不能视为可比剂量。
3. **检查接口与应用端点。** native MV-Adapter 与 MVDiffusion 结果是各自实现和数据上的边界证据，不能合并成一个跨架构效果。实际 mesh 烘焙、不参与烘焙的视角、GT self-bake、参考颜色与 shared-UV disagreement 共同限定图像指标能支持的结论；一致但颜色错误的输出不能称为材料保真。
4. **保留未成立的尝试。** 本地 projection、native middle-window 不检出、GSO bake 不检出，以及 seed sensitivity 应共同制约结论。增加数据量或统计校正提升证据可信度，本身不是方法新颖性。

上述是依据 `round_015` 披露内容提出的主张边界；各实验数量、效应和覆盖范围仍以项目实验审计及最终表格为准。

## 第 15 版引用与表述检查结果

| 引用或表述 | 审查结果 | 最终稿动作 |
|---|---|---|
| `kulkarni2026ssi` | 身份、作者、2026 NTIRE/CVPRW 归属成立；现稿已经承认几何时间/层调度先例，没有将 SSI 猜成其他论文 | 保留；加 arXiv ID 或官方 URL 有助核验 |
| `zeng2024paint3d` | **明确标题错误**。现稿写成 “Lighting-immersive texture generation”；官方标题为 **Paint3D: Paint Anything 3D with Lighting-Less Texture Diffusion Models**，CVPR 2024，4252–4262 | 修正标题；主 agent 已确认最终稿修正 |
| `castillo2023adaptive` | 引用键里的 2023 不等于出版年份；参考文献写 AAAI 2025 是正确的。其主题是 CFG 评估省略与效率，现稿将它泛置于 “quality/diversity/fidelity strength scheduling” 有表述漂移 | 单独说明效率调度；主 agent 已确认最终稿区分 |
| `huang2024mvadapter` | 2024 arXiv 与 2025 ICCV 分别成立；现稿 ICCV 2025 不是年份错误 | 保留；可补全七位作者，但缩写 et al. 不是错误 |
| `sad2024apg` | 2024 arXiv、ICLR 2025 正式发表均成立。作者 Sadat、Hilliges、Weber 和正式标题正确；bibkey 拼写不是事实错误 | 保留；明确 APG 修改 CFG 而非本地 adapter residual |
| MVPainter 与 GeoTex 的关系 | 官方 MVPainter 采用 Union ControlNet，且原系统另有 PBR module；本地“GeoTex-Adapter”是本地实现接口命名 | 应保持 “MVPainter-style / local implementation” 与官方原架构、原权重区别，不能新增等价或复现声称 |
| `cheng2024mvpaint` | 官方出版为 CVPR 2025，585–594；现稿写 2025 正确 | 保留 |
| `lai2025hunyuan3d` | arXiv:2501.12202 标题和首三作者 Zhao、Lai、Lin 与现稿一致；bibkey 用 Lai 不是引用事实错误 | 保留 |
| `perla2026survey` | Wiley 官方：2026-04-30，Computer Graphics Forum，e70392，DOI 10.1111/cgf.70392；现稿元数据成立 | 保留，作为领域背景和材料/投影限制背景 |
| `xu2026wondertex` | IEEE 向 Crossref 注册的数据为 2026-07，32(7)，5815–5825，DOI 10.1109/TVCG.2026.3673926；与现稿一致。IEEE 完整论文正文访问受限，本审查仅核实元数据，不增加其算法细节主张 | 保留现有有限背景引用 |
| `guzman2026adaptive`、`lv2025interpretable` | Elsevier 与 Springer 官方页面的题名、作者、卷页与现稿成立 | 属于流体 exemplar synthesis 和 procedural material graph，离本次 residual-allocation 主问题较远；精简相关工作时可删去这条旁支，不应拿来支撑本方法创新 |
| `ke2024era3d` | 官方 NeurIPS 2024 首三作者 Li、Liu、Long 和题名成立；现稿作者已正确，bibkey 的 Ke 不构成作者错误 | 保留或按正文需要精简 |

本审查没有逐条核验其余基础背景文献全部书目字段，因此不能将上述结果扩张为“所有参考文献完全正确”。没有发现 SSI、MV-Adapter、MVDiffusion、APG 的伪造文献或错配身份。

Paint3D 更正依据：[CVF 官方题名、作者与 BibTeX](https://openaccess.thecvf.com/content/CVPR2024/html/Zeng_Paint3D_Paint_Anything_3D_with_Lighting-Less_Texture_Diffusion_Models_CVPR_2024_paper.html)。其初始步骤是 depth-aware 2D diffusion 与多视图融合，随后 UV refinement，概括为 geometry-conditioned texturing pipeline 合理；若写成与所有其他模型完全相同的 synchronized multi-view architecture，则应改正。

## 建议最少新增引用及可直接用于相关工作的文字

新增 StyleID 引用可让 SSI 操作位点的区分直接落到原始方法；新增固定版本 Diffusers 与 ControlNet code 引用可明确更早工程先例。无需为了增加参考文献数量再扩展无关方法，也无需在没有同任务合法实现的情况下编造 SSI 数值基线。

> Inference-time conditioning scales and their allocation across layers or sampling progress are established controls. ControlNet's official implementation already exposes layer-dependent residual weights, and Diffusers provides temporal start/end gates. SSI further studies layer- and timestep-dependent style mixing together with scheduled geometric ControlNet conditioning. We therefore use temporal scaling as an intervention for a controlled empirical study, and contribute task-specific evidence about competitive controls, applied-scale accounting, interface boundaries and baked-texture outcomes rather than a new scheduling principle.

这段建议文字只概括已核实先例；它不声称最早性，也不把某个不同任务的调度规律宣称为本任务机制。最终稿的经验价值能否满足审稿人的新颖性要求仍需由研究问题、证据强度和期刊定位共同决定，不能用统计显著性自动“解决 R2.1”。
