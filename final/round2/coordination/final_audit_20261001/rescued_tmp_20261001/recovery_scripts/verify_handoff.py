"""Independent verification before handing off the temporary layer-LHL result."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path("/4T/CXY/MV-Painter")
TMP = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
EVAL_LIST = ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
HOLDOUT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
MERGED = TMP / "layer_official_v2_merged"
HEAD = TMP / "layer_official_v2_head/per_object_metrics.csv"
TAIL = TMP / "layer_official_v2_tail/per_object_metrics.csv"
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
STAGE = ROOT / "final/round2/stage_placement_276_20260929"

STANDARD = ["full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def check(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> None:
    checks: list[str] = []
    eval_uids = read_lines(EVAL_LIST)
    holdout_uids = read_lines(HOLDOUT_LIST)
    expected_objects = [f"obj_{i:04d}" for i in range(24, 300)]
    merged = rows(MERGED / "per_object_metrics.csv")
    head = rows(HEAD)
    tail = rows(TAIL)
    merged_by_object = {row["object"]: row for row in merged}

    check(len(eval_uids) == 300, "evaluation UID list has 300 entries", checks)
    check(holdout_uids == eval_uids[24:], "strict holdout equals positions 24..299 of the 300-object list", checks)
    check(len(holdout_uids) == 276 and len(set(holdout_uids)) == 276, "strict holdout has 276 unique UIDs", checks)
    check([row["object"] for row in merged] == expected_objects, "merged candidate CSV is ordered obj_0024..obj_0299", checks)
    check(len(merged) == 276 and len(merged_by_object) == 276, "merged candidate CSV has 276 unique rows", checks)
    check(len(head) == 138 and len(tail) == 138, "split candidate CSVs contain 138 rows each", checks)
    check(all(int(row["object_idx"]) < 138 for row in head), "head split contains only indices 0..137", checks)
    check(all(int(row["object_idx"]) >= 138 for row in tail), "tail split contains only indices 138..275", checks)

    for row in merged:
        check(row["schedule"] == "layer_LHL", f"candidate schedule is layer_LHL for {row['object']}", checks)
        check(int(row["object_idx"]) + 24 == int(row["object"].split("_")[1]), f"object index mapping is exact for {row['object']}", checks)
        for key, value in row.items():
            if key in {"object", "schedule"}:
                continue
            check(math.isfinite(float(value)), f"finite value {row['object']}/{key}", checks)

    for method in ("fixed_low", "c3", "fixed_high"):
        baseline = rows(BASE / f"per_object_{method}.csv")
        check([row["object"] for row in baseline if 24 <= int(row["object_idx"]) < 300] == expected_objects,
              f"main baseline {method} has exact 276-object slice", checks)
    for method in ("fixed_mean", "c3_lhl", "llh", "hll"):
        baseline = rows(STAGE / f"per_object_{method}.csv")
        check([row["object"] for row in baseline] == expected_objects,
              f"stage baseline {method} has exact 276-object keys", checks)

    reported = json.loads((MERGED / "official_comparisons.json").read_text())
    check(reported["row_counts"]["merged"] == 276, "comparison JSON records 276 merged rows", checks)
    for comparison in reported["comparisons"].values():
        check(comparison["n"] == 276, "every paired comparison has n=276", checks)
        for metric in STANDARD:
            left_mean = sum(float(row[metric]) for row in merged) / 276
            recorded = comparison["metrics"][metric]["left_mean"]
            check(abs(left_mean - recorded) < 1e-10, f"recomputed candidate mean matches JSON for {metric}", checks)

    head_pred = list((TMP / "layer_official_v2_head/predictions/layer_LHL").glob("*.png"))
    tail_pred = list((TMP / "layer_official_v2_tail/predictions/layer_LHL").glob("*.png"))
    check(len(head_pred) == 138 and len(tail_pred) == 138, "prediction PNG count is 138 per split", checks)
    check(md5(TMP / "layer_official_v2_head/predictions/layer_LHL/obj_0024.png") == md5(TMP / "determinism_a/predictions/layer_LHL/obj_0024.png"), "cross-GPU obj_0024 PNG matches deterministic check", checks)
    check(md5(TMP / "determinism_a/predictions/layer_LHL/obj_0024.png") == md5(TMP / "determinism_b/predictions/layer_LHL/obj_0024.png"), "same-GPU deterministic PNG check passes", checks)
    check(md5(TMP / "determinism_a/predictions/ground_truth/obj_0024.png") == md5(STAGE / "predictions/ground_truth/obj_0024.png"), "candidate GT matches formal stage GT for obj_0024", checks)

    manifest = json.loads((BASE / "evaluation_manifest.json").read_text())
    check(manifest["checkpoint_sha256"] == sha256(CHECKPOINT), "checkpoint hash matches evaluation manifest", checks)
    check(manifest["target_view_mode"] == "unique6" and manifest["target_views"] == [0, 15, 12, 16, 13, 14], "baseline manifest has the expected unique6 cameras", checks)

    result = {
        "status": "PASS",
        "checks": checks,
        "counts": {"head": len(head), "tail": len(tail), "merged": len(merged), "head_png": len(head_pred), "tail_png": len(tail_pred)},
        "checkpoint_sha256": sha256(CHECKPOINT),
        "object_list_sha256": sha256(HOLDOUT_LIST),
        "source_sha256": {
            "geotex_explore_contradiction": sha256(ROOT / "geotex/explore_contradiction.py"),
            "geotex_eval_exploration": sha256(ROOT / "geotex/eval_exploration.py"),
            "model_unet_geotex": sha256(ROOT / "MVPainter/mvpainter/model_unet_geotex.py"),
        },
        "layer_schedule": {
            "deep": [1.25, 2.5, 1.25],
            "middle": [1.25, 2.5, 1.25],
            "shallow": [0.5, 0.75, 0.5],
        },
    }
    (MERGED / "handoff_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "check_count": len(checks), "counts": result["counts"]}, indent=2))


if __name__ == "__main__":
    main()
