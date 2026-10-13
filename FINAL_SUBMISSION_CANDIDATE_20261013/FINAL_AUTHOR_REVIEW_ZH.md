# TCAS最终候选：作者审核报告

日期：2026年10月13日。目录：FINAL_SUBMISSION_CANDIDATE_20261013。现有01549、1014finalv1及此前冻结候选未覆盖。

## 本轮已完成

- 最后一次研究MVPainter、MVPaint、Paint3D、MV-Adapter及原01549正式方法图后，保留真实大图与科学结构，只优化参考条件标注。TCAS请求与existing cap归属明确，六视图camera014/015/000/016/012/013真实顺序、独立Bake10样本保留。图件设计结束。
- 精修主文的摘要、引言、贡献、方法边界、讨论与结论。中心问题是控制比较能识别什么、收益是否进入真实UV资产，既有调度先例得到明确承认。
- Supplement增加证据状态/样本身份导航与可点击目录，相关限制归位。保留全部重要负结果、回顾性/追加统计家族及失效记录。
- 回复信覆盖两轮真实意见，68处定位依据最终编译结果。R3二轮仅正面意见，无虚构请求；R2.1正面说明可证实知识价值，同时保持部分解决。
- 最小修复Supplement TableS2易误读的负号换行；28行数值、解释与字号均不变。

## 可直接查看的成品

|文件|内容|
|---|---|
|1014finalv1.pdf|清稿15页|
|Supplementary_1014finalv1.pdf|完整证据71页|
|review/Response_to_Reviewers.pdf|回复信5页|
|marked/Marked_up_Manuscript_01549.pdf|相对认证01549标记稿22页|
|figure1/fig1_tcas_editable.svg/PDF/previewPNG|最终可编辑方法图、矢量与预览|
|CLAIM_EVIDENCE_MAP.csv|15项关键主张、身份、证据与局限|
|VERIFICATION_REPORT.md、audit/|数值、引用、源文件、独立科学与实际PDF视觉检查|
|MANIFEST.sha256|交付文件SHA-256清单|

## 验收结论

SCIENTIFIC_GATE=PASS；EDITORIAL_GATE=PASS；SUBMISSION_TECHNICAL_READY=YES。
R1_CLOSURE=PARTIAL；R2_CLOSURE=PARTIAL；R2.1=PARTIALLY ADDRESSED。
AUTHOR_APPROVAL=PENDING。

独立审核实际检查主文、Supplement、回复及标记PDF，未发现剩余阻断；全部页做了布局覆盖，关键图与表做了放大检查。此结论不等于作者审美认可、算法新颖性获证或审稿人一定接受。

## 仍须由作者判断

1. TCAS仍是手工请求调度；现有任务特定知识论证不能消除R2对方法贡献强度的合理疑问。
2. 原主checkpoint不能认证；FreshC是受控再训练，历史276有未知替换UID，不能宣称精确复现或认证276对象独立holdout。
3. GeoTex10收益小且兼容性筛选；GSO20未检出，协议不同。材质/颜色差异仍明显，未验证PBR或seam质量。
4. 完整默认GeoTex质量对照及历史FAC训练重放仍不足；1200/1706身份差异、缺少run-boundmanifest/weights保持披露。
5. Supplement较长且部分表需放大阅读；浮动表留白、少量重复提醒/标记稿密度和个别标题双句点是非阻断问题，不再重开编辑路线。

原始Middle−average(Early,Late)300个差值、原bootstrap区间/p及12项secondary已完全复算；其他关键cohort配对均值和Holm家族亦核验一致。144份冻结数据逐字保留。Figure1的24项source/displaySHA核验无误。

用户已追加授权完成后上传GitHub：使用独立codex/tcas-final-submission-20261013分支，不覆盖main、不强制推送、不进行正式投稿。最终提交哈希在交付消息中给出；作者可据此整包审核并决定是否提交。
