#!/bin/bash
# =============================================================================
# 论文对比图一键 Pipeline
#
# 流程: 高质量推理 → 后处理增强 → 生成对比图
#
# 前置: 确保已安装 lpips, opencv-python
#   pip install lpips opencv-python
# =============================================================================
set -e

# Configuration
CONFIG="/4T/CXY/MV-Painter/MVPainter/configs/mvpainter-geotex-uponly.yaml"
CHECKPOINT="/4T/CXY/MV-Painter/mvpoutput/geotex_checkpoints/geotex_step_0002000.pt"
DEVICE="cuda:0"

# Top showcase objects (by combined FG-LPIPS + FG-SSIM improvement)
# Obj 79: FG-SSIM +0.2566, FG-LPIPS -0.1484 (best combined)
# Obj 72: FG-LPIPS -0.1927 (best perceptual)
# Obj 41: FG-LPIPS -0.1758
# Obj 209: FG-SSIM +0.2401, FG-LPIPS -0.1242
# Obj 43: FG-SSIM +0.2212
# Obj 32: Large object, FG-SSIM +0.2054
# Obj 56: FG-SSIM +0.1899
# Obj 106: FG-LPIPS -0.1160
SHOWCASE_OBJECTS="79,72,41,209,43,32,56,106"

# Output directories
QUALITY_DIR="/4T/CXY/MV-Painter/mvpoutput/quality_showcase"
ENHANCED_DIR="/4T/CXY/MV-Painter/mvpoutput/quality_showcase_enhanced"
FIGURES_DIR="/4T/CXY/MV-Painter/mvpoutput/paper_figures_final"

cd /4T/CXY/MV-Painter

echo "============================================================"
echo "PAPER FIGURES PIPELINE"
echo "============================================================"
echo "Objects: $SHOWCASE_OBJECTS"
echo "Config: $CONFIG"
echo "Checkpoint: $CHECKPOINT"
echo ""

# =============================================================================
# Step 1: High-Quality Inference (multi-seed)
# =============================================================================
echo ""
echo "============================================================"
echo "STEP 1: High-Quality Multi-Seed Inference"
echo "  - 8 seeds per object"
echo "  - 75 steps (vs default 50)"
echo "  - Adapter scales: 1.0, 1.25"
echo "============================================================"

python geotex/quality_inference.py \
    --config "$CONFIG" \
    --checkpoint "$CHECKPOINT" \
    --objects "$SHOWCASE_OBJECTS" \
    --output_dir "$QUALITY_DIR" \
    --device "$DEVICE" \
    --num_seeds 8 \
    --steps 75 \
    --scales "1.0,1.25"

echo "Step 1 DONE: $QUALITY_DIR"

# =============================================================================
# Step 2: Post-Processing Enhancement
# =============================================================================
echo ""
echo "============================================================"
echo "STEP 2: Post-Processing Enhancement"
echo "  - Unsharp mask sharpening"
echo "  - Color histogram matching to reference"
echo "  - CLAHE local contrast"
echo "  - Saturation boost 1.10x"
echo "============================================================"

python geotex/postprocess_for_paper.py \
    --input_dir "$QUALITY_DIR" \
    --output_dir "$ENHANCED_DIR" \
    --mode batch \
    --objects "$SHOWCASE_OBJECTS" \
    --profile paper_standard \
    --enhance_ours_only

echo "Step 2 DONE: $ENHANCED_DIR"

# =============================================================================
# Step 3: Generate Paper Comparison Figures
# =============================================================================
echo ""
echo "============================================================"
echo "STEP 3: Generate Paper-Quality Comparison Figures"
echo "  - GT | Baseline | Ours grid"
echo "  - Auto zoom-in crops (where improvement is largest)"
echo "  - Red/green boxes marking compared regions"
echo "============================================================"

python geotex/generate_paper_comparison.py \
    --input_dir "$ENHANCED_DIR" \
    --output_dir "$FIGURES_DIR" \
    --objects "$SHOWCASE_OBJECTS" \
    --layout standard_with_zooms \
    --source quality_showcase

echo "Step 3 DONE: $FIGURES_DIR"

# =============================================================================
# Also process existing eval visualizations (quick mode, no re-inference)
# =============================================================================
echo ""
echo "============================================================"
echo "BONUS: Enhance existing eval visualizations"
echo "============================================================"

EVAL_VIS="/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations"
EVAL_ENHANCED="/4T/CXY/MV-Painter/mvpoutput/paper_figures_final/enhanced_eval_vis"

if [ -d "$EVAL_VIS" ]; then
    python geotex/postprocess_for_paper.py \
        --input_dir "$EVAL_VIS" \
        --output_dir "$EVAL_ENHANCED" \
        --mode visualizations \
        --profile paper_standard

    # Generate comparison from enhanced eval vis
    python geotex/generate_paper_comparison.py \
        --input_dir "$EVAL_ENHANCED" \
        --output_dir "$FIGURES_DIR/from_eval" \
        --objects "$SHOWCASE_OBJECTS" \
        --layout standard_with_zooms \
        --source eval_vis

    echo "Enhanced eval vis saved: $EVAL_ENHANCED"
fi

echo ""
echo "============================================================"
echo "ALL DONE!"
echo "============================================================"
echo ""
echo "Output locations:"
echo "  Quality inference results: $QUALITY_DIR"
echo "  Enhanced results:          $ENHANCED_DIR"
echo "  Paper figures:             $FIGURES_DIR"
echo ""
echo "Next steps:"
echo "  1. Review $FIGURES_DIR/comparison_grid.png"
echo "  2. Pick the best 4-5 objects for main paper figure"
echo "  3. Use $FIGURES_DIR/comparison_obj_*.png for individual figures"
echo "  4. Check $QUALITY_DIR/quality_summary.json for best seeds/scales"
