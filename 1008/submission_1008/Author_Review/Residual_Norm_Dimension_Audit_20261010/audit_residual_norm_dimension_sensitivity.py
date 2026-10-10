#!/usr/bin/env python3
"""Re-summarize frozen A3b traces without treating raw L2 as cross-layer dose."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

LAYERS = ("deep", "middle", "shallow")
WINDOWS = tuple(range(1, 6))
N_OBJECTS = 150


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def quantile(values: list[float], probability: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), probability))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True,
                        help="FRESH_CONFIRM_B_20261005 campaign directory")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    wrapper_shapes: dict[str, dict[str, set[tuple[int, int]]]] = {
        layer: defaultdict(set) for layer in LAYERS
    }
    wrapper_ids: dict[str, set[str]] = {layer: set() for layer in LAYERS}
    input_hashes: list[tuple[str, str]] = []

    for layer in LAYERS:
        for window in WINDOWS:
            condition = f"a3_{layer}_W{window}"
            paths = sorted((run_root / "residual_logs" / condition).glob("*.json"))
            if len(paths) != N_OBJECTS:
                raise ValueError(f"{condition}: expected {N_OBJECTS} traces, found {len(paths)}")
            first_step = (window - 1) * 10
            for path in paths:
                raw = path.read_bytes()
                input_hashes.append((str(path.relative_to(run_root)), sha256_bytes(raw)))
                trace = json.loads(raw)
                if set(trace) != {str(i) for i in range(50)}:
                    raise ValueError(f"{path}: expected exactly 50 steps")
                per_step_means = []
                for step in range(first_step, first_step + 10):
                    entries = trace[str(step)]
                    layer_entries = [(str(k), e) for k, e in entries.items()
                                     if e.get("depth") == layer]
                    if not layer_entries:
                        raise ValueError(f"{path}/{step}: no entries for {layer}")
                    values = []
                    for wrapper, entry in layer_entries:
                        value = float(entry["mean_abs"])
                        h, w = int(entry["h"]), int(entry["w"])
                        if not math.isfinite(value) or value < 0 or h <= 0 or w <= 0:
                            raise ValueError(f"{path}/{step}/{wrapper}: invalid summary")
                        values.append(value)
                        wrapper_ids[layer].add(wrapper)
                        wrapper_shapes[layer][wrapper].add((h, w))
                    per_step_means.append(float(np.mean(values)))
                rows.append({
                    "object_uid": path.stem,
                    "layer": layer,
                    "window": f"W{window}",
                    "active_steps": f"{first_step}-{first_step + 9}",
                    "wrappers_per_step": len(layer_entries),
                    "active_window_sum_of_equal_wrapper_mean_abs": sum(per_step_means),
                })

    for layer in LAYERS:
        if len(wrapper_ids[layer]) != 3:
            raise ValueError(f"{layer}: expected 3 wrapper IDs, found {sorted(wrapper_ids[layer])}")
        if any(len(shapes) != 1 for shapes in wrapper_shapes[layer].values()):
            raise ValueError(f"{layer}: wrapper spatial shape varies across traces")

    csv_path = out_dir / "A3B_PER_ENTRY_CORRECTION_SENSITIVITY.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    input_hashes.sort()
    manifest_text = "\n".join(f"{path}\t{digest}" for path, digest in input_hashes)
    summaries = {}
    for layer in LAYERS:
        values = [float(row["active_window_sum_of_equal_wrapper_mean_abs"])
                  for row in rows if row["layer"] == layer]
        summaries[layer] = {
            "n_cell_rows": len(values),
            "q05": quantile(values, 0.05),
            "median": quantile(values, 0.50),
            "q95": quantile(values, 0.95),
            "wrapper_ids": sorted(wrapper_ids[layer], key=int),
            "spatial_shapes_by_wrapper": {
                wrapper: [list(shape) for shape in sorted(shapes)]
                for wrapper, shapes in sorted(wrapper_shapes[layer].items(), key=lambda item: int(item[0]))
            },
        }
    lower = max(value["q05"] for value in summaries.values())
    upper = min(value["q95"] for value in summaries.values())
    output = {
        "status": "descriptive post-outcome sensitivity; not a validated dose or causal support test",
        "cohort": "FRESH_CONFIRM_B A3b",
        "n_objects": N_OBJECTS,
        "n_cell_rows": len(rows),
        "summary_definition": (
            "For each object/layer/window, at each of the 10 active steps take the equal-wrapper "
            "mean of the logged post-scale per-entry mean absolute correction, then sum those "
            "10 step summaries. This avoids multiplying by spatial element count but does not "
            "equalize feature semantics, hidden-state scale, or intervention dose."
        ),
        "layer_summaries": summaries,
        "central_90_intersection": [lower, upper] if lower < upper else None,
        "raw_log_channel_count_recorded": False,
        "source_trace_count": len(input_hashes),
        "source_trace_manifest_sha256": sha256_bytes(manifest_text.encode("utf-8")),
        "source_trace_manifest": [
            {"path": path, "sha256": digest} for path, digest in input_hashes
        ],
    }
    (out_dir / "A3B_PER_ENTRY_CORRECTION_SENSITIVITY.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "csv": str(csv_path),
        "n_cell_rows": len(rows),
        "layer_summaries": {
            layer: {key: summaries[layer][key] for key in ("n_cell_rows", "q05", "median", "q95")}
            for layer in LAYERS
        },
        "central_90_intersection": output["central_90_intersection"],
        "source_trace_count": len(input_hashes),
        "source_trace_manifest_sha256": output["source_trace_manifest_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
