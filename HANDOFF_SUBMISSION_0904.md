# 投稿交接文档（HANDOFF）— 2026-09-04

> 目标：任何人（或下一个 AI 会话）拿到本文档后，5 分钟内能安全接手后续修改。
> 状态：**可提交**。正文 14 页 0 错误 / marked 15 页 / 信 7 页 / 合订 21 页 / supp 2 页。git `new0529` 分支，最新 commit `96eddaf`。

---

## 1. 权威文件地图（只认这些）

| 用途 | 唯一权威路径 | 页数 |
|---|---|---|
| 修改稿源文件 | `final/final_0903.tex` | — |
| 修改稿 PDF | `final/submission_package_CAG/final_0903.pdf`（与 `final/final_0903.pdf` md5 相同） | 14 |
| 回复信源文件 | `final/revision/response_letter_CAG_plain.md` | — |
| 回复信 PDF/docx | `final/submission_package_CAG/response_to_reviewers_CAG.pdf` / `.docx` | 7 |
| 修订标注版（latexdiff） | `final/submission_package_CAG/final_0903_marked.pdf` / `.tex` | 15 |
| 补充材料 | `final/supplementary_0903.tex` → 包内 `supplementary_0903.pdf` | 2 |
| 合订稿（信+正文） | 包内 `final_0903_with_letter.pdf` | 21 |
| LaTeX 源码包 | 包内 `latex.zip`（12 文件平铺，解包零编译验证过） | — |
| 打包说明日志 | 包内 `PACKAGING_NOTES.md`（每轮变更已记录） | — |

**废弃文件黑名单（勿看勿用勿提交）**：
- `final/final_0903_diff.pdf/tex` —— 08:04 旧 diff 产物，外部"0904意见"就是看它写的，已被 `final_0903_marked.*` 取代。
- `final/final.tex`、`final/revision_structured_0902.tex` —— 旧版正文，仅作 latexdiff 的 diff 基线（左侧）。
- `final/final_submit.tex` —— 另一代实验（artifact-amplification），仅 CLIP-IQA/偏好两表与主线同源，其余数字不可混用。
- 根目录 `TCAS_Demo.pptx` 已于 2026-09-04 用包内最新版覆盖（md5 一致 799df40a），不再有新旧两版；demo 改法见第 4 节末尾。

**Demo 同步（2026-09-04）**：`TCAS_Demo_fixed.pptx` 13 页中仅第 10 页曾含旧术语，已改为 "the 300-object evaluation pool, with no further search on the evaluation objects"；`TCAS_Demo.mp4` 用 LibreOffice→PDF→pdftoppm -r 144→ffmpeg 重导（1920×1080/30fps/60.2s 与旧版同参）。若再改 pptx 文字，重导链：`soffice --headless --convert-to pdf` → `pdftoppm -png -r 144` → `ffmpeg -framerate 13/60.2 -i slide-%02d.png -vf "scale=1920:1080:...,format=yuv420p" -r 30 -t 60.2`。

## 2. 关键事实链（数字出处，改稿时勿凭记忆写数）

- **数据**：`data/train_data/rendered_full/`。训练池 1,118（主 adapter）/ 1,706（strong-residual v2 实例，`train_objects_2000.txt`）；评估池 300 = `test_objects_300.txt`（固定顺序，前 24 = probe obj_0000–0023，后 276 = holdout）。训练/评估 overlap = 0（已复核）。类别 composition 元数据仓库不存在 → 复现表只写可验证事实。
- **checkpoint**：主 adapter = `geotex_refattn_v1/geotex_step_0002000.pt`（无 cap，主表全部用它）；strong-residual 实例 = `mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt`（MD5 a74cc1d16cb473a95022bdcbc58e1b22，per-layer caps deep 3.0/middle 3.5/shallow 0.8）；base = 本地 MVPainter_Pipeline snapshot（`checkpoints/hf_repo`，diffusers 0.20.0）。
- **口径**：`eval_schedule_comparison.py` 的 `psnr` = 整图 PSNR（16.71/16.79 dB sweep 用）；FAC/supp 的 9.88 = 前景 FG-PSNR。正文已消歧，勿再混。
- **276-holdout 调度迁移（Table 9）**：`mvpoutput/revision_holdout_split/holdout_summary.json` + `mvpoutput/revision_schedules_300/{linear_warmup,cosine_bump}/per_object_results.csv`。数字：ΔPSNR +0.258/+0.324/+0.323/+0.902 dB，wins 206/232/214/253，ΔFG-SSIM −0.0007(warm-up, tied)/+0.0458(bump)。
- **统计**：双侧配对检验；object-level percentile bootstrap 10,000；偏好研究用 participant+object 两级 cluster bootstrap（58.1% CI [50.1,65.8]；+33.6/+40.6 points）。

## 3. 修订决策史（6 轮，全部已推送 new0529）

