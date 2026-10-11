"""Reproduce recorded training order/dropout; no claim of GPU reexecution."""
from pathlib import Path
import json,csv,math,hashlib,numpy as np
r=Path(__file__).resolve().parents[1];d=r/'data/same_v29_base';f=d/'formal_ddp_training';identity=json.loads((f/'RUN_IDENTITY.json').read_text());audit=json.loads((d/'TRAINING_COMPLETION_AUDIT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();uids=(r/'data/native_training_preflight/train_objects_native_valid.txt').read_text().splitlines();assert sha(r/'data/native_training_preflight/train_objects_native_valid.txt')==identity['eligible_uid_sha256'];assert identity['successful_optimizer_steps']==2000 and identity['latest_checkpoint_sha256']==audit['checkpoint_sha256'];logs=[]
for rank in [0,1]:
 rows=list(csv.DictReader((f/f'train_rank{rank}.csv').open()));logs.append(rows);assert len(rows)==2000 and sha(f/f'train_rank{rank}.csv')==audit['logs'][f'train_rank{rank}.csv'];rng=np.random.default_rng(42);drop=np.random.default_rng(4242+rank);order=rng.permutation(len(uids));epoch=0
 for step,x in enumerate(rows,1):
  position=2*(step-1)+rank
  while epoch<position//len(uids):order=rng.permutation(len(uids));epoch+=1
  assert int(x['step'])==step and x['uid']==uids[order[position%len(uids)]] and int(x['drop_condition'])==int(drop.random()<.1)
  assert all(math.isfinite(float(x[k])) for k in ['loss','noise_loss','ssim_loss','reg_loss','gradient_norm','gradient_scale']) and float(x['gradient_norm'])>0
 gate=json.loads((d/f'ddp_backward_gate_attempt02/BASE_AND_CONDITION_IDENTITY_rank{rank}.json').read_text());assert gate['status']=='PASS1680_BASE_TENSORS_AND_TWO_NATIVE_CONDITIONS'
for a,b in zip(*logs):assert a['gradient_norm']==b['gradient_norm']
base=json.loads((d/'BASE_OVERLAY_IDENTITY.json').read_text());assert base['status']=='PASS1680_V29_UNET_TENSORS_EXACT_FP32_EXPORT' and base==identity['base_overlay_identity']
print('PASS: all4000 recorded exposures, seeded order/dropout, gradient synchronization and same-base provenance; GPU execution not rerun')
