# Fresh C：C3、LLH 与 generic-linear 的证据对齐 — 2026-10-06

## 当前判断

新的 300 对象 cohort 支持原生 cap 下 C3 相对 GFL 的前景指标改善；独立锁定的同 cohort 附录显示，LLH 与 generic linear 之间仍有前景 PSNR/LPIPS 权衡，且 LLH−C3 的对象响应高度异质。**不能据此宣布 C3、LLH 或 linear 是跨端点总赢家，也不能把均值差解释成典型对象都会获益。** Fresh C 与附录是 revision-era 新 cohort 验证，不是原 01549 的预注册复制。

## Cohort、执行与完整性

- 冻结 cohort：`FROZEN_FRESH_C_300`，300 个唯一 UID；UID 清单 SHA-256：`d93881865b6478dd31222a51c7d3ebafe44839fd5e1b76c5eb9605d3f1fdfa58`。
- 主 run 是 `no_adapter / native_gfl / native_gfh / native_gc3`，共 1,200/1,200 行；输入嵌入清单 SHA-256：`50f28b3f17ef5537ec0ab56a36c3c3c142486e5a7333adaf2a51d87cc83c8a2f`。身份、行覆盖、共享输入、有限数值、cap trace、预测图和残差日志门禁全部 PASS。
- Revision-era 附录只增加 `layer_llh / gen_linear`，600/600 行；与主 run 共用 cohort 清单、UID 顺序、六类输入张量、seed 42、checkpoint、runner 与 cap 语义。其独立完整性检查全部 PASS；两个条件没有被合并改写进原四条件协议。
- 主结果是一个单独的注册 primary FG-PSNR 检验；附录三项命名对比 × FG-PSNR/FG-LPIPS 构成预先锁定的六检验 Holm 家族。其余 Core-7 结果属于各自冻结的 15 检验次要家族。对象是推断单位，视角和 seeds 不增加 N。
- 独立差值方向复核重算了 primary 和 21 项附录检验的均值、配对 p、Holm p、端点方向和有利对象比例：**28 项检查 PASS，无符号或多重比较差错。**
- 执行中发生过 GPU lease 锁交接死锁：主闭环在等待附录时仍持有共享 GPU 锁，附录尚未推理。故障和状态哈希已归档；主四条件完整性 PASS 后释放已空闲的主流程锁，附录按原冻结设置完成。无条件、对象或输入更改，见 `data/fresh_c/FRESH_C_ADDENDUM_GPU_LOCK_HANDOFF_INCIDENT_20261006.json`。

## 锁定比较

所有差值均为 A−B；PSNR 越高越好，LPIPS 越低越好。CI 为对象 bootstrap 95% 区间；附录 p 值按六个 primary 端点检验做 Holm 校正。

| 比较 | FG-PSNR：均值 [95% CI]；中位数；A 有利对象比例；Holm p | FG-LPIPS：均值 [95% CI]；中位数；A 有利对象比例；Holm p |
|---|---|---|
| C3−GFL（原 primary） | **+0.522 dB** [+0.404, +0.641]；+0.555；68.7%；配对 p=5.70×10⁻¹⁶ | **−0.005345** [−0.006326, −0.004403]；−0.004547；71.0%；次要家族 Holm p=3.23×10⁻²² |
| LLH−C3 | **+0.621 dB** [+0.391, +0.855]；−0.153；46.7%；Holm p=1.23×10⁻⁶ | **−0.01214** [−0.01386, −0.01048]；−0.01084；75.0%；Holm p=8.99×10⁻³⁴ |
| LLH−generic linear | +0.0276 dB [−0.0148, +0.0698]；+0.0170；52.3%；Holm p=0.201 | **+0.001372** [+0.000762, +0.002081]；+0.000176；LLH 有利 46.7%；**Holm p=1.14×10⁻⁴** |
| C3−generic linear | **−0.593 dB** [−0.837, −0.351]；+0.074；C3 有利 51.7%；Holm p=7.16×10⁻⁶ | **+0.01351** [+0.01160, +0.01549]；+0.01223；C3 有利 25.7%；Holm p=1.31×10⁻³² |

### 对叙事的含义

