#!/bin/bash
# GeoTex v4 训练："甜点 adapter"
#
# 设计理由（find.md §8）：
# - v2 raw norm 太大（deep≈216, shallow≈1255）→ 推理时高 scale 伪影放大
# - v3 raw norm 太小（deep≈4.7, shallow≈131）→ scale 失效 no-op
# - 精细 γ 扫描定位甜点 γ≈0.6 相对 v2 → 目标 raw norm deep≈130, shallow≈750
#
# 策略：在训练时对所有层施加 _adapter_scale=0.6（而非 v3 的 shallow=0.1）,
# 使梯度更小、adapter 自然收敛到更弱 correction。
# 其余训练配置与 v2 相同（稳定训练 10000 步无 NaN）。
# 推理时用标准 LAYER_MAX_SCALES cap + C3 schedule。
#
# 变化 vs v2: 训练时 all_layers _adapter_scale=0.6 (v2 无, v3 shallow=0.1)
# 变化 vs v3: 去掉 var_weight, 去掉 output_proj clamp, 用 v2 LR/steps/accum

set -e
cd /4T/CXY/MV-Painter

python3 geotex/train_v2.py \
    --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
    --output_dir mvpoutput/geotex_v4_sweetspot \
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
    --var_weight 0.0 \
    --train_scale 0.6 \
    --proj_clamp 3.0 \
    --device cuda:0 \
    2>&1 | tee mvpoutput/geotex_v4_sweetspot_train.log
