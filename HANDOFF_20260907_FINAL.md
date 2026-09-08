# 交接文档 — C&G 投稿最终版（2026-09-07）

投稿：Computers & Graphics，按编辑决定（CAG-D-26-00954）以**全新原创投稿**重新提交。
EM 稿件编号：**CAG-S-26-01522**（见根目录 CAG-S-26-01522(1).pdf，EM 下载回执副本）。
分支：所有变更提交至 new0529 并推送。

## 1. 唯一权威版本（不要使用其他任何副本）

投稿包：final/submission_new_0907/（19 个文件，git 跟踪备份）

| 文件 | 状态 | md5 前 8 位 |
|---|---|---|
| Manuscript 0907.pdf | 15 页，6 关键词 | ff54eead |
| response to comments of reviewers 0907.pdf/.docx | 8 页终版信 | 1b297896 |
| Manuscript with response letter 0907.pdf | 23 页 = 信 8 + 稿 15 | 802afb3f |
| Marked-up manuscript 0907.pdf | 15 页，仅蓝色标新增、删除内容不显示，0 ?? | b8af03c3 |
| latex.zip | 12 文件平铺 | 5ae4b9ec |
| Supplementary material 0907.pdf | 2 页 | 7c666d71 |
| Cover letter 0907.pdf/.docx | 匿名，含 CAG-D-26-00954 透明句 | 55c65b5c |
| Titlepage 0907.pdf | 含 Wuxi 实验室资助 | 696a76e8 |
| Original conference submission 0907.pdf | 编辑许可命名，正文不引用 | c911ff91 |
| 其余（GA/Demo/stills/Highlights/Acknowledgements/Declaration） | 同前 | — |

关键门禁（全部通过）：
- 正文/信件 0 处 "earlier version"（信中仅 2 处认可的否定句）、0 处 preliminary；extended 仅余 4 处良性用法
- 数据口径：主 adapter 训练池 = 1,118；strong-residual/FAC 实例 = 1,706（信、正文、补充材料一致）
- 摘要 0.96 dB 明确归因 "full 300-object pooled evaluation with the main adapter"
- 关键词 6 个（EM 表单上限），已删 texture quality assessment
- FAC 旧正结果已标 superseded（"initial comparison" 表述）

## 2. 源文件与构建

| 源 | 说明 |
|---|---|
| final/final_0903.tex | 正文唯一源（pdflatex/latexmk）→ final_0903.pdf → 同步为包内 Manuscript 0907.pdf |
| final/final_0903_marked.tex + final_0903_marked_addonly.tex | 前者为 latexdiff 全量标记源（经参考文献整体替换 + tab:fac→Table 7 手术），后者由 strip_difdel.py 剥离删除内容生成（投稿用）；勿重跑 latexdiff |
| final/supplementary_0903.tex | 补充材料源（含复现表：checkpoint MD5、种子、协议） |
| final/revision/response_letter_new0907.md | 回复信唯一源（已入库）：pandoc 直转 docx；pandoc --pdf-engine=xelatex 转 PDF |
| final/revision/cover_letter_new0907.md | 封面信源 |
| final/title_page_CAG.tex、graphical_abstract_CAG.tex | 扉页 / 图文摘要 |
| final/output/、cls/sty/bst 符号链接、fig1-7.pdf、logo | 构建依赖，勿移动（output/ 被符号链接依赖） |
| final/figure/、final/figures/ | 图 1-7 矢量源与中间产物 |

重建命令（在 final/ 下）：

    latexmk -pdf -interaction=nonstopmode final_0903.tex
    latexmk -pdf -interaction=nonstopmode final_0903_marked.tex
    python3 strip_difdel.py && latexmk -pdf -interaction=nonstopmode final_0903_marked_addonly.tex
    pandoc revision/response_letter_new0907.md -o "submission_new_0907/response to comments of reviewers 0907.docx"
    pandoc revision/response_letter_new0907.md -o "submission_new_0907/response to comments of reviewers 0907.pdf" --pdf-engine=xelatex
    gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="submission_new_0907/Manuscript with response letter 0907.pdf" "submission_new_0907/response to comments of reviewers 0907.pdf" "submission_new_0907/Manuscript 0907.pdf"

本机 soffice 损坏：docx→pdf 一律走 pandoc/xelatex。

## 3. 本次整理归档（均未删除）

- final/archive/submission_0907_deprecated/ — 9-6 旧投稿包（旧命名 "Revised manuscript…"、含被禁扩展版框架，正文稿 md5 b865cf99…），禁止使用
- final/archive/final_legacy_misc_0907/legacy_pdfs|legacy_letters|legacy_builds/ — 7 月各版 PDF、旧信件、旧构建中间物、final_submit_figure(73M)、submission/、tmp/(168M)
- final/archive/submission_0907_legacy/ — 更早（0904 时代）快照，原有
- archive_workspace_0907/（根目录）— 旧交接文档 HANDOFF_0904/HANDOFF_TCAS、0904意见、0906.md、find/txt/paper_text 草稿、旧 zip
- archive3.0/ — 更早项目归档，原有

## 4. 根目录在用文件

- 审稿意见.txt — 三位审稿人 + 编辑意见原文（本轮整改依据）
- TCAS_EVIDENCE_LEDGER.md — 数据/结论证据台账
- 用户实验原始结果.CSV — 用户实验原始数据（真实数据，勿动）
- CAG-S-26-01522(1).pdf — EM 下载的投稿副本回执
- TCAS_Demo.pptx、代码与数据目录（MVPainter/ geotex/ data/ checkpoints/ mvpoutput/ scripts/ assets/）、blender 工具链、final/tools/（渲染工具链，1G）

## 5. EM 提交要点备忘

- Article Type：VSI: CAG_SS_CAD/Graphics 2026；PDF-only 初投可行，latex 源码 zip 不要上传（EM 会生成 text-only 版丢回复信）
- Keywords 限 6：multi-view diffusion model / 3D texture generation / adapter scaling / timestep-conditioned scaling / shape-texture trade-off / geometric control
- Funding 填系统元数据；匿名文件内不含作者信息
- ε 敏感性边界（如日后需要）：选择结果为 C3 当且仅当约 0.077 ≤ ε < 0.574 dB（基于点估计，成员条件为 ≥）
- 已冻结项：摘要措辞、Proposition 1、第二 backbone 实验、category composition、参考文献
