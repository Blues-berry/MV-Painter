# R1 颜色保真：论文主张与回复证据

本文档是给回复信和修订说明准备的证据映射；没有编辑正式论文文件，也没有替换 Fig. 4 或 Fig. 6。

## 只读检查的论文版本

检查对象位于隔离的论文工作树 `/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/`：

| 文件 | SHA-256 |
|---|---|
| `final_0903.tex` | `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` |
| 原始 `fig4.pdf` | `0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620` |
| 原始 `fig6.pdf` | `585af2af647e9f169cb98320fb5779aaba158b3493ea054bea2ff8eef675546c` |
| 投稿 PDF `01549_submitted_manuscript_0907.pdf` | `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da` |

论文源文件、图和投稿 PDF 以上述 SHA 身份只读检查；本任务没有写入这些文件。

## 原文主张、现有证据与建议边界

| 原文位置 | 原文主张（摘要） | 本轮证据现状 | 回复/修订建议 |
|---|---|---|---|
| `final_0903.tex:270,275`，Fig. 4 | Fig. 4 是 26 对象中的局部纹理比较；增大 scale 会减少局部颜色变化和高频细节；较保守 scale 更保留局部纹理。原文已说明 Figure 4 不表示任何方法完全匹配 GT。 | 原始 `BASELINE_COMPARISON.pdf` 支持所选图中强干预与表面更平滑/局部变化减少的对照。26 对象 P1 RGB 复核另外发现 19/26 有可见细节损失；Fig. 4 两对象存在视觉色相差异。`COLOR_FAILURE_CASEBOOK.pdf` 的 No Adapter/GFL/LLH 是独立、unique6 的诊断 RGB，不应冒充原图 scale 消融。 | 保留其“局部纹理对照”的范围；caption 增加一句：颜色变化/纹理保留的视觉对照不等于跨对象绝对 RGB 色度准确度。不要据 Fig. 4 宣称颜色问题普遍解决。 |
| `final_0903.tex:322,327`，Fig. 6 | C3 在所示裁剪中比 `s=2.50` 保留更多局部颜色变化/材质纹理，并比保守 scale 有更强几何修正。 | 原始 `STAGE2_GATE_COMPARISON.pdf` 与 RGB 案例说明 C3/中等干预可保留更多局部信息，但 C3 类结果仍有对象级色相偏移；原 Fig. 4 两对象也在 GFL/LLH 条件下复现。现有证据支持定性权衡，不支持颜色真值保证。 | 保留“所示裁剪中的相对纹理权衡”表述；补充“定性比较，不代表所有视角都达到 GT 颜色保真，个别对象仍有 hue shift”。不换正式图。 |
| `final_0903.tex:544` | 26 对象 audit 中 92% 在 `s=2.50` 有纹理平坦化/高频细节损失。 | 原失败表对 26 个对象中 19 个记录可见细节损失；它是失败富集开发集的视觉复核，不能将当前 P1 的 GFL vs No Adapter 统计直接当成 `s=2.50` 的重测。 | 保留原来对应 scale 对照及 92% 的限定条件；在说明中标注对象级细节损失是独立于颜色准确度的证据。不要把 19/26 替换成 92%，两个条件和标签定义不同。 |
| `final_0903.tex:548` | 论文不主张所有生成结果都视觉接近 GT，也不主张 TCAS 是普适替代方案。 | 与 P1 结果一致；有色差均值改善，也存在两个原始 Fig. 4 对象的明显失败。 | 保留并具体化这一能力边界，区分“相对保留颜色变化/局部纹理”与“相对 GT 的色度准确度”。 |

## 必须分开的五项事实

