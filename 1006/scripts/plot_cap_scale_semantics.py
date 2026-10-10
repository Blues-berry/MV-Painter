#!/usr/bin/env python3
"""Plot requested versus native-cap-applied scale profiles by layer group."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
OUT = ROOT / "1006/figures/strategy_comparison_gallery"
OUT.mkdir(parents=True, exist_ok=True)
CAPS = {"Deep": 3.0, "Middle": 3.5, "Shallow": 0.8}
PROFILES = {
    "GFL": {"Deep": (1.25, 1.25, 1.25), "Middle": (1.25, 1.25, 1.25),
            "Shallow": (1.25, 1.25, 1.25)},
    "GFH": {"Deep": (2.50, 2.50, 2.50), "Middle": (2.50, 2.50, 2.50),
            "Shallow": (2.50, 2.50, 2.50)},
    "C3": {"Deep": (1.25, 2.50, 1.25), "Middle": (1.25, 2.50, 1.25),
           "Shallow": (1.25, 2.50, 1.25)},
    "LLH": {"Deep": (1.25, 1.25, 2.50), "Middle": (1.25, 1.25, 2.50),
            "Shallow": (0.50, 0.50, 0.75)},
}
COLORS = {"GFL": "#0072B2", "GFH": "#D55E00", "C3": "#009E73",
          "LLH": "#CC79A7", "Generic linear": "#E69F00"}


def values(method: str, group: str, x: np.ndarray) -> np.ndarray:
    if method == "Generic linear":
        low, high = ((0.50, 0.75) if group == "Shallow" else (1.25, 2.50))
        return low + (high - low) * x
    trace = PROFILES[method][group]
    stage = np.where(x < 17 / 50, 0, np.where(x < 33 / 50, 1, 2))
    return np.asarray(trace, dtype=float)[stage]


def main() -> None:
    x = np.arange(50, dtype=float) / 49
    methods = ["GFL", "GFH", "C3", "LLH", "Generic linear"]
    rows = []
    fig, axes = plt.subplots(3, 1, figsize=(10.8, 8.8), sharex=True, constrained_layout=True)
    for ax, (group, cap) in zip(axes, CAPS.items()):
        for method in methods:
            requested = values(method, group, x)
            applied = np.minimum(requested, cap)
            color = COLORS[method]
            ax.plot(x, requested, color=color, linewidth=2.0, label=method)
            if np.any(requested > cap):
                ax.plot(x, applied, color=color, linewidth=2.6, linestyle="--")
            for step, req, eff in zip(range(50), requested, applied):
                rows.append({"method": method, "layer_group": group, "step": step,
                             "cap": cap, "requested_scale": float(req),
                             "cap_applied_scale": float(eff),
                             "cap_active": bool(req > cap)})
        ax.axhline(cap, color="#555555", linestyle=":", linewidth=1.5)
        ax.set_ylabel(f"{group}\nscale")
        ax.set_ylim(0, 2.8 if group == "Shallow" else cap * 1.12)
        ax.grid(axis="y", alpha=0.22)
        ax.text(0.99, 0.9, f"native cap = {cap:g}", transform=ax.transAxes,
                ha="right", va="top", color="#444444", fontsize=10)
    axes[-1].set_xlim(0, 0.98)
    axes[-1].set_xticks([0, 17 / 49, 33 / 49, 1], ["0", "17", "33", "49"])
    axes[-1].set_xlabel("Denoising step (early / middle / late windows: 17 / 16 / 17 steps)")
    handles, labels = axes[0].get_legend_handles_labels()
    from matplotlib.lines import Line2D
    handles += [Line2D([0], [0], color="#333333", linewidth=2, linestyle="--"),
                Line2D([0], [0], color="#555555", linewidth=1.5, linestyle=":")]
    labels += ["cap-applied when clipped", "native cap"]
    fig.legend(handles, labels, ncol=4, loc="upper center", bbox_to_anchor=(0.52, 1.02), frameon=False)
    fig.suptitle("Requested and native-cap-applied geometry-adapter scale", y=1.07, fontsize=15)
    fig.text(0.5, -0.01,
             "Dashed scale traces show clipping only; scale is not realized residual dose or equalized intervention strength.",
             ha="center", fontsize=9.5)
    fig.savefig(OUT / "cap_scale_semantics.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "cap_scale_semantics.pdf", bbox_inches="tight")
    with (OUT / "cap_scale_semantics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    plt.close(fig)
    clipped_counts = {(method, group): sum(r["cap_active"] for r in rows
                                              if r["method"] == method and r["layer_group"] == group)
                      for method in methods for group in CAPS}
    print({"output": str((OUT / "cap_scale_semantics.png").relative_to(ROOT)),
           "shallow_clipped_steps": {method: clipped_counts[(method, "Shallow")] for method in methods}})


if __name__ == "__main__":
    main()
