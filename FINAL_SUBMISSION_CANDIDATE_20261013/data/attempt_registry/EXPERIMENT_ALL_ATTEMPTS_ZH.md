# 本地全实验类别、失败尝试与最终论文方向审计

日期：2026-10-12。范围：主工作区及现存 14 个 Git 工作树的报告/配置/CSV/权重线索，外部归档和未注册临时目录的索引。根任务核实当前私仓为 **8 个远端分支**；历史 28 分支与其提交仍可通过 `refs/archive/...` 追溯，并非全部消失。此次没有新增训练、推理、烘焙或图像评分。

结论：**现有工作适合整理成关于预算、评价端点与接口依赖性的受控实证研究；不支持把 C3 中段调度、层窗显著性或失败后修复包装为普遍有效的新算法。** 旧 v2 权重已找回，原 v1 主表身份仍未闭合。新增 20261012 去重叠重训有价值，但发现一次实际随机样本替换和全图/前景指标方向反转，应透明单列为协议敏感性。

## 审计深度与不重复计数

`EXPERIMENT_LEDGER.csv` 有 **105 条实验/迭代/归档条目**。它包含成功、失败、混合、失效、未验证完成与纯包装，**不是 105 个独立实验**。完整原始来源使用绝对路径，并为每条标明评价单位、队列关系、接口/权重/预算、指标是否存在、引用上限与本次审查深度。

`METRIC_FILE_INVENTORY.json` 是现存 14 工作树的 ignored-inclusive CSV 清点：4278 个 metric/result/paired/summary/benchmark CSV 路径，572 个不同字节 hash，406 个多副本组。不同 hash 也可能是同数据的条件切片、汇总表、复算输出或不同换行，不等于独立实验；同 hash 可以证明文件副本，不证明独立复制。外部归档的扩展 metadata 清点由根任务单独交付；本文件不把初始 4278 范围冒充所有归档总数。

此次实际阅读了001–015逐轮最终结果、1010主/最新执行报告、早期科学审计、跨接口报告、色偏最终门槛、人类研究聚合审计、checkpoint来源与新276运行日志。关键原权重实读MD5，新276全部CSV实算配对统计和split交集。没有逐张人工审阅全raw PNG、视频、GLB，没有重新验证每个历史训练过程或每个存储的tensor hash。仅目录/配置存在的尝试明确标为“完成未认证/档案”，不会冒充性能证据。

## 1. 真正独立的队列与复用关系

已实读 UID 名单并交叉比对，`FRESH_COHORT_CROSSWALK.json` 保存路径和 SHA：

| 队列 | 对象数 | UID-list SHA 前缀 | 用途与复用 |
|---|---:|---|---|
| Fresh A | 300 UID | b81bd142 | A2/A3/B1B2/B3/Generic C 等科学干预共享该队列；不是多个独立300。历史审计记录一组视觉重复资产，300 UID/299种视觉内容。 |
| Fresh B | 150 UID | f681e33c | bounded A3b、LLH时间/预算、generic扩展共享同150；static48是选择性子集。 |
| Fresh C | 300 UID | d9388186 | 后期原四条件、generic加项、1010 matched300复用；native50和技术烘焙10/旧5是其子集，不能累加成另一个独立验证队列。 |

A/B/C两两 UID 交集均为0。它们是否 pristine 仍取决于每项决策前是否看过输出；UID独立不是研究决策独立。1010 matched300是已观察队列上的后见固定比较，不能因为冻结了脚本而追认为前瞻预注册。

旧 test300、24开发probe与名义276是同一旧列表的拆分。20260928受控重训 train1118 与其有101/300重合，其中79在名义276。clean-v2把101个UID替换，保留199，去掉UID泄漏同时改变来源组成；不能视作原300的同源精确复现。20261012改为删除训练交集79，保留原276**请求名单**，产生新权重；一次 loader 随机替换使实际覆盖不再等于请求覆盖。

