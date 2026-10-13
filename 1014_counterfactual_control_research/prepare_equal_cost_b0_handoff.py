#!/usr/bin/env python3
"""Add the second fixed-mean seed as a paired candidate in a separate handoff."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
ALT_GENERATION = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/generation_equal_cost_b0_seed43")
ALT_BAKE = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/bake_equal_cost_b0_seed43")
LOCAL_EXCLUDED_ROOT = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research")
BASE_HANDOFF = ROOT / "bake/BAKE_INPUT_HANDOFF.json"
ALT_METHOD = "counterfactual_b0_seed43"
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    base = json.loads(BASE_HANDOFF.read_text())
    records = {record["object"]: copy.deepcopy(record) for record in base["objects"]}
    original_rows = json.loads((ROOT / "generation/rows_shard0.json").read_text())
    alternate_rows = json.loads((ALT_GENERATION / "rows_shard0.json").read_text())
    original = {(int(row["object_idx"]), row["condition"]): row for row in original_rows}
    alternate = {(int(row["object_idx"]), row["condition"]): row for row in alternate_rows}
    uids = [line.strip() for line in Path(
        "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/bake_uids.txt"
    ).read_text().splitlines() if line.strip()]

    ALT_BAKE.mkdir(parents=True, exist_ok=True)
    for index in (0, 1, 2, 3, 4, 7):
        uid = uids[index]
        old = original[(index, "counterfactual_b0")]["input_hashes"]
        new = alternate[(index, "counterfactual_b0")]["input_hashes"]
        if any(old[key] != new[key] for key in old if key != "init_latent"):
            raise RuntimeError(f"non-latent inputs differ for {uid}")
        if old["init_latent"] == new["init_latent"]:
            raise RuntimeError(f"alternate latent is not distinct for {uid}")

        record = records[uid]
        for condition, condition_record in record.get("generated_conditions", {}).items():
            remapped_views = []
            for view in condition_record["target_views"]:
                source = Path(view["path"])
                suffix = source.relative_to(ROOT)
                local_source = LOCAL_EXCLUDED_ROOT / suffix
                if not local_source.is_file():
                    raise FileNotFoundError(local_source)
                crop = ALT_BAKE / "input_views" / uid / condition / source.name
                crop.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_source, crop)
                remapped_views.append({**view, "path": str(crop), "sha256": sha256(crop)})
            condition_record["target_views"] = remapped_views

        panel = ALT_GENERATION / "predictions/counterfactual_b0" / f"{uid}.png"
        with Image.open(panel) as source:
            panel_image = source.convert("RGB")
            if panel_image.size != (512, 768):
                raise RuntimeError(f"unexpected panel size {panel_image.size}: {panel}")
            target_views = []
            for mapping in record["target_view_mapping"]:
                slot = int(mapping["slot"])
                col, row = slot % 2, slot // 2
                crop = ALT_BAKE / "input_views" / uid / ALT_METHOD / f"slot_{slot}.png"
                crop.parent.mkdir(parents=True, exist_ok=True)
                panel_image.crop((col * 256, row * 256, (col + 1) * 256, (row + 1) * 256)).save(crop)
                target_views.append({
                    "slot": slot,
                    "raw_view_index": int(mapping["raw_view_index"]),
                    "path": str(crop),
                    "sha256": sha256(crop),
                })
        record.setdefault("generated_conditions", {})[ALT_METHOD] = {
            "panel_path": str(panel),
            "panel_sha256": sha256(panel),
            "latent_seed": 43,
            "target_views": target_views,
        }

    run_identity = ALT_GENERATION / "run_manifest_shard0.json"
    handoff = {
        **base,
        "status": "EQUAL_COST_FIXED_MEAN_SEED_CANDIDATE_HANDOFF",
        "conditions": ["gt", "counterfactual_b0", ALT_METHOD],
        "objects": [records[uid] for uid in UIDS],
        "alternate_candidate_run_manifest": str(run_identity),
        "alternate_candidate_run_manifest_sha256": sha256(run_identity),
        "fixed_mean_seed42_vs_seed43_shared_inputs_except_init_latent": True,
    }
    path = ALT_BAKE / "BAKE_INPUT_HANDOFF.json"
    path.write_text(json.dumps(handoff, indent=2) + "\n")
    print(json.dumps({"handoff": str(path), "objects": len(UIDS), "alternate_method": ALT_METHOD}, indent=2))


if __name__ == "__main__":
    main()
