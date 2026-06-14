#!/bin/bash
# Extended scale sweep: 1.60, 1.75, 2.00 (and 2.25, 2.50 if trend continues)
# Uses eval_scale_inline.py (memory-efficient, no baseline caching)

set -e

CONFIG="mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT="mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
OUTPUT_DIR="mvpoutput/geotex_refattn_v1/scale_sweep_v1_extended_50obj"
DEVICE="cuda:0"
NUM_OBJECTS=50
SEED=42

mkdir -p "$OUTPUT_DIR"

cat > "$OUTPUT_DIR/config_snapshot.json" << JSONEOF
{
  "config": "$CONFIG",
  "checkpoint": "$CHECKPOINT",
  "scales": [1.60, 1.75, 2.00],
  "num_objects": $NUM_OBJECTS,
  "steps": 50,
  "seed": $SEED,
  "method": "inline_per_scale",
  "note": "Extended sweep to find peak scale. May add 2.25, 2.50 if trend continues."
}
JSONEOF

echo "=== Extended Scale Sweep ==="
echo "Checkpoint: $CHECKPOINT"
echo "Device: $DEVICE"
echo "Objects: $NUM_OBJECTS"
echo ""

# Phase 1: Run 1.60, 1.75, 2.00
for SCALE in 1.60 1.75 2.00; do
    SCALE_NAME=$(echo "$SCALE" | sed 's/\./p/')
    SCALE_DIR="$OUTPUT_DIR/scale_${SCALE_NAME}"

    echo "=========================================="
    echo "Running scale=$SCALE → $SCALE_DIR"
    echo "=========================================="

    if [ -f "$SCALE_DIR/per_object_metrics.csv" ]; then
        echo "  Already exists, skipping."
        continue
    fi

    python geotex/eval_scale_inline.py \
        --config "$CONFIG" \
        --checkpoint "$CHECKPOINT" \
        --scale "$SCALE" \
        --num_objects "$NUM_OBJECTS" \
        --output_dir "$SCALE_DIR" \
        --device "$DEVICE" \
        --seed "$SEED"

    echo "  Done: scale=$SCALE"
    echo ""
done

# Phase 2: Check if we should continue to 2.25, 2.50
echo "=========================================="
echo "Checking trend: should we continue to 2.25, 2.50?"
echo "=========================================="

python3 << 'PYEOF'
import csv, numpy as np, os

# Load all available scale data (including from previous sweep)
prev_dir = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_50obj"
ext_dir = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_extended_50obj"

all_data = {}
for base in [prev_dir, ext_dir]:
    if not os.path.exists(base):
        continue
    for d in sorted(os.listdir(base)):
        path = f'{base}/{d}/per_object_metrics.csv'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            rows = list(csv.DictReader(f))
        scale = float(rows[0]['scale'])
        all_data[scale] = rows

scales = sorted(all_data.keys())
fg_means = []
for s in scales:
    vals = [float(r['delta_fg_ssim']) for r in all_data[s]]
    fg_means.append((s, np.mean(vals)))

print("\nFG SSIM trend:")
for s, m in fg_means:
    print(f"  s={s:.2f}: {m:+.4f}")

# Check last 3 scales
if len(fg_means) >= 3:
    last3 = fg_means[-3:]
    deltas = [last3[i+1][1] - last3[i][1] for i in range(len(last3)-1)]
    print(f"\nLast deltas: {[f'{d:+.4f}' for d in deltas]}")
    if all(d < 0.003 for d in deltas):
        print("STOP: gains < 0.003 per step — peak reached or plateau")
        with open(f"{ext_dir}/trend_decision.txt", "w") as f:
            f.write("STOP: gains < 0.003 per step\n")
    elif deltas[-1] < 0:
        print("STOP: last delta negative — peak passed")
        with open(f"{ext_dir}/trend_decision.txt", "w") as f:
            f.write("STOP: last delta negative\n")
    else:
        print("CONTINUE: trend still positive, adding 2.25 and 2.50")
        with open(f"{ext_dir}/trend_decision.txt", "w") as f:
            f.write("CONTINUE\n")
PYEOF

# Phase 3: Continue if needed
DECISION="STOP"
if [ -f "$OUTPUT_DIR/trend_decision.txt" ]; then
    DECISION=$(cat "$OUTPUT_DIR/trend_decision.txt" | head -1)
fi

