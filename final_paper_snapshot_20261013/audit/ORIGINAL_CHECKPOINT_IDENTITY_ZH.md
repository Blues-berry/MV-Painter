# 原权重身份追溯裁决（2026-10-12）

本次只读核查本地文件、Git 工作树、既有配置/日志/CSV；没有启动训练、生成、烘焙或重新评价图像。轻量统计复算与审计输出仅写入本目录。核查范围是现存 14 个 Git 工作树及其本地 ignored 文件；根任务另行核实的私有远端为 **8 个分支**，包括新增的 `codex/paper-fac-bundle-20261012`。不能把历史 7 分支快照当作当前远端状态。

## 1. 旧 geotex_v2 已实际恢复，且三份同字节

不是仅找到 README 或 GitHub 文件名。本地实读权重后计算 MD5：

| 实际文件绝对路径 | 字节数 | 实算 MD5 |
|---|---:|---|
| `/4T/CXY/MV-Painter/checkpoints_saved_20260803/v2_old/geotex_v2_ema_final.pt` | 8,858,979 | `a74cc1d16cb473a95022bdcbc58e1b22` |
| `/4T/CXY/MV-Painter/mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt` | 8,858,979 | `a74cc1d16cb473a95022bdcbc58e1b22` |
| `/4T/CXY/MV-Painter/final/EM_questionnaire_notes/share_kit/checkpoints/geotex_v2_ema_final.pt` | 8,858,979 | `a74cc1d16cb473a95022bdcbc58e1b22` |

旧非 EMA final 的备份及原输出文件同为 35,429,599 字节，MD5 `910f22c583de2944b84d0bc0e3d40017`。这些实算值符合 `/4T/CXY/MV-Painter/checkpoints_saved_20260803/README.md` 的 2026-08-03 记录。

`v2_old/train_args.json` 记录：10000 步、seed 42、peak LR 5e-5、gradient accumulation 4、clip 0.5、EMA 0.9995。原 README 明确旧 schedule comparison 使用 v2_old。同名的 v3 EMA 为另一套权重，实算 MD5 `fbbdcf06aef251a16cc6e593b1cfa571`；6000 步 anticollapse 训练具有 shallow scale 0.1、projection norm clamp 1.5 和 var weight 0.01，日志记录末期 NaN 跳过更新。不得混用同名文件。

**裁决：旧 geotex_v2 EMA 文件身份闭合。旧 v2 配置来源有明确记录；完整训练采样顺序、所有表格的 runtime/metric/input 链并未因文件恢复而自动闭合。**

## 2. 原 01549 主表不是这份 v2

权威来源：`/4T/MV-Painter-main/1008/audits/01549_MAIN_ADAPTER_VS_FRESHC_IDENTITY_AUDIT.md`，对照原提交源与 Fresh C manifest。原主表 Table 4 使用历史 `geotex_refattn_v1/geotex_step_0002000.pt`；强残差 v2 属于原 Table 9 的独立扩展（记录 1706 训练对象），不能替代 Table 4。历史 Table 4 未绑定原权重 hash、完整 runner hash、实际 hook/cap 列表及 metric 版本。

本次对现存 14 个工作树执行包含 ignored 文件的 geotex `.pt/.pth` 路径清点：找到 v2、v3、早期扩展/quick、20260928/20261012 重训和 1010 native 重训；没有找到 `geotex_refattn_v1` 的原目标文件。具有 `geotex_step_0002000.pt` 文件名的现存文件是新重训，不是找到原始主权重的证据。

