# TCAS Demo 配音稿（Narrated Demo Script）

> 13 页与 `TCAS_Demo_fixed.pptx` 一一对应；术语与修订稿完全统一（evaluation pool / no further search / 58.1% cluster bootstrap / TCAS sole method）。
> 声音：`en-US-AndrewNeural`；每页画面时长 = 配音时长 + 1.0 s 过渡缓冲。

| # | 幻灯片 | 配音文本（英文，实际合成用） | 中文大意 |
|---|---|---|---|
| 1 | 标题页 | Adapter Scaling Trade-off and Timestep-Conditioned Scheduling in Multi-view Diffusion Texture Generation. This video introduces TCAS — a training-free, plug-and-play inference schedule for geometry-conditioned multi-view diffusion. | 介绍论文与 TCAS 定位：免训练、即插即用 |
| 2 | Method overview | In geometry-conditioned texturing pipelines, the adapter scale controls how strongly normals, depth, and masks steer the denoising process. TCAS applies a conservative scale in the early and late stages, and concentrates strong geometric correction in the middle third — a low–high–low schedule, denoted C3, with scales 1.25, 2.50, and 1.25. | 方法：三段式低-高-低调度 C3 |
| 3 | Uniform sweep | A thirteen-point uniform sweep shows the trade-off: as the scale grows, structural similarity keeps improving, while texture diagnostics and perceptual quality degrade. | 13 尺度扫描呈现 trade-off |
| 4 | Per-object | The behavior holds across objects: higher scales buy structure but flatten surface appearance. | 逐对象一致 |
| 5 | Texture audit | In a twenty-six object audit, ninety-two percent of objects show texture flattening under aggressive scaling — evidence that the conflict is systematic, not anecdotal. | 26 对象审计 92% 压平 |
| 6 | Diagnostics | The key evidence is not a single proxy metric, but the agreement among RGB standard deviation, gradient magnitude, Laplacian variance, and local visual inspection. | 多诊断指标互相印证 |
| 7 | 17 variants | Seventeen uniform, layer-wise, and temporal variants are compared on a twenty-four object probe set. The low–high–low schedule C3 offers the best shape–texture balance, and the schedule is then frozen. | 17 变体 24 对象 probe 选出 C3 后冻结 |
| 8 | Qualitative | Qualitatively, C3 keeps stronger geometry than conservative scaling, and preserves more local texture variation than aggressive scaling. | 定性对比 |
| 9 | Generic schedules | Generic monotonic decay or warm-up rules cannot reproduce this: the benefit comes from concentrating the high scale in the middle denoising stage, not from merely varying the strength. | 单调 decay/warm-up 无法替代 |
| 10 | Large-scale | The frozen schedule is transferred unchanged to a three-hundred-object evaluation pool — twenty-four probe plus two-hundred-seventy-six held-out objects — with no further search. C3 improves PSNR by zero point nine six decibels over aggressive scaling with comparable structure, and on the disjoint holdout it outperforms trapezoid, Gaussian-peak, linear warm-up, and cosine-bump schedules. | 300 池（24+276）无再搜索迁移；+0.96 dB；276 holdout 胜 4 类调度 |
| 11 | Perceptual | A blinded three-alternative preference study supports this: C3 receives the highest overall-quality share, fifty-eight point one percent, significant under a participant-and-object cluster bootstrap. | 盲评 58.1%，cluster bootstrap 显著 |
| 12 | FAC | A controlled re-examination of the learned FAC extension shows that, under a strictly paired protocol with a disjoint training pool, no learned configuration outperforms the training-free schedule. TCAS therefore remains the main and sole method. | FAC 受控复检为负；TCAS 唯一主方法 |
| 13 | 结束 | Thanks for watching. Checkpoints and evaluation code are available upon reasonable request. | 致谢 + 可得性声明 |
