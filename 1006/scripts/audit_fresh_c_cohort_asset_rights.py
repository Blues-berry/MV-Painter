#!/usr/bin/env python3
"""Build a rights inventory from frozen Fresh C metadata and saved API checks."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDITS = ROOT / "1006/evidence/audits"
UIDS = ROOT / "1006/data/fresh_c/fresh_c_objects.txt"
QUEUE = ROOT / "1006/data/fresh_c/candidate_screen_queue.csv"
DOWNLOADS = ROOT / "1006/data/fresh_c/asset_download_manifest.csv"
OLD_LEDGER = AUDITS / "FINAL_ASSET_RIGHTS_AND_REDISTRIBUTION_LEDGER.csv"
ATLAS_RECHECK = AUDITS / "FRESH_C_ATLAS_ASSET_LICENSE_API_RECHECK_20261007.json"
COHORT_PARTIAL = AUDITS / "FRESH_C_COHORT_ASSET_API_RECHECK.partial.json"
GALLERY = ROOT / "1006/figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json"
API_OUT = AUDITS / "FRESH_C_IMAGE_COHORT_ASSET_API_RECHECK_20261007.json"
LEDGER_OUT = AUDITS / "FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv"
ATTRIBUTION_OUT = AUDITS / "FRESH_C_ATLAS_ATTRIBUTION_20261007.csv"
SUMMARY_OUT = AUDITS / "FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.json"

LICENSE_URLS = {
    "by": "https://creativecommons.org/licenses/by/4.0/",
    "by-sa": "https://creativecommons.org/licenses/by-sa/4.0/",
    "cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
}
SLUG_FAMILY = {"cc0-1.0": "cc0", "cc-by-4.0": "by", "cc-by-sa-4.0": "by-sa",
               "cc-by": "by", "cc-by-sa": "by-sa"}
ALLOWED = {"by", "by-sa", "cc0"}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def api_record_from_atlas(row: dict, queue_row: dict) -> dict:
    lic = row.get("api_license") or {}
    return {
        "uid": row["uid"], "checked_utc": row.get("checked_utc", ""),
        "http_status": row.get("http_status"), "api_license_slug": lic.get("slug", ""),
        "api_license_label": lic.get("label", lic.get("fullName", "")),
        "api_license_url": lic.get("url", ""), "creator": queue_row.get("creator", ""),
        "creator_username": row.get("creator_username", ""), "title": row.get("name", ""),
        "api_response_date": "", "response_sha256": row.get("response_sha256", ""),
        "error": row.get("error", ""), "api_url": row.get("api_url", ""),
    }


def main() -> None:
    AUDITS.mkdir(parents=True, exist_ok=True)
    uids = [x.strip() for x in UIDS.read_text().splitlines() if x.strip()]
    if len(uids) != 300 or len(set(uids)) != 300:
        raise ValueError(f"Expected 300 unique Fresh C objects, got {len(uids)} rows/{len(set(uids))} unique")
    queue = {r["uid"]: r for r in read_csv(QUEUE)}
    downloads = {r["uid"]: r for r in read_csv(DOWNLOADS)}
    prior = {r["asset_uid"]: r for r in read_csv(OLD_LEDGER) if r["asset_scope"] == "FRESH_C_FROZEN_24_GLB_PANEL"}
    if not set(uids) <= queue.keys() or not set(uids) <= downloads.keys():
        raise ValueError("Fresh C UID list does not match its source queue/download manifest")

    atlas = json.loads(ATLAS_RECHECK.read_text())
    atlas_api = {r["uid"]: api_record_from_atlas(r, queue[r["uid"]]) for r in atlas["records"]}
    selected = json.loads(GALLERY.read_text())["selected_groups"]
    atlas_uids = {r["object_uid"] for r in selected}
    if len(atlas_uids) != 20 or atlas_uids != set(atlas_api) or not atlas_uids <= set(uids):
        raise ValueError("Atlas membership does not match the saved 20-object current API audit")

    cached = {}
    if API_OUT.exists():
        cached.update({r["uid"]: r for r in json.loads(API_OUT.read_text()).get("records", [])})
    cached.update(atlas_api)
    if COHORT_PARTIAL.exists():
        cached.update({r["uid"]: r for r in json.loads(COHORT_PARTIAL.read_text()).get("records", [])})

    records = []
    for uid in uids:
        if uid in cached:
            row = dict(cached[uid])
        else:
            row = {"uid": uid, "checked_utc": "", "http_status": None, "api_license_slug": "",
                   "api_license_label": "", "api_license_url": "", "creator": "", "creator_username": "",
                   "title": "", "api_response_date": "", "response_sha256": "", "error": "NOT_RECHECKED_AFTER_RATE_LIMIT_STOP",
                   "api_url": f"https://api.sketchfab.com/v3/models/{uid}"}
        records.append(row)

    checked_count = sum(bool(r.get("checked_utc") and r.get("http_status") is not None) for r in records)
    http_status_counts = dict(Counter(str(r.get("http_status") or "NOT_RECHECKED") for r in records))
    input_hashes = {p.relative_to(ROOT).as_posix(): sha256(p) for p in [UIDS, QUEUE, DOWNLOADS, OLD_LEDGER, ATLAS_RECHECK, GALLERY]}
    api_report = {
        "status": "COMPLETE" if checked_count == 300 and all(r.get("http_status") == 200 for r in records) else "PARTIAL_RATE_LIMITED",
        "scope": "Frozen Fresh C 300-object cohort; saved official Sketchfab metadata GET responses only; no model downloads",
        "checked_utc": datetime.now(timezone.utc).isoformat(), "count": len(records),
        "current_api_checked_count": checked_count, "http_status_counts": http_status_counts,
        "input_files_sha256": input_hashes,
        "stop_reason": "Stopped after API returned HTTP 429 and HTTP 401; remaining rows use source snapshot metadata and are explicitly not current-API verified.",
        "records": records,
    }
    API_OUT.write_text(json.dumps(api_report, indent=2, ensure_ascii=False) + "\n")

    fields = ["asset_uid", "asset_scope", "cohort_role", "source", "original_url", "source_identifier",
              "creator", "creator_username", "title", "source_license_tag", "license", "license_slug_current_api",
              "license_url", "current_api_status", "api_http_status", "api_response_sha256", "api_response_date",
              "prior_api_result", "prior_api_status", "prior_api_response_sha256", "downloaded_date", "downloaded_sha256",
              "redistribution_allowed", "derivative_images_allowed", "glb_redistribution_allowed",
              "publication_figure_allowed", "anonymous_supplement_release_allowed", "evidence_source_record", "final_disposition"]
    rows = []
    for r in records:
        uid = r["uid"]
        source, download, old = queue[uid], downloads[uid], prior.get(uid, {})
        tag = source.get("source_license_tag", "").lower()
        tag_family = SLUG_FAMILY.get(tag, tag)
        slug = r.get("api_license_slug", "").lower()
        api_family = SLUG_FAMILY.get(slug, slug)
        http = r.get("http_status")
        checked = bool(r.get("checked_utc") and http is not None)
        matched = not tag_family or tag_family == api_family
        current_confirmed = checked and http == 200 and api_family in ALLOWED and matched
        api_status = ("LICENSE_CONFIRMED" if current_confirmed else
                      f"HTTP_{http}" if checked and http != 200 else
                      "LICENSE_MISMATCH_OR_RESTRICTIVE" if checked else "NOT_RECHECKED_AFTER_RATE_LIMIT_STOP")

        if current_confirmed:
            disposition = "FIGURE_ONLY" if uid in atlas_uids else "METRICS_ONLY"
            permission = ("YES_WITH_ATTRIBUTION_AND_SHAREALIKE" if api_family == "by-sa" else
                          "YES_WITH_ATTRIBUTION" if api_family == "by" else "YES_CC0")
            rights = {k: permission for k in ("redistribution_allowed", "derivative_images_allowed", "glb_redistribution_allowed",
                                               "publication_figure_allowed", "anonymous_supplement_release_allowed")}
        elif old.get("final_disposition") == "UNKNOWN":
            disposition, rights = "UNKNOWN", {k: "UNKNOWN" for k in ("redistribution_allowed", "derivative_images_allowed",
                       "glb_redistribution_allowed", "publication_figure_allowed", "anonymous_supplement_release_allowed")}
        elif checked and (http == 404 or http == 200):
            disposition, rights = "UNKNOWN", {k: "UNKNOWN" for k in ("redistribution_allowed", "derivative_images_allowed",
                       "glb_redistribution_allowed", "publication_figure_allowed", "anonymous_supplement_release_allowed")}
        elif uid not in atlas_uids and tag_family in ALLOWED:
            disposition = "METRICS_ONLY"
            rights = {k: "NO_ASSET_OR_DERIVED_IMAGE_IN_CANDIDATE_PACKAGE" for k in ("redistribution_allowed", "derivative_images_allowed",
                       "glb_redistribution_allowed", "publication_figure_allowed", "anonymous_supplement_release_allowed")}
        else:
            disposition, rights = "UNKNOWN", {k: "UNKNOWN" for k in ("redistribution_allowed", "derivative_images_allowed",
                       "glb_redistribution_allowed", "publication_figure_allowed", "anonymous_supplement_release_allowed")}

        license_label = r.get("api_license_label") or ("metadata tag only: " + source.get("license", ""))
        license_url = r.get("api_license_url") or LICENSE_URLS.get(tag_family, "")
        rows.append({
            "asset_uid": uid, "asset_scope": "FRESH_C_IMAGE_COHORT_300",
            "cohort_role": "FIGURE_D_ATLAS" if uid in atlas_uids else "METRIC_COHORT",
            "source": "Objaverse/Sketchfab", "original_url": source.get("viewer_url", ""), "source_identifier": uid,
            "creator": r.get("creator") or source.get("creator", ""),
            "creator_username": r.get("creator_username") or source.get("creator_username", ""),
            "title": r.get("title") or source.get("name", ""), "source_license_tag": source.get("source_license_tag", ""),
            "license": license_label, "license_slug_current_api": slug, "license_url": license_url,
            "current_api_status": api_status, "api_http_status": http if checked else "",
            "api_response_sha256": r.get("response_sha256", ""), "api_response_date": r.get("api_response_date", ""),
            "prior_api_result": old.get("api_result", ""), "prior_api_status": old.get("api_http_status", ""),
            "prior_api_response_sha256": old.get("api_response_sha256", ""),
            "downloaded_date": "NOT_RECORDED_IN_SOURCE_MANIFEST", "downloaded_sha256": download.get("sha256", ""),
            **rights,
            "evidence_source_record": "fresh_c_objects.txt; candidate_screen_queue.csv; asset_download_manifest.csv; saved Sketchfab API audit; original 48-row rights ledger",
            "final_disposition": disposition,
        })
    with LEDGER_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    attribution_fields = ["figure", "panel_order", "asset_uid", "title", "creator", "creator_username", "source_url",
                          "license", "license_url", "credit_line", "api_response_sha256", "downloaded_date", "downloaded_sha256", "status"]
    attribution_rows = []
    for group in selected:
        uid = group["object_uid"]
        r, source, download = cached[uid], queue[uid], downloads[uid]
        title, creator = r.get("title") or source.get("name", ""), r.get("creator") or source.get("creator", "")
        license_ok = r.get("http_status") == 200 and SLUG_FAMILY.get(r.get("api_license_slug", ""), r.get("api_license_slug", "")) == "by"
        license_name = r.get("api_license_label") or "CC Attribution"
        license_url = r.get("api_license_url") or LICENSE_URLS["by"]
        credit = f'"{title}" by {creator}, via Sketchfab ({source.get("viewer_url", "")}), licensed {license_name} ({license_url}). Rendered and arranged in the study contact sheet.'
        attribution_rows.append({
            "figure": "D", "panel_order": group["panel_order"], "asset_uid": uid, "title": title,
            "creator": creator, "creator_username": r.get("creator_username") or source.get("creator_username", ""),
            "source_url": source.get("viewer_url", ""), "license": license_name, "license_url": license_url,
            "credit_line": credit, "api_response_sha256": r.get("response_sha256", ""),
            "downloaded_date": "NOT_RECORDED_IN_SOURCE_MANIFEST", "downloaded_sha256": download.get("sha256", ""),
            "status": "VERIFIED_CC_BY_ATTRIBUTION_REQUIRED" if license_ok else "NOT_CLEARED",
        })
    with ATTRIBUTION_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=attribution_fields)
        writer.writeheader()
        writer.writerows(attribution_rows)

    summary = {
        "status": api_report["status"], "scope": api_report["scope"], "cohort_count": len(rows),
        "current_api_checked_count": checked_count, "http_status_counts": http_status_counts,
        "dispositions": dict(Counter(r["final_disposition"] for r in rows)),
        "source_license_tags": dict(Counter(queue[u]["source_license_tag"] for u in uids)),
        "atlas_api_status": dict(Counter(f"{r['api_http_status']}:{r['license_slug_current_api'] or 'UNAVAILABLE'}" for r in rows if r["cohort_role"] == "FIGURE_D_ATLAS")),
        "atlas_attribution_rows": len(attribution_rows), "atlas_attribution_verified": sum(r["status"] == "VERIFIED_CC_BY_ATTRIBUTION_REQUIRED" for r in attribution_rows),
        "download_dates": "NOT_RECORDED_IN_SOURCE_MANIFEST", "old_48_row_ledger_overwritten": False,
        "input_files_sha256": input_hashes,
        "api_report_sha256": sha256(API_OUT), "rights_ledger_sha256": sha256(LEDGER_OUT),
        "atlas_attribution_sha256": sha256(ATTRIBUTION_OUT), "audit_script_sha256": sha256(Path(__file__)),
        "api_report": API_OUT.relative_to(ROOT).as_posix(), "rights_ledger": LEDGER_OUT.relative_to(ROOT).as_posix(),
        "atlas_attribution": ATTRIBUTION_OUT.relative_to(ROOT).as_posix(),
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    COHORT_PARTIAL.unlink(missing_ok=True)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
