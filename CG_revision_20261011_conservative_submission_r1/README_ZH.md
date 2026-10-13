# C&G 保守修订版 r1

这是从 [conservative_visuals](/4T/CXY/MV-Painter/CG_revision_20261011_conservative_visuals) 独立派生的提交候选。最终正文、补充材料、审稿回复和交付件均带 `conservative_submission_r1` 后缀；同目录中的 `delivery_conservative_visuals` 是继承的旧快照，不是本轮交付。

本轮围绕“实际问题—TCAS 控制—配对图像与偏好证据—烘焙及第二接口验证”重组正文。标题、TCAS 定义和 C3 历史身份保留。历史 +0.96 dB 只在主文出现一次，限定为原 checkpoint、C3 对 Fixed High、原 300 对象池的 pooled full-image PSNR；Fresh C 是另一 checkpoint、UID 队列和 foreground 指标下的配对结果。正文同时展示强固定/线性基线及等预算对照。

Fresh C Figure 8 从五个已核验署名的既有对象中，按完整六视角拼图和 view 0 上 C3 对 Fixed Low 的 FG-PSNR、FG-LPIPS、FG-SSIM 同向规则选出 Cube 01 与 E5-5-2。图中标为 Target 的低变化渲染、完整 view 0 和统一 ROI 只说明图像指标方向，不代表纹理保真；对象级指标仍来自 3×2 六视角整体评分。Figure 5 展示 300 个配对差值和具名比较。图源、哈希、裁剪和许可记录在 `manuscript/FIGURE_ASSET_PROVENANCE.md` 及 Supplement Table S1。

新增工作限于复算、元数据补全、重绘和排版：将已保存的 matched-budget 1,800 行按 UID 从已有 seed lookup 补齐 seed，并记录于 `evidence/SEED_COMPLETION_AUDIT_R1.json`；未新增模型输出、训练或调度搜索。图表数值和既有结果方向保持不变。

交付目录 `delivery_conservative_submission_r1/` 包含 clean、marked、Supplement、回复 PDF/DOCX/TeX、视频及可独立重建的 LaTeX 源码包。构建脚本位于 `manuscript/`，运行 `build_clean_conservative_submission_r1.sh`、`build_marked_conservative_submission_r1.sh` 和 `build_supplement_conservative_submission_r1.sh` 可重新生成相应论文 PDF。

`ROUND_EXECUTION_ZH.md` 和版本化 diff 记录本轮处置；`validate_submission_r1.py` 与 `VALIDATION_conservative_submission_r1.json` 记录版本边界、图表范围、许可、交付副本和源码重建检查。

仍待作者在投稿系统确认的边界包括：历史主 checkpoint 的直接复现区间、GeoTex unset-scale 默认输出、FAC 完整训练恢复、可验证接缝与 PBR/重光照质量，以及第二接口主比较的精度和跨架构解释。十对象烘焙仍是技术兼容样本，现有真实输出中保留明显外观差异；本文据此陈述相对指标，不将其写成纹理保真恢复。
