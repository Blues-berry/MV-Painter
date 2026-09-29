"""Small, dependency-light metrics for baked-texture evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def stratified_object_ids(delta_by_object: dict[str, float], per_quartile: int = 3) -> list[str]:
    """Select deterministic IDs across four performance-difference quartiles."""
    if per_quartile <= 0 or len(delta_by_object) < 4 * per_quartile:
        raise ValueError("not enough objects for the requested quartile sample")
    ordered = sorted(delta_by_object.items(), key=lambda item: (float(item[1]), item[0]))
    bins = np.array_split(ordered, 4)
    selected = []
    for bucket in bins:
        positions = np.linspace(0, len(bucket) - 1, per_quartile, dtype=int)
        selected.extend(bucket[pos][0] for pos in positions)
    return selected


def uv_seam_color_difference(texture: np.ndarray, seam_pairs: np.ndarray) -> float:
    """Mean RGB Euclidean difference across paired texels on a UV seam."""
    texture = np.asarray(texture, dtype=np.float64)
    pairs = np.asarray(seam_pairs, dtype=np.int64)
    if texture.ndim != 2 or texture.shape[1] != 3 or pairs.ndim != 2 or pairs.shape[1] != 2:
        raise ValueError("texture must be Nx3 and seam_pairs must be Mx2")
    if len(pairs) == 0:
        return float("nan")
    if np.any(pairs < 0) or np.any(pairs >= len(texture)):
        raise IndexError("seam pair index outside texture")
    return float(np.linalg.norm(texture[pairs[:, 0]] - texture[pairs[:, 1]], axis=1).mean())


def cross_view_texel_variance(colors: np.ndarray, valid: np.ndarray | None = None) -> float:
    """Mean per-channel variance after multiple source views hit one texel."""
    colors = np.asarray(colors, dtype=np.float64)
    if colors.ndim != 3 or colors.shape[-1] != 3:
        raise ValueError("colors must have shape views x texels x 3")
    if valid is not None:
        valid = np.asarray(valid, dtype=bool)
        if valid.shape != colors.shape[:2]:
            raise ValueError("valid mask shape does not match colors")
        groups = [colors[valid[:, tex], tex] for tex in range(colors.shape[1]) if valid[:, tex].sum() > 1]
    else:
        groups = [colors[:, tex] for tex in range(colors.shape[1]) if colors.shape[0] > 1]
    if not groups:
        return float("nan")
    return float(np.mean([group.var(axis=0).mean() for group in groups]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta-json", type=Path, help="JSON object mapping object ID to paired delta")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.delta_json and args.output:
        values = json.loads(args.delta_json.read_text())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"selected_objects": stratified_object_ids(values)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
