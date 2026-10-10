# 第四轮冻结计划

1. 独立源文件来自完成的round003；旧轮不覆盖。
2. 两个同UID，四固定条件：cached/off、online/off、cached/CFG2、online/CFG2；全无GeoTex，256视图、50步Euler、seed与输入同旧控制。
3. cached/off输出必须与旧NoAdapter逐像素一致；各条件conditioning和初始latent相同。在线CLIP来自冻结base资产、同一已处理RGB，不调用原生RGBA重心/亮色处理。
4. 记录每次真实正/负UNet调用、正路CUDA RNG状态；四臂正路每步RNG轨迹相同，负路采样不改正路状态。online/cached差异只用于定义特征干预，不等同外观保真。
5. 完整展示八张六视图；无跨相机GT统计、无显著性检验、无独立泛化或新算法主张。保留旧C1/B2负结果。
6. 据输出是否定位可修复路径决定后续优先级；所有不利结果保留。整合独立正文/补充/回复并验证。
