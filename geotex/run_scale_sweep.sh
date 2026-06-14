#!/bin/bash
# Scale sweep using memory-efficient inline eval (one scale at a time)
# Usage: bash geotex/run_scale_sweep.sh

set -e

CONFIG="mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT="mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
OUTPUT_DIR="mvpoutput/geotex_refattn_v1/scale_sweep_v1_50obj"
DEVICE="cuda:0"
NUM_OBJECTS=50
SEED=42
SCALES="0.75 0.9 1.0 1.1 1.15 1.25 1.35 1.5"

mkdir -p "$OUTPUT_DIR"

echo "Starting scale sweep: $SCALES"
echo "Config: $CONFIG"
echo "Checkpoint: $CHECKPOINT"
echo "Device: $DEVICE"
echo "Objects: $NUM_OBJECTS"
echo ""

# Save config snapshot
cat > "$OUTPUT_DIR/config_snapshot.json" << JSONEOF
{
  "config": "$CONFIG",
  "checkpoint": "$CHECKPOINT",
  "scales": [0.75, 0.9, 1.0, 1.1, 1.15, 1.25, 1.35, 1.5],
  "num_objects": $NUM_OBJECTS,
  "steps": 50,
  "seed": $SEED,
  "method": "inline_per_scale"
}
JSONEOF

for SCALE in $SCALES; do
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

echo "All scales complete."
echo "Now run summary generation..."
python3 << 'PYEOF'
import os, json, csv, numpy as np

output_dir = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_50obj"
all_scales = {}

for d in sorted(os.listdir(output_dir)):
    if not d.startswith("scale_"):
        continue
    csv_path = os.path.join(output_dir, d, "per_object_metrics.csv")
    if not os.path.exists(csv_path):
        continue
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    scale = float(rows[0]["scale"])
    summary = {"scale": scale, "num_objects": len(rows)}
    for col in rows[0].keys():
        if col in ("object_idx", "scale", "fg_ratio"):
            continue
        try:
            vals = [float(r[col]) for r in rows if r.get(col) and r[col] != "None"]
        except (ValueError, TypeError):
            continue
        if vals:
            arr = np.array(vals)
            pos = int(np.sum(arr > 0)) if "delta" in col else None
            summary[col] = {"mean": float(arr.mean()), "std": float(arr.std()),
                            "positive": pos, "total": len(arr)}
    all_scales[str(scale)] = summary
    print(f"\nScale {scale}:")
    for m in ["delta_fg_ssim", "delta_nef_ssim", "delta_edge_ssim", "delta_crop_ssim",
              "delta_crop_lpips", "delta_full_psnr"]:
        if m in summary:
            s = summary[m]
            print(f"  {m:25s}: {s['mean']:+.4f} [{s.get('positive','?')}/{s['total']}]")

with open(os.path.join(output_dir, "all_scales_summary.json"), "w") as f:
    json.dump(all_scales, f, indent=2, default=str)

# Generate summary CSV
with open(os.path.join(output_dir, "scale_sweep_summary.csv"), "w", newline="") as f:
    metrics = ["delta_fg_ssim", "delta_nef_ssim", "delta_edge_ssim", "delta_crop_ssim",
               "delta_crop_lpips", "delta_full_psnr", "delta_fg_lpips", "delta_bgwhite_ssim"]
    writer = csv.writer(f)
    writer.writerow(["scale", "num_objects"] + [f"{m}_mean" for m in metrics] +
                     [f"{m}_positive" for m in metrics])
    for scale_str, summary in sorted(all_scales.items(), key=lambda x: float(x[0])):
        row = [summary["scale"], summary["num_objects"]]
        for m in metrics:
            row.append(summary.get(m, {}).get("mean", ""))
        for m in metrics:
            row.append(summary.get(m, {}).get("positive", ""))
        writer.writerow(row)

# Generate summary markdown
with open(os.path.join(output_dir, "scale_sweep_summary.md"), "w") as f:
    f.write("# V1 Scale Sweep Summary (50 objects)\n\n")
    f.write("| Scale | FG SSIM | NEF SSIM | Edge SSIM | Crop SSIM | Crop LPIPS | Full PSNR | FG pos | NEF pos |\n")
    f.write("|-------|---------|----------|-----------|-----------|------------|-----------|--------|--------|\n")
    for scale_str, summary in sorted(all_scales.items(), key=lambda x: float(x[0])):
        def fmt(m):
            s = summary.get(m, {})
            if not s: return "N/A"
            return f"{s['mean']:+.4f}"
        def pos(m):
            s = summary.get(m, {})
            if not s or s.get("positive") is None: return ""
            return f"{s['positive']}/{s['total']}"
        f.write(f"| {summary['scale']:.2f} | {fmt('delta_fg_ssim')} | {fmt('delta_nef_ssim')} | "
                f"{fmt('delta_edge_ssim')} | {fmt('delta_crop_ssim')} | {fmt('delta_crop_lpips')} | "
                f"{fmt('delta_full_psnr')} | {pos('delta_fg_ssim')} | {pos('delta_nef_ssim')} |\n")

print("\nSaved: all_scales_summary.json, scale_sweep_summary.csv, scale_sweep_summary.md")
PYEOF
echo "Scale sweep complete!"
