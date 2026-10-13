# C&G 保守修订版 r2

这是从 [保守修订版 r1](/4T/CXY/MV-Painter/CG_revision_20261011_conservative_submission_r1) 独立派生的第二版。创建时对 r1 的 285 个源文件逐项 SHA-256 校验一致；本轮只在 r2 目录内修改。r1、01549 原稿和独立实验分支均保留。

r2 保留 TCAS/C3 主文身份与 r1 的图表、主要统计及 Fresh C 定义。新增内容集中于补充材料 S22 和 R2.1 回复：对 Round 12 的逐视图 guidance projection 随访做独立复核，并明确它不是 TCAS/C3 复现，也不证明非参考视角非劣效、APG 优势或跨骨干泛化。源视角主结果来自 64 个对象、3 个种子和 768 条对象—条件—种子记录；该队列虽排除了单独的 32 对象方法开发集，但曾进入历史 Fresh C 研究，故不称为完全未暴露队列。

历史 +0.96 dB 仍只表示 01549 原 checkpoint、原对象池、C3 对 Fixed High 的 pooled full-image PSNR；Fresh C 的 +0.522 dB 是另一 checkpoint、另一配对队列、C3 对 Fixed Low 的前景 FG-PSNR。两者在正文、图表和回复中保持分开。

`delivery_conservative_submission_r2/` 是本轮交付目录，包含 clean、marked、Supplement、回复信、视频与独立源码包。证据处置见 [EVIDENCE_DISPOSITION_R2_ZH.md](EVIDENCE_DISPOSITION_R2_ZH.md)，图文核查见 [R2_VISUAL_AUDIT_ZH.md](R2_VISUAL_AUDIT_ZH.md)，执行记录与风险判断见版本化说明文档。Round 12 的复算程序可以从现存对象图像重新核对文件哈希与 RGB 像素哈希；源码包包含所有评分行、身份清单、配置、评估脚本和该复算器，但不重复封装 768 张模型输出图。

GSO100 对照、APG 扩展和烘焙闭环在 14:02 的快照中仍在运行或等待；14:22 再核时状态未变，没有已完成评分或报告进入本稿，也未触碰这些后台任务。
