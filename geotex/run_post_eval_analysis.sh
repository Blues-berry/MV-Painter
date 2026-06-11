#!/bin/bash
# Run after 300-object eval completes.
# Usage: bash geotex/run_post_eval_analysis.sh

set -e

EVAL_DIR="mvpoutput/geotex_refattn_v1/eval_300obj_clean"

echo "=== Post-Eval Analysis Pipeline ==="
echo "Eval dir: $EVAL_DIR"

# Check if eval completed
if [ ! -f "$EVAL_DIR/summary_metrics.json" ]; then
    echo "ERROR: summary_metrics.json not found. Eval may not be complete."
    exit 1
fi

echo ""
echo "=== Step 1: Performance Analysis ==="
python geotex/analyze_300obj_results.py \
    --metrics_dir "$EVAL_DIR" \
    --output_dir "$EVAL_DIR/analysis"

echo ""
echo "=== Step 2: Comparison Grids ==="
python geotex/make_comparison_grids.py \
    --eval_dir "$EVAL_DIR" \
    --analysis_dir "$EVAL_DIR/analysis" \
    --output_dir "$EVAL_DIR/comparison_grids"

echo ""
echo "=== Step 3: Update README ==="
# Update README_EVAL_VALIDITY.md with actual results
python3 -c "
import json
with open('$EVAL_DIR/summary_metrics.json') as f:
    s = json.load(f)
print('Summary loaded. Regions:')
for k in s:
    if isinstance(s[k], dict) and 'diff' in s[k]:
        print(f'  {k}: diff={s[k][\"diff\"]:+.4f} ({s[k][\"improved\"]}/{s[k][\"total\"]})')
"

echo ""
echo "=== Done ==="
echo "Outputs:"
echo "  $EVAL_DIR/summary_metrics.json"
echo "  $EVAL_DIR/per_object_metrics.csv"
echo "  $EVAL_DIR/region_metrics.csv"
echo "  $EVAL_DIR/analysis/performance_analysis.md"
echo "  $EVAL_DIR/analysis/*.png"
echo "  $EVAL_DIR/comparison_grids/*.png"
