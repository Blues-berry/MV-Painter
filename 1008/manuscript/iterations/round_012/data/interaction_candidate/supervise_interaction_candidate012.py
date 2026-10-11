"""Run candidate32x3 only after the verified baseline queue releases both GPUs."""
import json,os,sys,time,subprocess
from pathlib import Path
from revision_expansion_common import OUT,write,sha
HERE=Path(__file__).resolve().parent;ROOT=OUT/'iteration012_condition_interference';status=ROOT/'INTERACTION_CANDIDATE_SUPERVISOR.json'
def baseline_live():
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:args=[x.decode() for x in p.read_bytes().split(b'\0') if x]
  except (OSError,UnicodeDecodeError):continue
  if any(Path(x).name=='supervise_development32_baselines012.py' for x in args):return True
 return False
try:
 assert not status.exists();f=ROOT/'INTERACTION_CANDIDATE_DEVELOPMENT_FREEZE.json';plan=json.loads(f.read_text());write(status,{'status':'WAITING_VERIFIED_BASELINE_QUEUE','pid':os.getpid(),'freeze_sha256':sha(f)})
 while True:
  b=json.loads((ROOT/'DEVELOPMENT32_SUPERVISOR.json').read_text());assert not b['status'].startswith('FAILED'),b
  if b['status']=='COMPLETE_FROZEN_DEVELOPMENT32_GENERATION_NEW_CELLS':break
  assert baseline_live(),'Baseline queue missing/incomplete; no automatic restart';time.sleep(2)
 worker=HERE/'run_interaction_candidate012.py';mechanism=HERE/'reference_geometry_interaction012.py'
 for seed in plan['seeds']:
  assert sha(worker)==plan['worker_sha256'] and sha(mechanism)==plan['mechanism_sha256'];write(status,{'status':'RUNNING_FROZEN_INTERACTION_CANDIDATE','pid':os.getpid(),'seed':seed});children=[];logs=[]
  for rank in [0,1]:
   run=ROOT/f'development32_interaction_projection_seed{seed}_rank{rank}';assert not run.exists();log=(ROOT/f'{run.name}.log').open('w');logs.append(log);children.append(subprocess.Popen([sys.executable,str(worker),'--device',f'cuda:{rank}','--mode','interaction_projection','--count','32','--rank',str(rank),'--seed',str(seed),'--run-root',str(run)],cwd=HERE.parents[1],stdout=log,stderr=subprocess.STDOUT))
  for child in children:assert child.wait()==0,'Candidate worker failed; no automatic retry'
  for log in logs:log.close()
 write(status,{'status':'COMPLETE_INTERACTION_CANDIDATE_GENERATION','pid':os.getpid(),'scope':'Generation only; scoring and validity/novelty/second-backbone evaluation still required.'})
except Exception as exc:write(status,{'status':'FAILED_NO_AUTOMATIC_RETRY','pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
