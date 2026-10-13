"""Wait for active GPU work to finish, then train and evaluate the frozen cohort."""
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/4T/CXY/MV-Painter')
ARTIFACT = Path('/4T/CXY/MV-Painter/final/round2/main_adapter_original276_leaveout_20261012')
OUT = Path('/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_original276_leaveout_20261012')
TRAIN_ENTRY = ARTIFACT / 'run_train_seeded.py'
EVAL_ENTRY = ROOT / 'geotex/round2_main_eval.py'
EVAL_UIDS = ARTIFACT / 'eval_original276_uids.txt'
CHECKPOINT = OUT / 'checkpoints/geotex_step_0002000.pt'
MANIFEST = ARTIFACT / 'protocol_manifest.json'
LOG_DIR = OUT / 'logs'
PYTHON = '/home/ubuntu/anaconda3/bin/python'
WORKDIR = '/tmp/mv_main_rerun/geotex'
MARKERS = ('MV-Painter-1010/1010/experiments/', 'run_mva_temporal013.py', 'supervise_supplement013.py')
IDLE_WINDOW_S = 120
POLL_S = 20

def stamp():
    return datetime.now(timezone.utc).isoformat()

def log(message):
    line = f'{stamp()} {message}'
    print(line, flush=True)
    with (LOG_DIR / 'queue.log').open('a') as f:
        f.write(line + '\n')

def write_manifest(update):
    data = json.loads(MANIFEST.read_text())
    data.update(update)
    MANIFEST.write_text(json.dumps(data, indent=2) + '\n')

def gpu_state():
    result = subprocess.run([
        'nvidia-smi', '--query-gpu=memory.used,utilization.gpu',
        '--format=csv,noheader,nounits'
    ], check=True, capture_output=True, text=True)
    rows = []
    for line in result.stdout.strip().splitlines():
        memory, utilization = [int(part.strip()) for part in line.split(',')]
        rows.append((memory, utilization))
    return rows

def active_competitor_commands():
    commands = []
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            pid = int(proc.name)
            if pid == os.getpid():
                continue
            raw = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if any(marker in raw for marker in MARKERS):
                commands.append((pid, raw.strip()))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return commands

def run_logged(args, log_path, env):
    log(f'start: {" ".join(map(str, args))}')
    with log_path.open('w') as f:
        result = subprocess.run(args, cwd=WORKDIR, env=env, stdout=f, stderr=subprocess.STDOUT)
    log(f'finished: {log_path.name} exit={result.returncode}')
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, args)

if not OUT.is_dir() or not LOG_DIR.is_dir():
    raise SystemExit('Frozen output location disappeared; refusing to launch')
if CHECKPOINT.exists():
    raise SystemExit('Checkpoint path already exists; refusing to overwrite')

log('queued; waiting for all GPUs to be idle and the active MVA experiment processes to exit')
idle_since = None
last_notice = 0.0
while True:
    try:
        state = gpu_state()
    except Exception as exc:
        log(f'GPU query unavailable, retrying: {exc}')
        time.sleep(POLL_S)
        continue
    competitors = active_competitor_commands()
    free = len(state) >= 2 and all(memory <= 512 and util <= 5 for memory, util in state)
    if free and not competitors:
        idle_since = idle_since or time.monotonic()
        elapsed = int(time.monotonic() - idle_since)
        if elapsed >= IDLE_WINDOW_S:
            break
        if time.monotonic() - last_notice >= 60:
            log(f'GPUs appear idle; confirming stability for {IDLE_WINDOW_S}s ({elapsed}s observed)')
            last_notice = time.monotonic()
    else:
        idle_since = None
        if time.monotonic() - last_notice >= 60:
            log(f'holding: gpu_memory_util={state}, competing_experiment_processes={len(competitors)}')
            last_notice = time.monotonic()
    time.sleep(POLL_S)

device = 'cuda:0'
start = stamp()
log(f'GPU idle gate passed; starting the 2,000-step retrain on {device}')
write_manifest({'status': 'running', 'started_utc': start, 'device': device})
env = os.environ.copy()
env['PYTHONPATH'] = '/tmp/mv_main_rerun/geotex'
try:
    run_logged([PYTHON, str(TRAIN_ENTRY), device], LOG_DIR / 'training.log', env)
    if not CHECKPOINT.is_file() or CHECKPOINT.stat().st_size == 0:
        raise RuntimeError('Expected step-2000 checkpoint was not produced')
    digest = hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()
    eval_dir = OUT / 'eval_original276_unique6'
    eval_cmd = [
        PYTHON, str(EVAL_ENTRY), '--config', '../MVPainter/configs/mvpainter-geotex-full-train.yaml',
        '--checkpoint', str(CHECKPOINT), '--output_dir', str(eval_dir),
        '--num_objects', '276', '--device', device, '--steps', '50', '--seed', '42',
        '--object-list-file', str(EVAL_UIDS),
    ]
    run_logged(eval_cmd, LOG_DIR / 'evaluation.log', env)
    eval_manifest = eval_dir / 'evaluation_manifest.json'
    data = json.loads(eval_manifest.read_text())
    if data.get('num_objects') != 276 or data.get('object_uids') != EVAL_UIDS.read_text().splitlines():
        raise RuntimeError('Evaluation manifest does not match the frozen original 276 UIDs')
    write_manifest({
        'status': 'complete', 'completed_utc': stamp(),
        'checkpoint_sha256': digest, 'evaluation_manifest': str(eval_manifest),
        'evaluation_manifest_sha256': hashlib.sha256(eval_manifest.read_bytes()).hexdigest(),
    })
    log('training and original-276 evaluation completed successfully')
except Exception as exc:
    write_manifest({'status': 'failed', 'failed_utc': stamp(), 'error': repr(exc)})
    log(f'FAILED: {exc!r}')
    raise
