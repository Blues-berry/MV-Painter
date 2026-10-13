#!/usr/bin/env python3
"""Run the official MVDiffusion depth generator on an exported scene set.

This runner calls the upstream ``DepthGenerator`` directly so it does not
depend on the old PyTorch-Lightning CLI.  It keeps the official model and
checkpoint untouched, writes one 12-view result per object, and records the
seed/configuration needed for a later metric pass.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "final/round2/mvdiffusion/upstream"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(UPSTREAM))

from geotex.runtime import require_cuda  # noqa: E402
from src.dataset.Scannet import Scannetdataset  # noqa: E402
from src.lightning_depth import DepthGenerator  # noqa: E402


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_config(path: Path, data_root: Path, steps: int) -> dict:
    config = yaml.safe_load(path.read_text())
    config["dataset"]["image_dir"] = str(data_root)
    config["model"]["diff_timestep"] = int(steps)
    config.setdefault("train", {}).setdefault("max_epochs", 1)
    return config


def migrate_checkpoint_state(state: dict[str, torch.Tensor]) -> tuple[dict[str, torch.Tensor], dict]:
    """Adapt the official old-diffusers names to the installed diffusers API.

    The released checkpoint was saved with the legacy VAE attention module
    names.  Current diffusers uses the equivalent ``to_*`` names and no longer
    registers the text-encoder position-id buffer.  Keep this migration
    explicit and auditable, then load the resulting state dict strictly.
    """
    migrated = dict(state)
    renamed = {}
    dropped = []
    attention_prefixes = (
        "vae.encoder.mid_block.attentions.",
        "vae.decoder.mid_block.attentions.",
    )
    attention_names = {
        ".query.": ".to_q.",
        ".key.": ".to_k.",
        ".value.": ".to_v.",
        ".proj_attn.": ".to_out.0.",
    }
    for key in list(state):
        replacement = None
        if key.startswith(attention_prefixes):
            for old_name, new_name in attention_names.items():
                if old_name in key:
                    replacement = key.replace(old_name, new_name)
                    break
        if replacement is not None:
            if replacement in migrated:
                raise RuntimeError(f"checkpoint migration collision: {key} -> {replacement}")
            migrated[replacement] = migrated.pop(key)
            renamed[key] = replacement

    position_ids_key = "text_encoder.text_model.embeddings.position_ids"
    if position_ids_key in migrated:
        migrated.pop(position_ids_key)
        dropped.append(position_ids_key)
    return migrated, {"renamed": renamed, "dropped": dropped}


def load_checkpoint(model: DepthGenerator, checkpoint: Path) -> dict:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    state = payload.get("state_dict", payload)
    migrated, migration = migrate_checkpoint_state(state)
    model.load_state_dict(migrated, strict=True)
    return {
        "mode": "strict_after_explicit_key_migration",
        "source_key_count": len(state),
        "loaded_key_count": len(migrated),
        "renamed_key_count": len(migration["renamed"]),
        "dropped_key_count": len(migration["dropped"]),
        "renamed_keys": migration["renamed"],
        "dropped_keys": migration["dropped"],
    }


def base_provenance(model_id: str) -> dict:
    index_path = Path(model_id) / "model_index.json"
    if not index_path.is_file():
        return {"model_id": model_id, "native_official_depth_base": None}
    payload = json.loads(index_path.read_text())
    provenance = payload.get("mvdiffusion_compatibility")
    return {
        "model_id": model_id,
        "native_official_depth_base": (
            True if provenance is None else bool(provenance.get("native_official_depth_base", False))
        ),
        "compatibility": provenance,
    }


def move_batch(batch: dict, device: torch.device) -> dict:
    return {
        key: value.to(device) if torch.is_tensor(value) else value
        for key, value in batch.items()
    }


def batch_scene_id(batch: dict) -> str:
    paths = batch["image_paths"]
    first = paths[0]
    if isinstance(first, (tuple, list)):
        first = first[0]
    return Path(first).parent.parent.name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=UPSTREAM / "configs/depth_generation_fix_frames.yaml")
    parser.add_argument(
        "--model-id",
        default=None,
        help="local diffusers base; omit to use the official model_id in the config",
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--object", dest="object_ids", action="append", default=None)
    parser.add_argument("--max-objects", type=int, default=None)
    args = parser.parse_args()

    device = require_cuda(args.device, "MVDiffusion deployment")
    if not args.checkpoint.is_file():
        raise FileNotFoundError(args.checkpoint)
    data_payload = json.loads(args.data_manifest.read_text())
    objects = data_payload["objects"]
    by_id = {row["object"]: row for row in objects}
    selected = set(args.object_ids) if args.object_ids else None
    unknown = (selected or set()) - set(by_id)
    if unknown:
        raise ValueError(f"unknown exported objects: {sorted(unknown)}")
    if selected:
        objects = [row for row in objects if row["object"] in selected]
    if args.max_objects is not None:
        objects = objects[: args.max_objects]
    if not objects:
        raise ValueError("no exported objects selected")

    config = load_config(args.config, args.data_root, args.steps)
    if args.model_id is not None:
        model_path = Path(args.model_id)
        config["model"]["model_id"] = (
            str(model_path.resolve()) if model_path.exists() else args.model_id
        )
    config["dataset"]["num_views"] = len(data_payload["view_ids"])
    set_seed(args.seed)
    dataset = Scannetdataset(config["dataset"], mode="val")
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=1, shuffle=False, num_workers=0, drop_last=False
    )
    model = DepthGenerator(config)
    checkpoint_load = load_checkpoint(model, args.checkpoint)
    model.to(device).eval()

    requested = {row["object"] for row in objects}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    completed = []
    with torch.inference_mode():
        for batch_index, batch in enumerate(loader):
            scene_id = batch_scene_id(batch)
            if scene_id not in requested:
                continue
            set_seed(args.seed + batch_index)
            batch = move_batch(batch, device)
            images_pred = model.inference_gen(batch)
            images_pred = np.asarray(images_pred)
            if images_pred.ndim != 5 or images_pred.shape[1] != len(data_payload["view_ids"]):
                raise RuntimeError(f"unexpected prediction shape for {scene_id}: {images_pred.shape}")
            scene_out = args.output_dir / scene_id
            scene_out.mkdir(parents=True, exist_ok=True)
            for local_id, source_id in enumerate(data_payload["view_ids"]):
                Image.fromarray(images_pred[0, local_id]).save(
                    scene_out / f"view_{local_id:03d}_source_{source_id:03d}.png"
                )
            (scene_out / "prediction_shape.json").write_text(
                json.dumps({"shape": list(images_pred.shape)}, indent=2) + "\n"
            )
            completed.append(scene_id)
            print(json.dumps({"object": scene_id, "completed": len(completed)}), flush=True)

    missing = sorted(requested - set(completed))
    if missing:
        raise RuntimeError(f"exported objects were not produced: {missing}")
    (args.output_dir / "run_config.json").write_text(
        json.dumps(
            {
                "protocol": "mvdiffusion-depth-mvpainter-interop-v1",
                "data_manifest": str(args.data_manifest.resolve()),
                "checkpoint": str(args.checkpoint.resolve()),
                "checkpoint_load": checkpoint_load,
                "config": config,
                "base_provenance": base_provenance(config["model"]["model_id"]),
                "device": str(device),
                "steps": args.steps,
                "seed": args.seed,
                "objects": completed,
            },
            indent=2,
            default=str,
        )
        + "\n"
    )
    print(json.dumps({"status": "complete", "object_count": len(completed)}, indent=2))


if __name__ == "__main__":
    main()
