#!/usr/bin/env python3
"""Download frozen Fresh C candidates from the pinned Objaverse revision."""
from __future__ import annotations

import concurrent.futures
import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import requests

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
REVISION = "21e4e142159e2153706c23a3a02e55cec5591cea"
QUEUE = DATA / "candidate_screen_queue.csv"
ASSET_DIR = DATA / "assets"
MAX_WORKERS = 16


def download_one(row: dict[str, str]) -> dict[str, str | int]:
    uid = row["uid"]
    relative = row["source_path"]
    dest = ASSET_DIR / f"{uid}.glb"
    url = f"https://huggingface.co/datasets/allenai/objaverse/resolve/{REVISION}/{relative}"
    if dest.is_file() and dest.stat().st_size > 512:
        with dest.open("rb") as f:
            magic = f.read(4)
        if magic == b"glTF":
            return {"uid": uid, "status": "cached_valid", "path": str(dest),
                    "bytes": dest.stat().st_size, "sha256": sha256_file(dest), "error": ""}
        dest.unlink()

    last_error = ""
    for attempt in range(5):
        tmp = dest.with_suffix(".glb.tmp")
        digest = hashlib.sha256()
        written = 0
        try:
            with requests.get(url, stream=True, timeout=(10, 180)) as response:
                response.raise_for_status()
                with tmp.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        f.write(chunk)
                        digest.update(chunk)
                        written += len(chunk)
            with tmp.open("rb") as f:
                magic = f.read(4)
            if magic != b"glTF" or written <= 512:
                raise RuntimeError(f"unexpected GLB payload: magic={magic!r}, bytes={written}")
            tmp.replace(dest)
            return {"uid": uid, "status": "downloaded", "path": str(dest),
                    "bytes": written, "sha256": digest.hexdigest(), "error": ""}
        except Exception as exc:  # bounded retry; preserve failed objects in the log
            last_error = f"{type(exc).__name__}: {str(exc)[:220]}"
            tmp.unlink(missing_ok=True)
            if attempt < 4:
                time.sleep(2 ** attempt)
    return {"uid": uid, "status": "download_failed", "path": str(dest),
            "bytes": 0, "sha256": "", "error": last_error}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-rank", type=int, default=1)
    parser.add_argument("--count", type=int, default=600)
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()
    if args.start_rank < 1 or args.count < 1 or args.start_rank + args.count - 1 > 1000:
        parser.error("candidate rank range must be within the frozen 1..1000 queue")
    DATA.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with QUEUE.open(newline="") as f:
        candidates = list(csv.DictReader(f))
    lock = json.loads((DATA / "CANDIDATE_QUEUE_LOCK.json").read_text())
    if lock["dataset_revision"] != REVISION or lock["candidate_queue_sha256"] != sha256_file(QUEUE):
        raise RuntimeError("candidate queue/revision differs from the pre-output lock")
    selected = [r for r in candidates if args.start_rank <= int(r["queue_rank"]) < args.start_rank + args.count]
    if len(selected) != args.count:
        raise RuntimeError(f"rank interval produced {len(selected)} rows, expected {args.count}")
    expected_role = "screen" if args.start_rank + args.count - 1 <= 600 else "reserve"
    if any(r["queue_role"] != expected_role for r in selected):
        raise RuntimeError(f"rank interval crosses or violates the frozen {expected_role} block")
    output_path = DATA / "asset_download_manifest.csv"
    status_path = DATA / "ASSET_DOWNLOAD_STATUS.json"
    by_uid: dict[str, dict[str, str | int]] = {}
    previous_batches = []
    if output_path.is_file():
        if not args.append:
            raise RuntimeError("download manifest exists; use --append for the frozen reserve block")
        if status_path.is_file():
            previous_status = json.loads(status_path.read_text())
            previous_batches = previous_status.get("batches", [])
        with output_path.open(newline="") as f:
            for row in csv.DictReader(f):
                by_uid[row["uid"]] = row
    elif args.append:
        raise RuntimeError("cannot append reserve before the first download manifest exists")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(download_one, row): row["uid"] for row in selected}
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            by_uid[str(result["uid"])] = result
            if index % 25 == 0 or index == len(selected):
                ok = sum(r["status"] in {"downloaded", "cached_valid"} for r in by_uid.values())
                print(f"asset downloads {args.start_rank}-{args.start_rank + args.count - 1}: {index}/{len(selected)} batch complete; valid total={ok}", flush=True)
    queue_rank = {r["uid"]: r["queue_rank"] for r in candidates}
    fields = ["queue_rank", "uid", "status", "path", "bytes", "sha256", "error"]
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for uid in sorted(by_uid, key=lambda x: int(queue_rank[x])):
            writer.writerow({"queue_rank": queue_rank[uid], **by_uid[uid]})
    this_batch = {
        "rank_range": [args.start_rank, args.start_rank + args.count - 1],
        "candidate_count": len(selected),
        "download_script_sha256": sha256_file(Path(__file__).resolve()),
    }
    failed_count = sum(r["status"] == "download_failed" for r in by_uid.values())
    result = {
        "status": "DOWNLOADS_COMPLETE" if failed_count == 0 else "DOWNLOADS_COMPLETE_WITH_FAILURES",
        "source_revision": REVISION,
        "candidate_count": len(by_uid),
        "last_batch_rank_range": [args.start_rank, args.start_rank + args.count - 1],
        "batches": [*previous_batches, this_batch],
        "download_ok": sum(r["status"] in {"downloaded", "cached_valid"} for r in by_uid.values()),
        "download_failed": failed_count,
        "manifest": str(output_path),
        "manifest_sha256": sha256_file(output_path),
    }
    status_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
