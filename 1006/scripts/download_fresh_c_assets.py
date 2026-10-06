#!/usr/bin/env python3
"""Download frozen Fresh C candidates from the pinned Objaverse revision."""
from __future__ import annotations

import concurrent.futures
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
    DATA.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with QUEUE.open(newline="") as f:
        candidates = list(csv.DictReader(f))
    selected = [r for r in candidates if r["queue_role"] == "screen"]
    if len(selected) != 600:
        raise RuntimeError(f"expected exactly 600 frozen screen candidates, found {len(selected)}")
    output_path = DATA / "asset_download_manifest.csv"
    by_uid: dict[str, dict[str, str | int]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(download_one, row): row["uid"] for row in selected}
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            by_uid[str(result["uid"])] = result
            if index % 25 == 0 or index == len(selected):
                ok = sum(r["status"] in {"downloaded", "cached_valid"} for r in by_uid.values())
                print(f"asset downloads {index}/600 complete; valid={ok}", flush=True)
    queue_rank = {r["uid"]: r["queue_rank"] for r in selected}
    fields = ["queue_rank", "uid", "status", "path", "bytes", "sha256", "error"]
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for uid in sorted(by_uid, key=lambda x: int(queue_rank[x])):
            writer.writerow({"queue_rank": queue_rank[uid], **by_uid[uid]})
    result = {
        "status": "DOWNLOADS_COMPLETE_WITH_RECORDED_FAILURES",
        "source_revision": REVISION,
        "candidate_count": len(selected),
        "download_ok": sum(r["status"] in {"downloaded", "cached_valid"} for r in by_uid.values()),
        "download_failed": sum(r["status"] == "download_failed" for r in by_uid.values()),
        "manifest": str(output_path),
        "manifest_sha256": sha256_file(output_path),
    }
    (DATA / "ASSET_DOWNLOAD_STATUS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
