# 最终逐审稿项闭环裁决

审查对象：2026-10-12最终整合源码，以及第15版和第二轮原审稿意见。本表的“关闭”指已处理该具体文字/证据请求，不等于保证接收、建立优越算法或完整历史复现。

原意见来源：[第二轮审稿意见](/4T/MV-Painter-local-archive-20261010/run_20261010T033233Z/worktrees/core-shared/00_MV-Painter/untracked/1006/review/second_round_reviewer_comments.txt)。最终[回复](/4T/CXY/MV-Painter/final_paper_20261012/source/Response_to_Reviewers_final.md)。

| 原请求 | 实际完成的证据 | 尚未完成/不能推出 | 最终状态与合适措辞 |
|---|---|---|---|
| R1.1 完整对象、合理固定与unmodified对照、未见烘焙和consistency | 共同全对象框/ROI；GFH和Generic Linear完整；10兼容GeoTex实际UV烘焙，另20 GSO完整；GT同分辨自烘焙；80 incoming UV variance重放和已知颜色controls；native residual、No Adapter探索补充；实际mesh视频 | 主Fresh C300无完整官方default输出；native residual不是完整default；明显色偏/纹理失配未修；无验证seam/PBR端点；烘焙资产兼容选择且GSO校准后验 | **部分关闭、质量边界仍开放。** 写清小局部收益和另协议非检出，不声称已建立普遍实用优势 |
| R1.2 同historical main adapter、selection外同协议确认+0.96 | Fresh C300 UID-disjoint冻结重训与完整强对照；原276请求UID去79训练交集后1039重训，1104行完整；三份v2 EMA匹配既有MD5 | v1精确byte/run/metric identity没找到；原276日志确认obj_0046 loader随机替换未知实际UID，不能认证276唯一对象、train-disjoint或对象独立性；275排除只是技术敏感性；v2只属另强残差实验 | **历史复现未关闭；Fresh C新成对证据增强，original276不承担严格留出证明。** 不能叫+0.96复现，不能用新重训或v2替换v1 |
| R1.3 variation≠fidelity、可见artifacts | separate端点定义；失败富集26对象颜色诊断；原276raw +1.699dB但FG −1.314及LPIPS更差；烘焙GT比较；撤92%历史prevalence；保留C1/B2失败 | 无通用颜色cause或通过门槛修复；高频/梯度增加、几何未变不能证明材料或结构改善 | **解释与报告请求关闭；保真改进未建立。** 公开失败和端点反向 |
| R1.4 paired CI、Edge tradeoff、noninferiority | 对象配对区间；C3−GFH FGSSIM损失和Bake10 SSIM −.05274/原Holm=.00781公开；views/seeds嵌套；没有后验NI margin；区间pointwise说明 | 未检出不是equivalence/NI；多检验family分别控制不是全研究FWER | **统计解释关闭。** 使用“未检出”/“更低的结构端点”，不说无损保留 |
| R1.5 FAC代码/复现 | 恢复84文件两个入口、byte hashes；三种唯一CPU fixture forward/gradient/state checks；历史负表明确来源；1200/1706矛盾公开 | 历史seed/sourceCLI/checkpoint/输入输出绑定缺；组件check≠isolated full-model training；早入口可能训练base | **代码交付部分关闭；历史FAC训练复现未关闭。** “recoverable source and bounded component validation” |
| R2.1 超越手工schedule selection的实质贡献 | SSI等先例正面承认；移除时间函数即新方法论；恢复真实Middle−avg主问题；强固定/linear反证；实际烘焙与原276端点边界；native及seed限制 | C3非合理强control普遍胜出；CAI无独立选择器；A2/A3b无dose-independent机制；实验多≠innovation充分 | **可辩护实证贡献、编辑判断仍开放。** 三项有限新增知识，不声称方法创新已解决 |
| R2.2 CAI事后formalization | 独立推导/proposition/optimality从主动稿撤回；C3历史selected；applied budget≠realized correction；旧rawL2 common support撤回 | 不证明CAI正确或可前瞻预测；不同层范数无法直接比较剂量 | **通过撤回不支持主张关闭。** 不重新包装CAI理论 |
| R2.3 genuinely different backbone | 原生MV-Adapter50/350行、GSO100三seed、75 MVDiffusion第三接口；native/default18 images +features identity，MVDiffusion1552 tensors/单对象12 outputs scope公开；负结果完整 | 相同labels非共同operator/dose；depth未缩放的MVDiffusion为partial transfer；不同domain/weight/protocol不能归因backbone；没有普遍收益 | **不同骨干验证工作实质完成；正向泛化未成立。** 回应“已检验且混合/不利”，不是还缺第二骨干 |
| R3认可修回 | 保留研究连续性并按新证据修正主结论 | R3赞同不能覆盖R1/R2未闭合或新scope变化 | 感谢并明确本次贡献定位/结论更新 |

## 对最终源码和回复的一致性检查

最终主文/回复同时明确题名调整、实证定位、原中段主问题非检出、原276的反向端点、v2≠v1、CAI撤回、FAC恢复范围和seam/PBR缺失。此前primary遗漏及Supplement“12对象描述在主文”陈旧引用已修复。随后运行日志确认original276一次未知UID随机replacement：这将先前“actual UID hash缺口”升级为已知identity偏离，删除276真实独立对象/严格留出推断。最新摘要、正文254/268行、补充1135/1137行与R1.2回复已经改成request-slot技术敏感性并加入275排除读数；回复53行旧“276-object”字样也应统一。按此处理可保留核心实证稿，不应掩盖该失败。

可保留C&G修回：这是相同应用问题与干预在完整证据下修改推荐。应持续在cover/reply说明从“推荐C3方法”收敛为“控制分配受控实证”的变化。不能将新标题当隐藏方向变更的办法，也不需要为了符合方法叙事删除反证。

## 最终交付门槛

- 保留所有主检验的实际定义、原family、chronology和pointwise interval；尤其原Middle−avg不能被Middle−Mean替换。
- 原276和v2身份新增证据必须进入同一个最终包，表、正文、回复和复算入口一致。原276是一已知随机替换、276请求槽位、275剔除技术敏感性；记录映射完整不等于actual UID、train split或对象独立性认证。槽位interval/p不能冒充对象总体效应推断。
- 正/反烘焙结果、强固定/linear、非参考LPIPS、seed不稳定、native/v29弱质量和未成功修复不得因不利而删去。
- 更改后的PDF、marked稿、source/statistics、hash及文件地图应由最终构建重新验证；父版本PASS不能证明新PDF。
- 数据重算、源码恢复/组件执行、fresh inference和历史训练replay分级披露。不可称full replication badge。

**最终可交付状态：有限但可信的实证修回；原v1/FAC历史复现与材料实用品质请求仍有明确缺口；R2.1贡献充分性仍由编辑与审稿人裁定。** 不应继续以重复训练或新p值累加把“待判断”包装成“关闭”。
