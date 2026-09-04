# 打包说明日志（PACKAGING NOTES）

- 日期：2026-09-03
- 基准 commit：eaa078b（含本轮 tex 平铺引用修改）
- 目标期刊：Computers & Graphics（Elsevier），特刊 VSI: CAG_SS_CAD/Graphics 2026（CAD/Graphics 2026 推荐稿，Paper 75）
- 提交系统：Editorial Manager（https://www.editorialmanager.com/cag/）
- 截止：2026-09-10 23:59 GMT

## 一、LaTeX 源码包（latex.zip）结构

全部 12 个文件**平铺在 zip 根层级，无任何子文件夹**（关键要求，见下节依据）：

| 文件 | 用途 | 必要性 |
|---|---|---|
| final_0903.tex | 主稿源文件（引用写法为 `\includegraphics{figX.pdf}` 平铺形式） | 必须 |
| elsarticle.cls | Elsevier 文档类 | 必须 |
| cag.sty | CAG 期刊样式（内部引用 cag-logo / elsevier-logo） | 必须（EM 的 TeX Live 不含此样式） |
| cag-logo.pdf | cag.sty 标题区期刊 logo（`\def\jnllogo{cag-logo}` 硬依赖） | 必须 |
| elsevier-logo.pdf | cag.sty 标题区出版社 logo（`\def\elslogo{elsevier-logo}` 硬依赖） | 必须 |
| fig1.pdf – fig7.pdf | 七张插图（与 tex 引用文件名一一对应） | 必须 |

注：参考文献为内嵌 `thebibliography` 环境，无 .bib/.bst/.bbl，故不含此类文件。

## 二、打包依据

1. **官方要求（Elsevier / EM）**："Can I use subfolders in my TeX submission files? No, LaTeX submissions containing subfolders cannot be processed by EM. All submission files must be stored at the same folder level."（Elsevier 官方 LaTeX 投稿说明）。因此 tex 中原 `figures/figX.pdf` 引用已改为平铺 `figX.pdf`，zip 内一律平铺。
2. **成功先例**：参照师兄已录用稿件（submissions revise.zip 内 latex.zip）——插图 PDF 全部平铺在 zip 根层级，cls/bst 等支持文件一并打包。
3. **样式缺失处理**：官方提示 "Missing LaTeX style file? …please upload your style file separately."——cag.sty 为 CAG 专用样式，EM 环境没有，必须随包上传；elsarticle.cls 一并附上以保证版本一致。

## 三、验证方式

- 解包至全新目录，`pdflatex final_0903.tex` 连续两遍（无 bibtex 依赖）：**14 页**、0 错误、无未定义引用；表体全部恢复后仅剩标题区 logo 两处 <1.1pt 的历史 overfull（无实质影响），表格无超宽。
- 排版基准：8 张表均不含 `\resizebox`；多数表 `\small`，3 张宽表（probe/CLIP-IQA/preference）用 `\footnotesize` + 收紧 `\tabcolsep`（3–4pt）以适配单栏宽。
- 2026-09-04 更新：恢复 7 张表体（源自 0902 结构版与 final_submit 版的同源数据，已与 CSV/正文逐项核对）、FAC 反转说明段、fig1 裁切内嵌 caption、fig7 caption 方向修正、补引 6 篇文献（T2I-Adapter/Kynkääniemi 2024/Paint3D/MVPaint/Hunyuan3D 2.0/CLIP-IQA）、58.1%/+40.6 数字统一；页数 13 → **14**；marked 版 15 页；合并稿 21 页（信 7 + 正文 14）。信 PDF 由 response_letter_CAG_plain.md 经 pandoc(xelatex, 12pt, linestretch 1.25) 重新生成。
- 2026-09-04 二次更新（外部意见核查后收口，正文仍 **14 页**、marked 15 页、合并稿 21 页、0 错误）：
  1. 术语统一：全文 "300-object validation set/pool" 改为 **"300-object evaluation pool"**（摘要、贡献 (3)(4)、§4.1 四集合定义、§4.3/4.4/4.5、结论；probe=前 24 + holdout=276 已在首现处标注），Table 4/5 caption 注明 pooled statistics 含 24 个 probe 对象；不再把含 probe 的 300 称为独立 validation。
  2. 新增 **Table 9（§4.7）**：disjoint 276-object holdout 调度迁移表（trapezoid/Gaussian peak/linear warm-up/cosine bump vs C3，FG-SSIM、PSNR、ΔPSNR 95% CI、win 数）；数字与 holdout_summary.json 及 §4.7 文字逐项一致（+0.258/+0.324/+0.323/+0.902 dB，206/232/214/253 wins）。
  3. §4.6 补句：**"No configuration or hyperparameter was selected on any evaluation object"**（七配置全部报告于补充材料，关闭模型选择 leakage 质疑）。
  4. Limitations 补句：schedule **"has not yet been validated on a different geometry-conditioned multi-view diffusion backbone"**（与信 R2-1 一致）。
  5. 信四处同步：R2-1 弱化 "diffusion process itself" 过强句（正文同款已删，信漏改）；R1-2 补充材料复现表指引；R1-3 "30 objects drawn from the evaluation pool"；R3-1 指引 Table 9。
  6. Supplementary 新增 **S4 Reproducibility table**（数据源/渲染/双训练池 1118+1706/300 池 24+276 划分/零重叠/base pipeline 与 checkpoint/adapter checkpoint refattn_v1 与 geotex_v2_ema_final.pt（MD5 a74cc1d1…）/分辨率/views/scheduler/50 步/seed 42/无 text prompt/外观与几何条件/指标实现/统计口径/代码 snapshot 194bce2）；supplementary 现 2 页。
  7. Proposition 1 维持 0903 晚已修的 ε 等价边界版本（Remark 1: CI 下界 +0.006 dB ≪ ε=0.1 dB），未再改动。
