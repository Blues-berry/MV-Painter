# 01549 修订 P0–P3 增量轮计划（2026-10-11）

## 规则继承（与此前 agent 一致）

1. 不修改任何既有文件、稿件、实验目录；一切新增写入本文件夹。
2. 在途 GPU 队列（iteration012 四个监督器串行接力）绝不插入、重启或终止；失败保留，不自动重试。
3. 评价先冻结协议后执行；SHA256 记录来源；禁止逐对象挑优、禁止事后选样。
4. 负结果与失败证据完整保留。
5. 本轮所有产物仅为本文件夹内的增量证据与预案，不改写 conservative_final 交付。

## 现状核查结论（2026-10-11 凌晨核实）

| 项 | 状态 | 证据 |
|---|---|---|
| P0 iteration012 队列 | 运行中：dev32 基线 seed2026 view_projection 生成中；interaction/MV-Adapter/APG 排队 | `PERSISTENT_QUEUE_STATUS.json` |
| P0 早期信号 | seed42 view_projection vs native：source 视角 FG-PSNR +2.92 dB；未见视角 −0.41 dB（单种子开发集，不作确认） | `development32_seed42_view_projection_evaluation/DESCRIPTIVE_COMPARISON.json` |
| P1 native_unset 生成 | 10 对象烘焙输入级预测完成（PASS，2026-10-10 12:18 UTC），EGL 未见渲染 110 张齐全 | `iteration002_controls`、`iteration002_bake/native_egl_unseen/native_unset` |
| P1 native_unset 50 对象图像域评分 | 已有：nonref PSNR 15.814 / disabled 11.923；src PSNR 22.483 / 15.736 | `iteration009/scores_disabled_native_unset.json` |
| P1 native_unset 烘焙未见视角评分 | **缺失**：`native_egl_unseen/native_unset` 无 `NATIVE_EGL_METRIC_EVALUATION.json`；稿件（正文 L120/L499/L642）仍写"输出不可得" | 本轮 P1 补齐 |
| P2 棕色化根因 | 未做系统性只读诊断 | 本轮 P2 执行 |
| P3 整合 | 待 P0 完成与 P1 评分后 | 本轮出预案 |

## 本轮任务

- **P0（监控+预案）**：只读监视四监督器状态；写评价预案（评分、统计、验收门），队列完成后按预案执行（本轮不抢跑 GPU）。
- **P1（评分补齐）**：对已渲染的 110 张 native_unset 未见视角图按既有协议评分（GT 对照取自 bake_matrix_v2 同一批渲染），全部输出写本文件夹；LPIPS 用 GPU 空隙或 CPU，不与生成队列争用。
- **P2（只读诊断）**：核对 Fresh C 推理栈——条件缓存绑定、参考图编码与颜色空间、checkpoint 加载键、`scale_image`/`unscale_image` 往返、CFG bare 分支交互；输出假设排序与可检验预测，不改代码。
- **P3（预案）**：写稿件整合分支计划（native_unset+P0 结果如何进入正文/补充/回复；何种结果触发何种叙事），不预写结论。

## 验收

- 每项任务有独立 JSON/MD 证据文件，SHA 记录输入来源。
- P1 评分与 bake_matrix_v2 既有 GT 指标可在对象层面交叉核对（同一渲染文件 SHA）。
- 不产生任何对 conservative_final 或 iteration012 的写入。
