# r2 源码包说明

解压 `LaTeX_Source_conservative_submission_r2.zip` 后，在包根目录运行：

```bash
bash manuscript/build_clean_conservative_submission_r2.sh
bash manuscript/build_marked_conservative_submission_r2.sh
bash manuscript/build_supplement_conservative_submission_r2.sh
bash review/build_response_conservative_submission_r2.sh
```

压缩包包含 r2 正文、补充材料、01549 对照源码与期刊样式、图表、回复信和构建脚本，以及历史分析材料与 Round 12 统计证据。生成的 768 张 Round 12 图片不重复打包；对象行、协议、代码、身份清单和原文件/像素哈希均已保存。目标工作区的原始图片仍存在时，证据校验器会逐张核对文件哈希和 RGB 像素哈希。

回复信以 Markdown 为唯一内容源，构建脚本据此生成 TeX、PDF 与 DOCX。归档不包含模型权重，独立重建需要安装 TeX、Pandoc 和 PDF 工具链。
