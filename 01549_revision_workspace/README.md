# 01549 修改工作区（唯一修改区）

建立日期：2026-10-08。背景：仓库多分支/多副本/多代改写互相覆盖，本工作区将后续修订
所需的最小资料集合划归一处，**后续所有论文修改只在本文件夹内进行**。

## 目录结构

```
01549_revision_workspace/
├── README.md                 ← 本文件（规则）
├── CONFLICT_ANALYSIS.md      ← 两轮审稿意见 × 稿件 × 仓库 冲突分析与修改任务清单
├── reviews/                  ← 两轮审稿意见原文
│   ├── 第一轮_CAD Graphics会议意见_202609.txt   （会议推荐意见，截止 2026-09-10）
│   └── 第二轮_期刊审稿意见_202610.txt           （01549 稿件的期刊审稿，下一轮修改依据）
├── baseline_01549/           ← 投稿原版快照（只读，勿改；完整备份见仓库根 01549_BASELINE_BACKUP_20261008/）
├── work/                     ← ★ 唯一可编辑区 ★
│   ├── final_0903.tex        ← 从投稿版复制的正文（已验证：编译 15 页 / 与投稿 PDF 字节数一致）
│   ├── supplementary_0903.tex 等可按需从 baseline_01549 复制
│   └── fig1–7.pdf, cag.sty, elsarticle.cls, logos
└── salvage/                  ← 从 10-08 surgical 分支打捞的可复用材料
    └── RESPONSE_TO_REVIEWERS_1008_DRAFT.md（审稿回复草稿，内容需逐条复核后采用）
```

## 编译

```sh
cd work && latexmk -pdf -interaction=nonstopmode final_0903.tex
```

已验证：一次通过，15 页，0 错误，输出与投稿 PDF 字节数一致（3,682,333）。

## 铁律（吸取 10-08 事故教训）

1. **单一起点**：一切修改从 `work/final_0903.tex`（SHA-256 `203966151e11...`）出发，
   禁止从 `final/round2/`、`1006/`、其他分支/工作树的同名文件复制内容；
2. **投稿版身份自检**：\title 必须保持 "Timestep-Conditioned Adapter Scaling for
   Multi-view Diffusion Texture Generation"，除非明确决定改题；
3. **不依赖文件名判断版本**：仓库中至少有 4 处叫 `final_0903.tex` 的文件内容各不相同，
   只认 SHA-256 与本文件夹；
4. **结构性删除需留痕**：删节/删图/删表前，在 CONFLICT_ANALYSIS.md 附录登记
   （删除什么、审稿依据是什么）；
5. **定期锚定**：阶段性成果 git commit 到本工作区所在仓库，或另存带日期的
   `work/snapshot_YYYYMMDD/` 副本；
6. 其他 worktree（/4T/CXY/MV-Painter-1008 等）视为历史档案，不再作为修改基础。

## 关键哈希速查

| 文件 | SHA-256（前 16 位） |
|---|---|
| 投稿版 final_0903.tex（=baseline_01549/ 与 work/ 初始副本） | `203966151e1129d3` |
| 投稿包 latex.zip | `67464667d4ada0c4` |
| 投稿 PDF（Manuscript 0907.pdf） | `fc9cf793e4922df2` |
| 被改题版本 "On Adapter Scaling..."（勿用） | `fc61ce367b4297e0` |
| 被改题版本 "Layer-wise TCAS..."（勿用） | `efe09ba78728a265` |
