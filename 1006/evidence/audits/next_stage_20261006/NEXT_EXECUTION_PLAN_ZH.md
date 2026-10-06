# 下一阶段执行计划：GPU、审计、证据链与投稿门槛

日期：2026-10-06；依据现有 V3 结果及 01549 提交稿。
这是实验与证据工作计划，不是完整论文目录。正文保持到科学证据冻结后再改。
所有追加分析/研究都在已见 B 结果之后提出，必须标注真实时间顺序。

执行记录说明：下方资源与启动安排记录的是计划启动时状态；E1/E2 完成情况、E0
authority ledger 与当前未闭合门槛以文末“执行状态更新”及 readiness 文件为准。

## 本轮开始时的资源与立即动作

- 两张 RTX 5090，约 32 GB/张，本轮检查时均空闲；磁盘可用约 688 GB。
- 已核对 B runner SHA256 与原 manifest 一致：
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`。
- 建立 `MULTISEED_PROTOCOL.json`：六个固定配置、48 个 GT 分层抽样对象、
  generation seed 42/43/44；保留原 B 的完整 UID 顺序和 reference seed。
- 已实现 `run_multiseed.py`，只改变原 runner 的两个 generation-seed 调用，
  记录 parent source、wrapper、执行 AST、协议哈希；原 runner 字节不变。
- 已启动两卡技术预检：2 对象 × 6 条件 × 2 个生成种子，共 24 个生成。
  seed42 核验原结果复现；seed43 核验共享参照保持不变、初始 latent 改变。
  预检只验技术，不用于判断方法优劣。结果写入 `PILOT_VERIFICATION.json`。

预检版本的 wrapper source 已精确保存在 `run_multiseed_pilot_v1.py`。正式入口
增加了模型/config/inference/metric 的 launch 前哈希检查；执行的原 runner AST
与已测预检版本逐字节 dump 相同。该变化有独立 provenance，不重写历史运行身份。

正式 E1 入口：在项目根目录运行
`python final/round2/scientific_validation_v3/next_stage_20261006/launch_multiseed.py`。
入口会重新核验预检、当前代码和两卡占用，然后启动固定 seed43/44；完成生成后仍需
完整性审计和统计实现，不会把“生成完毕”当成科学结论。正式576生成在本轮未启动。

旧 B 中约 7 秒/对象条件是时间估算锚点，不是承诺；实际耗时还包含模型加载、
输入读取和存储。正式运行前按本次预检重新估算，并确认 GPU 当时仍空闲。

## 工作包与优先级

| 包 | 优先级 / 资源 | 回答的问题 | 交付物与依赖 |
|---|---|---|---|
| E0 证据契约与旧稿映射 | P0 / CPU | 01549 的每项主张究竟由哪些结果支持？ | Claim→comparison→cohort→seed→code→table 映射；先于新结果阅读冻结研究问题。 |
| E1 固定配置多生成种子 | P1 / 两 GPU | 均值优势与典型对象结果在新 realization 下是否稳定？ | 48×6×3 对象/配置/种子矩阵；576 个新正式生成；先过本次技术预检。 |
| E2 静态深浅配置 2×2 因子实验 | P1 / 两 GPU | 去掉时间变化后，deep/middle 与 shallow 强度各造成什么变化？ | 固定四条件、48 对象、三生成种子；具体 runner 及条件哈希锁定后运行。 |
| E3 三维输出与保真证据核查 | P1 / CPU，必要时 GPU 渲染 | 有效二维差异是否反映到当前存储的 GLB？ | 当前 N=20 同对象二维/原生三维配对；覆盖、颜色、结构、感知距离与失败图；禁止旧 seam 正证据。 |
| E4 人工偏好导入 | P1 / 等用户答卷，CPU | 对当前 LLH，外观保真与自然度是否得到人类支持？ | 全 8 终点、双向聚类区间、Holm、排除与 40 名额状态；原题目/停止规则不变。 |
| E5 标准化残差干预可行性 | P2 / 小 GPU 开发诊断 | 是否能建立技术上可控、可比较的 Layer×Window 干预？ | 仅开发对象残差/hidden 日志与 no-op 检验；技术失败立即结束，不跑正式图像找显著。 |
| E6 全证据重建与独立复算 | P0贯穿 / CPU，小 GPU复现 | 每项保留结果是否可从原始记录重建？ | 新证据表、指纹索引、隔离 checkout 统计重建；最终稿后补齐全部表图。 |
| E7 主张冻结与稿件审查 | 最后 / 无 GPU | 哪些结论应进入正文，哪些必须撤回？ | 冻结证据版本→改稿→R1/R2/R3/复现四视角审查→readiness verdict。 |

E1 和 E2 是固定干预问题，不是 schedule 搜索。E3 优先使用已经产生的有效输出。
E5 不作为本次保留有边界贡献的必需条件。不存在“必须得到 positive 才能结束”的门槛。

## E0：立即固定主张与来源

逐项建立机器可读记录：claim_id、原稿位置、方法、参照、实际尺度/cap、
队列、是否事前注册、effect/CI、有效样本、生成器与输入哈希、当前 disposition。
至少覆盖：旧 0.96 dB、旧 C3 人工 58.1%、新 LLH、CAI、interaction、
结构保持、纹理保真、三维与跨骨干。

旧 C3 人工研究和新 LLH 的人工研究分开。新 LLH−GFL 不能用作旧 C3
0.96 dB 的复现；pooled-300、strict276 重评价、fresh300、freshB 分开。
原始图片、失败样本和非显著结果均保留。新种子与新条件是追加研究，不能还原 B 盲态。

## E1：固定参照、多生成种子稳定性（已锁定并开始预检）

六个条件：GFL、GFH、GC3、LFM-EXACT、LLH、endpoint-matched gen_linear。
对象：B 的 150 对象按 GT Laplacian 排序形成四块，固定随机种子 20261006，
每块随机抽取 12 个，共 48。选择不读取方法输出；本次仍是见过 B 后的补充研究，
不是 untouched-object confirmation。

保留 object_seed=42+原 B index；generation seed=42/43/44。
只改变初始 latent 和生成时采样种子，参照图、目标、几何、global embeddings 不变。
不能用缩短的 48 UID 列表重新编号，否则 reference realization 会跟着变。

计数：总计 864 个对象条件 realization；seed42 的 288 行从已存在的 B / generic
extension 复用，seed43/44 新生成 576 行。复用须经过技术预检和输入身份核验。
两卡预估约 35–60 分钟，不含前置开发和异常处理。

五个固定 LLH 对比，FG-LPIPS 主终点、FG-PSNR 次终点；分别 Holm 五比较。
先在每对象内平均三 seed 的配对差，再以对象 bootstrap 10,000 次，seed20261006。
不能当成 144 个独立对象。报告每 seed 均值、中位数、有利比例和对象内符号稳定性，
不按 seed 选择结果。固定 48 对象的估计不直接替代原 150 对象估计。
同步报告已有结构/颜色终点为描述性，避免事后换主终点。

通过/停止：seed42 原输出、非耗时 metrics、输入和 residual 哈希一致；seed43
参照不变且 latent 改变；每种子内六条件 shared input 一致；条件覆盖完整、无非有限值。
任意技术失败先修复、重验，不开启方法结果解释。负结果按预案保留。

该实验检验 realization 稳定性，不检验参照抽样稳定性；不能把这两种随机性混为一谈。

## E2：静态 2×2 深浅强度干预（实施前锁定）

现在 LFM−GFL 的差值同时涉及深度配置、剂量和 cap 变化，不能叫纯深度收益。
用最小的固定因子设计补足明确的静态干预效应：

| 条件 | deep | middle | shallow | 时间配置 |
|---|---:|---:|---:|---|
| F00 | 1.25 | 1.25 | 0.50 | 全 50 步恒定 |
| F01 | 1.25 | 1.25 | 0.80 | 同上 |
| F10 | 1.675 | 1.675 | 0.50 | 同上 |
| F11 | 1.675 | 1.675 | 0.80 | 同上 |

值来自已存在 low、exact mean、native shallow ceiling，不再搜索网格。
同一 native capped forward、无 adaptive controller，所请求值均不超过 cap。
第一因子为 deep/middle 联动强度，第二因子为 shallow 强度；不能声称隔离了
deep 与 middle 各自的效应，也不声称匹配总实际剂量。

使用 E1 的同一 48 对象、reference、三 generation seed；总 576 行。
F00 seed42 候选复用 a3_baseline；F01 候选复用 native_gfl，前提是技术预检
证明其 effective trace 和原 GFL 输出完全一致，不能只因数值看似相同就复用。
若两项都可复用，新生成 480 行；否则至多新生成 576 行，预估约 30–60 分钟。
先检查静态 runner no-op 和恒定尺度 trace，再冻结 source/config/condition 哈希。

主终点 FG-LPIPS：两个平均因子效应与一个 difference-in-differences interaction，
Holm 三检验；FG-PSNR 同样独立三检验作为次终点。报告四条件及全部简单对比区间，
后者描述性。以对象内三 seed 均值为单位，不把 seed 当独立对象。
生成主效应和 interaction 的对象级 bootstrap/零假设方法需在正式结果前固定并
通过 additive-null/injected-interaction 检查，不能复用旧 SS bootstrap 缺陷。

与 LLH/LFM 的额外排序只做描述，不选出“新最优配置”。该实验可以识别指定
静态尺度的干预效应，不能证明其来自剂量之外的独立深度机制。
出现“shallow 不是更低更好”时照常报告；不据此另换因子值。

## E3：当前三维证据与接缝问题

第一阶段无需新生成：重建当前 20 个 UID 的二维→原生 GLB 对应表，使用实际
同对象、同 realization 输出。Fresh B 的总体均值不能直接作为这批 3D 的二维对照。
GT-textured sanity reference 也有非零误差，说明 bake/evaluation 存在绝对保真上限；
不能直接从预测误差扣除 GT sanity 误差或把它当可加的偏差校正。

交付：所有 N=20 配对结果、逐对象失败面板、11 未见视角采样定义、source GLB/
camera/sampler 哈希；PSNR、LPIPS、颜色分别报告，避免整体胜者结论。

接缝先做测量工具审计：合成连续纹理、已知 seam-jump、repeat/mipmap 场景和极端 UV。
通过后再针对现有 N=20 输出计算新指标，标为新开发的探索性诊断，不替换历史文件。
工具若不能通过，撤回接缝改善主张；不能继续使用已知 clamp/overflow 错误的数字。
cross-view consistency 可以用有效的固定同表面投影比较作为独立诊断，须先校验
可见性/遮挡与 photometric 语义，不能把模糊导致的低差异称为一致性改善。

当前先保留 N=20 original-UV 范围，不为凑 N=24 自动 UV unwrap，也不重烘焙
得到新赢家。若审稿仍要求 full-PBR，必须单独登记 lighting/material/render 设置；
当前 base-color 结果不能被改名为 full-PBR evidence。

## E4：真实人工数据

用户后续提供真实答卷。既定 40 名额、至少 36 有效完成、四比较×两问题、
双向 participant/object bootstrap、Holm 八终点保持不变。
通过 `../audit_scripts/run_closed_human_study.py` 执行，所有名额结束前禁止偏好分析。
模板与规则见 `../continuation_20261006/HUMAN_RESPONSE_GUIDE_ZH.md`。

无论 LLH 胜、负或不确定，都完成结果归档与证据关闭。少于 36 有效完成保持 gate OPEN，
不补人寻显著。二维偏好不评价 final GLB、seam、unseen-view 或剂量机制。

## E5：Layer×Window 标准化干预的开发可行性（有上限、非必需）

现有日志只记录 correction norm，未记录被加到的 hidden norm。已检查 wrapper：
correction 由 adapter 计算、按 scale/cap 缩放，再加到 hidden_states。
不能拿旧 raw L2 跨层对齐后就声称“等强度”。

开发目标：在原 baseline 上，沿 adapter correction 方向增加小扰动 δr，
控制相对幅度 ||δr||₂ / ||hidden||₂ = α，记录各 wrapper、group、step 的
hidden、未缩放 correction、实际 δr、effective scale、cap 与精度误差。
α 预设 0.005/0.01/0.02，仅按可行性选最小通过者，不读取图像质量选择幅度。
这些相对幅度不是质量阈值；不同层语义仍不同，也不等同于“所有机制剂量已匹配”。

先做纯张量 no-op/known-norm/cap/zero-residual 检查，再使用 6 个既有开发对象、
3 层×W1/W3/W5×3 幅度+baseline，最多 168 个 residual-only 生成；不输出或阅读
方法图像分数。开发样本在 launch 前由既定开发清单排序选取并锁定。

技术门槛：α=0 与原图像/输入严格一致；实际相对目标误差≤5%，至少99%有效
active-wrapper-step 达标；不改变 reference-write pass；零 residual/hidden 和 cap
不可行步骤全部记录。任何层不满足则停止，不扩大 scale、不删对象、不改 grouping。
误差界值是数值实施标准，不是科学效应门槛。

只有可行性通过、而最终保留主张确实需要进一步识别时，才设计新的独立对象诊断：
先核实至少150个对象不与训练、开发、A/B、旧评测交叉（含 byte/decoded-pixel），
冻结 baseline+15 cells、对象数和功效/精度依据，再正式运行，最低2400对象条件。
没有 untouched cohort 就不称独立确认；没有合适共同支持就不做回归外推救机制。
本轮不下载新资产或启动该正式 campaign；开发实现与新队列是明确前置依赖。

## E6：审计与可复现证据链

每一工作包实行两个入口：先技术完整性 gate，再公开条件级结果。
最低检查：唯一 object/condition/seed 键、预期行数、shared-input 指纹、checkpoint/
config/runner/metric 哈希、有效尺度 trace、prediction/residual 文件、非有限值、
分片一致性、JSON→CSV 最终重建。resume 身份不同则硬停止。

统计检查：方向、有利比例、中位数、对象区间、固定 Holm family、浮点 p 下溢标记；
零假设/注入效应验证、对象顺序不变性、重复内容敏感性。废弃的 layermap bootstrap
仅用于历史追溯，不能作为正式 interaction 检验入口。

预冻结做“证据表”的全重建：A2/A3/A3b、B 核心、generic、E1/E2、复杂度边界、
MV-Adapter、GLB、FAC 负结果和人工结果。每张表都有 generator、input 与哈希。
清洁 checkout 可重建证据表与统计；原模型资源同机挂载的限制明确。
新 GPU campaign 每包至少一个小条件在隔离 checkout 复现，用可核验内容而非 elapsed。
最终论文全部图表的整合重建留到证据冻结后的稿件阶段。

存在别的 chat 正在操作本分支时，实验仅写新目录、不自行 stage/commit/push、
不终止其任务；code/hash 改变则暂停本 campaign 的技术推进并记录冲突来源。

## E7：叙事与最终验收规则（先定主张，后组织全文）

同领域论文与直接先行工作对照已整理在
`evidence/audits/REVISION_STRATEGY_COMPARATIVE_EVIDENCE_20261006_ZH.md`，并已加入
E0 authority ledger。矩阵覆盖目标系统 MVPainter、Paint3D、MVPaint、Make-A-Texture、Im2SurfTex、UniTex
及 *Scheduled Style Injection*，比较它们的具体技术对象、对应消融/基准、人评/3D
端点与局限；它是代表性一手来源审查，不是 exhaustive systematic review。
SSI（CVPRW NTIRE 2026）已经测试 StyleID 注入与几何 ControlNet 强度在 layer/time
两轴的调度，覆盖反向与正向、线性/非线性形状、四项指标和 SD 1.4/1.5/2.1，报告
超过 35 个配置与 28,000 张图。因此，“layer × time 是通用新控制空间”不再可主张。
任务和 residual path 的差异可用于界定本文问题，却不能自行证明 R2.1 的贡献充分。

保留候选贡献：实际 scale/cap 语义、静态深浅配置的指定干预效应、时间变化的
额外收益与局限、对象复杂度适用边界。CAI 不作推导/预测创新；旧 C3 和新 LLH
各自对应自己的证据。Layer×Window 可作为有边界响应图，不要求成为核心理论。

预先决定的结果分支：

| 新证据 | 行动 |
|---|---|
| E1 稳定，E2 静态配置效应明显 | 强化已测配置效应与 realization 范围，避免等实际剂量机制表述。 |
| E1 不稳定或不同 seed 方向冲突 | 将单 realization 均值写为条件性结果；报告对象/seed 分布，不加种子筛选。 |
| E2 效应小或浅层方向不一致 | 撤回“深度配置第一阶占优”的强叙事，保留尺度语义与有限效应事实。 |
| 人工 LLH 不胜或效果不确定 | 删除人类保真/优势主张；保留该负证据，不改 pair 或人群。 |
| GLB 依然混合 | 维持 endpoint trade-off，撤回整体 3D 优势；不靠只选 LPIPS 解决 R1。 |
| E5 数值实现通过但浅层剂量越过 native cap | 不启动当前修订的三层等剂量正式试验；将 Layer×Window 结果限于已测请求值/实际 cap profile，不作 dose-independent 机制推断。 |
| R2 仍认为贡献不足 | 明确记录创新性/期刊适配风险；不能由 p 值、改名或降级主张伪造通过。 |

科学证据冻结：所有决定保留的主张有对应证据/范围，人工已按规则完成或由用户明确
变更研究范围，所有科学 P0 关闭、P1 关闭或合理限界，数据与统计版本锁定。
然后才修改论文、补充材料与回复；逐项更新 01549 主张，重建全部最终表图。
最后做 R1/R2/R3/复现四个视角检查，保留每项 concern、证据和 disposition。
无 blocking 才可判 submission ready；可信结果不自动保证期刊接收。

## 原始有限执行顺序（按文末执行状态更新核对）

1. 完成并审计本次 24 生成预检；冻结运行身份和 E0 映射。
2. E1 两卡正式 576 新生成；执行技术 gate 后再分析，完整保留负结果。
3. 实现/验证 E2 小 runner，锁定最终协议，执行固定四条件并分析。
4. 在 E1/E2 运行时完成 E3 现有三维配对与 E6 统计/来源审计；无需等人工答卷。
5. 导入用户人工答卷，执行 E4；E5 仅开发可行性，按其技术 gate 决定是否结束。
6. 汇总全部证据和主张分支→科学冻结→改稿→表图复现→最终审稿与 readiness。

不进行新的 schedule 排行搜索、不为阳性重调 MV-Adapter、不默认追加第三 backbone，
不在证据冻结前把旧正文替换成未经验证的强新机制。此计划已把 GPU 计算指向明确
缺口；后续是否有利由固定实验回答。

## 执行状态更新 — 2026-10-06

- **E0 authority bookkeeping：PASS。** `CLAIM_EVIDENCE_AUTHORITY_LEDGER.json` 收录
  14 项主张、61 个带 SHA-256 的本地来源；每项还记录注册状态、队列选择、干预 profile、
  统计单位、估计方法与 multiplicity；`validate_claim_evidence_authority_ledger.py`
  检查 source hashes、必要字段、claim/source 引用和 manuscript freeze policy，结果见
  `CLAIM_EVIDENCE_AUTHORITY_AUDIT.json`。这只关闭唯一来源与 supersession 的账本
  建设，不等于科学证据冻结。
- **strict-276：限界措辞已落到 reviewer/claim 矩阵。** GC3−GFL FG-PSNR
  +1.207771 dB，名义对象 bootstrap 95% CI [+1.116967,+1.294989]，259/276 有利；
  是此前暴露 cohort 中的回顾性补充比较。该比较不是注册 Core-7 primary contrast，
  旧 GFL/GC3 的输入张量哈希链与共同 runner 身份不能完全核验。不可称新独立确认，
  不可替代旧 +0.96 dB 的复现。GC3−GFH 的指标方向混合：FG-PSNR −1.214235 dB，
  Full-PSNR +0.725229 dB，Full-SSIM +0.001229；五个 endpoint 方向有利于 GFH，区间
  均未作多重比较校正。
- **E1/E2：已完成而非待启动。** E1 为固定 B 子集 48 对象、3 个固定生成种子；E2 为
  同一子集的静态 2×2；两者 integrity 均 PASS，结果分别见
  `MULTISEED_ANALYSIS.md` 与 `STATIC_FACTORIAL_ANALYSIS.md`。估计仍限于已见对象与
  指定种子；不代表新对象确认，也没有等实际 dose 结论。
- **跨骨干：** MV-Adapter（98/99）与 MVDiffusion（75）分开作为 interface-specific
  边界证据；不池化结果，也不追加 GPU retuning 或第三骨干。
- **剩余高价值工作：** 等真实 LLH 答卷并按已冻结统计方案一次性分析；修复/撤回无效
  seam 证据；完成 portable clean-clone 与论文表图重建；SSI 对照后重新判定 R2.1
  contribution adequacy。当前没有由本次论文视角审查引出的新 GPU 生成任务。
- **最终状态未变：** `SCIENTIFIC_EVIDENCE_FREEZE=NO`、`SUBMISSION_READY=NO`、
  `NOT READY / HOLD`。提交稿仍冻结，所有正文修改待证据冻结后执行。

## 后续执行增补 — 2026-10-06 07:04 UTC

- **E5 已按独立技术协议冻结并完成。** 六个既有开发对象、原对象索引与
  `object_seed=42+index` 固定；174 次生成只存输出张量哈希，不生成或查看图像质量
  指标。每个 wrapper 在每个去噪步会经历 reference-write 与 target-read 两次调用；
  reference-write 原样通过，标准化扰动仅加在 target-read。runner、wrapper、reference
  pipeline、数据/生成/指标代码、checkpoint、config、pilot、auditor 与 launcher
  均在 `1006/data/e5_residual_dose/E5_LOCK.json` 中哈希锁定。CPU 剂量公式/FP16
  检查与 GPU 数值门槛 PASS：alpha-zero 六对象全相等，4860 个 target-read 步骤全部有限且
  relative-dose error≤5%。但 shallow 的 native cap=0.8 在 alpha=0.005 时已有 164/540
  步骤（30.4%）超过等效总尺度；deep/middle 未超过。按冻结规则不调 alpha 或 grouping，
  因而不启动三层 cap-respecting dose-match 正式实验；Layer×Window 结果仅限于原 profile/cap。
  完整结论见 `evidence/audits/E5_RESIDUAL_DOSE_FEASIBILITY_REPORT_20261006.md`。
- **Fresh C 输入筛查已完成第一阶段。** 600/600 资产下载成功、零下载失败；同本地
  1,965 个历史 GLB 做字节哈希比较后无重复，600 个中 594 个几何可读、6 个无效。
  594 已超过目标 N=300；正在做 17 视图/深度渲染、coverage 与 decoded-pixel 去重，
  完成 cohort freeze 前不启动 Fresh C 推理。首批 downloader 是源码更新前启动的旧进程，
  其 SHA-256 已从先前提交恢复并写入 download status；“zero failures”与旧状态文字矛盾已在
  元数据中显式规范化，原下载 manifest 未改。详见 `FRESH_C_INPUT_SCREEN_20261006.md`。
- **优先级保持。** Fresh C 的身份、行数、共享输入、cap、预测与 residual 完整性门禁
  通过前不解盲；E5 技术通过与浅层 cap 限制均保留。人类答卷、两项来源级授权和 R2.1
  贡献充分性仍是独立未闭合事项。01549 原稿和提交版 PDF 均保持不动。

## 文献闭环与 Fresh C 执行快照 — 2026-10-06 08:20 UTC

- **比较审查完成，不等于 novelty pass。** 代表论文的证据链和 SSI 直接重叠已写入
  `REVISION_STRATEGY_COMPARATIVE_EVIDENCE_20261006_ZH.md`；C13 已关联该报告并明确
  R2.1 仍需作者/编辑判断。SSI 所报告的系统 schedule 对照强于本稿当前的方法证据，
  因此不通过额外调参、显著性或更换名称来“补新颖性”。E5 显示浅层 native cap
  使本轮 dose-matched 三组机制实验不可行；若将来必须证明独立方法贡献，应另立方法
  问题、先做开发可行性，再在未触碰对象上注册验证，不能嵌入本轮 revision。
- **Fresh C render 运行中。** 截至 08:20，594 个 geometry-valid 候选中有 90 个完成
  17-view image/normal/camera 产物；meta 文件计数包含在制对象，不能作为完成数。
  CPU worker 和 Blender 子进程按 07:32 启动时锁定的 source SHA、Blender、HDRI 和
  512²/17-view 设置运行；reserve/cohort-freeze 代码后续修正未改变 renderer。
  完成 594 个筛查前不取样、不推理、不看方法质量。
- **Fresh C 的预定后续。** 完成像素级去重、coverage 与 cohort freeze 后，按已冻结
  四条件运行 main backbone；唯一 confirmatory pair 是 GC3−GFL 的 FG-PSNR。若完整性
  或方向不支持，按 protocol 降级/撤回相应 superiority，不转成其他条件搜索。该 2D
  campaign 本身不闭合 R1 的 human/seam/全 PBR 质疑。
- 文献报告、更新后的 E0 ledger 和本执行计划保留在 1006；08:20 时之前的证据快照已推送，
  当前分支随后更新到 `00c4891` 并纳入 MVPainter 比较。本节记录 08:51 后的新增验证。

## 干净检出复建与当前阻塞处置 — 2026-10-06 08:51 UTC

- **复建门禁有界通过。** 在公开分支提交 `00c48915877f592c725d5b13be90905eab347b0a`
  上建立了新的稀疏检出（来自本地 Git object database；GitHub HTTP pack 下载当时
  超时，因此不把它写成一次成功的远程 clone）。检出前 `SHA256SUMS.txt` 的 401 项
  全部通过；strict-276 与 Fresh-B 分析、24 行归因表、图、主文和补充材料均成功重建。
  重建 PDF 的提取文本与已发布 PDF 字节级相同，补充 PDF 文件本身相同，主文 PDF
  仅差 3 字节；5 张重绘图在 150 dpi 栅格对比一致。记录见
  `evidence/audits/CLEAN_CHECKOUT_REBUILD_20261006.md`。这关闭“压缩证据包能否从新检出
  重建”的子门禁；由于旧 GPU prediction/residual/render 原始载荷未完整打包，
  **完整历史生成复现仍 PARTIAL**，不能宣称全论文 end-to-end reproducible。
- **E0 来源账本扩充到 62 项。** C14 已精确拆分 compact rebuild PASS 与 historic
  generation PARTIAL；E0 validator 复跑后仍需核对哈希、引用和冻结规则。
- **Fresh C 仍按原锁定继续。** 08:51 UTC 快照为 125/594 个有效候选完成 17-view/depth
  产物；像素级去重、coverage 和 cohort freeze 尚未完成，method outputs 仍为零。
  不因等待或进度改变 worker、视角数、cohort、比较条件或主终点。
- **未闭合问题的可行动路由。** R1.5：公开缺失的历史输入/输出载荷清单；有授权且完整的
  运行才重建，无法补齐者按 campaign 限界或撤回依赖结论。R1 fidelity/seam：等待用户
  提供真实答卷；完成 seam 指标合成/已知跳变校验，否则继续撤回 seam claim。R2.1：
  SSI 对照和同类论文审查已完成但只能支持收窄，不能裁决期刊贡献充分性；当前 cap
  pilot 不支持等剂量机制试验，若该机制是必要贡献，应另立可行性设计并在未触碰 cohort
  前注册，不能用本轮 Fresh C 替代。资产授权仍需要来源级证据；两项若无法确认，需在
  投稿公开包中移除其图像及衍生图再重新审计。
- **Readiness 保持 HOLD。** Fresh C、人类数据、R2.1、seam/source-level rights 和最终
  reviewer/pagination gates 尚未全部通过。01549 在科学证据冻结前不改；本轮没有上传期刊
  系统或把候选说成已被审稿人接受。

## 来源授权复核与进度快照 — 2026-10-06 09:00 UTC

- 官方 Sketchfab API 只读复核 Panel 02/05：02 返回 HTTP 200 但 `license={}`；05 返回
  HTTP 404。响应日期和原始 body SHA-256 已存入
  `licenses/ASSET_SOURCE_LICENSE_RECHECK_20261006.json`，解释见
  `evidence/audits/ASSET_SOURCE_LICENSE_RECHECK_20261006.md`。这没有给出使用授权，因此公开
  分支现有图及 supplement 衍生图仍是 release blocker；下一步只能取得来源条款/许可，或移除
  两个资产及全部衍生内容后重建、重新审计。
- E0 authority ledger 扩至 63 个哈希来源；其中独立记录这次授权复核。09:00 UTC Fresh C
  17-view/depth 完成数为 152/594，coverage/decoded-pixel 去重及冻结仍未完成，method outputs
  为零。
- 最新 verdict 仍为 **HOLD**。此复核使权利问题更明确但没有关闭；人类问卷仍等用户答卷，R2.1
  仍是 venue/editor 判断，seam 若不能通过测量工具的已知真值测试则保留撤回，历史缺失载荷按
  campaign 边界披露或撤回依赖结论。
