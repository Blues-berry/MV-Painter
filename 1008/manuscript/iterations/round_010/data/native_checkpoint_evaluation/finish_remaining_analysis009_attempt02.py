"""Complete scoring and both declared comparison families after verified GPU queues."""
import os,json,time,subprocess,sys,numpy as np
from pathlib import Path
from revision_expansion_common import OUT,sha,write
here=Path(__file__).resolve().parent;root=here.parents[1];r=OUT/'iteration009_native_checkpoint_evaluation';status=r/'FINAL_ANALYSIS_SUPERVISOR_ATTEMPT02.json';assert not status.exists();write(status,{'status':'WAITING_FOR_EXISTING_REMAINING_AND_V29_QUEUES','pid':os.getpid(),'source_sha256':sha(Path(__file__))});(r/'execution_final_analysis_supervisor_attempt02.py').write_bytes(Path(__file__).read_bytes())
try:
 while True:
  identities=[r/'v29_frozen_fresh50_rank0_attempt02/RUN_IDENTITY.json',r/'v29_frozen_fresh50_rank1/RUN_IDENTITY.json']
  states=[json.loads(p.read_text()) if p.exists() else None for p in identities]
  if any(d and d['status'].startswith('FAILED') for d in states):raise RuntimeError('Recorded v29 retry failed; no automatic restart')
  if all(d and d['status']=='COMPLETE_V29_FROZEN_FIFTY_OBJECT_RANK' for d in states):break
  live=False
  for cmd in Path('/proc').glob('[0-9]*/cmdline'):
   try:argv=[x.decode() for x in cmd.read_bytes().split(b'\0') if x]
   except (OSError,UnicodeDecodeError):continue
   if argv and Path(argv[0]).name.startswith('python') and any(Path(x).name=='run_v29_native_probe009.py' for x in argv[1:]):live=True
  if not live:raise RuntimeError('v29 worker missing before terminal state; no automatic restart')
  time.sleep(2)
 conditions=['native_gfl','native_gfh','native_gc3','gen_linear'];expected={(u,c) for u in (r/'objects.txt').read_text().splitlines() for c in conditions};actual=[]
 for rank in [0,1]:
  d=json.loads((r/f'rank{rank}_native_gfl_native_gfh_native_gc3_gen_linear/RUN_IDENTITY.json').read_text());assert d['status']=='COMPLETE_NATIVE_CHECKPOINT_MATRIX_STAGE';actual.extend((x['uid'],x['condition']) for x in d['rows'])
 assert len(actual)==200 and set(actual)==expected
 baseline=[]
 for rank in [0,1]:
  d=json.loads((r/('v29_frozen_fresh50_rank0_attempt02' if rank==0 else 'v29_frozen_fresh50_rank1')/'RUN_IDENTITY.json').read_text());assert d['status']=='COMPLETE_V29_FROZEN_FIFTY_OBJECT_RANK';baseline.extend((x['uid'],x['condition']) for x in d['rows'])
 assert len(baseline)==50 and set(baseline)=={(u,'v29_full_controlnet') for u in (r/'objects.txt').read_text().splitlines()}
 write(status,{'status':'SCORING_ALL_COMPLETED_REMAINING_AND_V29_OUTPUTS','pid':os.getpid()});children=[];handles=[]
 for device,methods,label in [('cuda:0',','.join(conditions),'remaining'),('cuda:1','v29_full_controlnet','v29')]:
  target=r/f"scores_{methods.replace(',', '_')}.json"
  if target.exists():assert json.loads(target.read_text())['status']=='COMPLETE_NATIVE_SLOT_SCORING';continue
  already=False
  for cmd in Path('/proc').glob('[0-9]*/cmdline'):
   try:argv=[x.decode() for x in cmd.read_bytes().split(b'\0') if x]
   except (OSError,UnicodeDecodeError):continue
   if argv and Path(argv[0]).name.startswith('python') and any(Path(x).name=='score_native_checkpoint009.py' for x in argv[1:]) and methods in argv:already=True
  if already:
   while not target.exists():time.sleep(2)
   assert json.loads(target.read_text())['status']=='COMPLETE_NATIVE_SLOT_SCORING';continue
  h=(r/f'{label}_final_scoring_attempt02.log').open('w');handles.append(h);children.append(subprocess.Popen([sys.executable,str(here/'score_native_checkpoint009.py'),'--conditions',methods,'--device',device],cwd=root,stdout=h,stderr=subprocess.STDOUT))
 codes=[p.wait() for p in children]
 for h in handles:h.close()
 assert all(code==0 for code in codes),codes
 subprocess.run([sys.executable,str(here/'analyze_native_checkpoint009.py')],cwd=root,check=True)
 native=json.loads((r/'scores_disabled_native_unset.json').read_text());v29=json.loads((r/'scores_v29_full_controlnet.json').read_text());a={x['uid']:x for x in native['rows'] if x['condition']=='native_unset'};b={x['uid']:x for x in v29['rows']};uids=(r/'objects.txt').read_text().splitlines();assert set(a)==set(b)==set(uids);tests=[]
 for metric in ['fg_psnr','fg_ssim','fg_lpips','ciede2000']:
  delta=np.array([a[u]['nonreference_mean'][metric]-b[u]['nonreference_mean'][metric] for u in uids]);rng=np.random.default_rng(20261010);boot=np.mean(delta[rng.integers(0,50,(20000,50))],axis=1);observed=abs(float(delta.mean()));count=0
  for start in range(0,200000,4000):count+=int((np.abs(np.mean(rng.choice([-1.,1.],size=(4000,50))*delta,axis=1))>=observed-1e-15).sum())
  tests.append({'metric':metric,'a':'native_unset','b':'v29_full_controlnet','difference_a_minus_b':float(delta.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'signflip_p':(count+1)/200001,'object_differences':dict(zip(uids,delta.tolist()))})
 order=sorted(range(4),key=lambda i:tests[i]['signflip_p']);prev=0.
 for rank,i in enumerate(order):prev=max(prev,min(1.,(4-rank)*tests[i]['signflip_p']));tests[i]['holm_p']=prev
 write(r/'V29_DEPLOYMENT_COMPARISON.json',{'status':'COMPLETE_FROZEN_V29_EXPLORATORY_FAMILY','tests':tests,'n_objects':50,'resampling_unit':'object; five nonreference-view means','family':'Holm4, separately frozen deployment comparison','scope':'differentUNetweights plus geometry branches; not isolated architecture causality or unmodified CLI','baseline_freeze_sha256':sha(r/'V29_FULL_BASELINE_FREEZE.json'),'source_sha256':sha(Path(__file__))})
 write(status,{'status':'COMPLETE_ALL_PREDECLARED_NATIVE_AND_V29_ANALYSIS','pid':os.getpid(),'main_analysis_sha256':sha(r/'PAIRED_NATIVE_ANALYSIS.json'),'v29_analysis_sha256':sha(r/'V29_DEPLOYMENT_COMPARISON.json')})
except Exception as exc:write(status,{'status':'FAILED_FINAL_WAIT_OR_ANALYSIS','pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
