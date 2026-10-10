#!/usr/bin/env python3
"""Create a clean, deterministic source archive for the 1008 author review."""
from __future__ import annotations

import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVISION = ROOT / "1008/manuscript/revision_01549_restored"
ORIGINAL = ROOT / "1008/manuscript/source_01549"
REVIEW = ROOT / "1008/submission_1008_author_review"
SELECTION = ROOT / "1008/audits/source_evidence/r1/fresh_c_visual/FRESH_C_COLOR_FIGURE_SELECTION.csv"
OUTPUT = REVIEW / "LaTeX_Source_1008.zip"
EXCLUDED_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".pyc", ".synctex.gz", ".toc"}
FORBIDDEN_SUFFIXES = {".json", ".npz", ".pt", ".pth", ".ckpt", ".glb"}
ARCHIVE_TIME = (2026, 10, 10, 0, 0, 0)


def archive_files() -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = [
        (REVIEW / "README_LaTeX_Source_1008.txt", "README_LaTeX_Source_1008.txt"),
    ]
    for source_root, prefix in ((REVISION, "revision_01549_restored"), (ORIGINAL, "source_01549")):
        for path in source_root.rglob("*"):
            if not path.is_file() or "build" in path.relative_to(source_root).parts:
                continue
            if path.name.lower().endswith(".synctex.gz") or path.suffix.lower() in EXCLUDED_SUFFIXES:
                continue
            archive_name = f"{prefix}/{path.relative_to(source_root).as_posix()}"
            files.append((path, archive_name))
    files.append((SELECTION, "revision_01549_restored/figures/FRESH_C_COLOR_FIGURE_SELECTION.csv"))
    return sorted(files, key=lambda item: item[1])


def main() -> None:
    files = archive_files()
    if not all(path.is_file() for path, _ in files):
        missing = [str(path) for path, _ in files if not path.is_file()]
        raise SystemExit(f"Missing source archive inputs: {missing}")
    bad = [name for _, name in files if Path(name).suffix.lower() in FORBIDDEN_SUFFIXES]
    if bad:
        raise SystemExit(f"Generated or raw-data artifacts are not allowed in the source archive: {bad[:5]}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, name in files:
            info = zipfile.ZipInfo(name, date_time=ARCHIVE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(OUTPUT) as archive:
        bad = [name for name in archive.namelist() if Path(name).suffix.lower() in FORBIDDEN_SUFFIXES]
        if bad or archive.testzip() is not None:
            raise SystemExit(f"Invalid source archive: {bad[:5]}")
    print(f"Created {OUTPUT} ({len(files)} files, {OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
