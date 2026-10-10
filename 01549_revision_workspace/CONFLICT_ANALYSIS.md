# CAG-S-26-01549 冲突分析：两轮审稿意见 × 投稿稿件 × 仓库版本状态

分析日期：2026-10-08
分析基线：投稿版 `final_0903.tex`（SHA-256 `203966151e1129d3...`，15 页 / 7 图 / 9 表）
审稿输入：`reviews/第一轮_CAD Graphics会议意见_202609.txt`、`reviews/第二轮_期刊审稿意见_202610.txt`

---

## 0. 一句话结论

**投稿源文件从未损坏**（tex 与投稿 zip 逐字节一致）；真正的风险来自三个**同路径不同内容的
衍生物谱系**（改题版、L-TCAS 重构版、过度删改的 surgical 版）。第二轮审稿意见引用的数字
与投稿稿**全部对得上**——不存在"审稿人评的是错误版本"的问题；下一轮修改应从本工作区
`work/final_0903.tex` 出发做增量修订。

---

## 1. 版本考古：谁是真投稿版

### 1.1 验证链（三方一致）

```
EM 投稿包 latex.zip (67464667d4...)
  └─ 内含 final_0903.tex (203966151e11...)  ←→  主工作区 final/final_0903.tex 逐字节一致
       └─ 编译产物 = Manuscript 0907.pdf (fc9cf793...) = 15 页 / 3,682,333 字节
            └─ git 锚点：700776e2（2026-09-07 14:36，"提交前最小修复"）为最后一个正文提交
```

10-07 独立审计（`1008/audits/01549_SOURCE_BASELINE_VERIFICATION.md`，在另一分支完成）从
zip 重建 PDF 并逐页栅格比对，结论相同。

### 1.2 分支污染地图（同名 `final_0903.tex`，三种内容）

| 内容版本 | 标题 | SHA-256 | 所在分支 |
|---|---|---|---|
| **投稿版（唯一权威）** | Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation | `203966151e1129d3` | 当前分支 scientific-validation-v3-20261002、final-evidence-freeze-20261001、round2-evidence-integrated-20261001、next-review-response-20260930、evidence-closure-audit-20261005、paper-1006-20261006、scientific-validation-v3-20261006、human-confirmatory-analysis-20261007 |
| 改题版 ① | On Adapter Scaling in Geometry-Controlled Multi-view Diffusion… | `fc61ce367b4297e0` | cg-revision-evidence-closure-20261007、cg-round2-1008-revision-20261008、cg-round2-1008-public-sanitized-20261008、**cg-01549-surgical-revision-20261008** |
| 改题版 ② | Layer-wise Timestep-Conditioned Adapter Scaling…（L-TCAS） | `efe09ba78728a265` | cg-ltcas-narrative-convergence-20261007 |

### 1.3 三代平行修改尝试及其结局

| 谱系 | 位置 | 内容 | 审计结论 |
|---|---|---|---|
| ① round2 | `final/round2/final_round2.tex`（923 行） | 09-29/30 的 L-TCAS 重构、"Core-7 authority surface" | 10-07 审计判定为"后续大幅重构候选稿，**非** 01549 源"；未采用 |
| ② 1006 | `1006/manuscript/main_1006.tex`（283 行） | 10-06 的独立重排候选稿 | 其自述"separate candidate…not replacements" |
| ③ 1008 surgical | 分支 cg-01549-surgical-revision-20261008 的 `1008/manuscript/revision_1008/final_0903.tex`（~430 行，9 页） | 10-07/08 从真 01549 出发的外科手术式修订 | 其自审报告 `01549_REVISION_ROOT_CAUSE_ANALYSIS.md` 判定：来源正确（WRONG_SOURCE 排除）但 **OVER_REWRITE 确认**——一次提交删 304 行、7 图→1 图、9 表→2 表，原图表承担的论证功能未逐项处置；已冻结，**不得直接作为下一轮底稿** |

**可打捞的资产**（见 `salvage/`）：
- `RESPONSE_TO_REVIEWERS_1008_DRAFT.md` — 逐条回复草稿，论证细致，但它是基于"撤回大量
  原稿结论"的激进策略写的，采纳前需按第 4 节策略重新定调；
