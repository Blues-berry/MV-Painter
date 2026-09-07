# 交接文档：CAG-S-26-01522 一审提交状态 与 二轮审稿预案

> **【2026-09-07 复核通过：新投稿包已终审】**
> 对编辑 5 项意见做了全量复核（dblp API + Crossref API 逐条核实），结论：
> 1. [41] 与扩展版表述已删净；45 条引用与正文 \cite 一一对应（双向均无孤儿）；
> 2. 9 条 arXiv 转正式版全部正确；DreamFusion=ICLR 2023 经 dblp 确认正确（官方项目页引用块未更新，勿据此"改回"arXiv）；MV-Adapter=ICCV 2025 (pp.16377-16387, DOI 10.1109/ICCV51701.2025.01520)、Castillo=AAAI 2025 (Kohler 作者名正确)、Perla=CGF 2026 e70392 (DOI 10.1111/cgf.70392)、Lv=TVC 41(13):11195-11205 均 Crossref/dblp 核实无误；
> 3. **已修**：Guzmán C&G 2026 文章号 104509→104490（104509 是同期另一篇特刊前言的编号，数字颠倒——提交前最后一处隐患）；WonderTex TVCG 补全 32(7): 5815-5825；
> 4. 重编译 15 页 0 错 0 未定义引用，泄露扫描 0，包内 Manuscript 0907.pdf 与源 md5 一致（299b8e7）。
> EM 上传提醒：补充材料 Description 口径 'Original conference SUBMISSION (CAD/Graphics 2026, Paper #75)'；EM 元数据摘要无扩展版措辞；Article Type 选 'VSI: CAG_SS_CAD/Graphics 2026'；不传 latex.zip/marked/response letter；EM 框内文件平铺无子文件夹。

> **【2026-09-07 更新：R2 预案已失效，转为 resubmit as new】**
> 编辑决定（CAG-D-26-00954，非审稿意见）：参考文献质量整改后按**新投稿**重投。已执行：
> 1. 删除参考文献 [41]（CAD/Graphics 2026 Submission #75）及摘要/引言/结论全部"会议扩展版"表述，按原创投稿口径处理；
> 2. 九条 arXiv 引用更新为正式发表版（SyncDreamer ICLR24、Wonder3D CVPR24、Era3D NeurIPS24、Text2Tex ICCV23、TEXTure SIGGRAPH23、T2I-Adapter AAAI24、DoRA ICML24、Castillo AAAI25、MV-Adapter ICCV25），修正 [8] 作者名（Ke Q→Li P）与 [27] 作者名（Legenstein→Kohler）、[26] CFG 年份（2022→2021 workshop）、[31] FLUX 补 URL；确为预印本的（Zero123++/ImageDream/MVPainter/Hunyuan3D2.0/IP-Adapter）保留 arXiv 标识；
> 3. 新增 5 篇期刊引用（Perla CGF26 综述、Guzmán C&G26、Lv TVC25、Liu SIGGRAPH Asia24、WonderTex TVCG26），文献总数 41→45，45 条引用与条目一一对应；
> 4. 编辑在 marked 稿里发现的 [8]/[28] 乱码根因是 latexdiff 把旧版参考文献删除文本混入新条目——新投稿不再提交 marked 稿与 response letter；
> 5. Cover letter 已重写（原创口径 + 参考文献整改说明 + 中性披露会议投稿副本），标题页/图表摘要/补充材料/演示视频未变、全部复用。
> 新投稿包：`final/submission_new_0907/`（12 文件，泄露扫描全 0，主稿 15 页 0 错，摘要 245 词）。EM 元数据摘要需同步删去扩展版措辞；旧包 `submission_0907/` 仅作存档，勿再上传。本节以下 R2 流程描述仅供历史参考。

更新：2026-09-06。本文档是二轮审稿（R2）的唯一交接入口；打包细节另见 `PACKAGING_NOTES.md` 第六节。

---

## 一、投稿当前状态

