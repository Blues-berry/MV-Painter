#!/bin/bash
# Monitor dataset expansion progress

LOG_FILE="/4T/CXY/MV-Painter/mvpoutput/dataset_expansion_v2.log"
OUTPUT_DIR="/4T/CXY/MV-Painter/data/train_data/rendered_full"

echo "=== Dataset Expansion Monitor ==="
echo "Log file: $LOG_FILE"
echo ""

while true; do
    # Count rendered objects
    rendered=0
    total=0
    for dir in "$OUTPUT_DIR"/*/; do
        if [ -d "$dir/image" ]; then
            count=$(ls "$dir/image" 2>/dev/null | wc -l)
            if [ "$count" -ge 17 ]; then
                rendered=$((rendered + 1))
            fi
        fi
        total=$((total + 1))
    done

    # Get log status
    success=$(grep "Success:" "$LOG_FILE" 2>/dev/null | tail -1)
    failed=$(grep "Failed:" "$LOG_FILE" 2>/dev/null | tail -1)

    # Clear line and print status
    echo -ne "\r[$(date +%H:%M:%S)] Rendered: $rendered | Total: $total | $success | $failed    "

    # Check if complete
    if grep -q "RENDERING COMPLETE" "$LOG_FILE" 2>/dev/null; then
        echo ""
        echo ""
        echo "=== RENDERING COMPLETE ==="
        tail -10 "$LOG_FILE"
        break
    fi

    sleep 10
done
