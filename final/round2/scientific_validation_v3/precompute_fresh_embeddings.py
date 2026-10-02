#!/usr/bin/env python3
"""Precompute embeddings/global_embeds.npy for the fresh render tree.

Verbatim mechanism from archive3.0/archive2.0/mvpainter_legacy/
precompute_embeddings.py (single cond view image/000.png through
vision_encoder (768) + vision_encoder_2 (1280), concat -> (1,1,2048),
float16). Only the root dir and sys.path are parameterized.
"""
import os
import sys

import numpy as np
import torch
from PIL import Image

RENDER_ROOT = "/4T/CXY/MV-Painter/data/fresh_confirm_v3_renders"
ROOT = "/4T/CXY/MV-Painter"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "MVPainter"))


def main():
    device = torch.device("cuda:0")
    print("Loading vision encoders...", flush=True)
    from mvpainter.mvpainter_pipeline import MVPainter_Pipeline

    pipeline = MVPainter_Pipeline.from_pretrained(
        os.path.join(ROOT, "checkpoints/hf_repo"), torch_dtype=torch.float16)
    vision_encoder = pipeline.vision_encoder.to(device)
    vision_encoder_2 = pipeline.vision_encoder_2.to(device)
    vision_processor = pipeline.vision_processor
    del pipeline
    torch.cuda.empty_cache()

    uids = sorted(os.listdir(RENDER_ROOT))
    print(f"Processing {len(uids)} objects...", flush=True)
    done = skipped = failed = 0
    for i, uid in enumerate(uids):
        obj_dir = os.path.join(RENDER_ROOT, uid)
        image_dir = os.path.join(obj_dir, "image")
        embed_dir = os.path.join(obj_dir, "embeddings")
        if os.path.exists(os.path.join(embed_dir, "global_embeds.npy")):
            skipped += 1
            continue
        img_path = os.path.join(image_dir, "000.png")
        if not os.path.isdir(image_dir) or not os.path.exists(img_path):
            failed += 1
            continue
        os.makedirs(embed_dir, exist_ok=True)
        try:
            img = Image.open(img_path).convert("RGB")
            pixel = vision_processor(images=[img], return_tensors="pt").pixel_values.to(
                device=device, dtype=torch.float16)
            with torch.no_grad():
                e1 = vision_encoder(pixel, output_hidden_states=False).image_embeds.unsqueeze(-2)
                e2 = vision_encoder_2(pixel, output_hidden_states=False).image_embeds.unsqueeze(-2)
                g = torch.concat([e1, e2], dim=-1)
            np.save(os.path.join(embed_dir, "global_embeds.npy"), g.cpu().numpy())
            done += 1
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"error {uid}: {e}", flush=True)
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(uids)} done={done} skip={skipped} fail={failed}", flush=True)
    print(f"finished: computed={done} skipped={skipped} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
