# APG开发强基线比较

差值为候选−APG；LPIPS越低越好。对象为重采样单位，3种子先在对象内平均。以下四项作Holm校正；属于开发集比较。

| 候选 | 基线 | 非参考视角LPIPS差 | 95%点态区间 | Holm p |
|---|---|---:|---|---:|
| view_projection | apg_projection_only | +0.000800 | [-0.002458959200387956, 0.004298526731193605] | 1 |
| view_projection | apg_paper_sdxl_parameters_at_native_cfg | -0.000462 | [-0.004353541200495481, 0.0034822463255598677] | 1 |
| interaction_projection | apg_projection_only | -0.002070 | [-0.005350705832497625, 0.0012590199646850416] | 0.725096 |
| interaction_projection | apg_paper_sdxl_parameters_at_native_cfg | -0.003331 | [-0.007564715737935334, 0.0005926498484768667] | 0.509957 |

下一阶段门槛：MV-Adapter相机/掩码/材质语义校准、真实GT自烘焙路径校准尚未通过，不自动扩大未校准数据。保留已有MVDiffusion负结果；无全面稳定优势或90%中稿概率声明。
