#!/usr/bin/env python3
"""Build the cross-study paired-effect figure from its compact source ledger."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "allocation_effects_data.json").read_text())
ROLE_STYLE = {
    "recorded_primary": ("#167E72", "o"),
    "later_pairwise": ("#C8793E", "s"),
    "native_interface": ("#275977", "D"),
    "protocol_sensitivity": ("#7A8188", "^"),
}


def draw_panel(ax, records, title, xlabel):
    for i, record in enumerate(records):
        lo, hi = record["ci95"]
        color, marker = ROLE_STYLE[record["role"]]
        ax.errorbar(
            record["mean"], i,
            xerr=[[record["mean"] - lo], [hi - record["mean"]]],
            fmt=marker, capsize=3, color=color, markersize=4.2, linewidth=1.25,
        )
    ax.axvline(0, color="#777777", lw=0.8, linestyle="--")
    ax.set_yticks(range(len(records)), [r["label"] for r in records], fontsize=7.4)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_xlabel(xlabel, fontsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="x", alpha=0.15)
    ax.spines[["top", "right"]].set_visible(False)


def main():
    fig, axs = plt.subplots(
        1, 2, figsize=(12.8, 4.55),
        gridspec_kw={"width_ratios": [1.65, 1]},
    )
    draw_panel(
        axs[0], DATA["image"], "(a) Generated-view FG-PSNR",
        "Paired difference (dB); higher favors first",
    )
    draw_panel(
        axs[1], DATA["baked"], "(b) Baked unseen-view FG-LPIPS",
        "Paired difference; lower favors first",
    )
    axs[1].ticklabel_format(axis="x", style="sci", scilimits=(-3, -3))
    legend_roles = ["recorded_primary", "later_pairwise", "native_interface", "protocol_sensitivity"]
    legend_labels = [
        "Recorded primary",
        "Later pairwise analysis",
        "Native interface",
        "Protocol / external cohort",
    ]
    handles = [
        Line2D([], [], marker=ROLE_STYLE[role][1], color=ROLE_STYLE[role][0],
               linestyle="none", markersize=5, label=label)
        for role, label in zip(legend_roles, legend_labels)
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=7.5, bbox_to_anchor=(0.5, 0.005))
    fig.tight_layout(w_pad=2.0, rect=(0, 0.08, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(ROOT / f"fig_allocation_effects014.{ext}",
                    bbox_inches="tight", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
