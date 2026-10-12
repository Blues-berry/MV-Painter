# 第15版投稿文件使用说明

Upload/ 中为本轮最终投稿候选文件；Editable/ 中为对应可编辑文本和来源说明。文件包准备与 GitHub 上传不触发实际投稿。

原正式底稿 final/submission_new_0907 保持原样；旧版 Cover Letter、Highlights、图形摘要和演示视频没有作为当前结论继续使用。新版标题带 Controlled Empirical Study 副标题，主文、补充、Title Page、Cover Letter 和回复保持一致。

| 建议上传项 | 当前文件 |
|---|---|
| Manuscript without author details | Manuscript_round_015.pdf |
| Marked-up manuscript | Marked-up_Manuscript_round_015.pdf |
| Response to reviewers | Response_to_Reviewers_round_015.pdf / .docx |
| Title Page（作者信息，不并入匿名主稿） | Title_Page_round_015.pdf / .docx |
| Anonymous Cover Letter | Cover_Letter_round_015.pdf / .docx |
| Highlights（单独可编辑文件） | Highlights_round_015.docx |
| Declaration of Interest | Declaration_of_Interest_round_015.docx |
| Acknowledgements / Funding（编辑端） | Acknowledgements_round_015.docx |
| Graphical Abstract | Graphical_Abstract_round_015.pdf / .png；SVG 可编辑 |
| Supplementary Material | Supplementary_Material_round_015.pdf |
| LaTeX source files | LaTeX_Source_round_015.zip：所有成员同一目录层级 |
| Recovered FAC code（独立源码包） | Recovered_FAC_Code_round_015.zip：恢复源码、入口差别及无需基础模型的离线组件检查；历史全模型重放未完成 |
| Reproduction evidence | Reproduction_round_015.zip：已在独立目录复算，无需 GPU/权重 |
| Example 3D meshes（独立样例包） | Mesh_Examples_round_015.zip：GT/Native/Fixed Mean/Late-high 四个原始导出及许可记录 |
| Video 1 / still | Video_1_GeoTex_Baked_round_015.mp4 / Video_1_Still_round_015.png |
| Video 2 / still | Video_2_GSO_Exported_Mesh_round_015.mp4 / Video_2_Still_round_015.png |
| Historical conference manuscript（明确标为历史附件） | Original_Conference_Submission_0907.pdf |

每个文件独立上传；不要把整个 Upload ZIP 当作匿名 manuscript。保留原编辑系统中的 VSI: CAG_SS_CAD/Graphics 2026 类型和原稿件关系。旧封面涉及先前 CAG-D-26-00954，但最新稿件导出未给出可验证的当前稿号；本轮 Cover Letter 不编造或替换编辑系统稿号。

匿名主文、补充、回复、Cover Letter 与源稿不含本研究作者姓名、邮箱或资助机构信息。Title Page 和 Acknowledgements 单独保留真实信息；作者顺序、通讯信息、资助和利益声明按此前正式材料继承，未推测新的作者角色。当前作者事实/声明和全体作者对最终稿的认可，应在正式提交时由作者核实；包中不声称已取得新的批准。

视觉检验用于发现布局、标签和图文错配，不能认证物理材质保真或替代科学复核。仅取消 no-adapter 失真视觉列，数值和失败证据保持完整。两条烘焙链不合并。

当前核查来源（2026-10-12）：
- C&G 官方 Guide for Authors：https://www.sciencedirect.com/journal/computers-and-graphics/publish/guide-for-authors 。当前直连返回403，不能声称已逐项获取最新全文；模板与已投稿 0907 包逐项对照。
- Elsevier LaTeX instructions：https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions 。源码包所有文件同层级；三份 TeX 均独立编译并核对文字/排版。
- Elsevier Highlights：https://www.elsevier.support/publishing/answer/how-do-i-include-highlights-with-my-manuscript 。提供四条、每条不超过85字符的独立 Word 文件。
- Elsevier 匿名评审说明：https://researcheracademy.elsevier.com/uploads/2017-11/Double-Blind%20Peer%20Review.pdf 。作者信息独立；检查审稿文件及元数据。
- Elsevier AI policy（2026年6月更新）：https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals 。当前主文说明文本/代码/视觉检查的 AI 辅助；实验图没有生成式修图；图形摘要来自可复算矢量/统计绘图。

编辑系统动态字段、任何特别修回指令和最新指南全文，以实际提交界面为准；本包已经准备相应文件，未把无法访问的指南推断为已确认规则。

第15版新增对象/种子稳定性、四端点支配及共享UV诊断，均明确为后验补充。核心统计保持第14版原值。复算ZIP已独立运行三个统计脚本；FAC源码ZIP已用snapshot-only模式在独立目录通过三个不同CPU控制器fixture。训练/评价入口完整孤立执行及历史1706对象身份未验证。84个恢复源文件的逐文件哈希和入口区别随包交付，不声称公开托管或取得期刊复现徽章。
