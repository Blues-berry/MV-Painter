#!/usr/bin/env python3
"""Merge the frozen G ledgers with the 17 technically runnable completions.

The original ledgers and completion shards remain immutable. Duplicate source
rows are accepted only when source UID and every metric (excluding runtime)
match exactly. The one remaining technical exclusion is recorded with the
frozen input and loader evidence; no substitute object is introduced.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import trimesh

V3 = Path(__file__).resolve().parent.parent
BASE = V3 / "g_formal"
COMPLETION = V3 / "g_completion18"
OUT = V3 / "g_formal_complete"
LAYERS = ("deep", "middle", "shallow")
CONDITIONS = ["g_baseline"] + [f"g_{layer}_W{w}" for layer in LAYERS for w in range(1, 6)]
METRICS = ("psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
           "gt_relative_texture_error")
ROW_FIELDS = ("object", "source_uid", "condition", "elapsed_seconds", *METRICS)
FAILED_OBJECT = "g_0098"


def read(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    unique: dict[tuple[str, str], dict] = {}
    source_row_count = 0
    duplicate_count = 0
    for path in (BASE / "rows_shard0.json", BASE / "rows_shard1.json"):
        for row in read(path):
            source_row_count += 1
            key = (row["object"], row["condition"])
            if key in unique:
                old = unique[key]
                assert old["source_uid"] == row["source_uid"], f"source UID mismatch: {key}"
                assert all(old[m] == row[m] for m in METRICS), f"metric mismatch: {key}"
                duplicate_count += 1
                continue
            unique[key] = row

    original_pairs = set(unique)
    completion_rows = []
    for path in (COMPLETION / "shard0/rows_shard0.json",
                 COMPLETION / "shard1/rows_shard0.json"):
        completion_rows.extend(read(path))
    completion_objects = {r["object"] for r in completion_rows}
    expected_completion = {
        line.strip() for line in (COMPLETION / "missing18_objects.txt").read_text().splitlines()
        if line.strip()
    } - {FAILED_OBJECT}
    assert completion_objects == expected_completion, (completion_objects, expected_completion)
    assert len(completion_rows) == len(expected_completion) * 16
    for row in completion_rows:
        key = (row["object"], row["condition"])
        assert key not in unique, f"completion overlaps original cohort: {key}"
        assert row["condition"] in CONDITIONS
        unique[key] = row

    objects = sorted({obj for obj, _ in unique}, key=lambda x: int(x[-4:]))
    assert len(objects) == 98, f"expected 98 analyzable objects, got {len(objects)}"
    for obj in objects:
        got = {condition for o, condition in unique if o == obj}
        assert got == set(CONDITIONS), f"incomplete condition set for {obj}: {got}"
    assert not any(obj == FAILED_OBJECT for obj, _ in unique)
    assert len(unique) == len(objects) * len(CONDITIONS)

    ordered = [unique[(obj, condition)] for obj in objects for condition in CONDITIONS]
    (OUT / "rows_shard0.json").write_text(json.dumps(ordered, indent=2) + "\n")
    with (OUT / "per_object_metrics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows({k: row[k] for k in ROW_FIELDS} for row in ordered)

    locked = json.loads((COMPLETION / "G_COMPLETION_INPUT_HASHES.json").read_text())
    fail_input = locked["inputs"][FAILED_OBJECT]
    fail_shard = json.loads((COMPLETION / "missing18_runner_shard1.json").read_text())
    fail_spec = next(o for o in fail_shard["objects"] if o["object"] == FAILED_OBJECT)
    mesh_path = Path(fail_spec["mesh_path"])
    assert mesh_path.is_file()
    mesh_sha = sha256(mesh_path)
    expected_sha = next(f["sha256"] for f in fail_input["files"] if f["role"] == "mesh")
    assert mesh_sha == expected_sha
    loaded = trimesh.load(str(mesh_path), force="mesh", process=False)
    assert isinstance(loaded, trimesh.path.Path3D), type(loaded)
    assert not hasattr(loaded, "faces")
    exception_log = (COMPLETION / "shard1.log").read_text(errors="replace")
    assert "Unknown mesh type" in exception_log and str(mesh_path) in exception_log
    exclusion = {
        "object": FAILED_OBJECT,
        "source_uid": fail_input["source_uid"],
        "planned_original_cohort": True,
        "analysis_rows": 0,
        "reason": "frozen source GLB loads as line/path geometry (Path3D), with no triangle faces; the unchanged G renderer requires a surface mesh and raises Unknown mesh type",
        "mesh_path": str(mesh_path),
        "mesh_sha256": mesh_sha,
        "trimesh_type": type(loaded).__name__,
        "path_vertices": int(len(loaded.vertices)),
        "path_entities": int(len(loaded.entities)),
        "triangle_faces": 0,
        "gt_views_frozen_and_hashed": len(fail_input["files"]) - 1,
        "substitution_or_loader_change": False,
        "evidence": "g_completion18/shard1.log",
    }
    (OUT / "TECHNICAL_EXCLUSION_G_0098.json").write_text(json.dumps(exclusion, indent=2) + "\n")
    report = {
        "source_row_count": source_row_count,
        "identical_duplicate_rows_removed": duplicate_count,
        "original_unique_objects": len({o for o, _ in original_pairs}),
        "original_unique_object_condition_pairs": len(original_pairs),
        "completion_objects": len(completion_objects),
        "completion_rows": len(completion_rows),
        "merged_objects": len(objects),
        "merged_object_condition_pairs": len(unique),
        "conditions_per_object": len(CONDITIONS),
        "planned_cohort_after_registered_exclusion": 99,
        "additional_frozen_input_technical_exclusions": [exclusion],
        "merged_json_sha256": sha256(OUT / "rows_shard0.json"),
        "merged_csv_sha256": sha256(OUT / "per_object_metrics.csv"),
    }
    (OUT / "MERGE_AUDIT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
