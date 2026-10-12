# 固定GSO100对象 MV-Adapter 外部输入验证

原生相机参考视角1，其余5视角LPIPS，种子在对象内平均。差值候选−基线，LPIPS越低越好。

| 候选 | 基线 | 差值 | 点态95%区间 | Holm9 p |
|---|---|---:|---|---:|
| grid_projection | native | +0.012381 | [0.009785899413454657, 0.01520706228997248] | 4.49998e-05 |
| grid_projection | fixed_mean | +0.011581 | [0.00917005404762458, 0.014190310753113588] | 4.49998e-05 |
| grid_projection | late_high | +0.011667 | [0.009214706125839927, 0.014330678262220072] | 4.49998e-05 |
| view_projection | native | +0.014637 | [0.0119275363401665, 0.017557296475706] | 4.49998e-05 |
| view_projection | fixed_mean | +0.013836 | [0.011255203354971799, 0.01659550859147372] | 4.49998e-05 |
| view_projection | late_high | +0.013923 | [0.011297959581048539, 0.01674105552130689] | 4.49998e-05 |
| interaction_projection | native | +0.011174 | [0.008717418404746179, 0.013830374942564708] | 4.49998e-05 |
| interaction_projection | fixed_mean | +0.010374 | [0.008140788147443286, 0.012779675008597153] | 4.49998e-05 |
| interaction_projection | late_high | +0.010460 | [0.008221981104587515, 0.012887861459826426] | 4.49998e-05 |

Different input domain from Fresh C; scanned-color source textures, not certified albedo/PBR. No cross-backbone score pooling. APG not yet integrated on MVA; no APG superiority claim. No baking or accepted-paper probability claim.
