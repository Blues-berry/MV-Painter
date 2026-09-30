#!/usr/bin/env python
"""Build an EXTENDED bake handoff that adds layer-wise conditions on top of
the frozen BAKE_INPUT_HANDOFF.json. The frozen handoff file is read-only; the
output is a new file. Panel crops follow the frozen slot mapping
(col = slot % 2, row = slot // 2) exactly like geotex/build_bake_input_handoff.py.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter")
FROZEN = ROOT / "final/round2/main_adapter_baking/BAKE_INPUT_HANDOFF.json"
PANELS = Path("/4T/tmp/mvpainter-layer-bake-input-20260930")
OUT = ROOT / "final/round2/main_adapter_baking/BAKE_INPUT_HANDOFF_LAYERWISE_20260930.json"
VIEW_OUT = ROOT / "final/round2/main_adapter_baking/frozen_views"
NEW_METHODS = ("layer_llh", "layer_lhl")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    handoff = json.loads(FROZEN.read_text())
    for record in handoff["objects"]:
        object_id = record["object"]
        generated = record["generated_conditions"]
        for method in NEW_METHODS:
            panel_path = PANELS / method / f"{object_id}.png"
            if not panel_path.exists():
                raise FileNotFoundError(panel_path)
            entry = {"panel": str(panel_path), "panel_sha256": sha256(panel_path), "target_views": []}
            panel = Image.open(panel_path).convert("RGB")
            if panel.size != (512, 768):
                raise RuntimeError(f"unexpected panel size {panel.size} for {panel_path}")
            for mapping in record["target_view_mapping"]:
                slot = int(mapping["slot"])
                raw_idx = int(mapping["raw_view_index"])
                col, row_index = slot % 2, slot // 2
                crop = panel.crop((col * 256, row_index * 256, (col + 1) * 256, (row_index + 1) * 256))
                vp = VIEW_OUT / object_id / method / f"slot_{slot}_raw_{raw_idx:03d}.png"
                vp.parent.mkdir(parents=True, exist_ok=True)
                crop.save(vp)
                entry["target_views"].append({
                    "slot": slot,
                    "raw_view_index": raw_idx,
                    "path": str(vp),
                    "sha256": sha256(vp),
                })
            generated[method] = entry
    handoff["protocol"] = "main-adapter-clean-v2-bake-input-handoff-v1-layerwise-extension"
    handoff["extends"] = str(FROZEN)
    handoff["conditions"] = list(handoff["conditions"]) + [m.upper() for m in NEW_METHODS]
    handoff["layerwise_generation_manifest"] = str(PANELS / "generation_manifest.json")
    handoff["status"] = "frozen geometry/UV/cameras/GT unchanged; layer-wise panels added from generation_manifest"
    OUT.write_text(json.dumps(handoff, indent=2) + "\n")
    print("extended handoff written:", OUT)


if __name__ == "__main__":
    main()
