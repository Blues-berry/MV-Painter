#!/bin/bash
# GeoTex v5 训练："甜点 adapter"（修复版 v2）
#
# 设计理由（find.md §8.3/§8.4 修正诊断）：
# - 根因（2026-08-07 确认）：fd6db2f (08-01 "TCAS 整理") 把 GeoTexAdapter.output_proj
#   从 random init (std=1e-3) 意外改回 zero init。zero init 切断 encoder/adapter 梯度流
#   （step1 gnorm 0.002 vs v2 的 0.0067），optimizer 空转 → 权重增长失控 → fp16 前向溢出。
#   v4 (781步) / v5 (2211步) NaN 均由此引起。
# - 修复：model_unet_geotex.py 恢复 random init（v2/v3 成功配方）。
# - v5 配置 = v2 成功配方（proj_clamp=1.5, var_weight=0.05, grad_clip=0.5, 10000 步零 NaN）
#   + 仅 deep/middle scale 从 1.0 → 0.6（甜点），shallow 保持 0.1（强抑制）。
#
# 甜点依据（find.md §8.2 精细 γ 扫描）：
#   γ=0.6 时 C3 SSIM 0.271 全谱最高；原生 v2 (γ=1.0) 过强 (0.255)。
#
# 变化 vs v4/v5-前: random init（根因修复）+ per-layer train_scale + v2 原配 hyperparams
# 保底措施: 若仍 NaN, 下一方案是 AMP GradScaler (train_v2.py 尚无)

set -e
cd /4T/CXY/MV-Painter

python3 geotex/train_v2.py \
    --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
    --output_dir mvpoutput/geotex_v5_sweetspot \
    --steps 8000 \
    --warmup_steps 800 \
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
    --var_weight 0.05 \
    --train_scale '{"deep":0.6,"middle":0.6,"shallow":0.1}' \
    --proj_clamp 1.5 \
    --device cuda:0 \
    2>&1 | tee mvpoutput/geotex_v5_sweetspot_train.log
