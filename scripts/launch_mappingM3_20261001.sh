#!/bin/bash
# M3 mapping-sensitivity formal runs (pre-registered 2026-10-01).
# GPU0: L-LLH then L-FIX sequentially. GPU1: L-LHL.
set -e
cd /4T/CXY/MV-Painter
BASE_ARGS="--manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --layer-profile final/round2/mv_adapter/layer_profile_transfer_mappingM3.json \
  --split holdout --geometry-source exact --seed 20260928 --steps 50 \
  --low 0.75 --high 1.00"
export HF_HUB_OFFLINE=1
export PYTHONPATH=.
LOG=final/round2/coordination/core7_same_runner_completion_20261001/mappingM3
mkdir -p $LOG
(
  CUDA_VISIBLE_DEVICES=0 python final/round2/mv_adapter/run_layerwise_experiment.py $BASE_ARGS \
    --output-dir final/round2/mv_adapter/results/holdout_exact_mapM3_llh_76 \
    --device cuda:0 --schedule LLH > $LOG/llh.log 2>&1
  CUDA_VISIBLE_DEVICES=0 python final/round2/mv_adapter/run_layerwise_experiment.py $BASE_ARGS \
    --output-dir final/round2/mv_adapter/results/holdout_exact_mapM3_fix_76 \
    --device cuda:0 --schedule FIXED_MEAN > $LOG/fix.log 2>&1
) &
GPU0_PID=$!
(
  CUDA_VISIBLE_DEVICES=1 python final/round2/mv_adapter/run_layerwise_experiment.py $BASE_ARGS \
    --output-dir final/round2/mv_adapter/results/holdout_exact_mapM3_lhl_76 \
    --device cuda:0 --schedule LHL > $LOG/lhl.log 2>&1
) &
GPU1_PID=$!
wait $GPU0_PID $GPU1_PID
echo "M3 runs complete"
