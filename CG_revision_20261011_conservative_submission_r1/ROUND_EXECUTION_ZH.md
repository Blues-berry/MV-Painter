# 保守提交版 r1 执行记录

本轮只在 `CG_revision_20261011_conservative_submission_r1` 内执行；父版 `conservative_visuals` 和激进稿均保持不变。开始时以 194 个父目录文件的 SHA-256 清单建立校验基线。修改不包含新模型输出、训练、调度参数搜索或重跑实验。

## 论文与证据链

- 正文按实际纹理问题、TCAS 控制、定量及偏好结果、烘焙和第二接口验证重排；保留标题、TCAS 定义与 C3 历史身份，压缩主文中的档案过程说明。
- 主文中的历史 +0.96 dB 只出现一次，明确限定为 01549 原 checkpoint、C3 对 Fixed High、原 300 对象池的 pooled full-image PSNR；开发对象重叠和缺少配对明细所造成的区间限制写清。Fresh C 的 +0.522 dB 单独对应新 checkpoint、独立 UID 队列、C3 对 Fixed Low 的配对 foreground FG-PSNR，不称作历史复现。
- 强固定尺度、Generic Linear 和等预算对照继续列在主文；图 5 给出全部 300 个配对差值及具名点估计/区间，并将同队列后续比较与主要验证分开标记。
- Figure 8 仅从五个已授权的既有候选中选择，同时满足对象级六视角拼图和展示 view 0 上 C3 对 Fixed Low 的三项指标同向改善。图中将低变化输入标为 Target，并在图注明确该案例说明图像指标方向、不表示纹理保真；完整队列结论仍由表 4 和图 5 支持。图源、ROI、哈希、许可和量化复算均保留。
- 主文以有效 native MV-Adapter N=50 检验为第二接口结果；较早 N=7、N=98、N=76 等探索结果各自留在 Supplement，没有混为确认集。历史偏好、Fresh C、烘焙与 MV-Adapter 的评价对象和端点分别表述。
- 从已有 UID seed lookup 给 matched-budget 六条件表补齐 1,800 行 seed 元数据；复核每对象六条件 seed 一致，指标列逐字不变。其余不同来源的 50 条空 seed 记录继续保留，不做推断填补。

## 成品与验证

- 已生成版本化 clean、marked、Supplement、回复 PDF/TeX/DOCX、视频和独立 LaTeX 源码包。最终页数分别是 15、16、36、4；回复 PDF 标题与文件名均指向 `conservative_submission_r1`。
- 已保存相对 `conservative_visuals` 与认证 01549 源稿的版本化 diff，便于审阅本轮正文、补充材料和回复变化。
- 从源码 ZIP 临时解压后，独立重建 clean、marked、Supplement 和回复。71 页逐页渲染与交付 PDF 的文字、版面和 72 dpi 页面图像完全一致；源码 ZIP CRC 检查通过。
- 主文、补充材料和回复编译均无未定义引用或编译错误；检查了图 5–10、补充前两页、回复页与许可表。Figure 8 图注已补充评价域与纹理保真边界。
- 视频完整解码通过：H.264，2304×346，24 fps，22 秒。
- 194 个父目录文件的清单和哈希均相同；`PROTECTED_MANUSCRIPTS.json` 中所有受保护源文件哈希均相同。

## 留存的证据边界

R2.1 仍是最大风险：时层调度已有先例，现有结果支持的是 GeoTex 任务中的可执行控制和受控实证，不支持通用新调度法。Fresh C 不复现原 checkpoint 的 +0.96 dB；烘焙样本是兼容性筛选的十对象小样本，生成烘焙仍有可见差异；默认 unset-scale GeoTex、验证过的 seam 指标、PBR/重光照与 FAC 完整训练恢复仍缺。MV-Adapter 的冻结主比较区间包括零。因此本轮提高的是论文主线、证据对应和交付可审计性，不能把未完成的实验缺口写成已解决。
