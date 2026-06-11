#!/bin/bash
# Batch runner for scale sweep. Runs one scale at a time to survive SIGKILL.
# Usage: nohup bash geotex/eval_scale_sweep_batch.sh &

set -e

CONFIG="mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT="mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
OUTPUT_DIR="mvpoutput/geotex_refattn_v1/scale_sweep_50obj"
DEVICE="cuda:1"
STEPS=50
SEED=42
NUM_OBJECTS=50
LOG="$OUTPUT_DIR/batch_sweep.log"

SCALES="0.25 0.5 0.75 1.0 1.25"

echo "$(date): Starting scale sweep batch" | tee -a "$LOG"

for SCALE in $SCALES; do
    SCALE_NAME=$(printf "scale_%.2f" $SCALE | sed 's/\./p/')
    SCALE_DIR="$OUTPUT_DIR/$SCALE_NAME"

    # Check if already done
    if [ -f "$SCALE_DIR/summary_metrics.json" ]; then
        DONE=$(python3 -c "import json; s=json.load(open('$SCALE_DIR/summary_metrics.json')); print(s.get('num_objects',0))" 2>/dev/null || echo 0)
        if [ "$DONE" -ge "$NUM_OBJECTS" ]; then
            echo "$(date): Scale $SCALE already done ($DONE objects), skipping" | tee -a "$LOG"
            continue
        fi
    fi

    echo "$(date): Running scale $SCALE ($NUM_OBJECTS objects)" | tee -a "$LOG"

    PYTHONUNBUFFERED=1 python geotex/eval_scale_sweep_v2.py \
        --config "$CONFIG" \
        --checkpoint "$CHECKPOINT" \
        --scales "$SCALE" \
        --num_objects "$NUM_OBJECTS" \
        --output_dir "$OUTPUT_DIR" \
        --device "$DEVICE" \
        --steps "$STEPS" \
        --seed "$SEED" \
        >> "$LOG" 2>&1

    EXIT_CODE=$?
    echo "$(date): Scale $SCALE exited with code $EXIT_CODE" | tee -a "$LOG"
done

echo "$(date): Scale sweep batch complete" | tee -a "$LOG"