1. `c657ff7/d4a4a1c/eaa078b`：信 R2-2 改引 probe Table 2；R3-1 改口 276-holdout；latex.zip 12 文件平铺重打。
2. `5040cf3`：包结构定型（EM 禁子文件夹）；.gitignore 放行包目录。
3. `7605762`：Proposition 1 ε 等价边界修复（tie-break 不再与 U_l CI [0.006,0.149] 矛盾）；8 表去 resizebox 统一 \small。
4. `bb81be2/51a316e`：恢复 7 张表体（曾整体丢失的事故）；FAC 反转透明披露；fig1/5/7 修正；补引 6 篇。
5. `467001e`：PSNR 口径消歧、FAC 目标函数写实（AdamW/1e-4/2000 步）、checkpoint 可得性、fig7 标签判定不改。
6. `deef289`：术语统一 "300-object evaluation pool"（13 处）；新增 Table 9；§4.6 补 no-model-selection 句；信 R2-1 弱化 "diffusion process itself"（正文已删信漏改）；supp 新增 S4 复现表。
7. `96eddaf`：摘要语病最小修复（re-search 4 处清零 / chosen only on / being preferred）；刻意保留结尾双重限定语（R2 防御）与第一句结构。

## 4. 标准修改 SOP（改任何正文文字都走全流程）

```
1. 编辑 final/final_0903.tex（同一文件多处改动必须串行 Edit，写后 grep 验证）
2. cd final && pdflatex -interaction=nonstopmode final_0903.tex ×2
   验收：grep -c '^!' log = 0；页数 14（±）；Overfull 仅剩 logo 区 2 处 <1.1pt
3. 重生成 marked：latexdiff --encoding=utf8 final.tex final_0903.tex > final_0903_marked.tex
   然后 sed 修 DIFdel 悬空引用：
   sed -i 's/\\DIFdel{Table~\\ref{tab:fac} reports/\\DIFdel{Table~7 reports/' final_0903_marked.tex
   pdflatex ×2，验收 0 错误、log 无 '??'
4. 同步包：cp final_0903{,.pdf} final_0903_marked{,.tex,.pdf}… → submission_package_CAG/
   （supp 改了则连 supplementary_0903.pdf 一起）
5. 重打 zip：cd submission_package_CAG && rm latex.zip && zip -j latex.zip final_0903.tex elsarticle.cls cag.sty cag-logo.pdf elsevier-logo.pdf fig{1..7}.pdf
6. 重合并：pdfunite response_to_reviewers_CAG.pdf final_0903.pdf final_0903_with_letter.pdf（信必须在第 1 页）
7. md5 对齐：包内外 5 文件逐一比对（信 PDF 两次 pandoc 生成字节会差，校验用页数+pdftotext 内容点）
8. git add（final/revision 在 ignore 内需 -f）→ commit → push origin new0529
```

**改信的流程**：改 `response_letter_CAG_plain.md` → pandoc 重编（命令见下）→ 包内 pdf+docx → 工作版 `response_letter_0903.md` 同步改动 → 合订稿重做。
```
pandoc response_letter_CAG_plain.md -o ../submission_package_CAG/response_to_reviewers_CAG.pdf \
  --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=12pt -V linestretch=1.25   # 固定 7 页
pandoc response_letter_CAG_plain.md -o ../submission_package_CAG/response_to_reviewers_CAG.docx
```

## 5. 坑清单（历次踩过，勿重踩）

- 同一文件并行 Edit 会写回竞态（后写覆盖先写），必须串行。
- 信含 Δ、×、→ 等 Unicode：pandoc 必须 `--pdf-engine=xelatex`；信内幂指数写 ASCII `10^-4`（上标 ⁴ 会被 lmroman 静默丢字）。
- `final/*` 被 gitignore，`final/revision/` 信源与 `final/*.tex/pdf` 需 `git add -f`（包目录已强制跟踪）。
- pdftotext 会在短语中间换行，grep 长短语 0 匹配 ≠ 内容缺失（如 "Table 9\nin Section 4.7"）。
- latexdiff 重生成后 DIFdel 内悬空 `\ref{tab:fac}` 每次都会重现，sed 修一次即可（见 SOP 第 3 步）。
- marked 版 DIFadd 下划线渲染会把新增 caption 拆字，grep 不到完整 caption 属正常。
- 摘要粘贴 EM 表单用纯文本：tex 里 `$=(1.25, 2.50, 1.25)$` 数学模式直接复制会乱码（当前摘要 243 词 < 250 上限）。

## 6. 遗留事项（有意不做/需作者决定）

1. **第二 backbone 迁移实验**：外部意见最看重的一项，9/10 截止前不可行，已决定不做；以限定措辞（信 R2-1 + Limitations "not yet been validated on a different geometry-conditioned multi-view diffusion backbone"）回应。若做下一篇/扩展版时优先补。
2. **fig7 中 "A s=1.25" 标签**：疑指向绿三角而非灰圆；绘图脚本与 17 变体逐点数据仓库中不存在，无法重生成；caption 不引用该标签 → 图不动。若作者重生成图时修正绑定。
3. **R3 的 category composition**：仓库无类别元数据，未提供；复现表只写采样/划分规则。若作者能从 Objaverse 元数据补统计，可加进 supp S4。
4. **checkpoint "upon reasonable request"**：文件都在仓库内，承诺可兑现；若期刊要求公开链接，届时再传 Zenodo/GitHub release。
5. **提交操作**：EM 上传对照表见 `PACKAGING_NOTES.md` 第四节；Article Type 选 `VSI: CAG_SS_CAD/Graphics 2026`；截止 **2026-09-10 23:59 GMT**；demo 用包内 `TCAS_Demo.mp4`。
