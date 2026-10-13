#!/usr/bin/env python
"""Independent, resumable A-2 launcher with durable state markers."""

from __future__ import annotations

import fcntl
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/stage_placement_276_20260929"
STATUS = OUT / "status.json"
FINAL = OUT / "final_manifest.json"
DONE = OUT / "DONE"
FAILED = OUT / "FAILED"
LOG = OUT / "runner_stage_placement_276_20260929_resume_v2.log"
LOCK_PATH = OUT / ".a2_independent_launcher.lock"
RUN_ID = "stage_placement_276_20260929_resume_v2"


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def records_and_errors() -> tuple[list[Path], list[str]]:
    records = sorted((OUT / "records").glob("*.json"))
    errors = (OUT / "errors.jsonl").read_text().splitlines() if (OUT / "errors.jsonl").exists() else []
    return records, errors


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    lock_handle = LOCK_PATH.open("w")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("another A-2 independent launcher is active", file=sys.stderr)
        return 73

    existing_records, _ = records_and_errors()
    remaining = max(0, 276 - len(existing_records))
    estimated_seconds = remaining * 30 + 300
    started = now()
    python_executable = os.environ.get("MVPAINTER_PYTHON", sys.executable)
    command = [
        python_executable,
        str(ROOT / "geotex/stage_placement_eval.py"),
        "--config", str(ROOT / "MVPainter/configs/mvpainter-geotex-full-train.yaml"),
        "--checkpoint", str(ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"),
        "--object-list", str(ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"),
        "--output-dir", str(OUT),
        "--device", "cuda:0",
        "--steps", "50",
        "--seed", "42",
        "--run",
        "--resume",
    ]
    environment = os.environ.copy()
    environment.setdefault("CUDA_VISIBLE_DEVICES", "1")
    visible_gpu = environment["CUDA_VISIBLE_DEVICES"]
    project_paths = os.pathsep.join(
        str(path) for path in (ROOT, ROOT / "geotex", ROOT / "MVPainter")
    )
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        value for value in (project_paths, existing_pythonpath) if value
    )

    DONE.unlink(missing_ok=True)
    FAILED.unlink(missing_ok=True)
    with LOG.open("a") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    atomic_json(STATUS, {
        "run_id": RUN_ID,
        "phase": "running",
        "pid": process.pid,
        "launcher_pid": os.getpid(),
        "gpu_visible_device": visible_gpu,
        "torch_device": "cuda:0",
        "started_at": stamp(started),
        "estimated_complete_at": stamp(started + timedelta(seconds=estimated_seconds)),
        "expected_remaining_seconds": estimated_seconds,
        "existing_valid_records_at_launch": len(existing_records),
        "output_dir": str(OUT.resolve()),
        "log": str(LOG.resolve()),
        "command": shlex.join(command),
        "resume": True,
        "protocol": "clean-v2-stage-placement-followup-v1",
    })

    return_code = process.wait()
    finished = now()
    records, errors = records_and_errors()
    runner_manifest = OUT / "stage_placement_manifest.json"
    final_payload: dict[str, object] = {
        "run_id": RUN_ID,
        "phase": "completed" if return_code == 0 else "failed",
        "exit_code": return_code,
        "pid": process.pid,
        "finished_at": stamp(finished),
        "record_count": len(records),
        "error_count": len(errors),
        "per_object_metrics_exists": (OUT / "per_object_metrics.csv").exists(),
        "stage_placement_manifest_exists": runner_manifest.exists(),
        "output_dir": str(OUT.resolve()),
    }
    if runner_manifest.exists():
        try:
            final_payload["runner_manifest"] = json.loads(runner_manifest.read_text())
        except Exception as exc:
            final_payload["runner_manifest_read_error"] = repr(exc)
    atomic_json(FINAL, final_payload)
    atomic_json(STATUS, {
        "run_id": RUN_ID,
        "phase": final_payload["phase"],
        "pid": process.pid,
        "finished_at": stamp(finished),
        "exit_code": return_code,
        "record_count": len(records),
        "error_count": len(errors),
        "final_manifest": str(FINAL.resolve()),
    })
    (DONE if return_code == 0 else FAILED).touch()
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
