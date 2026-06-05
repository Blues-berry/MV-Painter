"""
Create a professional mechanism figure for the paper.
Shows the UNet two-pass (write-read) reference attention mechanism
and how different LoRA strategies affect it.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Use a clean style
plt.style.use('seaborn-v0_8-whitegrid')

fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

# Color scheme
COLOR_PRESERVE = '#2E86AB'      # Blue - preserved
COLOR_LORA = '#E8553D'          # Red/Orange - LoRA modified
COLOR_FEATURE = '#27AE60'       # Green - features/output
COLOR_BG = '#F8F9FA'            # Light gray background
COLOR_ARROW = '#2C3E50'         # Dark gray arrows
COLOR_REF = '#8E44AD'           # Purple - reference features

def draw_unet_block(ax, x, y, width, height, label, color, fontsize=9):
    """Draw a rounded rectangle representing a UNet block."""
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor='#2C3E50',
                         linewidth=1.5, alpha=0.85)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, label,
            ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color='white' if color != COLOR_BG else '#2C3E50')

def draw_arrow(ax, x1, y1, x2, y2, label='', color=COLOR_ARROW, fontsize=8):
    """Draw an arrow with optional label."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.02, my, label, fontsize=fontsize,
                color=color, fontweight='bold', ha='left', va='center')

def draw_ref_features(ax, x, y, width, height, label="ref_dict"):
    """Draw reference feature storage."""
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.03",
                         facecolor=COLOR_REF, edgecolor='#2C3E50',
                         linewidth=1.5, alpha=0.7)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, label,
            ha='center', va='center', fontsize=8,
            fontweight='bold', color='white')

# ========== Panel A: Original MV-Painter ==========
ax = axes[0]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('(A) Original MV-Painter', fontsize=13, fontweight='bold', pad=15)

# UNet Pass 1 (Write)
draw_unet_block(ax, 0.15, 0.72, 0.7, 0.18, 'UNet Pass 1 (Write)', COLOR_PRESERVE)
ax.text(0.5, 0.92, 'Condition Image', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_FEATURE,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_FEATURE, alpha=0.2))

# Arrow from condition to Pass 1
draw_arrow(ax, 0.5, 0.88, 0.5, 0.90, '', COLOR_FEATURE)

# Reference storage
draw_ref_features(ax, 0.25, 0.55, 0.5, 0.12, 'ref_dict[l] = h_ref')
draw_arrow(ax, 0.5, 0.72, 0.5, 0.67, 'Store', COLOR_REF)

# UNet Pass 2 (Read)
draw_unet_block(ax, 0.15, 0.25, 0.7, 0.18, 'UNet Pass 2 (Read)', COLOR_PRESERVE)

# Arrow from ref_dict to Pass 2
draw_arrow(ax, 0.5, 0.55, 0.5, 0.43, 'Retrieve', COLOR_REF)

# Output
ax.text(0.5, 0.12, '6 Consistent Views', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_FEATURE,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_FEATURE, alpha=0.2))
draw_arrow(ax, 0.5, 0.25, 0.5, 0.17, '', COLOR_FEATURE)

# Labels for attn1 and attn2
ax.text(0.02, 0.81, 'attn1\n(self)', fontsize=7, ha='center', va='center',
        color=COLOR_PRESERVE, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_PRESERVE, alpha=0.8))
ax.text(0.02, 0.34, 'attn2\n(cross)', fontsize=7, ha='center', va='center',
        color=COLOR_PRESERVE, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_PRESERVE, alpha=0.8))

# ========== Panel B: Full LoRA ==========
ax = axes[1]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('(B) Full LoRA (Broken)', fontsize=13, fontweight='bold', pad=15, color=COLOR_LORA)

# UNet Pass 1 (Write) - with LoRA
draw_unet_block(ax, 0.15, 0.72, 0.7, 0.18, 'UNet Pass 1 + LoRA', COLOR_LORA)
ax.text(0.5, 0.92, 'Condition Image', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_FEATURE,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_FEATURE, alpha=0.2))
draw_arrow(ax, 0.5, 0.88, 0.5, 0.90, '', COLOR_FEATURE)

