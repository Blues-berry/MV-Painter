# Existing evidence matrix and source map

## 权威来源与去重规则

| 内容 | 主来源 | 校验/限制 |
|---|---|---|
| 当前候选稿 | `/4T/CXY/MV-Painter/1014finalv1/`；镜像 `/4T/CXY/MV-Painter/FINAL_CANDIDATE_20261013/source/1014finalv1/` | 正文与补充 PDF 的 SHA-256 两处一致；细节见 `SOURCE_AUDIT.json`。本支线未改写或重编译。 |
| 冻结的第15轮正文/补充 | `/4T/CXY/MV-Painter/final_paper_20261012/audit/frozen_round015_text/` | 视作证据快照，不与当前 v1 源文件混称同一版本。 |
| 原 01549 稿与 R2 | `/4T/CXY/MV-Painter/CG_revision_20261011_conservative_submission_r2/source_01549/official_submission_0907/`；`.../review/SECOND_ROUND_REVIEWER_COMMENTS.txt` | R2聚焦方法贡献有限、CAI像经验性调度总结、缺少跨骨干验证。 |
| 早期自适应几何预研 | `/4T/CXY/MV-Painter/CG_revision_20261013_adaptive_geo_control/FEASIBILITY_REPORT_ZH.md` 与 `SOURCE_HASHES.json` | 用于理解 Adapter 内部缺少相机/UV 对应的限制；BAVGC 改成后烘焙视角级接口后重新审计，没有直接沿用其结论。 |
| GeoTex 调度与烘焙主矩阵 | `/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/` | canonical 原始实验路径；冻结报告和指标副本另见 `final_paper_20261012/source/data/`。不重复运行矩阵。 |
| Round012 condition-interference 与 APG/MVA | `/4T/CXY/MV-Painter/CG_revision_20261011_conservative_submission_r2/evidence/round012/`；原始运行在 `MV-Painter-1010/.../iteration012_condition_interference/` | 报告、freeze、对象级分数与输出 ledger 互相指向。开发集或单项端点结果不外推为 BAVGC 证据。 |
| Round015 UV 跨视角诊断 | `/4T/CXY/MV-Painter/final_paper_20261012/source/data/gap_closure015/CROSS_VIEW_VALIDATION.json` | 80 条 replay/四种已知颜色控制，验证实现和一致性陷阱，不验证真实材质保真。 |
| 本次新增 Phase A | 本目录 `phase_a_signal_rows.csv`、`phase_a_signal_summary.json`、`scripts/phase_a_signal_audit.py` | 从冻结 bake 输入/指标读数据；新增参考视角 RGB MAE；对象为统计单位。 |

## 去重后的既有实验索引

“checkpoint”填已能确定的模型家族/冻结身份；具体绝对 checkpoint 文件由对应 `RUN_IDENTITY.json`、freeze 或 ledger 指定。未能由报告交叉确认的字段标作“未在本次重审中核实”，不推测填补。