if [[ "$DECISION" == CONTINUE* ]]; then
    echo ""
    echo "Trend still positive. Running 2.25 and 2.50..."
    for SCALE in 2.25 2.50; do
        SCALE_NAME=$(echo "$SCALE" | sed 's/\./p/')
        SCALE_DIR="$OUTPUT_DIR/scale_${SCALE_NAME}"

        echo "=========================================="
        echo "Running scale=$SCALE → $SCALE_DIR"
        echo "=========================================="

        if [ -f "$SCALE_DIR/per_object_metrics.csv" ]; then
            echo "  Already exists, skipping."
            continue
        fi

        python geotex/eval_scale_inline.py \
            --config "$CONFIG" \
            --checkpoint "$CHECKPOINT" \
            --scale "$SCALE" \
            --num_objects "$NUM_OBJECTS" \
            --output_dir "$SCALE_DIR" \
            --device "$DEVICE" \
            --seed "$SEED"

        echo "  Done: scale=$SCALE"
        echo ""
    done
fi

echo "=========================================="
echo "Generating summary..."
echo "=========================================="

python3 << 'PYEOF'
import csv, numpy as np, os, json

ext_dir = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_extended_50obj"
prev_dir = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_50obj"

# Load all data
all_data = {}
for base in [prev_dir, ext_dir]:
    if not os.path.exists(base):
        continue
    for d in sorted(os.listdir(base)):
        path = f'{base}/{d}/per_object_metrics.csv'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            rows = list(csv.DictReader(f))
        scale = float(rows[0]['scale'])
        all_data[scale] = rows

scales = sorted(all_data.keys())
metrics = ['delta_fg_ssim', 'delta_nef_ssim', 'delta_edge_ssim', 'delta_crop_ssim',
           'delta_crop_lpips', 'delta_full_psnr']

# Generate combined CSV
with open(f"{ext_dir}/extended_per_object_scale_sweep.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['object_idx', 'scale', 'fg_ratio'] + metrics)
    for s in scales:
        for r in all_data[s]:
            row = [r['object_idx'], s, r.get('fg_ratio', '')]
            for m in metrics:
                row.append(r.get(m, ''))
            writer.writerow(row)

# Generate summary CSV
with open(f"{ext_dir}/extended_scale_sweep_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['scale', 'num_objects'] + [f'{m}_mean' for m in metrics] +
                     [f'{m}_median' for m in metrics] + [f'{m}_positive' for m in metrics])
    for s in scales:
        rows = all_data[s]
        n = len(rows)
        row = [s, n]
        for m in metrics:
            vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
            row.append(np.mean(vals) if vals else '')
        for m in metrics:
            vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
            row.append(np.median(vals) if vals else '')
        for m in metrics:
            vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
            row.append(sum(1 for v in vals if v > 0) if vals else '')
        writer.writerow(row)

# Generate summary markdown
with open(f"{ext_dir}/extended_scale_sweep_summary.md", "w") as f:
    f.write("# Extended Scale Sweep Summary\n\n")
    f.write("**Date:** 2026-06-13\n")
    f.write("**Checkpoint:** v1 geotex_step_0002000.pt\n")
    f.write("**Method:** eval_scale_inline.py\n\n")

    f.write("## All Scales\n\n")
    f.write("| Scale | FG SSIM | NEF SSIM | Edge SSIM | Crop SSIM | Crop LPIPS | PSNR | FG pos |\n")
    f.write("|-------|---------|----------|-----------|-----------|------------|------|--------|\n")
    for s in scales:
        rows = all_data[s]
        n = len(rows)
        def fmt(m):
            vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
            return f"{np.mean(vals):+.4f}" if vals else "N/A"
        def pos(m):
            vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
            return f"{sum(1 for v in vals if v > 0)}/{n}" if vals else ""
        f.write(f"| {s:.2f} | {fmt('delta_fg_ssim')} | {fmt('delta_nef_ssim')} | "
                f"{fmt('delta_edge_ssim')} | {fmt('delta_crop_ssim')} | {fmt('delta_crop_lpips')} | "
                f"{fmt('delta_full_psnr')} | {pos('delta_fg_ssim')} |\n")

    # Find best scale
    best_fg = max(scales, key=lambda s: np.mean([float(r['delta_fg_ssim']) for r in all_data[s]]))
    best_nef = max(scales, key=lambda s: np.mean([float(r['delta_nef_ssim']) for r in all_data[s]]))
    f.write(f"\n## Best Scale\n\n")
    f.write(f"- **FG SSIM:** s={best_fg:.2f}\n")
    f.write(f"- **NEF SSIM:** s={best_nef:.2f}\n")

    # Trend analysis
    f.write(f"\n## Trend\n\n")
    fg_means = [(s, np.mean([float(r['delta_fg_ssim']) for r in all_data[s]])) for s in scales]
    for i in range(1, len(fg_means)):
        delta = fg_means[i][1] - fg_means[i-1][1]
        f.write(f"- s={fg_means[i-1][0]:.2f} → s={fg_means[i][0]:.2f}: ΔFG = {delta:+.4f}\n")

print(f"Saved: extended_scale_sweep_summary.md, .csv, extended_per_object_scale_sweep.csv")
PYEOF

echo ""
echo "Extended scale sweep complete!"
