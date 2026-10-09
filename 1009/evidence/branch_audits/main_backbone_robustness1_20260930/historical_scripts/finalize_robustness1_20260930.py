#!/usr/bin/env python
"""Finalize Robustness-1 artifacts: RUN_MANIFEST.json + ARTIFACT_SHA256SUMS.txt.

Copies the R1 per-object rows to the task root (per_object_metrics.csv,
per §12 of the task spec) and records protocol hashes, row counts, git state,
and artifact checksums. Run after all runs and the analysis complete.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
TASK = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
R0_DIR = Path("/4T/tmp/mvpainter-layer-confirmation-20260930")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    return len(json.loads(path.read_text()))


def main() -> None:
    # §12: top-level per_object_metrics.csv = R1 combined rows
    src = TASK / "realization1_core5/per_object_metrics.csv"
    if src.exists():
        shutil.copyfile(src, TASK / "per_object_metrics.csv")

    r1_rows = count_rows(TASK / "realization1_core5/rows.json")
    r0c3_rows = count_rows(TASK / "r0_completion_global_c3/rows.json")
    anchor = TASK / "r0_anchor_llh_10/anchor_comparison.json"
    analysis = TASK / "R0_R1_STABILITY_SUMMARY.json"

    manifest = {
        "task": "main-backbone Core-5 Robustness-1 (independent reference-preprocessing realization)",
        "date": "2026-09-30",
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_commit": git("rev-parse", "HEAD"),
        "base_branch": "codex/next-review-response-20260930",
        "base_commit": "edfb8d0",
        "protocol_lock": "PROTOCOL_LOCK.md (frozen before any R1 observation)",
        "dataset": {
            "object_list": "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt",
            "object_list_sha256": sha256(ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"),
            "n_objects": 276,
            "view_mode": "unique6 [0, 15, 12, 16, 13, 14]",
            "resolution": "256x256",
        },
        "checkpoint": {
            "path": "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt",
            "sha256": sha256(ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"),
        },
        "config": "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml",
        "sampler": "EulerDiscreteScheduler, 50 steps",
        "seed_policies": {
            "R0_reference": "object_seed = 42 + object_idx (random/np/torch before collate)",
            "R1_reference": "object_seed = 10042 + object_idx (random/np/torch before collate)",
            "latent": "torch.manual_seed(42) before initial latent and again before generation",
        },
        "methods": {
            "GFL": "global_fixed_low = 1.25",
            "GC3": "global_c3 = stage(p, 1.25, 2.50, 1.25)",
            "LFM": "layer_fixed_mean = deep/middle 1.65, shallow 0.58",
            "L-LHL": "layer_lhl = deep/middle stage(1.25,2.50,1.25), shallow stage(0.50,0.75,0.50)",
            "L-LLH": "layer_llh = deep/middle stage(1.25,1.25,2.50), shallow stage(0.50,0.50,0.75)",
        },
        "metric_path": "geotex.eval_exploration.compute_metrics",
        "bootstrap": "10,000 resamples, seed 20260930, paired percentile CI, object-level",
        "scripts": {
            name: sha256(ROOT / "scripts" / name)
            for name in [
                "run_robustness1_core5_20260930.py",
                "robustness1_shared_input_audit_20260930.py",
                "check_robustness1_shared_input_20260930.py",
                "robustness1_reference_realization_difference_20260930.py",
                "analyze_robustness1_20260930.py",
                "launch_robustness1_formal_20260930.sh",
            ]
        },
        "frozen_runner_reference": {
            "script": "scripts/run_layer_confirmation_276_20260930.py",
            "sha256": sha256(ROOT / "scripts/run_layer_confirmation_276_20260930.py"),
        },
        "row_counts": {
            "R1_core5_expected": 1380,
            "R1_core5_completed": r1_rows,
            "R0_c3_completion_expected": 276,
            "R0_c3_completion_completed": r0c3_rows,
            "R0_anchor_llh_10": count_rows(TASK / "r0_anchor_llh_10/rows.json"),
        },
        "preflight_gate": json.loads((TASK / "ROBUSTNESS1_SHARED_INPUT_AUDIT.json").read_text())["verdict"],
        "anchor_check": json.loads(anchor.read_text()) if anchor.exists() else "pending",
        "analysis_summary": json.loads(analysis.read_text())["classification_counts"] if analysis.exists() else "pending",
    }
    (TASK / "RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # SHA-256 index of all task artifacts (files only, relative paths)
    lines = []
    for path in sorted(TASK.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_SHA256SUMS.txt":
            rel = path.relative_to(TASK)
            lines.append(f"{sha256(path)}  {rel}")
    (TASK / "ARTIFACT_SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
    print(f"RUN_MANIFEST.json written; R1 rows={r1_rows}/1380, R0-C3 rows={r0c3_rows}/276; "
          f"{len(lines)} artifacts hashed")


if __name__ == "__main__":
    main()
