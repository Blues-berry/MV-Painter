# PBR Baseline Documentation

## Training Configuration
```yaml
# configs/mvpainter-pbr-train-mvpainter.yaml
pretrained_model_name_or_path: lizb6626/IDArb
pretrained_unet_path: lizb6626/IDArb
img_wh: [256, 256]
train_batch_size: 1
gradient_accumulation_steps: 2
max_train_steps: 10000
learning_rate: 5e-6
lr_scheduler: constant_with_warmup
lr_warmup_steps: 100
mixed_precision: fp16
gradient_checkpointing: true
use_ema: true
num_views: 2
dataloader_num_workers: 0
enable_xformers_memory_efficient_attention: false
checkpointing_steps: 500
```

## Environment
- GPU: RTX 5090 (31.4 GB VRAM)
- PyTorch: 2.7.0+cu128
- diffusers: 0.20.2 (patched for num_d compatibility)
- Python: 3.10.20

## Training Results
- **Total steps**: 29,731 (accumulated across gradient accumulation)
- **Initial loss**: 0.0062
- **Final loss**: 0.0167
- **Min loss**: 0.0001
- **Max loss**: 9.93
- **Mean loss**: 0.1187
- **Loss spikes (>1.0)**: 384 out of 29,731 steps (1.29%)

## GPU Memory Usage
- **Peak VRAM**: ~28 GB / 31.4 GB (89%)
- **Stable VRAM**: ~24 GB / 31.4 GB (76%)

## Checkpoints Saved
- checkpoint-9000
- checkpoint-9500
- checkpoint-10000

## Loss Spike Analysis
Loss spikes (>1.0) occur throughout training:
- 384 spikes out of 29,731 steps (1.29%)
- Spike magnitude: 1.0 ~ 9.93
- Spikes appear in clusters, suggesting certain objects/views cause instability
- Most spikes recover quickly (within 1-2 steps)

## Key Observations
1. Training converges but with significant loss spikes
2. Loss spikes likely caused by:
   - Cross-view inconsistency in PBR predictions
   - Single-view overfitting
   - Lack of multi-view consistency constraints
3. This baseline provides a clear target for improvement

## Files
- Loss curve: `output/baseline_loss_curve.txt`
- Config: `configs/mvpainter-pbr-train-mvpainter.yaml`
- Logs: `logs/pbr_train8.log`
