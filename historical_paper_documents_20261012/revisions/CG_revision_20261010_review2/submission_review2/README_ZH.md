# C&G 独立修订副本 Review2

原版本未被覆盖。新副本位于 `/4T/CXY/MV-Painter/CG_revision_20261010_review2`，基于已整合 matched300、native50、bake10 的最新稿，不是另起论文或更改实验条件。

阅读入口在 `submission_review2`：正文、01549 对照标记稿、补充材料、审稿回复、真实输出视频和源码包。

本次完成：
- 图内长标题、选择说明及统计文字移到图注，保留短方法名及案例编号。
- 用纯矢量方法图区分参考条件与几何输入；删除旧生成艺术底图与已废弃的重建脚本。
- 主文烘焙图加入 GT-256 和 Linear，以及同像素区域局部图；七对象补充图拆成独立大图。
- 补入已有 MV-Adapter 的同对象效果图，不重新推理、不搜索条件。
- 修正 S7 对照方向、图/章节引用及“完整六视角面板”的实际覆盖范围。
- 新增队列身份表、实际外观讨论、GT 校准数值及技术筛选分解，恢复报告原来的阶段主比较。
- 把部署收益收紧为小幅相对烘焙指标结果，并明确默认 GeoTex 对照、接缝/PBR、FAC 和共同外观失败仍未解决。

数据说明：所有既有生成条件数值保留；新增 GT 汇总行从新十对象原始 CSV 复算。旧五与新十按 source_id 分开。`evidence/MATCHED300_SEED_LOOKUP.json` 提供原始 300 对象 seed 关联，不覆盖留档 CSV 的空字段。`Reproduction_inherited_1008.zip` 是上一版已验证复算包，文件名明确标记沿用；本轮源码包含新稿与展示代码。

重建：在 manuscript 目录运行 build_revision_1008.sh、build_supplement_1008.sh、build_marked_up_1008.sh。图由 scripts/build_review_figures.py 重建，需要 Pillow、CairoSVG 和原始研究输出；本机已执行。生成 PDF 不需重跑模型。图/来源哈希及数值保持检查在 VALIDATION_REVIEW2.json。

没有新训练、GPU 推理或期刊上传。排版修改不能消除实际生成失真：共同棕色纹理原因未恢复；GeoTex unset-scale 默认输出尚缺；10 对象是技术兼容 pilot；R2.1 创新性仍未充分解决。这些边界已同步到正文和回复。
