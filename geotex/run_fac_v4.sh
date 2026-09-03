#!/bin/bash
# fac_v4: two-stage envelope-preserving FAC.
# LTAG is warm-started to the exact C3 envelope and FROZEN; only GSG/FSC train.
# Goal: test whether envelope-preserving learned refinement can reach/approach
# the originally reported FAC gains (Full FAC > TCAS baseline 19.12/0.3708).
cd /4T/CXY/MV-Painter || exit 1
mkdir -p mvpoutput/fac_v4_frozen
OUT=mvpoutput/fac_v4_frozen/full

CUDA_VISIBLE_DEVICES=0 python geotex/train_fac_v2.py \
  --base_checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
  --output_dir "$OUT" \
  --enable_ltag --enable_gsg --enable_fsc --freeze_ltag \
  --steps 2000 --save_every 500 \
  --device cuda:0 \
  > mvpoutput/fac_v4_frozen/full_train.log 2>&1 || { echo TRAIN_FAILED; exit 1; }

CKPT=$(ls -t "$OUT"/checkpoints/*.pt 2>/dev/null | head -1)
[ -z "$CKPT" ] && { echo NO_CHECKPOINT; exit 1; }
echo "Evaluating $CKPT"

CUDA_VISIBLE_DEVICES=0 python geotex/eval_fac_v2.py \
  --checkpoint "$CKPT" \
  --output_dir "$OUT/eval_300" \
  --num_objects 300 --num_steps 50 \
  --device cuda:0 \
  > mvpoutput/fac_v4_frozen/full_eval.log 2>&1

echo "DONE. Baseline TCAS: fg_psnr 19.12 / fg_ssim 0.3708"
python3 -c "
import json; m=json.load(open('$OUT/eval_300/summary.json'))['metrics']
print('fac_v4 frozen-LTAG full FAC: fg_psnr %.2f / fg_ssim %.4f' % (m['fg_psnr']['mean'], m['fg_ssim']['mean']))"
