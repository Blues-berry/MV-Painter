"""Generate MVADAPTER_LAYERWISE_76_REPORT.md + MVADAPTER_LAYERWISE_HASH_MANIFEST.json."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

METRICS = ["psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
           "gt_relative_texture_error"]
LABELS = ["R0", "G-FL", "G-LHL", "G-LLH", "L-FIX", "L-LLH", "L-LHL"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    base = Path(__file__).resolve().parent
    panel = list(csv.DictReader((base / "MVADAPTER_STANDARD_PANEL_76.csv").open(newline="")))
    boot = json.loads((base / "MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json").read_text())

    means = {}
    for label in LABELS:
        rows = [r for r in panel if r["condition"] == label]
        means[label] = {m: float(np.mean([float(r[m]) for r in rows])) for m in METRICS}

    ident = json.loads((base / "results/identity_audit_layerwise_identity/identity_audit_result.json").read_text())
    smoke = json.loads((base / "results/layerwise_smoke_3/layerwise_smoke_result.json").read_text())

    lines = [
        "# MV-Adapter Layer-wise 76-Object Report (Second Backbone)",
        "",
        "Experiment facts only. Branch `codex/next-review-response-20260930`,",
        "date 2026-09-30. Protocol: `MVADAPTER_LAYERWISE_PROTOCOL.md`",
        "(pre-registered); profile: `layer_profile_transfer.json` (frozen).",
        "",
        "## Gates",
        "",
        f"- IDENTITY_AUDIT = **{ident['verdict']}** (wrapper with multipliers = 1.0 is",
        "  bitwise identical to the global runner on 3 objects x G-FL/G-LHL/G-LLH;",
        "  PNG SHA-256, pixels, max abs diff 0, metrics equal; cond_encoder shapes",
        "  `[12,320,64,64],[12,640,32,32],[12,1280,16,16],[12,1280,8,8]`).",
        f"- SMOKE = **{smoke['verdict']}** (technical checks only).",
        "",
        "## New runs",
        "",
        "3 conditions x 76 objects = 228 new rows, all `exact_mesh`, all metrics",
        "finite: `holdout_exact_layer_fixed_76` (L-FIX), `holdout_exact_layer_llh_76`",
        "(L-LLH), `holdout_exact_layer_lhl_76` (L-LHL). Seed 20260928, 50 steps,",
        "low 0.75, high 1.00 (frozen; no recalibration).",
        "",
        "## Standard panel means (7 conditions)",
        "",
        "| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in LABELS:
        m = means[label]
        lines.append(
            f"| {label} | {m['psnr']:.6f} | {m['fg_ssim']:.6f} | {m['edge_ssim']:.6f} "
            f"| {m['fg_lpips']:.6f} | {m['ciede2000']:.6f} | {m['gt_relative_texture_error']:.6f} |"
        )
    lines += [
        "",
        "## Paired comparisons (10,000 object bootstrap, seed 20260928)",
        "",
        "Deltas direction-adjusted so positive favors the left condition",
        "(LPIPS/dE00/GT-texture are lower-better). * = 95% CI excludes 0.",
        "",
        "| comparison | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    star = lambda s: "*" if s["ci_excludes_zero"] else ""
    for comp_name in ["P1_L-LLH_vs_G-FL", "P2_L-LLH_vs_G-LLH", "P3_L-LLH_vs_L-FIX",
                      "P4_L-LHL_vs_G-LHL", "P5_G-LLH_vs_G-LHL"]:
        cells = []
        for m in METRICS:
            s = boot["comparisons"][comp_name]["metrics"][m]
            cells.append(f"{s['paired_mean_delta']:+.4f}{star(s)} [{s['ci95_low']:+.4f},{s['ci95_high']:+.4f}]")
        lines.append(f"| {comp_name} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Full mean/median/CI/win-rate records: `MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json`.",
        "",
        "## Reading (experiment-level conclusion, no paper edits)",
        "",
        "- Layer-wise vs global (P1, P2, P4): PSNR, dE00 and GT-relative texture",
        "  error consistently favor the layer-wise conditions (CI excludes 0 for",
        "  all three pairs); FG-SSIM and Edge-SSIM consistently favor global by a",
        "  small margin; FG-LPIPS is not separated. The layer-wise effect exists",
        "  (SUPPORTED) but its direction is metric-dependent.",
        "- Temporal-position effect within the frozen scales (P3 L-LLH vs L-FIX,",
        "  P5 G-LLH vs G-LHL): not separated except a marginal dE00 term in P3.",
        "  (NOT_SUPPORTED at this protocol.)",
        "- Per task §42 these are reported as found; no re-search was performed.",
    ]
    (base / "MVADAPTER_LAYERWISE_76_REPORT.md").write_text("\n".join(lines) + "\n")

    # hash manifest
    files = [
        "MVADAPTER_LAYERWISE_PROTOCOL.md",
        "layer_profile_transfer.json",
        "run_layerwise_experiment.py",
        "analyze_layerwise_identity_audit.py",
        "analyze_layerwise_smoke.py",
        "analyze_layerwise_panel_20260930.py",
        "build_layerwise_report_20260930.py",
        "MVADAPTER_STANDARD_PANEL_76.csv",
        "MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json",
        "MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP_SUMMARY.md",
        "MVADAPTER_LAYERWISE_76_REPORT.md",
        "results/identity_audit_global/per_object_metrics.csv",
        "results/identity_audit_layerwise_identity/per_object_metrics.csv",
        "results/identity_audit_layerwise_identity/MVADAPTER_LAYERWISE_IDENTITY_AUDIT.md",
        "results/layerwise_smoke_3/per_object_metrics.csv",
        "results/layerwise_smoke_3/MVADAPTER_LAYERWISE_SMOKE.md",
        "results/holdout_exact_layer_fixed_76/per_object_metrics.csv",
        "results/holdout_exact_layer_lhl_76/per_object_metrics.csv",
        "results/holdout_exact_layer_llh_76/per_object_metrics.csv",
    ]
    manifest = {
        "protocol": "mvadapter-layerwise-hash-manifest-v1",
        "date": "2026-09-30",
        "files": {f: sha256_file(base / f) for f in files},
        "new_image_grid_counts": {
            cond: len(list((base / "results" / d / "images" / lab).glob("*.png")))
            for cond, d, lab in [
                ("L-FIX", "holdout_exact_layer_fixed_76", "L-FIX"),
                ("L-LHL", "holdout_exact_layer_lhl_76", "L-LHL"),
                ("L-LLH", "holdout_exact_layer_llh_76", "L-LLH"),
            ]
        },
    }
    (base / "MVADAPTER_LAYERWISE_HASH_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("report + manifest written")
    print(json.dumps(manifest["new_image_grid_counts"]))


if __name__ == "__main__":
    main()
