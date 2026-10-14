# Figure 2 readability decision — V4 continuation

实际比较使用 c3017645 四行主文第7页和本轮三行主文第7页，见 `FIGURE2_FOUR_VS_THREE_ACTUAL_PAGES_V4.pdf`。四行图的侧边注释占用105pt，图像框约83pt；三行把选例说明放在行上方，图像框100pt，五列标题为8.5pt设计字号，图件整体从452pt降至390pt。所有 Target、Fixed Low、C3、Fixed High、Generic Linear 保留。

选择三行：Green Iguan 为输入颜色/纹理属性例，Mosque 为明确事后正向例，Specimen 103 为明确事后负向例。移出主文的 Lipno 中位例在四行实际页面及其来源清单保留；它的简化灰色目标及细小框状输出对当前科学解释增加有限。没有筛除任何数值队列或方法。

Target 是512×512源条件图；生成显示取同一六视角输出的 [0,0,256,256] 首块，即 raw000。源图和完整输出 mosaic 的 SHA 与既有索引逐个匹配；所有条件相机、checkpoint、runner 及显示帧身份一致。完整对象显示采用共同白底与等比例适配，没有逐条件裁剪或颜色处理。正向/负向名称针对 C3−Fixed Low 的既有对象级 FG-PSNR，不代表总体表现或材质质量。