1. **原 C3 结果获得新 cohort 的限定支持。** 相对 GFL，C3 的 FG-PSNR primary 均值、区间和有利对象比例都为正；FG-LPIPS 也朝有利方向。这支持“在本 cohort 和 cap profile 下，C3 在这些图像指标上优于 GFL”，不支持全任务质量或最终纹理赢家。
2. **LLH−C3 的 FG-PSNR 均值受明显对象异质性影响。** 均值为 LLH 有利，但中位数 −0.153 dB 且有利对象比例仅 46.7%；LPIPS 则在均值、中位数和 75% 对象比例上均有利于 LLH。与此同时，LLH−C3 的 full-image LPIPS 均值 +0.00491、full SSIM 均值 −0.00433，方向均不利于 LLH。不能将前景均值概括为典型对象或全图改善。
3. **Generic linear 是强对手，且历史方向更正得到新 cohort 支持。** LLH−linear 的 FG-PSNR 区间跨零，且无等效界值，所以只能称“没有检出差异”，不能称等效。LLH−linear FG-LPIPS 为正，低值更好，因此该差异有利于 linear；对象有利比例仅小幅过半，效应绝对量为 0.001372。它延续历史 Experiment C 的方向更正，但 Fresh C 自身仍是有限量级的端点差异，不等于总体验证。
4. **C3−linear 是指标和对象分布的双重权衡。** cohort 均值的 FG-PSNR 与 FG-LPIPS 都有利于 linear，但 PSNR 中位数略有利于 C3、51.7% 对象的 PSNR 差值也有利于 C3；这说明均值结论对少量大负差值敏感。完整对象排序与反例保留在图集，不删除尾部对象。
5. **分数很小的 p 值不等于效应普遍或重要。** 所有统计单位仍是 300 个对象；统计显著性、均值/区间、对象中位数、有利比例和未见视角/人工感知是不同问题。

## 对比图与对象索引

最终图集在两份独立 integrity gate 和分析完成后生成，覆盖 cohort 全部 300 个对象。20 组图按 C3−GFL、LLH−C3、LLH−linear、C3−linear 四个锁定比较各选五个对象，分别覆盖端点高/低/接近中位或极端；每组显示同 UID、同六视角的参考、GFL、GFH、no-adapter、C3、LLH、generic linear。单对象不计算显著性，也没有合成跨指标总分。全体对象差值、端点独立排序、cohort 统计排序、森林图和生成资产哈希均随图集保存。

- 总览：[20 组 contact sheet](/4T/CXY/MV-Painter/1006/figures/strategy_comparison_gallery/fresh_c_final/20_groups_contact_sheet.png)
- 全部完整 UID 图：[图集目录](/4T/CXY/MV-Painter/1006/figures/strategy_comparison_gallery/fresh_c_final/panels)
- Cohort-level 效应：[contrast forest plot](/4T/CXY/MV-Painter/1006/figures/strategy_comparison_gallery/fresh_c_final/cohort_contrast_forest.png)
- 排序表：[contrast summary](/4T/CXY/MV-Painter/1006/figures/strategy_comparison_gallery/fresh_c_final/cohort_contrast_summary_ranked_within_family.csv)；对象差值与秩见同目录 `rankings/`。

图集按对象差值选择可读案例，不用于选择人工评测对象或产生独立证据。选取、PNG 对应关系和来源 SHA-256 见 `gallery_manifest.json`、`gallery_asset_sha256.csv`。

## 仍未关闭的审稿门

- 人工保真：0 份真实答卷；旧 LLH 包未分发且继续封存。新四对比计划为 C3–GFL、C3–GFH、C3–no-adapter、LLH–linear。参考外观 fidelity 与自然度分开问；40 槽、每人 24 题、最低 36 份完整有效答卷、对象×参与者双向 bootstrap、八端点 Holm。没有伦理/同意记录和源素材归属清单前不得分发。
- GLB/未见视角：原 N=20 GLB-native 数据仍是 sampler-conformant、unlit base-color 的历史补充，不能代替新 cohort 的导出纹理验证。新 Fresh C 的 24 个 UV/权利标签合格对象已按输入侧冻结顺序选出，但新的烘焙实现、相机映射和 glTF sampler 技术门尚未通过；该子集与同 cohort 共享对象，不是独立 held-out 3D 样本。缝指标仍不成立。
- R2.1 新颖性/贡献充分性：SSI 等相关工作已被发现，仍是投稿判断，不会由 Fresh C 正结果自动关闭。
- 权利/交付：所选新 3D 对象均带 CC BY 标签，作者/来源归属及公开衍生图授权仍需落实；之前公开分支上已有两个素材来源许可未确认的衍生物。当前不推送、不宣称 release-ready。
- 因上述限制，01549 正文继续保持未修改；scientific evidence freeze、reviewer closure 和直接系统上传均为 **NO/HOLD**。

## 权威数据与复现入口

- 主 integrity：[FRESH_C_INTEGRITY_GATE.json](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_INTEGRITY_GATE.json)；统计：[fresh_c_c3_minus_gfl_analysis.json](/4T/CXY/MV-Painter/1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json)。
- 附录 integrity：[FRESH_C_ADDENDUM_INTEGRITY_GATE.json](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json)；统计：[FRESH_C_ADDENDUM_ANALYSIS.json](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json)。
- 独立符号/校正审计：[FRESH_C_RESULT_DIRECTION_AUDIT.json](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json)，由 `python 1006/scripts/validate_fresh_c_result_directions.py` 重建。
- 运行日志和行级原始结果位于 `1006/data/fresh_c/runs/c3_confirmation/` 与 `runs/revision_era_addendum/`。方法输出及大体积原始素材不因本报告变为可公开分发文件。