- 1008 分支的 `authority/SCIENTIFIC_EVIDENCE_MAP.md`、`experiments/` 时间线、Fresh C 证据
  链——回应 R1-2（held-out 验证）时的核心实验素材。

---

## 2. 第一轮意见（会议推荐，2026-09 初）→ 01549 投稿稿落实核对

第一轮实为 CAD/Graphics 2026 会议推荐流程（3 位审稿人，修订截止 2026-09-10），
01549 投稿稿即其修订产物。逐条核对：

| # | 意见要点 | 投稿稿落实位置 | 状态 |
|---|---|---|---|
| R1-1 | FAC 数据划分/训练目标不明 | §4.1.3；双池说明（主 adapter 1,118 / strong-residual-FAC 1,706，见提交 700776e2） | ✅ 已落实 |
| R1-2 | 精确实现细节 | §4.1.3（checkpoint、sampler、scheduler、分辨率） | ✅ 已落实 |
| R1-3 | 偏好研究需聚类/自助法区间 | Table 8（稿 L463）+ cluster-aware 分析；Table 9 用 object-level percentile bootstrap 10,000 次（稿 L512） | ✅ 已落实 |
| R2-1 | 单一 pipeline，泛化性不足 | §4.7 Adapter-Dependence of High-Scale Failure Modes（稿 L495）+ 跨 backbone 附加检查 | ⚠️ 部分落实（R2 二轮仍不满意，见 3.2） |
| R2-2 | TCAS novelty 有限、纯启发式 | 新增 CAI 阶段效用模型（稿 L154-155）+ 形式化选择规则 | ⚠️ 落实但引火烧身（二轮 R2-2 追击） |
| R3-1 | 竞争调度策略未在大集合验证 | Table 9：276-object 严格不相交 holdout 上对比 linear warm-up/cosine bump/trapezoid/Gaussian-peak（稿 L512） | ⚠️ 落实但换了 adapter 实例 → 引出二轮 R1-2 新冲突 |
| R3-2 | Table 6/7 聚合口径不明 | 稿 L397/L416 caption 明确"per-object ratio 的均值（等权）" | ✅ 已落实 |
| R3-3 | Table 8 ± 含义、检验细节 | 稿 L442 caption：± 为 50 objects 的标准差 | ✅ 已落实 |
| R3-4 | 数据集来源/重叠 + FAC 训练细节 | §4.1.2/4.1.3；276 严格排除声明 | ✅ 已落实 |

---

## 3. 第二轮意见（期刊审稿，2026-09-14/24/28）逐条核对与冲突定位

> 审稿对象身份已验证：R2 引用的 CAI、§4.7、Edge-SSIM 0.529/0.559、0.96 dB 均能在投稿稿
> 中精确定位——**审稿人评的确实是 01549 投稿版**。
> ⚠️ 遗留程序问题：审稿包名为 CAG-D-26-00962，投稿号为 CAG-S-26-01549，HANDOFF 记录
> "经作者确认作为本稿审稿集"，回复信提交前需再次核对 EM 系统中的稿件编号。

### 3.1 Reviewer 1（09-14，5 条）

