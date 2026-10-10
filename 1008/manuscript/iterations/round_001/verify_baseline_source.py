#!/usr/bin/env python3
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

for line in (HERE / "BASELINE_SOURCE_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
    expected, rel = line.split(None, 1)
    rel = rel.strip()
    path = ROOT / rel
    actual = sha(path)
    if actual != expected:
        raise SystemExit(f"FAIL: {rel}: expected {expected}, got {actual}")
print("PASS: restored TeX and referenced assets match the locked 2026-09-07 01549 submission")
