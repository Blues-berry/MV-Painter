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
- 2026-09-04 四次更新（Demo 同步）：`TCAS_Demo_fixed.pptx` 第 10 页旧术语与论文新稿冲突，已改——"the 300-object validation set, with no re-search on the validation objects" → "**the 300-object evaluation pool, with no further search on the evaluation objects**"（与摘要/正文/信完全同措辞）；其余 12 页核查无冲突（slide12 FAC 标题已与 §4.6 一致）。`TCAS_Demo.mp4` 由更新后 pptx 重导：LibreOffice→PDF→PNG→ffmpeg，参数与旧版一致（1920×1080, 30fps, 60.2s，13 页轮播）。根目录旧版 `TCAS_Demo.pptx`（slide10 存在文字重复 bug）已用最新版覆盖，两处 md5 一致（799df40a…），不再存在新旧两版。
- 2026-09-04 五次更新（配音版 Demo）：新增 `TCAS_Demo_narrated.mp4`（1920×1080/30fps，**2 分 53 秒**，5.0MB）与配音稿 `TCAS_Demo_narration.md`。制作链：piper 本地 TTS（en_US-lessac-medium，模型 63MB 于 /tmp）→ 13 段 wav（Σ162.2s）→ 页间 0.8s/首 0.6s/尾 1.0s 静音 → 画面 ffconcat 按"页时长=配音+0.8s"合成。讲解词与修订稿措辞严格一致（evaluation pool / no further search / 58.1% cluster bootstrap / TCAS main and sole method）。edge-tts 因微软 WSS 域被网络策略拦截不可用；重合成命令链见 HANDOFF_SUBMISSION_0904.md。
- 2026-09-06 更新（外部"0906意见"采纳 + marked 版改纯颜色标注；正文 **15 页**、marked 15 页、合并稿 **22 页**、0 错误）：
  1. **Proposition 1 重构为两阶段规则**（消除 "max Q" 与 ε tie-break 的 lexicographic 不自洽，0906 意见核心项）：先 fidelity 最优（$Q_{\max}$、$z^{\mathrm{fid}}$），再在 ε-等价集 $\mathcal{F}_\epsilon=\{z:Q(z)\ge Q_{\max}-\epsilon\}$ 内最小化 texture-deviation risk；标题 "Guardrailed bang–bang optimality" → **"Guardrailed ε-optimal selection"**（长标题致 20.4pt overfull，缩名解决）；Remark 1 改两阶段语言（middle 必须保留 high：0.574>ε 单独超阈；late fidelity-等价：0.077<ε，risk-dominant 选 conservative）；Remark 2 "conditional optimality guarantee" → **"conditional decision rule"**；proof 重写。全文 bang/tie-break 措辞清零。数字全部未动。
  2. **摘要直击 276 holdout**（0906 意见二）：改为 "selected using only a 24-object probe set from 17 scaling variants and then evaluated unchanged, without further search, on the **strictly disjoint 276-object holdout** (pooled 300-object statistics also reported)"；摘要 **248 词**（<250）。正文 pool 表述不变（0906 认可"正文已解释得很好"）。
  3. **§4.1 补 supp 指引**（0906 意见三）："...available upon reasonable request, **and a consolidated reproducibility table (data subsets, checkpoint identifiers, scheduler, seed, and metric implementations) is provided in the supplementary material**"（supp S4 复现表本就存在，0906 意见者未收到 supp 文件；正文显式指向后消除不一致观感）。
  4. **信 R2-2 同步**：Proposition 表述改为两阶段 epsilon-optimal selection rule（middle 0.574>epsilon 必须 high；late 0.077、CI 下界 0.006 远低于 epsilon，fidelity-等价 → risk-dominant conservative）。注意 **ε (U+03B5) 会被 xelatex lmroman 静默丢弃**——信内一律 ASCII "epsilon"（重蹈 10⁴ 覆辙，已修复并验证 0 missing character）。
  5. **marked 版改 CFONT 纯颜色标注**（按作者要求去掉横线/删除线）：`latexdiff --type=CFONT`，新增=**蓝色 sans**、删除=**红色小号**，无下划线无删除线；DIFdel 内 tab:fac→Table 7 悬空引用照例 sed 修复。15 页 0 错误 0 未定义引用；overfull 17 处均为 CFONT 固有特性（DIFdel scriptsize 换行差 + 首页浮动 vbox 28pt），内容完整，属辅助审阅文件可接受。
  6. zip 解包零编译 15 页 0 错误；包内外 tex/pdf md5 对齐；with_letter 22 页（信 7 + 正文 15）。
