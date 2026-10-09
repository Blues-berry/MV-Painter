#!/usr/bin/env python3
"""Build the scoped 1008 graphical abstract as vector PDF and a PNG preview."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


OUT = Path(__file__).resolve().parents[1]
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#18324b"
BLUE = "#3979a8"
TEAL = "#278a85"
GOLD = "#d59c3a"
INK = "#23313d"
MUTED = "#536574"
PAPER = "#f5f8fa"
WHITE = "#ffffff"

fig = plt.figure(figsize=(13.2, 7.4), facecolor=PAPER)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 13.2)
ax.set_ylim(0, 7.4)
ax.axis("off")

ax.text(0.62, 6.83, "Timestep-Conditioned Adapter Scaling", color=NAVY,
        fontsize=25, weight="bold", va="center")
ax.text(0.64, 6.38, "A bounded study of stage-wise geometry control in multi-view diffusion",
        color=MUTED, fontsize=13, va="center")

# Left panel: requested schedule, explicitly distinguished from realized scale.
left = FancyBboxPatch((0.55, 2.02), 5.45, 3.85,
                      boxstyle="round,pad=0.18,rounding_size=0.18",
                      linewidth=0, facecolor=WHITE)
ax.add_patch(left)
ax.text(0.9, 5.45, "TCAS requested scale", color=NAVY, fontsize=16, weight="bold")
ax.text(0.9, 5.08, "Training-free profile on an existing adapter path",
        color=MUTED, fontsize=11.5)

segments = [(1.0, 1.25, BLUE, "Early"), (2.72, 2.50, TEAL, "Middle"),
            (4.44, 1.25, BLUE, "Late")]
base_y, max_h = 2.76, 1.62
for x, value, color, label in segments:
    height = max_h * value / 2.5
    ax.add_patch(FancyBboxPatch((x, base_y), 1.18, height,
                                boxstyle="round,pad=0.05,rounding_size=0.08",
                                linewidth=0, facecolor=color))
    ax.text(x + 0.59, base_y + height + 0.16, f"{value:.2f}",
            ha="center", color=NAVY, fontsize=13, weight="bold")
    ax.text(x + 0.59, 2.42, label, ha="center", color=MUTED, fontsize=11)
ax.plot([0.98, 5.62], [2.72, 2.72], color="#cbd5dd", lw=1.2)
ax.text(0.92, 2.15, "Requested values; wrapper caps and residual magnitudes are separate.",
        color=MUTED, fontsize=9.5)

# Right panel: matched primary result and explicit counter-results.
right = FancyBboxPatch((6.3, 2.02), 6.34, 3.85,
                       boxstyle="round,pad=0.18,rounding_size=0.18",
                       linewidth=0, facecolor=WHITE)
ax.add_patch(right)
ax.text(6.68, 5.45, "Fresh C · 300 matched objects", color=NAVY,
        fontsize=16, weight="bold")
ax.text(6.68, 5.08, "One frozen checkpoint · shared runner and inference protocol",
        color=MUTED, fontsize=11.5)

result = FancyBboxPatch((6.68, 3.75), 5.58, 1.0,
                        boxstyle="round,pad=0.13,rounding_size=0.12",
                        linewidth=0, facecolor="#eaf3f7")
ax.add_patch(result)
ax.text(6.97, 4.43, "C3 − GFL FG-PSNR", color=MUTED, fontsize=11.5)
ax.text(6.97, 4.02, "+0.522 dB", color=BLUE, fontsize=23, weight="bold")
ax.text(9.72, 4.08, "95% CI\n[+0.404, +0.641]", color=NAVY,
        fontsize=11, va="center", linespacing=1.35)

counter = FancyBboxPatch((6.68, 2.48), 5.58, 0.92,
                         boxstyle="round,pad=0.13,rounding_size=0.12",
                         linewidth=0, facecolor="#fbf3e4")
ax.add_patch(counter)
ax.text(6.97, 3.11, "Counter-results retained", color=GOLD,
        fontsize=12, weight="bold")
ax.text(6.97, 2.76,
        "GFH and Generic Linear have more favorable means than C3\non all four displayed endpoints.",
        color=INK, fontsize=10.3, va="center", linespacing=1.25)

ax.text(0.66, 1.42,
        "Interpretation: matched rendered-image evidence for the tested pipeline; no claim of a universal schedule.",
        color=NAVY, fontsize=12.2, weight="bold")
ax.plot([0.64, 12.55], [1.12, 1.12], color="#d6dfe5", lw=1)
ax.text(0.66, 0.70,
        "Image-space endpoints do not establish baked-texture, seam, PBR, unseen-view, or human-preference quality.",
        color=MUTED, fontsize=10.7)
ax.text(12.55, 0.29, "1008 · DRAFT", ha="right", color=MUTED, fontsize=9)

fig.savefig(OUT / "Graphical_Abstract_1008_DRAFT.pdf", facecolor=PAPER)
preview_dir = OUT / "Author_Review"
preview_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(preview_dir / "Graphical_Abstract_1008_DRAFT_preview.png", dpi=180,
            facecolor=PAPER)
plt.close(fig)
