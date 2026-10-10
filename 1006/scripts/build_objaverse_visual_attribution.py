#!/usr/bin/env python3
"""Build the per-object attribution register for the 24-object visual panel.

The script reads frozen panel UIDs and Objaverse 1.0 annotations, then checks
the current Sketchfab model API for license details. Deleted/private models
and incomplete API records are retained with an explicit snapshot-only flag.
It writes metadata only; it does not download or redistribute source meshes.

Run from the repository root. Requires objaverse==0.1.7 and requests.
Network access is needed for the current API cross-check.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import time

import objaverse
import requests


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "visual_panel_classification.csv"
OUTPUT = ROOT / "licenses" / "objaverse_visual_cohort_attribution.csv"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as f:
        panels = list(csv.DictReader(f))
    uids = [row["uid"] for row in panels]
    annotations = objaverse.load_annotations(uids)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; MV-Painter evidence attribution audit/1.0)"})
    records = []

    for panel in panels:
        uid = panel["uid"]
        annotation = annotations[uid]
        model_url = annotation["viewerUrl"]
        api_url = annotation.get("uri", f"https://api.sketchfab.com/v3/models/{uid}")
        api_status = "verified_from_current_api"
        api_license_label = ""
        license_link = ""
        try:
            response = session.get(api_url, timeout=30)
            if response.status_code == 404:
                api_status = "objaverse_snapshot_only_model_api_404"
            else:
                response.raise_for_status()
                current = response.json()
                current_license = current.get("license") or {}
                api_license_label = current_license.get("fullName", "")
                license_link = current_license.get("url", "")
                if not api_license_label or not license_link:
                    api_status = "objaverse_snapshot_only_api_license_missing"
        except requests.RequestException as exc:
            api_status = f"objaverse_snapshot_only_api_error:{type(exc).__name__}"
        time.sleep(0.2)

        slug = annotation.get("license", "")
        if not license_link:
            license_link = {
                "by": "https://creativecommons.org/licenses/by/4.0/",
                "by-sa": "https://creativecommons.org/licenses/by-sa/4.0/",
            }.get(slug, "")
        license_name = api_license_label or {
            "by": "Creative Commons Attribution (Objaverse license slug: by)",
            "by-sa": "Creative Commons Attribution-ShareAlike (Objaverse license slug: by-sa)",
        }.get(slug, f"Objaverse license slug: {slug or 'unknown'}")
        creator = annotation.get("user", {}).get("displayName") or annotation.get("user", {}).get("username", "")
        creator_url = annotation.get("user", {}).get("profileUrl", "")
        model_name = annotation.get("name", "")
        records.append(
            {
                "panel": panel["panel"],
                "uid": uid,
                "model_title": model_name,
                "creator": creator,
                "creator_url": creator_url,
                "objaverse_license_slug": slug,
                "displayed_license": license_name,
                "license_url": license_link,
                "api_crosscheck_status": api_status,
                "model_url": model_url,
                "attribution_line": f'{model_name} by {creator}, via Sketchfab; {license_name} ({license_link})',
                "verified_utc_date": date.today().isoformat(),
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(records)} objects)")
    for lic in sorted({row["displayed_license"] for row in records}):
        print(f"{sum(row['displayed_license'] == lic for row in records)}\t{lic}")


if __name__ == "__main__":
    main()
