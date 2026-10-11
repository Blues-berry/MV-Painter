"""Wait for the existing fixed training, audit it, then run frozen stage1 on free GPUs."""
import time,json,subprocess,sys,os,datetime
from pathlib import Path
from revision_expansion_common import OUT,write,sha
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];r=OUT/'iteration009_native_checkpoint_evaluation';formal=OUT/'iteration008_native_training_attempt02/formal_ddp_training';status=r/'SUPERVISOR_STATUS.json'
assert not status.exists();(r/'execution_supervisor_attempt02.py').write_bytes(Path(__file__).read_bytes());write(status,{'status':'WAITING_FOR_EXISTING_FIXED_TRAINING','pid':os.getpid(),'source_sha256':sha(Path(__file__)),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
try:
 while True:
  failures=list(formal.glob('FAILURE*'))
  if failures:raise RuntimeError('Existing training has failure ledger: '+','.join(str(x) for x in failures))
  d=json.loads((formal/'RUN_IDENTITY.json').read_text())
  if d['status']=='COMPLETE_NATIVE512_DDP_TRAINING':break
  # Inspect live processes instead of interpreting a stale identity as a live job.
  live=[]
  for cmdfile in Path('/proc').glob('[0-9]*/cmdline'):
   try:argv=[x.decode() for x in cmdfile.read_bytes().split(b'\0') if x]
   except (OSError,UnicodeDecodeError):continue
   if argv and Path(argv[0]).name.startswith('python') and any(Path(x).name=='train_native_ddp008.py' for x in argv[1:]):live.append(cmdfile.parent.name)
  if not live:raise RuntimeError('Training worker missing before complete state; do not restart automatically')
  time.sleep(2)
 subprocess.run([sys.executable,str(HERE/'verify_native_training_completion009.py')],cwd=ROOT,check=True)
 while True:
  apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip()
  if not apps:break
  time.sleep(2)
 write(status,{'status':'RUNNING_FROZEN_NATIVE_STAGE1','pid':os.getpid(),'checkpoint_sha256':d['latest_checkpoint_sha256'],'scope':'all50objects x disabled/native_unset, not final complete eight-condition experiment'})
 children=[];handles=[]
 for rank in [0,1]:
  log=(r/f'stage1_rank{rank}.log').open('w');handles.append(log);cmd=[sys.executable,str(HERE/'run_native_checkpoint_matrix009.py'),'--rank',str(rank),'--device',f'cuda:{rank}','--conditions','disabled,native_unset'];children.append(subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT))
 codes=[p.wait() for p in children]
 for h in handles:h.close()
 assert codes==[0,0],codes
 write(status,{'status':'SCORING_FROZEN_NATIVE_STAGE1','pid':os.getpid()})
 with (r/'stage1_scoring.log').open('w') as log:subprocess.run([sys.executable,str(HERE/'score_native_checkpoint009.py'),'--conditions','disabled,native_unset','--device','cuda:0'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 write(status,{'status':'COMPLETE_FROZEN_NATIVE_STAGE1','pid':os.getpid(),'scope':'50x2 native checkpoint deployment test; remaining planned conditions pending scientific review','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
except Exception as exc:write(status,{'status':'FAILED_WAIT_OR_EVALUATION','pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
