# model_unet_geotex.py Refactor Plan

## Current State
- File: `MVPainter/mvpainter/model_unet_geotex.py`
- Contains: GeoEncoder, GeoTexAdapter, GeoTexResnetWrapper, MVDiffusionGeoTex (Lightning module), loss functions, checkpoint utilities
- Status: Functional, not refactored

## Proposed Split (Future Work)

### 1. geotex_encoder.py (~100 lines)
- `GeoTexEncoder` class
- Multiscale feature extraction (x1/x2/x3/x4)
- Per-scale projection layers

### 2. geotex_adapter.py (~80 lines)
- `GeoTexAdapter` class (bottleneck residual)
- `GeoTexResnetWrapper` class (UNet injection)
- `inject_adapters()` function

### 3. geotex_losses.py (~50 lines)
- `compute_ssim_loss()`
- `compute_edge_mask()`
- Foreground/edge/SSIM loss logic (currently in `compute_loss`)

### 4. geotex_checkpoint.py (~40 lines)
- `save_geotex_weights()`
- `load_geotex_weights()`
- `GeoTexCheckpointCallback`

### 5. model_unet_geotex.py (~200 lines)
- `MVDiffusionGeoTex` Lightning module
- Imports from above modules
- Training/validation logic

## Risk Assessment
- **Low risk**: Loss functions and checkpoint utils are self-contained
- **Medium risk**: Encoder/adapter split requires careful import management
- **High risk**: Lightning module split could break PL integration

## Recommendation
Do NOT split now. The current code works correctly. Split only if:
1. Multiple people need to work on different components
2. The file exceeds 1000 lines
3. A major refactor is needed for a new feature

## Current Safe Refactors
- Remove unused imports (if any)
- Ensure all paths come from config/CLI
- Add type hints to public functions
- Document loss function parameters
