# 第二轮冻结计划

1. 独立创建round002文件；冻结上一轮身份与既有十对象UID顺序，禁止改选对象。
2. 运行三个控制：native_unset（属性缺失的原生wrapper残差），capped1.0，NoAdapter。复用已验证模型/输入/50步采样；GPU启动前核查占用。不得改动上一轮runner或七条件矩阵。
3. 验收capped1.0与上一轮输入hash/种子/输出RGB逐像素一致；native每次真实wrapper调用记录属性缺失；NoAdapter无残差。
4. 同一原网格、GT256、相机、掩码、REPEAT、atlas与补洞参数烘焙新控制；评价相同11个未见相机。前一轮GT和七条件不重选、不重调。
5. 完整报告新控制均值；Late−native、C3−native、NoAdapter−native的五指标共15比较仅探索性，Holm一起校正，区间对象bootstrap点估计；不新增确认性primary。
6. 更新独立正文/补充/回复，保留GT差距与失败例；编译和验证完整该轮，记录新边界。完整官方pipeline身份仍须限定，不能因wrapper分支正确自动升级措辞。