| # | 意见 | 稿件对应位置 | 核对结果 / 需要做什么 |
|---|---|---|---|
| R1-1 | 图 4、图 6 紫色偏移、重复纹理，要求更多物体的全物体对比 + 未修改 pipeline + 竞争 fixed-scale 基线 + baked mesh 未见视角渲染 + 接缝/跨视图一致性 + 补充视频无法查看 | 图 4=纹理退化裁剪对比（稿 L274）；图 6=C3 与 uniform 定性对比（稿 L326） | ✅ 引用准确。**要做**：扩充全物体面板（含 No-Adapter/s=1.25/s=2.50 基线）；补 baked-mesh 未见视角渲染与接缝检查；确认 EM 视频可访问 |
| R1-2 | Table 4–6 用主 adapter（含 24 选择物体）；Table 9 却换了 adapter（per-layer-capped），不能在选择集外确证主 adapter 的 0.96 dB | 稿 L512 caption 原文"strong-residual, per-layer-capped adapter instance of Section 4.7"——**审稿人读得很准** | ✅ 引用准确。**下一轮最重的实验题**：用主 adapter 在 276/300 held-out 上重跑 C3 vs 主要基线；或诚实重构该声明 |
| R1-3 | PSNR/纹理指标增益 ≠ 纹理保真；需区分 texture variation 与 texture fidelity | 依赖 Laplacian variance / RGB std / gradient 作纹理指标（§4.2、Table 5-7） | **要做**：措辞降级（variation 代理 ≠ fidelity），避免把指标增益说成保真改进 |
| R1-4 | FG-SSIM 差异 CI 过零≠等效；Table 4 Edge-SSIM 0.529 vs 0.559 劣于激进 scaling，需报告配对区间、承认 trade-off、给出非劣效界或收窄声明 | 稿 L383-384（s=2.50 Edge-SSIM 0.559 / C3 0.529）——**数字与稿件一致** | ✅ 引用准确。**要做**：补 paired intervals；给出非劣效界 ε 或改口"comparable"的适用范围 |
| R1-5 | FAC 仍难复现，鼓励放代码 | §4.6（稿 L482） | **要做**：代码/数据可得性声明升级，或说明不发布的具体原因 |

### 3.2 Reviewer 2（09-24，3 条 major；上轮 -1 分，本轮语气缓和但核心保留）

| # | 意见 | 稿件对应位置 | 核对结果 / 需要做什么 |
|---|---|---|---|
| R2-1 | 方法论贡献仍限于"为现有 adapter 选调度"，不够 substantial | 全文方法定位（§3） | **最难的一条**。可用素材：把贡献重新定位为"受控证据链"（trace-off 度量+诊断+held-out 验证协议）而非调度本身；引 Scheduled Style Injection 等先例划清边界（salvage 草稿已有现成论证） |
| R2-2 | CAI 形式化是"事后为经验选出的调度补理论外衣" | 稿 L154-155（CAI 模型与 Pareto 选择规则） | **要做**：撤下 proposition/最优性暗示，把 CAI 降级为描述性/动机性框架，明确 C3 是 development-set 上的历史选择 |
| R2-3 | 跨 backbone 验证缺失（最重要缺失实验）；§4.7 的不同 adapter 幅度分析不能替代真正不同的 backbone | §4.7（稿 L495）；根目录 CROSS_BACKBONE_VALIDATION*.md 为 MV-Adapter/MVDiffusion 初步检查 | **要做**：要么补一个真正异构 backbone 的对照实验，要么在 Limitations 中明确声明单 backbone 边界并给出初步跨 backbone 证据的现状与局限 |

### 3.3 Reviewer 3（09-28）

"paid efforts in addressing the concerns… looks good for publication." — 无需技术动作，
回复信中致谢即可。

---

## 4. 冲突清单（三类）

### A. 审稿人之间 / 两轮之间的冲突

| 冲突 | 说明 | 处理建议 |
|---|---|---|
| 评分与立场分歧 | 一轮：R2 打 -1（borderline reject），R1/R3 均正分；二轮 R2 仍保留 novelty 保留意见 | 回复信以"证据增量"说服 R2：每条新实验/新分析都标注是针对其上轮意见 |
| 修复引入新冲突（核心链式冲突） | 一轮 R3 要求"在大集合上验证竞争调度" → 01549 用 276-holdout 回应，但**换了 adapter 实例** → 二轮 R1 抓住"主 adapter 的 0.96 dB 未在选择集外确证" | 下一轮必须闭合：主 adapter + held-out + 同一协议下重跑（或明确降级 0.96 dB 为 pooled 描述并给出 held-out 新证据） |
| R1 与 R2 关注点错位 | R1 全部是实证/统计问题（可修）；R2 是定位/哲学问题（novelty、事后合理化） | 两者不可混在一条回复里：R1 用数据，R2 用边界声明+定位重构 |
| 指标解释冲突 | 一轮 R2 称赞"多纹理诊断"，二轮 R1 指出这些代理指标不能证明"保真" | 措辞统一降级：所有 Laplacian/RGB-std 表述改为 texture variation/代理指标，不称 fidelity |

