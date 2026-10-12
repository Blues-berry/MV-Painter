# r2 新旧证据裁决

| 证据 | 当前可支持的结论 | r2 处理 |
|---|---|---|
| Fresh C 300 对象，TCAS C3 对 Fixed Low | 原冻结 checkpoint、FG-PSNR 的配对差值；不复现历史 +0.96 dB | 主文沿用 r1，比较对象和评价域不变 |
| 历史 01549 +0.96 dB | 原 checkpoint、原 pooled full-image PSNR、原对象池 C3 对 Fixed High；含开发对象，缺配对行 | 主文只保留历史标记，不从别的队列补区间 |
| Round 10 几何分支，50 对象 | 相对关闭分支改善 LPIPS；完整 v29 在 LPIPS/SSIM 上更好 | 不并入 TCAS 结果：模型训练与干预不同，不能据此支持 TCAS |
| Round 11 双 GPU 计时，5 性能对象 | 像素一致输出下的单机计时成本差 | 不写成 TCAS 加速或整体系统优势；仅在内部审计保留 |
| Round 12 view-projection，64 对象×3 seed | 对开发队列之外、但历史 Fresh C 已暴露对象，两个冻结源视角主指标优于 native；非参考视角次要比较未证明非劣效 | 新增 Supplement S22；明确不同方法线、历史暴露和端点边界，不用于 Fresh C/TCAS 主张 |
| Round 12 APG，32 对象×3 seed | 开发集四项候选对 APG 非参考 LPIPS 比较均未校正显著 | S22 作为最近强基线；不称 APG 被击败 |
| Round 12 MV-Adapter，32 对象×3 seed | 原生相机底色 target 上三项候选对 native 的 all-six-view LPIPS 均未分离 | S22 作为独立接口开发证据；不与稿件中的 MV-Adapter N=50 时间调度比较合并 |
| MVDiffusion 75、旧 MV-Adapter 76/98 等分支 | 已有混合或负结果；统计身份与域限制已在 r1 补充材料处理 | 不重复合并、不把多个研究问题当独立复现；保留原分支记录 |
| GSO100、APG100、20 对象 bake 后台链 | 冻结点时尚无最终评分/报告；校准门通过不等于质量结果 | 不纳入 r2。后续完成后应另行审计、独立迭代 |

本轮只新增一条补充材料随访结果，没有改变 TCAS 的主结果、Fresh C 的 +0.522 dB 定义或历史 +0.96 dB 的处理。具体源文件、哈希、统计复核程序及后台状态快照见 `evidence/round012/`。
