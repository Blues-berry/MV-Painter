#!/usr/bin/env python3
"""Check GPU device mapping before starting a model inference job."""

from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geotex.runtime import cuda_report, require_cuda  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    report = cuda_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    try:
        require_cuda(args.device, "GPU preflight")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"GPU device {args.device} is available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
