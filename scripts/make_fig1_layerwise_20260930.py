#!/usr/bin/env python
"""Redraw Figure 1 (method overview) centred on layer-wise stage-aware
adapter scaling. Replaces the TCAS/FAC-centred overview:
 - geometry residuals are injected at three UNet depth groups;
 - each depth group owns a per-stage scale function s_l(p) (the paper's
   equation h'_{l,t} = h_{l,t} + s_l(p_t) A_l(h_{l,t}, G));
 - the shown schedules are the frozen layer-LHL example and the shallow cap.

Output: final/fig1_layerwise_20260930.pdf (same aspect ratio as the old fig1).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"

FIG_W, FIG_H = 11.25, 6.94  # ~562x347 pts scaled x1.4 for crispness
fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 81)
ax.axis("off")

C_UNET = "#dbe7f7"
C_UNET_E = "#3c6cb4"
C_ADAPTER = "#fde9cf"
C_ADAPTER_E = "#d98a2b"
C_SCALE = "#e2efdb"
C_SCALE_E = "#4e8a3a"
C_IN = "#f2f2f2"
C_IN_E = "#8c8c8c"
C_OUT = "#eaf3fb"
C_OUT_E = "#3c6cb4"


def box(x, y, w, h, fc, ec, lw=1.4, radius=1.2):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=lw, facecolor=fc, edgecolor=ec, zorder=2,
    )
    ax.add_patch(p)


def text(x, y, s, size=9, weight="normal", color="black", ha="center", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color,
            ha=ha, va=va, zorder=6, style=style)


def arrow(x1, y1, x2, y2, color="#555555", lw=1.6, style="-|>", ls="-"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=13,
                        linewidth=lw, color=color, zorder=4, linestyle=ls)
    ax.add_patch(a)


# ---------------- Inputs (left) ----------------
box(1.5, 30, 13.5, 46, C_IN, C_IN_E)
text(8.2, 73.2, "Inputs", 10.5, "bold")

inp = [
    ("Reference\nimage", "#f6d5e0"),
    ("Normal map", "#cfe3f7"),
    ("Depth map", "#d9f0d5"),
    ("Foreground\nmask", "#eeeeee"),
]
yy = 63.5
for label, fc in inp:
    box(2.8, yy - 6.4, 10.9, 9.4, fc, "#aaaaaa", lw=1.0, radius=0.8)
    text(8.2, yy - 1.7, label, 7.6)
    yy -= 11.0

# ---------------- Frozen UNet (center-top) ----------------
box(19.5, 47, 47, 32, C_UNET, C_UNET_E, lw=1.8)
text(43, 75.4, "Frozen multi-view diffusion UNet", 10.5, "bold", C_UNET_E)

# depth-group blocks inside the UNet (deep -> shallow)
blocks = [
    ("deep\nup$_0$", 23.0, "cap 3.0"),
    ("middle\nup$_1$", 33.5, "cap 3.5"),
    ("shallow\nup$_2$", 44.0, "cap 0.8"),
]
for label, bx, cap in blocks:
    box(bx, 53.5, 8.2, 16.5, "#ffffff", C_UNET_E, lw=1.2, radius=0.9)
    text(bx + 4.1, 61.8, label, 8.2)
    text(bx + 4.1, 55.4, cap, 6.8, color="#777777")
arrow(31.2 + 0.4, 61.8, 33.5 - 0.2, 61.8, "#9db8dd", lw=1.2)
arrow(41.7 + 0.4, 61.8, 44.0 - 0.2, 61.8, "#9db8dd", lw=1.2)

# GeoTex-Adapter box under the UNet blocks
box(23.0, 48.2, 29.2, 4.4, C_ADAPTER, C_ADAPTER_E, lw=1.4, radius=0.9)
text(37.6, 50.4, "GeoTex-Adapter  $A_l(\\mathbf{h}_{l,t},\\mathbf{G})$", 8.6, "bold", "#a35f10")
arrow(37.6, 52.6, 27.1, 53.5, C_ADAPTER_E, lw=1.4)
arrow(37.6, 52.6, 37.6, 53.5, C_ADAPTER_E, lw=1.4)
arrow(37.6, 52.6, 48.1, 53.5, C_ADAPTER_E, lw=1.4)
text(59.4, 50.4, "residuals", 7.6, color="#a35f10")

# inputs -> adapter and UNet
arrow(15.0, 62, 19.5, 62, C_IN_E, lw=1.8)
arrow(15.0, 50.4, 23.0, 50.4, C_IN_E, lw=1.8)

# ---------------- Layer-wise scaling panel (center-bottom) ----------------
box(19.5, 8, 47, 33, C_SCALE, C_SCALE_E, lw=1.8)
text(43, 37.6, "Layer-wise stage-aware adapter scaling", 10.5, "bold", C_SCALE_E)
text(43, 33.8, r"$\mathbf{h}'_{l,t}=\mathbf{h}_{l,t}+s_l(p_t)\,A_l(\mathbf{h}_{l,t},\mathbf{G})$"
     "      (training-free; per-step scale assignment only)", 8.2)

def mini_schedule(x0, y0, w, h, pattern, lo, hi, label, value_text):
    box(x0, y0, w, h, "#ffffff", C_SCALE_E, lw=1.0, radius=0.6)
    n = 3
    seg = w / n
    for i, ch in enumerate(pattern):
        fc = "#7fb069" if ch == "H" else "#cfe3c0"
        ax.add_patch(Rectangle((x0 + i * seg + 0.25, y0 + 0.35), seg - 0.5, h - 0.7,
                               facecolor=fc, edgecolor="none", zorder=3))
        text(x0 + i * seg + seg / 2, y0 + h / 2, {"L": "L", "H": "H"}[ch], 7.6, "bold", "#33502a")
    text(x0 - 1.1, y0 + h / 2, label, 8.0, "bold", ha="right")
    text(x0 + w / 2, y0 - 1.9, value_text, 7.4, color="#33502a")

mini_schedule(27.6, 24.2, 25.0, 5.6, "LHL", None, None, "deep",
              "s = (1.25, 2.50, 1.25)")
mini_schedule(27.6, 15.9, 25.0, 5.6, "LHL", None, None, "middle",
              "s = (1.25, 2.50, 1.25)")
mini_schedule(27.6, 7.6, 25.0, 5.6, "LHL", None, None, "shallow",
              "s = (0.50, 0.75, 0.50), cap 0.8")
text(61.5, 27.0, "early / middle / late", 7.6, color="#555555")
text(61.5, 24.4, "(17 / 16 / 17 steps)", 7.2, color="#777777")
text(61.5, 17.5, "example schedule:\nlayer-LHL", 7.8, color="#33502a")
arrow(58.0, 24.5, 58.0, 24.5)

# arrow from scaling panel to adapter
arrow(43.0, 41.0, 43.0, 48.2, C_SCALE_E, lw=2.0)
text(63.4, 44.6, "per-group\nscale $s_l(p_t)$", 7.6, color=C_SCALE_E)

# ---------------- Outputs (right) ----------------
box(71.5, 30, 27, 46, C_OUT, C_OUT_E)
text(85, 73.2, "Outputs", 10.5, "bold", C_OUT_E)

# six target views icon
vx, vy = 75.0, 58.0
for i in range(6):
    col, row = i % 3, i // 3
    box(vx + col * 6.6, vy + (1 - row) * 5.6, 5.6, 4.6, "#ffffff", C_OUT_E, lw=1.0, radius=0.5)
text(85, 55.0, "six target views", 7.8)
arrow(66.5, 62, 71.5, 62, C_IN_E, lw=1.8)

box(74.5, 40.5, 21, 8.5, "#ffffff", C_OUT_E, lw=1.2)
text(85, 44.8, "projection\n& baking", 8.2)
arrow(85, 57.4, 85, 49.0, C_IN_E, lw=1.6)

box(76.5, 31.5, 16.5, 6.5, "#e8e3d9", "#8c7a55", lw=1.2)
text(84.8, 34.8, "textured mesh", 8.2)
arrow(85, 40.5, 85, 38.0, C_IN_E, lw=1.6)

# caption note
text(50, 1.6, "All schedules share one frozen pipeline: scales are assigned per denoising step and per depth group; "
    "no weights change.", 7.6, color="#555555")

fig.savefig("final/fig1_layerwise_20260930.pdf")
fig.savefig("/tmp/fig1_preview.png", dpi=110)
print("saved final/fig1_layerwise_20260930.pdf")