- 2026-09-06 二次更新（§4.1 拆分 + 长度合规核验；页数不变 **15**、marked 15、合并稿 22、0 错误）：
  1. **§4.1 划分为 3 个编号子节**（零内容搬运，仅插标题 + 超长段拆分）：**4.1.1 Experimental protocol and comparisons**（管线总述/固定条件协议/比较定位）、**4.1.2 Evaluation sets and metrics**（四集合/三类指标/FAC 协议）、**4.1.3 Implementation and dataset details**（原 run-in paragraph 升级为编号子节；超长段拆为 3 个自然段：数据与划分 / 模型与推理 / 指标实现与可得性；Statistical reporting 段保留其内）。正文词数 texcount 口径 **8,740 词（text）+117（headers）**，远低于 Elsevier 12,000 词参考线；CAG 无硬性页限，特刊 30% 新材料要求满足。
  2. **信引用同步**：R1-1/R1-2/R3-3 中 "Implementation and dataset details paragraph in Section 4.1" → "Section 4.1.3"（CAG_plain 3 处 + 工作版 1 处）；信重编 7 页 0 缺字。
  3. **Demo pptx/视频核查**：13 页幻灯片与配音稿中 **0 处章节号引用**（按实验内容组织），与本次拆分自动统一，无需改动；TCAS_Demo_narrated.mp4 同源不受影响。
  4. zip 解包零编译 15 页 0 错误；marked（CFONT）15 页 0 错误 0 未定义引用；包内外 md5 对齐；with_letter 22 页。
- 2026-09-06 三次更新（外部"0906二轮意见"硬逻辑修复；正文 **15 页**、marked 15 页、合并稿 **22 页**、0 错误）：
  1. **Proposition 1 条件改为点估计**（0906 二轮意见核心项，修复 "CI lower bound < ε 推不出 Ūk ≤ ε" 的形式逻辑漏洞，反例 Ūk=0.20/CI=[0.05,0.35]/ε=0.1）：第三种情形 "whose utility's 95% CI lower bound lies below ε" → **"whose estimated utility satisfies 0<U_k<ε"**；proof 同步（"estimated utility 0<U_k<ε contributes at most ε when dropped"）；命题末尾新增一句 **"Measured confidence intervals serve as auxiliary uncertainty information and do not enter the membership condition of F_ε"**；Remark 1 late-stage 句改为 **"U_l=0.077<ε=0.1 dB while its FG-SSIM change is statistically insignificant … reduces texture risk"**（数据句中 CI [0.006,0.149] 保留为辅助报告）。数字全部未动（0.077<0.1 本就成立）。
  2. **补 texture-deviation risk R 的比较规则**（0906 二轮意见第 2 条）：§3.3 R 定义后新增一句 **"Risk is compared by a non-worsening (Pareto) rule rather than a weighted scalarization: one assignment has lower risk than another only if it is no worse on every diagnostic and strictly better on at least one, so no artificial weights are introduced"**；R 定义括号展开为三个 foreground texture diagnostics（Laplacian variance / RGB Std / Grad Mag）。
  3. **§4.5 标题 "Large-scale Validation" → "Large-scale Pooled Evaluation"**（0906 二轮意见第 3 条，进一步避免 300-object pool 与 276 holdout 语义混淆）；Table 4/5 caption 同步 "validation" → "pooled evaluation / pooled texture-preservation evaluation"。正文 §4.5 内部表述不变（0904 已统一为 evaluation pool）。
  4. **Table 9 不扩**（0906 二轮意见第 8 条：仅 structure+PSNR 不再算问题）：仓库与补充材料均无 276-holdout 的 Lap Var/RGB Std 数据，按"不为录用重跑大实验"原则维持现状；正文 "shape-texture balance" 结论由 Table 5/6 texture 证据支撑，未做结构性调整。
  5. **信 R2-2 同步**（CAG_plain）：两阶段规则句补 Pareto 比较说明；late-stage 推导改为 "estimated utility 0.077 dB below epsilon = 0.1 dB with a statistically insignificant FG-SSIM change …, with confidence intervals serving only as auxiliary uncertainty information outside the epsilon-equivalence condition"。信内一律 ASCII "epsilon"。信重编 7 页；docx 同步重生成。
  6. marked 版手工同步四处（Proposition/proof/Remark 位于既有 \DIFadd{} 内直改；§4.5 标题与两处 caption 按 CFONT 规范补 \DIFdel/\DIFadd 标记），15 页 0 错误 0 未定义引用。
  7. zip 解包零编译 15 页 0 错误 0 未定义引用；包内外 tex md5 对齐；submission_0907/ 五个文件（Revised manuscript / with letter / Marked-up / response pdf+docx / latex.zip）已同步覆盖。
