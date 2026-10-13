# Figure 1：控制组件existing / intervention身份对照

|图中组件/ID|归属|实际操作与依据|
|---|---|---|
|Reference conditioning|Existing pipeline|冻结图像条件路径；真实camera014由embedding manifest确认。|
|Normal/depth/mask与GeoTex-Adapter|Existing pipeline|五通道多视图几何条件及预训练adapter，不是TCAS创建；展示代表性source014。|
|h_frozen → GeoTex特征支路|Existing pipeline|model_unet_geotex.py:143定义compute_correction(x,geo_feat)，343传入原resnet的hidden_states；不是新skip/training路径。|
|TCAS requested schedule / requested-C3-discrete-curve|Study intervention|研究指定的inference-time requested temporal profile；1.25/2.50/1.25及17/33离散切换。并不据此主张调度原理首次提出。|
|Existing wrapper / existing-native-cap-control|Existing implementation|原wrapper的per-group上限c_l，min(request,cap)；deep3/middle3.5/shallow.8。已从TCAS框中分离。|
|Applied scale / applied-scale-heading|Executed result|nativecap后的实际scalar，不是独立新算法模块；deep/middle保留请求，shallow全程.8。|
|× 与scaled geometry residual|Existing residual operation with studied scalar|geometry correction乘以上述executedscale；不是新residual分支。|
|Frozen feature addition / feature-addition|Existing injection operator|hidden_states+correction，原wrapper多个group/site的抽象示意；不存在新UNet训练。|
|Six RGB output views|Existing generation outcome|同一FreshC UID，native记录顺序014/015/000/016/012/013。|
|Independent bake panel|Downstream evaluation|另一个Bake10 UID的真实UV与unseen004；不属于TCAS推理模块，不与FreshC对象连成连续管线。|

方法图用于解释研究干预位置与实现边界，不作为算法新颖性、普遍效果或材质保真证据。代码中的可选后续adaptive controller不在本实验或图中。
