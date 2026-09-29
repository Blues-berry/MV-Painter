#!/usr/bin/env python3
"""Export the frozen MVPainter renders to MVDiffusion's ScanNet layout.

MVDiffusion's official depth branch expects one scene directory containing
``color/*.jpg``, metric ``depth/*.png`` (millimetres), camera-to-world
``pose/*.txt``, one ``intrinsic/intrinsic_depth.txt``, and text prompts.  The
MVPainter records use 17 orthographic views, normalized 16-bit depth, and
world-to-camera matrices, so this exporter makes those conversions explicit
and records them in a manifest rather than mutating the source dataset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


DEFAULT_VIEW_IDS = (0, 1, 2, 4, 5, 7, 9, 12, 13, 14, 15, 16)
DEFAULT_TARGET_VIEW_IDS = (0, 12, 13, 14, 15, 16)


def parse_ids(value: str) -> tuple[int, ...]:
    ids = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not ids:
        raise ValueError("view list must contain at least one integer")
    if len(set(ids)) != len(ids):
        raise ValueError(f"view list contains duplicates: {ids}")
    return ids


def rgba_to_rgb(path: Path) -> Image.Image:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0
    rgb = rgba[..., :3] * rgba[..., 3:4] + (1.0 - rgba[..., 3:4])
    return Image.fromarray(np.rint(rgb * 255.0).astype(np.uint8), mode="RGB")


def normalized_depth_to_mm(path: Path, near: float, far: float) -> Image.Image:
    raw = np.asarray(Image.open(path))
    if raw.ndim != 2:
        raw = raw[..., 0]
    if raw.dtype != np.uint16:
        raise ValueError(f"expected uint16 normalized depth at {path}, got {raw.dtype}")
    valid = (raw > 0) & (raw < np.iinfo(np.uint16).max)
    normalized = raw.astype(np.float32) / float(np.iinfo(np.uint16).max)
    metric_mm = np.rint((near + (far - near) * normalized) * 1000.0)
    metric_mm = np.clip(metric_mm, 0, np.iinfo(np.uint16).max).astype(np.uint16)
    metric_mm[~valid] = 0
    return Image.fromarray(metric_mm, mode="I;16")


def camera_to_world(camera_path: Path) -> tuple[np.ndarray, dict]:
    record = np.load(camera_path, allow_pickle=True).item()
    extrinsic = np.asarray(record["extrinsic"], dtype=np.float32)
    if extrinsic.shape == (3, 4):
        extrinsic = np.vstack([extrinsic, np.array([[0, 0, 0, 1]], dtype=np.float32)])
    if extrinsic.shape != (4, 4):
        raise ValueError(f"unexpected extrinsic shape at {camera_path}: {extrinsic.shape}")
    pose = np.linalg.inv(extrinsic).astype(np.float32)
    if not np.isfinite(pose).all():
        raise ValueError(f"non-finite camera-to-world pose at {camera_path}")
    return pose, record


def build_intrinsic(
    camera: dict,
    width: int,
    height: int,
    focal_mode: str,
    ortho_width: float,
) -> np.ndarray:
    if focal_mode == "source_intrinsic":
        intrinsic = np.asarray(camera["intrinsic"], dtype=np.float32).copy()
        if intrinsic.shape != (3, 3):
            raise ValueError(f"unexpected intrinsic shape: {intrinsic.shape}")
        return intrinsic
    if focal_mode != "ortho_equivalent":
        raise ValueError(f"unsupported focal mode: {focal_mode}")
    distance = float(camera.get("distance", 3.0))
    focal = width * distance / ortho_width
    return np.array(
        [[focal, 0.0, (width - 1) / 2.0],
         [0.0, focal, (height - 1) / 2.0],
         [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )


def load_rows(
    manifest_path: Path,
    split: str,
    object_ids: list[str] | None,
    excluded_ids: list[str] | None,
) -> list[dict]:
    payload = json.loads(manifest_path.read_text())
    ids = payload["calibration_objects"] if split == "calibration" else payload["holdout_objects"]
    by_id = {row["object"]: row for row in payload["objects"]}
    excluded = set(excluded_ids or [])
    unknown_excluded = excluded - set(by_id)
    if unknown_excluded:
        raise ValueError(f"unknown excluded object IDs: {sorted(unknown_excluded)}")
    if object_ids is not None:
        requested = set(object_ids)
        unknown = requested - set(by_id)
        if unknown:
            raise ValueError(f"unknown object IDs: {sorted(unknown)}")
        ids = [item for item in ids if item in requested and item not in excluded]
    else:
        ids = [item for item in ids if item not in excluded]
    rows = [by_id[item] for item in ids]
    if not rows:
        raise ValueError(f"no objects selected for split={split}")
    return rows


def export_object(
    row: dict,
    output_root: Path,
    view_ids: tuple[int, ...],
    target_view_ids: tuple[int, ...],
    prompt: str,
    near: float,
    far: float,
    focal_mode: str,
    ortho_width: float,
) -> dict:
    source_root = Path(row["render_root"])
    scene_root = output_root / row["object"]
    for folder in ("color", "depth", "intrinsic", "pose", "prompt"):
        (scene_root / folder).mkdir(parents=True, exist_ok=True)

    source_first = source_root / "image" / f"{view_ids[0]:03d}.png"
    first_image = Image.open(source_first)
    width, height = first_image.size
    first_camera = np.load(
        source_root / "camera" / f"{view_ids[0]:03d}.npy", allow_pickle=True
    ).item()
    intrinsic = build_intrinsic(first_camera, width, height, focal_mode, ortho_width)
    np.savetxt(scene_root / "intrinsic" / "intrinsic_depth.txt", intrinsic, fmt="%.8f")

    local_by_source = {source_id: local_id for local_id, source_id in enumerate(view_ids)}
    missing_targets = [source_id for source_id in target_view_ids if source_id not in local_by_source]
    if missing_targets:
        raise ValueError(f"target views are absent from exported views: {missing_targets}")

    for local_id, source_id in enumerate(view_ids):
        source_rgb = source_root / "image" / f"{source_id:03d}.png"
        source_depth = source_root / "depth_png" / f"{source_id:03d}.png"
        source_camera = source_root / "camera" / f"{source_id:03d}.npy"
        for path in (source_rgb, source_depth, source_camera):
            if not path.is_file():
                raise FileNotFoundError(path)

        # The upstream Scannet loader formats frame paths as ``{}.jpg``
        # (without zero padding), so the exported filenames must follow that
        # convention even though the source MVPainter records are padded.
        name = str(local_id)
        rgba_to_rgb(source_rgb).save(scene_root / "color" / f"{name}.jpg", quality=95)
        normalized_depth_to_mm(source_depth, near, far).save(scene_root / "depth" / f"{name}.png")
        pose, _ = camera_to_world(source_camera)
        np.savetxt(scene_root / "pose" / f"{name}.txt", pose, fmt="%.8f")
        (scene_root / "prompt" / f"{name}.txt").write_text(prompt.strip() + "\n")

    valid_ids = np.arange(len(view_ids), dtype=np.int64)
    np.save(scene_root / "valid_frames.npy", valid_ids)
    (scene_root / "key_frame_0.6.txt").write_text(
        "".join(f"{index}\n" for index in valid_ids)
    )
    return {
        "object": row["object"],
        "source_uid": row.get("source_uid"),
        "scene_dir": str(scene_root.resolve()),
        "source_render_root": str(source_root.resolve()),
        "source_view_ids": list(view_ids),
        "target_view_ids": list(target_view_ids),
        "target_local_indices": [local_by_source[item] for item in target_view_ids],
        "resolution_source": [width, height],
        "prompt": prompt,
        "depth_encoding": {
            "source": "uint16 normalized [0,65535], 65535 invalid",
            "target": "uint16 millimetres, zero invalid",
            "near_m": near,
            "far_m": far,
        },
        "pose_encoding": "inverse of the stored world-to-camera extrinsic",
        "intrinsic_encoding": focal_mode,
        "intrinsic_source": intrinsic.tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split", choices=("calibration", "holdout"), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--object", dest="object_ids", action="append", default=None)
    parser.add_argument("--exclude-object", dest="excluded_ids", action="append", default=None)
    parser.add_argument("--view-ids", default=','.join(map(str, DEFAULT_VIEW_IDS)))
    parser.add_argument("--target-view-ids", default=','.join(map(str, DEFAULT_TARGET_VIEW_IDS)))
    parser.add_argument(
        "--prompt",
        default="A high quality studio product photograph of a 3D object on a plain background.",
    )
    parser.add_argument("--near-m", type=float, default=2.0)
    parser.add_argument("--far-m", type=float, default=4.0)
    parser.add_argument(
        "--focal-mode",
        choices=("ortho_equivalent", "source_intrinsic"),
        default="ortho_equivalent",
    )
    parser.add_argument("--ortho-width", type=float, default=1.1)
    args = parser.parse_args()

    if args.near_m <= 0 or args.far_m <= args.near_m:
        raise ValueError("expected 0 < near_m < far_m")
    view_ids = parse_ids(args.view_ids)
    target_view_ids = parse_ids(args.target_view_ids)
    rows = load_rows(args.manifest, args.split, args.object_ids, args.excluded_ids)
    args.output_root.mkdir(parents=True, exist_ok=True)
    exported = [
        export_object(
            row,
            args.output_root,
            view_ids,
            target_view_ids,
            args.prompt,
            args.near_m,
            args.far_m,
            args.focal_mode,
            args.ortho_width,
        )
        for row in rows
    ]
    payload = {
        "protocol": "mvdiffusion-depth-mvpainter-interop-v1",
        "source_manifest": str(args.manifest.resolve()),
        "split": args.split,
        "view_ids": list(view_ids),
        "target_view_ids": list(target_view_ids),
        "excluded_objects": args.excluded_ids or [],
        "objects": exported,
        "compatibility_note": (
            "MVDiffusion was trained for perspective ScanNet scenes; the frozen "
            "MVPainter renders are orthographic. The exported pinhole K is an "
            "orthographic-equivalent approximation and must not be pooled with "
            "the native MVPainter/MV-Adapter absolute-score table."
        ),
        "evaluation_note": (
            "The target RGB views are not passed to the generator, but their "
            "depth maps remain part of the 12-view condition. Therefore these "
            "interop targets are not geometry-held-out novel views."
        ),
        "target_depth_conditioned": True,
        "target_rgb_conditioned": False,
    }
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_manifest.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"split": args.split, "object_count": len(exported), "view_count": len(view_ids)}, indent=2))


if __name__ == "__main__":
    main()
