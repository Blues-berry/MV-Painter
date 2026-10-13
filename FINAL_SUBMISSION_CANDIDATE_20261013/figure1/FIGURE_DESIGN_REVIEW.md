# Figure 1 最后一次文献参照设计审阅

2026-10-13。本次实际查看了正式论文中的方法图及紧邻方法文字；不以项目页介绍代替方法图。下面的构图结论是审阅判断，不是论文作者对TCAS图的背书。

| 原始来源与实际图 | 方法和视觉关联 | 本图可吸收的有限经验 |
|---|---|---|
| [MVPainter 正式论文](https://arxiv.org/pdf/2505.12635)，Fig.3 “Overview of our framework”，PDF p3 | 图以真实多视图、条件图和纹理网格交代生成/投影流程；旁文区分数据处理、几何条件和PBR提取 | 保留真实输入与六视图的显著面积。当前TCAS没有提出PBR模块，不移植其整条流程 |
| [MVPaint CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Cheng_MVPaint_Synchronized_Multi-View_Diffusion_for_Painting_Anything_3D_CVPR_2025_paper.pdf)，Fig.2 “The Framework Overview of MVPaint”，PDF p3 | 多视图生成、空间补全和UV细化分区，图像解释各阶段作用；旁文对应三个方法阶段 | 当前独立bake分区应继续保留，但它是selected downstream evaluation，不可照抄为新增方法阶段 |
| [Paint3D CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Zeng_Paint3D_Paint_Anything_3D_with_Lighting-Less_Texture_Diffusion_Models_CVPR_2024_paper.pdf)，Fig.3 “The overview of our coarse-to-fine framework”，PDF p3 | 上下两层区分粗生成/UV细化，真实图像贯穿；图例明确冻结/训练归属，旁文解释分别如何生成和细化纹理 | 采用颜色和文字明确existing/proposed归属，保留当前灰色Existing wrapper与青绿色TCAS requested schedule |
| [MV-Adapter ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.pdf)，Fig.2 “Inference pipeline”，PDF p3；Fig.3详细架构，p4 | Fig.2用灰色预训练网络及单独颜色的adapter简明说明插入点；Fig.3和方法文字再展开condition guider及decoupled attention | TCAS overview应保留示意而非凭空细化层架构；路径标签靠近其对应线，比增加装饰网络方块更有效 |
| 原01549 submitted manuscript，Fig.1 “Method overview”，PDF p4 | 包含FAC optional learned extension及较强的功能性叙述，输出示例很小，TCAS直接关联hidden-feature addition | 仅继承任务/注入点关系；当前版本移除了FAC和旧图暗示的额外方法创新，准确区分TCAS请求、既有cap和实际残差，不恢复旧模块 |

## 唯一建议的最终限定调整

当前主图已经保留六视图大图、独立Bake10、既有cap/TCAS请求归属和真正可编辑的机制。继续重设计不会带来与风险相称的收益。最后只收紧**Reference conditioning标签与其路径的空间联系**：现有`reference-path-label1/2`位于(525,146/180)，其路径在y≈265；建议下移约50单位到y≈196/230，保持其x位置和字号，并确认不碰到中央`frozen-heading`。这样可减少中央上部悬空标注，提高3秒阅读时的条件归属识别。其余路径、公式、调度、主图、相机顺序、独立bake和来源记录均保留。

这是一项标签定位修正，不增加模块、不改科学内容、不重新生成概念图，也不再开启布局投票。修改后只需出版宽度渲染核查，作者审美认可不得由自动检查替代。

## 实际查看证据文件

均在`fig1_redesign_png_to_svg/literature_visual/`：

- `mvpainter_method.png`：正式Fig.3及紧邻文字。
- `mvpaint_method.png`：正式Fig.2及紧邻文字。
- `paint3d_method.png`：正式Fig.3及紧邻文字。
- `mv_adapter_page3.png`：正式Fig.2及方法入口。
- `mv_adapter_page4.png`：正式Fig.3及详细方法。
- `original_submitted_fig1.png`：01549 submitted PDF p4，含Fig.1、旧注入公式和邻近方法。

当前待优化图另为`fig1_tcas_preview.png`，已在此前本轮独立视觉检查实际查看。原01549使用的本地源为`/4T/CXY/MV-Painter/1008/manuscript/source_01549/01549_submitted_manuscript_0907.pdf`；截图核对确认Fig.1实际含FAC，不能把旧图创新叙事恢复到本轮修订。

## 最终执行决定

采用限定优化并结束图件设计。为避免下移标签与Frozen U-Net标题重叠，最终两行标签置于(480,196/230)，字号不变；其他图像、箭头和机制保留。源文件在独立候选figure1/中，原图未覆盖。新脚本由包内原始图像及trace重建，保留原始路径与SHA。非阻断限制：真实UV atlas较稀疏、主样本颜色不保真；均作为科学结果保留，作者视觉批准仍待定。
