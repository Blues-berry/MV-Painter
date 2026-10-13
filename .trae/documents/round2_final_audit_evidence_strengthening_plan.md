# Round-2 Final Audit & Evidence Strengthening Plan（final_audit_20261001）

## Summary

在不修改论文正文的前提下，对 Round-2 全部证据做一次"司法审计"式收口：冻结证据基线 → 归档 LHL 异常溯源定性 → MV-Adapter 映射敏感性实验 → strict-276 离线纹理指标 → 12 对象烘焙一致性 → Core-7 同 runner 补齐 → 统计方向与可复现性审计 → 叙事降级建议与 reviewer readiness 报告。目标不是堆正结果，而是产出审稿人难以攻击的证据闭环。

**硬约束**：`final_round2.tex` / `supplementary_round2.tex` / `response_letter_round2.md` 零修改；所有 GPU 实验先预注册协议再跑；负结果原样保留；每个新实验有冻结协议 + 客观问题 + 对应审稿人关切 + 成败两种解释。

---

## Current State Analysis（探索确认的事实）

### 仓库状态
- 当前分支 `codex/round2-evidence-integrated-20261001`（跟踪 mvpainter 远端），HEAD `d30ed4f`。未跟踪：`.codex/`（**不提交**）、`scripts/verify_sd2_depth_mirror.py`（随本轮一并入库）。
- GPU：2× RTX 5090（32GB×2）空闲；2T 盘、CUDA 12.8。

### 证据分布（关键路径）
| 证据 | 位置 | 状态 |
|---|---|---|
| strict-276 stage-placement 全量图像 | `final/round2/stage_placement_276_20260929/predictions/{fixed_mean,c3_lhl,hll,llh,ground_truth}/obj_00XX.png` | 完整在盘（276×5） |
| 同 runner 确认集（GFL/GC3/LFM/LHL/LLH） | `/4T/tmp/mvpainter-layer-confirmation-20260930/`（CSV/manifest 全，**图像仅剩 2 张/调度**） | **易失，必须先抢救** |
| 官方归档 LHL（FG-PSNR 14.78） | `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/per_object_metrics.csv` | **易失，必须先抢救** |
| global C3 strict-276（6 方法 pilot） | `final/round2/coordination/c3_schedule_followup_strict276_20260930_persistent/pilot_results.json` | 在库 |
| MV-Adapter 76-object 面板（7 条件） | `final/round2/mv_adapter/`（`results/holdout_exact_{76,layer_fixed_76,layer_lhl_76,layer_llh_76}/`、`MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json`） | 在库；层间效应 SUPPORTED、temporal NOT_SUPPORTED |
| MVDiffusion 75-object 面板 | `final/round2/mvdiffusion/`（525 行） | 在库；layer-wise NOT_REPLICATED（负结果保留） |
| 烘焙 12 对象 | `final/round2/main_adapter_baking/cpu_bake_12{,_layerwise}/`（textured GLB + texture PNG + `bake_metadata.json` + `unseen_renders/`） | 在库；mask 在 `foreground_masks/` |
| Robustness R0/R1 | `final/round2/coordination/main_backbone_robustness1_20260930/` | 在库 |
| 既有审计 | `final/round2/coordination/final_acceptance_20260930/`（8 份，含 EVAL_AUGMENTATION_AUDIT、SHARED_INPUT_DETERMINISM_AUDIT、MVADAPTER_LAYER_MAPPING、STRICT276_GLOBAL_FIXED_LOW_CONFIRMATION） | 在库 |

### 差距
- 用户指定的 13 份目标文档**全部不存在**（全库零命中）；语义最近的现存文件为 `CLAIM_EVIDENCE_LEDGER.md`、`BAKE_12_VALIDATION_AUDIT.md`。
- strict-276 mask 不落盘（`geotex/stage_placement_eval.py` L204/L210 运行时由 batch mask + `compute_edge_mask` 生成）→ Phase 3 需按同一确定性规则重算。
- 同 runner 确认集与官方 LHL 归档在 `/4T/tmp/`（易失）→ Phase 0 首先抢救。
- 预注册机械映射（C：shallow={320@64}, middle={640@32}, deep={1280@16,1280@8}）已完成；**映射敏感性尚未测试**。

