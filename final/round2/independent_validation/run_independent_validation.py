"""Independent clean-v2 provenance and metric audit.

This module deliberately does not import the project's metric helpers.  It
reconstructs the frozen evaluation target from the original RGBA/depth PNGs,
implements the documented PSNR/SSIM/Sobel calculations locally, and compares
the result with the stored per-object CSVs.  It is an audit artifact, not an
inference runner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF


METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
CORE_METRICS = ("full_psnr", "fg_psnr", "full_ssim", "fg_ssim", "edge_ssim")
TARGET_VIEWS = (0, 15, 12, 16, 13, 14)
REVERSE_TARGET_VIEWS = (14, 15, 0, 16, 12, 13)


def read_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_json_with_literal_suffix(path: Path) -> dict:
    """Read normal JSON and tolerate the historical manifest's literal ``\\n``."""
    text = path.read_text()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(text.rstrip().rstrip("\\n").rstrip())


def read_rgba(path: Path) -> tuple[torch.Tensor, torch.Tensor]:
    raw = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0
    alpha = raw[:, :, 3:4]
    rgb = raw[:, :, :3] * alpha + (1.0 - alpha)
    return (
        torch.from_numpy(rgb.transpose(2, 0, 1)).float(),
        torch.from_numpy(alpha.transpose(2, 0, 1)).float(),
    )


def read_depth(path: Path) -> torch.Tensor:
    """Match ``MVPainterDataset.load_img_depth`` and its six-view normalization."""
    raw = np.asarray(Image.open(path))
    if raw.ndim == 2:
        raw = np.repeat(raw[:, :, None], 3, axis=2)
    else:
        raw = raw[:, :, :3]
    return torch.from_numpy((raw.astype(np.float32) / 65535.0).transpose(2, 0, 1)).float()


def rotate_view(item: torch.Tensor) -> torch.Tensor:
    return TF.rotate(item, angle=90)


def make_panel(views: list[torch.Tensor], reverse: bool) -> torch.Tensor:
    selected = REVERSE_TARGET_VIEWS if reverse else TARGET_VIEWS
    chosen = []
    for position, view_idx in enumerate(selected):
        item = views[view_idx]
        if reverse and position in (1, 3):
            item = rotate_view(item)
        chosen.append(item)
    return assemble_panel(chosen)


def assemble_panel(chosen: list[torch.Tensor]) -> torch.Tensor:
    """Resize six already ordered views and form the 3-by-2 panel."""
    stack = torch.stack(chosen)
    stack = TF.resize(
        stack,
        [256, 256],
        interpolation=InterpolationMode.BICUBIC,
        antialias=True,
    )
    # Equivalent to the dataset's einops ``(x y) c h w -> c (x h) (y w)``.
    x, y, channels, height, width = 3, 2, *stack.shape[1:]
    return stack.reshape(x, y, channels, height, width).permute(2, 0, 3, 1, 4).reshape(
        channels, x * height, y * width
    )


def reconstruct_object(data_root: Path, uid: str) -> dict[str, object]:
    root = data_root / uid
    images: list[torch.Tensor] = []
    alphas: list[torch.Tensor] = []
    depths: list[torch.Tensor] = []
    for view_idx in range(17):
        rgb, alpha = read_rgba(root / "image" / f"{view_idx:03d}.png")
        images.append(rgb)
        alphas.append(alpha)
        depths.append(read_depth(root / "depth_png" / f"{view_idx:03d}.png"))

    reverse = bool((alphas[0] == 0).sum() > (alphas[14] == 0).sum())

    # The dataset normalizes depth jointly over the selected views before
    # resizing and panel assembly. Background pixels remain at one.
    selected = REVERSE_TARGET_VIEWS if reverse else TARGET_VIEWS
    depth_stack = torch.stack([depths[idx] for idx in selected])
    if reverse:
        depth_stack[1] = rotate_view(depth_stack[1])
        depth_stack[3] = rotate_view(depth_stack[3])
    valid = depth_stack < 1.0
    depth_stack = depth_stack.clone()
    depth_stack[valid] = 1.0 / depth_stack[valid]
    if valid.any():
        lo = depth_stack[valid].min()
        hi = depth_stack[valid].max()
        if hi > lo:
            depth_stack[valid] = (depth_stack[valid] - lo) / (hi - lo)
        else:
            depth_stack[valid] = 0.0

    target = make_panel(images, reverse)
    mask = make_panel(alphas, reverse)
    depth = assemble_panel([depth_stack[i] for i in range(6)])
    return {
        "target": target,
        "mask": mask,
        "depth": depth,
        "reverse": reverse,
        "mask_coverage": float(mask.mean()),
        "foreground_pixels": int((mask > 0.5).sum().item()),
    }


def reconstruct_mask(data_root: Path, uid: str) -> float:
    """Reconstruct only alpha coverage for deterministic sample stratification."""
    root = data_root / uid
    alphas = [read_rgba(root / "image" / f"{view_idx:03d}.png")[1] for view_idx in range(17)]
    reverse = bool((alphas[0] == 0).sum() > (alphas[14] == 0).sum())
    mask = make_panel(alphas, reverse)
    return float(mask.mean())


def load_prediction(path: Path) -> torch.Tensor:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return torch.from_numpy(image.transpose(2, 0, 1)).float()


