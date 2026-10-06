# 人工评测答卷格式与接收标准

**2026-10-06 执行更新：用户确认旧 LLH 包尚未分发。以下是旧冻结方案的
归档说明与 CSV 格式参考，当前不要分发其中 ZIP。最终主方法确定后将按
`1006/evidence/protocols/FINAL_METHOD_HUMAN_GLB_HANDOFF_20261006.md` 显式换版；
新刺激集、条件和分配冻结前不能开始收集。真实答案格式仍适用。**

状态：等待真实答卷；当前真实答卷为 0。此文件说明既定方案的执行，
不新增题目、剔除规则、比较对象或统计方法。权威锁定文件、参与者包和协调者文件
仍保存在仓库根目录下的 `final/round2/scientific_validation_v3/`，并未复制进
`1006` 候选包。以下路径均相对于仓库根目录；原匿名图片、分配文件和分析程序未修改。

- 冻结方案：`final/round2/scientific_validation_v3/HUMAN_STUDY_FINAL_PAIR_LOCK.md`
- 参与者压缩包：`final/round2/scientific_validation_v3/human_study_site/participant_handoff.zip`
- 空 CSV 表头：`final/round2/scientific_validation_v3/human_study_site/responses_template.csv`
- 24 行格式示例（不是数据）：
  `final/round2/scientific_validation_v3/continuation_20261006/RESPONSE_FORMAT_ONLY_NOT_DATA.csv`
- 40 个冻结名额：
  `final/round2/scientific_validation_v3/human_study_site/coordinator_private/collection_slots.csv`

## 发放前的两个前置检查

1. 参与者包包含冻结的 `visualization_24` 图像；其中 Panel 02 与 Panel 05
   对应的源模型授权目前未能核实（一个 API 许可字段为空，另一个源页面 404）。
   详见 `1006/evidence/audits/ASSET_SOURCE_LICENSE_RECHECK_20261006.md`。
   发放当前 ZIP 前先确认来源条款或取得许可；若不能确认，应先修订并重新冻结
   刺激集与分配，不能在收集后临时删对象。
2. 页面目前只记录 18 岁以上和自愿参与确认；本目录没有伦理审批/豁免记录。
   招募前请核实所在机构要求并保存相应记录。不要在收集开始后私自修改页面或题目。

## 交付什么

推荐使用已核验的参与者压缩包
`final/round2/scientific_validation_v3/human_study_site/participant_handoff.zip`。
参与者使用分配给自己的匿名 ID 完成网页评测并下载 CSV。
每人一个文件、24 行答卷；不要手工重新随机化、合并成总体投票比例，
也不要只交“LLH 赢了多少次”的汇总表。

协调者保存 40 个预先分配的名额，状态表位于
`final/round2/scientific_validation_v3/human_study_site/coordinator_private/collection_slots.csv`。
字段为 `participant_id,assignment_slot,status,response_file`。
初始状态为 `pending`，全部结束后改为：

- `returned`：已返回答卷，填写文件名，例如匿名 ID 加 `.csv`。
  该状态不预先表示答卷有效，有效性由锁定规则判定。
- `withdrawn`：退出或最终没有答卷，`response_file` 留空。
  如果有中途导出，保留在独立的私有归档中，不放入正式分析的 responses 文件夹。

答卷放在 `final/round2/scientific_validation_v3/human_study_site/coordinator_private/responses/`。
姓名、电话、邮箱、身份信息不进入答卷、论文或版本库。
名额表、真实答卷及解盲键只交给协调者，不能打包给参与者。

## CSV 参考格式

空表头为 `final/round2/scientific_validation_v3/human_study_site/responses_template.csv`。
格式示例位于
`final/round2/scientific_validation_v3/continuation_20261006/RESPONSE_FORMAT_ONLY_NOT_DATA.csv`：真实分配元数据对应的
24 行空答卷样式，所有答案留空，仅供格式参考。它不是证据，不能进入
responses 文件夹，也不能据此补填、代答或重构丢失的答案。