- 2026-09-06 四次更新（双盲合规整改 + 致谢填入 title page；正文 **15 页**、marked 15 页、合并稿 **22 页**、title page 1 页、0 错误）：
  1. **核实 CAG Guide for Authors：double anonymized review**（官方原文："The title page (including author details) and anonymized manuscript (excluding author details) need to be submitted as separate files"、"Include acknowledgements only in the title page"、"anonymized manuscript and any supplementary materials do not contain any identifying information... or acknowledgements"）。据此确认刘立奥稿件不写作者的做法正确，且发现我方主稿 frontmatter 仍带作者块（desk-reject 风险）。
  2. **主稿 final_0903.tex 删除作者块**（\author/\cortext/\ead/\address 全部移除，保留 \title；代之以双盲说明注释）；marked 版同步删除（原 CFONT diff 中 "Xueyuan Che/Libo Sun" 以蓝色新增文字送审可见，整块移除后新旧两版均匿名，diff 无作者区）。
  3. **response letter 签名匿名化**（CAG_plain）：删 "First Author: Xueyuan Che / Corresponding author: Libo Sun (sunlibo@seu.edu.cn)"，改为 "The Authors" + 一行说明作者信息在单独 title page；letter 会随审稿人版本分发，必须匿名。
  4. **致谢/基金只填入 title_page_CAG.tex**（CAG 明确禁止出现在正文中）：四项江苏省项目——Key R&D Program of Jiangsu Province BE2023010-3、Basic Research Program of Jiangsu BK20253037、Advanced Technology Research and Development Program of Jiangsu BF2025018、Modern Agricultural Machinery Equipment and Technology Promotion Project of Jiangsu NJ2025-10。Titlepage 0907.pdf 重编译更新（1 页）。
  5. **匿名核查**：正文/marked/letter/supplementary 的 pdftotext 全文 0 处姓名与单位；四个 PDF 无 Author 元数据；title page 含基金号（仅该文件不送审）。cover letter 保留作者信息（该文件按 Elsevier 规则不送审）。EM 系统作者元数据照常填写（与双盲不冲突）；注意 EM 默认把投稿人标为 Corresponding Author，可在系统内改为 Libo Sun 与 title page 一致。
  6. **Supplementary 位置确认**：按 CAG Guide 作为单独文件随稿上传（submission_0907/ 已有 "Supplementary material 0907.pdf" 独立条目），正文 §4.1.3/§4.6 已引用——**不并入论文 PDF 之后**。
  7. zip 重打包并解包零编译 15 页 0 错误；submission_0907/ 六个文件（Revised manuscript / with letter / Marked-up / Titlepage / response pdf+docx / latex.zip）md5 对齐覆盖。
