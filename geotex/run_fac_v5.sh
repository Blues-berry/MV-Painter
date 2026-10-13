#!/bin/bash
# fac_v5: three mechanism-distinct FAC attempts (all strictly paired eval, 300 obj / 50 steps / seed 42).
#   A (GPU0): joint LTAG+GSG+FSC with envelope penalty lambda=1.0 (gate stays near C3, small deviations allowed)
#   C (GPU1): frozen-LTAG + fidelity-weighted objective (fg_weight 1.0, ssim_weight 0.5)
#   F (GPU0, after A): frozen-LTAG + gentle schedule (500 steps, peak_lr 2.5e-5)
# Success criterion: fg_psnr >= TCAS baseline 19.12 (fg_ssim 0.3708).
cd /4T/CXY/MV-Painter || exit 1
mkdir -p mvpoutput/fac_v5
BASE=mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt

chain_a() {
  OUT=mvpoutput/fac_v5/A_envpen
  CUDA_VISIBLE_DEVICES=0 python geotex/train_fac_v2.py \
    --base_checkpoint $BASE --output_dir "$OUT" \
    --enable_ltag --enable_gsg --enable_fsc \
    --envelope_penalty 1.0 --steps 2000 --device cuda:0 \
    > mvpoutput/fac_v5/A_train.log 2>&1 || { echo A_TRAIN_FAILED; return 1; }
  CKPT=$(ls -t "$OUT"/checkpoints/*.pt | head -1)
  CUDA_VISIBLE_DEVICES=0 python geotex/eval_fac_v2.py --checkpoint "$CKPT" \
    --output_dir "$OUT/eval_300" --num_objects 300 --num_steps 50 --device cuda:0 \
    > mvpoutput/fac_v5/A_eval.log 2>&1
  echo "A_DONE"
}

chain_c() {
  OUT=mvpoutput/fac_v5/C_fidw
  CUDA_VISIBLE_DEVICES=1 python geotex/train_fac_v2.py \
    --base_checkpoint $BASE --output_dir "$OUT" \
    --enable_ltag --enable_gsg --enable_fsc --freeze_ltag \
    --fg_weight 1.0 --ssim_weight 0.5 --steps 2000 --device cuda:1 \
    > mvpoutput/fac_v5/C_train.log 2>&1 || { echo C_TRAIN_FAILED; return 1; }
  CKPT=$(ls -t "$OUT"/checkpoints/*.pt | head -1)
  CUDA_VISIBLE_DEVICES=1 python geotex/eval_fac_v2.py --checkpoint "$CKPT" \
    --output_dir "$OUT/eval_300" --num_objects 300 --num_steps 50 --device cuda:1 \
    > mvpoutput/fac_v5/C_eval.log 2>&1
  echo "C_DONE"
}

chain_f() {
  OUT=mvpoutput/fac_v5/F_gentle
  CUDA_VISIBLE_DEVICES=0 python geotex/train_fac_v2.py \
    --base_checkpoint $BASE --output_dir "$OUT" \
    --enable_ltag --enable_gsg --enable_fsc --freeze_ltag \
    --steps 500 --peak_lr 2.5e-5 --device cuda:0 \
    > mvpoutput/fac_v5/F_train.log 2>&1 || { echo F_TRAIN_FAILED; return 1; }
  CKPT=$(ls -t "$OUT"/checkpoints/*.pt | head -1)
  CUDA_VISIBLE_DEVICES=0 python geotex/eval_fac_v2.py --checkpoint "$CKPT" \
    --output_dir "$OUT/eval_300" --num_objects 300 --num_steps 50 --device cuda:0 \
    > mvpoutput/fac_v5/F_eval.log 2>&1
  echo "F_DONE"
}

chain_a & APID=$!
chain_c & CPID=$!
wait $CPID; chain_f; FPID=$!
wait $APID; wait $FPID
echo "ALL_CHAINS_DONE"
