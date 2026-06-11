#!/bin/bash
# Run 300-object eval in small batches to survive SIGKILL.
# Each batch processes 20 objects, saves results, then exits.
# Next batch picks up from where the last one stopped.
#
# Usage: nohup bash geotex/eval_batch.sh &

set -e

CONFIG="mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT="mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
OUTPUT_DIR="mvpoutput/geotex_refattn_v1/eval_300obj_clean"
DEVICE="cuda:1"
STEPS=50
SEED=42
BATCH_SIZE=20
TOTAL=300

LOG="$OUTPUT_DIR/batch_runner.log"

echo "$(date): Starting batch eval" | tee -a "$LOG"

for START in $(seq 0 $BATCH_SIZE $((TOTAL - 1))); do
    END=$((START + BATCH_SIZE))
    if [ $END -gt $TOTAL ]; then END=$TOTAL; fi

    # Check if already done
    EXISTING=0
    if [ -f "$OUTPUT_DIR/per_object_metrics_partial.csv" ]; then
        EXISTING=$(python3 -c "
import csv
with open('$OUTPUT_DIR/per_object_metrics_partial.csv') as f:
    print(sum(1 for _ in csv.DictReader(f)))
" 2>/dev/null || echo 0)
    fi

    if [ "$EXISTING" -ge "$END" ]; then
        echo "$(date): Batch $START-$END already done ($EXISTING results), skipping" | tee -a "$LOG"
        continue
    fi

    echo "$(date): Running batch $START-$END ($EXISTING existing results)" | tee -a "$LOG"

    PYTHONUNBUFFERED=1 python geotex/eval_safe.py \
        --config "$CONFIG" \
        --checkpoint "$CHECKPOINT" \
        --num_objects "$END" \
        --output_dir "$OUTPUT_DIR" \
        --device "$DEVICE" \
        --steps "$STEPS" \
        --seed "$SEED" \
        --save_vis \
        --vis_count 300 \
        >> "$LOG" 2>&1

    EXIT_CODE=$?
    echo "$(date): Batch $START-$END exited with code $EXIT_CODE" | tee -a "$LOG"

    # Check how many we have now
    DONE=$(python3 -c "
import csv
with open('$OUTPUT_DIR/per_object_metrics_partial.csv') as f:
    print(sum(1 for _ in csv.DictReader(f)))
" 2>/dev/null || echo 0)
    echo "$(date): Total results: $DONE" | tee -a "$LOG"

    if [ "$DONE" -ge "$TOTAL" ]; then
        echo "$(date): All $TOTAL objects done!" | tee -a "$LOG"
        break
    fi
done

echo "$(date): Batch eval complete" | tee -a "$LOG"
