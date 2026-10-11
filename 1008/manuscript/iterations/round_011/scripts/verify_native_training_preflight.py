"""Integrity/cohort checks of recorded GPU gates; does not rerun GPU training."""
from pathlib import Path
import json,hashlib,csv,math
r=Path(__file__).resolve().parents[1];d=r/'data/native_training_preflight';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger=json.loads((d/'PACKAGED_SHA256.json').read_text())
for name,h in ledger.items():assert sha(d/name)==h,name
cache=json.loads((d/'conditioning_cache_complete_inputs_attempt03/RUN_IDENTITY.json').read_text());assert cache['status']=='COMPLETE_NATIVE_CONDITIONING_CACHE_WITH_INPUT_LEDGER'
uids=(d/'train_objects_native_valid.txt').read_text().splitlines();candidate=(d/'train_objects_1112.txt').read_text().splitlines();failed={x['uid'] for x in cache['input_failures']};assert len(uids)==len(set(uids))==1090 and len(failed)==22;assert set(uids).isdisjoint(failed) and set(uids)|failed==set(candidate)
assert [x['uid'] for x in cache['rows']]==uids and sha(d/'train_objects_native_valid.txt')==cache['eligible_uid_sha256']
fresh=set((r/'data/training_audit/fresh_c_objects.txt').read_text().splitlines());assert not set(uids)&fresh
for x in cache['rows']:assert x['target_reference_max_error']<1e-6
p=d/'preflight';z=json.loads((p/'ZERO_IDENTITY.json').read_text());assert len(z)==2
for x in z:assert x['rgb_pixels_identical'] and sha(p/f"zero_scale_{x['uid']}.png")==x['output_sha256']
c=json.loads((p/'CROSS_GPU_CONDITIONING_IDENTITY.json').read_text());assert len(c)==2 and all(x['gpu0_gpu1_payload_identical'] for x in c)
g=json.loads((d/'preflight_fp32_regularization_attempt03/RUN_IDENTITY.json').read_text());assert g['status']=='PASS_NATIVE512_TRAINING_PREFLIGHT';assert g['smoke_weights_discarded'];assert all(g['before_weights'][k]!=g['after_weights'][k] for k in g['before_weights'])
for x in g['backward_gates']:assert x['adapter_grad_norm']>0 and x['encoder_grad_norm']>0 and math.isfinite(x['loss']) and x['components']['train/reg_loss']>0
assert {x['drop_condition'] for x in g['backward_gates']}=={True,False}
gate=json.loads((d/'ddp_backward_gate/RUN_IDENTITY.json').read_text());assert gate['status']=='PASS_DDP_BACKWARD_GATE' and gate['successful_optimizer_steps']==2 and gate['active_trainable_parameters']==2201760
rows=[list(csv.DictReader((d/'ddp_backward_gate'/f'train_rank{i}.csv').open())) for i in range(2)]
for i in range(2):
 assert len(rows[i])==2
 for x in rows[i]:assert all(math.isfinite(float(x[k])) for k in ['loss','reg_loss','gradient_norm']) and float(x['gradient_norm'])>0
for a,b in zip(*rows):assert a['gradient_norm']==b['gradient_norm'] and a['drop_condition']=='0' and b['drop_condition']=='1'
print('PASS: packaged transcript integrity, 1090 strict inputs, zero Fresh overlap, native identity and finite synchronized backward records. GPU execution is not rerun.')
