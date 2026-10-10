#!/usr/bin/env python3
"""Canonical no-GPU analysis entry point: integrity, frozen statistics, sign audit."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
SCRIPTS = ROOT / "1006/scripts"


def run(script: str, command: str | None = None) -> None:
    args = [sys.executable, str(SCRIPTS / script)]
    if command:
        args.append(command)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    # Both integrity gates must pass before either locked analysis is regenerated.
    run("audit_analyze_fresh_c.py", "integrity")
    run("audit_analyze_fresh_c_addendum.py", "integrity")
    run("audit_analyze_fresh_c.py", "analyze")
    run("audit_analyze_fresh_c_addendum.py", "analyze")
    run("validate_fresh_c_result_directions.py")


if __name__ == "__main__":
    main()
