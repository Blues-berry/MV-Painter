"""Observe conditional interactions on an unchanged full-v29 development trajectory."""
import argparse,json,hashlib
from native_training_protocol008 import *
from run_v29_native_probe009 import controls,MVPainter_Pipeline,ControlNetModel_Union
from safetensors import safe_open
from reference_geometry_interaction012 import correct_interaction
R9=OUT/'iteration009_native_checkpoint_evaluation'
R10=OUT/'iteration010_same_v29_base'
R12=OUT/'iteration012_condition_interference'

def pixels(im):return hashlib.sha256(np.asarray(im.convert('RGB')).tobytes()).hexdigest()

def describe(g,a):
 g,a=g.float(),a.float();dot=(g*a).sum();gg=g.square().sum();aa=a.square().sum()
 return {'geometry_norm':float(gg.sqrt()),'reference_condition_difference_norm':float(aa.sqrt()),'dot':float(dot),'cosine':float(dot/(gg*aa).sqrt().clamp_min(1e-12)),'negative_dot':bool(dot<0),'opposed_parallel_energy_fraction':float(dot.square()/(gg*aa).clamp_min(1e-12)) if dot<0 else 0.}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--device',default='cuda:0');ap.add_argument('--mode',choices=['observe','native','interaction_projection'],default='interaction_projection');ap.add_argument('--count',type=int,default=2);ap.add_argument('--rank',type=int,choices=[0,1]);ap.add_argument('--seed',type=int,default=42);ap.add_argument('--start-index',type=int,default=0);ap.add_argument('--run-root',type=Path);a=ap.parse_args();assert a.count>0 and 0<=a.start_index<a.count;run=a.run_root if a.run_root else R12/('full_v29_development_attempt01' if a.mode=='observe' and a.rank is None else f'{a.mode}_development_rank{a.rank}_attempt01');assert not run.exists();gpu=base.gpu_snapshot(a.device);run.mkdir(parents=True);device=torch.device(a.device);torch.cuda.set_device(device);torch.set_num_threads(4)
 freeze=json.loads((R9/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());uids=freeze['uids'][:a.count];write(run/'PROTOCOL_FREEZE.json',{'uids':uids,'observed_steps':[0,24,49] if a.mode=='observe' else list(range(50)),'steps':50,'seed':a.seed,'start_index':a.start_index,'cfg':2.,'mode':a.mode,'rank':a.rank,'role':'previously evaluated development objects; factorial interaction development candidate; novelty and superiority not established','rng_policy':'auxiliary no-control call receives pre-main CPU/CUDA RNG state; restore post-main states before trajectory continues','comparison':'full controlled CFG noise versus bare CFG noise at the identical native latent; reference difference from bare positive-minus-negative conditional predictions is not pure appearance gradient'});(run/'execution_source.py').write_bytes(Path(__file__).read_bytes());(run/'reference_geometry_interaction012.py').write_bytes(Path(__file__).with_name('reference_geometry_interaction012.py').read_bytes())
 identity={'status':'RUNNING_CONDITION_INTERACTION_DIAGNOSTIC','gpu':gpu,'source_sha256':sha(Path(__file__)),'uids':uids};write(run/'RUN_IDENTITY.json',identity)
 try:
  config=OmegaConf.load(R10/'formal_ddp_training/native512_config.yaml');dataset=dataset_for(config,R9/'objects.txt',base.DATA_ROOT);audit=json.loads((R9/'controlnet_asset_audit_attempt02/CONTROLNET_ASSET_AUDIT.json').read_text());assert sha(audit['asset_path'])==audit['asset_sha256'];pipe=MVPainter_Pipeline.from_pretrained(str(base.load_launcher_helpers().BASE_MODEL),torch_dtype=torch.float16,use_safetensors=True);pipe.add_controlnet(ControlNetModel_Union.from_unet(pipe.unet).to(dtype=torch.float16),conditioning_scale=1.)
  with safe_open(audit['asset_path'],framework='pt',device='cpu') as f:
   state=pipe.unet.state_dict();assert set(state)==set(f.keys())
   with torch.no_grad():
    for k,t in state.items():x=f.get_tensor(k);assert t.shape==x.shape;t.copy_(x.to(t.dtype))
  del state,x;pipe.to(device);pipe.unet.eval();full=pipe.unet;bare=full.unet;rows=[];active={}
  def before(module,args,kw):
   active['step']+=1
   if a.mode!='observe' or active['step'] in [0,24,49]:active['cpu_pre']=torch.get_rng_state();active['cuda_pre']=torch.cuda.get_rng_state(device)
  def after(module,args,kw,result):
   step=active['step']
   if a.mode=='native' or (a.mode=='observe' and step not in [0,24,49]):return
   cpu_post=torch.get_rng_state();cuda_post=torch.cuda.get_rng_state(device)
   try:
    torch.set_rng_state(active['cpu_pre']);torch.cuda.set_rng_state(active['cuda_pre'],device)
    clean=dict(kw);clean['cross_attention_kwargs']={'cond_lat':kw['cross_attention_kwargs']['cond_lat']};clean['added_cond_kwargs']={k:v for k,v in kw['added_cond_kwargs'].items() if k!='control_type'}
    other=bare(*args,**clean)[0];fu,fc=result[0].chunk(2);bu,bc=other.chunk(2);g=(fu+2*(fc-fu))-(bu+2*(bc-bu));ref=bc-bu
    # Each view remains a separate spatial diagnostic, not an independent subject.
    h,w=g.shape[-2:];assert h%3==0 and w%2==0
    row={'uid':active['uid'],'step':step,'whole_grid':describe(g,ref),'views':[describe(g[:,:,i*h//3:(i+1)*h//3,j*w//2:(j+1)*w//2],ref[:,:,i*h//3:(i+1)*h//3,j*w//2:(j+1)*w//2]) for i in range(3) for j in range(2)],'native_prediction_hash':tensor_hash(result[0]),'bare_prediction_hash':tensor_hash(other)};rows.append(row);write(run/'INTERACTION_ROWS.json',rows)
   finally:torch.set_rng_state(cpu_post);torch.cuda.set_rng_state(cuda_post,device)
   assert torch.equal(torch.get_rng_state(),cpu_post) and torch.equal(torch.cuda.get_rng_state(device),cuda_post)
   if a.mode!='observe':
    changed,parts=correct_interaction(result[0],other,guidance_scale=2.);assert torch.isfinite(changed).all();return (changed,)+tuple(result[1:])
  pre=full.register_forward_pre_hook(before,with_kwargs=True);post=full.register_forward_hook(after,with_kwargs=True)
  outputs=[]
  try:
   for i,uid in enumerate(uids):
    if i<a.start_index or (a.rank is not None and i%2!=a.rank):continue
    assert Path(dataset.paths[i]).name==uid;source=source_for(dataset,i);normal,depth,meta=controls(Path(dataset.paths[i]),source);active.update(uid=uid,step=-1);seed_all(a.seed)
    with torch.no_grad():result=pipe(Image.open(source).convert('RGBA'),depth_image=normal,depth_image_2=depth,num_inference_steps=50,guidance_scale=2.,generator=torch.Generator(device=device).manual_seed(a.seed),output_type='pil')
    expected=R9/'predictions/v29_full_controlnet'/f'{uid}.png';actual=pixels(result[0]);assert active['step']==49
    if a.mode=='observe' or (a.mode=='native' and a.seed==42):assert actual==pixels(Image.open(expected)),'Diagnostic altered the native trajectory'
    result[0].save(run/f'{uid}.png');outputs.append({'uid':uid,'pixel_sha256':actual,'expected_pixel_sha256':pixels(Image.open(expected)) if a.seed==42 else None,'source_sha256':sha(source),'controls':meta});print('COMPLETED',a.mode,uid,flush=True)
  finally:pre.remove();post.remove()
  assert len(rows)==len(outputs)*(0 if a.mode=='native' else 3 if a.mode=='observe' else 50);identity.update(status='COMPLETE_PIXEL_IDENTICAL_CONDITION_INTERACTION_DIAGNOSTIC' if a.mode=='observe' else 'COMPLETE_NATIVE_DEVELOPMENT_BASELINE' if a.mode=='native' else 'COMPLETE_INTERACTION_CANDIDATE_DEVELOPMENT',mode=a.mode,outputs=outputs,observations=len(rows));write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:identity.update(status='FAILED_NO_AUTOMATIC_RETRY',error=f'{type(exc).__name__}: {exc}');write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
