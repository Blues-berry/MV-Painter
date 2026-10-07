"""Layer-wise (per-injection-point) wrapper around the frozen MV-Adapter runner.

Reuses run_experiment.py machinery (dataset loading, schedules, pipeline,
seed, cameras, metrics) without modification. The only addition is a wrapper
around ``pipe.cond_encoder.forward`` that pre-multiplies each of the four
output features by its frozen layer multiplier, so the existing per-step
global scaling inside the pipeline yields

    effective_scale(point, t) = layer_multiplier(point) * temporal_scale(t)

With all multipliers = 1.0 the wrapped features are bitwise identical to the
original ones, which the identity audit verifies. Scaling is inference-only;
no model weight is modified.

Protocol: MVADAPTER_LAYERWISE_PROTOCOL.md (pre-registered).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import torch

from run_experiment import (  # noqa: E402
    load_rows,
    object_metrics,
    save_grid,
    schedule_for_name,
)


CANONICAL_LABELS = {
    "FIXED_MEAN": "L-FIX",
    "LHL": "L-LHL",
    "LLH": "L-LLH",
}

# FIXED_MEAN reuses the existing global constant-scale code path at 5/6,
# identical to the equal-budget run's "fixed_0.8333333333333334" schedule.
GLOBAL_NAME_FOR = {
    "FIXED_MEAN": f"fixed_{5 / 6!r}",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_multipliers(profile_path: Path, identity: bool) -> list[float]:
    if identity:
        return [1.0, 1.0, 1.0, 1.0]
    payload = json.loads(profile_path.read_text())
    values = payload["target_mapping"]["per_point_multiplier_list_by_adapter_state_index"]
    if len(values) != 4:
        raise ValueError(f"expected 4 per-point multipliers, got {len(values)}")
    if any(not isinstance(v, (int, float)) or v < 0 for v in values):
        raise ValueError("multipliers must be non-negative numbers")
    return [float(v) for v in values]


def apply_layer_multipliers(pipe, multipliers: list[float], diagnostics: dict) -> None:
    """Wrap cond_encoder.forward: per-point pre-multiplication + shape audit."""

    original_forward = pipe.cond_encoder.forward

    def forward(x):
        features = original_forward(x)
        if not diagnostics.get("shapes_logged"):
            diagnostics["shapes_logged"] = True
            diagnostics["adapter_state_shapes"] = [list(f.shape) for f in features]
            if len(features) != len(multipliers):
                raise RuntimeError(
                    f"cond_encoder returned {len(features)} features, "
                    f"expected {len(multipliers)} injection points"
                )
            diagnostics["first_call_input_norms"] = [
                float(f.float().norm()) for f in features
            ]
            diagnostics["first_call_scaled_norms"] = [
                float((f * m).float().norm()) for f, m in zip(features, multipliers)
            ]
            diagnostics["first_call_norm_ratios"] = [
                s / n if n else float("nan")
                for s, n in zip(diagnostics["first_call_scaled_norms"], diagnostics["first_call_input_norms"])
            ]
        return [f * m for f, m in zip(features, multipliers)]

    pipe.cond_encoder.forward = forward


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter-path", type=Path, required=True)
    parser.add_argument("--layer-profile", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--split", choices=("calibration", "holdout"), required=True)
    parser.add_argument("--geometry-source", choices=("exact", "mixed"), default="exact")
    parser.add_argument("--proxy-manifest", type=Path, default=None)
    parser.add_argument("--exact-mesh-root", type=Path, default=None)
    parser.add_argument("--object", dest="object_ids", action="append", default=None,
                        help="restrict a diagnostic run to one or more manifest object IDs")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--seed", type=int, default=20260928)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--low", type=float, required=True)
    parser.add_argument("--high", type=float, required=True)
    parser.add_argument("--schedule", action="append", default=[],
                        help="FIXED_MEAN, LHL or LLH (canonical layer-wise conditions); "
                             "global schedule names also accepted for the identity audit")
    parser.add_argument("--identity", action="store_true",
                        help="force all layer multipliers to 1.0 (identity audit)")
    parser.add_argument("--resume", action="store_true",
                        help="skip (object, schedule) rows already present in the CSV")
    args = parser.parse_args()

    if not torch.cuda.is_available() or not args.device.startswith("cuda"):
        raise RuntimeError("formal MV-Adapter experiments require an explicit CUDA device")
    if not args.identity and args.layer_profile is None:
        raise ValueError("--layer-profile is required unless --identity is set")

    schedule_names = args.schedule or ["FIXED_MEAN", "LHL", "LLH"]
    canonical = {name: CANONICAL_LABELS.get(name.upper(), name) for name in schedule_names}
    multipliers = load_multipliers(args.layer_profile, args.identity)

    from scripts.inference_ig2mv_sd import prepare_pipeline, run_pipeline  # noqa: E402
    from geotex.metrics.image_metrics import get_lpips_fn  # noqa: E402

    rows = load_rows(
        args.manifest,
        args.split,
        args.geometry_source,
        args.proxy_manifest,
        args.object_ids,
        args.exact_mesh_root,
    )

    device = args.device
    pipe = prepare_pipeline(
        base_model=str(args.base_model),
        vae_model=None,
        unet_model=None,
        lora_model=None,
        adapter_path=str(args.adapter_path),
        scheduler="ddpm",
        num_views=6,
        device=device,
        dtype=torch.float16,
    )
    diagnostics: dict = {"shapes_logged": False, "identity_mode": bool(args.identity),
                         "multipliers": multipliers}
    apply_layer_multipliers(pipe, multipliers, diagnostics)

    lpips_fn = get_lpips_fn(device)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fields = [
        "object", "geometry_source", "schedule",
        "psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
        "gt_relative_texture_error",
    ]
    csv_path = args.output_dir / "per_object_metrics.csv"
    result_rows: list[dict] = []
    completed: set[tuple[str, str]] = set()
    if args.resume and csv_path.exists():
        with csv_path.open(newline="") as handle:
            existing = list(csv.DictReader(handle))
        result_rows = [{k: row[k] for k in fields} for row in existing]
        completed = {(row["object"], row["schedule"]) for row in existing}

    for row in rows:
        for schedule_name in schedule_names:
            label = canonical.get(schedule_name, schedule_name)
            if (row["object"], label) in completed:
                continue
            schedule = schedule_for_name(
                GLOBAL_NAME_FOR.get(schedule_name, schedule_name), args.low, args.high
            )
            images, _, _, _ = run_pipeline(
                pipe,
                mesh_path=row["mesh_path"],
                num_views=6,
                text="high quality",
                image=row["reference_image"],
                height=512,
                width=512,
                num_inference_steps=args.steps,
                guidance_scale=3.0,
                seed=args.seed,
                reference_conditioning_scale=1.0,
                control_conditioning_scale=1.0,
                geometry_scale_schedule=schedule,
                device=device,
            )
            metrics = object_metrics(images, row["gt_images_official_order"], lpips_fn, device)
            result_rows.append(
                {
                    "object": row["object"],
                    "geometry_source": row["geometry_source"],
                    "schedule": label,
                    **metrics,
                }
            )
            save_grid(images, args.output_dir / "images" / label / f"{row['object']}.png")
            with csv_path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(result_rows)
            finite = all(
                v == v and abs(v) != float("inf") for v in metrics.values()
            )
            print(f"[{row['object']}] {label} finite={finite} psnr={metrics['psnr']:.4f}", flush=True)

    finite_rows = sum(
        1 for row in result_rows
        if all(float(row[k]) == float(row[k]) and abs(float(row[k])) != float("inf")
               for k in fields[3:])
    )
    run_config = {
        **vars(args),
        "schedule": args.schedule,
        "canonical_schedule_labels": {k: canonical[k] for k in canonical},
        "layer_profile_sha256": sha256_file(args.layer_profile) if args.layer_profile else None,
        "layer_multipliers_by_point": multipliers,
        "identity_mode": bool(args.identity),
        "cond_encoder_diagnostics": diagnostics,
        "rows_written": len(result_rows),
        "rows_finite": finite_rows,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "global_runner_sha256": sha256_file(Path(__file__).resolve().parent / "run_experiment.py"),
    }
    (args.output_dir / "run_config.json").write_text(json.dumps(run_config, default=str, indent=2) + "\n")
    print(f"done: {len(result_rows)} rows ({finite_rows} finite) -> {csv_path}", flush=True)


if __name__ == "__main__":
    main()
