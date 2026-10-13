#!/usr/bin/env python3
"""Build a six-object native-UV bake handoff from frozen counterfactual panels."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
GENERATION = ROOT / "generation"
BASE_HANDOFF = Path(
    "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/"
    "bake_matrix_v2/BAKE_INPUT_HANDOFF_V3.json"
)
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]
CONDITIONS = ("counterfactual_b0", "counterfactual_bplus", "counterfactual_bminus")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    source = json.loads(BASE_HANDOFF.read_text())
    freeze_path = Path(source["input_freeze_path"])
    if sha256(freeze_path) != source["input_freeze_sha256"]:
        raise RuntimeError("frozen bake input manifest hash changed")
    base_records = {row["object"]: row for row in source["objects"]}
    records = []
    for uid in UIDS:
        if uid not in base_records:
            raise KeyError(f"selected object is not in the frozen handoff: {uid}")
        record = dict(base_records[uid])
        record["generated_conditions"] = {}
        for condition in CONDITIONS:
            panel_path = GENERATION / "predictions" / condition / f"{uid}.png"
            if not panel_path.is_file():
                raise FileNotFoundError(panel_path)
            with Image.open(panel_path) as image:
                panel = image.convert("RGB")
                if panel.size != (512, 768):
                    raise RuntimeError(f"unexpected 3x2 panel size {panel.size}: {panel_path}")
                targets = []
                for mapping in record["target_view_mapping"]:
                    slot = int(mapping["slot"])
                    column, row = slot % 2, slot // 2
                    crop_path = ROOT / "bake" / "input_views" / uid / condition / f"slot_{slot}.png"
                    crop_path.parent.mkdir(parents=True, exist_ok=True)
                    panel.crop((column * 256, row * 256, (column + 1) * 256, (row + 1) * 256)).save(crop_path)
                    targets.append({
                        "slot": slot,
                        "raw_view_index": int(mapping["raw_view_index"]),
                        "path": str(crop_path),
                        "sha256": sha256(crop_path),
                    })
            record["generated_conditions"][condition] = {
                "panel_path": str(panel_path),
                "panel_sha256": sha256(panel_path),
                "target_views": targets,
            }
        records.append(record)

    output = {
        "status": "FROZEN_INPUTS_WITH_COUNTERFACTUAL_GENERATIONS",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": list(CONDITIONS),
        "objects": records,
        "input_freeze_path": str(freeze_path),
        "input_freeze_sha256": source["input_freeze_sha256"],
        "method_run_identity_path": str(GENERATION / "run_manifest_shard0.json"),
        "method_run_identity_sha256": sha256(GENERATION / "run_manifest_shard0.json"),
        "parent_handoff_path": str(BASE_HANDOFF),
        "parent_handoff_sha256": sha256(BASE_HANDOFF),
    }
    path = ROOT / "bake" / "BAKE_INPUT_HANDOFF.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"handoff": str(path), "objects": len(records), "conditions": list(CONDITIONS)}, indent=2))


if __name__ == "__main__":
    main()
