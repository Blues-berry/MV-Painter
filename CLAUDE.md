# MV-Painter 项目

## 图片处理规则（重要）

主模型 `sonnet`（mimo-v2.5-pro）**不支持视觉**。读取图片时必须通过 Agent 工具委派给 `image-reader` 智能体，并**显式指定 `model: "opus"`**：

```
Agent(subagent_type="image-reader", model="opus", prompt="请读取并描述 /path/to/image.png")
```

关键：必须传 `model="opus"` 参数，否则智能体会继承主模型的 mimo-v2.5-pro 导致报错。

**禁止**使用 Python 脚本通过 `localhost:8000` 连接本地模型服务，该服务未运行。

## 代码编辑反馈评估流程（重要）

任何代码编辑完成后，必须执行以下反馈评估流程：

### 评估流程

1. **代码编辑完成** → 输出修改内容摘要
2. **双角色评估**：
   - **论文专家视角**：评估修改是否符合论文目标、实验设计是否合理、结果是否可复现
   - **代码专家视角**：评估代码质量、潜在 bug、性能问题、边界情况处理
3. **反馈整合**：将两位专家的意见整合为结构化反馈
4. **修正迭代**：根据反馈意见修正代码，直到两位专家均无重大问题

### 评估输出格式

```
## 代码反馈评估

### 论文专家意见
- [ ] 实验设计合理性：...
- [ ] 结果可复现性：...
- [ ] 论文目标一致性：...

### 代码专家意见
- [ ] 代码质量：...
- [ ] 潜在问题：...
- [ ] 性能优化：...

### 修正建议
1. ...
2. ...

### 是否需要修正：是/否
```

### 执行原则

- **不跳过评估**：即使是小改动也要进行评估
- **迭代修正**：如有重大问题，修正后需再次评估
- **记录决策**：评估过程和决策理由应记录在相关文件或 memory 中

---

## 论文迭代工作流

### 使用 /goal 推进论文计划

论文完整计划见 memory `lora-paper-master-plan.md`。每次会话的使用流程：

1. **查看进度**：读取 memory 中的进度表，找到下一个 ⬜ 待开始的 Task
2. **设置 goal**：用 `/goal` 设置当前 Task 的完成条件
3. **执行**：Claude 会持续工作直到条件满足
4. **更新进度**：完成后更新 memory 进度表为 ✅

### /goal 条件编写规范

goal 条件必须是**可验证的文件存在性**，不能是模糊描述。模板：

```
/goal 文件 mvpoutput/paper_assets/eval_reference_consistency.md 已存在且包含 Original/Crashed/Working 三路的 CLIP Sim 和 DINO Cos 数据
```

```
/goal 文件 mvpoutput/paper_assets/paper_main_figure_v2.png 已存在且宽度 >= 3000px
```

```
/goal 文件 mvpoutput/paper_draft/abstract_intro.md 已存在且包含完整的 Abstract 和 Introduction
```

### Task 1A 专用 goal（当前最高优先级）

```
/goal 文件 mvpoutput/paper_assets/eval_reference_consistency.md 已存在，包含 10 个测试对象的 Original/Crashed/Working 三路 CLIP Sim 和 DINO Cos 均值汇总表
```

### 并行任务说明

Phase 4（Wonder3D 搜索）可与 Phase 1 并行，无需单独设置 goal，在执行 Task 1A 时顺便搜索即可。
