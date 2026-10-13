#!/usr/bin/env python3
"""Score native EGL renders against frozen Fresh C views and depth maps."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = Path("/4T/CXY/MV-Painter")
DEFAULT_DEPTH_ROOT = PROJECT_ROOT / "1006/data/fresh_c/renders"
METRICS = ("fg_psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000", "silhouette_iou")
HIGHER_IS_BETTER = {
    "fg_psnr": True,
    "fg_ssim": True,
    "edge_ssim": True,
    "fg_lpips": False,
    "ciede2000": False,
    "silhouette_iou": True,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_rgba(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(path)
    image = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0
    if not np.isfinite(image).all():
        raise ValueError(f"non-finite RGBA pixels: {path}")
    return image


def to_tensor(image: np.ndarray, device: torch.device) -> torch.Tensor:
    return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1))).float().unsqueeze(0).to(device)


def bootstrap_mean_ci(values: np.ndarray, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(50_000, len(values)))
    means = values[indices].mean(axis=1)
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def load_metric_implementations() -> dict:
    sys.path.insert(0, str(PROJECT_ROOT))
    image_metrics = importlib.import_module("geotex.metrics.image_metrics")
    mask_ops = importlib.import_module("geotex.metrics.mask_ops")
    round2_texture = importlib.import_module("geotex.round2_texture")
    sources = {
        "image_metrics": PROJECT_ROOT / "geotex/metrics/image_metrics.py",
        "mask_ops": PROJECT_ROOT / "geotex/metrics/mask_ops.py",
        "round2_texture": PROJECT_ROOT / "geotex/round2_texture.py",
    }
    return {
        "compute_psnr": image_metrics.compute_psnr,
        "compute_ssim": image_metrics.compute_ssim,
        "get_lpips_fn": image_metrics.get_lpips_fn,
        "compute_lpips": image_metrics.compute_lpips,
        "compute_edge_mask": mask_ops.compute_edge_mask,
        "masked_ciede2000": round2_texture.masked_ciede2000,
        "source_hashes": {name: {"path": str(path), "sha256": sha256(path)} for name, path in sources.items()},
    }


def validate_render_manifest(render_dir: Path, run_identity: dict, objects: list[str],
                             methods: list[str], views: list[int]) -> dict:
    manifest_path = render_dir / "GLB_NATIVE_EGL_RENDER_MANIFEST.json"
    manifest = read_json(manifest_path)
    expected = {(uid, method, view) for uid in objects for method in methods for view in views}
    actual = {(row["object"], row["method"], int(row["raw_view"])) for row in manifest["renders"]}
    if actual != expected or manifest.get("render_count") != len(expected):
        raise RuntimeError(f"native EGL render coverage mismatch: expected {len(expected)}, got {len(actual)}")
    if manifest["renderer"].get("sampler_probe", {}).get("status") != "PASS":
        raise RuntimeError("native EGL sampler probe did not pass")
    if run_identity.get("status") != "COMPLETED" or run_identity.get("render_count") != len(expected):
        raise RuntimeError("native EGL wrapper identity is incomplete")
    if run_identity.get("render_manifest_sha256") != sha256(manifest_path):
        raise RuntimeError("native EGL wrapper identity does not match render manifest")
    for row in manifest["renders"]:
        path = render_dir / row["render_path"]
        if not path.is_file() or sha256(path) != row["render_sha256"]:
            raise RuntimeError(f"render file hash mismatch: {path}")
    return {"path": str(manifest_path), "sha256": sha256(manifest_path), "render_count": len(actual)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--objects", required=True)
    parser.add_argument("--methods", required=True)
    parser.add_argument("--views", default=",".join(str(i) for i in range(1, 12)))
    parser.add_argument("--view-role", choices=("auto", "unseen", "target", "custom"), default="auto")
    parser.add_argument("--depth-root", type=Path, default=DEFAULT_DEPTH_ROOT)
    parser.add_argument("--lpips-device", default="cuda:0")
    args = parser.parse_args()
    render_dir = args.render_dir.resolve()
    handoff_path = args.handoff.resolve()
    objects = [value.strip() for value in args.objects.split(",") if value.strip()]
    methods = [value.strip() for value in args.methods.split(",") if value.strip()]
    views = [int(value.strip()) for value in args.views.split(",") if value.strip()]
    if not objects or not methods or not views or "gt" not in methods:
        raise ValueError("objects, methods, and views must be non-empty, and methods must include gt")
    if len(set(views)) != len(views) or any(view < 0 or view >= 17 for view in views):
        raise ValueError("views must contain unique indices in the frozen 0–16 camera range")
    view_role = args.view_role
    if view_role == "auto":
        view_role = (
            "unseen" if set(views) == set(range(1, 12)) else
            "target" if set(views) == {0, 12, 13, 14, 15, 16} else
            "custom"
        )

    identity_path = render_dir.parent / f"{render_dir.name}_RUN_IDENTITY.json"
    run_identity = read_json(identity_path)
    render_manifest_identity = validate_render_manifest(render_dir, run_identity, objects, methods, views)
    handoff = read_json(handoff_path)
    input_freeze_value = handoff.get("input_freeze_manifest") or handoff.get("input_freeze_path")
    if not input_freeze_value:
        raise RuntimeError("handoff does not identify its frozen input manifest")
    input_freeze_path = Path(input_freeze_value)
    if not input_freeze_path.is_file() or sha256(input_freeze_path) != handoff["input_freeze_sha256"]:
        raise RuntimeError("frozen GLB bake input manifest is missing or its hash differs")
    records = {row["object"]: row for row in handoff["objects"]}
    if not set(objects) <= set(records):
        raise ValueError("requested objects are not all in the frozen bake handoff")
    if view_role == "target":
        for uid in objects:
            target_views = {int(row["raw_view_index"]) for row in records[uid]["target_view_mapping"]}
            if target_views != set(views):
                raise ValueError(f"requested views do not match frozen target cameras for {uid}")

    metric_impl = load_metric_implementations()
    device = torch.device(args.lpips_device if args.lpips_device != "auto" else
                          ("cuda:0" if torch.cuda.is_available() else "cpu"))
    if device.type == "cuda" and not torch.cuda.is_available():
        device = torch.device("cpu")
    lpips_model = None
    lpips_status = "unavailable"
    try:
        lpips_model = metric_impl["get_lpips_fn"](device)
        lpips_status = "available" if lpips_model is not None else "package_or_weights_unavailable"
    except Exception as exc:  # Keep non-learned metrics available if LPIPS cannot initialize.
        lpips_status = f"unavailable: {type(exc).__name__}: {exc}"

    per_view = []
    object_rows = []
    depth_hashes = {}
    gt_hashes = {}
    for uid in objects:
        record = records[uid]
        source_uid = record.get("source_uid", record["object"])
        for method in methods:
            method_dir = render_dir / method / uid
            metadata = read_json(method_dir / "bake_metadata.json")
            per_method_views = []
            for view in views:
                pred_rgba = load_rgba(method_dir / "unseen_renders" / f"view_{view:03d}.png")
                gt_path = Path(record["gt_rgba_17"][view])
                gt_rgba = load_rgba(gt_path)
                gt_hashes[str(gt_path)] = sha256(gt_path)
                if pred_rgba.shape != gt_rgba.shape:
                    raise ValueError(f"render/GT shape mismatch: {pred_rgba.shape} vs {gt_rgba.shape}")
                gt_rgb = gt_rgba[:, :, :3] * gt_rgba[:, :, 3:4] + (1.0 - gt_rgba[:, :, 3:4])
                pred_rgb = pred_rgba[:, :, :3]
                gt_mask = gt_rgba[:, :, 3]
                mask_t = torch.from_numpy((gt_mask > 0.5).astype(np.float32))[None, None].to(device)
                pred_t = to_tensor(pred_rgb, device)
                target_t = to_tensor(gt_rgb, device)

                depth_path = args.depth_root.resolve() / source_uid / "depth_png" / f"{view:03d}.png"
                depth_rgba = np.asarray(Image.open(depth_path), dtype=np.float32) / 65535.0
                if depth_rgba.ndim == 3:
                    depth_rgba = depth_rgba[:, :, 0]
                if depth_rgba.shape != gt_mask.shape:
                    raise ValueError(f"depth/GT shape mismatch: {depth_rgba.shape} vs {gt_mask.shape}")
                depth_hashes[f"{source_uid}/{view:03d}.png"] = sha256(depth_path)
                depth_t = torch.from_numpy(depth_rgba)[None, None].to(device)
                edge_t = metric_impl["compute_edge_mask"](depth_t, threshold=0.1) * mask_t

                values = {
                    "fg_psnr": float(metric_impl["compute_psnr"](pred_t, target_t, mask_t)),
                    "fg_ssim": float(metric_impl["compute_ssim"](pred_t, target_t, mask_t)),
                    "edge_ssim": float(metric_impl["compute_ssim"](pred_t, target_t, edge_t)),
                    "fg_lpips": (
                        float(metric_impl["compute_lpips"](pred_t, target_t, mask_t, lpips_fn=lpips_model,
                                                             device=device))
                        if lpips_model is not None else float("nan")
                    ),
                    "ciede2000": float(metric_impl["masked_ciede2000"](pred_rgb, gt_rgb, gt_mask,
                                                                          erosion_radius=1)),
                    "silhouette_iou": float(
                        np.logical_and(pred_rgba[:, :, 3] > 0.5, gt_mask > 0.5).sum()
                        / max(np.logical_or(pred_rgba[:, :, 3] > 0.5, gt_mask > 0.5).sum(), 1)
                    ),
                    "gt_foreground_coverage": float((gt_mask > 0.5).mean()),
                    "render_foreground_coverage": float((pred_rgba[:, :, 3] > 0.5).mean()),
                }
                row = {"object_uid": uid, "method": method, "raw_view": view, **values}
                per_view.append(row)
                per_method_views.append(row)
            object_row = {"object_uid": uid, "method": method, f"{view_role}_views": len(views)}
            for metric in METRICS:
                vals = np.asarray([row[metric] for row in per_method_views], dtype=np.float64)
                finite = vals[np.isfinite(vals)]
                object_row[metric] = float(finite.mean()) if len(finite) else None
            for metadata_key in ("texture_coverage", "cross_view_texel_variance", "uv_seam_discontinuity"):
                object_row[metadata_key] = metadata.get(metadata_key)
            object_rows.append(object_row)

    by_uid_method = {(row["object_uid"], row["method"]): row for row in object_rows}
    metric_summary = {}
    for method in methods:
        metric_summary[method] = {}
        for metric_idx, metric in enumerate(METRICS):
            object_values = [by_uid_method[(uid, method)][metric] for uid in objects]
            finite_values = [float(value) for value in object_values
                             if value is not None and np.isfinite(float(value))]
            values = np.asarray(finite_values, dtype=np.float64)
            metric_summary[method][metric] = {
                "n_objects": len(values),
                "mean_object_mean": float(values.mean()) if len(values) else None,
                "median_object_mean": float(np.median(values)) if len(values) else None,
                "sd_object_mean": float(values.std(ddof=1)) if len(values) > 1 else None,
                "object_bootstrap_95ci": bootstrap_mean_ci(values, 20261010 + metric_idx + methods.index(method) * 31)
                if len(values) else None,
                "object_values": {uid: by_uid_method[(uid, method)][metric] for uid in objects},
            }

    paired = {}
    for baseline in ("native_gc3", "budget_fixed_mean"):
        if baseline not in methods:
            continue
        paired[baseline] = {}
        for method in methods:
            if method in (baseline, "gt"):
                continue
            paired[baseline][method] = {}
            for metric_idx, metric in enumerate(METRICS):
                object_deltas = {}
                for uid in objects:
                    left = by_uid_method[(uid, method)][metric]
                    right = by_uid_method[(uid, baseline)][metric]
                    if left is None or right is None or not np.isfinite(float(left) + float(right)):
                        object_deltas[uid] = None
                        continue
                    object_deltas[uid] = float(left) - float(right)
                valid = [(uid, value) for uid, value in object_deltas.items() if value is not None]
                deltas = np.asarray([value for _, value in valid], dtype=np.float64)
                if not HIGHER_IS_BETTER[metric]:
                    deltas = -deltas
                paired[baseline][method][metric] = {
                    "n_objects": len(deltas),
                    "mean_oriented_delta": float(deltas.mean()) if len(deltas) else None,
                    "object_bootstrap_95ci": bootstrap_mean_ci(
                        deltas, 20261011 + metric_idx + methods.index(method) * 47
                    ) if len(deltas) else None,
                    "object_values_oriented": {
                        uid: (None if value is None else float(value) * (1 if HIGHER_IS_BETTER[metric] else -1))
                        for uid, value in object_deltas.items()
                    },
                }

    output_stem = f"NATIVE_EGL_{view_role.upper()}"
    per_view_path = render_dir / f"{output_stem}_PER_VIEW_METRICS.csv"
    object_path = render_dir / f"{output_stem}_OBJECT_METRICS.csv"
    with per_view_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_view[0]))
        writer.writeheader()
        writer.writerows(per_view)
    with object_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(object_rows[0]))
        writer.writeheader()
        writer.writerows(object_rows)

    wrapper_identity_path = render_dir.parent / f"{render_dir.name}_RUN_IDENTITY.json"
    output = {
        "protocol": f"fresh-c-native-egl-{view_role}-metrics-v1",
        "status": "COMPLETED_EXPLORATORY_METRIC_ANALYSIS",
        "evidence_grade": "EXPLORATORY_TECHNICAL_COHORT",
        "render_dir": str(render_dir),
        "render_run_identity_path": str(wrapper_identity_path),
        "render_run_identity_sha256": sha256(wrapper_identity_path),
        "render_manifest": render_manifest_identity,
        "handoff_path": str(handoff_path),
        "handoff_sha256": sha256(handoff_path),
        "input_freeze_manifest_path": str(input_freeze_path),
        "input_freeze_manifest_sha256": sha256(input_freeze_path),
        "objects": objects,
        "methods": methods,
        "raw_views": views,
        "view_role": view_role,
        "n_objects": len(objects),
        "n_views_per_object_method": len(views),
        "metric_source_hashes": metric_impl["source_hashes"],
        "depth_root": str(args.depth_root.resolve()),
        "depth_png_sha256": depth_hashes,
        "gt_rgba_sha256": gt_hashes,
        "lpips": {"status": lpips_status, "device": str(device)},
        "metrics": METRICS,
        "mask_protocol": "GT RGBA alpha > 0.5; FG PSNR/SSIM/LPIPS use the frozen image_metrics module; CIEDE2000 uses round2_texture with erosion_radius=1; edge mask is frozen depth Sobel threshold 0.1 multiplied by the GT foreground mask.",
        "summary_unit": "Per-view metrics are averaged within each object before object-level summaries and paired bootstrap; views are not treated as independent samples.",
        "condition_metric_means": metric_summary,
        "paired_object_contrasts": paired,
        "texture_export_diagnostics_by_object_method": [
            {key: row[key] for key in ("object_uid", "method", "texture_coverage", "cross_view_texel_variance", "uv_seam_discontinuity")}
            for row in object_rows
        ],
        "limitations": [
            "The cohort is selected for GLB/material/camera compatibility and remains exploratory.",
            "The EGL shader evaluates embedded baseColor texture with the GLB sampler and is unlit; it is not a full PBR or human-fidelity evaluation.",
            "The gt method is a source-texture/render alignment sanity condition, not a learned method advantage claim.",
            "No primary endpoint was designated before outputs; all metric contrasts are exploratory.",
            *(["Target-view renders overlap the six views used as model inputs; these metrics describe in-sample target-view fidelity, not novel-view generalization."] if view_role == "target" else []),
        ],
        "per_view_metrics_path": str(per_view_path),
        "per_view_metrics_sha256": sha256(per_view_path),
        "object_metrics_path": str(object_path),
        "object_metrics_sha256": sha256(object_path),
        "evaluation_script_path": str(Path(__file__).resolve()),
        "evaluation_script_sha256": sha256(Path(__file__).resolve()),
    }
    report_path = render_dir / "NATIVE_EGL_METRIC_EVALUATION.json"
    report_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    report_md = [
        f"# Fresh C native GLB EGL: exploratory {view_role}-view metrics",
        "",
        f"{len(objects)} objects × {len(views)} {view_role} views × {len(methods)} methods; metrics were averaged over views within each object.",
    ]
    if view_role == "target":
        report_md += [
            "",
            "Target-camera renders overlap the six images used as model inputs. Treat these as in-sample target-view fidelity, not novel-view generalization.",
        ]
    report_md += [
        "",
        "The EGL shader samples the exported GLB baseColor texture using the embedded glTF sampler. The render is unlit and texture-only; results do not claim full PBR fidelity.",
        "",
        "| Method | FG-PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-LPIPS ↓ | CIEDE2000 ↓ | Silhouette IoU ↑ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in methods:
        columns = [metric_summary[method][metric]["mean_object_mean"] for metric in METRICS]
        report_md.append("| " + method + " | " + " | ".join("n/a" if value is None else f"{value:.4f}" for value in columns) + " |")
    report_md += ["", f"LPIPS status: `{lpips_status}` on `{device}`. Detailed per-object paired contrasts and render/depth hashes are in `{report_path.name}`."]
    (render_dir / "NATIVE_EGL_METRIC_EVALUATION.md").write_text("\n".join(report_md) + "\n")
    print(json.dumps({"status": output["status"], "objects": len(objects), "views": len(views),
                      "methods": len(methods), "lpips": lpips_status, "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
