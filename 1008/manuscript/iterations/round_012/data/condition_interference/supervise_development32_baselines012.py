"""Finish both existing grid workers, then run the frozen32 three-seed baseline matrix."""
import subprocess,sys,time,json,os
from pathlib import Path
from revision_expansion_common import OUT,write,sha
HERE=Path(__file__).resolve().parent;ROOT=OUT/'iteration012_condition_interference';worker=HERE/'probe_condition_interference012.py';status=ROOT/'DEVELOPMENT32_SUPERVISOR.json'
def runpath(mode,seed,rank):return ROOT/f'development32_{mode}_seed{seed}_rank{rank}'
def terminal(path):
 p=path/'RUN_IDENTITY.json'
 if not p.exists():return False
 d=json.loads(p.read_text());assert not d['status'].startswith('FAILED'),d.get('error');return d['status'].startswith('COMPLETE_')
def live(path):
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:a=[x.decode() for x in p.read_bytes().split(b'\0') if x]
  except (OSError,UnicodeDecodeError):continue
  if str(path) in a and any(Path(x).name==worker.name for x in a):return True
 return False
try:
 assert not status.exists();freeze=ROOT/'DEVELOPMENT32_BASELINE_FREEZE.json';plan=json.loads(freeze.read_text());assert len(plan['uids'])==32 and plan['seeds']==[42,2026,31415];source_sha=sha(worker);write(status,{'status':'WAITING_VERIFIED_INITIAL_GRID32','pid':os.getpid(),'worker_sha256':source_sha,'freeze_sha256':sha(freeze)})
 initial=[runpath('grid_projection',42,rank) for rank in [0,1]]
 while not all(terminal(p) for p in initial):
  for p in initial:
   if not terminal(p):assert live(p),f'Initial worker missing and incomplete: {p}; no automatic restart'
  time.sleep(2)
 stages=[('view_projection',42)]+[(mode,seed) for seed in [2026,31415] for mode in ['native','grid_projection','view_projection']]
 for mode,seed in stages:
  assert sha(worker)==source_sha,'Worker changed after freeze';write(status,{'status':'RUNNING_FROZEN_DEVELOPMENT32_BASELINES','pid':os.getpid(),'mode':mode,'seed':seed,'worker_sha256':source_sha});children=[];handles=[]
  for rank in [0,1]:
   run=runpath(mode,seed,rank);assert not run.exists();log=(ROOT/f'development32_{mode}_seed{seed}_rank{rank}.log').open('w');handles.append(log);args=[sys.executable,str(worker),'--device',f'cuda:{rank}','--mode',mode,'--count','32','--rank',str(rank),'--seed',str(seed),'--start-index','6' if seed==42 else '0','--run-root',str(run)];children.append(subprocess.Popen(args,cwd=HERE.parents[1],stdout=log,stderr=subprocess.STDOUT))
  for child in children:assert child.wait()==0,'Development baseline worker failed; preserve outputs, no automatic retry'
  for log in handles:log.close()
  assert all(terminal(runpath(mode,seed,rank)) for rank in [0,1])
 write(status,{'status':'COMPLETE_FROZEN_DEVELOPMENT32_GENERATION_NEW_CELLS','pid':os.getpid(),'worker_sha256':source_sha,'freeze_sha256':sha(freeze),'scope':'Generation stages complete only; aggregate reuse ledger and scoring still required. No new-method superiority claim.'})
except Exception as exc:write(status,{'status':'FAILED_NO_AUTOMATIC_RETRY','pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