### B. 审稿意见 × 稿件事实核对（防止"在错误内容上迭代"的正面验证）

第二轮意见引用的全部具体事实在投稿稿中**逐项核实为真**：
- Edge-SSIM 0.529 vs 0.559 → 稿 L383-384 ✅
- +0.96 dB pooled headline → 稿 L33（摘要）、L546（结论）✅
- CAI 模型 → 稿 L154-155 ✅
- §4.7 adapter 依赖性分析 → 稿 L495 ✅
- Table 9 换用 per-layer-capped adapter → 稿 L512 caption ✅
- 图 4 / 图 6 视觉问题所指对象 → 稿 L274 / L326 ✅

**结论：不存在审稿人评错版本的问题；所有"数字对不上"的担忧可以解除。**

### C. 仓库内部版本冲突（"乱"的根源）

| 冲突 | 现状 | 处置 |
|---|---|---|
| 3 种标题并存 | 投稿题 / "On Adapter Scaling…" / "Layer-wise TCAS…" | 一律以投稿题为唯一正名（改题需明确决策，且会触发 EM 元数据修改） |
| 4+ 处同名 final_0903.tex | final/、round2/、1008 分支×2、1006（不同名但同角色） | 只认 SHA-256；工作区外文件视为档案 |
| surgical 候选 9 页版 vs 投稿 15 页版 | surgical 版撤回过多原稿论证（其自审已确认） | 不采用；其回复信草稿与证据地图打捞到 salvage/ |
| 根目录散落结论性 md | CROSS_BACKBONE_VALIDATION*.md、TCAS_EVIDENCE_LEDGER.md 等 | 本轮不清理（避免误删）；其内容作为 R2-3 回应素材引用 |

---

## 5. 下一轮修改路线（增量防御策略）

原则：**保持核心叙事（TCAS 低-高-低、300-object 评价、人类偏好研究）不动，按意见逐点
加固；每处修改可追溯到具体审稿意见；不做整段删除式重构。**

优先级排序（先关键后次要）：

1. **P0 实验：主 adapter held-out 确证**（同时闭合 R1-2 与一轮 R3-1 的链式冲突）
   - 主 adapter（非 per-layer-capped）在 276/300 held-out 上 C3 vs s=1.25 / s=2.50 /
     主要竞争调度的配对对比 + bootstrap CI；
   - 若结果与 0.96 dB 一致 → 替换/补充 Table 9 叙事；若不一致 → 诚实重构 headline。
   - 素材：1008 分支 Fresh C 证据链与实验时间线。
2. **P0 统计与措辞**（R1-3、R1-4）：paired intervals 进 Table 4/5；明确 texture variation
   ≠ fidelity；非劣效界 ε 或收窄 "comparable/preservation" 声明。
3. **P1 定位与理论**（R2-1、R2-2）：CAI 降级为描述性框架；novelty 叙事收窄为
   "training-free 阶段依赖控制 + 受控证据协议"；与先例划界。
4. **P1 视觉证据**（R1-1）：全物体对比面板（含 No-Adapter 基线）、baked-mesh 未见视角、
   接缝检查；核实 EM 补充视频可访问。
5. **P2**（R1-5、R2-3、R3）：代码/数据声明；跨 backbone 边界声明（引用现有两份
   CROSS_BACKBONE 报告作为初步证据并说明局限）；R3 致谢。
6. 全程在 `work/final_0903.tex` 上增量修改；每完成一条在本文档附录登记
   （改动位置 / 依据意见 / 删除内容处置）。

## 6. 提交前待确认清单

- [ ] EM 稿件编号：CAG-D-26-00962 vs CAG-S-26-01549（以编辑决策信为准）
- [ ] 正式 revision round 与 decision date（本地材料中无决策信原件）
- [ ] 补充视频在审稿端可访问
- [ ] 代码/数据发布承诺与 Data Availability 声明一致

---

## 附录：修改登记表（每处修改一行，持续追加）

| 日期 | 位置（行/节/表） | 改动摘要 | 依据意见 | 删除内容处置 |
|---|---|---|---|---|
| 2026-10-08 | — | 建立工作区，work/=投稿版逐字节副本（编译 15 页验证通过） | — | 无 |
