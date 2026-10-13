#!/usr/bin/env python3
"""Run the frozen native-EGL wrapper with bbox records embedded in our handoff."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
FROZEN_RUNNER = Path(
    "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/"
    "final_code/run_fresh_c_native_egl_audit.py"
)
HANDOFF = ROOT / "bake" / "BAKE_INPUT_HANDOFF.json"
BBOX_RECORDS = ROOT / "bake" / "EGL_BBOX_RECORDS_FROM_FROZEN_HANDOFF.json"
RENDERER_SOURCE = Path(
    "/4T/CXY/MV-Painter-1010/1008/audits/source_evidence/r1/n20_glb/"
    "render_glb_native_egl.py"
)


def main() -> None:
    handoff = json.loads(HANDOFF.read_text())
    records = []
    for row in handoff["objects"]:
        bbox = row.get("blender_audit_bbox")
        if not bbox or set(("bbox_min", "bbox_max")) - set(bbox):
            raise RuntimeError(f"missing frozen Blender bbox for {row['object']}")
        records.append({
            "uid": row["object"],
            "bbox_min_blender_world": bbox["bbox_min"],
            "bbox_max_blender_world": bbox["bbox_max"],
        })
    BBOX_RECORDS.write_text(json.dumps({"records": records}, indent=2) + "\n")

    spec = importlib.util.spec_from_file_location("frozen_native_egl_audit", FROZEN_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen renderer wrapper: {FROZEN_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The old wrapper points to a deleted extraction.json, while this immutable
    # handoff already carries the same Blender-audited bounding boxes.
    module.EXTRACTION = BBOX_RECORDS
    # The frozen wrapper's relative path is stale in this checkout. This is the
    # exact renderer path and SHA recorded by the historical native-EGL run.
    module.RENDERER_SOURCE = RENDERER_SOURCE
    module.main()


if __name__ == "__main__":
    main()
