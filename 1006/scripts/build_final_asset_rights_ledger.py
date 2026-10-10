#!/usr/bin/env python3
"""Build a source-level rights ledger for the active GLB and visual panels."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
FRESH_PANEL = ROOT / "1006/data/fresh_c/FRESH_C_GLB_PANEL_SELECTION_20261006.json"
QUEUE = ROOT / "1006/data/fresh_c/candidate_screen_queue.csv"
DOWNLOADS = ROOT / "1006/data/fresh_c/asset_download_manifest.csv"
LEGACY_ATTR = ROOT / "1006/licenses/objaverse_visual_cohort_attribution.csv"
OUT_JSON = ROOT / "1006/evidence/audits/FRESH_C_ASSET_SOURCE_LICENSE_API_RECHECK_20261007.json"
OUT_CSV = ROOT / "1006/evidence/audits/FINAL_ASSET_RIGHTS_AND_REDISTRIBUTION_LEDGER.csv"
ALLOWED_SLUGS = {"cc0", "by", "by-sa", "cc-by", "cc-by-sa", "cc0-1.0", "cc-by-4.0", "cc-by-sa-4.0"}


def body_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def query(uid: str) -> dict:
    url = f"https://api.sketchfab.com/v3/models/{uid}"
    try:
        response = requests.get(url, timeout=20, headers={"User-Agent": "evidence-rights-audit/1.0"})
        raw = response.content
        payload = response.json() if response.status_code == 200 else {}
        license_data = payload.get("license") if isinstance(payload, dict) else None
        if not isinstance(license_data, dict):
            license_data = {}
        return {
            "uid": uid, "request_url": url, "http_status": response.status_code,
            "response_date": response.headers.get("Date", ""), "response_sha256": body_hash(raw),
            "response_bytes": len(raw), "model_title": payload.get("name", "") if isinstance(payload, dict) else "",
            "creator": (payload.get("user") or {}).get("displayName", "") if isinstance(payload, dict) else "",
            "creator_username": (payload.get("user") or {}).get("username", "") if isinstance(payload, dict) else "",
            "license_slug": str(license_data.get("slug", "")),
            "license_label": str(license_data.get("label", license_data.get("fullName", ""))),
            "license_url": str(license_data.get("url", "")),
            "result": "LICENSE_CONFIRMED" if license_data.get("slug") else ("HTTP_404" if response.status_code == 404 else "LICENSE_EMPTY_OR_UNAVAILABLE"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"uid": uid, "request_url": url, "http_status": None, "response_date": "",
                "response_sha256": "", "response_bytes": 0, "model_title": "", "creator": "",
                "creator_username": "", "license_slug": "", "license_label": "", "license_url": "",
                "result": "REQUEST_ERROR", "error": f"{type(exc).__name__}: {exc}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-api", action="store_true", help="reuse the saved current API recheck")
    args = parser.parse_args()
    panel = json.loads(FRESH_PANEL.read_text())
    if args.skip_api and OUT_JSON.exists():
        api_report = json.loads(OUT_JSON.read_text())
        api_by_uid = {x["uid"]: x for x in api_report["results"]}
    else:
        uids = [x["uid"] for x in panel["selected"]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            queried = list(pool.map(query, uids))
        api_report = {
            "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": "official Sketchfab v3 model API; GET only",
            "selection_sha256": hashlib.sha256(FRESH_PANEL.read_bytes()).hexdigest(),
            "results": queried,
        }
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(api_report, indent=2, ensure_ascii=False) + "\n")
        api_by_uid = {x["uid"]: x for x in queried}

    queue_by_uid = {r["uid"]: r for r in csv.DictReader(QUEUE.open(encoding="utf-8", newline=""))}
    download_by_uid = {r["uid"]: r for r in csv.DictReader(DOWNLOADS.open(encoding="utf-8", newline=""))}
    rows = []
    for item in panel["selected"]:
        uid = item["uid"]
        source = queue_by_uid[uid]
        dl = download_by_uid.get(uid, {})
        api = api_by_uid.get(uid, {})
        slug = api.get("license_slug", "")
        confirmed = api.get("result") == "LICENSE_CONFIRMED" and slug.lower() in ALLOWED_SLUGS
        status = "FIGURE_ONLY" if confirmed else "UNKNOWN"
        rows.append({
            "asset_uid": uid, "asset_scope": "FRESH_C_FROZEN_24_GLB_PANEL", "source": "Objaverse/Sketchfab",
            "original_url": source.get("viewer_url", ""), "source_identifier": uid,
            "creator": api.get("creator") or source.get("creator", ""),
            "creator_username": api.get("creator_username") or source.get("creator_username", ""),
            "license": api.get("license_label") or ("metadata tag only: " + source.get("license", "")),
            "license_slug_current_api": slug, "license_url": api.get("license_url", ""),
            "api_result": api.get("result", "MISSING"), "api_http_status": api.get("http_status", ""),
            "api_response_sha256": api.get("response_sha256", ""), "api_response_date": api.get("response_date", ""),
            "downloaded_date": "NOT_RECORDED_IN_SOURCE_MANIFEST", "downloaded_sha256": dl.get("sha256", item.get("asset_sha256", "")),
            "redistribution_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "derivative_images_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "glb_redistribution_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "publication_figure_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "anonymous_supplement_release_allowed": "UNKNOWN_PENDING_ATTRIBUTION_AND_ANONYMITY_REVIEW" if confirmed else "UNKNOWN",
            "evidence_source_record": f"candidate_screen_queue.csv; FRESH_C_GLB_PANEL_SELECTION_20261006.json; asset_download_manifest.csv; {OUT_JSON.relative_to(ROOT)}",
            "final_disposition": status,
        })

    for source in csv.DictReader(LEGACY_ATTR.open(encoding="utf-8", newline="")):
        confirmed = source["api_crosscheck_status"] == "verified_from_current_api"
        status = "FIGURE_ONLY" if confirmed else "UNKNOWN"
        rows.append({
            "asset_uid": source["uid"], "asset_scope": "LEGACY_3D_VISUAL_PANEL_24", "source": "Objaverse/Sketchfab",
            "original_url": source["model_url"], "source_identifier": source["uid"],
            "creator": source["creator"], "creator_username": "", "license": source["displayed_license"],
            "license_slug_current_api": source["objaverse_license_slug"], "license_url": source["license_url"],
            "api_result": source["api_crosscheck_status"], "api_http_status": "",
            "api_response_sha256": "", "api_response_date": source["verified_utc_date"],
            "downloaded_date": "NOT_RECORDED_IN_SOURCE_MANIFEST", "downloaded_sha256": "",
            "redistribution_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "derivative_images_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "glb_redistribution_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "publication_figure_allowed": "YES_WITH_ATTRIBUTION" if confirmed else "UNKNOWN",
            "anonymous_supplement_release_allowed": "UNKNOWN_PENDING_ATTRIBUTION_AND_ANONYMITY_REVIEW" if confirmed else "UNKNOWN",
            "evidence_source_record": "1006/licenses/objaverse_visual_cohort_attribution.csv; 1006/evidence/audits/ASSET_SOURCE_LICENSE_RECHECK_20261006.json",
            "final_disposition": status,
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    from collections import Counter
    print(json.dumps({"rows": len(rows), "fresh_c_rows": 24,
                      "fresh_c_api_results": dict(Counter(x.get("result", "MISSING") for x in api_report["results"])),
                      "dispositions": dict(Counter(r["final_disposition"] for r in rows)),
                      "api_record": str(OUT_JSON.relative_to(ROOT)), "ledger": str(OUT_CSV.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
