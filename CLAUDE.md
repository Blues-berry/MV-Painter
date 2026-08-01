# MV-Painter 项目

## 项目现状（TCAS）

当前项目重点是 **TCAS（Timestep-Conditioned Adapter Scaling）**：基于 MV-Painter 多视图扩散管线 + GeoTex-Adapter，研究适配器在去噪各阶段注入强度的调度，以平衡几何对齐与纹理保留。

- 论文: `final/final.tex`（实验章节见 Sections 4.2–4.6，revision 补充见 `final/revision_supplement_0707.md`）
- 训练脚本: `geotex/train_v2.py`（config: `MVPainter/configs/mvpainter-geotex-v2-train.yaml`）
- 评估脚本: `geotex/eval_unified_300.py`（300-obj）、`geotex/eval_schedule_comparison.py`（schedule 对比，24-obj probe）、`geotex/eval_clipiqa.py`（感知质量）
- TCAS 调度: `geotex/tcas_schedule.py`（C3 三段式 + TCAS-V2 5阶段逐层）
- Live checkpoint: `mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt`
- 基础模型: `checkpoints/hf_repo`，数据: `data/train_data/rendered_full`
- 旧产物（PBR/LoRA/GeoTex v1）已隔离到 `archive2.0/`

## 图片处理规则（重要）

主模型 **不支持视觉**。读取图片时必须通过 Agent 工具委派给 `image-reader` 智能体，并**显式指定 `model: "opus"`**：

```
Agent(subagent_type="image-reader", model="opus", prompt="请读取并描述 /path/to/image.png")
```

关键：必须传 `model="opus"` 参数，否则智能体会继承主模型导致报错。

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

### 是否需要修正：是/否
```

### 执行原则

- **不跳过评估**：即使是小改动也要进行评估
- **迭代修正**：如有重大问题，修正后需再次评估
- **记录决策**：评估过程和决策理由应记录在相关文件或 memory 中