### 关键技术判断：映射分组的非退化性（决定 Phase 2 设计）
冻结源 profile 为 deep=1.65/middle=1.65/shallow=0.58（deep 与 middle 同值）。4 注入点按值 (0.58, 1.65, 1.65, 1.65) 归一化（加权 mean=1.0）后，三种连续三分组的每点乘子为：
- (1,1,2) 与 (1,2,1)：每点乘子向量**完全相同**（0.4195, 1.1935, 1.1935, 1.1935）→ 输出 bitwise 相同，**无需跑 GPU**，用算术证明 + 3 对象 identity 确证；
- (2,1,1)（shallow={p1,p2}, middle={p3}, deep={p4}）：乘子向量不同（0.5202, 0.5202, 1.4798, 1.4798）→ **唯一非退化备选，需跑 76 对象**。

因此 Phase 2 的诚实设计 = 1 个非退化备选映射 × 76 runs + 1 个退化映射的解析证明 + 3 对象 identity 抽查（3 runs）。不做最优映射搜索。

---

## 用户已确认的决策

1. **GPU 实验**：Phase 2 + Phase 5 都做；**执行前先检查是否有其他 agent 正在跑**（tmux / nvidia-smi / GPU_QUEUE.md / 新增 results 目录），已在做则跳过该 Phase 并在 inventory 中记录状态。
2. **分支**：继续在 `codex/round2-evidence-integrated-20261001` 上提交并 push 到 mvpainter 远端。
3. **LHL 定性**：执行时再定——先完成 runner diff（Phase 1.2），依结果选 Case A（根因=未播种 cond 拉伸，引现有审计佐证）或 Case B（仅以 provenance 无法保证为由排除）。

---

## Deliverables（全部放 `final/round2/coordination/final_audit_20261001/`，英文，git add -f）

| # | 文件 | 来源 Phase |
|---|---|---|
| 1 | `final_round2_evidence_inventory.md` | 0 |
| 2 | `FINAL_REPRODUCIBILITY_MANIFEST.json` | 0 |
| 3 | `claim_evidence_matrix.md` | 0 |
| 4 | `ARCHIVED_LHL_PROVENANCE_AUDIT.md` | 1 |
| 5 | `archived_vs_current_runner_diff.md` | 1 |
| 6 | `historical_result_exclusion_reason.md` | 1 |
| 7 | `MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL.md`（预注册，跑前提交）+ `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md` | 2 |
| 8 | `STRICT276_TEXTURE_FIDELITY_AUDIT.md`（+ per-object CSV） | 3 |
| 9 | `baking_consistency_report.md`（+ per-object CSV） | 4 |
| 10 | `STRICT276_CORE7_MATRIX.md` | 5 |
| 11 | `metric_direction_audit.md` + `statistics_reproducibility_audit.md` | 6 |
| 12 | `FINAL_NARRATIVE_RECOMMENDATION.md` + `FINAL_REVIEWER_READINESS_REPORT.md` | 7 |

新脚本：`scripts/audit_strict276_texture_20261001.py`、`scripts/audit_bake_consistency_20261001.py`、`scripts/audit_metric_directions_20261001.py`（或并入现有分析）、mapping-B 的 runner 配置（复用 `final/round2/mv_adapter/run_layerwise_experiment.py`）。

---

## Phase 0 — Evidence Freeze（Priority 0，最先执行）

1. **抢救 /4T/tmp 易失工件** → `final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/`：
   - `/4T/tmp/mvpainter-layer-confirmation-20260930/` 全部 `*_per_object_metrics.csv`、`*_rows.json`、`*_run_manifest.json`、`confirmation_analysis.json`、剩余 PNG；
   - `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/per_object_metrics.csv`（官方归档 LHL）；
   - 逐文件 SHA-256 记入 manifest。若源已丢失，在 inventory 中如实记录缺失。