# Corrupted reference storage
draw_ref_features(ax, 0.25, 0.55, 0.5, 0.12, 'ref_dict[l] = h_corrupted')
draw_arrow(ax, 0.5, 0.72, 0.5, 0.67, 'Store ✗', COLOR_LORA)

# UNet Pass 2 (Read) - with LoRA
draw_unet_block(ax, 0.15, 0.25, 0.7, 0.18, 'UNet Pass 2 + LoRA', COLOR_LORA)

# Arrow from corrupted ref_dict to Pass 2
draw_arrow(ax, 0.5, 0.55, 0.5, 0.43, 'Retrieve ✗', COLOR_LORA)

# Output - degraded
ax.text(0.5, 0.12, 'Inconsistent Views', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_LORA,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_LORA, alpha=0.2))
draw_arrow(ax, 0.5, 0.25, 0.5, 0.17, '', COLOR_LORA)

# Labels for attn1 and attn2 - both modified
ax.text(0.02, 0.81, 'attn1+LoRA', fontsize=7, ha='center', va='center',
        color=COLOR_LORA, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_LORA, alpha=0.8))
ax.text(0.02, 0.34, 'attn2+LoRA', fontsize=7, ha='center', va='center',
        color=COLOR_LORA, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_LORA, alpha=0.8))

# ========== Panel C: attn2-only LoRA ==========
ax = axes[2]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('(C) attn2-only LoRA (Ours)', fontsize=13, fontweight='bold', pad=15, color=COLOR_PRESERVE)

# UNet Pass 1 (Write) - preserved
draw_unet_block(ax, 0.15, 0.72, 0.7, 0.18, 'UNet Pass 1 (Preserved)', COLOR_PRESERVE)
ax.text(0.5, 0.92, 'Condition Image', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_FEATURE,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_FEATURE, alpha=0.2))
draw_arrow(ax, 0.5, 0.88, 0.5, 0.90, '', COLOR_FEATURE)

# Preserved reference storage
draw_ref_features(ax, 0.25, 0.55, 0.5, 0.12, 'ref_dict[l] = h_ref ✓')
draw_arrow(ax, 0.5, 0.72, 0.5, 0.67, 'Store ✓', COLOR_PRESERVE)

# UNet Pass 2 (Read) - attn2 has LoRA
draw_unet_block(ax, 0.15, 0.25, 0.7, 0.18, 'UNet Pass 2 (attn2+LoRA)', COLOR_LORA)

# Arrow from preserved ref_dict to Pass 2
draw_arrow(ax, 0.5, 0.55, 0.5, 0.43, 'Retrieve ✓', COLOR_PRESERVE)

# Output - consistent
ax.text(0.5, 0.12, 'Consistent 6 Views', fontsize=10, ha='center',
        fontweight='bold', color=COLOR_FEATURE,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_FEATURE, alpha=0.2))
draw_arrow(ax, 0.5, 0.25, 0.5, 0.17, '', COLOR_FEATURE)

# Labels for attn1 (preserved) and attn2 (LoRA)
ax.text(0.02, 0.81, 'attn1\n(Preserved)', fontsize=7, ha='center', va='center',
        color=COLOR_PRESERVE, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_PRESERVE, alpha=0.8))
ax.text(0.02, 0.34, 'attn2+LoRA', fontsize=7, ha='center', va='center',
        color=COLOR_LORA, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=COLOR_LORA, alpha=0.8))

# ========== Legend ==========
legend_elements = [
    mpatches.Patch(facecolor=COLOR_PRESERVE, label='Preserved (Original Weights)', alpha=0.85),
    mpatches.Patch(facecolor=COLOR_LORA, label='LoRA Modified', alpha=0.85),
    mpatches.Patch(facecolor=COLOR_REF, label='Reference Features', alpha=0.7),
    mpatches.Patch(facecolor=COLOR_FEATURE, label='Data Flow / Output', alpha=0.7),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=4,
           fontsize=10, frameon=True, fancybox=True, shadow=True,
           bbox_to_anchor=(0.5, -0.02))

plt.tight_layout(rect=[0, 0.04, 1, 0.98])

output_path = '/4T/CXY/MV-Painter/output/paper_normal/figures/mechanism_comparison_v2.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"Saved to: {output_path}")
plt.close()