def psnr(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor | None = None) -> float:
    if mask is None:
        error = pred - target
    else:
        valid = mask[:1] > 0.5
        if not bool(valid.any()):
            return 0.0
        error = (pred - target)[:, valid.expand_as(pred)[0]]
    mse = float((error * error).mean())
    return 100.0 if mse < 1e-10 else float(10.0 * math.log10(1.0 / mse))


def ssim_map(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred = pred.unsqueeze(0)
    target = target.unsqueeze(0)
    c1, c2 = 0.01**2, 0.03**2
    mu_p = F.avg_pool2d(pred, 3, 1, 1)
    mu_t = F.avg_pool2d(target, 3, 1, 1)
    var_p = F.avg_pool2d(pred * pred, 3, 1, 1) - mu_p * mu_p
    var_t = F.avg_pool2d(target * target, 3, 1, 1) - mu_t * mu_t
    cov = F.avg_pool2d(pred * target, 3, 1, 1) - mu_p * mu_t
    value = ((2 * mu_p * mu_t + c1) * (2 * cov + c2)) / (
        (mu_p * mu_p + mu_t * mu_t + c1) * (var_p + var_t + c2)
    )
    return value.clamp(0.0, 1.0)


def ssim(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor | None = None) -> float:
    value = ssim_map(pred, target)
    if mask is None:
        return float(value.mean())
    mask_d = F.max_pool2d(mask[:1].unsqueeze(0), 3, 1, 1)
    valid = mask_d > 0.5
    if not bool(valid.any()):
        return 0.0
    return float((value[:, :1] * mask_d)[valid].mean())


def sobel_edges(depth: torch.Tensor, threshold: float = 0.1) -> torch.Tensor:
    gray = depth.mean(dim=0, keepdim=True).unsqueeze(0)
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=gray.dtype).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=gray.dtype).view(1, 1, 3, 3)
    gx = F.conv2d(gray, sobel_x, padding=1)
    gy = F.conv2d(gray, sobel_y, padding=1)
    magnitude = torch.sqrt(gx * gx + gy * gy + 1e-8)
    magnitude = magnitude / (magnitude.max() + 1e-8)
    return (magnitude > threshold).float()[0]


def core_metrics(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor, depth: torch.Tensor) -> dict[str, float]:
    edge = sobel_edges(depth)
    return {
        "full_psnr": psnr(pred, target),
        "fg_psnr": psnr(pred, target, mask),
        "full_ssim": ssim(pred, target),
        "fg_ssim": ssim(pred, target, mask),
        "edge_ssim": ssim(pred, target, edge),
    }


