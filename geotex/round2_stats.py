"""Shared statistics for the second-round reviewer experiments.

The functions in this module deliberately operate on arrays or small CSV
tables rather than on model objects.  This keeps the statistical layer
reproducible when inference is rerun on another machine and prevents the
probe/holdout split from being inferred differently by each experiment.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np


PROBE_IDS = tuple(f"obj_{i:04d}" for i in range(24))
MAIN_HOLDOUT_IDS = tuple(f"obj_{i:04d}" for i in range(24, 300))
MAIN_POOLED_IDS = tuple(f"obj_{i:04d}" for i in range(300))
MV_ADAPTER_CALIBRATION_IDS = PROBE_IDS
MV_ADAPTER_HOLDOUT_IDS = tuple(f"obj_{i:04d}" for i in range(24, 100))
MV_ADAPTER_TOTAL_IDS = tuple(f"obj_{i:04d}" for i in range(100))
UNIQUE_TARGET_VIEWS = (0, 15, 12, 16, 13, 14)
LEGACY_TARGET_VIEWS = (0, 15, 12, 15, 13, 14)
BOOTSTRAP_SEED = 20260928


def validate_view_ids(view_ids: Sequence[int], *, expected_count: int = 6) -> tuple[int, ...]:
    """Return view IDs after rejecting duplicates or malformed protocols."""
    values = tuple(int(v) for v in view_ids)
    if len(values) != expected_count:
        raise ValueError(f"expected {expected_count} views, got {len(values)}")
    if len(set(values)) != len(values):
        raise ValueError(f"view IDs must be unique, got {values}")
    return values


def validate_split(ids: Iterable[str], *, split: str) -> tuple[str, ...]:
    """Validate a named split against its fixed object-ID rule."""
    values = tuple(ids)
    expected = {
        "probe": PROBE_IDS,
        "main_probe": PROBE_IDS,
        "main_holdout": MAIN_HOLDOUT_IDS,
        "main_pooled": MAIN_POOLED_IDS,
        "mv_adapter_calibration": MV_ADAPTER_CALIBRATION_IDS,
        "mv_adapter_holdout": MV_ADAPTER_HOLDOUT_IDS,
        "mv_adapter_total": MV_ADAPTER_TOTAL_IDS,
    }[split]
    if values != expected:
        raise ValueError(
            f"{split} must be the fixed ordered split; first/last received "
            f"{values[:2]} / {values[-2:] if values else values}, "
            f"expected {expected[:2]} / {expected[-2:]}"
        )
    return values


def validate_fixed_partitions() -> dict[str, tuple[str, ...]]:
    """Validate the complete, disjoint object partitions used in Round 2."""
    partitions = {
        "main_probe": validate_split(PROBE_IDS, split="main_probe"),
        "main_holdout": validate_split(MAIN_HOLDOUT_IDS, split="main_holdout"),
        "main_pooled": validate_split(MAIN_POOLED_IDS, split="main_pooled"),
        "mv_adapter_calibration": validate_split(
            MV_ADAPTER_CALIBRATION_IDS, split="mv_adapter_calibration"
        ),
        "mv_adapter_holdout": validate_split(MV_ADAPTER_HOLDOUT_IDS, split="mv_adapter_holdout"),
        "mv_adapter_total": validate_split(MV_ADAPTER_TOTAL_IDS, split="mv_adapter_total"),
    }
    if set(partitions["main_probe"]).intersection(partitions["main_holdout"]):
        raise ValueError("main probe and holdout overlap")
    if set(partitions["mv_adapter_calibration"]).intersection(partitions["mv_adapter_holdout"]):
        raise ValueError("MV-Adapter calibration and holdout overlap")
    if set(partitions["main_probe"]) | set(partitions["main_holdout"]) != set(partitions["main_pooled"]):
        raise ValueError("main probe and holdout do not form the 300-object pool")
    if set(partitions["mv_adapter_calibration"]) | set(partitions["mv_adapter_holdout"]) != set(
        partitions["mv_adapter_total"]
    ):
        raise ValueError("MV-Adapter calibration and holdout do not form the 100-object total")
    return partitions


def symmetric_log_error(pred: np.ndarray, gt: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """Compute the symmetric log-ratio error requested for texture statistics."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    pred = np.asarray(pred, dtype=np.float64)
    gt = np.asarray(gt, dtype=np.float64)
    if pred.shape != gt.shape:
        raise ValueError(f"pred and gt shapes differ: {pred.shape} vs {gt.shape}")
    if not np.all(np.isfinite(pred)) or not np.all(np.isfinite(gt)):
        raise ValueError("texture statistics must be finite")
    if np.any(pred < 0) or np.any(gt < 0):
        raise ValueError("texture statistics must be non-negative")
    return np.abs(np.log((pred + epsilon) / (gt + epsilon)))


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    n_resamples: int = 10_000,
    seed: int = BOOTSTRAP_SEED,
    confidence: float = 0.95,
) -> dict[str, float | int | list[float]]:
    """Percentile bootstrap CI for an object-level mean."""
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("bootstrap input must be a non-empty one-dimensional vector")
    if not np.all(np.isfinite(values)):
        raise ValueError("bootstrap input contains NaN or Inf")
    if n_resamples <= 0 or not 0 < confidence < 1:
        raise ValueError("invalid bootstrap parameters")
    rng = np.random.default_rng(seed)
    # Generate in one call for deterministic, compact, object-level resampling.
    sample_idx = rng.integers(0, values.size, size=(n_resamples, values.size))
    means = values[sample_idx].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    return {
        "n": int(values.size),
        "mean": float(values.mean()),
        "ci95": [float(np.quantile(means, alpha)), float(np.quantile(means, 1 - alpha))],
        "wins": int(np.sum(values > 0)),
        "ties": int(np.sum(values == 0)),
        "win_rate": float(np.mean(values > 0)),
        "seed": int(seed),
        "resamples": int(n_resamples),
    }


