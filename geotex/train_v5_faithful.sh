#!/bin/bash
# GeoTex v5-faithful：v2 精确配方完整训练（健康 adapter 的稳定复现）
#
# 配方 = v2 的 train_args.json（10000 步零 NaN 的成功条件）+ tcas_ramp scale 逻辑：
#   --tcas_ramp:  Phase1 (0-2000) uniform 1.0 → Phase2 (2000-4000) ramp →
#                 Phase3 (4000+) 完整 TCAS v2 schedule（deep/middle 最高 3.0/3.5）
#   --var_weight 0:  v2 时代无 var_loss（该 term 是 fd6db2f 后加的，且会驱动
#                 adapter 权重失控生长 → 已诊断为此前 NaN 的共因之一）
#   --proj_clamp 0:  v2 时代无 clamp
#   --reg_weight 5e-5: v2 的原始值（当前默认 1e-3 是 fd6db2f 后改的）
#   config 已恢复 train_objects_2000.txt（v2 训练数据，fd6db2f 改成 clean）
#   model_unet_geotex.py output_proj 已恢复 random init (std=1e-3)
#
# 训练完成后：推理时以 γ=0.6 应用（甜点，C3 SSIM ≈ 0.271）
set -e
cd /4T/CXY/MV-Painter

python3 geotex/train_v2.py \
    --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
    --output_dir mvpoutput/geotex_v5_faithful \
    --steps 10000 \
    --warmup_steps 1000 \
    --peak_lr 5e-5 \
    --min_lr 5e-6 \
    --grad_accum 4 \
    --ema_decay 0.9995 \
    --save_every 2000 \
    --eval_every 2000 \
    --grad_clip 0.5 \
    --seed 42 \
    --fg_weight 0.7 \
    --edge_weight 0.3 \
    --ssim_weight 0.2 \
    --reg_weight 5e-5 \
    --var_weight 0 \
    --proj_clamp 0 \
    --tcas_ramp \
    --device cuda:0 \
    2>&1 | tee mvpoutput/geotex_v5_faithful_train.log
