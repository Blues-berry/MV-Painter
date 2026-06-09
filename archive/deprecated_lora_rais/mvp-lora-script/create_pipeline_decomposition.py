"""
Create MV-Painter Pipeline Decomposition Figure.

Shows the complete flow from input to output with intermediate stages:
1. Input: Condition Image
2. UNet Write Pass: Reference Feature Storage
3. UNet Read Pass: Multi-view Generation
4. Output: 6-view Results
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# Set style
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'figure.dpi': 300,
    'savefig.dpi': 300,
})

# Colors
COLORS = {
    'input': '#E3F2FD',  # Light blue
    'write': '#FFF3E0',  # Light orange
    'read': '#E8F5E9',   # Light green
    'output': '#F3E5F5', # Light purple
    'arrow': '#424242',
    'text': '#212121',
    'highlight': '#FF5722',
}


def load_condition_image(obj_id='d6a5427888b8413fbfcbcaad14353af8'):
    """Load a real condition image."""
    img_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
    if os.path.exists(img_path):
        img = Image.open(img_path).convert('RGB')
        # Resize to 128x128 for visualization
        img = img.resize((128, 128), Image.LANCZOS)
        return img
    else:
        # Create placeholder
        img = Image.new('RGB', (128, 128), (200, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.text((30, 50), "Input", fill=(0, 0, 0))
        return img


def load_output_views(obj_id='d6a5427888b8413fbfcbcaad14353af8'):
    """Load real output views."""
    views = []
    img_dir = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image'

    for i in range(6):
        img_path = os.path.join(img_dir, f'{i:03d}.png')
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB')
            img = img.resize((96, 96), Image.LANCZOS)
            views.append(img)
        else:
            img = Image.new('RGB', (96, 96), (200, 200, 200))
            views.append(img)

    return views


def create_feature_heatmap(size=(128, 128), style='stored'):
    """Create a synthetic feature heatmap visualization."""
    np.random.seed(42)

    if style == 'stored':
        # Stored reference features - structured pattern
        x, y = np.meshgrid(np.linspace(0, 1, size[0]), np.linspace(0, 1, size[1]))
        data = np.sin(2 * np.pi * x) * np.cos(2 * np.pi * y) * 0.5 + 0.5
        data += np.random.normal(0, 0.1, size)
        data = np.clip(data, 0, 1)
    elif style == 'attention':
        # Attention map - focused pattern
        x, y = np.meshgrid(np.linspace(-1, 1, size[0]), np.linspace(-1, 1, size[1]))
        data = np.exp(-(x**2 + y**2) / 0.5)
        data += np.random.normal(0, 0.05, size)
        data = np.clip(data, 0, 1)
    else:
        data = np.random.rand(*size)

    # Convert to RGB heatmap
    cmap = plt.cm.viridis
    colored = cmap(data)
    return Image.fromarray((colored[:, :, :3] * 255).astype(np.uint8))


def create_attn_diagram(size=(128, 128), layer_type='attn1'):
    """Create attention mechanism diagram."""
    img = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    if layer_type == 'attn1':
        # Self-Attention + Reference Storage
        draw.rectangle([10, 10, 60, 50], fill='#2196F3', outline='#1565C0')
        draw.text((15, 20), 'Q', fill='white')

        draw.rectangle([70, 10, 120, 50], fill='#2196F3', outline='#1565C0')
        draw.text((80, 20), 'K', fill='white')

        draw.rectangle([40, 65, 90, 105], fill='#FF9800', outline='#E65100')
        draw.text((50, 75), 'V', fill='white')

        # Arrow from V to storage
        draw.line([(65, 105), (65, 120)], fill='#424242', width=2)
        draw.text((30, 110), 'ref_dict', fill='#E65100')

    elif layer_type == 'attn2':
        # Cross-Attention
        draw.rectangle([10, 10, 60, 50], fill='#4CAF50', outline='#2E7D32')
        draw.text((15, 20), 'Q', fill='white')

        draw.rectangle([70, 10, 120, 50], fill='#9C27B0', outline='#6A1B9A')
        draw.text((75, 20), 'K/V', fill='white')

        draw.text((20, 65), 'Text/Img', fill='#424242')
        draw.text((20, 80), 'Embeddings', fill='#424242')

    return img


def add_box(ax, x, y, w, h, color, label, fontsize=9):
    """Add a rounded box with label."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                         facecolor=color, edgecolor='#757575', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=COLORS['text'])


def add_arrow(ax, start, end, color='#424242'):
    """Add an arrow between two points."""
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=2))


