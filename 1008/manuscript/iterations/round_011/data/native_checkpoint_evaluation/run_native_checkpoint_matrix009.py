"""Evaluate the preselected step2000 checkpoint in the unchanged native loop."""
import os,argparse,json,time,importlib.util
from native_training_protocol008 import *
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
import geotex.eval_exploration as ee
R9=OUT/'iteration009_native_checkpoint_evaluation'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rank',type=int,choices=[0,1],required=True);ap.add_argument('--device',required=True);ap.add_argument('--attempt',type=int,default=1);ap.add_argument('--conditions',default='disabled,native_unset');args=ap.parse_args();conditions=args.conditions.split(',')
 cohort=json.loads((R9/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());assert set(conditions)<=set(cohort['conditions'])
 formal=RUN/'formal_ddp_training';training=json.loads((formal/'RUN_IDENTITY.json').read_text());assert training['status']=='COMPLETE_NATIVE512_DDP_TRAINING' and training['successful_optimizer_steps']==2000;checkpoint=formal/'geotex_step2000.pt';assert sha(checkpoint)==training['latest_checkpoint_sha256']
 gpu=base.gpu_snapshot(args.device);config=OmegaConf.load(formal/'native512_config.yaml');dataset=dataset_for(config,R9/'objects.txt',base.DATA_ROOT);device=torch.device(args.device);torch.set_num_threads(4);seed_all(42)
 stage=R9/(f"rank{args.rank}_{'_'.join(conditions)}"+(f'_attempt{args.attempt:02d}' if args.attempt!=1 else ''));assert not stage.exists();stage.mkdir();(stage/'execution_source.py').write_bytes(Path(__file__).read_bytes());identity={'status':'RUNNING_NATIVE_CHECKPOINT_MATRIX','rank':args.rank,'conditions':conditions,'checkpoint_sha256':sha(checkpoint),'cohort_freeze_sha256':sha(R9/'COHORT_AND_ANALYSIS_FREEZE.json'),'statistics_freeze_sha256':sha(R9/'STATISTICAL_PROTOCOL.json'),'source_sha256':sha(Path(__file__)),'input_helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py')),'gpu':gpu};write(stage/'RUN_IDENTITY.json',identity)
 os.environ.update(MVP_RUN_DIR=str(stage),MVP_OBJECT_LIST=str(R9/'objects.txt'),MVP_CONDITIONS='native_gfl,native_gfh,native_gc3,gen_linear')
 spec=importlib.util.spec_from_file_location('frozen_native_schedules009',base.RUNNER_SOURCE);registry=importlib.util.module_from_spec(spec);spec.loader.exec_module(registry)
 schedules={n:registry.CONDITIONS[n]['fn'] for n in ['native_gfl','native_gfh','native_gc3','gen_linear']};schedules.update(budget_fixed_mean=lambda _:1.65,budget_late16=lambda p:2.5 if round(p*49)>=34 else 1.25)
 model=ee.load_model(str(formal/'native512_config.yaml'),None,device);state=torch.load(checkpoint,map_location='cpu',weights_only=False);assert state['step']==2000 and isinstance(state['adapters'],dict);model.adapters.load_state_dict(state['adapters'],strict=True);model.geo_encoder.load_state_dict(state['encoder'],strict=True)
 for key,tensor in model.adapters.state_dict().items():assert torch.equal(tensor.cpu(),state['adapters'][key])
 for key,tensor in model.geo_encoder.state_dict().items():assert torch.equal(tensor.cpu(),state['encoder'][key])
 model.unet.eval();model.adapters.eval();model.geo_encoder.eval();pipe=model.pipeline;pipe.prepare_init=True
 for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to(device,dtype=torch.float16).eval()
 wrappers=[m for m in pipe.unet.modules() if isinstance(m,GeoTexResnetWrapper)];assert len(wrappers)==9;frozen={x['uid']:x for x in cohort['rows']};rows=[]
 try:
  for i,uid in enumerate(cohort['uids']):
   if i%2!=args.rank:continue
   seed_all(42+i);batch=strict_batch(dataset,i,device);source=source_for(dataset,i);verify_reference_target(batch,source);_,target,normal,depth,geo,mask=prepare_batch(batch,512,device);rec=frozen[uid]
   assert tensor_hash(target)==rec['target_tensor_hash'] and tensor_hash(geo)==rec['geometry_tensor_hash'] and tensor_hash(mask)==rec['mask_tensor_hash'] and sha(source)==rec['source_sha256']
   with torch.no_grad():features=model.geo_encoder(geo.float().clamp(0,1))
   traces=[]
   for condition in conditions:
    path=R9/'predictions'/condition/f'{uid}.png';assert not path.exists();model._clear_geo_feats_on_wrappers()
    for w in wrappers:
     if hasattr(w,'_adapter_scale'):del w._adapter_scale
    if condition!='disabled':model._set_geo_feats_on_wrappers(features)
    trace={'calls':0,'initial_latent_hash':None,'read_counts':[0]*9,'write_skip_counts':[0]*9,'rng_hashes':[],'scales':[]};original=pipe.prepare_latents
    def observe_prepare(*a,**kw):
     result=original(*a,**kw);trace['initial_latent_hash']=tensor_hash(result);return result
    def before(module,a,kw):
     step=trace['calls'];assert step<50;trace['rng_hashes'].append(tensor_hash(torch.cuda.get_rng_state(device)));scale=None if condition in ['disabled','native_unset'] else schedules[condition](step/49);trace['scales'].append(scale)
     if scale is not None:
      for w in wrappers:w._adapter_scale=scale.get(w.depth_group,1.) if isinstance(scale,dict) else scale
     trace['calls']+=1
    def observe(i):
     def after(m,a,output):
      if GeoTexResnetWrapper._skip_correction:trace['write_skip_counts'][i]+=1
      else:
       trace['read_counts'][i]+=1
       if condition!='disabled':assert m._last_correction is not None and m._last_correction.shape[0]==2 and torch.isfinite(m._last_correction).all()
     return after
    pipe.prepare_latents=observe_prepare;hooks=[pipe.unet.register_forward_pre_hook(before,with_kwargs=True)]+[w.register_forward_hook(observe(j)) for j,w in enumerate(wrappers)];seed_all(42);started=time.time()
    try:
     with torch.no_grad():result=pipe(Image.open(source).convert('RGBA'),num_inference_steps=50,generator=torch.Generator(device=device).manual_seed(42),guidance_scale=2.,depth_image=None,output_type='pil')
    finally:
     for h in hooks:h.remove()
     pipe.prepare_latents=original;model._clear_geo_feats_on_wrappers()
    assert trace['calls']==50 and trace['read_counts']==[50]*9 and trace['write_skip_counts']==[50]*9;assert result[0].size==(1024,1536)
    if traces:assert trace['initial_latent_hash']==traces[0]['initial_latent_hash'] and trace['rng_hashes']==traces[0]['rng_hashes']
    path.parent.mkdir(parents=True,exist_ok=True);result[0].save(path);rows.append({'uid':uid,'condition':condition,'output_path':str(path),'output_sha256':sha(path),'source_sha256':sha(source),'geometry_hash':tensor_hash(geo),'trace':trace,'elapsed_seconds':time.time()-started});traces.append(trace);write(stage/'ROWS.json',rows);print('Saved',args.rank,uid,condition,flush=True)
  identity.update(status='COMPLETE_NATIVE_CHECKPOINT_MATRIX_STAGE',rows=rows);write(stage/'RUN_IDENTITY.json',identity)
 except Exception as exc:identity.update(status='FAILED_NATIVE_CHECKPOINT_MATRIX_STAGE',error=f'{type(exc).__name__}: {exc}',rows=rows);write(stage/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
