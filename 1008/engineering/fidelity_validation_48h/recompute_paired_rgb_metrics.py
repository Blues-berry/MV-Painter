#!/usr/bin/env python3
"""Recompute paired color/detail metrics from frozen Fresh C, Fresh B, and R1 PNGs.

This is a CPU-only post-processing pass. It does not load a model or modify any
source image. Prediction files are verified against the campaign's SHA-256
manifest before they are read. The target panel reconstruction follows the
frozen dataset path: RGBA-to-white compositing, unique6 selection/reordering,
reverse-view rotations, bicubic antialiased resize, and a 3x2 view montage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image
from scipy.ndimage import convolve, minimum_filter
from skimage.color import deltaE_ciede2000, rgb2lab
from torchvision.transforms import v2
from torchvision.transforms.functional import rotate


DEFAULT_FRESHC_ROOT = Path("/4T/CXY/MV-Painter/1006/data/fresh_c")
DEFAULT_FRESHB_ROOT = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3")
DEFAULT_FRESHB_RENDER_ROOT = Path("/4T/CXY/MV-Painter/data/fresh_confirm_v3_renders")
DEFAULT_DIAGNOSTIC_CSV = Path(
    "/4T/CXY/MV-Painter-r1color/1008/engineering/color_failure/final_closure/"
    "COLOR_FIDELITY_PAIRED_RESULTS.csv"
)
DEFAULT_FRESHC_MANIFEST = Path(
    "/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/"
    "FRESH_C_COHORT_MANIFEST.json"
)

TARGETS_NORMAL = [0, 15, 12, 16, 13, 14]
TARGETS_REVERSED = [14, 15, 0, 16, 12, 13]
LAPLACIAN_CROSS = np.array([[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float32)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row.keys()))
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def read_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def reconstruct_target(render_dir: Path) -> tuple[torch.Tensor, torch.Tensor, list[int], bool, str]:
    """Return float RGB/mask panels as [C,H,W], plus exact source identity."""
    first = read_rgba(render_dir / "image" / "000.png")
    fourth = read_rgba(render_dir / "image" / "014.png")
    reverse = int(np.count_nonzero(first[:, :, 3] == 0)) > int(np.count_nonzero(fourth[:, :, 3] == 0))
    target_ids = TARGETS_REVERSED if reverse else TARGETS_NORMAL

    rgb_views: list[torch.Tensor] = []
    alpha_views: list[torch.Tensor] = []
    source_digest = hashlib.sha256()
    for view_id in target_ids:
        path = render_dir / "image" / f"{view_id:03d}.png"
        rgba = read_rgba(path)
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
        rgb = rgb * alpha + (1.0 - alpha)
        rgb_views.append(torch.from_numpy(rgb).permute(2, 0, 1).contiguous())
        alpha_views.append(torch.from_numpy(alpha).permute(2, 0, 1).contiguous())
        source_digest.update(f"{view_id:03d}.png\0".encode())
        source_digest.update(bytes.fromhex(sha256_file(path)))

    if reverse:
        # MVPainterData rotates target view slots 1 and 3 by +90 degrees.
        for slot in (1, 3):
            rgb_views[slot] = rotate(rgb_views[slot], angle=90)
            alpha_views[slot] = rotate(alpha_views[slot], angle=90)

    rgb = v2.functional.resize(
        torch.stack(rgb_views), 256, interpolation=3, antialias=True
    ).clamp(0, 1)
    alpha = v2.functional.resize(
        torch.stack(alpha_views), 256, interpolation=3, antialias=True
    ).clamp(0, 1)

    # Exact layout of prepare_batch: six ordered views -> three rows by two columns.
    rgb_panel = rgb.reshape(3, 2, 3, 256, 256).permute(2, 0, 3, 1, 4).reshape(3, 768, 512).contiguous()
    mask_panel = alpha.reshape(3, 2, 1, 256, 256).permute(2, 0, 3, 1, 4).reshape(1, 768, 512).contiguous()
    return rgb_panel, mask_panel, list(target_ids), reverse, source_digest.hexdigest()


def unpack_panel(rgb_panel: np.ndarray, mask_panel: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Split a 3x2 montage into its six views, preserving row-major order."""
    if rgb_panel.shape[:2] != (768, 512) or mask_panel.shape[:2] != (768, 512):
        raise ValueError(f"Expected 768x512 panel; got RGB={rgb_panel.shape}, mask={mask_panel.shape}")
    views = []
    for i in range(6):
        row, col = divmod(i, 2)
        ys, xs = slice(row * 256, (row + 1) * 256), slice(col * 256, (col + 1) * 256)
        views.append((rgb_panel[ys, xs].astype(np.float32), mask_panel[ys, xs] > 0.5,
                      rgb_panel[ys, xs].astype(np.float32)))
    return views


