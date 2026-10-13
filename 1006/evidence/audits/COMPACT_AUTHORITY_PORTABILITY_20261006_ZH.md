# 紧凑证据 authority 的独立检出修复

发布目录检查发现：76 项 authority source 中，20 项仍使用本机 `final/`
路径。它们并非全部缺失：12 项在 1006 已有字节相同的副本，8 项需要补充
紧凑归档。旧验证器硬编码本机根目录，因而旧 PASS 只证明本机 source 存在，
不能证明独立检出能解析全部 authority。

修复保留每项原始 `path`、SHA-256、角色和科学解释，新增 `package_path`
指向字节相同的包内证据。未用近似报告、更新文本或其他 cohort 替代证据。
八项新增报告在 `1006/evidence/authority_sources/`；完整原始到包内映射
在同名 JSON 审计。验证器改为从实际脚本所在的检出目录解析包内路径。

此修复仅关闭紧凑账本的文件定位和字节核验问题，不补齐历史 GPU 原始
prediction/render payloads，不证明新方法有效，也不改变 HOLD 与改稿冻结。
