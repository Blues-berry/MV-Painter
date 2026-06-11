#!/bin/bash
# Run eval ignoring SIGTERM (signal 15)
# Usage: bash geotex/eval_ignoresig.sh

trap '' TERM

PYTHONUNBUFFERED=1 python /4T/CXY/MV-Painter/geotex/eval_safe.py \
  --config /4T/CXY/MV-Painter/mvpoutput/geotex/eval_config_snapshot.yaml \
  --checkpoint /4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt \
  --num_objects 300 \
  --output_dir /4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/eval_300obj_clean \
  --device cuda:1 \
  --steps 50 \
  --seed 42 \
  --save_vis \
  --vis_count 300 \
  > /4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/eval_300obj_clean/eval_log_v7.txt 2>&1

echo "Eval completed with exit code $?"