MV-Adapter旧76面板的映射/层窗/匹配范围/预算补充共享76；G层窗98/99是另一套冻结输入和接口干预。MVDiffusion75亦另列。GSO100的三seed与GSO20烘焙子集是便利外部域敏感性，不与GeoTex/MVA50/MVD75池化。每对象先汇总view/固定seed后推断，不把视图与seed当新的独立对象。

## 2. 历史v2/v3、重训与原始调度探索

来源：`/4T/CXY/MV-Painter/mvpoutput/`、`checkpoints_saved_20260803/` 和 `archive3.0/archive2.0/mvpoutput_old/`。

- **v2_old：** 10000步旧强残差EMA的三个本地副本MD5均 `a74cc1d16cb473a95022bdcbc58e1b22`，文件身份已闭合。eval_300四条件与eval300v2四条件CSV各保留；数据路线不同，不合并。它是强残差扩展，不是原v1主表恢复。
- **v3 anticollapse：** 6000步日志完成，但最后micro-step均NaN跳过；浅层0.1、projection clamp1.5、防坍塌损失改变了模型。step1000四对象30step诊断有轻微PSNR变化，不是普遍部署验证。
- **v4 sweetspot / v5 faithful / v5 sweetspot及smoke：** 8000/10000计划、训练参数、部分step权重/日志存留。某些末尾没有完成证据；本次未恢复有效最终质量链，不能据目录名宣布成功，也不能不加分辨一律写失败。
- **v2_ext / v2_quick、era_repro / reg_probe / repro_test：** 历史扩展/小训练/再现尝试存留。权重与计划存在不代表原v1恢复或精确训练重放。
- **24对象调度搜索：** `revision_schedule_comparison` 312行/13条件；`revision_scale_sweep_v2` 72行；`revision_c3_sensitivity` 360行/15配方。对应4对象smoke分别保留，不能把smoke加到正式样本。
- **300对象后续通用调度：** cosine/linear各300；C3/gaussian/trapezoid的`revision_top2_300` 900行。它们是旧队列上的更多条件，不能作为3个独立300对象确认。
- **矛盾/剂量诊断：** v2/v3、stage ablation6/24及24rerun、cap ablation4、norm schedule/control6、strength-match6、residual-scale粗/细扫均列入台账。`OLD_POLLUTED`和`BUG_CUMULATIVE`显式归档；最终rerun不能和被污染/累计缩放bug输出池化。norm-flat与weak-fixed的对应限制了“独立归一化算法”解释。

允许的结论是某个checkpoint/cap/输入协议中强度和时间会改变输出，早期最有利均值不提供全域最优、机制独立或新算法创新的证据。

## 3. FAC全部可见尝试

`fac_v2`有500步训练完成日志；`fac_v2_v2`及`fac_v3_smoke`仅部分/开发材料。`fac_v3`的LTAG、LTAG+GSG、full各300对象CSV，FG-PSNR约7.794/7.035/6.941；历史TCAS表为9.940。`fac_v4_frozen/full`约7.320；`fac_v5` A_envpen/C_fidw/F_gentle各300约7.138/7.510/8.775。不同损失、冻结与训练终态不能仅由均值公平归因，但这些尝试显然不能忽略而继续声称FAC已被证实普遍提升。

第015轮恢复84份原字节源码/config/依赖和三个CPU控制器fixture；前向、梯度、保存加载是组件有效性，不能替代原1706训练名单、seed、checkpoint与主表绑定。早期入口默认训练adapter/encoder，后期controller-only；FSC实际FFT且初始掩模非严格恒等。当前第8远端FAC bundle e1f54f91新增55文稿/图/回复包装路径，继承这些已有检查，没有新FAC训练或图像质量实验。

## 4. 早期科学验证的正确引用等级

来源：`/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/`；最终上限：`/4T/MV-Painter-01549-unified-20261009/1006/evidence/audits/LAYER_WINDOW_FINAL_INTERPRETATION.md`。

