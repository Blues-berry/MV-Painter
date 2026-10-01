#!/usr/bin/env python3
"""Post-load state equivalence between the compat base and the native mirror.

Constructs DepthGenerator twice (model_id = sd21_depth_compat vs
sd2_depth_native_mirror), loads the identical depth_gen_new.pth with the same
explicit migration and strict=True, and compares the complete loaded state:
parameter names, shapes, dtypes, per-tensor SHA-256, max/mean abs difference.

CPU-only; writes MVDIFFUSION_POSTLOAD_EQUIVALENCE.md + JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "final/round2/mvdiffusion/upstream"))
sys.path.insert(0, str(ROOT / "scripts"))

import yaml  # noqa: E402

import run_mvdiffusion_depth as base  # noqa: E402
from src.lightning_depth import DepthGenerator  # noqa: E402


def tensor_sha(t: torch.Tensor) -> str:
    return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def build_state(model_id: Path, checkpoint: Path, config_path: Path) -> dict:
    config = yaml.safe_load(config_path.read_text())
    config["model"]["model_id"] = str(model_id.resolve())
    config["dataset"]["image_dir"] = "/4T/tmp/unused_for_state_load"
    config["model"]["diff_timestep"] = 50
    config.setdefault("train", {}).setdefault("max_epochs", 1)
    model = DepthGenerator(config)
    load_info = base.load_checkpoint(model, checkpoint)
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    return state, load_info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compat", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "final/round2/mvdiffusion/upstream/configs/depth_generation_fix_frames.yaml")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "final/round2/mvdiffusion/results/phase_c_logs")
    args = parser.parse_args()

    state_a, load_a = build_state(args.compat, args.checkpoint, args.config)
    state_b, load_b = build_state(args.mirror, args.checkpoint, args.config)

    keys_a, keys_b = set(state_a), set(state_b)
    only_a = sorted(keys_a - keys_b)
    only_b = sorted(keys_b - keys_a)
    shared = sorted(keys_a & keys_b)

    shape_mismatch, dtype_mismatch, value_diff = [], [], []
    identical = 0
    for key in shared:
        ta, tb = state_a[key], state_b[key]
        if ta.shape != tb.shape:
            shape_mismatch.append(key)
            continue
        if ta.dtype != tb.dtype:
            dtype_mismatch.append(key)
        if ta.dtype.is_floating_point:
            diff = (ta.float() - tb.float()).abs()
            max_diff = float(diff.max()) if diff.numel() else 0.0
            mean_diff = float(diff.mean()) if diff.numel() else 0.0
        else:
            max_diff = 0.0 if torch.equal(ta, tb) else float("inf")
            mean_diff = max_diff
        if max_diff == 0.0 and tensor_sha(ta) == tensor_sha(tb):
            identical += 1
        else:
            value_diff.append({"key": key, "max_abs": max_diff, "mean_abs": mean_diff,
                               "sha_a": tensor_sha(ta), "sha_b": tensor_sha(tb)})

    equivalent = not only_a and not only_b and not shape_mismatch and not value_diff
    result = {
        "audit": "MVDIFFUSION_POSTLOAD_EQUIVALENCE",
        "verdict": "PASS" if equivalent else "FAIL",
        "checkpoint_load_compat": load_a,
        "checkpoint_load_mirror": load_b,
        "total_keys": {"compat": len(keys_a), "mirror": len(keys_b), "shared": len(shared)},
        "only_in_compat": only_a[:20],
        "only_in_mirror": only_b[:20],
        "shape_mismatch": shape_mismatch[:20],
        "dtype_mismatch": dtype_mismatch[:20],
        "bitwise_identical_tensors": identical,
        "value_diffs": value_diff[:20],
        "n_value_diffs": len(value_diff),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "postload_equivalence.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# MVDiffusion Post-load State Equivalence (compat vs native mirror)",
        "",
        f"**POSTLOAD_STATE_EQUIVALENT = {'YES' if equivalent else 'NO'}**",
        "",
        f"- shared keys: {len(shared)}; identical: {identical}; value diffs: {len(value_diff)}",
        f"- only in compat: {len(only_a)}; only in mirror: {len(only_b)}; "
        f"shape mismatch: {len(shape_mismatch)}; dtype mismatch: {len(dtype_mismatch)}",
        "",
        "Both models loaded the identical `depth_gen_new.pth` with the same explicit",
        "key migration and `strict=True`. This compares loaded weights only;",
        "inference equivalence is section 28 of the task (single-object output run).",
    ]
    (args.output_dir / "MVDIFFUSION_POSTLOAD_EQUIVALENCE.md").write_text("\n".join(lines) + "\n")
    print(f"POSTLOAD_STATE_EQUIVALENT = {'YES' if equivalent else 'NO'}")
    print(f"shared={len(shared)} identical={identical} diffs={len(value_diff)} "
          f"only_a={len(only_a)} only_b={len(only_b)} shape={len(shape_mismatch)}")


if __name__ == "__main__":
    main()