| 字段 | 要求 |
|---|---|
| participant_id | 冻结分配表中的匿名 ID；同一文件只允许一个 ID |
| assignment_slot | 对应的固定名额 1–40 |
| trial_order | 1–24，各出现一次，顺序与该人的冻结任务相符 |
| task_id | 冻结任务 ID，每人 24 个不重复任务 |
| left_image_id / right_image_id | 与冻结分配一致；不能交换后直接沿用 A/B 答案 |
| first_question | `appearance` 或 `texture`，与冻结题目顺序一致 |
| appearance_choice | `A`、`B` 或 `T`；A 为左图、B 为右图、T 为无明显差别 |
| texture_choice | 同上；两题各自保留答案 |
| attention_check_answer | 网页末尾理解检查的真实答案，整份文件一致；不要人工修正 |
| randomization_seed | 网页导出的冻结字符串；不是任意新种子 |

评测内容：appearance 判断参照外观、颜色和材质匹配；texture 判断纹理细节
自然程度及几何合理性。两题不能合并为一个“质量分”。
不要向参与者透露方法名、预期赢家、理解检查答案或现有实验结果。

## 有效答卷与停止标准

每人看 24 个对象，每个对象一次；四组比较各 6 个任务。
完成全部 40 个名额（返回或退出）后才能开展偏好分析。
至少 36 份完整有效答卷才满足现有人体证据的样本数量门槛。
不补名额，不因显著性提前停止，不根据偏好方向剔除人或对象。

整人剔除的既定理由为：24 项不完整、重复题目、缺失/非法选项、理解检查失败。
没有用时剔除。ID、左右图、随机种子等与冻结表不符时应停止并核查源文件；
不要自行修答案。重复 ID/名额是硬错误，不能择优保留一份。
少于 36 份有效答卷时保持 gate OPEN，报告实际样本和原因，不能把数据不足
转换为“无差异”或换人凑显著。新增研究如确有必要，应单独设计与登记。

## 统计方法与审稿意见

你提供的审稿意见肯定了 cluster-aware preference analysis，并明确要求
区分纹理变化与纹理保真、避免由跨零区间推导等效。
因此不能把 40×24 次判断或两个问题当作独立样本做普通二项检验。
同一人评价多个对象，同一对象也被多人评价，保留两种聚类结构。

沿用冻结方案：对四个比较 × 两个问题，共 8 个终点分别计算
LLH 偏好概率。先计算每个对象的偏好均值，再等权平均 24 个对象；
平局计 0.5。参与者和对象双向重采样，10,000 次 bootstrap，种子 20261005；
报告 95% 区间、相对 0.5 的双侧 bootstrap 检验、plus-one 修正、
8 终点 Holm 校正。原始 A/B/平局计数、方法胜负、对象曝光数、
排除人数和原因一并报告。不能只展示显著比较，不能合并两个问题。

95% 区间是逐终点区间，不能称为 8 个终点同时置信区间。
无显著差异不等于等效；本研究没有注册新的人工偏好等效界值。
bootstrap 是冻结的近似推断方法；小规模仿真检查也不能证明任何数据生成机制下
都校准正确。纹理分层结果只做描述，不再搜索“显著人群”。36–40 人是原定执行门槛，
不是针对任意微小差异的功效保证；不显著的精确度应由区间说明。

满足样本门槛只表示完成了该项评测，不要求 LLH 获胜。
负结果同样必须进入证据包，论文相应减少主张。

## 正式分析入口

使用新增的协调者入口，它先检查 40 个名额全部关闭、目录与名额表一致，
核验原分析程序哈希，按既定规则检查答卷，并要求至少 36 份有效答卷。
这些检查通过后才调用原程序，不改变其统计结果。

```sh
python final/round2/scientific_validation_v3/audit_scripts/run_closed_human_study.py \
  --slots final/round2/scientific_validation_v3/human_study_site/coordinator_private/collection_slots.csv
```

在项目根目录运行。不能绕过入口直接使用旧程序提前查看偏好结果。
结果会写入
`final/round2/scientific_validation_v3/human_study_site/coordinator_private/results/`。
保留原始答卷、排除记录、名额表与结果哈希，返回全部 8 个终点。

此评测仅覆盖固定 24 对象的二维图像偏好，且来自原 300 对象集合。
它不是 FRESH_CONFIRM_B 的新增独立确认，也不评价未见视角、UV 接缝、
全 PBR 材质或最终烘焙质量。人工结果不能替代 A3b 剂量共同支持证据。

2026-10-06：未招募、未分发、未填入或分析真实答案。该执行入口在真实答卷之前
加入，用于落实已存在的固定停止规则；原 participant ZIP 和分析程序哈希不变。
