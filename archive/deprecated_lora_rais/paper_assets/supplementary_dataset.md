# Supplementary Material: Dataset Details

## 1. Training Dataset

LoRA training uses a self-rendered subset of Objaverse, containing **1,200 training objects**. Each object is rendered from **17 viewpoints** at a resolution of **512×512** pixels using Blender Cycles engine.

### 1.1 Data Sources

The training objects are drawn from Objaverse:

| Source | Description | Object Count |
|--------|-------------|--------------|
| Objaverse (self-rendered) | 3D models rendered via custom Blender pipeline | 1,200 |
| **Total** | | **1,200** |

### 1.2 Per-Object Data Structure

Each training object contains the following modalities stored in separate subdirectories:

| Modality | Format | Description |
|----------|--------|-------------|
| `image/` | RGB PNG (with alpha channel, RGBA) | Rendered multi-view images |
| `normal/` | RGB PNG | Surface normal maps |
| `depth_png/` | 16-bit PNG | Depth maps |
| `depth/` | OpenEXR (.exr) | Raw depth values (float32) |
| `camera/` | NumPy array (.npy) | Camera intrinsic/extrinsic parameters |
| `embeddings/` | NumPy array (.npy) | Pre-computed CLIP and DINO global embeddings |

### 1.3 Rendering Configuration

```json
{
  "num_views": 17,
  "resolution": [512, 512],
  "engine": "CYCLES",
  "viewpoint_sampling": "uniform spherical distribution"
}
```

### 1.4 Condition Inputs for LoRA Training

During LoRA training, the following conditions are used as input (replacing text prompts):

- **RGB images** (RGBA with alpha channel): rendered multi-view images
- **Surface normal maps** (RGB PNG): geometric surface orientation
- **Depth maps** (16-bit PNG): per-pixel depth values
- **Pre-computed CLIP/DINO global embeddings**: used as text-prompt replacement for conditioning

---

## 2. Test Dataset

The end-to-end evaluation uses **300 test objects**, each generating **6 target viewpoints**. Test objects are completely disjoint from the training set — no test object participated in LoRA training.

### 2.1 Test Object Selection

Test objects are selected from Objaverse and rendered using the same pipeline as training (Blender Cycles, 512×512). The 300 test objects cover a diverse range of object categories including furniture, vehicles, household items, architectural elements, and organic shapes.

### 2.2 Evaluation Protocol

- **Inference pipeline**: Full MV-Painter pipeline with custom UNet checkpoint, ControlNet, depth conditioning, unified prompts, unified random seeds, unified resolution, and unified denoising configuration
- **Target views**: 6 views per object (subset of the 17 training viewpoints)
- **Metrics**: PSNR, SSIM, LPIPS, CLIP/DINO conditional similarity, multi-view consistency

---

## 3. Train/Test Split Guarantees

| Property | Value |
|----------|-------|
| Train objects | 1,200 |
| Test objects | 300 |
| Overlap | **0** (no shared objects) |
| Test in LoRA training | **Never** (test objects excluded from all training stages) |
| Same preprocessing | Yes (identical render pipeline, resolution, camera setup) |

---

## 4. LoRA Training Configuration (for reproducibility)

For comparability between different target-layer configurations (Full LoRA vs. attn2-only LoRA):

| Parameter | Value |
|-----------|-------|
| LoRA rank | 4 |
| LoRA alpha | 4 |
| Learning rate | 1×10⁻⁵ |
| Batch size | 1 |
| Max training steps | 250 |
| Gradient clipping | 1.0 |
| Drop condition probability | 0.1 |
| Random seed | Fixed across all configurations |
| Training data | Identical across Full/attn2-only |
| Preprocessing | Identical across Full/attn2-only |

---

## 5. Dataset File Listing

The actual dataset files are stored separately and not included in the repository. The following lists provide the complete object IDs for reproducibility.

### 5.1 Training Object IDs (LoRA training)

Total: 1,200 objects

The full list of 1,200 training object IDs is stored in `train_objects_1200.txt`. These objects are sourced from Objaverse and rendered using the custom Blender pipeline described above.

*(See: `train_objects_1200.txt`)*

### 5.2 Test Object IDs (End-to-end evaluation)

Total: 300 objects

The full list of 300 test object IDs is stored in `test_objects_300.txt`. These objects are completely disjoint from the training set.

*(See: `test_objects_300.txt`)*

### 5.3 End-to-End Evaluation Subset (10 objects, detailed)

*(See: `test_objects.txt` in `MVPainter/datalist/`)*

---

## 6. Hook/RAIS Diagnostic Experiments

Hook/RAIS diagnostic experiments use the **same object set and inference pipeline** as end-to-end evaluation. This ensures that internal activation analysis is consistent with the actual generation pathway — diagnostic results reflect real model behavior, not artifacts of a simplified or altered pipeline.

---

## 7. Data Availability

Dataset files are available upon request. The rendering pipeline scripts are included in the repository under `data/train_data/render_all.sh`. Camera parameters and embedding files can be regenerated using the provided scripts.

### 7.1 Data Storage Locations

| Data Type | Location | Status |
|-----------|----------|--------|
| Training objects (1200) | `mvpoutput/paper_assets/train_objects_1200.txt` | 1,200 objects (all valid) |
| Test objects (300) | `mvpoutput/paper_assets/test_objects_300.txt` | 300 objects (all valid) |
| Rendered data | `data/train_data/rendered_full/` | 1,500 valid objects |
| Supplementary document | `mvpoutput/paper_assets/supplementary_dataset.md` | Complete |

### 7.2 Rendering Pipeline

The rendering pipeline is documented in `data/train_data/render_all.sh`. Key parameters:
- Blender Cycles engine
- 17 viewpoints per object
- 512×512 resolution
- RGB + Normal + Depth + Camera + Embeddings
