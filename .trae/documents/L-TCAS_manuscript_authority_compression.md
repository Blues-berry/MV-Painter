# L-TCAS 论文权威压缩重构方案（AUTHORITY_COMPRESSION 已授权）

## Context

Gate-3 关闭后（commit `9a77891`，EVIDENCE_FREEZE=YES），被授权的下一阶段是把稿件重构为以 **strict-276 Core-7 same-runner 七条件矩阵**为唯一当前 baseline 权威面，并采纳 01549 叙事决策报告的 **N1 路线**。用户已确认三项决策：
1. **完整 L-TCAS 重构**（方法名 L-TCAS，TCAS/C3 = shared-layer 特例）；
2. **标题改 Option B**："Layer-wise Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation"（现标题仅 "Stage-aware" → "Timestep-Conditioned" 一处词组变化）；
3. **legacy 三表全部下放补充材料**。

硬约束：无新实验/无 GPU inference；所有数字来自冻结 CSV；43 条参考文献不动；禁用词表清零；全文单一 benefit-oriented 展示约定；页数目标 ≤15pp（现 13pp）。

## 关键设计规则

- **CI 一致性规则**：Core-7 矩阵段落统一引用 `CORE7_FINAL_PAIRED_STATISTICS.csv`（如 LLH−GFL +3.2443 [+2.9463,+3.5305] 242/34）；pre-registered confirmation 的历史叙述（S11/letter）保留其协议锁定原 CI（[+2.936,+3.542]）；同一对比不得在相邻段落出现两个 CI 并列。补充材料 S11 加一句说明两者为两次 bootstrap 运行、各自协议锁定。
- **不得声称 GFH>GFL**（Full-PSNR CI 跨零）；LLH−GC3 的 Full-SSIM CI 跨零写 "no detected difference"。
- **M3 与 B′ 不得混入同一比较句**；措辞用 "robust across the tested contiguous mapping choices"，禁 "invariant"。
- **禁用词清零**：`generalize across backbones / automatically discovers / universal optimal / the optimal LLH / improves texture quality（无限定）/ invariant / unseeded / +0.96 / 14.78 / cross-view fidelity / all phases closed`。
- **"best" 必须列具体 metric**：LLH best-of-seven 仅限 FG-PSNR / FG-LPIPS / Full-PSNR / Full-SSIM；诚实反向三格必须保留（FG-SSIM→No Adapter 0.4799；Full-LPIPS→GFH 0.1967；Edge-SSIM→GFH 0.5538）。

## 权威数字（已亲验 CSV）

Core-7 聚合（n=276，FG/Full-PSNR dB）：No Adapter 8.826/10.563；GFL 10.731/18.229；GFH 13.153/18.242；GC3 11.939/18.968；LFM 13.100/19.516；LHL 12.974/19.635；**LLH 13.975/20.828**。
Core-7 配对（benefit 口径）：LLH−no_adapter FG-PSNR +5.1490 [+4.8964,+5.3959]；LLH−GFL +3.2443 [+2.9463,+3.5305] 242/34；LLH−GFH +0.8223 [+0.6168,+1.0330] / Full-PSNR +2.5852 [+2.4001,+2.7690]，反向 FG-SSIM −0.0164 / Full-LPIPS −0.0021 / Edge-SSIM −0.0062；LLH−GC3 +2.0365 [+1.8068,+2.2608]；LLH−LFM +0.8750 [+0.7724,+0.9793]；LLH−LHL +1.0008 [+0.9088,+1.0942]。
其他：M3 映射敏感性 16/18 MAPPING_STABLE（P1 PSNR +0.097→+0.147、CIEDE2000 +0.344→+0.484）；R0/R1 稳健性 27/28 STABLE_STRONG +1 STABLE_DIRECTIONAL；纹理 Part B（n=275）llh−fixed_mean CIEDE2000 +2.79101 [+2.55311,+3.04778] 271/275；seam（`BAKE_SEAM_AUDIT_20261001/SEAM_AUDIT_AGGREGATES.json`，旧 4.40 报告禁引）LLH 4.885 < LHL 5.598 < G-C3 7.545 < G-FL 8.865。

## 一、final_round2.tex 逐节指令

新结构树：Title/Abstract → 1 Intro → 2 Related → 3 Method(3.1–3.5) → 4 Experiments(4.1 Setup / 4.2 Core-7 / 4.3 Development probe / 4.4 Texture & Robustness / 4.5 Bake / 4.6 Transfer & Boundary / 4.7 FAC 短段) → 5 Limitations → 6 Conclusion。

1. **标题/摘要/贡献**（L25-28, 32-35, 63-75）
   - 标题换 Option B；keywords（L37-40）同步 L-TCAS 命名。
   - 摘要按 01549 七步逻辑重写（L272-281 模板句为底）：global scale 混淆 depth×stage → S=[s_{l,k}] 训练无关分配 → shared-input 分解 + pre-registered strict-276 same-runner Core-7 → primary fidelity 增益与 SSIM/感知权衡并存 → MV-Adapter 部分迁移/temporal 架构依赖/MVDiffusion 负边界 → 12-object bake+seam 案例 → 拒绝 universal schedule。
   - 贡献四条（01549 L302-307，不列 CAI）：①问题/度量 ②formulation（TCAS/C3=shared-layer 特例）③分解+strict-276 确认 ④transfer/边界/practical。
   - Intro 问题句 "when should residuals dominate"（L53-61）改为 where×when 双轴。
