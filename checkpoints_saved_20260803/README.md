# Checkpoint 备份快照 (2026-08-03)

在继续"fixed_high vs C3 矛盾"探索前保存的两个 checkpoint 版本。
所有文件均已用 `cmp` 校验与源文件逐字节一致（见下方 md5）。

## 两个版本的关键差异（训练配置，源自 train_args.json / train_v2.py）

| 项目 | v2_old（旧） | v3_current（当前） |
|---|---|---|
| 目录 | mvpoutput/geotex_v2 | mvpoutput/geotex_v3_anticollapse |
| 训练步数 | 10000 | 6000 |
| peak_lr | 5e-05 | 8e-05 |
| grad_accum | 4 | 2 |
| grad_clip | 0.5 | 1.0 |
| **shallow 层 scale cap** | 无 | **0.1（重度抑制浅层）** |
| output_proj 权重范数 clamp | 无 | **1.5** |
| var_weight（防模式坍缩） | 无 | **0.01** |
| 训练末期状态 | 正常 | step 5995-6000 全部 NaN，跳过 |
| EMA 可用 | 是 | 是 |

v3 的 anticollapse 约束来源见 `geotex/train_v2.py`：
- `module._adapter_scale = 0.1` for shallow（浅层强抑制）
- output projection weight norm clamping（cap=1.5）
- 设计动机：v2_ext 中 shallow layer 0 的 correction/hidden 达 10.5x，防模式坍缩

## 文件清单

### v2_old/（来源 mvpoutput/geotex_v2/checkpoints/）
- geotex_v2_ema_final.pt   md5=a74cc1d16cb473a95022bdcbc58e1b22
- geotex_v2_final.pt       md5=910f22c583de2944b84d0bc0e3d40017
- train_args.json

### v3_current/（来源 mvpoutput/geotex_v3_anticollapse/checkpoints/）
- geotex_v2_ema_final.pt       md5=fbbdcf06aef251a16cc6e593b1cfa571
- geotex_v2_ema_step_001000.pt md5=98765852575fd99b2963f3cae159b66e
- geotex_v2_final.pt           md5=5cc3bd77835a8a54c856154fda4547f9
- geotex_v2_step_001000.pt     md5=878ef5b2cfefd57f7a676d04bb82c2af
- train_args.json

## 注意
- 两个版本的 `geotex_v2_ema_final.pt` / `geotex_v2_final.pt` 文件名相同但内容不同，
  探索实验加载时必须区分路径，不能混用。
- 已存在的 schedule 对比表（mvpoutput/revision_schedule_comparison/）使用的是 **v2_old** checkpoint。