- 期刊/路径：Computers & Graphics（EM 代码 CAG），VSI: CAG_SS_CAD/Graphics 2026（CAD/Graphics 2026 会议推荐，CMT Paper 75），双盲评审。
- 投稿号：**CAG-S-26-01522**。EM 内 10 个文件已上传、Build PDF（61 页）已按清单核验。
- 待办（作者自决，非合规问题）：EM 里同时传了合并稿与单独干净稿，正文在审稿 PDF 中重复出现；删不删均可 Approve。
- 会议扩展版三条专款（改题/明引+附原稿/≥30% 新材料）已全部落实并逐字验证；作者已确认 `anonymous_submission_0709_final.pdf`（12 页，2026-07-09）即 CMT Paper 75 投稿与评审版。

## 二、文件地图

| 用途 | 路径 |
|---|---|
| EM 上传终版（自然语言命名 + 0907 后缀） | `final/submission_0907/`（15 个文件） |
| 制作源/工作区 | `final/submission_package_CAG/` |
| 回信源文件（R2 回信在此续写） | `final/revision/response_letter_CAG_plain.md`（匿名版，合并稿信件源）、`response_letter_0903.md`（会议侧快照）、`response_letter.md`（最早版） |
| 会议原稿（专款要求的附件） | `final/submission_0907/Original conference paper 0907.pdf`（= 根目录 `anonymous_submission_0709_final.pdf`） |
| LaTeX 源包（R2 必传） | `final/submission_0907/latex.zip`（12 文件平铺：final_0903.tex + elsarticle.cls + cag.sty + 两 logo + fig1–7.pdf） |
| 审稿意见存档 | 根目录 `审稿意见.txt`、`0906.md`、`0904意见/` |

## 三、当前产物清单（页数 = 验证值）

| 产物 | 页数 | 说明 |
|---|---|---|
| final_0903.pdf（干净稿） | 15 | 0 错 0 未定义引用；摘要 249 词 |
| final_0903_marked.pdf | 16 | latexdiff --type=CFONT，基线 final.tex（Aug 13） |
| final_0903_with_letter.pdf（合并稿） | 22 | 信 7 + 正文 15，pdfunite 合成 |
| title_page_CAG.pdf | 1 | 含作者/单位/通讯邮箱/致谢（4 基金）；**无 COI**（已移除，独立文件承担） |
| response_letter_CAG_plain.pdf | 7 | 匿名回信（合并稿信件部分同源） |
| response_letter_0903.pdf | 8 | 会议侧带审稿意见编号版 |
| supplementary_0903.pdf | 2 | FAC 剂量-反应表 + S4 复现表 |
| Original conference paper 0907.pdf | 12 | 会议版原文，旧标题属正常 |

## 四、R2 时 EM 的硬性变化（与一审不同）

1. **必须传可编辑源文件**：EM 明文 "At revision stage, PDFs are not supported for Manuscript file, Table and Title page"。latex.zip 已备好直接传（Manuscript without author details 类型，12 文件平铺、无子文件夹——EM 不接受子文件夹）。
2. **Item Type 下拉可能出现新类型**：`Response to Reviewers`（有的期刊要求 Word 回信）和/或 `Revision with Tracked Changes`。若出现 Response to Reviewers：以 `response_to_reviewers_CAG.docx` 为模板续写后从 md 经 pandoc 重建（配方见第五节）。
3. 修改稿通常还需**逐条回信**：在 `response_letter_CAG_plain.md` 按审稿人/条目续写，每条写明改了什么、在第几节。

## 五、构建配方（踩坑记录，R2 直接照抄）

