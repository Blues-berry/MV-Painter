# CAG-S-26-01549 投稿基线备份（2026-10-08 建立）

## 这是什么

CAG-S-26-01549（2026-09-07 提交至 Computers & Graphics，CAD/Graphics 2026 特刊）
投稿时刻的源文件与 PDF 的一份**经三重验证的只读备份**。

## 验证链（三方一致）

| 证据 | SHA-256 |
|---|---|
| 投稿包 `submission_package/latex.zip` | `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a` |
| 包内 `final_0903.tex` = 本备份 `final_0903.tex` | `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` |
| 投稿稿 `submission_package/Manuscript 0907.pdf` | `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da` |

交叉验证：
1. md5 对比：备份 tex 与投稿包 latex.zip 解包成员逐字节一致；
2. git 锚点：`700776e2`（2026-09-07 14:36 "提交前最小修复"）是最后一个改动 `final/final_0903.tex`
   的提交，工作区该文件与此提交零差异；
3. 独立复核：`1008/audits/01549_SOURCE_BASELINE_VERIFICATION.md`（2026-10-07）从 zip 重建
   PDF，15 页逐页栅格化与投稿 PDF 一致，记录的 tex 哈希与本备份相同；
4. 编译复现（2026-10-08）：在 01549_revision_workspace/work/ 用本备份副本编译，
   产出 15 页 / 3,682,333 字节，与 `Manuscript 0907.pdf` 字节数一致。

## 投稿版标题（身份标识）

> Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation

若任何文件 `final_0903.tex` 的 \title 不是上述标题，即不是投稿版（仓库中存在两个改题版本，
见工作区 CONFLICT_ANALYSIS.md 的污染地图）。

## 目录内容

- `final_0903.tex` — 投稿正文源文件（核心）
- `supplementary_0903.tex` — 补充材料源文件
- `final_0903_marked.tex` / `final_0903_marked_addonly.tex` — 标记修改版（投稿用"仅标新增"口径，
  由提交 `d9379fe9` 生成）
- `fig1.pdf`–`fig7.pdf`、`cag.sty`、`elsarticle.cls`、`cag-logo.pdf`、`elsevier-logo.pdf` — 编译依赖，
  逐一与投稿 zip 成员 md5 比对一致
- `submission_package/` — 实际上传 EM 的 PDF 包与 latex.zip 原件

## 使用规则

1. 本目录为只读档案，禁止编辑；
2. 所有修改请在 `../01549_revision_workspace/work/` 进行；
3. 校验：`sha256sum -c SHA256SUMS.txt`