2. **Method（L103-224 → 3.1–3.5）**
   - 3.1 基础管线 + layer-indexed 注入（L106-128，h'_{l,t} 主式）；
   - 3.2 allocation matrix S=[s_{l,k}] 定义 + 四特例（吸收现 L154-168）；
   - 3.3 specializations 与实现语义（L179-206：caps = evaluated implementation 语义、up-block 映射、开销；保留 "development-selected, holdout-frozen" 表述）；
   - 3.4 评估四维度（L130-152 压缩）；
   - 3.5 CAI 描述性诊断（L208-213 保留 Remark，入 diagnostic 不入贡献；theorem/ε 机制移 supplement）；
   - FAC（L215-224）压为一段，细节下放 S7。Figure 1 caption 改称 L-TCAS。
3. **4.2 Core-7 主面（新写）**
   - 删 tab:strict276（L453-469）、tab:stage276（L487-503）、tab:serialized276（L523-548）、tab:confirmation（L575-594）；正文各留一句 legacy 指针（→S2/S3/S11）。
   - 新单表 7 行×7 指标（数字如上），caption 注明 4 条 pre-registered candidates（GFL/LFM/LHL replica/LLH）+3 条同冻结协议补齐 arms（no_adapter/GFH/GC3）；加粗 4 个 primary 指标列 + 诚实反向 3 格。
   - 配对段全用 CORE7 CSV；pre-registered 确认叙述（协议冻结于任何 holdout 数字之前）保留但 CI 引用按一致性规则。
4. **4.3 Development probe**（L301-435）：tab:layerablation/tab:factorial 保留，叙述压缩，统一 "development-selected" 措辞。
5. **4.4 Texture & Robustness（新）**：Part A 探针（distance-to-GT，LLH vs GFL 全显著、对 LFM/LHL hf_energy 反向如实）与 Part B CIEDE2000（n=275）分行呈现并声明两 surface 不混用；R0/R1 句（27/28 STABLE_STRONG）。
6. **4.5 Bake**（L627-689）：压缩；加 corrected seam ΔE00 四值（标 12-object case study）；cross-view 只写 "render-time cross-view color-stability descriptor"。
7. **4.6 Transfer & Boundary**（L702-753）：MV-Adapter layer-wise SUPPORTED（PSNR/ΔE00/GT-texture CI 排零；FG-/Edge-SSIM 小反向；LPIPS ns）+ "prespecified topology-derived grouping" + mapping 句（M3 两值；B′ 全不分离；两者分句）；MVDiffusion 段：INTERFACE-BOUNDARY EXPERIMENT、PARTIAL 接口（depth latent concat 禁缩放、9 CPBlock+α）、NOT_REPLICATED 如实；结论句用 `CROSS_BACKBONE_FINAL_CLAIM_BOUNDARY.md` L46-51 模板。
8. **Limitations/Conclusion**（L755-823）：按七条 claim-width 收窄；结论末句换 01549 L435-437 首选句（"A geometry adapter should not be treated as having one inference-time strength…"）。修复 L257 内联 subsection 标题断行。Data availability 与 bib 不动。

## 二、supplementary_round2.tex

- S2 扩为 "legacy uncapped panels"：接收三个下放表（含 serialized SSIM CI）；S3 不动。
- S11 加 CI 双 bootstrap 运行说明句。
- 新增 S12 Robustness & stability：R0/R1 表、M1/M3 mapping 对照、B′ budget-neutral；可含 Part A 明细。
- S7 接收 FAC 训练细节；S9/S10 不动；标题/首页同步 Option B。

## 三、response_letter_round2.md 最小同步

- 开头 editorial note：L-TCAS 命名 + 标题变更 + "formal generalization prompted by the reviewer's methodological concern, not post-hoc renaming"。
- R2.1 措辞对齐 allocation matrix/特例表述；R2.2 保留；R1.2 CI 维持协议锁定值。
- Package changes 段更新：Core-7 单表、legacy 表下放 S2、新 S12。

## 验证

1. `pdflatex` ×2 零 error/零未定义引用；主稿 ≤15pp、补充材料编译通过。
2. 禁用词 grep 清零（对三文件）：`generaliz\w* across backbone|automatically discover|universal optimal|the optimal LLH|improves texture quality|invariant|unseeded|\+0\.96|14\.78|cross-view (fidelity|consistency)|all phases closed`。
3. 数字三方抽查（正文 vs 冻结 CSV vs letter）：Core-7 七均值、六组配对 CI、seam 四值、27/28、M3 两值、Part B CI。
4. 43 条 bib diff 为空；Git diff 确认未触碰 coordination 审计文档（除新增 build 产物外不入库）。

## Commit

全量验证通过后单次提交（惯例 add -f final/ 下文本交付物）：
`docs: restructure manuscript as L-TCAS with Core-7 authority surface`
推送 `origin/codex/final-evidence-freeze-20261001`（HTTPS 代理若再 502 则用 SSH 传输）。