1. **主稿**：`pdflatex -interaction=nonstopmode final_0903.tex` 连续两遍。参考文献内联（thebibliography，41 条），无 bibtex 依赖。
2. **marked 版**：`latexdiff --type=CFONT final.tex final_0903.tex > final_0903_marked.tex`，编译前检查 `tab:fac` 悬空引用——若 `\DIFdel{Table~\ref{tab:fac}...}` 出现，照例把 `\ref{tab:fac}` 改成 `7`（历史遗留：Table 7 已删）。CFONT 下新增=蓝、删除=红，标题区新旧题并存属 diff 特性。
3. **信 PDF**：`pandoc <md> -o <pdf> --pdf-engine=xelatex -V fontsize=12pt -V linestretch=1.25 -V geometry:margin=2.5cm`。**margin=2.5cm 不可省**——缺它信从 7 页膨胀到 10–11 页。
4. **合并稿**：`pdfunite revision/response_letter_CAG_plain.pdf final_0903.pdf final_0903_with_letter.pdf`。
5. **ε 一律写 ASCII `epsilon`**（xelatex 会静默丢弃 Unicode ε——历史教训）。
6. **docx**：`pandoc <md> -o <docx>`（cover letter / acknowledgements / response 均此法）。
7. **title_page 有两份源**：`final/title_page_CAG.tex`（编译用）与 `final/submission_package_CAG/title_page_CAG.tex`（存档）——**必须同步改**；曾发生 root 版致谢内容丢失导致上传版缺基金（2026-09-06 已修复）。改完两边 grep 核对。

## 六、双盲合规红线（每次改稿后全包重扫）

- 泄露扫描：对全部送审 PDF/docx 跑 `grep -ciE "Libo|Xueyuan|sunlibo|Southeast|@seu"`，**必须 0**；唯一例外 Titlepage（作者信息合法存在，不送审）。
- 致谢/基金只允许出现在 titlepage + 独立 Acknowledgements 文件，**不进正文**（指南双盲节逐字禁止）；COI/Data availability 无身份信息，已入正文。
- Cover letter 禁止 funding 信息与 author declarations（指南明文）；prior art 状态须与参考文献一致（MVPainter arXiv 2025 / MV-Adapter arXiv 2024 / ControlNet ICCV 2023 / Kynkääniemi NeurIPS 2024，章节号 2.3 与 4.4）。
- 旧标题字符串（`Adapter Scaling Trade-off and Timestep-Conditioned Scheduling in Multi-view Diffusion Texture Generation`）只允许出现在两处：参考文献 [41] 会议条目、会议原稿 PDF 本体。新标题：`Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation`。

## 七、会议扩展版合规链（已闭合，R2 可能被审稿人问）

- 30% 新材料的量化口径：会议版内容指纹（pdftotext 计数）Proposition=0、holdout=0、276=0、epsilon=0 → 两阶段 epsilon-optimal 选择规则（Prop 1）与 276-object holdout 协议为期刊版新增；FAC 与 300-object pool 会议版已有（61/10 次），**不得声称新增**；页数 12→15。
- 若审稿人质疑比例：引言扩展段 (i)(ii)(iii) 即逐条答复模板；会议原稿已作 Supplementary material 附上，EM 内 Description 注明专款依据。

## 八、数据完整性红线（项目铁律）

- 用户实验数据必须真实、与论文聚合数（Table 9 等）一致；数据集划分口径固定：adapter 训练池 1,118 objects、评测池 300（probe 24 = obj_0000–0023、holdout 276 = obj_0024–0299，两集合零交集；50-object sweep、26-object audit、50-object CLIP-IQA、30-object preference 均为 pool 子集）。R2 修改不得触碰这些口径与数字，除非有新的真实实验数据。

## 九、Git 规范

- 分支 `new0529`；改前先快照提交，改后串行修改（**同一文件并行 Edit 会写冲突**——已踩两次）、逐处验证、提交推送。最新提交：bda2ad8（正文加 Data availability/COI、titlepage 修复）→ 6f4c474（Paper 75 确认入档）。

## 十、R2 流程速查（收到 modify 决定后）

1. 从 EM "Submissions Needing Revision" 进入，旧文件列表自动带出，勾选保留项。
2. 改 `final_0903.tex` → 重编译三件套 → 更新 latex.zip 与 0907 包 → md5 对齐。
3. 续写回信 md → pandoc 重建信 PDF/docx → 重新合并合并稿。
4. EM：Revised manuscript（LaTeX 源 zip）+ Marked-up + Response to Reviewers + 全套附属文件替换上传。
5. Build PDF 核对（信/回信在前、图表渲染、泄露扫描）→ Approve。
