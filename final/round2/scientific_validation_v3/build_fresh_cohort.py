#!/usr/bin/env python3
"""Phase III fresh cohort pipeline.

Subcommands:
  glbcheck  — trimesh load validation over fresh disjoint candidates
  render    — parallel Blender rendering of the GLB-valid pool (17 views each)
  depth     — EXR -> 16-bit PNG depth conversion
  audit     — completeness + coverage audit, deterministic selection, freeze

All artifacts land in final/round2/scientific_validation_v3/; renders land in
data/fresh_confirm_v3_renders/<uid>/ (format-identical to rendered_full).
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

ROOT = "/4T/CXY/MV-Painter"
V3 = os.path.join(ROOT, "final/round2/scientific_validation_v3")
RENDER_DIR = os.path.join(ROOT, "data/fresh_confirm_v3_renders")
BLENDER = os.path.join(ROOT, "blender-4.2.4-linux-x64/blender")
BLENDER_SCRIPT = os.path.join(ROOT, "archive3.0/archive2.0/root_legacy/data_process/blender_script.py")
HDRI = "/home/ubuntu/ssd_work/projects/spar3d/demo_files/hdri/studio_small_08_1k.hdr"
SEED = 20261002
TARGET_VIEWS = [0, 15, 12, 16, 13, 14]
CHECK_VIEWS = sorted(set([0, 14] + TARGET_VIEWS))
COVERAGE_LO, COVERAGE_HI = 0.02, 0.95
N_TARGET = 300

CANDIDATES = os.path.join(V3, "fresh_disjoint_candidates.txt")
GLB_OK = os.path.join(V3, "glb_load_valid.txt")
RENDER_OK = os.path.join(V3, "render_success.txt")
AUDIT_JSON = os.path.join(V3, "technical_validity_audit.json")


def glb_dir(uid):
    return os.path.join(RENDER_DIR, uid)


def load_list(path):
    with open(path) as f:
        return [l.strip() for l in f if l.strip()]


def find_glb(uid):
    base = "/home/ubuntu/.objaverse/hf-objaverse-v1/glbs"
    for shard in os.listdir(base):
        p = os.path.join(base, shard, uid + ".glb")
        if os.path.exists(p):
            return p
    return None


# ---------------------------------------------------------------- glbcheck
def _check_one(uid):
    import trimesh

    path = find_glb(uid)
    if path is None:
        return uid, "missing_glb"
    try:
        scene = trimesh.load(path, force="scene", process=False)
        geom = list(scene.geometry.values()) if hasattr(scene, "geometry") else []
        if not geom:
            return uid, "empty_geometry"
        n_faces = 0
        lo = np.array([np.inf] * 3)
        hi = -lo.copy()
        for g in geom:
            if hasattr(g, "faces") and len(g.faces):
                n_faces += len(g.faces)
                lo = np.minimum(lo, g.bounds[0])
                hi = np.maximum(hi, g.bounds[1])
        if n_faces == 0 or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)):
            return uid, "invalid_geometry"
        return uid, f"ok:{n_faces}"
    except Exception as e:  # noqa: BLE001
        return uid, f"error:{type(e).__name__}:{str(e)[:120]}"


def cmd_glbcheck(args):
    cands = load_list(CANDIDATES)
    print(f"Checking {len(cands)} candidate GLBs ...")
    ok, bad = [], {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_check_one, u): u for u in cands}
        for i, fut in enumerate(as_completed(futs), 1):
            uid, status = fut.result()
            if status.startswith("ok"):
                ok.append(uid)
            else:
                bad[uid] = status
            if i % 50 == 0:
                print(f"  {i}/{len(cands)} checked, {len(ok)} ok, {len(bad)} bad")
    ok.sort()
    with open(GLB_OK, "w") as f:
        f.write("\n".join(ok) + "\n")
    with open(os.path.join(V3, "glb_load_failures.json"), "w") as f:
        json.dump(bad, f, indent=2)
    print(f"GLB-valid: {len(ok)} / {len(cands)} (failures: {len(bad)})")


# ---------------------------------------------------------------- render
def _render_one(uid):
    out = glb_dir(uid)
    done = os.path.exists(os.path.join(out, "image", "016.png")) and \
        os.path.exists(os.path.join(out, "camera", "016.npy")) and \
        os.path.exists(os.path.join(out, "meta.npy"))
    if done:
        return uid, "skip"
    if os.path.exists(out):
        import shutil

        shutil.rmtree(out)
    path = find_glb(uid)
    if path is None:
        return uid, "missing_glb"
    cmd = [
        BLENDER, "-noaudio", "--background", "-Y", "-t", "4",
        "--python", BLENDER_SCRIPT, "--",
        "--object_path", path,
        "--object_uid", uid,
        "--output_dir", RENDER_DIR,
        "--hdri_path", HDRI,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if r.returncode == 0:
            return uid, "success"
        return uid, f"error:{r.stderr[-200:] if r.stderr else 'rc=%d' % r.returncode}"
    except subprocess.TimeoutExpired:
        return uid, "timeout"
    except Exception as e:  # noqa: BLE001
        return uid, f"exception:{str(e)[:150]}"


def cmd_render(args):
    uids = load_list(GLB_OK)
    print(f"Rendering {len(uids)} objects -> {RENDER_DIR}")
    os.makedirs(RENDER_DIR, exist_ok=True)
    results = {}
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_render_one, u): u for u in uids}
        for fut in as_completed(futs):
            uid, status = fut.result()
            results[uid] = status
            done += 1
            if done % 10 == 0 or done == len(uids):
                n_ok = sum(1 for s in results.values() if s in ("success", "skip"))
                print(f"  {done}/{len(uids)} done, {n_ok} ok")
    with open(os.path.join(V3, "render_log.json"), "w") as f:
        json.dump(results, f, indent=2)
    n_ok = sum(1 for s in results.values() if s in ("success", "skip"))
    print(f"Rendered ok: {n_ok}/{len(uids)}")


# ---------------------------------------------------------------- depth
def _convert_depth_dir(uid):
    os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
    import OpenEXR
    import Imath
    from PIL import Image

    ddir = os.path.join(glb_dir(uid), "depth")
    pdir = os.path.join(glb_dir(uid), "depth_png")
    if not os.path.isdir(ddir):
        return uid, "no_depth_dir"
    os.makedirs(pdir, exist_ok=True)
    for fn in sorted(os.listdir(ddir)):
        if not fn.endswith(".exr"):
            continue
        out_png = os.path.join(pdir, fn[:-4] + ".png")
        if os.path.exists(out_png):
            continue
        try:
            exr = OpenEXR.InputFile(os.path.join(ddir, fn))
            header = exr.header()
            size = (header["displayWindow"].max.x + 1, header["displayWindow"].max.y + 1)
            # matches archive3.0/.../batch_depth_convert.py: channel 'V', scale 1.0
            ch = exr.channel("V", Imath.PixelType(Imath.PixelType.FLOAT))
            arr = np.frombuffer(ch, dtype=np.float32).reshape((size[1], size[0])).copy()
            invalid = arr == 1.0
            arr /= 1.0
            u16 = (arr * 65535).astype(np.uint16)
            u16[invalid] = 65535
            Image.fromarray(u16).save(out_png)
        except Exception as e:  # noqa: BLE001
            return uid, f"error:{type(e).__name__}:{str(e)[:120]}"
    return uid, "ok"


def cmd_depth(args):
    uids = load_list(GLB_OK)
    print(f"Converting depth EXR->PNG for {len(uids)} objects ...")
    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_convert_depth_dir, u): u for u in uids}
        for i, fut in enumerate(as_completed(futs), 1):
            uid, status = fut.result()
            results[uid] = status
            if i % 100 == 0:
                print(f"  {i}/{len(uids)}")
    with open(os.path.join(V3, "depth_convert_log.json"), "w") as f:
        json.dump(results, f, indent=2)
    n_ok = sum(1 for s in results.values() if s == "ok")
    print(f"Depth ok: {n_ok}/{len(uids)}")


# ---------------------------------------------------------------- audit
def cmd_audit(args):
    from PIL import Image

    uids = load_list(GLB_OK)
    rows, valid = [], []
    for uid in uids:
        d = glb_dir(uid)
        row = {"uid": uid, "reason": ""}
        # completeness over all 17 views
        missing = []
        for v in range(17):
            tag = f"{v:03d}"
            for sub in ("image", "normal", "camera", "depth_png"):
                ext = "npy" if sub == "camera" else "png"
                p = os.path.join(d, sub, f"{tag}.{ext}")
                if not os.path.exists(p):
                    missing.append(f"{sub}/{tag}")
        if not os.path.exists(os.path.join(d, "meta.npy")):
            missing.append("meta.npy")
        if missing:
            row["reason"] = "incomplete:" + ",".join(missing[:5])
            rows.append(row)
            continue
        # coverage over protocol views
        cov = {}
        bad_cov = []
        for v in CHECK_VIEWS:
            img = Image.open(os.path.join(d, "image", f"{v:03d}.png"))
            alpha = np.asarray(img.convert("RGBA"))[:, :, 3]
            c = float((alpha > 0).mean())
            cov[f"{v:03d}"] = round(c, 5)
            if c < COVERAGE_LO or c > COVERAGE_HI:
                bad_cov.append(f"{v:03d}:{c:.4f}")
        row["coverage"] = cov
        if bad_cov:
            row["reason"] = "coverage:" + ",".join(bad_cov[:5])
            rows.append(row)
            continue
        row["reason"] = "ok"
        valid.append(uid)
        rows.append(row)

    valid.sort()
    rng = np.random.default_rng(SEED)
    n = min(N_TARGET, len(valid))
    selected = sorted(rng.choice(valid, size=n, replace=False).tolist())

    with open(AUDIT_JSON, "w") as f:
        json.dump(
            {
                "seed": SEED,
                "pool_size": len(uids),
                "complete_and_inbounds": len(valid),
                "selected_n": n,
                "target": N_TARGET,
                "coverage_bounds": [COVERAGE_LO, COVERAGE_HI],
                "check_views": CHECK_VIEWS,
                "selected": selected,
                "rows": rows,
            },
            f,
            indent=2,
        )

    name = f"fresh_confirm_{n}" if n == 300 else f"fresh_confirm_N{n}"
    lst = os.path.join(V3, f"{name}.txt")
    with open(lst, "w") as f:
        f.write("\n".join(selected) + "\n")

    # manifest csv
    cov_by_uid = {r["uid"]: r.get("coverage", {}) for r in rows}
    man = os.path.join(V3, f"{name}_manifest.csv")
    with open(man, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uid", "glb_path", "render_dir"] + [f"coverage_{v:03d}" for v in CHECK_VIEWS])
        for uid in selected:
            cov = cov_by_uid.get(uid, {})
            w.writerow([uid, find_glb(uid) or "", glb_dir(uid)] + [cov.get(f"{v:03d}", "") for v in CHECK_VIEWS])

    # sha256 sums for frozen artifacts + GLBs
    sums = os.path.join(V3, "SHA256SUMS.txt")
    with open(sums, "w") as f:
        for p in sorted([lst, man, AUDIT_JSON, os.path.join(V3, "uid_disjointness_audit.json")]):
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
            f.write(f"{h}  {os.path.relpath(p, ROOT)}\n")
        for uid in selected:
            p = find_glb(uid)
            if p:
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                f.write(f"{h}  {os.path.relpath(p, '/home/ubuntu')}\n")

    print(f"Valid pool: {len(valid)}; selected {n} -> {lst}")
    print(f"Manifest: {man}")
    print(f"SHA256SUMS: {sums}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("glbcheck", "render", "depth", "audit"):
        s = sub.add_parser(name)
        s.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    {"glbcheck": cmd_glbcheck, "render": cmd_render, "depth": cmd_depth, "audit": cmd_audit}[args.cmd](args)


if __name__ == "__main__":
    main()
