#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) — Bit-level input identity verification (P0 gate).

Re-derives, with the CURRENT code path (same imports as
scripts/run_validation_v3_experiment.py), the six per-row input hashes for a
deterministic sample of objects spanning every shard boundary plus the
flagged duplicate-asset pair, and compares them bit-for-bit against the
hashes stored in the A2 formal ledger.

Also verifies on CPU:
  * init_latent hash is a global constant across every formal row (A2/A3/B1B2/B3/C)
  * the duplicate-asset pair renders are pixel-identical across all 17 views

Output: AUDIT_DEEP_VERIFICATION.json next to this script.
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
os.environ.setdefault("MVP_RUN_DIR", "/tmp/audit_v3_deepverify_run")
os.environ.setdefault("MVP_OBJECT_LIST", str(V3 / "fresh_confirm_300.txt"))
os.environ.setdefault("MVP_DATA_ROOT", str(ROOT / "data/fresh_confirm_v3_renders"))
os.environ.setdefault("MVP_DEVICE", "cuda:0")
os.environ.setdefault("MVP_NUM_THREADS", "6")

import torch  # noqa: E402
import random  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import run_validation_v3_experiment as R  # noqa: E402
from data_utils import collate_batch  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402
from omegaconf import OmegaConf  # noqa: E402

HASH_KEYS = ["cond", "target", "normal", "depth", "global_embeds", "init_latent"]


def h_tensor(t):
    return torch.sha256 if False else __import__("hashlib").sha256(
        t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def main():
    out = {"sample_objects": [], "init_latent_constant_check": None,
           "duplicate_pair_pixel_check": None}

    # ---- 0. init-latent constancy across ALL formal rows (ledger-only) -------
    vals = set()
    for camp in ("campaign_A2", "campaign_A3", "campaign_B1B2", "campaign_B3", "campaign_C"):
        for s in range(4):
            p = V3 / "formal" / camp / f"rows_shard{s}.json"
            if not p.exists():
                continue
            for r in json.loads(p.read_text()):
                vals.add(r["input_hashes"]["init_latent"])
    out["init_latent_constant_check"] = {
        "distinct_init_latent_hashes_across_16950_rows": len(vals),
        "hash": sorted(vals)[0][:16] if len(vals) == 1 else sorted(vals)[:5],
    }
    print("init_latent distinct hashes:", len(vals))

    # ---- 1. dataset (current code path, same env overrides as formal run) ----
    config = OmegaConf.load(R.CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(R.OBJECT_LIST.resolve())
    data_root = os.environ.get("MVP_DATA_ROOT")
    if data_root:
        validation.params.root_dir_list = [str(Path(data_root).resolve())]
    dataset = instantiate_from_config(validation)
    with R.OBJECT_LIST.open() as f:
        uids = [line.strip() for line in f if line.strip()]
    assert len(uids) == len(dataset), (len(uids), len(dataset))
    idx_of = {u: i for i, u in enumerate(uids)}

    device = torch.device(os.environ["MVP_DEVICE"])

    # deterministic sample: all shard-boundary neighborhoods + duplicate pair
    sample_idx = sorted({0, 1, 2, 3, 4, 5,
                         73, 74, 75, 76, 77, 78,
                         147, 148, 149, 150, 151, 152,
                         221, 222, 223, 224, 225, 226,
                         296, 297, 298, 299,
                         idx_of["0099ab6d44b742b0b62a40a7c70c29b1"],
                         idx_of["0130e5149b6f4156b9799daa5e4006da"]})
    assert len(sample_idx) >= 20

    # stored A2 hashes (condition-independent shared inputs; take a_baseline row)
    stored = {}
    for s in range(4):
        for r in json.loads((V3 / "formal/campaign_A2" / f"rows_shard{s}.json").read_text()):
            if r["condition"] == "a_baseline":
                stored[r["object_idx"]] = (r["object_uid"], r["input_hashes"])

    n_ok = n_bad = 0
    for i in sample_idx:
        object_seed = 42 + i
        random.seed(object_seed)
        np.random.seed(object_seed)
        torch.manual_seed(object_seed)
        batch = collate_batch(dataset, i, device)
        got = {
            "cond": h_tensor(batch["cond_imgs"]),
            "target": h_tensor(batch["target_imgs"]),
            "normal": h_tensor(batch["depth_imgs"]),
            "depth": h_tensor(batch["real_depth_imgs"]),
            "global_embeds": h_tensor(batch["global_embeds"]),
        }
        latent_h = latent_w = None
        try:
            img_size = config.model.params.img_size
        except Exception:
            img_size = 512
        latent_h, latent_w = img_size * 3 // 8, img_size * 2 // 8
        torch.manual_seed(42)
        init = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        got["init_latent"] = h_tensor(init)

        uid, ref = stored[i]
        mismatch = [k for k in HASH_KEYS if got[k] != ref[k]]
        rec = {"object_idx": i, "uid": uid,
               "shard_of_idx": i % 4,
               "match": not mismatch, "mismatched_keys": mismatch}
        out["sample_objects"].append(rec)
        if mismatch:
            n_bad += 1
            print(f"  idx={i} uid={uid[:12]} MISMATCH {mismatch}")
        else:
            n_ok += 1
        del batch
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out["sample_summary"] = {"n": len(sample_idx), "match": n_ok, "mismatch": n_bad}
    print(f"bit-level input verification: {n_ok}/{len(sample_idx)} match, {n_bad} mismatch")

    # ---- 2. duplicate-asset pair: all-17-view pixel comparison ---------------
    try:
        from PIL import Image
        pair = ["0099ab6d44b742b0b62a40a7c70c29b1",
                "0130e5149b6f4156b9799daa5e4006da"]
        base = ROOT / "data/fresh_confirm_v3_renders"
        views = [f"{k:02d}" for k in range(17)]
        n_view_same = 0
        detail = []
        for sub in ("image", "normal", "depth_png"):
            same = 0
            for v in views:
                a = np.array(Image.open(base / pair[0] / sub / f"{v}.png"))
                b = np.array(Image.open(base / pair[1] / sub / f"{v}.png"))
                if a.shape == b.shape and bool((a == b).all()):
                    same += 1
            detail.append({"modality": sub, "identical_views": same, "of": len(views)})
            n_view_same += same
        out["duplicate_pair_pixel_check"] = {
            "pair": pair, "detail": detail,
            "verdict": "pixel_identical_all_views_all_modalities"
            if n_view_same == 3 * 17 else "DIFFERS",
        }
        print("duplicate pair:", out["duplicate_pair_pixel_check"]["verdict"])
    except Exception as e:  # noqa: BLE001
        out["duplicate_pair_pixel_check"] = {"error": repr(e)}

    (Path(__file__).parent / "AUDIT_DEEP_VERIFICATION.json").write_text(
        json.dumps(out, indent=2))
    print("wrote AUDIT_DEEP_VERIFICATION.json")
    sys.exit(1 if (n_bad or out["init_latent_constant_check"]
                   ["distinct_init_latent_hashes_across_16950_rows"] != 1) else 0)


if __name__ == "__main__":
    main()