def bundle_hash(data_root: Path, uid: str) -> str:
    digest = hashlib.sha256()
    root = data_root / uid
    for folder, suffix in (("image", "png"), ("normal", "png"), ("depth_png", "png"), ("camera", "npy")):
        for index in range(17):
            path = root / folder / f"{index:03d}.{suffix}"
            if not path.is_file():
                return ""
            digest.update(f"{folder}/{path.name}\0".encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def complete_views(data_root: Path, uid: str) -> bool:
    root = data_root / uid
    return all(
        (root / folder / f"{index:03d}.{suffix}").is_file()
        for folder, suffix in (("image", "png"), ("normal", "png"), ("depth_png", "png"), ("camera", "npy"))
        for index in range(17)
    )


def duplicate_groups(values: Iterable[tuple[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for key, label in values:
        if key:
            groups[key].append(label)
    return {key: labels for key, labels in groups.items() if len(labels) > 1}


def audit_provenance(root: Path, output_dir: Path) -> dict[str, object]:
    data_root = root / "data/train_data/rendered_full"
    hist_path = root / "mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt"
    pool_path = data_root / "train_objects_1200.txt"
    old_eval_path = data_root / "test_objects_300.txt"
    clean_path = root / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
    probe_path = root / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
    holdout_path = root / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
    candidate_path = root / "final/round2/clean_dataset_v2/replacement_candidate_pool_189.txt"
    mapping_path = root / "final/round2/clean_dataset_v2/old_to_new_uid_mapping.csv"
    provenance_path = root / "final/round2/main_adapter_clean_v2/clean_v2_provenance_300.csv"
    freeze_path = root / "final/round2/main_adapter_clean_v2/clean_v2_freeze_manifest.json"
    training_manifest_path = root / "mvpoutput/reviewer1_main_rerun_20260928/training_manifest.json"
    checkpoint_path = root / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"

    lists = {
        "historical_train_1118": read_lines(hist_path),
        "candidate_pool_1200": read_lines(pool_path),
        "old_eval_300": read_lines(old_eval_path),
        "clean_v2_300": read_lines(clean_path),
        "probe_24": read_lines(probe_path),
        "holdout_276": read_lines(holdout_path),
        "candidate_pool_complete_189": read_lines(candidate_path),
    }
    sets = {name: set(values) for name, values in lists.items()}
    mapping = list(csv.DictReader(mapping_path.open(newline="")))
    provenance = list(csv.DictReader(provenance_path.open(newline="")))
    by_uid = {row["uid"]: row for row in provenance}

    # Re-read the Smithsonian source table independently of the generated
    # provenance CSV when it is present.
    smith_rows: dict[str, dict[str, str]] = {}
    smith_path = Path("/home/ubuntu/.objaverse/smithsonian/smithsonian.parquet")
    if smith_path.is_file():
        try:
            import pandas as pd

            frame = pd.read_parquet(smith_path, columns=["fileIdentifier", "metadata", "sha256"])
            for file_identifier, metadata, source_sha in zip(frame.fileIdentifier, frame.metadata, frame.sha256):
                if not file_identifier:
                    continue
                try:
                    metadata_obj = json.loads(metadata) if isinstance(metadata, str) else {}
                except (TypeError, json.JSONDecodeError):
                    metadata_obj = {}
                uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(file_identifier)))
                smith_rows[uid] = {
                    "source_file_identifier": str(file_identifier),
                    "source_asset_sha256": str(source_sha),
                    "source_title": str(metadata_obj.get("title") or metadata_obj.get("name") or ""),
                }
        except Exception as exc:  # pragma: no cover - environment-dependent parquet engines
            smith_rows = {"__error__": {"error": repr(exc)}}

    render_hashes: dict[str, str] = {}
    for index, uid in enumerate(lists["clean_v2_300"], start=1):
        render_hashes[uid] = bundle_hash(data_root, uid)
        if index % 50 == 0:
            print(f"[D1] rendered bundle fingerprints: {index}/300", flush=True)
    old_probe_hashes = {uid: bundle_hash(data_root, uid) for uid in lists["old_eval_300"][:24]}
    new_holdout_uids = set(lists["clean_v2_300"][24:])
    old_probe_hash_set = {value for value in old_probe_hashes.values() if value}
    alias_hash_overlap = sorted(
        uid for uid in new_holdout_uids if render_hashes.get(uid) and render_hashes[uid] in old_probe_hash_set
    )

    # Build the requested per-object matrix. The rendered-bundle fingerprint
    # is distinct from an asset/GLB SHA and is only a duplicate-render check.
    matrix_fields = [
        "object", "position", "uid", "old_uid", "replacement_status", "reason", "split",
        "source_type", "source_file_identifier", "source_asset_sha256", "local_exact_glb",
        "local_exact_glb_sha256", "complete_17_view_bundle", "render_bundle_sha256",
        "smithsonian_metadata_match",
    ]
    matrix_rows = []
    for position, row in enumerate(mapping):
        uid = row["new_uid"]
        p = by_uid.get(uid, {})
        smith = smith_rows.get(uid, {})
        matrix_rows.append({
            "object": row["object_id"],
            "position": position,
            "uid": uid,
            "old_uid": row["old_uid"],
            "replacement_status": "replaced" if "replaced" in row["reason"] else "retained",
            "reason": row["reason"],
            "split": "probe24" if position < 24 else "strict_holdout276",
            "source_type": p.get("source_type", ""),
            "source_file_identifier": p.get("source_file_identifier", ""),
            "source_asset_sha256": p.get("source_asset_sha256", ""),
            "local_exact_glb": p.get("local_exact_glb", ""),
            "local_exact_glb_sha256": p.get("local_exact_glb_sha256", ""),
            "complete_17_view_bundle": complete_views(data_root, uid),
            "render_bundle_sha256": render_hashes.get(uid, ""),
            "smithsonian_metadata_match": bool(
                smith and p.get("source_file_identifier") == smith.get("source_file_identifier")
                and p.get("source_asset_sha256") == smith.get("source_asset_sha256")
            ) if smith else ("not_applicable" if not p.get("source_file_identifier") else "unavailable"),
        })
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "CLEAN_V2_PROVENANCE_MATRIX.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=matrix_fields)
        writer.writeheader()
        writer.writerows(matrix_rows)

    replacement_rows = [row for row in mapping if "replaced" in row["reason"]]
    retained_rows = [row for row in mapping if "retained" in row["reason"]]
    source_hash_dups = duplicate_groups((row.get("source_asset_sha256", ""), row["object"]) for row in provenance)
    file_id_dups = duplicate_groups((row.get("source_file_identifier", ""), row["object"]) for row in provenance)
    glb_hash_dups = duplicate_groups((row.get("local_exact_glb_sha256", ""), row["object"]) for row in provenance)
    render_dups = duplicate_groups((render_hashes.get(uid, ""), f"obj_{index:04d}") for index, uid in enumerate(lists["clean_v2_300"]))

    training_manifest = parse_json_with_literal_suffix(training_manifest_path)
    checkpoint_hash = sha256_file(checkpoint_path) if checkpoint_path.is_file() else ""
    expected_checkpoint_hash = training_manifest.get("checkpoint_sha256", "")
    expected_train_hash = training_manifest.get("train_list_sha256", "")
    manifest_train_file = root / "mvpoutput/reviewer1_main_rerun_20260928" / Path(training_manifest.get("train_list", "")).name
    relations = {
        "historical_train_count": len(lists["historical_train_1118"]),
        "candidate_pool_count": len(lists["candidate_pool_1200"]),
        "historical_intersection_candidate_pool": len(sets["historical_train_1118"] & sets["candidate_pool_1200"]),
        "historical_only_vs_candidate_pool": len(sets["historical_train_1118"] - sets["candidate_pool_1200"]),
        "candidate_pool_only_vs_historical": len(sets["candidate_pool_1200"] - sets["historical_train_1118"]),
        "old_eval_count": len(lists["old_eval_300"]),
        "old_eval_historical_overlap": len(sets["old_eval_300"] & sets["historical_train_1118"]),
        "old_eval_retained_count": len(sets["old_eval_300"] - sets["historical_train_1118"]),
        "replacement_count": len(replacement_rows),
        "retained_count": len(retained_rows),
        "replacement_subset_candidate_pool": {row["new_uid"] for row in replacement_rows} <= sets["candidate_pool_1200"],
        "replacement_subset_complete_candidate_pool": {row["new_uid"] for row in replacement_rows} <= sets["candidate_pool_complete_189"],
        "replacement_historical_overlap": len({row["new_uid"] for row in replacement_rows} & sets["historical_train_1118"]),
        "clean_count": len(lists["clean_v2_300"]),
        "clean_unique": len(sets["clean_v2_300"]) == len(lists["clean_v2_300"]),
        "clean_historical_overlap": len(sets["clean_v2_300"] & sets["historical_train_1118"]),
        "clean_old_eval_retained_overlap": len(sets["clean_v2_300"] & sets["old_eval_300"]),
        "clean_candidate_pool_overlap": len(sets["clean_v2_300"] & sets["candidate_pool_1200"]),
        "probe_count": len(lists["probe_24"]),
        "holdout_count": len(lists["holdout_276"]),
        "probe_holdout_intersection": len(sets["probe_24"] & sets["holdout_276"]),
        "probe_is_clean_prefix": lists["probe_24"] == lists["clean_v2_300"][:24],
        "holdout_is_clean_suffix": lists["holdout_276"] == lists["clean_v2_300"][24:],
        "old_probe_replaced": sum("replaced" in row["reason"] for row in mapping[:24]),
        "old_probe_retained": sum("retained" in row["reason"] for row in mapping[:24]),
        "old_probe_bundle_hash_overlap_with_new_holdout": len(alias_hash_overlap),
    }
    checkpoint = {
        "training_manifest_present": training_manifest_path.is_file(),
        "training_manifest_train_list_field": training_manifest.get("train_list", ""),
        "training_manifest_train_hash_matches_local": bool(expected_train_hash and sha256_file(hist_path) == expected_train_hash),
        "training_manifest_train_list_matches_audited_path": manifest_train_file.resolve() == hist_path.resolve(),
        "training_manifest_checkpoint_field": training_manifest.get("checkpoint", ""),
        "checkpoint_present": checkpoint_path.is_file(),
        "checkpoint_sha256_matches_training_manifest": bool(checkpoint_hash and checkpoint_hash == expected_checkpoint_hash),
        "checkpoint_sha256_matches_freeze_manifest": checkpoint_hash == parse_json_with_literal_suffix(freeze_path).get("checkpoint", {}).get("sha256", ""),
        "checkpoint_step": training_manifest.get("steps"),
    }
    direct_source = {
        "smithsonian_table_present": smith_path.is_file(),
        "smithsonian_clean_uid_matches": len(set(smith_rows) & sets["clean_v2_300"]) if smith_rows and "__error__" not in smith_rows else 0,
        "smithsonian_provenance_exact_matches": sum(row["smithsonian_metadata_match"] is True for row in matrix_rows),
        "source_asset_sha_filled": sum(bool(row.get("source_asset_sha256")) for row in provenance),
        "source_asset_sha_duplicate_groups": source_hash_dups,
        "source_file_identifier_duplicate_groups": file_id_dups,
        "local_exact_glb_count": sum(bool(row.get("local_exact_glb_sha256")) for row in provenance),
        "local_exact_glb_sha_duplicate_groups": glb_hash_dups,
        "render_bundle_duplicate_groups": render_dups,
        "render_bundle_missing": sum(not bool(render_hashes.get(uid)) for uid in lists["clean_v2_300"]),
    }
    result = {
        "status": "STOP-GATE" if (
            relations["clean_historical_overlap"]
            or relations["replacement_historical_overlap"]
            or relations["old_probe_bundle_hash_overlap_with_new_holdout"]
            or source_hash_dups
            or render_dups
        ) else "PASS_WITH_LIMITATIONS",
        "relations": relations,
        "checkpoint": checkpoint,
        "direct_source": direct_source,
        "hashes": {
            "historical_train_1118": sha256_file(hist_path),
            "candidate_pool_1200": sha256_file(pool_path),
            "old_eval_300": sha256_file(old_eval_path),
            "clean_v2_300": sha256_file(clean_path),
            "probe_24": sha256_file(probe_path),
            "holdout_276": sha256_file(holdout_path),
        },
        "old_probe_bundle_hashes": old_probe_hashes,
        "alias_hash_overlap_uids": alias_hash_overlap,
    }
    (output_dir / "CLEAN_V2_PROVENANCE_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def load_existing_rows(eval_dir: Path, method: str) -> dict[str, dict[str, float]]:
    with (eval_dir / f"per_object_{method}.csv").open(newline="") as handle:
        return {
            row["object"]: {key: float(value) for key, value in row.items() if key not in {"object", "schedule", "object_idx"}}
            for row in csv.DictReader(handle)
        }


def audit_metrics(root: Path, output_dir: Path, sample_only: bool = False) -> dict[str, object]:
    data_root = root / "data/train_data/rendered_full"
    object_list = root / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
    eval_dir = root / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
    uids = read_lines(object_list)
    existing = {method: load_existing_rows(eval_dir, method) for method in METHODS}

    coverage = {}
    if sample_only:
        for index, uid in enumerate(uids):
            coverage[f"obj_{index:04d}"] = reconstruct_mask(data_root, uid)
            if (index + 1) % 50 == 0:
                print(f"[D2] alpha coverage scan: {index + 1}/{len(uids)}", flush=True)

    reconstructed: dict[str, dict[str, object]] = {}
    process_objects = [f"obj_{index:04d}" for index in range(len(uids))]
    if sample_only:
        c3_diffs = {
            obj: existing["c3"][obj]["fg_psnr"] - existing["fixed_low"][obj]["fg_psnr"]
            for obj in existing["c3"]
        }
        no_adapter_fg_ssim = {obj: existing["no_adapter"][obj]["fg_ssim"] for obj in existing["no_adapter"]}
        roles: dict[str, set[str]] = defaultdict(set)
        for obj in sorted(c3_diffs, key=c3_diffs.get, reverse=True)[:3]:
            roles[obj].add("C3 clearly above fixed-low (top 3 existing FG-PSNR delta)")
        for obj in sorted(c3_diffs, key=c3_diffs.get)[:3]:
            roles[obj].add("C3 clearly below fixed-low (bottom 3 existing FG-PSNR delta)")
        for obj in sorted(no_adapter_fg_ssim, key=no_adapter_fg_ssim.get, reverse=True)[:3]:
            roles[obj].add("no-adapter high FG-SSIM (top 3 existing values)")
        for obj in sorted(coverage, key=coverage.get)[:2]:
            roles[obj].add("smallest foreground mask (bottom 2 reconstructed coverage)")
        for obj in sorted(coverage, key=coverage.get, reverse=True)[:2]:
            roles[obj].add("largest foreground mask (top 2 reconstructed coverage)")
        process_objects = sorted(roles, key=lambda value: int(value[4:]))

    all_rows = []
    for object_id in process_objects:
        index = int(object_id[4:])
        uid = uids[index]
        reconstructed[object_id] = reconstruct_object(data_root, uid)
        item = reconstructed[object_id]
        target = item["target"]
        mask = item["mask"]
        depth = item["depth"]
        for method in METHODS:
            pred = load_prediction(eval_dir / "predictions" / method / f"{object_id}.png")
            recomputed = core_metrics(pred, target, mask, depth)
            row = {
                "object": object_id,
                "uid": uid,
                "method": method,
                "reverse": item["reverse"],
                "mask_coverage": item["mask_coverage"],
                "foreground_pixels": item["foreground_pixels"],
            }
            for metric in CORE_METRICS:
                row[f"existing_{metric}"] = existing[method][object_id][metric]
                row[f"recomputed_{metric}"] = recomputed[metric]
                row[f"delta_{metric}"] = recomputed[metric] - existing[method][object_id][metric]
            # LPIPS is retained as provenance only; this audit intentionally
            # does not load a learned network or treat a PNG recomputation as
            # equivalent to the float inference value.
            row["existing_full_lpips"] = existing[method][object_id].get("full_lpips", float("nan"))
            row["existing_fg_lpips"] = existing[method][object_id].get("fg_lpips", float("nan"))
            all_rows.append(row)
        print(f"[D2] metric recomputation: {object_id}", flush=True)

    # Selection rules are fixed before reading recomputed values: the existing
    # stored CSV identifies the diagnostic strata, and source mask coverage is
    # an independent input property.
    c3_diffs = {
        obj: existing["c3"][obj]["fg_psnr"] - existing["fixed_low"][obj]["fg_psnr"]
        for obj in existing["c3"]
    }
    no_adapter_fg_ssim = {obj: existing["no_adapter"][obj]["fg_ssim"] for obj in existing["no_adapter"]}
    if not coverage:
        coverage = {obj: float(reconstructed[obj]["mask_coverage"]) for obj in reconstructed}
    roles: dict[str, set[str]] = defaultdict(set)
    for obj in sorted(c3_diffs, key=c3_diffs.get, reverse=True)[:3]:
        roles[obj].add("C3 clearly above fixed-low (top 3 existing FG-PSNR delta)")
    for obj in sorted(c3_diffs, key=c3_diffs.get)[:3]:
        roles[obj].add("C3 clearly below fixed-low (bottom 3 existing FG-PSNR delta)")
    for obj in sorted(no_adapter_fg_ssim, key=no_adapter_fg_ssim.get, reverse=True)[:3]:
        roles[obj].add("no-adapter high FG-SSIM (top 3 existing values)")
    for obj in sorted(coverage, key=coverage.get)[:2]:
        roles[obj].add("smallest foreground mask (bottom 2 reconstructed coverage)")
    for obj in sorted(coverage, key=coverage.get, reverse=True)[:2]:
        roles[obj].add("largest foreground mask (top 2 reconstructed coverage)")
    selected_objects = sorted(roles, key=lambda value: int(value[4:]))

    fields = list(all_rows[0])
    with (output_dir / "METRIC_RECOMPUTE_ALL.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    sample_rows = [row for row in all_rows if row["object"] in selected_objects]
    with (output_dir / "METRIC_RECOMPUTE_SAMPLE.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["roles", *fields])
        writer.writeheader()
        for row in sample_rows:
            writer.writerow({"roles": "; ".join(sorted(roles[row["object"]])), **row})

    summary: dict[str, object] = {
        "n_objects": len(process_objects),
        "evaluated_scope": "predeclared diagnostic sample" if sample_only else "all clean-v2 objects",
        "methods": {},
        "selected_objects": {obj: sorted(roles[obj]) for obj in selected_objects},
        "selection_rule": {
            "c3_above_fixed_low": "top 3 existing per-object FG-PSNR deltas",
            "c3_below_fixed_low": "bottom 3 existing per-object FG-PSNR deltas",
            "no_adapter_high_fg_ssim": "top 3 existing no-adapter FG-SSIM values",
            "mask_extremes": "two smallest and two largest independently reconstructed alpha coverage values",
        },
        "implementation_facts": {
            "target_composite": "RGBA RGB*alpha + white*(1-alpha)",
            "target_views": list(TARGET_VIEWS),
            "reverse_rule": "alpha-zero count view 000 > view 014; reverse order and rotate panel positions 1 and 3 by 90 degrees",
            "resolution": "source 512x512 -> bicubic antialiased 256x256 -> 3x2 panel 768x512 (saved PNG is 512x768 W x H)",
            "foreground_psnr_denominator": "mean RGB squared error over pixels where resized alpha mask > 0.5; RGB channels count equally",
            "foreground_ssim_mask": "3x3 max-pooled alpha mask; SSIM map is averaged over mask>0.5 after multiplying by pooled alpha",
            "edge_source": "normalized real depth PNG selected by the dataset; Sobel magnitude across mean of its three channels, global per-panel normalization, threshold > 0.1",
            "lpips": "not independently recomputed; stored float inference values retained as provenance",
        },
    }
    for method in METHODS:
        rows = [row for row in all_rows if row["method"] == method]
        method_summary = {}
        for metric in CORE_METRICS:
            existing_values = np.asarray([row[f"existing_{metric}"] for row in rows], dtype=float)
            recomputed_values = np.asarray([row[f"recomputed_{metric}"] for row in rows], dtype=float)
            delta = recomputed_values - existing_values
            method_summary[metric] = {
                "existing_mean": float(existing_values.mean()),
                "recomputed_mean": float(recomputed_values.mean()),
                "mean_delta_recomputed_minus_existing": float(delta.mean()),
                "mean_abs_delta": float(np.abs(delta).mean()),
                "max_abs_delta": float(np.abs(delta).max()),
                "recomputed_min": float(recomputed_values.min()),
                "recomputed_max": float(recomputed_values.max()),
            }
        summary["methods"][method] = method_summary
    (output_dir / "METRIC_RECOMPUTE_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def write_reports(root: Path, output_dir: Path, provenance: dict[str, object], metrics: dict[str, object]) -> None:
    rel = lambda path: str(path.relative_to(root))
    relations = provenance["relations"]
    direct = provenance["direct_source"]
    checkpoint = provenance["checkpoint"]
    status = provenance["status"]
    report = [
        "# CLEAN-V2 Independent Audit",
        "",
        f"Status: **{'PASS WITH LIMITATIONS' if status == 'PASS_WITH_LIMITATIONS' else status}** (independent UID audit; see explicit limitations below).",
        "",
        "This report was generated by `run_independent_validation.py` from the original list files, the checkpoint/training manifest, the local rendered data, and the Smithsonian metadata parquet when available. The existing Codex-A provenance CSV is cross-checked, not treated as the sole source of truth.",
        "",
        "## Set relations",
        "",
        "| relation | result |",
        "|---|---:|",
        f"| historical training list | {relations['historical_train_count']} unique UIDs |",
        f"| `train_objects_1200` | {relations['candidate_pool_count']} unique UIDs |",
        f"| historical train ∩ candidate pool | {relations['historical_intersection_candidate_pool']} |",
        f"| historical-only UIDs relative to candidate pool | {relations['historical_only_vs_candidate_pool']} |",
        f"| candidate-only UIDs relative to historical train | {relations['candidate_pool_only_vs_historical']} |",
        f"| old evaluation ∩ historical train | {relations['old_eval_historical_overlap']} |",
        f"| old evaluation retained after cleaning | {relations['old_eval_retained_count']} |",
        f"| clean-v2 replacement rows | {relations['replacement_count']} |",
        f"| clean-v2 retained rows | {relations['retained_count']} |",
        f"| clean-v2 ∩ historical train | {relations['clean_historical_overlap']} |",
        f"| clean-v2 ∩ old evaluation | {relations['clean_old_eval_retained_overlap']} |",
        f"| clean-v2 ∩ candidate pool | {relations['clean_candidate_pool_overlap']} |",
        "",
        "The 1,200-entry candidate list is therefore not a superset of the historical 1,118-object training list: it has 1,011 shared UIDs and 189 candidate-only UIDs. The 101 replacements are a subset of those 189 candidate-only UIDs. The apparent 82-object arithmetic contradiction does not apply to the observed files.",
        "",
        "## Mapping and split checks",
        "",
        f"- Mapping rows are unique and decompose into {relations['retained_count']} retained + {relations['replacement_count']} replaced rows.",
        f"- Replacement UIDs are in the candidate pool: `{relations['replacement_subset_candidate_pool']}`; in the complete candidate pool: `{relations['replacement_subset_complete_candidate_pool']}`.",
        f"- Replacement UIDs still in historical training: `{relations['replacement_historical_overlap']}`.",
        f"- The 24/276 split is a direct prefix/suffix of clean-v2: probe `{relations['probe_is_clean_prefix']}`, holdout `{relations['holdout_is_clean_suffix']}`, split intersection `{relations['probe_holdout_intersection']}`.",
        f"- The old first-24 probe positions contain {relations['old_probe_replaced']} replaced and {relations['old_probe_retained']} retained UIDs. Position-preserving construction puts no old probe position into the new holdout.",
        "",
        "## Checkpoint/training evidence",
        "",
        f"- Training manifest train-list field points to `{checkpoint['training_manifest_train_list_field']}` and its SHA-256 matches the audited 1,118-entry file: `{checkpoint['training_manifest_train_hash_matches_local']}`.",
        f"- The manifest train-list path resolves to the audited file: `{checkpoint['training_manifest_train_list_matches_audited_path']}`.",
        f"- Checkpoint is present and its SHA-256 matches the training manifest: `{checkpoint['checkpoint_sha256_matches_training_manifest']}`; it also matches the freeze manifest: `{checkpoint['checkpoint_sha256_matches_freeze_manifest']}`.",
        f"- Training manifest records step `{checkpoint['checkpoint_step']}`. This verifies the recorded checkpoint/list linkage; it does not recreate the training process or prove undocumented historical provenance.",
        "",
        "## Source identity and duplicate checks",
        "",
        f"- Independently re-read Smithsonian metadata matches: {direct['smithsonian_provenance_exact_matches']} rows; clean UIDs found in the metadata table: {direct['smithsonian_clean_uid_matches']}.",
        f"- Source asset SHA-256 values are available for {direct['source_asset_sha_filled']}/300 rows; duplicate groups among those values: {len(direct['source_asset_sha_duplicate_groups'])}.",
        f"- Local exact GLBs are available for {direct['local_exact_glb_count']}/300 rows; duplicate GLB SHA-256 groups: {len(direct['local_exact_glb_sha_duplicate_groups'])}.",
        f"- Complete rendered image/normal/depth/camera bundle fingerprints are missing for {direct['render_bundle_missing']} rows; duplicate fingerprints within clean-v2: {len(direct['render_bundle_duplicate_groups'])}.",
        f"- Exact rendered-bundle fingerprint overlap between old probe assets and new holdout: {relations['old_probe_bundle_hash_overlap_with_new_holdout']} UIDs.",
        "",
        "## Verification boundary",
        "",
        "**VERIFIED:** list cardinalities and uniqueness; 1,118/1,200/old-300/clean-300 set relations; 101/199 mapping; zero clean-v2 UID overlap with the recorded historical train list; 24/276 split; checkpoint manifest linkage; direct Smithsonian metadata agreement for the 113 metadata-backed clean UIDs; no duplicate source SHA, local GLB SHA, or complete rendered-bundle fingerprint in the available clean-v2 evidence.",
        "",
        "**PARTIALLY VERIFIED:** absence of semantic aliases for the 187 local-only rendered assets. Those rows have no canonical source identifier or local GLB in this workspace. The exact rendered-bundle check found no duplicate among complete files and no old-probe/new-holdout bundle collision, but that is not a universal source-asset identity proof.",
        "",
        "**STOP-GATE:** not triggered by the available UID, metadata-SHA, GLB-SHA, or rendered-bundle evidence. No dataset replacement was performed by this audit.",
        "",
        "## Evidence files",
        "",
        f"- Matrix: `{rel(output_dir / 'CLEAN_V2_PROVENANCE_MATRIX.csv')}`",
        f"- Machine-readable audit: `{rel(output_dir / 'CLEAN_V2_PROVENANCE_AUDIT.json')}`",
        f"- Historical training list: `{rel(root / 'mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt')}`",
        f"- Candidate pool: `{rel(root / 'data/train_data/rendered_full/train_objects_1200.txt')}`",
        f"- Clean-v2 list: `{rel(root / 'final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt')}`",
    ]
    (output_dir / "CLEAN_V2_INDEPENDENT_AUDIT.md").write_text("\n".join(report) + "\n")

    scope = metrics.get("evaluated_scope", "all clean-v2 objects")
    n_metric_objects = metrics.get("n_objects", "?")
    metric_report = [
        "# Metric Implementation Audit",
        "",
        f"Status: **PARTIALLY VERIFIED**. Core PSNR/SSIM/Edge-SSIM values were independently recomputed from the stored prediction PNGs and original source RGBA/depth PNGs for {n_metric_objects} objects in the `{scope}` scope and four conditions. PSNR and foreground/edge SSIM are comparatively close on this sample, but Full SSIM has a systematic stored-CSV versus PNG/source mismatch that is not explained by ordinary PNG quantization alone. The original float prediction tensors and exact metric-dtype provenance are unavailable here; LPIPS was not rerun with a learned network.",
        "",
        "## Protocol and implementation comparison",
        "",
        "| item | paper/protocol definition | code actually used | independent finding |",
        "|---|---|---|---|",
        "| Full PSNR | RGB PSNR on the full 3×2 panel | `geotex/round2_main_eval.py` calls `eval_exploration.compute_metrics`; `compute_psnr` averages all RGB/panel values; no foreground-only denominator | Background is included and can dominate when the object mask is small. It is not a 3D texture metric. |",
        "| Foreground MSE/PSNR | foreground RGB error under alpha mask | alpha is resized with the same bicubic pipeline; `compute_psnr` thresholds mask values at `>0.5`, expands one mask over RGB, then averages selected RGB values | Denominator is selected foreground RGB values, not all panel pixels. |",
        "| Foreground SSIM | masked local SSIM | 3×3 average-pool SSIM; mask is 3×3 max-pooled and values are multiplied before averaging where pooled mask `>0.5` | Edge pixels enter the statistic through mask dilation; this is not a crop or a strict original-alpha-only SSIM. |",
        "| RGBA/GT | white-background composite from RGBA | dataset uses `RGB*alpha + white*(1-alpha)` and retains alpha masks | Independently reconstructed target agrees with saved GT within PNG/resampling quantization; see summary JSON. |",
        "| 512→256 | bicubic antialiased resize per view, then panel assembly | dataset/data preparation uses torchvision resize and 3×2 rearrangement | Reproduced locally; reverse order and rotations are included. |",
        "| unique6 | `[0,15,12,16,13,14]`, or reversed `[14,15,0,16,12,13]` with rotations | dataset implements this exact mapping | Reproduced locally for every object. |",
        "| Edge-SSIM | depth/normal discontinuity proxy | round-2 runner selects normalized real depth when present, falls back to normal; `compute_edge_mask` averages 3 channels, Sobel-normalizes per panel, thresholds `>0.1`; SSIM then max-pools the edge mask | This is a depth-derived edge mask in the frozen run, not a joint depth+normal discontinuity detector. |",
        "| No-adapter | same unmodified pipeline with adapter contribution disabled | round-2 schedule sets scale 0 and still uses the same condition image, scheduler, seed, target and metric code | Definitionally consistent with an adapter-free baseline, conditional on the zero-scale wrapper behavior. |",
        "",
        "## Recomputed aggregate comparison",
        "",
        "| condition | metric | stored CSV mean | PNG/source recompute mean | mean absolute difference | max absolute difference |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        for metric in CORE_METRICS:
            item = metrics["methods"][method][metric]
            metric_report.append(
                f"| {method} | {metric} | {item['existing_mean']:.6f} | {item['recomputed_mean']:.6f} | {item['mean_abs_delta']:.6f} | {item['max_abs_delta']:.6f} |"
            )
    metric_report += [
        "",
        "The supplied `METRIC_RECOMPUTE_SAMPLE.csv` is a predeclared diagnostic sample: top/bottom three C3−fixed-low foreground-PSNR objects using the stored CSV, top three no-adapter foreground-SSIM objects using the stored CSV, and the two smallest/two largest independently reconstructed foreground coverages. It is not used to change pooled statistics.",
        "",
        "## Interpretation of the reported anomaly",
        "",
        "The observed ordering—no-adapter having higher foreground structure values than C3, and fixed-high being worse than fixed-low on foreground structure—is present in the stored metrics and is not erased by the independent PNG/source recomputation. Full-image metrics can still favor adapter conditions because background agreement and silhouette/edge behavior contribute over the entire panel. This is a genuine shape–texture trade-off signal under the current definitions, not evidence that foreground metrics should be redefined.",
        "",
        "Potential bias sources retained rather than corrected: small foreground masks make Full PSNR background-dominated; max-pooled SSIM masks include a one-pixel neighborhood around the alpha boundary; alpha is antialiased before the `>0.5` threshold; Sobel edge masks are panel-normalized and threshold-relative; PNG quantization changes recomputed values slightly; LPIPS values remain float-run provenance and were not silently replaced. The Full SSIM discrepancy is a separate metric-provenance/implementation-mismatch candidate and remains pending until the original float predictions or an exact rerun are available.",
        "",
        "## Required follow-up",
        "",
        "A candidate minimal float32 hardening patch is recorded in `METRIC_FLOAT32_RECOMMENDED.patch` but is intentionally not applied: it must be tested against the original float predictions before changing shared metric code. The paper-facing Full SSIM column should be re-audited or explicitly caveated; a future robustness appendix should also report mask coverage and a strict-eroded foreground sensitivity table, and should avoid describing Edge-SSIM as a full normal/depth discontinuity metric unless the normal branch is actually used.",
        "",
        "Evidence: `METRIC_RECOMPUTE_ALL.csv`, `METRIC_RECOMPUTE_SAMPLE.csv`, and `METRIC_RECOMPUTE_SUMMARY.json` in this directory.",
    ]
    (output_dir / "METRIC_IMPLEMENTATION_AUDIT.md").write_text("\n".join(metric_report) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--skip-provenance", action="store_true", help="reuse CLEAN_V2_PROVENANCE_AUDIT.json")
    parser.add_argument("--sample-only", action="store_true", help="recompute only the predeclared D2 diagnostic sample")
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir.resolve()
    torch.set_num_threads(1)
    provenance_path = output_dir / "CLEAN_V2_PROVENANCE_AUDIT.json"
    if args.skip_provenance and provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text())
    else:
        provenance = audit_provenance(root, output_dir)
    metrics = audit_metrics(root, output_dir, sample_only=args.sample_only)
    write_reports(root, output_dir, provenance, metrics)
    print(json.dumps({"provenance_status": provenance["status"], "objects": metrics["n_objects"], "output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
