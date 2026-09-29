"""Build a UID-audited replacement for the contaminated Round-2 eval split.

The historical controlled checkpoint was trained on 1,118 UIDs.  This tool
keeps the old 300-object list untouched, preserves every non-overlapping
position, and replaces only positions whose UID occurs in the historical
training list.  The replacement pool is taken from already rendered,
complete objects that are not in that historical list.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


REQUIRED = {
    "image": "png",
    "normal": "png",
    "depth_png": "png",
    "camera": "npy",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_list(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def complete_protocol_views(root: Path, uid: str) -> tuple[bool, list[str]]:
    missing = []
    for folder, extension in REQUIRED.items():
        for view in range(17):
            path = root / uid / folder / f"{view:03d}.{extension}"
            if not path.is_file():
                missing.append(str(path))
    return not missing, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--historical-train", type=Path, required=True)
    parser.add_argument("--old-eval", type=Path, required=True)
    parser.add_argument("--candidate-pool", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replace-count", type=int, default=None)
    args = parser.parse_args()

    historical = read_list(args.historical_train)
    old_eval = read_list(args.old_eval)
    candidate_source = read_list(args.candidate_pool)
    historical_set = set(historical)
    old_set = set(old_eval)

    if len(old_eval) != 300 or len(old_set) != 300:
        raise ValueError(f"old evaluation list must contain 300 unique UIDs, got {len(old_eval)}")
    if len(historical_set) != len(historical):
        raise ValueError("historical training list contains duplicate UIDs")
    if len(set(candidate_source)) != len(candidate_source):
        raise ValueError("candidate pool contains duplicate UIDs")

    overlap_positions = [i for i, uid in enumerate(old_eval) if uid in historical_set]
    replace_count = len(overlap_positions) if args.replace_count is None else args.replace_count
    if replace_count != len(overlap_positions):
        raise ValueError(
            f"replace-count must equal the audited overlap count {len(overlap_positions)}; "
            f"received {replace_count}"
        )

    candidates = [
        uid for uid in candidate_source
        if uid not in historical_set and uid not in old_set
    ]
    valid_candidates = []
    invalid_candidates = {}
    for uid in candidates:
        complete, missing = complete_protocol_views(args.data_root, uid)
        if complete:
            valid_candidates.append(uid)
        else:
            invalid_candidates[uid] = missing
    if len(valid_candidates) < replace_count:
        raise ValueError(
            f"only {len(valid_candidates)} complete candidates are available; "
            f"need {replace_count}"
        )

    replacements = valid_candidates[:replace_count]
    replacement_iter = iter(replacements)
    new_eval = []
    mapping = []
    for index, old_uid in enumerate(old_eval):
        if old_uid in historical_set:
            new_uid = next(replacement_iter)
            reason = "historical_train_uid_replaced"
        else:
            new_uid = old_uid
            reason = "retained_disjoint_uid"
        new_eval.append(new_uid)
        mapping.append({
            "position": index,
            "object_id": f"obj_{index:04d}",
            "old_uid": old_uid,
            "new_uid": new_uid,
            "reason": reason,
        })

    if len(set(new_eval)) != 300:
        raise ValueError("new evaluation list is not unique")
    intersection = set(new_eval) & historical_set
    if intersection:
        raise ValueError(f"new evaluation list still overlaps training: {sorted(intersection)[:3]}")
    if any(not complete_protocol_views(args.data_root, uid)[0] for uid in new_eval):
        raise ValueError("new evaluation list contains incomplete rendered objects")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    list_paths = {
        "eval_objects_300_clean_v2.txt": new_eval,
        "probe_objects_24_clean_v2.txt": new_eval[:24],
        "strict_holdout_objects_276_clean_v2.txt": new_eval[24:],
        "replacement_candidate_pool_189.txt": valid_candidates,
    }
    for name, values in list_paths.items():
        (args.output_dir / name).write_text("\n".join(values) + "\n")

    with (args.output_dir / "old_to_new_uid_mapping.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(mapping[0]))
        writer.writeheader()
        writer.writerows(mapping)

    manifest = {
        "protocol": "round2-clean-eval-v2",
        "status": "ready_for_new_inference",
        "data_root": str(args.data_root.resolve()),
        "historical_train_list": str(args.historical_train.resolve()),
        "historical_train_count": len(historical),
        "historical_train_sha256": sha256(args.historical_train),
        "old_eval_list": str(args.old_eval.resolve()),
        "old_eval_count": len(old_eval),
        "old_eval_sha256": sha256(args.old_eval),
        "candidate_pool_source": str(args.candidate_pool.resolve()),
        "candidate_pool_source_sha256": sha256(args.candidate_pool),
        "candidate_pool_complete_count": len(valid_candidates),
        "replacement_count": len(replacements),
        "new_eval_count": len(new_eval),
        "new_eval_train_uid_intersection_count": len(intersection),
        "new_eval_sha256": sha256(args.output_dir / "eval_objects_300_clean_v2.txt"),
        "probe_count": 24,
        "probe_sha256": sha256(args.output_dir / "probe_objects_24_clean_v2.txt"),
        "strict_holdout_count": 276,
        "strict_holdout_sha256": sha256(args.output_dir / "strict_holdout_objects_276_clean_v2.txt"),
        "replacement_rule": "preserve old order and replace only UID-level historical-training overlaps",
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "required_views_per_object": 17,
        "invalid_candidate_count": len(invalid_candidates),
        "invalid_candidate_examples": {k: v[:4] for k, v in list(invalid_candidates.items())[:3]},
        "files": {name: str(args.output_dir / name) for name in list_paths},
    }
    (args.output_dir / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