| 研究 | 原始规模 | 保留发现 | 不能升级成什么 |
|---|---|---|---|
| A2层×窗 | FreshA300×16=4800行 | native干预下响应异质性显著 | 独立验证的通用机制 |
| A3剂量压力 | 同300×16=4800 | 显著性仍在但FGPSNR交互share约0.8%；浅层stress-only | A2独立复制/完全等剂量 |
| A3b bounded | FreshB150，2250干预+baseline子矩阵 | LPIPS/PSNR异质性存在 | 剂量独立交互；0/2250三层共同支持、跨层范数尺度不可直接比较 |
| B1B2 / B3 | FreshA300×6/7 | LLH对exact-layer-mean常量约+0.435dB；cap影响明显 | 把layer/cap/budget贡献相加；只凭显著性选择最佳窗口 |
| Generic C | 同300×8=2400 | endpoint-matched linear未检测到FGPSNR差异 | LLH普遍胜所有调度；未预设margin不能叫等效 |
| FreshB temporal | 150×30=4500 | LLH−LFMexact+0.325dB；LLH−HLL+0.687均值但仅45.3%对象有利 | 典型对象都受益；超实用margin优势；early-high所有端点都损害 |
| FreshB generic扩展 | 150×8=1200 | 所有通用shape/预算版本保留 | 另一个独立FreshB复制 |
| Static48 | 48×4×3固定seed | LPIPS交互近零，PSNR交互约+.365 | 随机训练seed总体机制或新的确认集 |
| G层窗MVAdapter | 98×16=1568 | 小的晚期浅层LPIPS恶化；全局交互校正未确认 | 迁移规律或全接口零效应；99目标中1个无三角面不能偷偷替换 |
| GT纹理失败边界 | FreshA300 | LLH−GFL改善集中低纹理，HF关联ρ≈−.691，丰富纹理可反转 | C3最优/真实材质保真 |

生产interaction bootstrap发现零功效缺陷后的Wald/GEE修正是真实审计改进，但不能倒推出原预注册检验全部成功。以最终解释为准，A2/A3/A3b保持辅助表征，不承担方法创新核心。

## 5. 跨接口、外部基线与人类证据

MV-Adapter旧24校准/76holdout有global identity、层映射B211/M3、LHL/LLH、matched-range和equal-budget面板，全部不是“尚未做第二骨干”。新native50校准后350行，Middle−Mean FGPSNR约+0.029dB，CI跨0，p=.281。旧N7质量表因为相机/归一化不匹配失效，native bitwise身份门槛本身保留。

MVDiffusion75×7=525行，450新增生成、SD2-depth原生镜像1552/1552张量核对、单对象12/12输出一致和原生36/36视角门槛有记录。控制操作是decoder CPBlock插值，不能称GeoTex残差算子的严格架构复制。负面和混合结果支持接口边界，不支持跨骨干普遍收益。

SF3D JSON分别29与298对象；298不是300完整覆盖，29不是另一个独立大样本。任务改变了几何生成/渲染路线，本次未重新认证公平camera/material端点，因此保留作历史外部baseline资料。Wonder3D-TCAS配置和多shard输出存在，但本次未发现并认证统一有效metrics；不能根据输出文件数量宣称性能。CLIPIQA逐对象CSV亦不能代替human/material质量。

**确实存在已分析的人类研究。** main的`1009/evidence/branch_audits/human_confirmatory_analysis_20261007/`记录40 slots、37合格参与者、24对象、4比较×2问题，每端点222判断。八个点估计都利于LLH，但none Holm显著；GFL texture约.647/Holm.0984，GC3约.632/Holm.1281。endpoint冻结不消除分配/左右/问序/stimulus hash执行偏差以及缺失consent/ethics文档。只保留聚合审计，不读取个人响应，也不把它写成正面偏好证实。`mvpoutput/revision_human_study`空目录不等于全仓无人类数据。