def rgb_panel_to_metrics(pred_path: Path, target_panel: torch.Tensor, mask_panel: torch.Tensor) -> dict[str, float]:
    pred_u8 = np.asarray(Image.open(pred_path).convert("RGB"), dtype=np.uint8)
    if pred_u8.shape != (768, 512, 3):
        raise ValueError(f"Expected saved 768x512 RGB panel at {pred_path}, got {pred_u8.shape}")
    target = target_panel.permute(1, 2, 0).cpu().numpy().astype(np.float32)
    target_u8 = np.floor(np.clip(target, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    target = target_u8.astype(np.float32) / 255.0
    mask = mask_panel[0].cpu().numpy().astype(np.float32)
    mask_u8 = np.floor(np.clip(mask, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    if target.shape != pred_u8.shape[:2] + (3,):
        raise ValueError(f"Target/prediction panel shape mismatch for {pred_path}")

    ciede_by_view: list[float] = []
    delta_a_by_view: list[float] = []
    delta_b_by_view: list[float] = []
    hf_abs_sum = 0.0
    hf_weight = 0
    for view_idx in range(6):
        row, col = divmod(view_idx, 2)
        ys, xs = slice(row * 256, (row + 1) * 256), slice(col * 256, (col + 1) * 256)
        p = pred_u8[ys, xs].astype(np.float32) / 255.0
        t = target[ys, xs]
        m = mask_u8[ys, xs] > 127
        if not m.any():
            continue
        plab = rgb2lab(p)
        tlab = rgb2lab(t)
        de = deltaE_ciede2000(plab, tlab)
        ciede_by_view.append(float(de[m].mean()))
        delta_a_by_view.append(float((plab[:, :, 1] - tlab[:, :, 1])[m].mean()))
        delta_b_by_view.append(float((plab[:, :, 2] - tlab[:, :, 2])[m].mean()))

        eroded = minimum_filter(m.astype(np.uint8), size=3, mode="constant", cval=0) > 0
        if eroded.any():
            p_lap = np.stack([convolve(p[:, :, c], LAPLACIAN_CROSS, mode="reflect") for c in range(3)], axis=2)
            t_lap = np.stack([convolve(t[:, :, c], LAPLACIAN_CROSS, mode="reflect") for c in range(3)], axis=2)
            hf_abs_sum += float(np.abs(p_lap - t_lap)[eroded].sum())
            hf_weight += int(eroded.sum()) * 3

    if not ciede_by_view or hf_weight == 0:
        raise ValueError(f"Empty foreground mask for {pred_path}")
    return {
        "fg_ciede2000_rgb": float(np.mean(ciede_by_view)),
        "signed_mean_delta_a_star": float(np.mean(delta_a_by_view)),
        "signed_mean_delta_b_star": float(np.mean(delta_b_by_view)),
        "gt_relative_laplacian_error_rgb": hf_abs_sum / hf_weight,
    }


def parse_b_preunblind_hashes(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and len(parts[0]) == 64:
            result[parts[1].lstrip("* ")] = parts[0]
    return result


def load_runner_rows(run_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    result = {}
    for path in sorted(run_dir.glob("rows_shard*.json")):
        for row in load_json(path):
            result[(row["object_uid"], row["condition"])] = row
    return result


def residual_summary(path: Path) -> dict[str, float]:
    data = load_json(path)
    by_group: dict[str, list[float]] = {"deep": [], "middle": [], "shallow": []}
    l2_values = []
    scales: dict[str, list[float]] = {"deep": [], "middle": [], "shallow": []}
    for step in data.values():
        for entry in step.values():
            group = entry.get("depth")
            if group not in by_group:
                continue
            by_group[group].append(float(entry.get("mean_abs", 0.0)))
            scales[group].append(float(entry.get("eff_scale", entry.get("scale", 0.0))))
            l2_values.append(float(entry.get("l2", 0.0)))
    out: dict[str, float] = {
        "residual_l2_sum_descriptive": float(sum(l2_values)),
        "residual_module_calls": float(len(l2_values)),
    }
    for group in by_group:
        out[f"residual_mean_abs_{group}_mean"] = float(np.mean(by_group[group])) if by_group[group] else float("nan")
        out[f"residual_effective_scale_{group}_mean"] = float(np.mean(scales[group])) if scales[group] else float("nan")
    return out


def condition_metric_map(path: Path, uid_field: str = "object_uid") -> dict[tuple[str, str], dict[str, str]]:
    return {(r[uid_field], r["condition"]): r for r in load_csv(path)}


def main() -> None:
    torch.set_num_threads(4)
    ap = argparse.ArgumentParser()
    ap.add_argument("--freshc-root", type=Path, default=DEFAULT_FRESHC_ROOT)
    ap.add_argument("--freshc-manifest", type=Path, default=DEFAULT_FRESHC_MANIFEST)
    ap.add_argument("--freshb-validation-root", type=Path, default=DEFAULT_FRESHB_ROOT)
    ap.add_argument("--freshb-render-root", type=Path, default=DEFAULT_FRESHB_RENDER_ROOT)
    ap.add_argument("--diagnostic-csv", type=Path, default=DEFAULT_DIAGNOSTIC_CSV)
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    partial_metrics = args.output_dir / "RGB_RECOMPUTED_CONDITION_METRICS.partial.csv"
    partial_audit = args.output_dir / "RGB_HASH_AND_INPUT_AUDIT.partial.csv"
    for partial in (partial_metrics, partial_audit):
        partial.unlink(missing_ok=True)

    diagnostic_rows = load_csv(args.diagnostic_csv)
    diagnostic_uids = {r["uid"] for r in diagnostic_rows}
    c_manifest = load_json(args.freshc_manifest)
    c_objects = {o["uid"]: o for o in c_manifest["objects"]}
    c_primary = args.freshc_root / "runs" / "c3_confirmation"
    c_addendum = args.freshc_root / "runs" / "revision_era_addendum"
    c_hash_rows = load_csv(c_primary / "OUTPUT_FILE_SHA256.csv") + load_csv(c_addendum / "OUTPUT_FILE_SHA256.csv")
    c_prediction_hashes = {(r["condition"], r["uid"]): r["sha256"] for r in c_hash_rows if r["kind"] == "prediction"}
    c_metrics = condition_metric_map(c_primary / "per_object_metrics.csv")
    c_metrics.update(condition_metric_map(c_addendum / "per_object_metrics.csv"))
    c_input_rows = load_runner_rows(c_primary) | load_runner_rows(c_addendum)
    for run_dir, condition in ((c_primary, "native_gfl"), (c_addendum, "layer_llh")):
        manifest = load_json(run_dir / "run_manifest_shard0.json")
        for (uid, row_condition), row in c_input_rows.items():
            if row_condition == condition:
                row["checkpoint_sha256"] = manifest.get("checkpoint_sha256", "")
                row["runner_sha256"] = manifest.get("runner_script_sha256", "")

    b_run = args.freshb_validation_root / "formal" / "campaign_FRESH_CONFIRM_B_20261005"
    b_manifest_path = args.freshb_validation_root / "fresh_confirm_b" / "FRESH_CONFIRM_B_MANIFEST.json"
    b_manifest = load_json(b_manifest_path)
    b_objects = {o["source_uid"]: o for o in b_manifest["objects"]}
    b_rows = condition_metric_map(b_run / "per_object_metrics.csv")
    b_input_rows = load_runner_rows(b_run)
    b_run_manifest = load_json(b_run / "run_manifest_shard0.json")
    for row in b_input_rows.values():
        row["checkpoint_sha256"] = b_run_manifest.get("checkpoint_sha256", "")
        row["runner_sha256"] = b_run_manifest.get("runner_script_sha256", "")
    b_preunblind = parse_b_preunblind_hashes(args.freshb_validation_root / "B_PREUNBLIND_SHA256SUMS.txt")

    output_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    def append_cohort_row(cohort: str, uid: str, obj_idx: int, render_dir: Path,
                          condition: str, pred_path: Path, metric_row: dict[str, str], input_row: dict[str, Any],
                          expected_prediction_sha: str | None, manifest_file_hashes: dict[str, str] | None = None,
                          external_output_relpath: str | None = None) -> None:
        pred_sha = sha256_file(pred_path)
        if expected_prediction_sha and pred_sha != expected_prediction_sha:
            raise ValueError(f"prediction SHA mismatch: {pred_path}")
        if external_output_relpath and b_preunblind.get(external_output_relpath) != pred_sha:
            raise ValueError(f"Fresh B pre-unblind SHA mismatch: {external_output_relpath}")

        target_panel, mask_panel, target_ids, reversed_view, source_sha = reconstruct_target(render_dir)
        if manifest_file_hashes is not None:
            for view_id in target_ids:
                rel = f"image/{view_id:03d}.png"
                expected = manifest_file_hashes.get(rel)
                actual = sha256_file(render_dir / rel)
                if expected != actual:
                    raise ValueError(f"Fresh C GT image hash mismatch {uid}/{rel}")

        metrics = rgb_panel_to_metrics(pred_path, target_panel, mask_panel)
        input_hashes = input_row.get("input_hashes", {})
        output_rows.append({
            "cohort": cohort,
            "uid": uid,
            "object_idx": obj_idx,
            "object_seed": 42 + obj_idx,
            "condition": condition,
            "target_view_ids": json.dumps(target_ids),
            "reverse_view_rotation": reversed_view,
            "checkpoint_sha256": input_row.get("checkpoint_sha256", ""),
            "runner_sha256": input_row.get("runner_sha256", ""),
            "target_tensor_sha256_logged": input_hashes.get("target", ""),
            "prediction_png": str(pred_path),
            "prediction_sha256": pred_sha,
            "gt_render_dir": str(render_dir),
            "gt_selected_source_files_digest_sha256": source_sha,
            "fg_psnr_recorded": metric_row.get("fg_psnr", ""),
            "fg_lpips_recorded": metric_row.get("fg_lpips", ""),
            "fg_ssim_recorded": metric_row.get("fg_ssim", ""),
            "edge_ssim_recorded": metric_row.get("edge_ssim", ""),
            "gt_fg_lap_var": metric_row.get("gt_fg_lap_var", ""),
            "gt_fg_hf_energy": metric_row.get("gt_fg_hf_energy", ""),
            "gt_fg_grad_mag": metric_row.get("gt_fg_grad_mag", ""),
            "gt_fg_rgb_std": metric_row.get("gt_fg_rgb_std", ""),
            "crop_area": metric_row.get("crop_area", ""),
            **metrics,
        })
        audit_rows.append({
            "cohort": cohort,
            "uid": uid,
            "condition": condition,
            "prediction_png": str(pred_path),
            "prediction_sha256_actual": pred_sha,
            "prediction_sha256_manifest": expected_prediction_sha or (b_preunblind.get(external_output_relpath, "") if external_output_relpath else ""),
            "output_sha_pass": True,
            "gt_selected_source_files_digest_sha256": source_sha,
            "gt_files_verified_against_cohort_manifest": manifest_file_hashes is not None,
            "logged_target_tensor_sha256": input_hashes.get("target", ""),
            "target_views": json.dumps(target_ids),
            "reverse_view_rotation": reversed_view,
        })

    # Fresh C: the native GFL result belongs to primary run; LLH belongs to the
    # separately frozen addendum. Their inputs are joined by UID and tensor hashes.
    ordered_c_objects = sorted(c_objects.items(), key=lambda item: int(item[1]["object_index"]))
    for ordinal, (uid, obj) in enumerate(ordered_c_objects, 1):
        obj_idx = int(obj["object_index"])
        files = {f["relative_path"]: f["sha256"] for f in obj["files"]}
        for condition, run_dir in (("native_gfl", c_primary), ("layer_llh", c_addendum)):
            metric_row = c_metrics[(uid, condition)]
            input_row = c_input_rows[(uid, condition)]
            pred_path = run_dir / "predictions" / condition / f"{uid}.png"
            append_cohort_row("FreshC", uid, obj_idx, Path(obj["render_dir"]), condition,
                              pred_path, metric_row, input_row,
                              c_prediction_hashes[(condition, uid)], files)
        if ordinal % 25 == 0:
            write_csv(partial_metrics, output_rows)
            write_csv(partial_audit, audit_rows)
            print(f"Fresh C paired objects verified and scored: {ordinal}/{len(ordered_c_objects)}", flush=True)

    # Fresh B: frozen UID list and pre-unblind SHA manifest are authoritative.
    b_uid_path = args.freshb_validation_root / "fresh_confirm_b" / "fresh_confirm_B_150.txt"
    b_uids = [line.strip().split("/")[-1] for line in b_uid_path.read_text().splitlines() if line.strip()]
    for ordinal, uid in enumerate(b_uids, 1):
        obj = b_objects[uid]
        metric_idx = int(b_input_rows[(uid, "native_gfl")]["object_idx"])
        for condition in ("native_gfl", "layer_llh"):
            metric_row = b_rows[(uid, condition)]
            input_row = b_input_rows[(uid, condition)]
            pred_path = b_run / "predictions" / condition / f"{uid}.png"
            rel = f"formal/campaign_FRESH_CONFIRM_B_20261005/predictions/{condition}/{uid}.png"
            append_cohort_row("FreshB", uid, metric_idx, Path(obj["render_root"]),
                              condition, pred_path, metric_row, input_row, None,
                              external_output_relpath=rel)
        if ordinal % 25 == 0:
            write_csv(partial_metrics, output_rows)
            write_csv(partial_audit, audit_rows)
            print(f"Fresh B paired objects verified and scored: {ordinal}/{len(b_uids)}", flush=True)

    # Diagnostic images are already frozen composites with exact reference/mask
    # PNGs. Recompute using the same Python 3.13 color/texture implementation.
    for item in diagnostic_rows:
        pred_path = Path(item["prediction_png"])
        ref_path = Path(item["reference_png"])
        mask_path = Path(item["mask_png"])
        pred_sha = sha256_file(pred_path)
        ref_sha = sha256_file(ref_path)
        mask_sha = sha256_file(mask_path)
        if pred_sha != item["prediction_sha256"] or ref_sha != item["reference_sha256"] or mask_sha != item["mask_sha256"]:
            raise ValueError(f"R1 diagnostic PNG SHA mismatch for {item['uid']}/{item['condition']}")
        pred = np.asarray(Image.open(pred_path).convert("RGB"), dtype=np.uint8)
        ref = np.asarray(Image.open(ref_path).convert("RGB"), dtype=np.uint8).astype(np.float32) / 255.0
        mask = np.asarray(Image.open(mask_path).convert("L"), dtype=np.uint8).astype(np.float32) / 255.0
        metrics = rgb_panel_to_metrics(pred_path, torch.from_numpy(ref).permute(2, 0, 1), torch.from_numpy(mask[None]))
        output_rows.append({
            "cohort": "diagnostic26",
            "uid": item["uid"],
            "object_idx": item["object_idx"],
            "object_seed": item["object_seed"],
            "condition": item["condition"],
            "target_view_ids": item["target_view_ids"],
            "reverse_view_rotation": "from frozen reference panel",
            "checkpoint_sha256": item["checkpoint_sha256"],
            "runner_sha256": item["runner_sha256"],
            "prediction_png": str(pred_path),
            "prediction_sha256": pred_sha,
            "reference_png": str(ref_path),
            "reference_sha256": ref_sha,
            "mask_png": str(mask_path),
            "mask_sha256": mask_sha,
            "source": item["source"],
            "fg_psnr_recorded": item["fg_psnr"],
            "fg_lpips_recorded": item["fg_lpips"],
            "fg_ssim_recorded": "",
            "edge_ssim_recorded": item["edge_ssim"],
            "gt_fg_lap_var": item["texture_gt_fg_lap_var"],
            "gt_fg_hf_energy": item["texture_gt_fg_hf_energy"],
            "gt_fg_grad_mag": item["texture_gt_fg_grad_mag"],
            "gt_fg_rgb_std": item["texture_gt_fg_rgb_std"],
            **metrics,
        })
        audit_rows.append({
            "cohort": "diagnostic26",
            "uid": item["uid"],
            "condition": item["condition"],
            "prediction_png": str(pred_path),
            "prediction_sha256_actual": pred_sha,
            "prediction_sha256_manifest": item["prediction_sha256"],
            "reference_sha256_actual": ref_sha,
            "mask_sha256_actual": mask_sha,
            "output_sha_pass": True,
            "gt_selected_source_files_digest_sha256": "",
            "gt_files_verified_against_cohort_manifest": False,
            "logged_target_tensor_sha256": "",
            "target_views": item["target_view_ids"],
            "reverse_view_rotation": "frozen reference panel",
        })

    write_csv(args.output_dir / "RGB_RECOMPUTED_CONDITION_METRICS.csv", output_rows)
    write_csv(args.output_dir / "RGB_HASH_AND_INPUT_AUDIT.csv", audit_rows)
    partial_metrics.unlink(missing_ok=True)
    partial_audit.unlink(missing_ok=True)
    print(json.dumps({
        "python": __import__("sys").version,
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "numpy": np.__version__,
        "freshc_objects": len(c_objects),
        "freshb_objects": len(b_uids),
        "diagnostic26_objects": len(diagnostic_uids),
        "condition_metric_rows": len(output_rows),
        "hash_audit_rows": len(audit_rows),
        "output_metrics": str(args.output_dir / "RGB_RECOMPUTED_CONDITION_METRICS.csv"),
        "output_audit": str(args.output_dir / "RGB_HASH_AND_INPUT_AUDIT.csv"),
    }, indent=2))


if __name__ == "__main__":
    main()