2. **`final_round2_evidence_inventory.md`**：按用户表格逐条列（Evidence | Dataset | Backbone | Status | Reviewer concern），覆盖：主 strict-276（stage-placement + 同 runner 确认）、R0/R1 robustness、MV-Adapter 76、MVDiffusion 75、Baking 12、global C3 pilot；每条标注 PASS / partial / audit needed / rescued。
3. **`FINAL_REPRODUCIBILITY_MANIFEST.json`**：对每个 paper-facing 实验记录 checkpoint SHA、config SHA、object list SHA、runner SHA、metric script SHA、环境（GPU 型号/驱动、CUDA、PyTorch、diffusers 版本）。复用既有 `MVADAPTER_LAYERWISE_HASH_MANIFEST.json` 与 `final_acceptance_20260930/` Phase-12 SHA 审计，缺项补测。
4. **`claim_evidence_matrix.md`**：从 `CLAIM_EVIDENCE_LEDGER.md` 派生 + 并入跨骨干/robustness 新证据；列 Claim | Evidence | Strength(strong/medium/weak) | Risk(low/medium/high)。此矩阵随后续 Phase 结果滚动更新。

## Phase 1 — Archived LHL 溯源审计（Priority 1）

1. **`ARCHIVED_LHL_PROVENANCE_AUDIT.md`**：对官方归档 LHL 记录重建溯源链——runner commit（`git log` 追 `geotex/layer_lhl_ablation_shared.py`）、checkpoint、config、dataset、metric 实现版本（与当时 `stage_placement_eval.py` 的对应关系）、环境。以 rescued 工件为准。
2. **`archived_vs_current_runner_diff.md`**：逐项对照 archived runner（`layer_lhl_ablation_shared.py`）vs 当前确认 runner（`run_layer_confirmation_276_20260930.py` / `stage_placement_eval.py`）：seed 初始化、random 调用点、DataLoader 行为、对象顺序、预处理（`random_stretch_or_compress` 播种状态）、target view 选择、latent 生成、VAE sampling、scheduler、metric 计算。附 D19 卫生注记（unet.eval() 缺失经证伪无数值影响：全链路无 BatchNorm/非零 dropout/self.training 分支）。
3. **定性（执行时依 diff 结果决定）**：
   - Case A：diff 确认单一根因 = 未播种 cond 随机拉伸 → `historical_result_exclusion_reason.md` 引 `EVAL_AUGMENTATION_AUDIT`、`SHARED_INPUT_DETERMINISM_AUDIT`、R0/R1 受控实现差 0.03dB、r=0.66 作证据；
   - Case B：根因无法证明 → 仅写 "Historical record removed from active evidence because complete provenance cannot be guaranteed."
   - 无论 A/B：归档 LHL 不进入任何定量主张（现状保持，文档化）。

## Phase 2 — MV-Adapter 映射敏感性（Priority 2，GPU）

1. **冲突预检**：`tmux ls`、`nvidia-smi`、`GPU_QUEUE.md`、`final/round2/mv_adapter/results/` 是否出现新映射目录。已有 agent 在做 → 跳过并记录。
2. **预注册** `MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL.md`（跑前 commit）：冻结 checkpoint、76-object Exact holdout 名单、seed 20260928、temporal LLH、50 steps、评估脚本；声明乘子规则（同一机械归一，无重校准）；预注册两种解释：
   - 全部映射 layer>global 方向一致 → "layer redistribution transfers independent of exact partition"；
   - 仅部分映射有效 → "transfer is architecture-aware and mapping-sensitive"。
3. **执行**：
   - 映射 B′=(2,1,1)：shallow={320@64,640@32}=0.520179, middle={1280@16}=1.479821, deep={1280@8}=1.479821 → L-LLH × 76 = 76 runs；
   - 退化映射 (1,2,1)：算术证明每点乘子与已跑映射 C 相同，另跑 3 对象 identity 抽查确证 bitwise 一致（3 runs）；
   - 合计 ≈79 runs。对照基线复用既有 G-FL/G-LLH/L-LLH(C) 行，不重跑。
