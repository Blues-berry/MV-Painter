#!/bin/bash
# Run few-shot experiments: 10/30/73 objects × Baseline/Ours

cd /4T/CXY/MV-Painter/MVPainter

# Activate conda environment
source activate mvpainter
export LD_LIBRARY_PATH=/home/ubuntu/ssd_work/conda_envs/mvpainter/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Clean GPU
nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs kill -9 2>/dev/null
sleep 2

echo "=== Starting few-shot experiments ==="
echo "Timestamp: $(date)"

# Run experiments
for n in 10 30 73; do
    echo ""
    echo "=== Experiment: ${n} objects ==="

    # Clean GPU before each run
    nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs kill -9 2>/dev/null
    sleep 3

    # Baseline
    echo "[$(date)] Starting Baseline ${n}..."
    accelerate launch --config_file configs/acc/1gpu_pbr.yaml train_pbr.py --config configs/mvpainter-pbr-baseline-${n}.yaml 2>&1 | tee logs/fewshot_baseline_${n}.log
    echo "[$(date)] Baseline ${n} completed"

    # Clean GPU
    nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs kill -9 2>/dev/null
    sleep 3

    # Ours
    echo "[$(date)] Starting Ours ${n}..."
    accelerate launch --config_file configs/acc/1gpu_pbr.yaml train_pbr.py --config configs/mvpainter-pbr-ours-${n}.yaml 2>&1 | tee logs/fewshot_ours_${n}.log
    echo "[$(date)] Ours ${n} completed"
done

echo ""
echo "=== All experiments completed ==="
echo "Timestamp: $(date)"
