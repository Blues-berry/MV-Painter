#!/usr/bin/env python3
"""Build a local SD2.1-depth-compatible base for MVDiffusion.

The public Hugging Face ``stabilityai/stable-diffusion-2-depth`` repository
may require access approval in a deployment environment.  MVDiffusion's depth
branch only needs the SD2.1 component layout plus a five-channel UNet input;
this utility makes a clearly marked local compatibility base from the already
staged SD2.1 base by zero-initialising the additional depth channel.  If the
official MVDiffusion checkpoint contains the full base state, loading it later
replaces this bootstrap tensor.  Results made with this fallback must retain
the fallback provenance and are not native SD2-depth benchmark numbers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from safetensors.torch import load_file, save_file


def link_or_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    target.symlink_to(source.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--output-model", type=Path, required=True)
    args = parser.parse_args()

    base = args.base_model.resolve()
    out = args.output_model
    if not (base / "unet/diffusion_pytorch_model.safetensors").is_file():
        raise FileNotFoundError(base / "unet/diffusion_pytorch_model.safetensors")
    out.mkdir(parents=True, exist_ok=True)

    for component in ("feature_extractor", "scheduler", "text_encoder", "tokenizer", "vae"):
        source = base / component
        if source.exists():
            link_or_copy(source, out / component)

    base_index = json.loads((base / "model_index.json").read_text())
    base_index["mvdiffusion_compatibility"] = {
        "source_base": str(base),
        "unet_input_channels": 5,
        "depth_channel_initialization": "zeros",
        "native_official_depth_base": False,
    }
    (out / "model_index.json").write_text(json.dumps(base_index, indent=2) + "\n")

    unet_config = json.loads((base / "unet/config.json").read_text())
    unet_config["in_channels"] = 5
    (out / "unet").mkdir(parents=True, exist_ok=True)
    (out / "unet/config.json").write_text(json.dumps(unet_config, indent=2) + "\n")

    state = load_file(str(base / "unet/diffusion_pytorch_model.safetensors"), device="cpu")
    weight = state["conv_in.weight"]
    if weight.shape[1] == 5:
        expanded = state
    elif weight.shape[1] == 4:
        expanded = dict(state)
        expanded["conv_in.weight"] = torch.cat(
            [weight, torch.zeros(weight.shape[0], 1, *weight.shape[2:], dtype=weight.dtype)],
            dim=1,
        )
    else:
        raise ValueError(f"unexpected conv_in input channels: {weight.shape}")
    save_file(expanded, str(out / "unet/diffusion_pytorch_model.safetensors"))
    print(
        json.dumps(
            {
                "output_model": str(out.resolve()),
                "source_base": str(base),
                "conv_in_shape": list(expanded["conv_in.weight"].shape),
                "native_official_depth_base": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
