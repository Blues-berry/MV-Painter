#!/usr/bin/env python3
"""Write a reproducible provenance and generated-output hash index."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
WORKTREE = Path("/4T/tmp/MV-Painter-counterfactual")
LOCAL_EXCLUDED = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def item(path: str | Path, relative_to: Path | None = None) -> dict[str, str]:
    source = Path(path)
    label = str(source.relative_to(relative_to)) if relative_to else str(source)
    return {"path": label, "sha256": sha256(source)}


def main() -> None:
    phase_a = json.loads((ROOT / "phase_a_identity_audit.json").read_text())
    gen = json.loads((ROOT / "generation/run_manifest_shard0.json").read_text())
    bake = json.loads((ROOT / "bake/BAKE_RUN_SUMMARY.json").read_text())
    egl_id = json.loads((ROOT / "bake/native_egl_unseen_RUN_IDENTITY.json").read_text())
    render = json.loads((ROOT / "bake/native_egl_unseen/GLB_NATIVE_EGL_RENDER_MANIFEST.json").read_text())
    equal_cost_gen = json.loads((LOCAL_EXCLUDED / "generation_equal_cost_b0_seed43/run_manifest_shard0.json").read_text())
    equal_cost_bake = json.loads((LOCAL_EXCLUDED / "bake_equal_cost_b0_seed43/cpu_bake_v3/BAKE_RUN_SUMMARY.json").read_text())
    equal_cost_egl_id = json.loads((LOCAL_EXCLUDED / "bake_equal_cost_b0_seed43/native_egl_unseen_RUN_IDENTITY.json").read_text())
    equal_cost_render = json.loads((LOCAL_EXCLUDED / "bake_equal_cost_b0_seed43/native_egl_unseen/GLB_NATIVE_EGL_RENDER_MANIFEST.json").read_text())

    worktree_files = [
        "MVPainter/mvpainter/model_unet_geotex.py",
        "MVPainter/mvpainter/view_scale_audit.py",
        "geotex/explore_contradiction.py",
        "geotex/run_counterfactual_experiment.py",
        "geotex/run_counterfactual_b0_seed43.py",
        "tests/test_view_scale_audit.py",
    ]
    local_scripts = sorted(ROOT.glob("*.py"))
    immutable_paths = {
        "checkpoint": gen["checkpoint"],
        "generation_config": gen["config"],
        "generation_spec": gen["a3_spec"],
        "source_handoff": phase_a["source_handoff"],
        "frozen_generation_identity": phase_a["frozen_identity_path"],
        "frozen_object_list": phase_a["object_list"],
        "uv_baker": "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/final_code/bake_fresh_c_native_uv.py",
        "native_egl_renderer": egl_id["renderer_source_path"],
        "native_egl_evaluator": "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/final_code/evaluate_fresh_c_native_egl.py",
        "latest_1014_manuscript_source": "/4T/CXY/MV-Painter/final_paper_20261012/source/Manuscript_final.tex",
        "latest_1014_supplement_source": "/4T/CXY/MV-Painter/final_paper_20261012/source/Supplementary_final.tex",
        "latest_1014_manuscript_pdf": "/4T/CXY/MV-Painter/final_paper_20261012/deliverables/Manuscript_final.pdf",
        "latest_1014_supplement_pdf": "/4T/CXY/MV-Painter/final_paper_20261012/deliverables/Supplementary_final.pdf",
    }

    generation_panels = {}
    with (ROOT / "generation/GENERATION_VIEW_METRICS.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            path = Path(row["output_path"])
            actual_sha = sha256(path)
            if actual_sha != row["output_sha256"]:
                raise RuntimeError(f"generation image hash mismatch: {path}")
            generation_panels[str(path.relative_to(ROOT))] = actual_sha

    textures_and_glbs = []
    for record in bake["records"]:
        for kind, path_key in (("texture_png", "texture_path"), ("textured_glb", "output_textured_glb")):
            source = Path(record[path_key])
            actual_sha = sha256(source)
            if kind == "textured_glb" and actual_sha != record["output_textured_glb_sha256"]:
                raise RuntimeError(f"baked GLB hash mismatch: {source}")
            textures_and_glbs.append({
                "object": record["object"],
                "condition": record["method"],
                "kind": kind,
                "path": str(source.relative_to(ROOT)),
                "sha256": actual_sha,
            })

    unseen_renders = []
    for record in render["renders"]:
        path = ROOT / "bake/native_egl_unseen" / record["render_path"]
        actual_sha = sha256(path)
        if actual_sha != record["render_sha256"]:
            raise RuntimeError(f"native EGL image hash mismatch: {path}")
        unseen_renders.append({
            "object": record["object"],
            "condition": record["method"],
            "raw_camera": record["raw_view"],
            "path": str(path.relative_to(ROOT)),
            "sha256": actual_sha,
        })

    git = subprocess.run(
        ["git", "-C", str(WORKTREE), "rev-parse", "HEAD", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for label, source in gen["code_source_sha256"].items():
        if sha256(Path(source["path"])) != source["sha256"]:
            raise RuntimeError(f"generation source hash mismatch: {label}")

    source_code = {
        "worktree_changes": [item(WORKTREE / path, WORKTREE) for path in worktree_files],
        "research_scripts": [item(path, ROOT) for path in local_scripts],
        "generation_manifest_sources": gen["code_source_sha256"],
        "upstream_baker_sha256": bake["records"][0]["baker_source_sha256"],
        "native_egl_renderer_sha256": egl_id["renderer_source_sha256"],
        "native_egl_wrapper_sha256": egl_id["wrapper_source_sha256"],
        "equal_cost_generation_manifest_sources": equal_cost_gen["code_source_sha256"],
        "equal_cost_upstream_baker_sha256": equal_cost_bake["records"][0]["baker_source_sha256"],
        "equal_cost_native_egl_renderer_sha256": equal_cost_egl_id["renderer_source_sha256"],
    }
    output_files = [
        "ACTION_RESPONSE_RESULTS.csv",
        "ACTION_RESPONSE_SUMMARY.json",
        "generation/GENERATION_VIEW_METRICS.csv",
        "generation/GENERATION_VIEW_METRICS_MANIFEST.json",
        "bake/BAKE_RUN_SUMMARY.json",
        "bake/native_egl_unseen/GLB_NATIVE_EGL_RENDER_MANIFEST.json",
        "bake/native_egl_unseen/NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv",
        "bake/native_egl_unseen/NATIVE_EGL_UNSEEN_PER_VIEW_METRICS.csv",
        "bake/native_egl_unseen/NATIVE_EGL_METRIC_EVALUATION.json",
        "EQUAL_COST_CANDIDATE_SELECTION.md",
        "EQUAL_COST_CANDIDATE_SELECTION_RESULTS.csv",
        "EQUAL_COST_CANDIDATE_SELECTION_SUMMARY.json",
        "equal_cost_phase_a_audit.json",
        "evaluate_equal_cost_b0_seed43.py",
        "prepare_equal_cost_b0_handoff.py",
        "run_equal_cost_native_egl.py",
        "audit_equal_cost_identity.py",
        "analyze_equal_cost_comparison.py",
        "make_equal_cost_visuals.py",
        "COUNTERFACTUAL_PROTOCOL.md",
        "INTERVENTION_IDENTITY_AUDIT.md",
        "SOURCE_TO_BAKE_DIRECTION_ANALYSIS.md",
        "FAILURE_CASES.md",
        "PRIOR_ART_COMPARISON.md",
        "FINAL_GO_NO_GO.md",
    ]
    visual_outputs = sorted(path for path in (ROOT / "visuals").iterdir() if path.is_file())
    archive_root = ROOT / "EQUAL_COST_BASELINE"
    archive_files = sorted(path for path in archive_root.rglob("*") if path.is_file())
    alternate_uids = [
        "1dc2c857f7614caeb6c2aa0559ccf973", "21678bd623654182b52c11d013de4e71",
        "238ff3e41c964655b83aa9c8770cc766", "2dd9bc8172c6461797947cc7214db399",
        "2f6c94487ee54cb88021f4643409d849", "e261c0fe85af46388260e2359a9bfc92",
    ]
    alternate_panel_hashes = []
    for uid in alternate_uids:
        path = LOCAL_EXCLUDED / "generation_equal_cost_b0_seed43/predictions/counterfactual_b0" / f"{uid}.png"
        alternate_panel_hashes.append(item(path, LOCAL_EXCLUDED))

    equal_cost_unseen_renders = []
    for record in equal_cost_render["renders"]:
        path = LOCAL_EXCLUDED / "bake_equal_cost_b0_seed43/native_egl_unseen" / record["render_path"]
        actual_sha = sha256(path)
        if actual_sha != record["render_sha256"]:
            raise RuntimeError(f"equal-cost EGL image hash mismatch: {path}")
        equal_cost_unseen_renders.append({
            "object": record["object"], "condition": record["method"],
            "raw_camera": record["raw_view"],
            "path": str(path.relative_to(LOCAL_EXCLUDED)), "sha256": actual_sha,
        })

    for subdir, source_dir in (
        ("generation", LOCAL_EXCLUDED / "generation_equal_cost_b0_seed43"),
        ("bake", LOCAL_EXCLUDED / "bake_equal_cost_b0_seed43"),
    ):
        for original in source_dir.rglob("*"):
            if original.is_file():
                copied = archive_root / subdir / original.relative_to(source_dir)
                if sha256(original) != sha256(copied):
                    raise RuntimeError(f"equal-cost archival copy mismatch: {copied}")

    manifest = {
        "study": "view-wise counterfactual geometry-control test",
        "generated_at_utc": "2026-10-13",
        "worktree": str(WORKTREE),
        "branch": git[1],
        "base_commit": "384f97e2a6e23b17555fa88f1a7f5fcb48d6e3bb",
        "current_head": git[0],
        "immutable_inputs_and_reference_release": {
            name: item(path) for name, path in immutable_paths.items()
        },
        "source_code": source_code,
        "results_and_visualization_files": {
            path: item(ROOT / path, ROOT) for path in output_files
        },
        "visualization_files": {path.name: item(path, ROOT) for path in visual_outputs},
        "equal_cost_archive_file_hashes": [item(path, ROOT) for path in archive_files],
        "generated_artifact_hashes": {
            "generation_panels": [
                {"path": path, "sha256": digest}
                for path, digest in sorted(generation_panels.items())
            ],
            "uv_textures_and_textured_glbs": textures_and_glbs,
            "native_egl_unseen_renders": unseen_renders,
            "equal_cost_generation_panels": alternate_panel_hashes,
            "equal_cost_native_egl_renders": equal_cost_unseen_renders,
            "equal_cost_bake_records": equal_cost_bake["records"],
        },
        "counts": {
            "generation_panels": len(generation_panels),
            "uv_textures_and_textured_glbs": len(textures_and_glbs),
            "native_egl_unseen_renders": len(unseen_renders),
            "equal_cost_generation_calls": len(json.loads((LOCAL_EXCLUDED / "generation_equal_cost_b0_seed43/rows_shard0.json").read_text())),
            "equal_cost_bakes": len(equal_cost_bake["records"]),
            "equal_cost_native_egl_renders": equal_cost_egl_id["render_count"],
            "objects": 6,
            "conditions": 3,
        },
        "notes": [
            "Generation panel hashes are recorded in the original per-view generation CSV and repeated here for a compact integrity check.",
            "The 264 EGL render hashes are cross-referenced from GLB_NATIVE_EGL_RENDER_MANIFEST.json.",
            "Native EGL images are unlit base-color renders and do not represent a full PBR assessment.",
        ],
    }
    (ROOT / "SOURCE_HASH_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
