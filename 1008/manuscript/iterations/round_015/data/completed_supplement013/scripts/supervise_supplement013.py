"""Persistent existing-method validation chain; stop on failure, never select by quality."""
import json,os,subprocess,sys,time
from pathlib import Path
from revision_expansion_common import OUT,sha,write
H=Path(__file__).resolve().parent;R=OUT/'iteration012_condition_interference';RUN=R/'gso_temporal_complete013';BASE=R/'gso_bake_closure_attempt02_calibrated';EXTRA=R/'gso_bake_temporal013'

def launch(args,log):
 stream=log.open('w');process=subprocess.Popen([sys.executable,*map(str,args)],cwd=H,stdout=stream,stderr=subprocess.STDOUT);return process,stream

def join(children):
 codes=[p.wait() for p,_ in children]
 for _,s in children:s.close()
 assert all(x==0 for x in codes),f'Children failed: {codes}'

def freeze_check(plan):
 assert all(sha(Path(k))==v for k,v in plan['runtime_sources'].items()),'Runtime source changed'
 assert sha(RUN/'MATRIX_FREEZE.json')==plan['matrix_sha256']

def main():
 plan=json.loads((RUN/'PROTOCOL_FREEZE.json').read_text());freeze_check(plan);assert not (RUN/'STATUS.json').exists();write(RUN/'STATUS.json',{'status':'WAITING_CALIBRATED20_BAKE_TO_RELEASE_GPUS','pid':os.getpid()})
 while True:
  completed=[]
  for rank in [0,1]:
   f=BASE/f'rank{rank}/STATUS.json';state=subprocess.check_output(['systemctl','--user','show',f'cg-round013-gso-bake-rank{rank}.service','-p','ActiveState','--value'],text=True).strip()
   if f.exists():assert json.loads(f.read_text())['status']=='COMPLETE_BAKED_UNSEEN_EVALUATION';completed.append(state=='inactive')
   else:assert state in ['active','activating'],f'Bake rank{rank} exited without complete';completed.append(False)
  if all(completed):break
  time.sleep(10)
 oldrows=[];new={}
 for rank in [0,1]:
  oldrows+=json.loads((R/f'gso_bake_closure_attempt01/rank{rank}/OBJECT_METRICS.json').read_text())
  rows=json.loads((BASE/f'rank{rank}/OBJECT_METRICS.json').read_text());assert len(rows)==250
  for row in rows:new[row['uid'],row['seed'],row['condition']]=row
 for old in oldrows:
  row=new[old['uid'],old['seed'],old['condition']];assert old['glb_sha256']==row['glb_sha256'] and old['mean_unseen']==row['mean_unseen']
 write(BASE/'REPRODUCED_ORIGINAL15.json',{'status':'PASS_ALL375_EXISTING_HASHES_AND_METRICS','rows':len(oldrows)})
 write(BASE/'STATUS.json',{'status':'COMPLETE20_REVISED_CALIBRATION_BAKES','cells':500,'protocol_addendum':'PosthocGT-only diagnosis, unchanged projection; oldrawUV failure preserved'})
 # Execute actual native/default identity and scalar-injection gates before full1200.
 write(RUN/'STATUS.json',{'status':'RUNNING_ACTUAL_TEMPORAL_PREFLIGHT','pid':os.getpid()});children=[]
 for rank in [0,1]:children.append(launch([H/'run_mva_temporal013.py','--freeze',RUN/'MATRIX_FREEZE.json','--run-root',RUN/f'pilot_seed42_rank{rank}','--rank',rank,'--seed',42,'--count',2,'--device',f'cuda:{rank}'],RUN/f'pilot_rank{rank}.log'))
 join(children);freeze_check(plan)
 for rank in [0,1]:
  for c in plan['new_conditions']:assert json.loads((RUN/f'pilot_seed42_rank{rank}/APPLIED_SCALE_GATE_{c}.json').read_text())['status']=='PASS_APPLIED_RESIDUAL_RMS_RATIO'
 for seed in plan['seeds']:
  write(RUN/'STATUS.json',{'status':'RUNNING_FIXED_PROFILE_GENERATION','pid':os.getpid(),'seed':seed,'planned_new_cells':1200});children=[]
  for rank in [0,1]:children.append(launch([H/'run_mva_temporal013.py','--freeze',RUN/'MATRIX_FREEZE.json','--run-root',RUN/f'matrix_seed{seed}_rank{rank}','--rank',rank,'--seed',seed,'--device',f'cuda:{rank}'],RUN/f'generate_seed{seed}_rank{rank}.log'))
  join(children);freeze_check(plan)
  for rank in [0,1]:assert len(json.loads((RUN/f'matrix_seed{seed}_rank{rank}/ROWS.json').read_text()))==200
 write(RUN/'STATUS.json',{'status':'RUNNING_FROZEN_SCORING','pid':os.getpid()});children=[]
 for gpu,seed in enumerate(plan['seeds'][:2]):children.append(launch([H/'score_mva_external012.py','--freeze',RUN/'MATRIX_FREEZE.json','--run-prefix',RUN/'matrix','--seeds',seed,'--device',f'cuda:{gpu}','--out',RUN/f'scores_seed{seed}'],RUN/f'score_seed{seed}.log'))
 join(children);freeze_check(plan)
 # Independent final scoring onGPU0 and remaining method baking onGPU1.
 seed=plan['seeds'][2];score=launch([H/'score_mva_external012.py','--freeze',RUN/'MATRIX_FREEZE.json','--run-prefix',RUN/'matrix','--seeds',seed,'--device','cuda:0','--out',RUN/f'scores_seed{seed}'],RUN/f'score_seed{seed}.log')
 def bake(rank):return launch([H/'run_gso_mva_bakes013.py','--plan',EXTRA/'PROTOCOL_FREEZE.json','--out',EXTRA/f'rank{rank}','--rank',rank,'--device',f'cuda:{rank}','--additional-rows-prefix',RUN/'matrix'],RUN/f'additional_bake_rank{rank}.log')
 rank1=bake(1);join([score]);rank0=bake(0);write(RUN/'STATUS.json',{'status':'RUNNING_EXISTING_SCHEDULE_BAKES','pid':os.getpid(),'planned_total_bakes':740});join([rank0,rank1]);freeze_check(plan)
 child=launch([H/'analyze_gso_supplement013.py','--temporal-root',RUN,'--bake-root',BASE,'--extra-bake-root',EXTRA,'--out',RUN/'analysis'],RUN/'analysis.log');join([child]);freeze_check(plan)
 write(RUN/'STATUS.json',{'status':'COMPLETE_SUPPLEMENTARY_EXPERIMENTS_AND_ANALYSIS','pid':os.getpid(),'new_generated_cells':1200,'total_generated_cells':3600,'total_bakes':740,'analysis':str(RUN/'analysis')})
 child=launch([H/'deliver_supplement013.py','--temporal-root',RUN,'--bake-root',BASE,'--extra-bake-root',EXTRA,'--paper-round','/4T/CXY/MV-Painter-cg-revision-20261010/1008/manuscript/iterations/round_013'],RUN/'delivery.log');join([child]);freeze_check(plan)
 write(RUN/'STATUS.json',{'status':'COMPLETE_SUPPLEMENTARY_EXPERIMENTS_ANALYSIS_AND_REVIEW_DELIVERY','pid':os.getpid(),'total_generated_cells':3600,'total_bakes':740,'no_new_algorithm':True,'analysis':str(RUN/'analysis'),'delivery':str(RUN/'delivery')})
if __name__=='__main__':
 try:main()
 except Exception as e:write(RUN/'STATUS.json',{'status':'FAILED_NO_AUTOMATIC_RETRY','pid':os.getpid(),'error':f'{type(e).__name__}: {e}'});raise
