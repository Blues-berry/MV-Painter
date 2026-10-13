#!/usr/bin/env python3
"""P0 read-only queue watcher for the increment folder.

Does NOT replace the in-flight monitor_persistent_queue012.py (which stays authoritative
inside iteration012). This watcher adds a per-run progress snapshot (how many of the
frozen 32-object development cells are complete per mode/seed) plus the aggregate view
needed to decide when the evaluation preplan may run. It only reads; failures are
reported, never restarted.
"""
import json
import time
from pathlib import Path

R12 = Path('/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/iteration012_condition_interference')
OUT = Path('/4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p0_queue_watch')
SUPERVISORS = ['DEVELOPMENT32_SUPERVISOR.json', 'INTERACTION_CANDIDATE_SUPERVISOR.json',
               'MVADAPTER_DEVELOPMENT_SUPERVISOR.json', 'APG_NATIVE_GATE_SUPERVISOR.json']
ONCE = '--once' in __import__('sys').argv


def run_complete(run_dir: Path) -> bool:
    ident = run_dir / 'RUN_IDENTITY.json'
    if not ident.is_file():
        return False
    try:
        return json.loads(ident.read_text())['status'].startswith('COMPLETE_')
    except Exception:
        return False


def progress() -> dict:
    cells = {}
    for run_dir in sorted(R12.glob('development32_*_rank*')):
        if run_dir.is_dir():
            cells[run_dir.name] = run_complete(run_dir)
    done = sum(cells.values())
    return {'development32_cells_complete': f'{done}/{len(cells)}',
            'cells': cells}


def snapshot() -> dict:
    rows = []
    for name in SUPERVISORS:
        p = R12 / name
        try:
            d = json.loads(p.read_text())
            proc = Path('/proc') / str(d.get('pid', -1)) / 'cmdline'
            rows.append({'file': name, 'status': d['status'],
                         'live': proc.exists() and bool(proc.read_bytes())})
        except Exception as exc:
            rows.append({'file': name, 'status': f'READ_ERROR: {exc}', 'live': False})
    overall = ('FAILED_REQUIRES_REVIEW' if any(r['status'].startswith('FAILED') or
                                               (not r['status'].startswith(('COMPLETE', 'WAITING', 'RUNNING')) or False) or
                                               (not r['status'].startswith('COMPLETE') and not r['live'])
                                               for r in rows)
               else 'COMPLETE_FROZEN_CHAIN' if all(r['status'].startswith('COMPLETE') for r in rows)
               else 'RUNNING_PERSISTENT_CHAIN')
    return {'status': overall, 'supervisors': rows, 'progress': progress(),
            'note': 'read-only watcher; the in-flight queue monitor inside iteration012 stays authoritative; no restarts'}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    while True:
        snap = snapshot()
        (OUT / 'P0_QUEUE_SNAPSHOT.json').write_text(json.dumps(snap, indent=2) + '\n')
        if ONCE or snap['status'] in ('COMPLETE_FROZEN_CHAIN', 'FAILED_REQUIRES_REVIEW'):
            print(json.dumps({'status': snap['status'], 'progress': snap['progress']['development32_cells_complete']}))
            break
        time.sleep(120)


if __name__ == '__main__':
    main()
