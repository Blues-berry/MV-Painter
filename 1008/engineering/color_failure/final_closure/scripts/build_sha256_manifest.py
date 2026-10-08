#!/usr/bin/env python3
"""Write a checksum manifest for staged evidence and explicitly local-only data."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / "1008/engineering/color_failure"
OUT = ARTIFACT / "final_closure/SHA256SUMS.txt"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def files_under(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*") if p.is_file())


def main() -> None:
    raw = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], cwd=ROOT
    )
    staged = [Path(s.decode()) for s in raw.split(b"\0") if s]
    staged = [p for p in staged if p != OUT.relative_to(ROOT) and (ROOT / p).is_file()]

    selected = set(staged)
    excluded_raw = [
        p for p in files_under(ARTIFACT / "raw_rgb")
        if p.suffix.lower() == ".png" and p.relative_to(ROOT) not in selected
    ]
    excluded_runs = files_under(ARTIFACT / "runs")
    excluded_repro = files_under(ARTIFACT / "final_closure/repro")
    excluded_logs = [p for p in files_under(ARTIFACT / "logs") if p.suffix == ".log"]

    lines = [
        "# SHA-256 identities for the R1 color-fidelity closure.",
        "# Standard entries below are staged for the experiment branch; run sha256sum -c from the repository root.",
        "# The SHA256SUMS.txt file is intentionally not self-hashed.",
        "",
    ]
    for p in sorted(staged, key=lambda q: str(q)):
        lines.append(f"{sha(ROOT / p)}  {p.as_posix()}")

    lines += [
        "",
        "# EXTERNAL READ-ONLY INPUTS; not copied into this repository.",
        "# The checkpoint is referenced by its SHA and location; it is not uploaded.",
        "# The original 01549 manuscript/figures were read-only and remain in the separate paper worktree.",
        "",
        "# LOCAL-ONLY FILES; hashes/sizes below identify evidence intentionally not uploaded.",
        "# Reason: full tensor traces and redundant raw runs exceed the useful review payload; compact tables, scripts, and selected RGBs are staged.",
    ]
    groups = [
        ("unselected raw_rgb PNGs", excluded_raw),
        ("full raw run outputs/residual logs", excluded_runs),
        ("full trace/intermediate scratch", excluded_repro),
        ("console logs", excluded_logs),
    ]
    for label, paths in groups:
        total = sum(p.stat().st_size for p in paths)
        lines.append(f"# {label}: {len(paths)} files, {total} bytes")
        for p in paths:
            lines.append(f"# {sha(p)}  {p.stat().st_size}  {p.relative_to(ROOT).as_posix()}")

    external = [
        ("0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0",
         "/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"),
        ("203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01",
         "/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/final_0903.tex"),
        ("0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620",
         "/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/fig4.pdf"),
        ("585af2af647e9f169cb98320fb5779aaba158b3493ea054bea2ff8eef675546c",
         "/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/fig6.pdf"),
        ("fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da",
         "/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/01549_submitted_manuscript_0907.pdf"),
    ]
    for digest, path in external:
        lines.append(f"# EXTERNAL SHA256 {digest}  {path}")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} with {len(staged)} staged and "
          f"{sum(len(ps) for _, ps in groups)} local-only file identities")


if __name__ == "__main__":
    main()
