# Fresh C 证据闭环与后续门禁对齐 — 2026-10-06

> 本文中的 `SCIENTIFIC_EVIDENCE_FREEZE=NO` 是 2026-10-06 的历史状态。2026-10-07 四个 P0 关闭后，受限主张的科学证据冻结已为 YES；当前审稿与交付状态仍为 PARTIAL/HOLD。见 `../../gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md` 与 `../../gates/FINAL_READINESS_VERDICT_20261007.md`。

## 当前结论

Fresh C 的原四条件主实验、独立锁定的 LLH/linear revision-era 附录、方向与 Holm 复核，以及比较图集均已完成并通过各自技术门禁。它们关闭了**图像空间策略比较**这一阶段，不等于论文证据冻结或审稿闭环。01549 提交稿仍保持原样。

Fresh C 的 C3−GFL 前景 PSNR 主比较为 +0.522 dB（对象 bootstrap 95% CI [+0.404,+0.641]，N=300）；LPIPS 也朝有利于 C3 的方向。附录则显示 LLH、C3、generic linear 在端点与对象分布上的权衡：LLH−C3 的 FG-PSNR 均值为正，但中位数为 −0.153 dB，46.7% 对象有利于 LLH；LLH−linear 的 FG-PSNR 未检出差异，FG-LPIPS +0.001372 经六检验 Holm 校正后仍显著且有利于 generic linear。没有非劣效界值，不得称两者等效；也没有跨指标总赢家。

## 已关闭的本阶段工作

- Fresh C 冻结 N=300，原四条件 1,200/1,200 行通过身份、输入、有限指标、cap trace、预测和残差日志门禁。唯一注册 primary C3−GFL FG-PSNR 支持正向 cohort 均值差。
- revision-era 附录在同 cohort 加入 LLH 与 generic linear，600/600 行通过独立门禁。三项命名对比 × 两个 primary 端点组成六检验 Holm 家族；五个 secondary Core-7 端点形成独立 15 检验家族。
- 独立方向复核从原始配对行重算主检验和 21 项附录统计，共 28 项检查 PASS。正 LPIPS 差值按 lower-is-better 解释；历史 LLH−linear 方向更正仍有效。
- 六策略图集覆盖 20 个对象案例及全体 300 对象的独立端点排序、差值和 cohort 森林图。案例包含不利结果；单对象未计算显著性；图集不用于选择人评样本。
- GPU lease handoff 死锁发生在附录推理前。事件和哈希保留；之后冻结的附录设置未变并独立完成。

## 可用于论文的边界措辞

Fresh C 可以支持：“在该冻结 cohort 和原生 cap 执行配置下，C3 相对 GFL 的前景 PSNR 平均差为 +0.522 dB；对象响应存在差异。”可附带报告 FG-LPIPS 的配对差。附录应明确列出 LLH−C3 的均值/中位数/有利对象比例，以及 linear 在 LLH 对比中的 LPIPS 优势。

不得从这些数据推出整体 3D 质量、人类感知保真、剂量无关的 Layer×Window 机制、跨骨干迁移、LLH 与 linear 等效、或唯一最优 schedule。Fresh C 是修订期新 cohort；附录受此前 Fresh B 结果启发，不是 01549 原预注册的复制。

## 人工与三维样本选择的协议校正

当前 24 个 GLB 候选按 Fresh C 冻结 cohort 顺序，选择最先满足源 GLB 哈希、许可标签和有限 UV 条件的对象。选择代码没有读方法预测或指标，但主实验汇总结果在选择前已经可见。因此该集合是同 cohort 的 outcome-blind、资格筛选子集，不是独立 3D holdout。它也**没有实现旧 handoff 草案提出的 texture/coverage/geometry 分层**，不能再称为分层样本。

为避免另选一组并制造结果筛选疑虑，后续如启动人工评测，使用同一份冻结 24 UID 清单，并在参与者包锁定中写明它是按资格和 cohort 顺序形成的固定案例集。不得称其为分层或独立样本；在完成权利、伦理/同意、展示素材与分配 manifest 核查前不得分发。所有 24 个对象目前只有 CC BY 标签；作者归属和衍生素材公开权利尚未清账。

新的 3D 面板仍没有烘焙或未见视角输出。只读代码检查发现现有 `BakePipeline.call_bake` 会调用 `mesh_uv_wrap`/xatlas 并替换 UV；9/24 个冻结 GLB 的有限 UV 坐标在 `[0,1]` 之外，因此该入口不能原样用于新面板。`render_glb_native_egl.py` 只渲染已烘焙 GLB，不提供新 bake。技术门与后续验证项详见 `protocols/FRESH_C_GLB_BAKE_FEASIBILITY_AUDIT_20261006.md`。下一步若实施，必须原样保留 UV/采样语义，先通过已知纹理合成图、相机映射、glTF sampler 和源资产 lineage 检查，再冻结 bake 和 view 协议；资格失败要保留，不得看方法输出后换对象。若无法通过，保留历史 N=20 unlit base-color 结果并关闭新 3D 主张，不推断 seam 或全 PBR。

## 剩余总门禁

人工结果需要真实答卷；项目负责人仍需提供来源权利和伦理/同意记录。R2.1 贡献充分性仍是审稿判断，近似先行工作 SSI 未因 Fresh C 结果消失。strict-276 的旧输入哈希缺口、两个图件的来源许可疑点、seam 指标和论文全量 GPU 重建仍分别保留原边界。故当前为 `SCIENTIFIC_EVIDENCE_FREEZE=NO`、`REVIEWER_CLOSURE=PARTIAL`、`DIRECT_SYSTEM_UPLOAD=NO`。

下一步按以下次序推进：先维持本报告、数据、图表和账本为统一权威；完成源素材归属/伦理核对和人评素材包锁定；单独完成或明确撤回新的 GLB/seam 端点；再汇总人评真实数据；然后更新主张账本和审稿闭环矩阵。只有这些结论冻结后，才改写提交版和逐条回复，并执行干净环境重建及页码复核。R2.1 若仍没有足够方法贡献，应保留 HOLD 并重新评估投稿适配。

## 权威产物

- 主结果：[Fresh C 策略比较报告](FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md)
- 图像比较：[最终 20 组图集](/4T/CXY/MV-Painter/1006/figures/strategy_comparison_gallery/fresh_c_final/20_groups_contact_sheet.png)
- 主完整性：[Fresh C 主门禁](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_INTEGRITY_GATE.json)
- 附录完整性：[LLH/linear 附录门禁](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json)
- 方向审计：[差值方向复核](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json)
- 当前总门禁：[最终 readiness verdict](/4T/CXY/MV-Painter/1006/gates/FINAL_READINESS_VERDICT.md)
