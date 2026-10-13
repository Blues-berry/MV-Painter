#!/usr/bin/env python3
"""Rebuild requested/applied/residual accounting from frozen Fresh C logs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "1006/data/fresh_c/runs/c3_confirmation/residual_logs"
ADDENDUM = ROOT / "1006/data/fresh_c/runs/revision_era_addendum/residual_logs"
OUT_AUDIT = ROOT / "1006/evidence/audits"
OUT_FIG = ROOT / "1006/figures"
STRATEGIES = {
    "GFL": (PRIMARY, "native_gfl"),
    "GFH": (PRIMARY, "native_gfh"),
    "C3": (PRIMARY, "native_gc3"),
    "LLH": (ADDENDUM, "layer_llh"),
    "generic linear": (ADDENDUM, "gen_linear"),
}
DEPTHS = ("deep", "middle", "shallow")
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_traces(root: Path, condition: str) -> tuple[list[dict], list[dict]]:
    paths = sorted((root / condition).glob("*.json"))
    if not paths:
        raise RuntimeError(f"no traces at {root / condition}")
    entries: list[dict] = []
    sources = []
    for path in paths:
        trace = json.loads(path.read_text())
        if set(trace) != {str(i) for i in range(50)}:
            raise RuntimeError(f"unexpected timestep set in {path}")
        sources.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
        for step in range(50):
            for wrapper, item in trace[str(step)].items():
                depth = item["depth"]
                requested = float(item["scale"])
                applied = float(item["eff_scale"])
                if depth not in CAPS or applied != min(requested, CAPS[depth]):
                    raise RuntimeError(f"cap semantics mismatch: {path}, step {step}, {wrapper}")
                entries.append({
                    "strategy": condition, "uid": path.stem, "step": step,
                    "wrapper": int(wrapper), "depth": depth,
                    "requested_scale": requested, "applied_scale": applied,
                    "cap_activation": requested > applied,
                    # _last_correction is recorded after multiplying by applied_scale.
                    "applied_correction_l2": float(item["l2"]),
                    "correction_mean_abs": float(item["mean_abs"]),
                    "correction_max_abs": float(item["max_abs"]),
                    "height": int(item["h"]), "width": int(item["w"]),
                })
    return entries, sources


def main() -> None:
    all_rows: list[dict] = []
    source_index = {}
    for label, (root, condition) in STRATEGIES.items():
        rows, sources = read_traces(root, condition)
        for row in rows:
            row["strategy_label"] = label
        all_rows.extend(rows)
        source_index[label] = {"condition": condition, "objects": len(sources), "trace_files": sources}

    summary_rows: list[dict] = []
    for label in STRATEGIES:
        these = [r for r in all_rows if r["strategy_label"] == label]
        for step in range(50):
            for depth in DEPTHS:
                cells = [r for r in these if r["step"] == step and r["depth"] == depth]
                if not cells:
                    raise RuntimeError(f"missing {label}/{step}/{depth}")
                req = sorted({r["requested_scale"] for r in cells})
                applied = sorted({r["applied_scale"] for r in cells})
                correction = np.asarray([r["applied_correction_l2"] for r in cells], dtype=float)
                summary_rows.append({
                    "strategy": label, "step": step, "depth": depth,
                    "requested_scale_values": "|".join(f"{v:.9g}" for v in req),
                    "applied_scale_values": "|".join(f"{v:.9g}" for v in applied),
                    "requested_scale_min": min(req), "requested_scale_max": max(req),
                    "applied_scale_min": min(applied), "applied_scale_max": max(applied),
                    "cap_activated_wrapper_fraction": float(np.mean([r["cap_activation"] for r in cells])),
                    "applied_correction_l2_median": float(np.median(correction)),
                    "applied_correction_l2_q25": float(np.quantile(correction, 0.25)),
                    "applied_correction_l2_q75": float(np.quantile(correction, 0.75)),
                    "correction_mean_abs_median": float(np.median([r["correction_mean_abs"] for r in cells])),
                    "wrapper_records": len(cells),
                    "object_count": len({r["uid"] for r in cells}),
                })

    OUT_AUDIT.mkdir(parents=True, exist_ok=True)
    table = OUT_AUDIT / "FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv"
    with table.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0]))
        writer.writeheader(); writer.writerows(summary_rows)

    # Figure: one row per strategy. Solid lines are requested; dashed lines are post-cap.
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
                         "legend.fontsize": 6.8, "pdf.fonttype": 42, "ps.fonttype": 42})
    colors = {"deep": "#0072B2", "middle": "#D55E00", "shallow": "#009E73"}
    fig, axes = plt.subplots(5, 2, figsize=(10.8, 10.2), sharex=True,
                             gridspec_kw={"width_ratios": [1.2, 1]})
    for row_i, label in enumerate(STRATEGIES):
        left, right = axes[row_i]
        left.set_title(f"{label}: requested and applied scale" if row_i == 0 else label, loc="left")
        for depth in DEPTHS:
            cells = [r for r in summary_rows if r["strategy"] == label and r["depth"] == depth]
            x = np.asarray([r["step"] for r in cells])
            req = np.asarray([r["requested_scale_min"] for r in cells])
            app = np.asarray([r["applied_scale_min"] for r in cells])
            line, = left.plot(x, req, color=colors[depth], lw=1.25, label=f"{depth} requested")
            left.plot(x, app, color=colors[depth], lw=1.25, ls="--", label=f"{depth} applied")
            cap = CAPS[depth]
            if np.any(req > app):
                left.fill_between(x, app, req, where=req > app, color=colors[depth], alpha=.11, interpolate=True)
        left.set_ylim(-0.05, max(2.65, left.get_ylim()[1]))
        left.grid(alpha=.22, linewidth=.5)
        if row_i == 0:
            left.legend(ncol=2, frameon=False, loc="upper right")
        right.set_title("Applied correction norm (median; IQR)" if row_i == 0 else "", loc="left")
        for depth in DEPTHS:
            cells = [r for r in summary_rows if r["strategy"] == label and r["depth"] == depth]
            x = np.asarray([r["step"] for r in cells])
            med = np.asarray([r["applied_correction_l2_median"] for r in cells])
            q25 = np.asarray([r["applied_correction_l2_q25"] for r in cells])
            q75 = np.asarray([r["applied_correction_l2_q75"] for r in cells])
            right.plot(x, med, color=colors[depth], lw=1.25, label=depth)
            right.fill_between(x, q25, q75, color=colors[depth], alpha=.12, linewidth=0)
        right.set_yscale("symlog", linthresh=1e-2)
        right.grid(alpha=.22, linewidth=.5)
        if row_i == 0:
            right.legend(frameon=False, ncol=3, loc="upper right")
        if row_i < 4:
            left.tick_params(labelbottom=False); right.tick_params(labelbottom=False)
    axes[-1, 0].set_xlabel("Denoising step (0–49)")
    axes[-1, 1].set_xlabel("Denoising step (0–49)")
    axes[2, 0].set_ylabel("Scale")
    axes[2, 1].set_ylabel("Correction L2 norm")
    fig.suptitle("Fresh C execution semantics: nominal scale, native cap, realized correction", y=.995, fontsize=11)
    fig.text(.5, .006, "Shading in left panels marks cap-active intervals. Correction L2 is descriptive across logged wrappers and objects; no inference is made from wrapper counts.", ha="center", fontsize=7)
    fig.tight_layout(rect=(0, .025, 1, .982), h_pad=.55, w_pad=.9)
    png = OUT_FIG / "FRESH_C_EXECUTION_SEMANTICS.png"
    pdf = OUT_FIG / "FRESH_C_EXECUTION_SEMANTICS.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)

    report = {
        "status": "PASS_DESCRIPTIVE_RECONSTRUCTION",
        "source_sets": source_index,
        "rows": len(summary_rows),
        "schema": "Per strategy/step/depth: requested scale, applied scale after native group cap, cap activation fraction, median/IQR of applied residual correction L2, median mean-absolute correction, wrapper/object counts.",
        "interpretation": "scale is the requested nominal intervention; eff_scale is min(requested, native depth-group cap). The saved l2 is the norm of _last_correction after multiplying by eff_scale, not the norm of an unscaled residual or an independent dose measure.",
        "statistical_unit": "descriptive wrapper entries nested within object; no hypothesis tests, no treating wrappers as independent objects",
        "outputs": {"table": str(table.relative_to(ROOT)), "figure_png": str(png.relative_to(ROOT)), "figure_pdf": str(pdf.relative_to(ROOT))},
        "hashes": {"table": sha256(table), "figure_png": sha256(png), "figure_pdf": sha256(pdf)},
    }
    (OUT_AUDIT / "FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "source_sets"}, indent=2))


if __name__ == "__main__":
    main()
