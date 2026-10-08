# 最终裁决

日期：2026-10-08

```text
COLOR_ROOT_CAUSE_IDENTIFIED = PARTIAL
COLOR_FIX_VALIDATED = NO
REPRODUCIBILITY_CLOSED = YES
R1_FIDELITY_EVIDENCE_READY = YES
```

## 裁决依据

- **COLOR_ROOT_CAUSE_IDENTIFIED = PARTIAL**：已确认此前 Fresh C 跨运行栈图像不一致的可重复原因族，并在 FP16 初始 latent 乘 scheduler sigma 处定位第一个数值变化；已把颜色异常定位到烘焙前生成 RGB，并在一个 Fig. 4 对象的后段去噪快照中观察到粉红表面。完整颜色生成根因仍未确定，不能归因于 VAE、Adapter 或残差门控中的某一个。
- **COLOR_FIX_VALIDATED = NO**：P1 没有产生稳定且有明确因果依据的颜色修复点。GFL 的平均色差优于 No Adapter，但两例可见偏色保留；LLH 的主要作用是压低细节；VAE 往返不复现同方向、同量级偏色；既有 feature-relative gate 为负结果。故没有启动 P2 新修复实验，也没有将任何条件称为已验证修复。
- **REPRODUCIBILITY_CLOSED = YES**：三个预先锁定代表对象的 P3.13 完整重复逐张量相同且逐像素复现 archive；P3.10 完整追踪逐像素复现此前 observer 身份；跨栈首个数值变化位置已量化。此“关闭”限于解释输出身份分叉和三例逐层追踪，不表示 120 个对象都完成逐张量复核，也不表示不同栈的 RGB/指标可以互换。
- **R1_FIDELITY_EVIDENCE_READY = YES**：已提供对象级 26 对象配对效果量和不确定性、P0 首差异表、VAE 隔离、去噪阶段 RGB、可核验原始 PNG 与 casebook，以及论文原文主张映射和不改正式 Fig. 4/6 的 caption/回复建议。根因未决与能力边界均有明确披露。

## 停止规则与提交边界

没有证据支持继续 Gate / Scale / timestep 搜索。当前交付保留失败和不确定性，不把负结果包装成新方法贡献。完整高体积 tensor trace 和未入选的原始运行图像留在隔离工作树并在 `SHA256SUMS.txt` 记录身份；提交轻量 trace 摘要、源脚本、配对表、选定原始 PNG 和 PDF casebook。正式论文工作树保持未修改。

下一步如要进行新的颜色方法试验，必须先有可操纵的、能解释已观测偏差的具体生成环节；本报告不授权把现有诊断性关联当成干预证据。
