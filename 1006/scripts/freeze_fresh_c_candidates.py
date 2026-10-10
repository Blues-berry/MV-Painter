#!/usr/bin/env python3
"""Freeze a license-filtered, UID-disjoint Objaverse v1 screen queue for Fresh C."""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import requests

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
OUT = ROOT / "1006/data/fresh_c"
CACHE = OUT / "source_cache"
REVISION = "21e4e142159e2153706c23a3a02e55cec5591cea"
DATASET = "allenai/objaverse"
SEED = 20261006
SCREEN_N = 600
MAX_QUEUE_N = 1000
UID_RE = re.compile(r"[0-9a-fA-F]{32}")
ALLOWED_LICENSES = {"cc0", "by", "by-sa"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_uid(value: str) -> str:
    return re.sub(r"[-_]", "", value.strip().lower())


def fetch_pinned(relative_path: str, destination: Path) -> bytes:
    url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{relative_path}"
    last = None
    for attempt in range(5):
        try:
            response = requests.get(url, timeout=(10, 90))
            response.raise_for_status()
            data = response.content
            if not data:
                raise RuntimeError(f"empty response for {relative_path}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            tmp = destination.with_suffix(destination.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(destination)
            return data
        except Exception as exc:  # bounded retries, preserve exact failure in the final error
            last = exc
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to fetch pinned Objaverse file {relative_path}: {last}")


def load_objaverse_paths() -> tuple[dict[str, str], str]:
    path = CACHE / "object-paths.json.gz"
    data = path.read_bytes() if path.is_file() else fetch_pinned("object-paths.json.gz", path)
    digest = sha256_bytes(data)
    obj_paths = json.loads(gzip.decompress(data))
    if len(obj_paths) < 700_000:
        raise RuntimeError(f"pinned object-path index unexpectedly small: {len(obj_paths)}")
    return obj_paths, digest


def add_uid_value(value: Any, bucket: set[str]) -> None:
    if isinstance(value, str):
        normalized = norm_uid(value)
        if normalized.isalnum() and 12 <= len(normalized) <= 80:
            bucket.add(normalized)
        else:
            for match in UID_RE.findall(value):
                bucket.add(match)


def walk_uid_json(node: Any, bucket: set[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_lower = key.lower()
            if "uid" in key_lower or key_lower == "object":
                add_uid_value(value, bucket)
            if isinstance(value, (dict, list)):
                walk_uid_json(value, bucket)
    elif isinstance(node, list):
        for value in node:
            walk_uid_json(value, bucket)


def ingest_path(path: Path, bucket: set[str]) -> int:
    before = len(bucket)
    if not path.is_file():
        return 0
    suffix = path.suffix.lower()
    try:
        if suffix == ".txt":
            for line in path.read_text(errors="ignore").splitlines():
                add_uid_value(line.split(",", 1)[0].strip(), bucket)
        elif suffix == ".csv":
            with path.open(newline="", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key in (reader.fieldnames or []):
                        key_lower = key.lower()
                        if "uid" in key_lower or key_lower == "object":
                            add_uid_value(row.get(key), bucket)
        elif suffix == ".json":
            if path.stat().st_size > 150_000_000:
                return 0
            walk_uid_json(json.loads(path.read_text()), bucket)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, csv.Error):
        return 0
    return len(bucket) - before


def build_exclusion_set() -> tuple[set[str], list[dict[str, Any]]]:
    excluded: set[str] = set()
    audit: list[dict[str, Any]] = []

    # Reuse the previously frozen disjointness source list and add every
    # screened Fresh300/Fresh B UID, including technical failures from the
    # old 508-object candidate pool.
    old_audit_path = V3 / "uid_disjointness_audit.json"
    old_audit = json.loads(old_audit_path.read_text())
    for key, source in old_audit.get("sources", {}).items():
        path = Path(source)
        added = ingest_path(path, excluded)
        audit.append({"source": key, "path": str(path), "new_uids": added,
                      "sha256": sha256_file(path) if path.is_file() else None})

    additional_lists = [
        V3 / "fresh_disjoint_candidates.txt",
        V3 / "fresh_confirm_300.txt",
        V3 / "fresh_confirm_b/fresh_confirm_B_150.txt",
        V3 / "next_stage_20261006/MULTISEED_48_UIDS.txt",
    ]
    for path in additional_lists:
        added = ingest_path(path, excluded)
        audit.append({"source": "explicit_historical_candidate_list", "path": str(path),
                      "new_uids": added, "sha256": sha256_file(path) if path.is_file() else None})

    # Include all recorded V3 object-condition outputs, not just registered
    # cohorts, and any UID-named input-render directories.
    output_files = 0
    for pattern in ("rows_shard*.json", "per_object_metrics*.csv"):
        for path in V3.rglob(pattern):
            output_files += 1
            ingest_path(path, excluded)
    audit.append({"source": "all_v3_object_condition_ledgers",
                  "path": str(V3), "files_scanned": output_files})

    for directory in (ROOT / "data/train_data/rendered_full",
                      ROOT / "data/fresh_confirm_v3_renders"):
        if directory.is_dir():
            names = 0
            for child in directory.iterdir():
                if child.is_dir():
                    add_uid_value(child.name, excluded)
                    names += 1
            audit.append({"source": "rendered_directory_safety_bucket",
                          "path": str(directory), "directories_scanned": names})

    normalized = {
        norm_uid(uid) for uid in excluded
        if norm_uid(uid).isalnum() and 12 <= len(norm_uid(uid)) <= 80
    }
    required_legacy_count = int(old_audit.get("excluded_identifier_count_normalized", 0))
    if len(normalized) < required_legacy_count:
        raise RuntimeError(
            f"historical exclusion union {len(normalized)} is below the existing audited count "
            f"{required_legacy_count}; check UID parsing before sampling"
        )
    return normalized, audit


def canonical_license(raw: Any) -> str:
    value = str(raw or "").strip().lower().replace("_", "-").replace(" ", "")
    aliases = {
        "cc0": "cc0", "cc0-1.0": "cc0", "publicdomain": "cc0",
        "by": "by", "cc-by": "by", "cc-by-4.0": "by",
        "by-sa": "by-sa", "cc-by-sa": "by-sa", "cc-by-sa-4.0": "by-sa",
    }
    return aliases.get(value, value)


def fetch_metadata_shard(shard: str) -> tuple[dict[str, Any], str]:
    path = CACHE / "metadata" / f"{shard}.json.gz"
    data = path.read_bytes() if path.is_file() else fetch_pinned(f"metadata/{shard}.json.gz", path)
    digest = sha256_bytes(data)
    return json.loads(gzip.decompress(data)), digest


def ensure_metadata_shard(shard: str) -> tuple[str, str]:
    path = CACHE / "metadata" / f"{shard}.json.gz"
    data = path.read_bytes() if path.is_file() else fetch_pinned(f"metadata/{shard}.json.gz", path)
    return shard, sha256_bytes(data)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    protocol_path = ROOT / "1006/evidence/protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md"
    script_path = Path(__file__).resolve()
    obj_paths, object_paths_sha = load_objaverse_paths()
    excluded, exclusion_audit = build_exclusion_set()
    eligible = sorted(uid for uid in obj_paths if norm_uid(uid) not in excluded)
    if len(eligible) < 1000:
        raise RuntimeError(f"only {len(eligible)} source UIDs remain after exclusions")

    shuffled = eligible[:]
    random.Random(SEED).shuffle(shuffled)
    accepted: list[dict[str, Any]] = []
    metadata_shard_hashes: dict[str, str] = {}
    reviewed_candidates = 0
    cursor = 0
    batch_size = 8000
    while len(accepted) < MAX_QUEUE_N and cursor < len(shuffled):
        batch = shuffled[cursor:cursor + batch_size]
        cursor += len(batch)
        reviewed_candidates += len(batch)
        print(f"license metadata batch: {reviewed_candidates}/{len(shuffled)} source UIDs; accepted={len(accepted)}", flush=True)
        by_shard: dict[str, list[str]] = {}
        for uid in batch:
            source_path = obj_paths[uid]
            parts = source_path.split("/")
            if len(parts) < 3 or not parts[0] == "glbs":
                continue
            by_shard.setdefault(parts[1], []).append(uid)
        batch_metadata: dict[str, tuple[dict[str, Any], str]] = {}
        with ThreadPoolExecutor(max_workers=16) as pool:
            for shard, shard_sha in pool.map(ensure_metadata_shard, by_shard):
                metadata_shard_hashes[shard] = shard_sha
        for shard, uids in by_shard.items():
            metadata, shard_sha = fetch_metadata_shard(shard)
            batch_metadata.update({uid: (metadata[uid], shard_sha) for uid in uids if uid in metadata})
        for uid in batch:
            if uid not in batch_metadata:
                continue
            item, shard_sha = batch_metadata[uid]
            license_code = canonical_license(item.get("license"))
            if license_code not in ALLOWED_LICENSES:
                continue
            user = item.get("user") or {}
            accepted.append({
                "queue_rank": len(accepted) + 1,
                "uid": uid,
                "license": license_code,
                "source_license_tag": item.get("license"),
                "name": item.get("name", ""),
                "creator": user.get("displayName") or user.get("username", ""),
                "creator_username": user.get("username", ""),
                "source_uri": item.get("uri", ""),
                "viewer_url": item.get("viewerUrl", ""),
                "source_path": obj_paths[uid],
                "metadata_shard": obj_paths[uid].split("/")[1],
                "metadata_shard_sha256": shard_sha,
            })
            if len(accepted) == MAX_QUEUE_N:
                break
        print(f"license metadata batch complete: accepted={len(accepted)}", flush=True)

    if len(accepted) < MAX_QUEUE_N:
        raise RuntimeError(f"only {len(accepted)} allowed-license candidates found")
    if len({r["uid"] for r in accepted}) != MAX_QUEUE_N:
        raise RuntimeError("candidate UID duplication detected")
    if any(norm_uid(r["uid"]) in excluded for r in accepted):
        raise RuntimeError("candidate overlaps a historical exclusion")

    csv_path = OUT / "candidate_screen_queue.csv"
    fields = list(accepted[0].keys()) + ["queue_role"]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in accepted:
            item = dict(row)
            item["queue_role"] = "screen" if row["queue_rank"] <= SCREEN_N else "reserve"
            writer.writerow(item)
    initial_path = OUT / "screen_uids_600.txt"
    initial_path.write_text("".join(row["uid"] + "\n" for row in accepted[:SCREEN_N]))
    reserve_path = OUT / "reserve_uids_400.txt"
    reserve_path.write_text("".join(row["uid"] + "\n" for row in accepted[SCREEN_N:]))

    manifest = {
        "protocol": "Fresh C3 confirmation — revision-era follow-up",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dataset": DATASET,
        "dataset_revision": REVISION,
        "dataset_url": f"https://huggingface.co/datasets/{DATASET}/tree/{REVISION}",
        "object_paths_sha256": object_paths_sha,
        "source_path_index_count": len(obj_paths),
        "selection_seed": SEED,
        "selection_algorithm": "CPython random.Random(20261006).shuffle over lexicographically sorted eligible UIDs; license-filter in shuffled order",
        "historical_exclusion_count": len(excluded),
        "historical_exclusion_sources": exclusion_audit,
        "eligible_source_uid_count": len(eligible),
        "randomized_uids_examined_for_license": reviewed_candidates,
        "candidate_queue_count": len(accepted),
        "screen_count": SCREEN_N,
        "reserve_count": len(accepted) - SCREEN_N,
        "allowed_license_tags": sorted(ALLOWED_LICENSES),
        "metadata_shard_hashes": metadata_shard_hashes,
        "candidate_queue_sha256": sha256_file(csv_path),
        "screen_uid_list_sha256": sha256_file(initial_path),
        "reserve_uid_list_sha256": sha256_file(reserve_path),
        "protocol_sha256": sha256_file(protocol_path),
        "selection_script_sha256": sha256_file(script_path),
        "prior_method_outputs_in_fresh_c": 0,
        "method_results_accessed_for_selection": False,
        "status": "PRE_METHOD_OUTPUT_CANDIDATE_QUEUE_FROZEN",
    }
    manifest_path = OUT / "CANDIDATE_QUEUE_LOCK.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    note = f"""# Fresh C candidate queue lock

Frozen before any Fresh C method output: {manifest['frozen_at_utc']}

- Source revision: `{REVISION}`
- Historical UID exclusions: {len(excluded):,}
- License-eligible candidate queue: {len(accepted)} (600 initial technical screen, 400 reserve)
- Source UIDs checked for licenses: {reviewed_candidates:,}
- Selected method outcomes accessed: no
- Candidate queue SHA-256: `{manifest['candidate_queue_sha256']}`
- Initial screen list SHA-256: `{manifest['screen_uid_list_sha256']}`
- Reserve list SHA-256: `{manifest['reserve_uid_list_sha256']}`
- Lock manifest SHA-256: `{sha256_file(manifest_path)}`

This is an outcome-blind technical queue frozen after the historical results
were known. It is not the original preregistration and does not conceal that
the confirmation question was motivated by earlier outcomes.
"""
    (OUT / "CANDIDATE_QUEUE_LOCK.md").write_text(note)
    print(json.dumps({k: manifest[k] for k in (
        "frozen_at_utc", "historical_exclusion_count", "eligible_source_uid_count",
        "randomized_uids_examined_for_license", "candidate_queue_count",
        "candidate_queue_sha256", "status")}, indent=2))


if __name__ == "__main__":
    main()
