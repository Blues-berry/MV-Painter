"""Audit the complete fixed-step training, including data/dropout and actual weights."""
import json,csv,math,numpy as np,torch
from pathlib import Path
from revision_expansion_common import OUT,sha,write
r=OUT/'iteration008_native_training_attempt02';formal=r/'formal_ddp_training';identity=json.loads((formal/'RUN_IDENTITY.json').read_text());assert identity['status']=='COMPLETE_NATIVE512_DDP_TRAINING' and identity['successful_optimizer_steps']==2000
uids=(r/'train_objects_native_valid.txt').read_text().splitlines();assert len(uids)==1090 and sha(r/'train_objects_native_valid.txt')==identity['eligible_uid_sha256'];logs=[list(csv.DictReader((formal/f'train_rank{i}.csv').open())) for i in range(2)];counts={u:0 for u in uids};summaries=[]
for rank,rows in enumerate(logs):
 assert len(rows)==2000 and [int(x['step']) for x in rows]==list(range(1,2001));order_rng=np.random.default_rng(42);drop_rng=np.random.default_rng(4242+rank);order=order_rng.permutation(len(uids));epoch=0
 for step,x in enumerate(rows,1):
  position=2*(step-1)+rank
  while epoch<position//len(uids):order=order_rng.permutation(len(uids));epoch+=1
  assert x['uid']==uids[int(order[position%len(uids)])] and int(x['rank'])==rank;assert int(x['drop_condition'])==int(drop_rng.random()<.1);counts[x['uid']]+=1
  assert 0<=int(x['timestep'])<1000
  assert all(math.isfinite(float(x[k])) for k in ['loss','noise_loss','ssim_loss','reg_loss','gradient_norm','gradient_scale','elapsed_seconds','peak_allocated_bytes']);assert float(x['gradient_norm'])>0 and float(x['gradient_scale'])>=1024
 summaries.append({'rank':rank,'steps':len(rows),'drop_count':sum(int(x['drop_condition']) for x in rows),'drop_fraction':np.mean([int(x['drop_condition']) for x in rows]),'peak_allocated_bytes':max(float(x['peak_allocated_bytes']) for x in rows),'elapsed_seconds':float(rows[-1]['elapsed_seconds'])})
for a,b in zip(*logs):assert a['gradient_norm']==b['gradient_norm'] and a['gradient_scale']==b['gradient_scale']
assert sum(counts.values())==4000 and set(counts.values())=={3,4} and not list(formal.glob('FAILURE*'))
checkpoint=formal/'geotex_step2000.pt';assert sha(checkpoint)==identity['latest_checkpoint_sha256'];state=torch.load(checkpoint,map_location='cpu',weights_only=False);assert state['step']==2000
for name in ['adapters','encoder']:assert isinstance(state[name],dict) and all(torch.isfinite(t).all() for t in state[name].values())
steps={int(v['step'].item()) for v in state['optimizer']['state'].values()};assert steps=={2000};assert len(state['optimizer']['state'])==len(state['optimizer']['param_groups'][0]['params'])
for step in [500,1000,1500,2000]:
 assert (formal/f'geotex_step{step}.pt').exists()
 for rank in [0,1]:assert (formal/f'rng_step{step}_rank{rank}.pt').exists()
write(OUT/'iteration009_native_checkpoint_evaluation/TRAINING_COMPLETION_AUDIT.json',{'status':'PASS_COMPLETE_FIXED2000_NATIVE512_TRAINING','checkpoint_path':str(checkpoint),'checkpoint_sha256':sha(checkpoint),'formal_identity_sha256':sha(formal/'RUN_IDENTITY.json'),'logs':{f'train_rank{i}.csv':sha(formal/f'train_rank{i}.csv') for i in range(2)},'rank_summaries':summaries,'training_uid_count':len(uids),'total_object_exposures':4000,'exposure_histogram':{str(k):sum(v==k for v in counts.values()) for k in [3,4]},'exact_seeded_order_and_dropout_verified':True,'synchronized_gradient_norms_verified':True,'optimizer_parameter_steps':list(steps),'optimizer_parameter_tensors':len(state['optimizer']['state']),'active_trainable_parameter_count':identity['active_trainable_parameters'],'finite_checkpoint_tensors_verified':True,'source_sha256':sha(Path(__file__)),'scope':'training completion and numerical validity; no quality benefit or exact historical reproduction'});print('PASS2000 dual-rank steps,4000 exposures, exact dropout/order, synchronized gradients and finite finalweights')
