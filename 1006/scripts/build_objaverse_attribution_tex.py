#!/usr/bin/env python3
"""Generate the supplementary per-object attribution table from the CSV."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "licenses" / "objaverse_visual_cohort_attribution.csv"
OUTPUT = ROOT / "manuscript" / "objaverse_attribution_table.tex"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    output = [
        r"\begin{longtable}{r p{3.4cm} p{4.3cm} p{2.7cm} p{2.0cm}}",
        r"\caption{Source and license attribution for the fixed visual panel.}\\",
        r"\toprule",
        r"Panel & Source UID / model page & Creator & License & API record \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Panel & Source UID / model page & Creator & License & API record \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for row in rows:
        creator = row["creator"].replace("&", r"\&").replace("_", r"\_")
        creator_link = row["creator_url"] or row["model_url"]
        if row["objaverse_license_slug"] == "by-sa":
            license_text = "CC BY-SA 4.0"
        else:
            license_text = "CC BY 4.0"
        license_link = row["license_url"].replace("http://", "https://", 1)
        stale = row["api_crosscheck_status"] != "verified_from_current_api"
        if stale:
            license_text += r"$^{\dagger}$"
            api_status = r"snapshot only$^{\dagger}$"
        else:
            api_status = "live API"
        output.append(
            f"{int(row['panel']):02d} & "
            f"\\href{{{row['model_url']}}}{{Sketchfab model page}} & "
            f"\\href{{{creator_link}}}{{{creator}}} & "
            f"\\href{{{license_link}}}{{{license_text}}} & {api_status} \\\\"
        )
    output.append(r"\end{longtable}")
    OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(rows)} asset rows)")


if __name__ == "__main__":
    main()