4. **指标**：PSNR、FG-SSIM、Edge-SSIM、FG-LPIPS、ΔE00、GT-texture（与既有面板一致）；paired bootstrap（10k，seed 20260928）。
5. **输出** `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`：映射×条件矩阵 + 配对表 + 两种预设解释的判定。负/混合方向原样保留。

## Phase 3 — Strict-276 离线纹理审计（Priority 3，无 GPU）

1. **数据**：`final/round2/stage_placement_276_20260929/predictions/`（fixed_mean/c3_lhl/hll/llh × 276 + ground_truth）。
2. **mask 重算**：先核对 `stage_placement_eval.py` 的 batch mask + `compute_edge_mask` 输入是否可确定性重建（所需 depth/normal 输入在盘与否）；可重建 → 按同一规则重算并记录规则；不可 → 在报告中如实声明改用前景 mask 并标注偏差。
3. **新脚本 `scripts/audit_strict276_texture_20261001.py`**，每对象 × 每调度 vs GT（前景内）：
   - CIEDE2000（复用 `audit_c3_schedule_strict276.py` 的既有实现）；
   - GT-relative Laplacian variance error、GT-relative RGB variance error、GT-relative gradient magnitude error——**一律"到 GT 统计量的距离"**（如 |log(gen/gt)| 或相对差），禁止"variance 越高越好"式主张。
4. **统计**：LLH vs 其余各调度（及 LHL vs C3）配对 10k percentile bootstrap，seed 20260930，对象级重采样。
5. **输出** `STRICT276_TEXTURE_FIDELITY_AUDIT.md` + per-object CSV。强化 R1 texture 关切回应。

## Phase 4 — 烘焙 Seam / 跨视一致性审计（Priority 4，CPU）

1. **数据**：`final/round2/main_adapter_baking/cpu_bake_12{,_layerwise}/` 12 对象全方法（textured GLB + texture PNG）。不扩大对象集。
2. **新脚本 `scripts/audit_bake_consistency_20261001.py`**：
   - **UV seam**：解析 GLB UV，检测 UV chart 边界边，栅格化至 texture 空间并两侧各膨胀 2px，计算 seam 两侧像素对 ΔE00 不连续度；
   - **Surface reprojection**：离屏渲染（trimesh+pyrender）K=8 固定视角，输出 position map + RGB；跨视同表面点（position 距离 < ε）颜色方差，聚合 mean/max；
   - **Cross-view consistency score**：按方法汇总。
3. **输出** `baking_consistency_report.md`：12 对象描述性对比（不做推断性统计主张），与 `BAKE_12_VALIDATION_AUDIT.md`、`bake_metadata.json` 交叉引用。

## Phase 5 — Core-7 同 runner 补齐（Priority 5，GPU，条件执行）

1. **冲突预检**（同 Phase 2.1）。
2. **方法清点**：核对 `pilot_results.json`（6 方法×276）实际方法列表；Core-5 = GFL/GC3/LFM/LHL/LLH（rescued 确认集 CSV）。确认缺 no_adapter、fixed_high 后再跑；若 fixed_high 已存在于 pilot，则只补 no_adapter。
3. **执行**：no_adapter + fixed_high × 276，复用同 runner 内核（`geotex/stage_placement_eval.py`）、与确认实验一致的 generation seed/协议（执行时从 `*_run_manifest.json` 读出实际 seed 并对齐，禁止新协议）。
4. **输出** `STRICT276_CORE7_MATRIX.md`：7 条件×7 指标，LLH vs 其余 6 组关键配对 bootstrap（10k，seed 20260930），消除"不同 pipeline 混源"质疑。

## Phase 6 — 统计审计（Priority 6，必做，无 GPU）

1. **`metric_direction_audit.md`**：逐报告（确认集分析、MV-Adapter paired bootstrap、MVDiffusion panel、robustness）核对 delta 约定——higher-better: delta=A−B；lower-better: delta=B−A；正=改善；验证 bootstrap/胜率/CI/ranking 方向实现一致，列出任何歧义表。
2. **`statistics_reproducibility_audit.md`**：仅重跑分析（零推理）：`scripts/analyze_layer_confirmation_20260930.py` 复算，核对 seed 20260930、10k percentile、对象级重采样；复算 CI/胜率与 archived `confirmation_analysis.json`、`STRICT276_GLOBAL_FIXED_LOW_CONFIRMATION.md` 数字逐位比对，记录完全一致或差异。