def create_pipeline_figure(output_path):
    """Create the main pipeline decomposition figure."""
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # ============ Stage 1: Input ============
    # Background box
    add_box(ax, 0.5, 3, 3, 4, COLORS['input'], '', fontsize=8)
    ax.text(2, 7.3, 'Input', ha='center', fontsize=12, fontweight='bold', color='#1565C0')

    # Load and display condition image
    cond_img = load_condition_image()
    img_array = np.array(cond_img)
    ax.imshow(img_array, extent=[1, 2.5, 4, 5.5], aspect='auto', zorder=5)
    ax.text(1.75, 3.5, 'Condition\nImage', ha='center', fontsize=9, style='italic')

    # ============ Stage 2: UNet Write Pass ============
    add_box(ax, 4, 1, 5.5, 7, COLORS['write'], '', fontsize=8)
    ax.text(6.75, 8.3, 'UNet Write Pass', ha='center', fontsize=12, fontweight='bold', color='#E65100')
    ax.text(6.75, 7.8, '(Condition Processing)', ha='center', fontsize=9, style='italic')

    # attn1 layers
    add_box(ax, 4.5, 5, 2, 1.5, '#2196F3', 'attn1\n(Self-Attn)', fontsize=9)
    ax.text(5.5, 6.7, 'Write mode', ha='center', fontsize=8, color='#E65100')

    # attn2 layers
    add_box(ax, 4.5, 2.5, 2, 1.5, '#4CAF50', 'attn2\n(Cross-Attn)', fontsize=9)

    # FFN
    add_box(ax, 7, 3.75, 2, 1.5, '#9E9E9E', 'FFN\n(Feed-Forward)', fontsize=9)

    # Reference Dictionary
    add_box(ax, 7, 5.5, 2, 1.5, '#FF9800', 'ref_dict\n(Storage)', fontsize=9)
    ax.text(8, 7.2, 'Reference\nFeatures', ha='center', fontsize=8, color='#E65100', style='italic')

    # Arrows in Write Pass
    add_arrow(ax, (3.5, 5), (4.5, 5.75))  # Input -> attn1
    add_arrow(ax, (6.5, 5.75), (7, 6.25))  # attn1 -> ref_dict

    # ============ Stage 3: Denoising Loop ============
    add_box(ax, 10, 1, 5.5, 7, COLORS['read'], '', fontsize=8)
    ax.text(12.75, 8.3, 'UNet Read Pass', ha='center', fontsize=12, fontweight='bold', color='#2E7D32')
    ax.text(12.75, 7.8, '(Multi-view Generation)', ha='center', fontsize=9, style='italic')

    # attn1 with reference
    add_box(ax, 10.5, 5, 2, 1.5, '#2196F3', 'attn1\n(Read mode)', fontsize=9)
    ax.text(11.5, 6.7, 'Read ref_dict', ha='center', fontsize=8, color='#2E7D32')

    # attn2
    add_box(ax, 10.5, 2.5, 2, 1.5, '#4CAF50', 'attn2\n(Cross-Attn)', fontsize=9)

    # FFN
    add_box(ax, 13, 3.75, 2, 1.5, '#9E9E9E', 'FFN\n(Feed-Forward)', fontsize=9)

    # Noisy Input
    add_box(ax, 13, 5.5, 2, 1.5, '#E0E0E0', 'Noisy\nMulti-view', fontsize=9)
    ax.text(14, 7.2, 'Timestep t', ha='center', fontsize=8, color='#757575', style='italic')

    # Arrows in Read Pass
    add_arrow(ax, (9.5, 6.25), (10.5, 5.75))  # ref_dict -> attn1
    add_arrow(ax, (12.5, 5.75), (13, 6.25))  # attn1 -> Noisy

    # ============ Stage 4: Iterative Denoising ============
    ax.annotate('', xy=(15.5, 4.5), xytext=(15.5, 2.5),
                arrowprops=dict(arrowstyle='->', color='#FF5722', lw=3))
    ax.text(16.5, 3.5, 'Iterate\n50 steps', ha='center', fontsize=10,
            fontweight='bold', color='#FF5722', style='italic')
    ax.text(16.5, 2.8, 't=50→0', ha='center', fontsize=8, color='#757575')

    # ============ Stage 5: Output ============
    add_box(ax, 16, 1, 3.5, 7, COLORS['output'], '', fontsize=8)
    ax.text(17.75, 8.3, 'Output', ha='center', fontsize=12, fontweight='bold', color='#6A1B9A')

    # Load and display output views
    output_views = load_output_views()
    view_positions = [
        (16.3, 5.8), (17.4, 5.8), (18.5, 5.8),
        (16.3, 4.3), (17.4, 4.3), (18.5, 4.3),
    ]

    for idx, (vx, vy) in enumerate(view_positions):
        img_array = np.array(output_views[idx])
        ax.imshow(img_array, extent=[vx, vx+0.9, vy, vy+1.2], aspect='auto', zorder=5)
        ax.text(vx+0.45, vy-0.15, f'View {idx+1}', ha='center', fontsize=7, color='#424242')

    ax.text(17.75, 3.5, '6-View\nOutput', ha='center', fontsize=9, style='italic', color='#6A1B9A')

    # ============ Main Flow Arrows ============
    # Input -> Write Pass
    add_arrow(ax, (3.5, 5), (4, 5))
    ax.text(3.75, 5.3, '1', ha='center', fontsize=10, fontweight='bold', color='#FF5722')

    # Write Pass -> Read Pass
    add_arrow(ax, (9.5, 5), (10, 5))
    ax.text(9.75, 5.3, '2', ha='center', fontsize=10, fontweight='bold', color='#FF5722')

    # Read Pass -> Output
    add_arrow(ax, (15.5, 5), (16, 5))
    ax.text(15.75, 5.3, '3', ha='center', fontsize=10, fontweight='bold', color='#FF5722')

    # ============ Legend ============
    legend_elements = [
        mpatches.Patch(facecolor='#2196F3', label='attn1 (Self-Attention + Reference)'),
        mpatches.Patch(facecolor='#4CAF50', label='attn2 (Cross-Attention)'),
        mpatches.Patch(facecolor='#9E9E9E', label='FFN (Feed-Forward)'),
        mpatches.Patch(facecolor='#FF9800', label='ref_dict (Feature Storage)'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=4,
             fontsize=9, framealpha=0.9, bbox_to_anchor=(0.5, -0.02))

    plt.title('MV-Painter Pipeline Decomposition: From Input to Multi-View Output',
             fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Saved: {output_path}")


def create_reference_mechanism_figure(output_path):
    """Create detailed figure showing Reference Attention mechanism."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # ============ (a) Write Mode ============
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('(a) Write Mode\n(Condition Processing)', fontsize=12, fontweight='bold', color='#E65100')

    # Condition input
    cond_img = load_condition_image()
    ax1.imshow(np.array(cond_img), extent=[0.5, 3.5, 6, 9], aspect='auto')
    ax1.text(2, 5.5, 'Condition Image', ha='center', fontsize=9)

    # attn1 processing
    add_box(ax1, 4.5, 6, 2.5, 2, '#2196F3', 'attn1\nQ·K^T·V', fontsize=10)
    ax1.text(5.75, 5.3, 'Self-Attention', ha='center', fontsize=8, style='italic')

    # ref_dict storage
    add_box(ax1, 4.5, 2, 2.5, 2, '#FF9800', 'ref_dict[l]\n= h_ref', fontsize=10)
    ax1.text(5.75, 1.3, 'Store Features', ha='center', fontsize=8, style='italic')

    # Arrows
    ax1.annotate('', xy=(4.5, 7), xytext=(3.5, 7.5),
                arrowprops=dict(arrowstyle='->', color='#424242', lw=2))
    ax1.annotate('', xy=(5.75, 4), xytext=(5.75, 6),
                arrowprops=dict(arrowstyle='->', color='#E65100', lw=2.5))

    # Layer indicator
    ax1.text(8, 8, 'Layer l\n(1 of 70)', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    # ============ (b) Read Mode ============
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('(b) Read Mode\n(View Generation)', fontsize=12, fontweight='bold', color='#2E7D32')

    # Noisy input
    add_box(ax2, 0.5, 6, 2.5, 2, '#E0E0E0', 'Noisy\nLatent', fontsize=10)
    ax2.text(1.75, 5.3, 'View t', ha='center', fontsize=8)

    # attn1 with reference
    add_box(ax2, 4.5, 6, 2.5, 2, '#2196F3', 'attn1\nconcat(h, ref)', fontsize=10)
    ax2.text(5.75, 5.3, 'Read Reference', ha='center', fontsize=8, style='italic')

    # ref_dict
    add_box(ax2, 4.5, 2, 2.5, 2, '#FF9800', 'ref_dict[l]\n=h_ref', fontsize=10)
    ax2.text(5.75, 1.3, 'Load Features', ha='center', fontsize=8, style='italic')

    # Output
    add_box(ax2, 8, 6, 2, 2, '#4CAF50', 'Enhanced\nFeatures', fontsize=10)

    # Arrows
    ax2.annotate('', xy=(4.5, 7), xytext=(3, 7),
                arrowprops=dict(arrowstyle='->', color='#424242', lw=2))
    ax2.annotate('', xy=(5.75, 4), xytext=(5.75, 6),
                arrowprops=dict(arrowstyle='->', color='#E65100', lw=2.5))
    ax2.annotate('', xy=(8, 7), xytext=(7, 7),
                arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2))

    # ============ (c) Full LoRA vs attn2-only ============
    ax3 = axes[2]
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.set_aspect('equal')
    ax3.axis('off')
    ax3.set_title('(c) LoRA Application\nComparison', fontsize=12, fontweight='bold')

    # Full LoRA (broken)
    add_box(ax3, 0.5, 5.5, 4, 1.5, '#FFCDD2', 'Full LoRA', fontsize=10)
    ax3.text(2.5, 6.25, 'attn1 + attn2', ha='center', fontsize=9, color='#C62828')
    ax3.text(2.5, 4.8, '❌ Breaks ref_dict', ha='center', fontsize=9, color='#C62828', fontweight='bold')

    # attn2-only (working)
    add_box(ax3, 0.5, 2, 4, 1.5, '#C8E6C9', 'attn2-only LoRA', fontsize=10)
    ax3.text(2.5, 2.75, 'Only attn2', ha='center', fontsize=9, color='#2E7D32')
    ax3.text(2.5, 1.3, '✓ Preserves ref_dict', ha='center', fontsize=9, color='#2E7D32', fontweight='bold')

    # Visual indicator
    ax3.text(5.5, 6.25, 'W\'_q, W\'_k, W\'_v\nCorrupt stored\nreference features',
            ha='center', fontsize=8, color='#C62828',
            bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.8))

    ax3.text(5.5, 2.75, 'W_q, W_k, W_v\nOriginal attn1\npreserves features',
            ha='center', fontsize=8, color='#2E7D32',
            bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Saved: {output_path}")


def create_feature_flow_figure(output_path):
    """Create figure showing feature flow through the network."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')

    # Title
    ax.text(7, 7.5, 'Reference Feature Flow in MV-Painter',
           ha='center', fontsize=14, fontweight='bold')

    # ============ Layer 1-20 (Shallow) ============
    add_box(ax, 0.5, 5, 3, 1.5, '#E3F2FD', 'Layers 1-20\n(Shallow)', fontsize=10)
    ax.text(2, 4.5, 'High-level features', ha='center', fontsize=8, style='italic')

    # ============ Layer 21-50 (Middle) ============
    add_box(ax, 5, 5, 3, 1.5, '#FFF3E0', 'Layers 21-50\n(Middle)', fontsize=10)
    ax.text(6.5, 4.5, 'Mid-level features', ha='center', fontsize=8, style='italic')

    # ============ Layer 51-70 (Deep) ============
    add_box(ax, 9.5, 5, 3, 1.5, '#FCE4EC', 'Layers 51-70\n(Deep)', fontsize=10)
    ax.text(11, 4.5, 'Low-level features', ha='center', fontsize=8, style='italic')

    # ============ Reference Feature Storage ============
    add_box(ax, 2, 2, 9, 1.5, '#FF9800', 'ref_dict: Store h_ref at each layer', fontsize=11)
    ax.text(6.5, 1.3, '70 reference feature vectors', ha='center', fontsize=9, style='italic')

    # Arrows showing storage
    for x in [2, 6.5, 11]:
        ax.annotate('', xy=(x, 3.5), xytext=(x, 5),
                    arrowprops=dict(arrowstyle='->', color='#E65100', lw=2, linestyle='dashed'))

    # ============ Full LoRA Effect ============
    ax.text(2, 0.5, 'Full LoRA: Corrupts all 70 layers\n(avg cosine: 0.72)',
           ha='center', fontsize=9, color='#C62828', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.8))

    ax.text(6.5, 0.5, 'attn2-only: Preserves all 70 layers\n(avg cosine: 0.999)',
           ha='center', fontsize=9, color='#2E7D32', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.8))

    ax.text(11, 0.5, 'Deeper layers =\nmore corruption',
           ha='center', fontsize=9, color='#E65100', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Saved: {output_path}")


def main():
    output_dir = '/4T/CXY/MV-Painter/output/paper_normal/figures'
    os.makedirs(output_dir, exist_ok=True)

    print("Creating pipeline decomposition figures...")
    print("=" * 60)

    # Figure A: Main Pipeline Decomposition
    create_pipeline_figure(
        os.path.join(output_dir, 'fig_pipeline_decomposition.png'))

    # Figure B: Reference Attention Mechanism Detail
    create_reference_mechanism_figure(
        os.path.join(output_dir, 'fig_reference_mechanism.png'))

    # Figure C: Feature Flow
    create_feature_flow_figure(
        os.path.join(output_dir, 'fig_feature_flow.png'))

    print("=" * 60)
    print("All pipeline figures created!")
    print(f"\nOutput directory: {output_dir}")

    for f in sorted(os.listdir(output_dir)):
        if 'pipeline' in f or 'reference' in f or 'feature' in f:
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"  {f}: {size/1024:.1f} KB")


if __name__ == '__main__':
    main()
