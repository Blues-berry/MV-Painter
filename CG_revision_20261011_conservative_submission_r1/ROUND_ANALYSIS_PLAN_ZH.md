# 保守提交版 r1 分析与执行计划

本轮只在 `CG_revision_20261011_conservative_submission_r1` 内修改，从 `CG_revision_20261011_conservative_visuals` 独立派生。已经记录父目录完整文件快照；激进稿与此前保守副本保持原状。不新增生成、训练或参数搜索。

开始修改前先核对四项假设：

1. Fresh C 冻结指标对每个对象的 3×2 六视角拼图整体评分；逐视角数值仅用于图示核查。
2. 历史 +0.96 dB 是原 01549 主表 checkpoint 上 C3 对 Fixed High 的 pooled full-image PSNR；原 300 对象池含 24 个开发对象，存档不能重建配对区间。Fresh C 采用新冻结 checkpoint、UID-disjoint 队列及 foreground 指标。
3. 两个正向案例只从五个既有授权素材中筛选；筛选同时要求完整拼图和展示 view 0 的三项图像指标方向一致。图片不替代总体统计。
4. 有效第二接口证据是 MV-Adapter 原生 N=50；旧 N=7、N=98、N=76 和 MVDiffusion 记录须各自保留原身份。

执行顺序：

1. 重组主文主线，压缩重复的档案说明，把 checkpoint、队列、恢复与历史出处集中到 Supplement 和回复。
2. 在摘要和讨论突出训练时无需新增参数、原刺激偏好、Fresh C 对 Fixed Low 的配对结果及应用比较；强基线、指标差异和适用边界继续保留。
3. 对照 LaTeX 源码实际顺序修订图号、表号、许可行与审稿回复定位；核对图示指标范围、裁剪、来源哈希和作者署名。
4. 从既有 UID seed lookup 补齐 matched-budget 对象条件表缺少的 1,800 个 seed 字段，并留存 join 规则及前后哈希；不改任何指标数值。
5. 生成版本化 clean、marked、Supplement、回复及独立源码包；逐页检查 PDF 和引用，并从源码包隔离重建。
6. 检查视频完整解码、交付文件身份、父版本全目录哈希及其他受保护稿件哈希。
