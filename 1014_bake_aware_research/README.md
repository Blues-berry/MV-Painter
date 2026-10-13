# BAVGC 独立研究记录

**研究代号：** Bake-Aware View-Adaptive Geometry Control（BAVGC，暂定）  
**裁决：STOP（不进入 Phase C GPU 开发试验）**  
**研究目录：** `/4T/CXY/MV-Painter/1014_bake_aware_research/`

本支线检验：已知参考外观偏差和 UV 表面跨视角分歧，能否为六个生成视角的几何残差分配提供可靠、无需目标 GT 的反馈。现有离线结果给参考图偏差一个有限的对象级诊断信号，但 UV 分歧不能在对象内选择较好的未见视角 LPIPS 配置；两者合用反而较差。独立 worktree 中的张量接口合成测试通过，然而没有可信的“反馈信号 → 每视角控制动作”规则。因此接口通过不等于机制通过，按任务门槛停止。

## 文件导航

- [PRIOR_ART_AND_NOVELTY.md](PRIOR_ART_AND_NOVELTY.md)：先例对比和新颖性边界。
- [EXISTING_EVIDENCE_MATRIX.md](EXISTING_EVIDENCE_MATRIX.md)：相关工作树、冻结实验和可复用资产索引。
- [FEEDBACK_SIGNAL_AUDIT.md](FEEDBACK_SIGNAL_AUDIT.md)：Phase A 信号、统计单位、反例和限制。
- [INTERFACE_FEASIBILITY.md](INTERFACE_FEASIBILITY.md)：生成器接口、独立实现切片和合成测试结果。
- [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)：当前门槛、未执行的 GPU 协议和停止条件。
- [RESULTS_AND_FAILURES.md](RESULTS_AND_FAILURES.md)：实际结果与负结果汇总。
- [NOVELTY_VERDICT.md](NOVELTY_VERDICT.md)：是否构成新方法的判断。
- [FINAL_GO_NO_GO.md](FINAL_GO_NO_GO.md)：最终裁决。
- [SOURCE_AUDIT.json](SOURCE_AUDIT.json)：关键来源路径与内容哈希。
- [phase_a_signal_rows.csv](phase_a_signal_rows.csv) / [phase_a_signal_summary.json](phase_a_signal_summary.json)：可复核的对象级离线分析结果。
- [scripts/phase_a_signal_audit.py](scripts/phase_a_signal_audit.py)：Phase A 重算脚本；只读冻结输入，只写本目录。

## 复核入口

Phase A：

```bash
cd /4T/CXY/MV-Painter
python 1014_bake_aware_research/scripts/phase_a_signal_audit.py
```

Phase B 的代码切片保存在独立 worktree `/4T/tmp/MV-Painter-bavgc-phase-b`，分支 `codex/bavgc-phase-b-20261013`，未合并、未提交。合成接口测试曾以 11/11 通过：

```bash
cd /4T/tmp/MV-Painter-bavgc-phase-b
python -m unittest tests/test_bavgc_view_budget.py -v
```

这组测试只覆盖预算投影和 3×2 tile 映射，不执行扩散模型，也不验证反馈策略或纹理质量。

## 研究边界

未修改论文、冻结实验、历史 CSV、checkpoint 或评测协议。没有启动本支线的 GPU 任务，没有生成新的纹理，也没有执行 Phase C/D。主工作树中原有的修改和删除均保留；本支线只新增此目录。独立 worktree 中的实现仍是未提交的实验切片。