Fresh C 使用受控重训权重 SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`；原 Table 4 没有可比 hash。其 300 UID 与原训练/原测试/24 probe/clean-v2 测试的 UID 均不重合；这是内部配对的新队列研究，不能称旧 +0.96 dB 直接复现。其 hash-pinned runner 与原实现的逐节点、cap、端点等价性也未完整认证。

**裁决：原 01549 v1 主表身份无法闭合；历史 +0.96 dB 不可同权重重放。** 终止理由是目标文件未在授权范围内发现、原始 hash 未记录、旧 runner/端点/run-level 输入身份缺失。继续重训会产生新实验而不能恢复这条身份链；此次结束追溯，不以类似文件名或旧 v2 MD5代替证据。

## 3. 20261012 原 276 请求名单的留出重训：有新证据，也有实际替换

来源：`/4T/CXY/MV-Painter/final/round2/main_adapter_original276_leaveout_20261012/protocol_manifest.json`；CSV：`/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_original276_leaveout_20261012/eval_original276_unique6/per_object_metrics.csv`。

已逐项实核：

- 请求评估名单精确等于原 test300 的 0-based 位置 24–299，顺序一致，共 276 个唯一 UID。
- 历史受控 train1118 与该请求名单有 **79** UID 重合；删除名单恰好等于此交集；1039 新训练 UID 恰好是 1118 减 79，训练/请求评估交集为 0。
- 新训练 seed 20261012、2000 步、LR 1e-4、256 训练，训练报告用时 1050.77 秒；新 final-step SHA-256 实算 `19ae8afa08886f774c1b18e1888badbc47108f820774906cd875a5aaa33cf05c`，与 manifest 一致。
- `/tmp/mv_main_rerun/geotex/train.py` 和 `model_unet_geotex.py` 的当前文件 hash 与所记录训练来源一致。配置中的 dropout 0.1 不等于入口实际执行了 dropout；第007轮已经核实同训练入口忽略它。
- CSV 有 1104 个唯一 ordinal×condition 行，四条件完整；每条件 276 张 PNG，GT 276 张。实际完成于北京时间 2026-10-12 11:36–13:58。

**但实际 UID 门槛失败。** evaluation.log 的 623–624 行记录空有效深度的 `min()` 错误和 `wrong path: .../f7ef602b19214debb0b350db9af55ff2/image`。请求 UID 对应 `obj_0046`。loader 的 exception 分支随机改 index 后继续，返回数据不包含实际 UID；`collate_batch` 未校验 UID，runner 把原 ordinal 写入 CSV。因此日志显示 277 次 loader 基目录打印、一次 retry，而不是 276 个原 UID 经运行时认证。替换后的实际 UID未记录；请求 manifest 不是实际样本证明。报告不能写“原276对象已全部有效评价”“精确原队列身份闭合”。

这组对象曾出现在历史研究决策中，不是 pristine 确认集。合理标签为：**去掉训练/请求名单重合的新权重、276 ordinal 配对的后见协议敏感性，含一次已记录的未知实际 UID 替换；排除受影响 ordinal 的 275 行组敏感性另列。** 未复用它作为 Fresh C 原主检验，也未覆盖历史结果。

## 4. 该新研究的端点不是可互换的“PSNR”

当前 helper 把六张 256×256 目标视图排成 3×2 图网格。full PSNR 是整网格像素 MSE 的 `10 log10(1/MSE)`；FG-PSNR 是 mask>0.5 前景像素的 MSE，同样取 log，**不是六个视图 PSNR 的简单平均**。FG-LPIPS 把网格变换至 [-1,1] 后给两图乘前景 mask，再取 AlexNet LPIPS 标量。当前源码快照只能解释现存实现，不能追认没有 live-captured hash 的全部 runtime bytes。

后见复算 C3−Fixed High（N=276 ordinal；点态 10000 次 bootstrap CI）：

| 端点 | 均值差 | 点态 95% CI | C3 有利 ordinal |
|---|---:|---|---:|
| Full-image PSNR | +1.69908 dB | [+1.62148,+1.77602] | 276/276 |
| FG-PSNR | −1.31354 dB | [−1.38483,−1.24106] | 9/276 |
| FG-SSIM | −0.059606 | [−0.063031,−0.056050] | 9/276 |
| FG-LPIPS | +0.011271 | [+0.010220,+0.012328] | 30/276 |
| Edge-SSIM | −0.027775 | [−0.029367,−0.026130] | 5/276 |

全图 PSNR 正增益同时伴随明显前景劣势；不可选取全图端点把它解释为纹理质量胜出。8 个端点×3 比较的完整后见分析在 `ORIGINAL276_RETRAIN_AUDIT.json`；exact RNG/重采样顺序在 `RECOMPUTE_ORIGINAL276_AUDIT.py`，已与前述 JSON 的均值、CI、p 全部逐项一致。技术性删除 `obj_0046` 的分析在 `ORIGINAL275_SENSITIVITY_STATS.json`。均不构成预先指定主检验。

## 5. FAC 恢复等级

第015轮的 84 份原字节文件和 3 个 CPU 控制器 fixture 是真实源码交付/组件检查；它们没有恢复历史1706训练名单、seed、checkpoint与逐表runtime身份。早期训练默认同时更新 adapter/encoder，后期只训 controller；FSC 实际为 FFT 而非注释所说的 DCT，初始频率掩模不是严格恒等。新 `codex/paper-fac-bundle-20261012` 的 e1f54f91 是保守 r2 **论文/图表/回复包装提交**，没有新增 FAC 训练或图像质量证据。保留工作树中的未提交工作笔记也不能算新独立实验。

最终分开三个结论：**旧v2权重已恢复；原v1主表身份仍无法闭合；新276请求名单重训存在实际替换，只能作有界协议敏感性。**
