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

- 解包至全新目录，`pdflatex final_0903.tex` 连续两遍（无 bibtex 依赖）：14 页、0 错误、无未定义引用。
- 编译产物与正式提交 PDF 字节数一致（3,660,648 字节基准），即 zip 内容与已编译 PDF 完全同源。

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

- 合并稿 `final_0903_with_letter.pdf`（20 页 = 回复信 6 页 + 正文 14 页）按会议要求"信附于修改稿开头"制作，存于 `final/` 根目录；若 EM 按分件上传则以上表为准，不重复上传合并稿。
- Article Type 步骤选择 **VSI: CAG_SS_CAD/Graphics 2026**。

## 五、注意事项

1. 上传 demo 请用包内 `TCAS_Demo_fixed.pptx` / `TCAS_Demo.mp4`；仓库根目录的 `TCAS_Demo.pptx` 为旧版，勿传。
2. `figures/` 子目录仅用于本地编译（`final/figures/`），不属于 EM 上传内容。
3. latex.zip 内不要加顶层目录前缀，也不要再塞入子文件夹，否则 EM 构建失败。
4. 如 EM Build PDF 出现引用问号，通常是 bib 未编译所致；本稿参考文献内嵌，不受影响。
