# 第二轮执行记录（进行中）

原生wrapper控制生成已完成：10对象×3条件；capped1.0全部与前一轮预测RGB逐像素一致，输入和种子一致；native_unset每次实际wrapper调用均检查尺度属性缺失。NoAdapter独立保留。

证据：实验目录revision_expansion_20261010/ITERATION002_CONTROL_EXTENSION.json与iteration002_controls。保持50步冻结采样，不能把该控制称为官方75步完整默认pipeline。

新增20次真实原UV烘焙正在运行。此前GT+七条件80记录不覆盖；新增两条件共享相机、掩码、纹理分辨率和补洞规则。分析会先验证原几何身份及GT覆盖率一致，再评价220个未见视角。

执行入口：run_geotex_native_unset_controls.py → prepare_round002_native_control_handoff.py → bake_fresh_c_native_uv.py（两个新条件）→ evaluate_round002_native_controls.py。

统计规则未改：已看过的同十对象，事后探索；三个具名差异×五端点=15项Holm校正；旧确认性Late−Mean主要比较不替换。当前尚无新增烘焙结论，稿件尚未完成整合与验收。

下一轮工作按../PRIORITY_POLICY.md裁决；开发新算法不属于必须执行事项。
