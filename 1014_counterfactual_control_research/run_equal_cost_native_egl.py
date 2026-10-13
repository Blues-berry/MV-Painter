#!/usr/bin/env python3
"""Render the equal-call fixed-mean candidate set through the frozen EGL code."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ALT_BAKE = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/bake_equal_cost_b0_seed43")
HANDOFF = ALT_BAKE / "BAKE_INPUT_HANDOFF.json"
OUTPUT = ALT_BAKE / "native_egl_unseen"
BBOX_RECORDS = ALT_BAKE / "EGL_BBOX_RECORDS_FROM_HANDOFF.json"
FROZEN_RUNNER = Path("/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/final_code/run_fresh_c_native_egl_audit.py")
RENDERER = Path("/4T/CXY/MV-Painter-1010/1008/audits/source_evidence/r1/n20_glb/render_glb_native_egl.py")
OBJECTS = (
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
)
METHODS = ("gt", "counterfactual_b0", "counterfactual_b0_seed43")


def main() -> None:
    handoff = json.loads(HANDOFF.read_text())
    BBOX_RECORDS.write_text(json.dumps({
        "records": [
            {
                "uid": record["object"],
                "bbox_min_blender_world": record["blender_audit_bbox"]["bbox_min"],
                "bbox_max_blender_world": record["blender_audit_bbox"]["bbox_max"],
            }
            for record in handoff["objects"]
        ]
    }, indent=2) + "\n")
    spec = importlib.util.spec_from_file_location("frozen_equal_cost_egl_runner", FROZEN_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen EGL wrapper {FROZEN_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.EXTRACTION = BBOX_RECORDS
    module.RENDERER_SOURCE = RENDERER
    sys.argv = [
        str(FROZEN_RUNNER),
        "--bake-root", str(ALT_BAKE),
        "--handoff", str(HANDOFF),
        "--output-dir", str(OUTPUT),
        "--objects", ",".join(OBJECTS),
        "--methods", ",".join(METHODS),
        "--views", "1,2,3,4,5,6,7,8,9,10,11",
        "--resolution", "512",
    ]
    module.main()


if __name__ == "__main__":
    main()