- 2026-09-06 五次更新（对照 sciencedirect 版 Guide for Authors 全文逐项核查；合规收口）：
  1. **合规确认项**：摘要 248 词 <250 ✓；关键词 7 个（上限 7，无 and/of 多词组）✓；Highlights 5 条且最长 82 字符 ≤85 ✓；图形摘要为 PDF（推荐格式）✓；表格 booktabs 无竖线、无 resizebox、正文全引用 ✓；fig1–7 为矢量 PDF 且文件名规范 ✓；正文编号分节 4.1.1 式 ✓；LaTeX 可编辑源码平铺 12 文件 ✓；Research data Option C 以 §4.1.3 "available upon reasonable request" + supp 复现表满足 ✓；fig5.pdf 元数据 Author=anonymous 无碍，其余图与主 PDF 无作者元数据 ✓；cover letter 含三要素（贡献综述/最近先行工作+状态/差异说明）且无基金信息 ✓；Declaration of Interest 为独立 .docx ✓。
  2. **Cover letter 旧术语修复**：'chosen only on a 24-object probe set and transferred unchanged to a 300-object validation set without re-search' → 'selected using only a 24-object probe set and then evaluated unchanged, without further search, on the strictly disjoint 276-object holdout (pooled 300-object statistics also reported)'（与摘要/正文 0906 口径统一）。
  3. **Highlights 术语同步**：第 4 条 'without re-search' → 'no further search'（保持 ≤85 字符），重生成 highlights_CAG.docx；cover letter 重生成 cover_letter_CAG.docx；0907 包内 'Research Highlights 0907.docx'、'Cover letter 0907.docx' 已覆盖。
  4. **待作者确认（不阻塞上传）**：(a) 若本稿为 CAD/Graphics 2026 Paper 75 扩展版，指南要求正文明确引用会议版并说明扩展点、随投稿附会议原稿副本、≥30% 新材料（该通道 'anonymization policy does not hold'，但保持匿名不违规）；(b) 若写作过程使用生成式 AI 工具，需在参考文献前加 Declaration of generative AI 节，未用则不加；(c) 图形摘要 h:w≈0.303，指南建议 531×1328 px（h×w≈0.4）或等比更大，可选择性微调；(d) demo 视频为可选项，若上传需附 still 图并在正文提及；(e) CRediT 贡献声明在 EM 系统内填写，不写入匿名主稿。
- 2026-09-06 六次更新（图形摘要重修 + latex 源全文一致性核查；正文 **15 页**、marked 15 页、合并稿 22 页、GA 1 页、0 错误）：
  1. **图形摘要确认存在实际缺陷并重修**（作者指出生成物有问题）：300 dpi 放大检查发现编译产物中 Panel A/B 两个坐标轴**叠画在同一位置**（两组刻度 1/3、2/3 与 1、1.5、2、2.5 混排、图例压住 Panel A 标题）——根因是 pgfplots `at={(x,y)}` 轴定位被静默忽略，该图自初次编译起即坏。修复：两轴改用 `\begin{scope}[shift=...]` 包裹（纯 TikZ 定位，100% 可靠），Panel A 图例改 `legend style={at={(0.04,0.98)},anchor=north west}` 置于绘图区内空白处，不再触碰标题；Panel C 文案采用作者 IDE 内改进版（"Evaluation: 300 objects + disjoint holdout" + "No further search: 24-object probe → disjoint 276-object holdout"，与正文 276-holdout 口径一致）。
  2. **GA 比例达标**：`\useasboundingbox (-0.1,1.05) rectangle (22.5,-7.9)` 固定画布，页尺寸 644.6×257.7 pt，h:w=**0.3998**（指南 0.4）✓；逐面板 200/300 dpi 渲染目检 0 遮挡 0 重叠。
  3. **latex 源一致性核查发现单点分歧**：zip 内 tex 与工作区 tex 在 L318 差一个词（"large-scale evaluation" vs "large-scale validation"——作者在 IDE 已改为 evaluation 且重建过部分产物）。按全文术语约定统一为 **"before large-scale evaluation"**：clean tex 直改；marked 版同句按 CFONT 规范补 \DIFdel{validation}/\DIFadd{evaluation} 标注。除此之外 zip tex 与 package tex **逐字节一致**（diff 仅此一处）。
  4. **全量重建（单一状态源）**：主稿/marked 15 页 0 错误 0 未定义引用；信 7 页重编（docx 重生成）；合并稿 22 页首页为信 ✓；latex.zip 重打包；GA PDF 重编译同步。
  5. **submission_0907/ 终检**：7 个 PDF 页数符合预期（15/15/22/7/1/1/2）；送审文件姓名 0 命中（Titlepage 3 处属预期，该文件不送审）；合并稿第一页为 Response to Reviewers ✓；6 项产物 package↔0907 md5 对齐 ✓；4 个 docx zip 完整性 ✓；GA 源码 final/graphical_abstract_CAG.tex 强制入库（此前被 ignore，含作者 IDE 改动与本次修复）。