| 研究线 / 研究问题 | checkpoint、对象、种子、采样 | 主要指标与结论 | 限制 | 可复用产物 |
|---|---|---|---|---|
| GeoTex Fresh C / Iteration 1–12：Adapter 几何注入、静态 TCAS/C3、条件交互和训练/部署有效性 | GeoTex 冻结原始模型与 v29 家族的不同阶段分别报告；对象面板包括 10/20/50/64 等，各轮不可混池。核心调度矩阵为 10 对象×7 条件，50 步 `EulerDiscreteScheduler`；生成对象种子策略为 `42 + frozen object index`，条件共享；核心 RUN_IDENTITY checkpoint source SHA-256 为 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` | 已完成静态调度与模型/条件消融；预算匹配 late-high 对 fixed-mean 的烘焙 FG-LPIPS 差 −0.00265165，95% CI [−0.00414366, −0.00136744]，p=0.001953125，10/10 对象方向有利。仅为既有小面板结论，不是 BAVGC | 条件结果是静态 profile；不是反馈控制。多个迭代模型和接口不能合并成一个效果量 | `BAKE_STATISTICS.json`、`geotex_matrix/RUN_IDENTITY.json`、`bake_matrix_v2/BAKE_RUN_SUMMARY.json`、10 对象×7 条件图像与指标 |
| 10 对象真实 UV 烘焙矩阵：静态条件是否改变未见视角纹理质量 | 七个控制与 GT；1024 UV、512 渲染；11 个未见视角；每对象/条件一条归档烘焙运行；生成条件使用共享对象随机种子 | `BAKE10_OBJECT_METRICS.csv` 提供 FG-LPIPS、PSNR、SSIM、CIEDE2000、覆盖率、跨视角 texel 方差和 seam discontinuity | 开发对象、单条已归档 bake realization；不是独立确认集。UV 跨视角指标在本次证明不等于 LPIPS | 本次 Phase A 原始行与复算脚本；冻结 handoff 与对象级 metrics |
| Round015 跨视角一致性 replay | 两个对象的四种已知颜色控制，80 replay 行 | 恒定黑色跨视角方差为 0；不同相机灰色方差约 0.125–0.127。支持“错误但恒定也可高度一致” | 合成控制，不能代表完整 PBR、接缝或未见视角质量 | `CROSS_VIEW_VALIDATION.json` |
| UV aliasing / seam footprint | 两对象诊断；分辨率 256/512/1024；UV 岛边界、重复 UV 和高误差 footprint | 被标出的 footprint 覆盖 100% 被检查到的高误差像素；分辨率变化会改变误差，显示 aliasing 敏感性 | 小样本；不证明任意遮挡/UV 拓扑均处理正确，也不是学习控制 | `iteration012_condition_interference/uv_aliasing_audit013_attempt02/REPORT.json` 及图像/掩码 |
| 第12轮 confirmation64：参考视角投影处理 | 同底座；64 对象×4 条件×3 seeds=768 输出；主要评测是参考图像和其余生成视角，不是烘焙 11 个未见相机 | view-projection 对参考视角 FG-PSNR +4.2827 dB（CI [+3.4089,+5.2052]），CIEDE2000 −2.2299（CI [−3.0609,−1.5630]）；非参考 PSNR −0.2824、LPIPS +0.000269，区间跨 0，未证明非劣 | 参考区域大幅变好不能推出其他视角无损；不是 BAVGC 烘焙控制 | `ROUND012_CURRENT_RESULTS.md`、`CONFIRMATION64_TEST.json`、三种子 scores、output identity ledger |
| APG 强基线开发比较 | round012 development/closure 条件和各自冻结 seeds；原始 v29 GeoTex 路径 | APG 报告比较候选 projection 与 APG；现有文件记录 APG 实现修复和闭合状态；不是 UV 反馈方法 | 比较仍是开发 evidence；不可由参考区域负余弦/梯度量推出烘焙质量 | `evidence/round012/apg/APG_PROTOCOL_FREEZE.json`、`APG_REPORT.md`、源码及 score hash ledger |
| MV-Adapter 条件交互开发/校准 | 32 对象×多个条件×3 seeds；另有 50 对象七条件旧面板；另有外部 GSO100 固定对象实验，域与新烘焙不同 | 32 对象投影候选的非参考 LPIPS未分离；外部 GSO100 投影候选相对 native/fixed/late LPIPS 明显变差（0.010–0.015 左右） | MV-Adapter 与 GeoTex 不是同一模型接口；不能跨骨干汇总。外部 GSO100 是扫描颜色输入，不是认证 albedo/PBR，且不含 UV 烘焙 | `mvadapter/MVA_REPORT.md`、`MVA_COMPARISONS.json`；`final_paper_20261012/source/data/gso_mva_external_attempt01/REPORT.md` |
| GSO100 静态调度补充验证 | 固定 100 对象、3 seeds、同输入；冻结的四个新增 profile 与既有条件；6 个原生视角 | middle-high−fixed-mean 主 PSNR −0.01366 dB，95% CI [−0.03056,+0.00352]，p=.1223。校准 20 对象烘焙 late-high−fixed-mean LPIPS +0.0000838，CI [−0.000103,+0.000286]，Holm p=.78765 | 未支持这一跨域静态调度优势；100对象视觉指标、20对象烘焙是不同端点/子集，不混池 | `completed_supplement013/analysis/REPORT.md`、固定 100 对象数据与 calibrated bake rows |
| GSO20 / APG / UV 投影近邻 | 20对象、多个条件和3 seeds；开发 convenience cohort | APG 与 projection 相比的开发报告不支持 projection 提升未见 LPIPS；较强 UV projection 候选比 APG/静态 profile 更差 | 样本小、方便抽取 cohort；原始扫描来源/材质不能视为真实 PBR 认证；不是独立确认 | round012 APG 与 bake freeze/report、原始生成和 UV bake outputs |
| FAC、feature-relative gate、LLH 等历史失败线 | 多次研究迭代，各自 checkpoint/对象/seed 依 attempt registry；不可当一个统一实验 | FAC 扩展表现不如 TCAS；历史 feature-relative residual gate 在 26 对象 CIEDE2000 +1.35，在六个历史失败案 +3.18，视觉无改善；LLH/timing profile 已经比较过 | 一些尝试是“完成未认证/档案”；以 attempt registry 标明的真实状态为准 | `EXPERIMENT_ALL_ATTEMPTS_ZH.md`、对应 `attempt_registry` 记录和 source hashes |
| BAVGC Phase A（本次） | 冻结 10 对象×7 静态控制；一个已归档 bake realization / 对象 / 条件；原始生成 object seed policy 42 + frozen index | 见 [FEEDBACK_SIGNAL_AUDIT.md](FEEDBACK_SIGNAL_AUDIT.md)：参考 MAE 有有限对象级预测关系；UV 方差对主 LPIPS 接近随机 | 不是新对象验证集；用同一控制身份做 LOOUO 预测；不能证明动态视角动作因果有效 | 本目录 CSV/JSON/script |

## 采样、身份和数据独立性

主矩阵身份文件记录生成 seed base 42，按 object index 派生对象 seed，且所有条件共享同对象 seed。原 bake 指标表中每个 object×control 仅一条结果。未将图像视角、对象内控制或 seed 当成独立对象。不同轮次、GeoTex 与 MV-Adapter、扫描纹理与烘焙 PBR 数据均不合并统计。

## 工作树扫描范围

本次枚举了本机所有已注册 worktree；与该研究直接相关的权威位置是当前论文树 `/4T/CXY/MV-Painter`、原始扩展实验树 `/4T/CXY/MV-Painter-1010`、Round012 只读 evidence bundle、冻结第15轮 bundle，以及本次新建的隔离 worktree `/4T/tmp/MV-Painter-bavgc-phase-b`。其他活跃/归档 worktree 作为派生复核或旧稿，不覆盖以上 canonical source。完整的本机 worktree 列表在执行时包括 `/4T/CXY/MV-Painter-01549-surgical-20261008`、`/4T/CXY/MV-Painter-1006-wt`、`/4T/CXY/MV-Painter-1008`、`/4T/CXY/MV-Painter-cg-revision-20261010`、`/4T/CXY/MV-Painter-r1color`、`/4T/MV-Painter-01549-unified-20261009`、`/4T/MV-Painter-main`、`/4T/tmp/01549-clean-checkout-20261008`、`/4T/tmp/mvpainter-paper-fac-bundle`、`/4T/tmp/MV-Painter-bavgc-phase-b`、`/tmp/MV-Painter-evidence-closure`、`/tmp/cg-closure-clean-audit` 和 `/tmp/mvpainter-cg-evidence-closure`。历史产物的权威性由其 run identity/hash 决定，不由 worktree 新旧决定。
