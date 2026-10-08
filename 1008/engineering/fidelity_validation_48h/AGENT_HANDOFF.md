# 48 小时任务交接

- 当前分支：`codex/r1-fidelity-validation-48h-20261008`
- 当前 HEAD：基线 `7311b9446733637e0f0a8e85211cd7fc02c67810`；Phase A–E 证据整理已完成，最终 SHA 清单、限定目录提交和远端核验待执行。
- 当前阶段：最终审计与 Git 交付。所有新工作只在 `1008/engineering/fidelity_validation_48h/`；不得触碰论文工作树、原始 TeX/Fig. 4/6、上一轮冻结目录或无关未跟踪的原始 run/RGB。
- GPU 队列：无任务。本专项复用冻结 RGB 和 CPU 指标复核，没有启动 GPU 推理；GPU 时间为 0。
- 新产物目录：`1008/engineering/fidelity_validation_48h/`。
- 上一轮冻结证据不可修改。
- 论文工作树只读，不在其中创建或编辑文件。
- 已生成配对结果：`A_COHORT_HETEROGENEITY.csv`、`B_OBJECT_LEVEL_RESULTS.csv`、`DIAGNOSTIC26_REANALYSIS.csv`、`C_CAUSAL_PROBE_RESULTS.csv`。
- 已生成审计脚本和输入核验：`summarize_fidelity_cohorts.py`、`audit_cohort_input_pair_identity.py`、`audit_freshc_appearance_condition.py`、`recompute_freshc_noadapter_probe.py`；GPU 无运行进程。
- 恢复时先读 `48H_PROGRESS.md`、`INITIAL_STATE.json` 和本文件；不得重算已验证的 RGB 指标或改动 frozen `color_failure` 与论文工作树。
- 最终裁决见 `FINAL_READINESS_VERDICT.md`；推送后在此记录远端 commit SHA。
