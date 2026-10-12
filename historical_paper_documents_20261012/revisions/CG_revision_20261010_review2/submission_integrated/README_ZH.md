# C&G 独立修订副本：整合版

最新阅读入口：`submission_integrated`。原始候选稿没有覆盖；上一轮交付保留在 `submission_review2`，本轮修改前的源码保留在 `archive/layout_before_integration`。

本轮整合后的正文 18 页，补充材料 31 页。正文图8集中展示 Source、GT-256、Fixed Mean、Late-high；七控制的完整烘焙对照放在补充图S2–S8。正文图9展示 Target、Fixed Mean、Middle-high、Late-high，补充图S9保留全部原生条件。图5保留原有共享局部ROI，图6、7、8、9只展示共享完整对象框。每对象所有条件采用相同框与等比例缩放，未修色、重绘或替换实验结果。

方法图改为简洁矢量示意，图内仅保留方法名、输入输出及必要数值；长说明进入图注。移除造成大面积空白的强制浮动屏障，并修正图7局部图、S1六视角覆盖范围的过时描述。

阅读详细科学判断：`INDEPENDENT_REVIEW_ZH.md`（初审记录及当前处置状态）与 `LAYOUT_INTEGRATION_ZH.md`。数据、队列身份、原阶段主比较及GT校准数值见正文/补充。所有原生成条件数值保持不变；旧五、新十及历史N=20未合并。matched300 seed关联见 `evidence/MATCHED300_SEED_LOOKUP.json`。

重建：在 manuscript 下运行 build_revision_1008.sh、build_supplement_1008.sh、build_marked_up_1008.sh。图由 scripts/build_review_figures.py 重建，需要 Pillow、NumPy、CairoSVG 及原始图源；交付的PDF和图资产可直接编译，无需模型推理。VALIDATION_INTEGRATED.json记录源文件哈希、表格行、引用与交付包一致性。

`Reproduction_inherited_1008.zip`及视频沿用已有交付，并明确标记。没有新训练、GPU推理或期刊上传。GeoTex真正默认输出、共同棕色失真的完整原因、接缝/PBR、FAC缺口及R2.1创新性仍未解决；本轮完善展示和证据解释，不能据此认定实用外观质量已修好。