## 四、EM 上传对照表

> **2026-09-07 起最终上传集迁移至 `final/submission_0907/`**（按师兄 `submissions revise.zip` 模板重命名：自然语言文件名 + 0907 后缀；tex 源码只存在于 latex.zip 内，不散放）。`final/submission_package_CAG/` 保留为工作区与制作源（pptx/narration/md 等），**不再直接用于 EM 上传**。

| EM 上传项（Item/类型） | 0907 包文件（submission_0907/） | 工作区源文件（submission_package_CAG/） |
|---|---|---|
| Manuscript（LaTeX 主文件） | latex.zip（12 文件平铺：final_0903.tex + cls/sty/logo/fig1–7） | 同左 |
| Manuscript PDF（合并稿，信在开头） | Revised manuscript with response letter 0907.pdf | final_0903_with_letter.pdf |
| Manuscript PDF（备选：仅正文） | Revised manuscript 0907.pdf | final_0903.pdf |
| Marked-up version（修订标注版，CFONT 纯颜色） | Marked-up manuscript 0907.pdf | final_0903_marked.pdf |
| Response to Reviewers | response to comments of reviewers 0907.pdf（.docx 备用） | response_to_reviewers_CAG.pdf / .docx |
| Supplementary material | Supplementary material 0907.pdf | supplementary_0903.pdf（FAC 剂量-反应表 + S4 复现表，正文 §4.1.3/§4.6 与信所引） |
| Title page | Titlepage 0907.pdf | title_page_CAG.pdf |
| Cover Letter | Cover letter 0907.docx | cover_letter_CAG.docx / .md |
| Highlights | Research Highlights 0907.docx | highlights_CAG.docx / .md |
| Graphical Abstract | Graphical abstract 0907.pdf | graphical_abstract_CAG.pdf |
| Declaration of Interest | Declaration of Interest Statement.docx | 同左 |
| Video / 演示材料（可选） | demo.mp4（静音 60s）；demo with narration 0907.mp4（英文配音 2m53s） | TCAS_Demo.mp4 / TCAS_Demo_narrated.mp4 |
| Demo 制作源（不上传） | — | TCAS_Demo_fixed.pptx、TCAS_Demo_narration.md |

- 合并稿 `final_0903_with_letter.pdf`（**22 页 = 回复信 7 页 + 正文 15 页**）按会议要求"信附于修改稿开头"制作，现**已放入本包**；EM 上传时可将合并稿作为 Manuscript PDF 上传（同时照常提供 latex.zip 源码），信另在 Response to Reviewers 项单独上传，两种方式均满足会议字面要求。
- Article Type 步骤选择 **VSI: CAG_SS_CAD/Graphics 2026**。

## 五、注意事项

1. 上传 demo 请用包内 `TCAS_Demo_fixed.pptx` / `TCAS_Demo.mp4`（2026-09-04 已同步最新术语）；根目录 `TCAS_Demo.pptx` 现为同一最新版的副本，可传可不传。
2. 包内已无 `figures/` 子目录（2026-09-04 清理）；fig1–7.pdf 平铺置于包根目录并与 latex.zip 内文件 md5 一致，手工上传时直接选取根目录文件即可。
3. latex.zip 内不要加顶层目录前缀，也不要再塞入子文件夹，否则 EM 构建失败。
4. 如 EM Build PDF 出现引用问号，通常是 bib 未编译所致；本稿参考文献内嵌，不受影响。