## 6. 色偏、烘焙与自适应控制失败不能遗漏

色偏`r1color`的四对象Phase B16条件/64生成/384view显示global-appearance通路可控制部分色向。B2实际八次生成完成，CIEDE2000平均差+.1729，只有1/4改善，未过3/4且均值≤−1的冻结门槛；C1数值−1.560，但视觉门槛失败、青蓝边缘/残余失配，未开启FreshB修复验证。它们没有建立稳定修复或唯一根因。

历史科学烘焙N20（24预选排4无UV）有CPU与GLB-native EGL端点。旧CPU clamp UV与GLB repeat/filter不一致，旧seam/renderer数值不能当忠实GLB结果；native EGL闭合保存输出采样，但不能追认clamp-based bake过程完整正确。多端点仍冲突，非唯一LLH赢家。

1010新烘焙目标20，300输入仅10通过冻结技术门槛；7生成方法+GT256形成80对象条件与880未见view行。Late−Mean LPIPS−.00265，CI[−.00414,−.00137]，10/10同向。旧5经REPEAT/极点/alpha校正后单列，C3与GFH等端点仍冲突，不能和新10池化。GSO20修订校准后Late−Mean未见LPIPS+.0000838，CI跨0；有限10对象的局部收益不能推成普遍部署法则。

未注册`/4T/tmp/mvpainter-adaptive-control`还保存TRB/TRB2旧24开发pilot。TRB−C3 LPIPS+.001302，CI[.000079,.002549]；修复预算计账后的TRB2−C3−.000045，CI[−.000827,.000670]，仍未稳定胜C3，且额外50step校准pass使实际开销约翻倍。promotion gate失败，276holdout未开；这是不同于后期APG/投影的早期负面候选，不应遗忘，也不重启同类试验。

## 7. 第001–015轮各自完成了什么

各轮报告在`/4T/CXY/MV-Painter-cg-revision-20261010/1008/manuscript/iterations/`；完整source见台账。

| 轮次 | 增量与最终裁决 |
|---|---|
| 001 | GT256标尺、Late−Mean相对误差/删一对象敏感性；复算不是新对象。 |
| 002 | native-unset/NoAdapter/constant控制、30生成/20新烘焙/330view；调度native差异均未Holm显著，完整默认路径仍不同。 |
| 003 | 两已见失败对象50/75step四次完整base；首RGB输入失败留档，未作跨路径GT推断。 |
| 004 | CFG×缓存/在线embedding八次；没有恢复参考外观。 |
| 005 | 256/512目标尺寸×CFG八次；512恢复布局线索，但颜色/纹理失败未解决。 |
| 006 | 60相机元数据、两对象×8原生GeoTex；关闭逐像素匹配，开启几何损参考内容。 |
| 007 | 12个编码尺寸/CFGbranch对照，半幅局部改善不泛化；训练入口未实际执行configured dropout，旧target含重复top，精确重放缺口。 |
| 008 | 1118→1112完整→1090有效、22输入预生成排除；真实FP32正则/两GPU反向gate后正式训练启动，当轮训练未完成。 |
| 009 | 固定2000step训练完成；50×8加完整v29共450输出；几何优于弱HF-off但C3/Late无强基线优势。 |
| 010 | 同v29底座再训2000step、50×2与复用v29；几何对off LPIPS−.0131，但仍输v29 .0159，SSIM亦差。 |
| 011 | 5对象两GPU60计时+8warmup均身份一致；约23%延迟节省伴随质量损失，不归因TCAS。 |
| 012 | 条件投影/APG开发32/确认64、nativeMVA32、GSO100三seed；源view正面而非参考未稳定胜；外部投影更差；原GSO烘焙UV-ramp失败后停止。 |
| 013 | 追加既有四调度1200形成3600unique generation/21600view；20×12×3+GT=740GLB/8140view；主要Middle−Mean与Late bake不支持，GT-only校准修订透明保留。 |
| 014 | 13结果进入完整稿、图表/负面/strong-control重排和包核查；未增加算法。 |
| 015 | 无新训练生成：UV方差80条重放、三seed对象稳定性、270/300 C3点估计被至少一控制弱支配、84FAC源码与3CPUfixture。 |

