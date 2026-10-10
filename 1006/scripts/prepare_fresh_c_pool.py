#!/usr/bin/env python3
"""Technical-screen and freeze the new Fresh C object cohort before inference."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
V3 = ROOT / "final/round2/scientific_validation_v3"
ASSETS = DATA / "assets"
RENDERS = DATA / "renders"
BLENDER = ROOT / "blender-4.2.4-linux-x64/blender"
BLENDER_SCRIPT = ROOT / "archive3.0/archive2.0/root_legacy/data_process/blender_script.py"
HDRI = Path("/home/ubuntu/ssd_work/projects/spar3d/demo_files/hdri/studio_small_08_1k.hdr")
RENDER_WORKERS = 10
SEED = 20261006
TARGET_N = 300
MIN_N = 276
VIEWS = tuple(f"{i:03d}" for i in range(17))
CHECK_VIEWS = ("000", "012", "013", "014", "015", "016")


def cohort_status(valid_count: int, max_screened_rank: int) -> str:
    if valid_count < TARGET_N and max_screened_rank < 1000:
        return "RESERVE_BLOCK_REQUIRED"
    if valid_count < MIN_N:
        return "BLOCKED_TECHNICAL_COHORT_BELOW_MINIMUM"
    if valid_count < TARGET_N:
        return "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET"
    return "FROZEN_FRESH_C_300"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pixel_sha(path: Path) -> str:
    from PIL import Image

    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        h = hashlib.sha256()
        h.update(f"{rgba.width}x{rgba.height}\0".encode())
        h.update(rgba.tobytes())
        return h.hexdigest()


def image_signature(object_dir: Path) -> tuple[str, ...] | None:
    paths = [object_dir / "image" / f"{view}.png" for view in VIEWS]
    if not all(p.is_file() for p in paths):
        return None
    return tuple(pixel_sha(p) for p in paths)


def signature_sha(signature: tuple[str, ...]) -> str:
    return hashlib.sha256("\n".join(signature).encode()).hexdigest()


def read_queue() -> list[dict[str, str]]:
    path = DATA / "candidate_screen_queue.csv"
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_downloads() -> dict[str, dict[str, str]]:
    path = DATA / "asset_download_manifest.csv"
    with path.open(newline="") as f:
        return {row["uid"]: row for row in csv.DictReader(f)}


def historical_glbs() -> list[Path]:
    roots = [
        Path.home() / ".objaverse/hf-objaverse-v1/glbs",
        Path.home() / ".objaverse/smithsonian/objects",
        ROOT / "final/round2",
    ]
    found: set[Path] = set()
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*.glb"):
            if DATA in path.parents:
                continue
            found.add(path)
    return sorted(found)


def cmd_asset_audit() -> None:
    import trimesh

    queue = read_queue()
    queue_lock = json.loads((DATA / "CANDIDATE_QUEUE_LOCK.json").read_text())
    if queue_lock["candidate_queue_sha256"] != sha256_file(DATA / "candidate_screen_queue.csv"):
        raise RuntimeError("candidate queue differs from its pre-output lock")
    if queue_lock["dataset_revision"] != "21e4e142159e2153706c23a3a02e55cec5591cea":
        raise RuntimeError("candidate source revision differs from the frozen Objaverse revision")
    downloads = read_downloads()
    if not set(downloads).issubset({row["uid"] for row in queue}):
        raise RuntimeError("download manifest contains a UID outside the frozen candidate queue")
    screen = [r for r in queue if r["uid"] in downloads]
    old_hashes: dict[str, list[str]] = {}
    old_glbs = historical_glbs()
    for index, path in enumerate(old_glbs, 1):
        digest = sha256_file(path)
        old_hashes.setdefault(digest, []).append(str(path))
        if index % 250 == 0:
            print(f"historical GLB hashes {index}/{len(old_glbs)}", flush=True)

    new_rows: list[dict[str, Any]] = []
    hash_groups: dict[str, list[str]] = {}
    for row in screen:
        uid = row["uid"]
        source = ASSETS / f"{uid}.glb"
        download_row = downloads.get(uid)
        status = "download_missing"
        digest = ""
        error = ""
        face_count = 0
        geometry_count = 0
        if source.is_file() and download_row and download_row.get("status") in {"downloaded", "cached_valid"}:
            digest = sha256_file(source)
            if digest != download_row.get("sha256"):
                status = "download_hash_mismatch"
            elif digest in old_hashes:
                status = "duplicate_historical_glb_bytes"
            else:
                hash_groups.setdefault(digest, []).append(uid)
                try:
                    scene = trimesh.load(source, force="scene", process=False)
                    geometries = list(scene.geometry.values()) if hasattr(scene, "geometry") else []
                    geometry_count = len(geometries)
                    low = np.array([np.inf, np.inf, np.inf])
                    high = -low.copy()
                    for geom in geometries:
                        if hasattr(geom, "faces") and len(geom.faces):
                            face_count += len(geom.faces)
                            low = np.minimum(low, geom.bounds[0])
                            high = np.maximum(high, geom.bounds[1])
                    if face_count and np.all(np.isfinite(low)) and np.all(np.isfinite(high)):
                        status = "glb_load_valid"
                    else:
                        status = "invalid_geometry"
                except Exception as exc:  # noqa: BLE001
                    status = "glb_load_error"
                    error = f"{type(exc).__name__}: {str(exc)[:180]}"
        elif download_row:
            status = str(download_row.get("status") or "download_failed")
            error = str(download_row.get("error") or "")
        new_rows.append({
            "queue_rank": int(row["queue_rank"]), "uid": uid, "license": row["license"],
            "asset_path": str(source), "asset_bytes": source.stat().st_size if source.is_file() else 0,
            "asset_sha256": digest, "status": status, "geometry_count": geometry_count,
            "face_count": face_count, "error": error,
        })

    duplicated_new = {uid for group in hash_groups.values() if len(group) > 1 for uid in group}
    for row in new_rows:
        if row["uid"] in duplicated_new and row["status"] == "glb_load_valid":
            row["status"] = "duplicate_candidate_glb_bytes"
    report_path = DATA / "candidate_asset_technical_audit.csv"
    with report_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(new_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_rows)
    valid = [r["uid"] for r in new_rows if r["status"] == "glb_load_valid"]
    (DATA / "glb_load_valid_600.txt").write_text("".join(uid + "\n" for uid in valid))
    audit = {
        "candidate_count": len(screen), "historical_glb_count": len(old_glbs),
        "historical_unique_sha256_count": len(old_hashes),
        "historical_duplicate_source_hash_groups": sum(len(v) > 1 for v in old_hashes.values()),
        "historical_byte_duplicate_candidates": sum(r["status"] == "duplicate_historical_glb_bytes" for r in new_rows),
        "candidate_byte_duplicate_groups": [v for v in hash_groups.values() if len(v) > 1],
        "glb_load_valid_count": len(valid),
        "download_status_sha256": sha256_file(DATA / "ASSET_DOWNLOAD_STATUS.json"),
        "preparation_script_sha256": sha256_file(Path(__file__).resolve()),
        "asset_audit_sha256": sha256_file(report_path),
        "status": "TECHNICAL_SCREEN_ONLY_NO_METHOD_OUTPUTS",
    }
    (DATA / "ASSET_IDENTITY_TECHNICAL_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


def _render_one(uid: str) -> tuple[str, str]:
    out = RENDERS / uid
    done = all((out / sub / f"016.{ext}").is_file() for sub, ext in (
        ("image", "png"), ("normal", "png"), ("camera", "npy"))) and (out / "meta.npy").is_file()
    if done:
        return uid, "skip_complete"
    if out.exists():
        import shutil

        shutil.rmtree(out)
    source = ASSETS / f"{uid}.glb"
    if not source.is_file():
        return uid, "missing_asset"
    cmd = [
        str(BLENDER), "-noaudio", "--background", "-Y", "-t", "4",
        "--python", str(BLENDER_SCRIPT), "--", "--object_path", str(source),
        "--object_uid", uid, "--output_dir", str(RENDERS), "--hdri_path", str(HDRI),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            return uid, "rendered"
        return uid, f"render_error:{(result.stderr or '')[-250:]}"
    except subprocess.TimeoutExpired:
        return uid, "render_timeout"
    except Exception as exc:  # noqa: BLE001
        return uid, f"render_exception:{type(exc).__name__}:{str(exc)[:180]}"


def cmd_render() -> None:
    uids = [line.strip() for line in (DATA / "glb_load_valid_600.txt").read_text().splitlines() if line.strip()]
    record_render_stage(uids)
    RENDERS.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=RENDER_WORKERS) as pool:
        futures = {pool.submit(_render_one, uid): uid for uid in uids}
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            uid, status = future.result()
            results[uid] = status
            if index % 25 == 0 or index == len(uids):
                print(f"renders {index}/{len(uids)}; complete={sum(v in {'rendered', 'skip_complete'} for v in results.values())}", flush=True)
    path = DATA / "render_log_600.json"
    path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"render log: {path} sha256={sha256_file(path)}")


def record_render_stage(uids: list[str]) -> None:
    """Record the exact driver identity for each initial/reserve render pass."""
    identity_path = DATA / "FRESH_C_RENDER_STAGE_IDENTITY.json"
    blender_info = subprocess.run([str(BLENDER), "--version"], capture_output=True,
                                  text=True, timeout=30)
    stage = {
        "stage_index": 1,
        "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "candidate_count": len(uids),
        "uid_list_sha256": hashlib.sha256("\n".join(uids).encode()).hexdigest(),
        "source_uid_list_file_sha256": sha256_file(DATA / "glb_load_valid_600.txt"),
        "asset_audit_json_sha256": sha256_file(DATA / "ASSET_IDENTITY_TECHNICAL_AUDIT.json"),
        "download_manifest_sha256": sha256_file(DATA / "asset_download_manifest.csv"),
        "candidate_queue_sha256": sha256_file(DATA / "candidate_screen_queue.csv"),
        "preparation_script_sha256": sha256_file(Path(__file__).resolve()),
        "blender_binary_sha256": sha256_file(BLENDER),
        "blender_script_sha256": sha256_file(BLENDER_SCRIPT),
        "hdri_sha256": sha256_file(HDRI),
        "blender_version_output": (blender_info.stdout or blender_info.stderr).splitlines()[:4],
        "resolution": [512, 512], "views": 17, "renderer": "Cycles",
    }
    if identity_path.is_file():
        identity = json.loads(identity_path.read_text())
        stages = identity.setdefault("stages", [])
        key = (stage["uid_list_sha256"], stage["preparation_script_sha256"])
        existing = next((s for s in stages if (s["uid_list_sha256"], s["preparation_script_sha256"]) == key), None)
        if existing:
            return
        stage["stage_index"] = len(stages) + 1
        stages.append(stage)
    else:
        identity = {
            "protocol": "fresh_c3_input_render_stage_v1",
            "stages": [stage],
            "method_outputs_exist": False,
        }
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")


def convert_depth_one(uid: str) -> tuple[str, str]:
    os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
    try:
        import Imath
        import OpenEXR
        from PIL import Image
    except ImportError as exc:
        return uid, f"depth_dependency_error:{exc}"
    ddir = RENDERS / uid / "depth"
    pdir = RENDERS / uid / "depth_png"
    if not ddir.is_dir():
        return uid, "no_depth_directory"
    pdir.mkdir(parents=True, exist_ok=True)
    for exr_path in sorted(ddir.glob("*.exr")):
        out = pdir / f"{exr_path.stem}.png"
        if out.is_file():
            continue
        try:
            exr = OpenEXR.InputFile(str(exr_path))
            header = exr.header()
            window = header["displayWindow"]
            width, height = window.max.x + 1, window.max.y + 1
            raw = exr.channel("V", Imath.PixelType(Imath.PixelType.FLOAT))
            arr = np.frombuffer(raw, dtype=np.float32).reshape((height, width)).copy()
            invalid = arr == 1.0
            arr *= 1.0
            depth = (arr * 65535).astype(np.uint16)
            depth[invalid] = 65535
            Image.fromarray(depth).save(out)
        except Exception as exc:  # noqa: BLE001
            return uid, f"depth_error:{type(exc).__name__}:{str(exc)[:180]}"
    return uid, "depth_converted"


def cmd_depth() -> None:
    uids = [line.strip() for line in (DATA / "glb_load_valid_600.txt").read_text().splitlines() if line.strip()]
    results: dict[str, str] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(convert_depth_one, uid): uid for uid in uids}
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            uid, status = future.result()
            results[uid] = status
            if index % 100 == 0 or index == len(uids):
                print(f"depth conversion {index}/{len(uids)}", flush=True)
    path = DATA / "depth_convert_log_600.json"
    path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"depth log: {path} sha256={sha256_file(path)}")


def historical_pixel_groups() -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    roots = [ROOT / "data/train_data/rendered_full", ROOT / "data/fresh_confirm_v3_renders"]
    groups: dict[str, list[str]] = {}
    inventory: list[dict[str, Any]] = []
    for root in roots:
        if not root.is_dir():
            inventory.append({"root": str(root), "exists": False, "complete_17_view_objects": 0})
            continue
        completed = 0
        for object_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            signature = image_signature(object_dir)
            if signature is None:
                continue
            groups.setdefault(signature_sha(signature), []).append(f"{root}:{object_dir.name}")
            completed += 1
            if completed % 250 == 0:
                print(f"historical 17-view pixel signatures {root.name}: {completed}", flush=True)
        inventory.append({"root": str(root), "exists": True, "complete_17_view_objects": completed})
    return groups, inventory


def cmd_freeze() -> None:
    if (DATA / "runs/c3_confirmation/rows_shard0.json").exists() or (DATA / "runs/c3_confirmation/rows_shard1.json").exists():
        raise RuntimeError("Fresh C model-output ledger exists; cohort cannot be changed after inference")
    queue = read_queue()
    downloads = read_downloads()
    asset_rows = list(csv.DictReader((DATA / "candidate_asset_technical_audit.csv").open(newline="")))
    render_log = json.loads((DATA / "render_log_600.json").read_text())
    depth_log = json.loads((DATA / "depth_convert_log_600.json").read_text())
    render_identity_path = DATA / "FRESH_C_RENDER_STAGE_IDENTITY.json"
    if not render_identity_path.is_file():
        raise RuntimeError("render stage identity is missing; cannot freeze cohort")
    render_identity = json.loads(render_identity_path.read_text())
    asset_by_uid = {r["uid"]: r for r in asset_rows}
    queue_by_uid = {r["uid"]: r for r in queue}

    history_pixels, history_inventory = historical_pixel_groups()
    candidate_rows: list[dict[str, Any]] = []
    pixel_groups: dict[str, list[str]] = {}
    for row in asset_rows:
        uid = row["uid"]
        render_status = render_log.get(uid, "not_attempted")
        depth_status = depth_log.get(uid, "not_attempted")
        obj_dir = RENDERS / uid
        missing: list[str] = []
        if row["status"] != "glb_load_valid":
            reason = row["status"]
        elif render_status not in {"rendered", "skip_complete"}:
            reason = render_status
        else:
            for view in VIEWS:
                for folder, ext in (("image", "png"), ("normal", "png"), ("camera", "npy"), ("depth_png", "png")):
                    if not (obj_dir / folder / f"{view}.{ext}").is_file():
                        missing.append(f"{folder}/{view}.{ext}")
            if not (obj_dir / "meta.npy").is_file():
                missing.append("meta.npy")
            if missing:
                reason = "incomplete:" + ",".join(missing[:5])
            else:
                from PIL import Image

                bad_coverage = []
                coverage = {}
                for view in CHECK_VIEWS:
                    with Image.open(obj_dir / "image" / f"{view}.png") as image:
                        rgba = image.convert("RGBA")
                        alpha = np.asarray(rgba)[:, :, 3]
                    value = float((alpha > 0).mean())
                    coverage[view] = value
                    if not 0.02 <= value <= 0.95:
                        bad_coverage.append(f"{view}:{value:.5f}")
                signature = image_signature(obj_dir)
                if signature is None:
                    reason = "missing_17_view_pixel_signature"
                elif signature_sha(signature) in history_pixels:
                    reason = "duplicate_historical_decoded_17_view_signature"
                elif any(value < 0.02 or value > 0.95 for value in coverage.values()):
                    reason = "coverage_bounds:" + ",".join(bad_coverage)
                else:
                    reason = "technical_valid_candidate"
                    pixel_groups.setdefault(signature_sha(signature), []).append(uid)
        candidate_rows.append({
            "queue_rank": int(queue_by_uid[uid]["queue_rank"]), "uid": uid,
            "license": queue_by_uid[uid]["license"], "name": queue_by_uid[uid]["name"],
            "creator": queue_by_uid[uid]["creator"], "source_uri": queue_by_uid[uid]["source_uri"],
            "viewer_url": queue_by_uid[uid]["viewer_url"],
            "asset_sha256": row["asset_sha256"], "render_status": render_status,
            "depth_status": depth_status, "validity": reason,
            "pixel_signature_sha256": signature_sha(signature) if "signature" in locals() and signature is not None else "",
        })
        signature = None

    # A repeated source-render signature makes every member of that candidate
    # duplicate group ineligible; this avoids an arbitrary winner selection.
    duplicate_uids = {uid for group in pixel_groups.values() if len(group) > 1 for uid in group}
    for row in candidate_rows:
        if row["uid"] in duplicate_uids:
            row["validity"] = "duplicate_candidate_decoded_17_view_signature"
    valid_pool = sorted(r["uid"] for r in candidate_rows if r["validity"] == "technical_valid_candidate")
    max_screened_rank = max((int(r["queue_rank"]) for r in asset_rows), default=0)
    status = cohort_status(len(valid_pool), max_screened_rank)
    if status == "RESERVE_BLOCK_REQUIRED":
        # The locked protocol requires screening reserve blocks until N=300 or
        # the 1,000-candidate queue is exhausted; 276–299 is not an early stop.
        selected: list[str] = []
    elif status == "BLOCKED_TECHNICAL_COHORT_BELOW_MINIMUM":
        selected = []
    elif status == "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET":
        selected = valid_pool
    else:
        rng = np.random.default_rng(SEED)
        selected = sorted(rng.choice(valid_pool, size=TARGET_N, replace=False).tolist())

    audit_csv = DATA / "candidate_technical_validity_audit.csv"
    with audit_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(candidate_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidate_rows)
    selected_path = DATA / "fresh_c_objects.txt"
    if status == "RESERVE_BLOCK_REQUIRED":
        # Record the technical screen but do not create a cohort identity that
        # could be mistaken for the final cohort before the reserve is checked.
        selected_path.unlink(missing_ok=True)
        summary = {
            "status": status, "candidate_screen_n": len(candidate_rows),
            "technical_valid_unique_n": len(valid_pool), "selected_n": 0,
            "queue_max_rank_screened": max_screened_rank,
            "reserve_next_rank": max_screened_rank + 1,
            "target_count": TARGET_N, "minimum_count": MIN_N,
            "method_outputs_exist": False,
            "candidate_validity_counts": {},
        }
        for row in candidate_rows:
            key = row["validity"]
            summary["candidate_validity_counts"][key] = summary["candidate_validity_counts"].get(key, 0) + 1
        (DATA / "FRESH_C_COHORT_AUDIT.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
        return

    selected_path.write_text("".join(uid + "\n" for uid in selected))

    objects = []
    for index, uid in enumerate(selected):
        obj_dir = RENDERS / uid
        files = []
        for path in sorted(p for p in obj_dir.rglob("*") if p.is_file()):
            files.append({"relative_path": path.relative_to(obj_dir).as_posix(),
                          "bytes": path.stat().st_size, "sha256": sha256_file(path)})
        source = ASSETS / f"{uid}.glb"
        source_row = queue_by_uid[uid]
        signature = image_signature(obj_dir)
        objects.append({
            "object_index": index, "object_seed": 42 + index, "uid": uid,
            "asset_path": str(source), "asset_bytes": source.stat().st_size,
            "asset_sha256": sha256_file(source), "license": source_row["license"],
            "source_name": source_row["name"], "creator": source_row["creator"],
            "source_uri": source_row["source_uri"], "viewer_url": source_row["viewer_url"],
            "render_dir": str(obj_dir),
            "decoded_17_view_pixel_hashes": list(signature or ()),
            "decoded_17_view_signature_sha256": signature_sha(signature) if signature else "",
            "files": files,
        })
    blender_info = subprocess.run([str(BLENDER), "--version"], capture_output=True,
                                  text=True, timeout=30)
    selected_manifest = {
        "protocol": "Fresh C3 confirmation — revision-era follow-up",
        "status": status,
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dataset_revision": "21e4e142159e2153706c23a3a02e55cec5591cea",
        "candidate_queue_lock_sha256": sha256_file(DATA / "CANDIDATE_QUEUE_LOCK.json"),
        "candidate_queue_sha256": sha256_file(DATA / "candidate_screen_queue.csv"),
        "download_status_sha256": sha256_file(DATA / "ASSET_DOWNLOAD_STATUS.json"),
        "preparation_script_sha256": sha256_file(Path(__file__).resolve()),
        "cohort_freeze_script_sha256": sha256_file(Path(__file__).resolve()),
        "render_stage_identity_sha256": sha256_file(render_identity_path),
        "render_stages": render_identity["stages"],
        "asset_audit_script_sha256": json.loads((DATA / "ASSET_IDENTITY_TECHNICAL_AUDIT.json").read_text())["preparation_script_sha256"],
        "asset_download_manifest_sha256": sha256_file(DATA / "asset_download_manifest.csv"),
        "asset_technical_audit_sha256": sha256_file(DATA / "candidate_asset_technical_audit.csv"),
        "render_log_sha256": sha256_file(DATA / "render_log_600.json"),
        "depth_log_sha256": sha256_file(DATA / "depth_convert_log_600.json"),
        "selected_uid_list_sha256": sha256_file(selected_path),
        "technical_pool_count": len(valid_pool), "selected_count": len(selected),
        "queue_max_rank_screened": max_screened_rank,
        "target_count": TARGET_N, "minimum_count": MIN_N,
        "selection_seed": SEED,
        "selection_rule": "numpy.default_rng(20261006).choice(sorted valid pool, min(300, pool size), replace=False); if pool is 276-299 use the entire sorted pool",
        "historical_pixel_roots": history_inventory,
        "historical_pixel_signature_count": sum(len(v) for v in history_pixels.values()),
        "candidate_duplicate_pixel_groups": [v for v in pixel_groups.values() if len(v) > 1],
        "render_environment": {
            "blender_version_output": (blender_info.stdout or blender_info.stderr).splitlines()[:4],
            "blender_binary_sha256": sha256_file(BLENDER),
            "blender_script_sha256": sha256_file(BLENDER_SCRIPT),
            "hdri_sha256": sha256_file(HDRI),
            "resolution": [512, 512], "views": 17,
            "renderer": "Cycles",
        },
        "objects": objects,
    }
    manifest_path = DATA / "FRESH_C_COHORT_MANIFEST.json"
    manifest_path.write_text(json.dumps(selected_manifest, indent=2) + "\n")
    summary = {
        "status": status, "candidate_screen_n": len(candidate_rows),
        "technical_valid_unique_n": len(valid_pool), "selected_n": len(selected),
        "selected_uid_sha256": sha256_file(selected_path),
        "manifest_sha256": sha256_file(manifest_path),
        "method_outputs_exist": False,
        "candidate_validity_counts": {},
    }
    for row in candidate_rows:
        summary["candidate_validity_counts"][row["validity"]] = summary["candidate_validity_counts"].get(row["validity"], 0) + 1
    (DATA / "FRESH_C_COHORT_AUDIT.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("asset-audit", "render", "depth", "freeze"))
    args = parser.parse_args()
    if args.command == "asset-audit":
        cmd_asset_audit()
    elif args.command == "render":
        cmd_render()
    elif args.command == "depth":
        cmd_depth()
    elif args.command == "freeze":
        cmd_freeze()


if __name__ == "__main__":
    main()
