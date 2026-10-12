# P2 外观失败（棕色化）只读诊断报告

日期：2026-10-11。全部为只读核对与统计，无代码/权重/输出改动，无新 GPU 生成。

## 一、排除项（推理栈完整性核对）

| 核对项 | 结论 | 依据 |
|---|---|---|
| VAE 编解码往返 | **一致** | 训练端 target 编码 `(x−0.5)/0.8 → ×scaling → scale_latents`（[model_unet_geotex.py L678-684](file:///4T/CXY/MV-Painter/MVPainter/mvpainter/model_unet_geotex.py#L678-L684)）与推理端解码 `unscale_latents → ÷scaling → vae.decode → 0.8x+0.5`（[mvpainter_pipeline.py L712-718](file:///4T/CXY/MV-Painter/MVPainter/mvpainter/mvpainter_pipeline.py#L712-L718)）互为代数逆 |
| 参考条件潜码路径 | **一致** | 训练 `encode_condition_image` 与推理 `encode_image` 同为 `feature_extractor_vae → vae.encode`，均不乘 scaling |
| CFG 负参考分支 | **一致** | 训练 drop 分支（p=0.1）编码全零图（L735-753）＝推理 `negative_lat`（L621） |
| checkpoint 加载 | **此前已审计 PASS** | iteration009 `CONTROLNET_ASSET_AUDIT`：键集全等、SHA 校验；iteration012 worker 载入前再校验 |
| 参考图预处理死代码 | 记录（无已证影响） | [mvpainter_pipeline.py L614-615](file:///4T/CXY/MV-Painter/MVPainter/mvpainter/mvpainter_pipeline.py#L614-L615)：`recenter_img` 结果被下一行覆盖，Fresh C 路径实际未执行 recenter/white_out；Fresh C source 已预对齐，未证明有影响 |
| RGBA 白底合成 | 次要候选 | `to_rgb_image` 不做预乘，半透明边缘留轻微暗晕；不能解释主失效模式 |

## 二、决定性只读证据

**1. 几何-参考干涉观测**（[full_v29_development_attempt01/INTERACTION_ROWS.json](file:///4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/iteration012_condition_interference/full_v29_development_attempt01/INTERACTION_ROWS.json)，未改动轨迹的 2 对象 × 3 步观察）：
- **6/6 步** whole-grid 受控噪声与参考外观方向负点积；cosine 均值 **−0.585**（−0.759 至 −0.417）
- 反向平行能量占比均值 **36.2%**
- 含义：几何控制残差在每个观测步**系统性对抗**参考外观信号

**2. 训练分布色调**（2,007 训练对象抽样 185 张有效前景渲染）：
- 前景均值 RGB **(0.474, 0.439, 0.430)**；**34.6%** 物体暖棕主导（R>G>B 且 R−B>0.04）
- 含义：模型先验本身偏向暗暖棕色

**3. 输出向先验收敛**（10 个烘焙对象 view0，生成 vs 参考前景色调）：
- 生成 **7/10** 暖棕主导，参考仅 **4/10**
- 参考从近中性（0.27 灰）到强暖（0.51/0.38/0.24）不等，生成全部收敛到 **0.84–0.93 亮暖灰带**
- 含义：不论参考什么颜色，输出回归训练色调先验——参考条件被部分覆盖

## 三、因果图景（假设排序）

**H1（主假设）：几何-参考干涉 → 先验回归。** 几何残差通路与参考外观方向负干涉（~36% 反向能量）削弱参考条件，使模型落回暗暖训练先验（棕色重复纹理）。adapter scale 调度只调节干涉幅度——解释了六条件全部棕色化且指标接近；也解释 `native_unset`（raw correction）不消除失效（烘焙未见 PSNR 11.14 vs GT 22.38）。

支持链：6/6 负 cosine 观测 + 训练先验暖偏 + 输出收敛 + seed42 view_projection（移除对抗分量）source 视角 +2.92 dB（方向与 H1 预测一致）。

**H2（次要）**：边缘暗晕/白底合成——幅度小。**已排除**：VAE 空间、cond_lat 路径、CFG 负分支、checkpoint 加载。

## 四、可证伪预测

1. 若 H1 成立：iteration012 的投影条件应跨种子改善 source 视角参考贴合（完成即直接检验）。
2. 若 H1 不成立：投影条件在冻结开发协议上不与 native 分离。

## 五、稿件建议

- 冻结输出不改；失效按原样保留并缩小适用结论（与独立审查一致）。
- Discussion 可加一句机制性表述：跨对象棕色失效与"系统性几何-参考干涉 + 暖偏训练先验"一致，而非投影/烘焙伪影（source/GT bake 保留参考外观）。
- 引用边界：干涉观测是 6 行开发观察；色调统计是只读分布证据；只允许 "consistent with" 措辞，不作因果断言。

详细数字见 [P2_DIAGNOSIS_EVIDENCE.json](file:///4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p2_appearance_diagnosis/P2_DIAGNOSIS_EVIDENCE.json)。