- 2026-09-04 三次更新（摘要语病最小修复，正文仍 **14 页**、marked 15 页、合并稿 21 页、0 错误）：摘要 243 词（<250 官方上限）。仅修零争议语病，不动结构与限定语：① "without re-search" 自造连字符词消除（摘要/贡献(3)/§4.1/§4.5 共 4 处统一为 "without further search / without any further schedule search / not searched again"）；② 摘要 "chosen only on" → "selected using only"（与 §4.1 措辞统一，消歧义）；③ "being preferred" → "receiving higher preference"（平行结构）。第一句结构、结尾双重限定语、guardrails 短语、"a blunt control" 隐喻均**刻意保留**（R2 防御策略与增量原则）。信与补充材料无 re-search、未引用摘要原文，无需同步。

## 四、EM 上传对照表

| EM 上传项（Item/类型） | 本包文件 |
|---|---|
| Manuscript（LaTeX 主文件） | final_0903.tex（+ latex.zip 或逐个上传 tex/cls/sty/logo/fig1–7） |
| Manuscript PDF（系统 Build PDF 后核准） | final_0903.pdf |
| Response to Reviewers | response_to_reviewers_CAG.pdf（docx 备用） |
| Marked-up version（修订标注版） | final_0903_marked.pdf |
| Supplementary material | supplementary_0903.pdf（FAC 七配置剂量-反应表，正文 §4.6 所引） |
| Title page | title_page_CAG.pdf |
| Cover Letter | cover_letter_CAG.docx / .md |
| Highlights | highlights_CAG.docx / .md（5 条，每条 ≤85 字符） |
| Graphical Abstract | graphical_abstract_CAG.pdf |
| Declaration of Interest | Declaration_of_Interest_Statement.docx |
| Video / 演示材料（可选附件） | TCAS_Demo.mp4（由 TCAS_Demo_fixed.pptx 导出） |

- 合并稿 `final_0903_with_letter.pdf`（**21 页 = 回复信 7 页 + 正文 14 页**）按会议要求"信附于修改稿开头"制作，现**已放入本包**；EM 上传时可将合并稿作为 Manuscript PDF 上传（同时照常提供 latex.zip 源码），信另在 Response to Reviewers 项单独上传，两种方式均满足会议字面要求。
- Article Type 步骤选择 **VSI: CAG_SS_CAD/Graphics 2026**。

## 五、注意事项

1. 上传 demo 请用包内 `TCAS_Demo_fixed.pptx` / `TCAS_Demo.mp4`；仓库根目录的 `TCAS_Demo.pptx` 为旧版，勿传。
2. 包内已无 `figures/` 子目录（2026-09-04 清理）；fig1–7.pdf 平铺置于包根目录并与 latex.zip 内文件 md5 一致，手工上传时直接选取根目录文件即可。
3. latex.zip 内不要加顶层目录前缀，也不要再塞入子文件夹，否则 EM 构建失败。
4. 如 EM Build PDF 出现引用问号，通常是 bib 未编译所致；本稿参考文献内嵌，不受影响。
