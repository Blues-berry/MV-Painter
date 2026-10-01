#!/usr/bin/env python3
"""Index historical-LHL marker hits in tracked human-readable sources.

Generated-data CSV/JSON/logs and vendored tools are excluded because values
such as 12.97 occur as ordinary measurements there; the index targets prose,
manuscript, and source files where the markers can make a claim.
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/coordination/final_evidence_freeze_20261001/HISTORICAL_LHL_SEARCH_HITS.csv"
EXTENSIONS = {".md", ".tex", ".txt", ".py", ".sh", ".yaml", ".yml"}
MARKERS = {
    "14.776": re.compile(r"14\.776", re.IGNORECASE),
    "22.052": re.compile(r"22\.052", re.IGNORECASE),
    "14.78": re.compile(r"14\.78", re.IGNORECASE),
    "12.97": re.compile(r"12\.97", re.IGNORECASE),
    "unseeded": re.compile(r"unseeded", re.IGNORECASE),
    "Python RNG": re.compile(r"Python\s+RNG", re.IGNORECASE),
    "reference preprocessing randomness": re.compile(r"reference\s+preprocessing\s+randomness", re.IGNORECASE),
    "archived LHL": re.compile(r"archived.{0,40}\bLHL\b|\bLHL\b.{0,40}archived", re.IGNORECASE),
}


def classify(path: str) -> str:
    if path in {
        "final/round2/final_round2.tex",
        "final/round2/supplementary_round2.tex",
        "final/round2/response_letter_round2.md",
    }:
        return "ACTIVE_MANUSCRIPT_SOURCE"
    if path.startswith("final/round2/archive/") or path.startswith("final/archive/"):
        return "ARCHIVE_SUPERSEDED"
    if "/coordination/" in path:
        return "AUDIT_OR_COORDINATION_RECORD"
    return "OTHER_TRACKED_SOURCE"


def main() -> None:
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode("utf-8", "replace").split("\0")
    rows = []
    for rel in filter(None, listed):
        path = Path(rel)
        if path.suffix.lower() not in EXTENSIONS or rel.startswith("final/tools/"):
            continue
        try:
            lines = (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            found = [name for name, pattern in MARKERS.items() if pattern.search(line)]
            if found:
                rows.append({
                    "path": rel,
                    "line": number,
                    "markers": ";".join(found),
                    "source_class": classify(rel),
                    "excerpt": " ".join(line.strip().split())[:220],
                })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["path", "line", "markers", "source_class", "excerpt"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"indexed {len(rows)} prose/source hits -> {OUT.relative_to(ROOT)}")
    print("scope: tracked .md/.tex/.txt/.py/.sh/.yaml/.yml, excluding final/tools and generated CSV/JSON/log data")


if __name__ == "__main__":
    main()