## Phase 7 — 叙事重构研究（Priority 7，只写建议不改稿）

1. **`FINAL_NARRATIVE_RECOMMENDATION.md`**：
   - 主贡献改写建议：从"发现最优 LLH 调度"→"adapter 残差跨深度/去噪阶段的分配分析；temporal placement 与 layer redistribution 是可分离因子；主 pipeline 下提升保真、跨一个 adapter 架构部分迁移、并揭示架构相关适用边界"；
   - 降级规则落地："generalizes across backbones"→"shows transferability across one additional adapter architecture"；"CAI automatically discovers schedule"→"CAI provides diagnostic motivation"；"universal optimal schedule"→"architecture-dependent effective residual allocation pattern"；
   - 并入 Phase 2 映射敏感性判定、MVDiffusion NOT_REPLICATED 边界、Phase 3/4 纹理与烘焙结果。
2. **`FINAL_REVIEWER_READINESS_REPORT.md`**：① R1 readiness（holdout/统计/texture/baking）；② R2 readiness（novelty/CAI/cross-backbone）；③ 剩余风险；④ 最终 claim 边界；⑤ 必要正文修改清单（仅列清单）；⑥ 仍建议追加的实验。

---

## 执行顺序与调度

```
P0 抢救+冻结 → P1 LHL 溯源（读 rescued 工件）
              ↘ P2 映射敏感性（GPU，后台 tmux mv_painter_mapB_*）
P0 完成 → P3 纹理离线审计（CPU，与 P2 并行）
        → P4 烘焙一致性（CPU，与 P2 并行）
P2/P3/P4 → P5 Core-7（GPU，P2 结束后）
全部 → P6 统计审计 → P7 叙事建议
```

每个 Phase 完成即 commit（前缀惯例 `docs:` / `exp:` / `qa:`）并 push mvpainter 远端当前分支；`final/` 交付物 `git add -f`；`.codex/` 永不提交；文档中机器绝对路径写相对路径（沿用 release 清洗惯例）。

## 禁止事项（全程生效）

- 不修改 `final_round2.tex` / `supplementary_round2.tex` / `response_letter_round2.md` 及任何论文性文本；
- 不依新结果调 schedule / 换 checkpoint / 改评估协议；
- 不删改任何负结果（MVDiffusion NOT_REPLICATED、temporal NOT_SUPPORTED 原样保留）；
- 不做最优映射/调度搜索（Phase 2 仅两个预设分组，其一解析退化）。

## Verification

1. **论文零改动**：收尾 `git diff` 确认三个论文文件无 diff；
2. **数字三方一致**：每份报告的表格数字与其源 JSON/CSV 抽查逐位一致；claim matrix ↔ inventory ↔ readiness report 交叉引用一致；
3. **可复现性**：P6 分析复算与 archived 数字完全一致（seed 确定性）；
4. **预注册合规**：P2/P5 的 protocol 文件 commit 时间早于对应 results；
5. **git 卫生**：工作区干净（仅 `.codex/` 未跟踪），分支已 push，交付物全部 add -f 入库。

## Assumptions & Risks

- 假设 `/4T/tmp` 工件当前仍在盘（探索时确认存在；若 Phase 0 执行时已丢，inventory 如实记录，P1 降级为 Case B 口径）；
- P3 mask 确定性重算若输入缺失，按预案降级为前景 mask 并声明偏差；
- P2 的乘子算术（退化映射 bitwise 相同）执行前须对 `layer_profile_transfer.json` 与 runner 实现核实"按点施加"假设，若实现按组施加则退化结论改为 3 对象 identity 实测；
- 其他 agent 并行风险：P2/P5 各自预检，发现已跑则只做汇总审计不重跑。
