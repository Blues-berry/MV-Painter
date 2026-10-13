# MV-Adapter GSO100最近APG强基线比较

100对象、3种子，参考视角1不纳入主要LPIPS；对象为重采样单位。差值候选−APG，越低越好。

| 候选 | APG | LPIPS差 | 点态95%区间 | Holm6 p |
|---|---|---:|---|---:|
| grid_projection | apg_projection_only | +0.009113 | [0.006270826170795288, 0.011996712444668324] | 2.99999e-05 |
| grid_projection | apg_paper_sd21_at_native_cfg | +0.008553 | [0.005027113883942367, 0.011898217868416881] | 2.99999e-05 |
| view_projection | apg_projection_only | +0.011369 | [0.00846624664472571, 0.014357046254584569] | 2.99999e-05 |
| view_projection | apg_paper_sd21_at_native_cfg | +0.010809 | [0.00725528837518456, 0.014266035686790319] | 2.99999e-05 |
| interaction_projection | apg_projection_only | +0.007906 | [0.0051834736334548034, 0.010647478323748022] | 2.99999e-05 |
| interaction_projection | apg_paper_sd21_at_native_cfg | +0.007347 | [0.003934984544323135, 0.010590038117843988] | 2.99999e-05 |

Existing APG, not new method. Paper preset at native CFG3 vs original paper CFG10. Source-selected convenience100; scanned colors not certified physical albedo. Baseline protocol frozen before APG outputs; not jointly preregistered with earlier candidate generation. All outcomes retained, no across-interface pooling.
