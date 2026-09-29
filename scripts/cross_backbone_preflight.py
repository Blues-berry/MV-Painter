#!/usr/bin/env python3
"""Inventory cross-backbone candidates without starting model inference.

This is intentionally a preflight tool rather than a benchmark runner.  It
checks whether the official source/weights, the shared Objaverse protocol and
the expected result artifacts are present, while keeping semantic mismatches
explicit.  A candidate marked ``ready`` is not automatically a valid TCAS
transfer: the ``evidence_role`` field records what may be claimed in the
paper.

Example::

    python scripts/cross_backbone_preflight.py \
        --output release/round2_repro/cross_backbone_preflight.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    paper_fit: str
    condition_interface: str
    official_source: str
    official_paper: str
    local_paths: tuple[str, ...]
    evidence_role: str
    next_action: str


CANDIDATES = (
    CandidateSpec(
        name="mvpainter_geotex",
        paper_fit="anchor",
        condition_interface="five-channel GeoTex residual adapter in a joint six-view UNet",
        official_source="local MVPainter implementation",
        official_paper="https://arxiv.org/abs/2505.12635",
        local_paths=(
            "MVPainter/configs/mvpainter-geotex-full-train.yaml",
            "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt",
            "final/round2/main_adapter_clean_v2/main_adapter_clean_v2_strict276.csv",
        ),
        evidence_role="main-backbone anchor; absolute scores are reported only here",
        next_action="keep as the reference protocol and do not merge absolute scores with other backbones",
    ),
    CandidateSpec(
        name="mv_adapter_sd21",
        paper_fit="strict cross-backbone",
        condition_interface="official image+geometry adapter on SD2.1 with per-step residual scaling",
        official_source="https://github.com/huanngzh/MV-Adapter",
        official_paper="https://arxiv.org/abs/2412.03632",
        local_paths=(
            "final/round2/mv_adapter/upstream",
            "final/round2/mv_adapter/models/sd21_base",
            "final/round2/mv_adapter/models/mv-adapter/mvadapter_ig2mv_sd21.safetensors",
            "final/round2/mv_adapter/data_manifest.json",
            "final/round2/mv_adapter/results/holdout_exact_76/per_object_metrics.csv",
        ),
        evidence_role="primary second-backbone diagnostic; paired within-backbone deltas only",
        next_action="use the existing Exact 24/76 results, but report stage effects without claiming a unique TCAS winner",
    ),
    CandidateSpec(
        name="mvdiffusion_depth",
        paper_fit="high task fit, interop diagnostic completed",
        condition_interface="multi-view depth-conditioned diffusion with correspondence-aware attention",
        official_source="https://github.com/Tangshitao/MVDiffusion",
        official_paper="https://arxiv.org/abs/2307.01097",
        local_paths=(
            "final/round2/mvdiffusion/upstream",
            "final/round2/mvdiffusion/models/sd21_depth_compat",
            "final/round2/mvdiffusion/upstream/weights/depth_gen_new.pth",
            "final/round2/mvdiffusion/data_manifest_holdout_exact_75.json",
            "final/round2/mvdiffusion/data/scannet/holdout_exact_75",
        ),
        evidence_role="independent geometry-conditioned interop diagnostic; not a pooled absolute baseline",
        next_action="rerun with the native official SD2-depth base before making a paper-quality absolute claim; preserve the text/depth and orthographic-to-pinhole distinction",
    ),
    CandidateSpec(
        name="nvs_adapter_sd21",
        paper_fit="adapter transfer candidate",
        condition_interface="SD2.1 NVS-Adapter; optional depth ControlNet is a separate SD1.5 path",
        official_source="https://github.com/POSTECH-CVLab/nvsadapter",
        official_paper="https://arxiv.org/abs/2309.03453",
        local_paths=(),
        evidence_role="low-cost adapter-strength diagnostic, not a direct six-view geometry-texture replication",
        next_action="only stage after fixing the view-count and SD-version mismatch; use a four-view subset and label it exploratory",
    ),
    CandidateSpec(
        name="wonder3d",
        paper_fit="boundary baseline",
        condition_interface="cross-domain image-conditioned multi-view UNet; no external geometry residual adapter",
        official_source="https://github.com/xxlong0/Wonder3D",
        official_paper="https://arxiv.org/abs/2310.15008",
        local_paths=(
            "/4T/CXY/Wonder3D",
            "mvpoutput/wonder3d_tcas/input_images_shard000",
            "mvpoutput/wonder3d_tcas/input_images_shard150",
            "mvpoutput/wonder3d_tcas/outputs_shard000/cropsize-192-cfg3.0",
            "mvpoutput/wonder3d_tcas/outputs_shard150/cropsize-192-cfg3.0",
        ),
        evidence_role="deployment/data-pipeline boundary check only; do not call condition scaling TCAS transfer",
        next_action="retain the 299-object output inventory as a baseline asset, but do not add it to the adapter-stage table",
    ),
    CandidateSpec(
        name="era3d",
        paper_fit="multi-view baseline, weak TCAS fit",
        condition_interface="high-resolution image-conditioned six-view diffusion; no explicit mesh residual adapter",
        official_source="https://github.com/pengHTYX/Era3D",
        official_paper="https://arxiv.org/abs/2405.11616",
        local_paths=(),
        evidence_role="quality/reference baseline only",
        next_action="do not prioritize for this revision; it adds a generator comparison, not a clean adapter-strength test",
    ),
    CandidateSpec(
        name="mvedit_3d_adapter",
        paper_fit="geometry-consistent but operationally unsuitable",
        condition_interface="optimization-based 3D-Adapter/MVEdit around off-the-shelf multi-view priors",
        official_source="https://github.com/Lakonik/MVEdit",
        official_paper="https://arxiv.org/abs/2410.18974",
        local_paths=(),
        evidence_role="not suitable for the current controlled TCAS table",
        next_action="defer: official README notes the GRM-based adapter release limitation and requires at least 24GB GPU memory",
    ),
)


def resolve_path(raw: str, root: Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def inspect_paths(spec: CandidateSpec, root: Path) -> list[dict[str, object]]:
    checks = []
    for raw in spec.local_paths:
        path = resolve_path(raw, root)
        checks.append(
            {
                "declared": raw,
                "resolved": str(path),
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            }
        )
    return checks


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def finite_metric_rows(rows: Iterable[dict[str, str]]) -> bool:
    ignored = {"object", "schedule", "geometry_source", "mesh_path", "reference_image"}
    for row in rows:
        for key, value in row.items():
            if key in ignored or value in (None, ""):
                continue
            try:
                if not math.isfinite(float(value)):
                    return False
            except ValueError:
                # Non-numeric provenance columns are allowed.
                continue
    return True


def candidate_result_check(spec: CandidateSpec, root: Path) -> dict[str, object]:
    if spec.name == "mvpainter_geotex":
        result_path = root / "final/round2/main_adapter_clean_v2/main_adapter_clean_v2_strict276.csv"
        if not result_path.is_file():
            return {"status": "not_available", "reason": "main clean-v2 CSV is missing"}
        rows = read_rows(result_path)
        return {
            "status": "anchor_artifacts_ready",
            "row_count": len(rows),
            "interpretation": "main-backbone anchor; use its own absolute-score protocol",
        }
    if spec.name == "mv_adapter_sd21":
        csv_path = root / "final/round2/mv_adapter/results/holdout_exact_76/per_object_metrics.csv"
        if not csv_path.is_file():
            return {"status": "not_available", "reason": "Exact holdout CSV is missing"}
        rows = read_rows(csv_path)
        objects = sorted({row.get("object") for row in rows if row.get("object")})
        schedules = sorted({row.get("schedule") for row in rows if row.get("schedule")})
        exact = all(row.get("geometry_source") == "exact_mesh" for row in rows)
        return {
            "status": "ready",
            "row_count": len(rows),
            "object_count": len(objects),
            "schedule_count": len(schedules),
            "schedules": schedules,
            "all_exact_mesh": exact,
            "all_numeric_values_finite": finite_metric_rows(rows),
            "interpretation": "diagnostic stage-placement evidence; no unique CAI winner",
        }
    if spec.name == "mvdiffusion_depth":
        data_manifest = root / "final/round2/mvdiffusion/data_manifest_holdout_exact_75.json"
        checkpoint = root / "final/round2/mvdiffusion/upstream/weights/depth_gen_new.pth"
        metrics = root / "final/round2/mvdiffusion/results/holdout_exact_75_50steps/per_object_metrics.csv"
        if not data_manifest.is_file():
            return {"status": "not_staged", "reason": "interop data manifest is missing"}
        if metrics.is_file():
            rows = read_rows(metrics)
            object_count = len({row.get("object") for row in rows})
            expected_object_count = len(json.loads(data_manifest.read_text()).get("objects", []))
            complete = len(rows) == expected_object_count and object_count == expected_object_count
            summary_path = metrics.parent / "summary.json"
            summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
            run_config_path = metrics.parent / "run_config.json"
            run_config = json.loads(run_config_path.read_text()) if run_config_path.is_file() else {}
            base_provenance = run_config.get("base_provenance", {})
            return {
                "status": "ready" if complete else "incomplete",
                "row_count": len(rows),
                "object_count": object_count,
                "expected_object_count": expected_object_count,
                "complete_object_set": complete,
                "all_numeric_values_finite": finite_metric_rows(rows),
                "mean": summary.get("mean"),
                "steps": run_config.get("steps"),
                "native_official_depth_base": base_provenance.get("native_official_depth_base"),
                "interpretation": "interop diagnostic only; absolute scores are not pooled across backbones",
            }
        return {
            "status": "staged_inputs_ready" if checkpoint.is_file() else "awaiting_checkpoint",
            "data_object_count": len(json.loads(data_manifest.read_text()).get("objects", [])),
            "checkpoint_present": checkpoint.is_file(),
            "interpretation": "no inference result has been certified yet",
        }
    if spec.name == "wonder3d":
        input_paths = list((root / "mvpoutput/wonder3d_tcas").glob("input_images_shard*/*.png"))
        output_paths = list(
            (root / "mvpoutput/wonder3d_tcas").glob(
                "outputs_shard*/cropsize-192-cfg3.0/*/rgb_000_*.png"
            )
        )
        expected = len(input_paths) * 6
        return {
            "status": "baseline_inventory_ready" if output_paths else "not_available",
            "input_count": len(input_paths),
            "rgb_output_count": len(output_paths),
            "expected_six_view_output_count": expected,
            "complete_six_view_sets": len(output_paths) == expected,
            "interpretation": "generation baseline only; no geometry-residual TCAS semantics",
        }
    return {"status": "not_staged", "reason": "no local source/weights registered"}


def runtime_probe() -> dict[str, object]:
    result: dict[str, object] = {
        "nvidia_smi": shutil.which("nvidia-smi"),
        "torch_cuda_available": False,
        "torch_device_count": 0,
    }
    try:
        import torch

        result["torch_version"] = torch.__version__
        result["torch_cuda_available"] = bool(torch.cuda.is_available())
        result["torch_device_count"] = int(torch.cuda.device_count())
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        result["torch_error"] = f"{type(exc).__name__}: {exc}"
    if result["nvidia_smi"]:
        try:
            probe = subprocess.run(
                [str(result["nvidia_smi"]), "-L"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            result["nvidia_smi_returncode"] = probe.returncode
            result["nvidia_smi_output"] = probe.stdout.strip() or probe.stderr.strip()
        except Exception as exc:  # pragma: no cover - diagnostic fallback
            result["nvidia_smi_error"] = f"{type(exc).__name__}: {exc}"
    return result


def build_report(root: Path) -> dict[str, object]:
    candidates = []
    for spec in CANDIDATES:
        path_checks = inspect_paths(spec, root)
        candidates.append(
            {
                **asdict(spec),
                "local_paths": path_checks,
                "all_declared_paths_present": (
                    all(check["exists"] for check in path_checks) if path_checks else None
                ),
                "result_check": candidate_result_check(spec, root),
            }
        )
    return {
        "protocol": "cross-backbone-preflight-v1",
        "root": str(root),
        "runtime": runtime_probe(),
        "claim_policy": {
            "absolute_scores_across_backbones": False,
            "shared_factors_required_for_paired_claim": [
                "object identifiers",
                "seed and initial latent",
                "target camera IDs",
                "resolution and denoising steps",
                "metric implementation and foreground mask",
            ],
            "ready_does_not_mean_positive_transfer": True,
        },
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
