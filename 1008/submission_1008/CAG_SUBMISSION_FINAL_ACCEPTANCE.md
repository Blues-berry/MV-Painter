# Computers & Graphics 1008 二轮投稿最终验收

**状态：** `AUTHOR_REVIEW_READY / DRAFT`  
**捕获时间：** `2026-10-09T07:15:50Z` UTC  
**投稿批准：** `SUBMISSION_APPROVED=NO`  
**投稿状态：** 未向期刊上传

本稿以 2026-09-07 已完成第一轮修订的正式稿 01549 为基线。01549 原始 TeX 未改动。

## 科学主张

论文保留 TCAS，将其描述为 GeoTex-Adapter 残差路径上的任务特定免训练推理干预。Fresh C 的 C3−GFL FG-PSNR 为 `+0.522352 dB`（对象级 bootstrap 95% CI `[+0.404160,+0.640669]`）。GFH 与 Generic Linear 在四个展示端点的队列均值均优于 C3；C3 与 GFL 的 deep/middle 累积应用尺度是 82.5 与 62.5，比较不能单独解释为时间调度效应。独立 stage-placement follow-up 中 Temporal L–L–H 在六个正式端点都优于 C3；不声称 C3 普遍最优。纹理变化指标不称为纹理保真，不声称 3D bake、seam、PBR 或原生默认 Adapter 已通过验证。

颜色审计只支持“全局 appearance embedding 可控制所选样例的 chroma”，不支持完整根因或有效修复。Fresh B 缓存/来源不一致是合理但未证实的贡献因素。C1 通过数值门但未通过锁定视觉门；B2 八次生成后未通过预设数值门，未显示明确视觉修正。没有独立 Fresh B 修复验证。

## 第二轮状态

R1.1 `PARTIAL`; R1.2 `ADDRESSED WITH LIMITS`; R1.3 `ADDRESSED WITH LIMITS`; R1.4 `PARTIAL`; R1.5 `PARTIAL, first-round result retained`; R2.1 `PARTIAL, editorial novelty risk`; R2.2 `ADDRESSED by withdrawing CAI claim`; R2.3 `NOT FULLY ANSWERED`; R3 `ACKNOWLEDGED`. 生产 additive-bootstrap 的 `p=0.6523` 交互推断已撤回。解释和剩余限制见 [FINAL_CG_SUBMISSION_READINESS.md](FINAL_CG_SUBMISSION_READINESS.md)。

第二轮审稿原文逐字认证仍未完成：保存的 PDF 标注为 initial-submission reviews。回复信按二轮要求矩阵和证据撰写；这个来源限制已披露，未被说成已认证。

## 编译和文件验收

- 主文 13 页，SHA-256 `29e48af0348377bd45f887a3be662937c83857a58aee67af70c12727c22df6d5`。
- 标注稿 13 页，SHA-256 `3c78161c31d68163007ea8f337c06b8259ad90fb96d39a789958974ff23447d5`。
- Supplement 11 页，SHA-256 `8bc53b24ef4b43a420d40356e8f91daca5137852c6aab7cbda418932f8c5b898`。
- Response 5 页，SHA-256 `c9cebb9dc8198ec9077d36f3dcf1dad084a9b064793bce9678303228a28d96a0`；作者审阅目录 DOCX SHA-256 `0cbd727f360bd8df865738ccdbd14aab6fdd18ec6706a78c8c431a65465bfe96`。投稿包 DOCX 由同一 Markdown 生成，按包内 manifest/checksum 校验。
- 源 ZIP 44 entries，32,009,054 bytes，CRC 通过，SHA-256 `fcfecf9787b087296bd922301f59953d445795815ba4b7253aee9e4bff74c37c`；主文和 Supplement TeX 在 ZIP 中与活动源逐字节相同。ZIP 不含 JSON、NPZ、checkpoint、GLB 或生成图像数据。
- 空目录解压重建主文、Supplement、标注稿分别 13、11、13 页。三份脚本各执行两遍 pdfLaTeX；第二遍无未解析引用，提取文本与交付 PDF 相符。
- 内置编辑器 LaTeX 编译器报告平台 standard directories 不可用；已用项目脚本和干净源包完成构建验证。
- `SUBMISSION_FILE_MANIFEST.csv` 与 `SHA256SUMS.txt` 在 assembler 刷新后校验。详见 `Author_Review/SOURCE_PACKAGE_BUILD_CHECK.md`。

## 状态门

`MAIN_SINGLE_EDITING_AUTHORITY = PARTIAL`  
`ALL_RELEVANT_BRANCH_CONTENT_REVIEWED = YES`  
`UNIQUE_VALUABLE_SOURCES_ACCOUNTED_FOR = YES`  
`PENDING_117_DISPOSITIONS_RESOLVED_OR_EXPLICITLY_BLOCKED = YES`  
`BULK_EXPERIMENT_DATA_PRESERVED = YES`  
`UNSAFE_MERGES_AVOIDED = YES`  
`SCIENTIFIC_CLAIMS_CONSISTENT = YES`  
`REVIEW_RESPONSE_MATCHES_PAPER = YES`  
`LATEX_BUILD_PASSED = YES`  
`PRIVATE_MAIN_SYNCED = YES`  
`SUBMISSION_APPROVED = NO`

`MAIN_SINGLE_EDITING_AUTHORITY=PARTIAL` 的原因是编辑器根目录尚未通过工具切换。请作者手动 Open Folder `/4T/MV-Painter-main`，并确认 Source Control 顶部为 `main`。

## 作者上传前核验

核实作者/通讯信息、题名页、基金致谢和利益声明；审阅仍标为 `DRAFT` 的 cover letter、research highlights、graphical abstract、title page；确认当前 manuscript ID、编辑部说明、0907 会议稿附件、图形摘要或演示媒体是否需要。未得到作者确认前不投稿。

私有投稿目录：[Blues-berry/MVPainter — `1008/submission_1008`](https://github.com/Blues-berry/MVPainter/tree/main/1008/submission_1008)。