def paired_delta_summary(
    left: Sequence[float],
    right: Sequence[float],
    *,
    higher_is_better: bool = True,
    **bootstrap_kwargs,
) -> dict:
    """Summarize paired left-minus-right differences with direction-aware wins."""
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.shape != right.shape:
        raise ValueError(f"paired vectors differ: {left.shape} vs {right.shape}")
    delta = left - right if higher_is_better else right - left
    return bootstrap_mean_ci(delta, **bootstrap_kwargs)


def read_object_csv(path: str | Path, object_column: str = "object") -> dict[str, dict[str, str]]:
    """Read a per-object CSV while accepting the historical ``object_idx`` key."""
    path = Path(path)
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = {}
    for row in rows:
        key = row.get(object_column) or row.get("object_id")
        if key is None and row.get("object_idx") is not None:
            key = f"obj_{int(float(row['object_idx'])):04d}"
        if not key:
            raise ValueError(f"no object identifier in {path}")
        if key in out:
            raise ValueError(f"duplicate object identifier {key} in {path}")
        out[key] = row
    return out


def paired_csv_summary(
    left_rows: Mapping[str, Mapping[str, str]],
    right_rows: Mapping[str, Mapping[str, str]],
    *,
    metrics: Sequence[str],
    object_ids: Sequence[str],
    higher_is_better: Mapping[str, bool] | None = None,
    **bootstrap_kwargs,
) -> dict:
    """Compute all requested paired metrics on an explicitly supplied split."""
    higher_is_better = higher_is_better or {}
    missing = [o for o in object_ids if o not in left_rows or o not in right_rows]
    if missing:
        raise ValueError(f"missing {len(missing)} objects from paired CSVs; first={missing[:3]}")
    out = {}
    for metric in metrics:
        left = np.asarray([float(left_rows[o][metric]) for o in object_ids])
        right = np.asarray([float(right_rows[o][metric]) for o in object_ids])
        out[metric] = paired_delta_summary(
            left, right, higher_is_better=higher_is_better.get(metric, True), **bootstrap_kwargs
        )
    return out


def aggregate_view_rows(
    rows: Iterable[Mapping[str, str]],
    *,
    object_ids: Sequence[str],
    metrics: Sequence[str],
    view_ids: Sequence[int] = UNIQUE_TARGET_VIEWS,
) -> list[dict[str, str]]:
    """Aggregate raw per-view rows into one row per object.

    Every object must have exactly one row for each of the six expected camera
    IDs.  Metrics are averaged within object only after this validation, so a
    missing view or a duplicate view cannot silently change the object weight
    in the final statistics.
    """
    expected_objects = tuple(object_ids)
    expected_views = validate_view_ids(view_ids)
    metric_names = tuple(metrics)
    if not metric_names or len(set(metric_names)) != len(metric_names):
        raise ValueError("metrics must be a non-empty list of unique names")

    grouped: dict[str, dict[int, dict[str, str]]] = {obj: {} for obj in expected_objects}
    expected_set = set(expected_objects)
    for row in rows:
        object_id = row.get("object") or row.get("object_id")
        if object_id is None and row.get("object_idx") is not None:
            object_id = f"obj_{int(float(row['object_idx'])):04d}"
        view_value = row.get("view") or row.get("view_id") or row.get("camera_id")
        if not object_id or view_value is None:
            raise ValueError("each raw row needs an object and view identifier")
        if object_id not in expected_set:
            raise ValueError(f"unexpected object {object_id}")
        view_id = int(float(view_value))
        if view_id not in expected_views:
            raise ValueError(f"unexpected view {view_id} for {object_id}")
        if view_id in grouped[object_id]:
            raise ValueError(f"duplicate view {view_id} for {object_id}")
        for metric in metric_names:
            if metric not in row or row[metric] in (None, ""):
                raise ValueError(f"missing metric {metric} for {object_id}/{view_id}")
            value = float(row[metric])
            if not np.isfinite(value):
                raise ValueError(f"non-finite metric {metric} for {object_id}/{view_id}")
        grouped[object_id][view_id] = row

    output = []
    for object_id in expected_objects:
        received = tuple(sorted(grouped[object_id]))
        if received != tuple(sorted(expected_views)):
            raise ValueError(
                f"object {object_id} has views {received}; expected {tuple(sorted(expected_views))}"
            )
        result = {"object": object_id, "view_count": str(len(expected_views))}
        for metric in metric_names:
            result[metric] = str(
                float(np.mean([float(grouped[object_id][view][metric]) for view in expected_views]))
            )
        output.append(result)
    return output


def aggregate_view_csv(
    input_path: str | Path,
    output_path: str | Path,
    *,
    object_ids: Sequence[str],
    metrics: Sequence[str],
    view_ids: Sequence[int] = UNIQUE_TARGET_VIEWS,
) -> None:
    """Rebuild a per-object CSV from a raw per-view CSV."""
    with Path(input_path).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    aggregated = aggregate_view_rows(
        rows, object_ids=object_ids, metrics=metrics, view_ids=view_ids
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["object", "view_count", *metrics])
        writer.writeheader()
        writer.writerows(aggregated)


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: str | Path, payload: Mapping) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