当前不能以“第15版”当全部实验的唯一权威，也不能以轮次增长当科学优势增长。第9–11轮已重新训练并比较完整强底座；第12–13轮已经试过APG/投影及外部GSO，不应再称这些研究尚未执行。

## 8. 新276重训的额外发现与限定

`ORIGINAL_CHECKPOINT_IDENTITY_ZH.md`和`ORIGINAL276_RETRAIN_AUDIT.json`给出详细身份链。训练/请求评估名单0重合和2000step新权重已经实核；但loader在`obj_0046`的空有效深度错误后随机换样本，实际替换UID未记录，不能声称精确原276全覆盖。

C3−FixedHigh：full-image PSNR+1.699dB，同时FGPSNR−1.314dB、FGSSIM−.05961、FGLPIPS+.01127、EdgeSSIM−.02777。排除已知替换ordinal后275敏感性方向不变：全图+1.6965，前景PSNR−1.3110，LPIPS+.011272。它揭示**端点与背景影响**，而不是挽救C3性能主张。六视图在这组runner中拼成网格统一评分，不套用FreshC逐视图均值定义。新分析是后见探索、不是原v1+0.96重放。

## 9. 外部归档、历史refs与尚未完整实审的范围

下列目录均存在并列入台账：`/4T/MV-Painter-local-archive-20261010`、`...-20261009`、`/4T/MV-Painter-01549-local-records-20261009`、`/4T/MV-Painter-main-consolidation-20261009`。Oct10归档含source/patch/hash清单、1006证据包HOLD、未认证新24-object panel、human聚合副本、adaptive负面pilot和活动稿快照。归档README的21树/22 heads/旧main SHA是采集时状态，不冒充当前live状态。

`/4T/tmp/mvpainter-layer-bake-input-20260930`、`...-recovery-HLzm9O`、`...-adaptive-control`、`...-layer-lhl-ablation`、`...-layer-confirmation-20260930`、`...-e6-authority-clean-xknggnwm`、`...-b3-recompute-y4kwdrq6`是现存未注册索引。恢复/确认/复算副本只有确定UID/hash才归入原实验；本次并未把其所有内部图/JSON逐项科学复审。所有归档路径检索亦未找到原v1目标或旧EMA额外副本。

历史refs包括main-unification的local/remote/wip/pre-wip和clone-retirement提交，不是论文之外证据都被删掉。真正尚未全部实审的范围是：完整ignored媒体逐图、每个历史训练采样/loader runtime、未认证24对象面板、部分v4/v5/SF3D/Wonder3D末端有效性，以及临时恢复目录每个汇总文件。它们的存在已记录；未知部分不作为有利结论，也不用于把最后论文标为科学门槛全关。

## 最终正文组织建议

先给FreshC同应用尺度预算的明确反证：Middle−average(Early,Late) −.0339dB，CI跨0；C3输固定均值和Late。再并列有限GeoTex10烘焙正面与GSO20零结果，解释图像/烘焙端点、对象与seed稳定性。native训练/完整v29说明实际质量成本边界，MVA50/MVD75说明接口边界。原权重与新276协议敏感性独立小节，公开身份缺口、替换与端点反转。A2/A3b保持辅助表征，FAC/修复/TRB/APG/投影保留负面档案。

这种组织支持关于**控制分配效应、强对照反证、评价端点差异与应用边界**的可核查知识；不承诺新方法胜出、中段最优、跨骨干普适、剂量独立机制、材质/接缝/PBR保真或接收概率。最后论文价值应由这个有限贡献与已有先例的正面比较判断，不能靠重复训练或隐去失败提高表面说服力。
