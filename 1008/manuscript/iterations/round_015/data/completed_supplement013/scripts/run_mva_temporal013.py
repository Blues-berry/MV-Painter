"""Existing fixed/early/middle/linear schedules; no new method or parameter search."""
import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np,torch
from PIL import Image
from revision_expansion_common import OUT,sha,write
from reference_geometry_interaction_mva012 import correct_multiview_interaction
ROOT=OUT/'iteration012_condition_interference'
def pixelhash(images):return hashlib.sha256(b''.join(np.asarray(x.convert('RGB')).tobytes() for x in images)).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--device',required=True);ap.add_argument('--rank',type=int,choices=[0,1],required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--run-root',type=Path,required=True);ap.add_argument('--count',type=int,default=100);a=ap.parse_args();assert 0<a.count<=100;run=a.run_root;assert not run.exists()
 from run_fresh_c_glb_method_matrix import gpu_snapshot
 gpu=gpu_snapshot(a.device);run.mkdir();freeze=json.loads(a.freeze.read_text());records=freeze['objects'][:a.count];device=torch.device(a.device);torch.cuda.set_device(device);torch.set_num_threads(4);source=Path(freeze['deployed_source_root']);sys.path.insert(0,str(source));from scripts.inference_ig2mv_sd import prepare_pipeline,run_pipeline
 for relative,digest in freeze['deployed_source_file_sha256'].items():assert sha(source/relative)==digest
 model=freeze['model_identities'];assert sha(model['adapter_path'])==model['adapter_sha256'];write(run/'PROTOCOL_FREEZE.json',{'uids':[x['object_uid'] for x in records],'seed':a.seed,'rank':a.rank,'steps':50,'cfg':3.,'resolution':512,'conditions':freeze['conditions'],'role':'Fixed GSO external objects with matched native-camera reference; separate input domain; no tuning or cross-domain pooling','helper_sha256':sha(Path(__file__).with_name('reference_geometry_interaction012.py'))});(run/'execution_source.py').write_bytes(Path(__file__).read_bytes());identity={'status':'RUNNING_MVADAPTER_NATIVE_GATE_AND_DEVELOPMENT','gpu':gpu,'seed':a.seed,'rank':a.rank};write(run/'RUN_IDENTITY.json',identity)
 try:
  pipe=prepare_pipeline(base_model=model['base_model_path'],vae_model=None,unet_model=None,lora_model=None,adapter_path=model['adapter_path'],scheduler='ddpm',num_views=6,device=a.device,dtype=torch.float16);pipe.unet.eval();active={'mode':'native','step':0};original=pipe.unet.forward;traces={}
  schedules={'fixed_low':lambda p:.75,'early_high':lambda p:1. if p<=15/49 else .75,'middle_high':lambda p:1. if 17/49<=p<=32/49 else .75,'generic_linear':lambda p:.75+.16*p,'constant_default':lambda p:1.}
  assert abs(sum(schedules['generic_linear'](j/49) for j in range(50))-41.5)<1e-10
  assert all(abs(sum(schedules[k](j/49) for j in range(50))-41.5)<1e-10 for k in ['early_high','middle_high'])
  def before(module,args,kw):
   cross=kw.get('cross_attention_kwargs') or {}
   if 'cache_hidden_states' in cross:return
   active['step']+=1
   if active.get('audit'):active['trace'].append([float(x.float().square().mean().sqrt()) for x in kw['down_intrablock_additional_residuals']])
   active['cpu_pre']=torch.get_rng_state();active['cuda_pre']=torch.cuda.get_rng_state(device)
  def after(module,args,kw,result):
   if 'cache_hidden_states' in (kw.get('cross_attention_kwargs') or {}) or active['mode'] in ['native','fixed_mean','late_high','fixed_low','early_high','middle_high','generic_linear','constant_default']:return
   cpu_post=torch.get_rng_state();cuda_post=torch.cuda.get_rng_state(device)
   try:
    torch.set_rng_state(active['cpu_pre']);torch.cuda.set_rng_state(active['cuda_pre'],device);clean=dict(kw);clean['down_intrablock_additional_residuals']=None;clean['cross_attention_kwargs']=dict(kw['cross_attention_kwargs']);bare=original(*args,**clean)[0];full=result[0];assert full.shape[0]==12 and torch.isfinite(bare).all()
   finally:torch.set_rng_state(cpu_post);torch.cuda.set_rng_state(cuda_post,device)
   if active['mode']=='observe':return
   if active['mode']=='interaction_projection':changed,_=correct_multiview_interaction(full,bare,3.)
   else:
    fu,fc=full.float().chunk(2);bu,bc=bare.float().chunk(2);g=(fu+3*(fc-fu))-(bu+3*(bc-bu));ref=bc-bu;dims=(0,1,2,3) if active['mode']=='grid_projection' else (1,2,3);coefficient=(g*ref).sum(dim=dims,keepdim=True).clamp(max=0)/ref.square().sum(dim=dims,keepdim=True).clamp_min(1e-12);delta=-coefficient*ref;changed=full+delta.to(full.dtype).repeat(2,1,1,1)
   assert torch.isfinite(changed).all();return (changed,)+tuple(result[1:])
  pre=pipe.unet.register_forward_pre_hook(before,with_kwargs=True);post=pipe.unet.register_forward_hook(after,with_kwargs=True)
  def execute(record,mode):
   active.update(mode=mode,step=0,audit=record['object_uid']==records[a.rank]['object_uid'],trace=[]);torch.manual_seed(a.seed);torch.cuda.manual_seed_all(a.seed)
   with torch.inference_mode():images,_,_,_=run_pipeline(pipe=pipe,mesh_path=record['mesh_path'],num_views=6,text='high quality',image=record['reference_image_path'],height=512,width=512,num_inference_steps=50,guidance_scale=3.,seed=a.seed,reference_conditioning_scale=1.,control_conditioning_scale=1.,geometry_scale_schedule=schedules.get(mode),device=a.device)
   assert active['step']==50 and len(images)==6
   if active['audit']:traces[mode]=active['trace'];write(run/'APPLIED_RESIDUAL_TRACE.json',traces)
   return images
  rows=[]
  try:
   first=records[a.rank];assert sha(first['mesh_path'])==first['mesh_sha256'] and sha(first['reference_image_path'])==first['reference_image_sha256'];native=execute(first,'native');constant=execute(first,'constant_default');assert pixelhash(native)==pixelhash(constant),'Constant-default path differs from native';baseline=ROOT/'gso_mva_external_attempt01'/f'matrix_seed{a.seed}_rank{a.rank}';saved=next(x for x in json.loads((baseline/'ROWS.json').read_text()) if x['uid']==first['object_uid'] and x['condition']=='native');assert pixelhash(native)==saved['pixel_sha256'],'Regenerated native differs from completed matrix';observed=execute(first,'observe');assert pixelhash(native)==pixelhash(observed),'Auxiliary geometry-removal observation changed native pixels';write(run/'NATIVE_OBSERVATION_IDENTITY_GATE.json',{'status':'PASS_EXACT_SIX_VIEW_NATIVE_PIXEL_IDENTITY','uid':first['object_uid'],'seed':a.seed,'native_pixel_sha256':pixelhash(native),'observed_pixel_sha256':pixelhash(observed),'scope':'Actual50-step inference with every-step auxiliary prediction; direct UNet.forward bypasses outer hooks and restores CPU/CUDA RNG.'})
   for i,record in enumerate(records):
    if i%2!=a.rank:continue
    assert sha(record['mesh_path'])==record['mesh_sha256'] and sha(record['reference_image_path'])==record['reference_image_sha256']
    for condition in freeze['conditions']:
     images=native if i==a.rank and condition=='native' else execute(record,condition)
     if i==a.rank:
      reference=np.asarray(traces['native']);current=np.asarray(traces[condition]);expected=np.asarray([schedules[condition](j/49) for j in range(50)])[:,None];valid=reference>1e-12;error=float(np.max(np.abs((current/reference)[valid]-np.broadcast_to(expected,current.shape)[valid])));assert error<.002,(condition,error);write(run/f'APPLIED_SCALE_GATE_{condition}.json',{'status':'PASS_APPLIED_RESIDUAL_RMS_RATIO','max_error':error,'expected_scale_sum':float(expected.sum()),'steps':50})
     folder=run/'predictions'/condition/record['object_uid'];folder.mkdir(parents=True)
     for j,im in enumerate(images):im.save(folder/f'view_{j:02d}.png')
     rows.append({'uid':record['object_uid'],'condition':condition,'seed':a.seed,'pixel_sha256':pixelhash(images),'output_files':[str(folder/f'view_{j:02d}.png') for j in range(6)]});write(run/'ROWS.json',rows);print('MVA_DEVELOPMENT',record['object_uid'],condition,flush=True)
  finally:pre.remove();post.remove()
  identity.update(status='COMPLETE_MVADAPTER_NATIVE_GATE_AND_DEVELOPMENT',rows=rows);write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:identity.update(status='FAILED_NO_AUTOMATIC_RETRY',error=f'{type(exc).__name__}: {exc}');write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
