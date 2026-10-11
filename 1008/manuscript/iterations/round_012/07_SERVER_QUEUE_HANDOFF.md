# 服务器持久化实验与暂停交接

按作者要求，已将当前活进程树直接接入用户systemd scope `cg-round012-experiments.scope`，未中断或重启已有实验。核实四个队列主进程实际存在且属于该scope。用户Linger=yes，退出当前聊天或登录会话后仍可运行。独立监测服务`cg-round012-monitor.service`写入PERSISTENT_QUEUE_STATUS.json。

自动顺序：32对象三种子强原生/整图与逐视图投影 → 交互项候选96单元 → 真正第二骨干384单元及原生一致性门槛 → APG原生一致性探针。当前执行的是推理与评价；尚未确定的新训练不自动启动。各阶段校验冻结源与完整结果，失败保留并停止续接，不重复启动。

本链覆盖已冻结开发工作；主确认150对象、外部100对象与真实3D50对象仍需开发结果及有效性门槛后裁决。不能以后台运行替代方法胜出或论文完成。服务器重启不自动恢复；需人工检查最后完整对象及失败原因再制定续跑方案，避免重复/混合输出。

恢复目标后先读真实状态与输出，不仅依赖日志或旧PID。检查命令：

```bash
systemctl --user status cg-round012-experiments.scope cg-round012-monitor.service
cat /4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/iteration012_condition_interference/PERSISTENT_QUEUE_STATUS.json
```

用户已要求暂停目标等待实验完成。暂停只停止代理继续研究工作，服务器队列继续执行。第12轮及10–12综合总结尚未完成。后续需要全矩阵统计、APG质量对照、原生GSO光栅校准、逐轮论文/回复交付与风险分析。
