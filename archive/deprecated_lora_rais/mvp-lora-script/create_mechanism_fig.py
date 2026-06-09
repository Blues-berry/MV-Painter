"""
Create mechanism diagram showing reference attention and LoRA impact.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_mechanism_figure(output_path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Color scheme
    colors = {
        'normal': '#4CAF50',
        'reference': '#2196F3',
        'lora': '#FF5722',
        'disabled': '#9E9E9E',
        'bg': '#F5F5F5',
        'arrow': '#333333',
    }

    # ============================================
    # Panel A: Reference Attention Mechanism
    # ============================================
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('A: Reference Attention\n(MV-Painter)', fontsize=14, fontweight='bold', pad=10)

    # Draw UNet blocks
    rect1 = FancyBboxPatch((1, 7), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['reference'], edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    ax.text(5, 8, 'attn1: Self-Attention\n+ Reference Storage', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    rect2 = FancyBboxPatch((1, 4), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['normal'], edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    ax.text(5, 5, 'attn2: Cross-Attention\n(Text/Image Embeddings)', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    # Draw flow arrows
    ax.annotate('', xy=(5, 7), xytext=(5, 6),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.text(5.5, 6.5, 'Write\n(mode=w)', fontsize=8, ha='left', color=colors['arrow'])

    ax.annotate('', xy=(5, 6), xytext=(5, 7),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2, linestyle='--'))
    ax.text(5.5, 7.5, 'Read\n(mode=r)', fontsize=8, ha='left', color=colors['arrow'])

    # Input/output labels
    ax.text(5, 2.5, 'Condition Image\n→ Reference Features', ha='center', va='center',
            fontsize=9, style='italic', color=colors['reference'])
    ax.annotate('', xy=(5, 4), xytext=(5, 3),
                arrowprops=dict(arrowstyle='->', color=colors['reference'], lw=2))

    ax.text(5, 0.5, 'Output: 6-View Images', ha='center', va='center',
            fontsize=9, style='italic', color=colors['normal'])

    # ============================================
    # Panel B: Full LoRA (Broken)
    # ============================================
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('B: Full LoRA (attn1 + attn2)\nReference Disrupted', fontsize=14, fontweight='bold', pad=10)

    # Draw UNet blocks with LoRA
    rect1 = FancyBboxPatch((1, 7), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['lora'], edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    ax.text(5, 8, 'attn1: Self-Attention\n+ LoRA ❌', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    rect2 = FancyBboxPatch((1, 4), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['lora'], edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    ax.text(5, 5, 'attn2: Cross-Attention\n+ LoRA', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    # Broken reference
    ax.text(5, 2.5, 'Reference Storage\nDISRUPTED ❌', ha='center', va='center',
            fontsize=9, fontweight='bold', color=colors['lora'])
    ax.annotate('', xy=(5, 4), xytext=(5, 3),
                arrowprops=dict(arrowstyle='->', color=colors['lora'], lw=2, linestyle='--'))

    ax.text(5, 0.5, 'Output: Reference Ignored\n(Consistency Lost)', ha='center', va='center',
            fontsize=9, fontweight='bold', color=colors['lora'])

    # ============================================
    # Panel C: attn2-only LoRA (Working)
    # ============================================
    ax = axes[2]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('C: attn2-only LoRA (Working)\nOur Approach', fontsize=14, fontweight='bold', pad=10)

    # Draw UNet blocks
    rect1 = FancyBboxPatch((1, 7), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['reference'], edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    ax.text(5, 8, 'attn1: Self-Attention\n(Preserved) ✓', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    rect2 = FancyBboxPatch((1, 4), 8, 2, boxstyle="round,pad=0.1",
                           facecolor=colors['lora'], edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    ax.text(5, 5, 'attn2: Cross-Attention\n+ LoRA', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

    # Preserved reference
    ax.text(5, 2.5, 'Reference Storage\nPRESERVED ✓', ha='center', va='center',
            fontsize=9, fontweight='bold', color=colors['reference'])
    ax.annotate('', xy=(5, 4), xytext=(5, 3),
                arrowprops=dict(arrowstyle='->', color=colors['reference'], lw=2))

    ax.text(5, 0.5, 'Output: High Quality\n(Consistent 6-View)', ha='center', va='center',
            fontsize=9, fontweight='bold', color=colors['normal'])

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=colors['reference'], label='Reference Attention (Preserved)'),
        mpatches.Patch(facecolor=colors['lora'], label='LoRA Modified'),
        mpatches.Patch(facecolor=colors['normal'], label='Standard Processing'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10,
              frameon=True, fancybox=True, shadow=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0.5)
    print(f"Mechanism figure saved to {output_path}")


if __name__ == '__main__':
    output_path = '/4T/CXY/MV-Painter/mvpoutput/paper_assets/mechanism_fig.png'
    create_mechanism_figure(output_path)
