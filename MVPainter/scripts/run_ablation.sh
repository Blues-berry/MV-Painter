#!/bin/bash
# Run ablation study with different consistency weights
# Uses GPU 1, 10 objects, 5000 steps each

cd /4T/CXY/MV-Painter/MVPainter
export LD_LIBRARY_PATH=/home/ubuntu/ssd_work/conda_envs/mvpainter/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

CONFIGS=(
  "configs/mvpainter-pbr-ablation-baseline.yaml"
  "configs/mvpainter-pbr-ablation-w0.001.yaml"
  "configs/mvpainter-pbr-ablation-w0.01.yaml"
  "configs/mvpainter-pbr-ablation-w0.05.yaml"
  "configs/mvpainter-pbr-ablation-w0.1.yaml"
  "configs/mvpainter-pbr-ablation-w0.5.yaml"
)

for config in "${CONFIGS[@]}"; do
  name=$(basename "$config" .yaml)
  echo "============================================"
  echo "Starting: $name"
  echo "Config: $config"
  echo "Time: $(date)"
  echo "============================================"

  # Create output dir
  output_dir=$(grep "output_dir:" "$config" | cut -d"'" -f2)
  mkdir -p "$output_dir"

  # Run training
  accelerate launch --num_processes=1 --mixed_precision fp16 train_pbr.py --config "$config" 2>&1 | tee "logs/ablation_${name}.log"

  echo "============================================"
  echo "Completed: $name"
  echo "Time: $(date)"
  echo "============================================"
  echo ""
done

echo "All ablation experiments completed!"
