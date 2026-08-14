#!/bin/bash
# GeoTex v5-faithful smoke：验证已复现 v2 训练条件（指纹：step-1 gnorm ≈ 0.0067）
#
# 背景（2026-08-07 诊断，见 find.md）：
# - v4/v5 训练 (train_scale=0.6) 全部 NaN。根因不是 init 也不是 var_loss：
#   v4 传了 var_weight=0 照样炸。共同因子是 train_scale=0.6 —— 低 scale 使
#   corrections 的 L2 正则梯度 ∝ scale² 相对拟合压力 ∝ scale 成比例变弱，
#   adapter 权重失控生长（reg_loss 爆到 100-400）→ 发散。
# - v2 用 TCAS ramp（Phase1 scale=1.0, Phase2-3 ramp 到 TCAS schedule 最高 3.5）
#   训 10000 步零 NaN。γ=0.6 甜点是"强 adapter"在推理时的衰减，不是训练目标。
# - 正确路径：复现 v2 稳定配方 → 推理时 γ=0.6。
#
# 本 smoke 验证：
#   1. 用 v2 精确条件（tcas_ramp + var_weight=0 + proj_clamp=0 + reg=5e-5 +
#      2000 数据 + random init + seed 42 + warmup 1000）
#   2. step-1 gnorm 指纹 ≈ v2 的 0.0067（确认代码/数据/scale 全部对齐）
#   3. 200 步零 NaN，reg_loss 不爬升
set -e
cd /4T/CXY/MV-Painter

python3 geotex/train_v2.py \
    --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
    --output_dir mvpoutput/geotex_v5_faithful_smoke \
    --steps 200 \
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
    2>&1 | tee mvpoutput/geotex_v5_faithful_smoke.log