1. **重复参考视角问题已修复。** 历史评估模式曾把一个参考 tile 重复使用；当前受控生成和指标表采用 6 个唯一 target view。修复的是评估协议，不是颜色生成器。
2. **所见颜色异常发生在烘焙之前。** `generate_with_schedule` 先从最终 latent 经 VAE 解码为 RGB，再由 observer 直接保存 PNG；这条 PNG 路径没有 UV 投影、纹理烘焙或 GLB 导出。代码在 `geotex/explore_contradiction.py:128–240, 375–390`。因此这些 RGB 已存在的偏差不能归因于后续烘焙。
3. **完整颜色生成根因尚未识别。** No Adapter 与 Adapter 均在同两例中出现视觉粉色/粉紫色偏；GFL 26 对象平均色差优于 No Adapter，但没有消除这两例。VAE GT 往返差异较小，削弱 VAE-only 解释，但不能排除生成 latent 的分布依赖。
4. **残差门控原型是负结果。** C3+feature-relative gate 相对 C3 的平均 CIEDE2000 增加 1.35；六个原 Fig. 4/6 对象增加 3.18，视觉复核没有看到明确粉色偏减轻。Linear+gate 虽优于 Generic Linear，仍比 GFL 高 3.30 CIEDE2000；不应写成已验证的颜色修复方法。
5. **真实能力边界是局部纹理权衡，不是色彩计量保真保证。** 在冻结 26 对象配对集中，GFL − No Adapter 的 CIEDE2000 平均差 −19.654 `[95% CI −26.370, −13.248]`，24/26 对象下降；同时，两例可见粉色偏保留，19/26 对象仍有细节损失。LLH 相对 GFL 平均 CIEDE2000 增加 3.583，且局部梯度/高频/颜色熵下降。

## 回复信可直接改用的事实性表述

> 感谢审稿人指出颜色保真边界。我们使用同一 checkpoint、对象级配对输入和六个唯一目标视角，对 26 个诊断对象的 No Adapter、GFL 与 LLH 输出重新比较。相对于 No Adapter，GFL 的平均前景 CIEDE2000 下降 19.65（95% 对象配对 bootstrap CI：−26.37 至 −13.25），26 个对象中有 24 个误差下降；但 Fig. 4 的两个原对象在 No Adapter、GFL 和 LLH 输出中仍可见色相偏移。LLH 相对 GFL 的平均 CIEDE2000 增加 3.58，且局部纹理梯度和高频能量下降。我们还确认这些 RGB 偏差已存在于烘焙前输出。GT 的 VAE encode–decode 隔离测试平均 CIEDE2000 为 4.09，方向与该 GFL 个例的粉色偏不同，因此目前没有证据将完整问题归因于 VAE。我们会将局部纹理变化的定性比较与绝对颜色保真区分，并明确指出对象级颜色根因仍未确定；不把负结果门控称为修复。

该文字只适用于颜色保真相关审稿意见；它报告当前诊断证据，不声称颜色问题已解决，也不把失败富集的 26 对象诊断集描述为新的独立确认实验。

## 候选 caption 建议（仅供论文 Agent 采纳，不写回源文件）

**Fig. 4 建议：**

> *Figure 4. Local texture comparison under different adapter scales. In the selected crops, increasing adapter strength can suppress local color variation and high-frequency detail. This qualitative comparison illustrates a texture trade-off and does not establish absolute colorimetric agreement with the ground-truth renders across objects.*

**Fig. 6 建议：**

> *Figure 6. Qualitative comparison between C3 and uniform adapter scaling. In the shown crops, C3 retains more local color variation and material texture than (s=2.50), while providing stronger geometric correction than (s=1.25). The comparison is qualitative; object-specific hue mismatch may remain and the figure does not imply colorimetric fidelity in every view.*

## 候选图像和身份链

- 正式 Fig. 4/6 未替换。
- `COLOR_FAILURE_CASEBOOK.pdf` 包含原始 GT、No Adapter、GFL、LLH、Python 3.13/3.10/archive 复现图、逐步去噪快照和 VAE mode/sample 输出；图像 PNG 像素原样嵌入，只有 PDF 显示尺寸变化。
- 可逐张复核的 PNG 放在 `evidence_rgb/`；对应源位置、对象 UID、checkpoint、runner、view IDs、mask SHA 和 PNG SHA 在 `COLOR_FIDELITY_PAIRED_RESULTS.csv`、`P0_OUTPUT_DIFFERENCE_TABLE.csv` 与 `SHA256SUMS.txt` 中。
- 原始比较 PDF 的摘要身份：`BASELINE_COMPARISON.pdf` SHA-256 `f7711f958877e5a0aa7ca310afafa928e480856d6b62de316b0c92fc95f2aa6f`；`STAGE2_GATE_COMPARISON.pdf` SHA-256 `29caf12c611c1a4b3b9c98757973955302e2b284f7dd540aaaeb25f4259355e5`；`VIEWMODE_ABLATION_COMPARISON.pdf` SHA-256 `9015d063b63fa2eb83b50f5257d7469dca43d654f47307a8232faa79eb2a12bc`。
