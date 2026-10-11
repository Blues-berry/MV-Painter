"""Run the second-backbone32x4x3 matrix after the current frozen GPU queues."""
import json,os,sys,time,subprocess
from pathlib import Path
from revision_expansion_common import OUT,sha,write
HERE=Path(__file__).resolve().parent;ROOT=OUT/'iteration012_condition_interference';status=ROOT/'MVADAPTER_DEVELOPMENT_SUPERVISOR.json'
def predecessor_live():
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:a=[x.decode() for x in p.read_bytes().split(b'\0') if x]
  except (OSError,UnicodeDecodeError):continue
  if any(Path(x).name=='supervise_interaction_candidate012.py' for x in a):return True
 return False
try:
 assert not status.exists();freeze=ROOT/'MVADAPTER_DEVELOPMENT32_FREEZE.json';plan=json.loads(freeze.read_text());write(status,{'status':'WAITING_VERIFIED_FIRST_BACKBONE_QUEUE','pid':os.getpid(),'freeze_sha256':sha(freeze)})
 while True:
  d=json.loads((ROOT/'INTERACTION_CANDIDATE_SUPERVISOR.json').read_text());assert not d['status'].startswith('FAILED'),d
  if d['status']=='COMPLETE_INTERACTION_CANDIDATE_GENERATION':break
  assert predecessor_live(),'Predecessor queue missing/incomplete; no automatic restart';time.sleep(2)
 worker=HERE/'run_mvadapter_interaction012.py'
 for seed in plan['seeds']:
  assert sha(worker)==plan['worker_sha256'];write(status,{'status':'RUNNING_SECOND_BACKBONE_NATIVE_GATES_AND_DEVELOPMENT','seed':seed,'pid':os.getpid()});children=[];logs=[]
  for rank in [0,1]:
   log=(ROOT/f'mvadapter_development32_seed{seed}_rank{rank}.log').open('w');logs.append(log);children.append(subprocess.Popen([sys.executable,str(worker),'--device',f'cuda:{rank}','--rank',str(rank),'--seed',str(seed),'--count','32'],cwd=HERE.parents[1],stdout=log,stderr=subprocess.STDOUT))
  for child in children:assert child.wait()==0,'Second-backbone gate or generation failed; preserve evidence, no automatic retry'
  for log in logs:log.close()
 write(status,{'status':'COMPLETE_SECOND_BACKBONE_DEVELOPMENT_GENERATION','pid':os.getpid(),'scope':'Generation only. Scoring and actual stable superiority/novelty validation remain.'})
except Exception as exc:write(status,{'status':'FAILED_NO_AUTOMATIC_RETRY','pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
