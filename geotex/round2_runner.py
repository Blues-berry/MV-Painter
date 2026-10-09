"""Preflight and launch the corrected main-adapter round-two evaluation.

Inference is intentionally delegated to the recovered v1 evaluator.  This
wrapper owns the protocol checks and the immutable experiment manifest, so a
future evaluator cannot silently fall back to the duplicated-top-view order.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    from .round2_protocol import protocol_manifest
    from .round2_stats import file_sha256, write_json
except ImportError:  # direct script execution
    from round2_protocol import protocol_manifest
    from round2_stats import file_sha256, write_json


def build_manifest(args) -> dict:
    checkpoint = Path(args.checkpoint)
    config = Path(args.config)
    if not checkpoint.is_file():
        raise FileNotFoundError(f"missing v1 checkpoint: {checkpoint}")
    if not config.is_file():
        raise FileNotFoundError(f"missing v1 evaluation config: {config}")
    config_text = config.read_text()
    if "target_view_mode: unique6" not in config_text.replace("\"", "").replace("'", ""):
        raise ValueError(
            "refusing to run: the evaluation config must explicitly contain "
            "target_view_mode: unique6; legacy duplicate-top configs are audit-only"
        )
    manifest = protocol_manifest(resolution=args.resolution)
    manifest.update({
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": file_sha256(checkpoint),
        "config": str(config.resolve()),
        "config_sha256": file_sha256(config),
        "seed": args.seed,
        "steps": args.steps,
        "objects": args.objects,
        "scales": args.scales,
        "output_root": str(Path(args.output_root).resolve()),
        "status": "preflight_only" if args.dry_run else "ready_to_launch",
    })
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--legacy-evaluator", help="path to recovered uniform-scale evaluator")
    parser.add_argument("--schedule-evaluator", help="path to recovered schedule-aware evaluator")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--objects", type=int, default=300)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resolution", type=int, default=256)
    parser.add_argument("--scales", nargs="+", default=["1.25", "2.50", "c3", "no_adapter"])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = build_manifest(args)
    write_json(args.manifest, manifest)
    print(json.dumps(manifest, indent=2))
    if args.dry_run:
        return
    if not args.legacy_evaluator:
        raise SystemExit("--legacy-evaluator is required for a non-dry run")
    evaluator = Path(args.legacy_evaluator)
    if not evaluator.is_file():
        raise FileNotFoundError(evaluator)
    for scale in args.scales:
        if scale in {"c3", "no_adapter"}:
            if not args.schedule_evaluator:
                raise SystemExit("--schedule-evaluator is required for C3 and no_adapter")
            evaluator = Path(args.schedule_evaluator)
            if not evaluator.is_file():
                raise FileNotFoundError(evaluator)
            output = Path(args.output_root) / f"unique6_{scale}"
            command = [
                sys.executable, str(evaluator), "--config", args.config,
                "--checkpoint", args.checkpoint, "--schedule", scale,
                "--output_dir", str(output), "--num_objects", str(args.objects),
                "--device", args.device, "--steps", str(args.steps), "--seed", str(args.seed),
            ]
            print("Launching:", " ".join(command))
            subprocess.run(command, check=True)
            continue
        if not args.legacy_evaluator:
            raise SystemExit("--legacy-evaluator is required for uniform scales")
        evaluator = Path(args.legacy_evaluator)
        if not evaluator.is_file():
            raise FileNotFoundError(evaluator)
        output = Path(args.output_root) / f"unique6_s{scale.replace('.', '')}"
        command = [
            sys.executable, str(evaluator), "--config", args.config,
            "--checkpoint", args.checkpoint, "--scale", scale,
            "--output_dir", str(output), "--num_objects", str(args.objects),
            "--device", args.device, "--steps", str(args.steps), "--seed", str(args.seed),
        ]
        print("Launching:", " ".join(command))
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
