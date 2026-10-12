# P3 稿件整合预案（待 P0 完成后执行）

原则：在保守_final 之上做第 003 轮增量迭代（新建独立目录，不改任何既有交付）；叙事由结果分支决定，不预写结论。

## 已可锁定的整合内容（不依赖 P0）

### 1. native_unset 默认对照闭合 R1.1（P1 结果，证据等级：探索性技术队列）

- 正文 L120：`its generated outputs are not available here (Supplementary Section S20)` → 改为已提供；引用新补充小节（建议 S22）。
- 正文 L499：`No generated output for that unmodified path is available in this comparison, so the corresponding reviewer request remains partially unresolved.` → 改为已提供 native_unset 10 对象烘焙未见视角对照，结果不优于任何显式 scale 条件；R1.1 该子项从 PARTIAL 升级为 ADDRESSED（默认对照部分）。
- 正文 L642 Limitations 同步更新：删除"true unset-scale GeoTex output absent"，保留 seams/PBR 未验证。
- 回复信 R1.1：新增完成度行（unset 对照已补，10 对象探索性，方向不利于"默认即更好"假设）。
- 补充新增 S22：聚合视图构建、派生关系、配对对比表（从 P1 JSON 转录）。
- 措辞红线：10 对象探索性；不与 50 对象图像域结果合并叙事；不引入"非劣效"。

### 2. 棕色化机制表述（P2 结果，证据等级：只读分布+6 行开发观察）

- Discussion 增加一段：跨对象棕色失效与 H1（几何-参考干涉 + 暖偏训练先验）一致；source/GT bake 保留参考外观排除烘焙伪影；引用 P2 证据 JSON 数字（6/6 负 cosine、34.6% 训练暖棕、7/10 输出暖棕收敛）。
- 措辞红线：仅 "consistent with"；干涉观察为开发观察样本；不做因果断言；不改动任何冻结图表。

### 3. iteration012（P0 完成后按分支二选一）

**分支 A（interaction/view projection 跨 3 种子 source 视角改善且未见视角不显著变差）**
- 贡献叙事升级：TCAS 调度 + 干涉管理投影统一为"推理时几何-参考干涉管理"框架；TCAS 是幅度调度，投影是方向修正，共享同一干涉观测基础。
- R2.1 回复重写核心段：从"实证系统研究"升级为"受控发现（干涉的系统性反向）+ 最小机制干预（PCGrad 式投影移植，明确署名来源）+ 跨骨干复验（MV-Adapter 方向一致性）"。
- 主文新增 1 图（source 视角跨种子效应）+ 1 表（配对对比）；Supplement 收开发细节。
- 若 MV-Adapter 同向：加"接口方向一致"一段（分集，不池化）。

**分支 B（无分离或方向不一致）**
- 维持实证定位；iteration012 作为探索性负/中性结果进入 S21 扩展或 Limitations（干涉可测、投影未产生稳定收益）。
- R2.1 维持现有回复 + 补一句"已尝试最小机制干预，未产生稳定收益"（诚实负结果，增强 R1.5 透明度叙事的一致性）。

### 4. 版本与验证

- 新目录名建议 `CG_revision_20261012_p0p3_integration`（若当日执行）。
- 继承验证链：全表格值/图资产一致性 diff、clean/marked/supplement/response 四编译、REVIEWER_TO_MANUSCRIPT_TRACEABILITY 更新（R1.1 行、R2.1 行按分支改写）。
- 投稿 zip 排除本增量文件夹的内部备忘。

## 当前状态

- [x] P1 证据锁定（native_unset 烘焙对照）
- [x] P2 证据锁定（只读诊断）
- [ ] P0 队列完成 → 评价 → 选分支
- [ ] 执行整合（新目录、独立编译与验证）
