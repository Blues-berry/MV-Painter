"""Identity audit analysis: layer-wise runner (multipliers=1.0) vs global runner.

Compares PNG bytes, pixel equality, max absolute pixel difference and CSV
metrics between:
  A = results/identity_audit_global                (unmodified global runner)
  B = results/identity_audit_layerwise_identity    (wrapper, --identity)
and additionally reports reproducibility of the archived 76-object grids.

Emits identity_audit_result.json and MVADAPTER_LAYERWISE_IDENTITY_AUDIT.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

METRIC_FIELDS = [
    "psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
    "gt_relative_texture_error",
]

# The wrapper canonicalizes labels (LHL -> L-LHL, LLH -> L-LLH); the global
# runner and the archived records keep the original names.
IDENTITY_LABEL_FOR = {"FIXED_MEAN": "L-FIX", "LHL": "L-LHL", "LLH": "L-LLH"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> dict[tuple[str, str], dict[str, float]]:
    rows: dict[tuple[str, str], dict[str, float]] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["object"], row["schedule"])
            rows[key] = {field: float(row[field]) for field in METRIC_FIELDS}
    return rows


def compare_pair(path_a: Path, path_b: Path) -> dict:
    if not path_a.is_file() or not path_b.is_file():
        return {"exists": False, "png_sha_equal": False}
    a_sha, b_sha = sha256_file(path_a), sha256_file(path_b)
    arr_a = np.asarray(Image.open(path_a).convert("RGB"))
    arr_b = np.asarray(Image.open(path_b).convert("RGB"))
    if arr_a.shape != arr_b.shape:
        return {
            "exists": True, "png_sha_equal": a_sha == b_sha,
            "pixel_equal": False, "shape_mismatch": True,
            "max_abs_pixel_diff": None,
            "png_sha_a": a_sha, "png_sha_b": b_sha,
        }
    diff = np.abs(arr_a.astype(np.int16) - arr_b.astype(np.int16))
    return {
        "exists": True,
        "png_sha_equal": a_sha == b_sha,
        "pixel_equal": bool(np.array_equal(arr_a, arr_b)),
        "max_abs_pixel_diff": int(diff.max()),
        "png_sha_a": a_sha,
        "png_sha_b": b_sha,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mv-adapter-dir", type=Path,
                        default=Path("final/round2/mv_adapter"))
    parser.add_argument("--dir-a", type=Path, default=None,
                        help="global runner output (default: <dir>/results/identity_audit_global)")
    parser.add_argument("--dir-b", type=Path, default=None,
                        help="layer-wise identity output (default: <dir>/results/identity_audit_layerwise_identity)")
    parser.add_argument("--objects", nargs="+", required=True)
    parser.add_argument("--schedules", nargs="+", required=True)
    args = parser.parse_args()

    base = args.mv_adapter_dir
    dir_a = args.dir_a or base / "results" / "identity_audit_global"
    dir_b = args.dir_b or base / "results" / "identity_audit_layerwise_identity"

    archived_for = {
        "fixed_low": base / "results" / "holdout_exact_76",
        "LHL": base / "results" / "holdout_exact_lhl_shape_transfer_76",
        "LLH": base / "results" / "holdout_exact_equal_budget_76",
    }

    csv_a = load_csv(dir_a / "per_object_metrics.csv")
    csv_b = load_csv(dir_b / "per_object_metrics.csv")

    per_case = []
    for schedule in args.schedules:
        id_label = IDENTITY_LABEL_FOR.get(schedule, schedule)
        for object_id in args.objects:
            entry = {"schedule": schedule, "identity_label": id_label,
                     "object": object_id}
            entry["global_vs_identity"] = compare_pair(
                dir_a / "images" / schedule / f"{object_id}.png",
                dir_b / "images" / id_label / f"{object_id}.png",
            )
            if schedule in archived_for:
                entry["global_vs_archived"] = compare_pair(
                    dir_a / "images" / schedule / f"{object_id}.png",
                    archived_for[schedule] / "images" / schedule / f"{object_id}.png",
                )
            key_a = (object_id, schedule)
            key_b = (object_id, id_label)
            if key_a in csv_a and key_b in csv_b:
                metric_diffs = {
                    field: abs(csv_a[key_a][field] - csv_b[key_b][field])
                    for field in METRIC_FIELDS
                }
                entry["metric_max_abs_diff"] = max(metric_diffs.values())
                entry["metric_equal"] = all(v == 0.0 for v in metric_diffs.values())
            else:
                entry["metric_max_abs_diff"] = None
                entry["metric_equal"] = False
                entry["metric_missing"] = True
            per_case.append(entry)

    config_b_path = dir_b / "run_config.json"
    diagnostics = None
    if config_b_path.is_file():
        diagnostics = json.loads(config_b_path.read_text()).get("cond_encoder_diagnostics")

    identity_checks = {
        "all_png_sha_equal": all(c["global_vs_identity"].get("png_sha_equal") for c in per_case),
        "all_pixel_equal": all(c["global_vs_identity"].get("pixel_equal") for c in per_case),
        "all_max_abs_pixel_diff_zero": all(
            c["global_vs_identity"].get("max_abs_pixel_diff") == 0 for c in per_case
        ),
        "all_metrics_equal": all(c["metric_equal"] for c in per_case),
        "all_cases_present": all(
            c["global_vs_identity"].get("exists") and not c.get("metric_missing")
            for c in per_case
        ),
    }
    if diagnostics is not None:
        identity_checks["cond_encoder_features_count_ok"] = (
            diagnostics.get("adapter_state_shapes") is not None
            and len(diagnostics["adapter_state_shapes"]) == 4
        )
        ratios = diagnostics.get("first_call_norm_ratios") or []
        identity_checks["norm_ratios_are_one"] = len(ratios) == 4 and all(
            abs(r - 1.0) < 1e-6 for r in ratios
        )
    verdict = "PASS" if all(identity_checks.values()) else "FAIL"

    result = {
        "audit": "MVADAPTER_LAYERWISE_IDENTITY_AUDIT",
        "verdict": verdict,
        "identity_checks": identity_checks,
        "cond_encoder_diagnostics": diagnostics,
        "expected_shapes_note": "batch B=12 (6 views x CFG); expected feature shapes [B,320,64,64],[B,640,32,32],[B,1280,16,16],[B,1280,8,8] at 512x512",
        "cases": per_case,
    }
    out_json = dir_b / "identity_audit_result.json"
    out_json.write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# MV-Adapter Layer-wise Identity Audit",
        "",
        "Comparison A = global runner (`run_experiment.py`) vs B = layer-wise wrapper",
        "(`run_layerwise_experiment.py --identity`, all multipliers = 1.0).",
        f"Objects: {', '.join(args.objects)}. Schedules: {', '.join(args.schedules)}.",
        "Seed 20260928, 50 steps, low 0.75, high 1.00, exact meshes, same GPU.",
        "",
        f"**IDENTITY_AUDIT = {verdict}**",
        "",
        "| check | result |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in identity_checks.items()]
    if diagnostics:
        lines += [
            "",
            "## cond_encoder diagnostics (first wrapped call)",
            "",
            f"- adapter_state shapes: `{diagnostics.get('adapter_state_shapes')}`",
            f"- input norms: `{diagnostics.get('first_call_input_norms')}`",
            f"- scaled norms: `{diagnostics.get('first_call_scaled_norms')}`",
            f"- norm ratios (must be 1.0): `{diagnostics.get('first_call_norm_ratios')}`",
        ]
    lines += [
        "",
        "## Per-case detail",
        "",
        "| schedule | object | PNG SHA equal | pixel equal | max abs diff | metrics equal | archived SHA equal |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in per_case:
        g = c["global_vs_identity"]
        arch = c.get("global_vs_archived", {})
        lines.append(
            f"| {c['schedule']} | {c['object']} | {g.get('png_sha_equal')} "
            f"| {g.get('pixel_equal')} | {g.get('max_abs_pixel_diff')} "
            f"| {c['metric_equal']} | {arch.get('png_sha_equal', 'n/a')} |"
        )
    out_md = dir_b / "MVADAPTER_LAYERWISE_IDENTITY_AUDIT.md"
    out_md.write_text("\n".join(lines) + "\n")
    print(f"IDENTITY_AUDIT = {verdict}")
    print(f"json: {out_json}\nmd:   {out_md}")


if __name__ == "__main__":
    main()
