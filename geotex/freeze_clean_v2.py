"""Write the immutable clean-v2 provenance and protocol audit bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import uuid
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/main_adapter_clean_v2"
DATA = ROOT / "data/train_data/rendered_full"
LIST = ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
MAP = ROOT / "final/round2/clean_dataset_v2/old_to_new_uid_mapping.csv"
TRAIN = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt"
POOL = DATA / "train_objects_1200.txt"
EVAL = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
CKPT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
CONFIG = Path("/tmp/mv_main_rerun/MVPainter/configs/mvpainter-geotex-full-train.yaml")
SMITH = Path("/home/ubuntu/.objaverse/smithsonian/smithsonian.parquet")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_hashes(path: Path) -> dict[str, str]:
    h1 = hashlib.sha256(path.read_bytes()).hexdigest()
    h2 = hashlib.md5(path.read_bytes()).hexdigest()
    return {"sha256": h1, "md5": h2}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(MAP.open()))
    uid_lines = [x.strip() for x in LIST.read_text().splitlines() if x.strip()]
    train_uids = {x.strip() for x in TRAIN.read_text().splitlines() if x.strip()}
    pool_uids = {x.strip() for x in POOL.read_text().splitlines() if x.strip()}

    smith = {}
    if SMITH.exists():
        table = pd.read_parquet(SMITH, columns=["fileIdentifier", "metadata", "sha256"])
        for file_identifier, metadata, source_sha256 in zip(table.fileIdentifier, table.metadata, table.sha256):
            try:
                md = json.loads(metadata) if isinstance(metadata, str) else {}
            except Exception:
                md = {}
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(file_identifier)))
            smith[uid] = {
                "file_identifier": str(file_identifier),
                "title": md.get("title") or md.get("name"),
                "source_sha256": str(source_sha256) if source_sha256 else "",
                "uuid5_rule": "uuid.uuid5(uuid.NAMESPACE_DNS, fileIdentifier)",
            }

    exact_dir = OUT / "exact_glbs"
    exact_hashes = {}
    for glb in sorted(exact_dir.glob("*.glb")):
        exact_hashes[glb.stem] = {"path": str(glb), **file_hashes(glb)}

    by_uid = {row["new_uid"]: row for row in rows}
    provenance = []
    for idx, uid in enumerate(uid_lines):
        old = by_uid.get(uid, {}).get("old_uid", "")
        reason = by_uid.get(uid, {}).get("reason", "")
        source = smith.get(uid, {})
        local = exact_hashes.get(uid, {})
        if source:
            source_type = "Smithsonian_ObjaverseXL_metadata_uuid5"
            source_status = "metadata_recoverable; exact_GLΒ_local" if local else "metadata_recoverable; source_GLΒ_not_local"
        else:
            source_type = "rendered_full_local_only"
            source_status = "local_render_verified"
        provenance.append({
            "object": f"obj_{idx:04d}",
            "uid": uid,
            "retained_or_replaced": "replaced" if reason == "historical_train_uid_replaced" else "retained",
            "old_uid": old,
            "replacement_reason": reason,
            "source_type": source_type,
            "source_title": source.get("title", ""),
            "source_file_identifier": source.get("file_identifier", ""),
            "source_asset_sha256": source.get("source_sha256", ""),
            "source_uuid5_rule": source.get("uuid5_rule", ""),
            "local_exact_glb": local.get("path", ""),
            "local_exact_glb_sha256": local.get("sha256", ""),
            "local_exact_glb_md5": local.get("md5", ""),
            "source_status": source_status,
        })
    with (OUT / "clean_v2_provenance_300.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(provenance[0]))
        writer.writeheader()
        writer.writerows(provenance)

    eval_manifest = EVAL / "evaluation_manifest.json"
    config_copy = OUT / "mvpainter-geotex-full-train.clean_v2_snapshot.yaml"
    if CONFIG.exists():
        shutil.copy2(CONFIG, config_copy)
    freeze = {
        "protocol": "clean-v2-frozen-main-adapter-audit-v1",
        "status": "frozen; no dataset or checkpoint changes permitted",
        "object_count": len(uid_lines),
        "retained_count": sum(x["retained_or_replaced"] == "retained" for x in provenance),
        "replaced_count": sum(x["retained_or_replaced"] == "replaced" for x in provenance),
        "objects": "clean_v2_provenance_300.csv",
        "train_eval_overlap": {
            "historical_1118_count": len(train_uids),
            "clean_v2_intersection_count": len(set(uid_lines) & train_uids),
            "candidate_pool_1200_count": len(pool_uids),
            "clean_v2_intersection_with_candidate_pool": len(set(uid_lines) & pool_uids),
            "replacement_uids_in_historical_train": len({x["uid"] for x in provenance if x["retained_or_replaced"] == "replaced"} & train_uids),
        },
        "split": {
            "probe": {"count": 24, "list": str(ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"), "sha256": sha256(ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt")},
            "strict_holdout": {"count": 276, "list": str(ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"), "sha256": sha256(ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt")},
            "rule": "obj_0000--obj_0023 probe; obj_0024--obj_0299 strict holdout",
        },
        "dataset_hashes": {
            "eval_list_sha256": sha256(LIST),
            "historical_train_1118_sha256": sha256(TRAIN),
            "train_objects_1200_sha256": sha256(POOL),
            "evaluation_manifest_sha256": sha256(eval_manifest),
        },
        "checkpoint": {"path": str(CKPT), "step": 2000, **file_hashes(CKPT), "source_commit": "f2f0019a008277213af0127fa7cb628cb5fa1eef", "label": "controlled retraining checkpoint; not recovered original"},
        "training_protocol": {"config": str(config_copy), "historical_train_list": str(TRAIN), "max_steps": 2000, "candidate_pool_note": "train_objects_1200 is the expanded local candidate pool used during dataset construction; it is not the historical 1,118-object list and was not used to select this checkpoint"},
        "evaluation_manifest": str(eval_manifest),
        "evaluation_config": json.loads(eval_manifest.read_text()),
        "views": {"mode": "unique6", "target_views": [0, 15, 12, 16, 13, 14], "resolution": "256x256 per view; 512x768 saved panel", "conditions": ["no_adapter", "fixed_low_s1.25", "fixed_high_s2.50", "c3_1.25_2.50_1.25"]},
        "exact_glb_local_count": len(exact_hashes),
    }
    (OUT / "clean_v2_freeze_manifest.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({k: freeze[k] for k in ["object_count", "retained_count", "replaced_count", "train_eval_overlap", "exact_glb_local_count"]}, indent=2))


if __name__ == "__main__":
    main()
