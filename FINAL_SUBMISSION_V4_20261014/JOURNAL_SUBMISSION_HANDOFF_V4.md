# V4 journal submission handoff

本轮唯一实际期刊交付目录：`/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4`。四份PDF来自本轮V4当前源，数值表未变。源稿基准为PR#1 c3017645；作者信息、Highlights和声明文件逐字节保留。不要上传quality_review中的替代候选主文页面作额外稿件。

| 文件 | 上传角色 |
|---|---|
| FINAL_V4_MANUSCRIPT.pdf | Clean/Revised Manuscript（13页） |
| FINAL_V4_MARKED_MANUSCRIPT.pdf | Marked/Tracked-changes Manuscript（21页） |
| FINAL_V4_SUPPLEMENTARY.pdf | Supplementary Material（71页） |
| FINAL_V4_RESPONSE_TO_REVIEWERS.pdf / .docx | Response to Reviewers（PDF5页；选择系统支持的格式） |
| Manuscript_LaTeX_Sources_V4.zip | LaTeX Source Files；主源选择FINAL_V4_MANUSCRIPT.tex |
| Research_Evidence_V4.zip | Supplementary Research Data；原冻结内容完整保留，追加当前显示/质量记录 |
| Title_Page_V4.pdf / .docx | 独立Title Page；不合并入匿名主文 |
| Highlights_V4.txt / .docx | Highlights |
| Declaration_of_Interest_V4.docx | Declaration of Interest |
| 两个MP4及对应Still.png | 分别Video和Video Still；没有专用类别时使用Supplemental |

必须实际分别上传的两段视频：

- `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4/Supplementary_GeoTex_Baked_Comparison.mp4`（22秒，H264，2304×346，528帧；LG Remote/Tire，各11个raw001–011相机）。SHA-256：`6191b81e6336c6be62fcd8962a33f1e84245667b68ae6346be2815da1d9502a3`。
- `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4/Supplementary_GSO_Baked_Comparison.mp4`（5.5秒，H264，1024×1128，11帧；首个mouse、seed42、12条件、11个协议相机index0–10）。SHA-256：`2e76a5d742fc8432aa8f0f6e58df13d442074bfddcb8552bc539fe665f1261b5`。

GSO的source_gt是原始source-mesh渲染，不是GT self-bake。GeoTex视频不包含主文Figure3的font对象；Tire与主文共享同一协议。视频只是完整固定条件示例，不等同于十/二十对象总体统计。相机编号跨协议不能互换。详细身份/解码/源帧对比见quality_review/VIDEO_VALIDATION_V4.json。MP4保留原字节；不依赖GitHub或网页链接来完成期刊附件交付。

对应Still.png以及`Supplementary_Video_Captions_V4.txt`已在同一目录。根据[Elsevier视频提交指引](https://www.elsevier.support/publishing/answer/how-do-i-include-a-video-with-my-submission)，在Attach Files分别上传视频和静帧，提供文字引用/说明；若没有Video类别，用Supplemental。预览时检查视频下载链接。LaTeX源包与审阅PDF分别提交，见[Editorial Manager文件准备指引](https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager)。

完整本地文件路径、大小和SHA在`/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4/JOURNAL_SUBMISSION_MANIFEST_V4.json`；其公开交接副本在quality_review/JOURNAL_DELIVERY_MANIFEST_V4.json。

AUTHOR_REVIEW_READY=YES；SUBMISSION_READY=YES，含义是该受限实证稿和实际附件已可交作者提交，而非录用或真实部署品质认证。贡献强度与不能关闭的科学缺口见quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md。没有执行期刊系统的最终提交操作。
