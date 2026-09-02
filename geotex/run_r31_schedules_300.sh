#!/bin/bash
# R3.1 revision experiment: evaluate the reviewer-named generic schedules
# (cosine bump + linear warm-up) on the full 300-object pool.
# Protocol identical to revision_top2_300 / revision_schedule_comparison:
#   geotex_v2 EMA checkpoint, capped forward, EulerDiscreteScheduler,
#   50 steps, seed 42, shared initial latents, 6 views @ 256.
#
# One schedule per GPU, run in parallel. Launch from /4T/CXY/MV-Painter with
# the SAME python env used for the previous revision runs (anaconda3 base,
# torch 2.7.1+cu128):
#   bash geotex/run_r31_schedules_300.sh
# Outputs:
#   mvpoutput/revision_schedules_300/cosine_bump/per_object_results.csv
#   mvpoutput/revision_schedules_300/linear_warmup/per_object_results.csv
# Then feed both CSVs into geotex/analyze_holdout_split.py-style analysis
# (extend it to these two files) for the disjoint 276-object holdout stats.

cd /4T/CXY/MV-Painter || exit 1
mkdir -p mvpoutput/revision_schedules_300

CUDA_VISIBLE_DEVICES=0 nohup python geotex/eval_schedule_comparison.py \
  --schedules cosine_bump \
  --num_objects 300 \
  --num_steps 50 \
  --device cuda:0 \
  --output_dir mvpoutput/revision_schedules_300/cosine_bump \
  > mvpoutput/revision_schedules_300/cosine_bump.log 2>&1 &
echo "cosine_bump on GPU0, pid $!"

CUDA_VISIBLE_DEVICES=1 nohup python geotex/eval_schedule_comparison.py \
  --schedules linear_warmup \
  --num_objects 300 \
  --num_steps 50 \
  --device cuda:0 \
  --output_dir mvpoutput/revision_schedules_300/linear_warmup \
  > mvpoutput/revision_schedules_300/linear_warmup.log 2>&1 &
echo "linear_warmup on GPU1, pid $!"

echo "Monitor: tail -f mvpoutput/revision_schedules_300/*.log"
