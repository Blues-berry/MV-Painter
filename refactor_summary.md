# Refactor Summary

## New Structure

```
geotex/
├── __init__.py          # Package marker
├── metrics.py           # PSNR, SSIM, edge mask, latent scaling (shared)
├── data_utils.py        # Batch preparation, collation
├── vis_utils.py         # Comparison, error map, region visualization
├── train.py             # Training entry point
├── eval.py              # Evaluation entry point
└── audit.py             # Sanity, leakage, range checks
```

## Key Improvements

### 1. No Hardcoded Paths
All paths via CLI args or config. No more `/4T/CXY/MV-Painter/...` in scripts.

### 2. Shared Utilities
Functions like `compute_psnr`, `compute_ssim`, `scale_latents` defined once in `metrics.py`.
No more copy-paste across scripts.

### 3. Single Entry Points
- `python geotex/train.py --config ...` — one training script
- `python geotex/eval.py --config ...` — one eval script
- `python geotex/audit.py --config ... --check all` — one audit script

### 4. Config-Driven
Eval uses `--config` to load the correct model config. No hardcoded `mvpainter-geotex-uponly.yaml`.

### 5. Structured Output
- `train_metrics.csv` + `train_summary.json` from training
- `per_object_metrics.csv` + `summary_metrics.json` from eval
- `audit_results.json` from audit

### 6. Fair Comparison
Eval ensures: same seed, same scheduler, same init latents, same condition, same view order.
Adapter geo_feats cleared after each forward pass.

## Run Commands

```bash
# Train
python geotex/train.py \
  --config MVPainter/configs/mvpainter-geotex-full-train.yaml \
  --output_dir mvpoutput/geotex \
  --steps 2000 --save_every 500 --device cuda:0

# Eval
python geotex/eval.py \
  --config MVPainter/configs/mvpainter-geotex-full-train.yaml \
  --checkpoint mvpoutput/geotex_checkpoints/geotex_step_0002000.pt \
  --num_objects 50 --device cuda:0

# Audit
python geotex/audit.py \
  --config MVPainter/configs/mvpainter-geotex-full-train.yaml \
  --check all --device cuda:0
```
