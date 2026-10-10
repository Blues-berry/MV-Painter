"""Actual native identity and conditional/unconditional backward gates at512."""
import json,time,datetime
from pathlib import Path
from native_training_protocol008 import *
import geotex.eval_exploration as ee
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

def grad_norm(module):
 values=[p.grad for p in module.parameters() if p.grad is not None]
 assert values and all(torch.isfinite(x).all() for x in values)
 return float(torch.sqrt(sum(x.float().square().sum() for x in values)))
def state_hash(module):
 h=hashlib.sha256()
 for name,t in module.state_dict().items():h.update(name.encode());h.update(t.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()
def main():
 run=RUN/'preflight';assert not run.exists();gpu=base.gpu_snapshot('cuda:0');sources=base.verify_sources();run.mkdir(parents=True)
 identity={'status':'FROZEN_NATIVE512_TRAINING_PREFLIGHT','source_sha256':sha(Path(__file__)),'helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py')),'gpu':gpu,'sources':sources,'seed':42,'geometry_target_resolution':512,'target_view_mode':'unique6','optimizer_lr':1e-4,'drop_probe_order':['conditional','unconditional'],'regularization':'compute_loss before clearing wrapper corrections','scope':'feasibility only, smoke weights discarded; no quality or historical replay claim','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(run/'RUN_IDENTITY.json',identity)
 (run/'execution_source.py').write_bytes(Path(__file__).read_bytes());(run/'execution_helper.py').write_bytes(Path(__file__).with_name('native_training_protocol008.py').read_bytes())
 seed_all(42);torch.set_num_threads(4);device=torch.device('cuda:0');config=OmegaConf.load(RUN/'native512_config.yaml');model=ee.load_model(str(RUN/'native512_config.yaml'),None,device);pipe=model.pipeline;pipe.prepare_init=True;model.unet.eval();model.geo_encoder.eval()
 wrappers=[m for m in model.unet.modules() if isinstance(m,GeoTexResnetWrapper)];assert len(wrappers)==9
 for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to(device,dtype=torch.float16).eval()
 try:
  hand={x['uid']:x for x in json.loads((OUT/'ITERATION002_BAKE_HANDOFF.json').read_text())['objects']};dev=['1dc2c857f7614caeb6c2aa0559ccf973','21678bd623654182b52c11d013de4e71'];dev_list=run/'dev_objects.txt';dev_list.write_text('\n'.join(dev)+'\n');dataset=dataset_for(config,dev_list,base.DATA_ROOT);zero_rows=[]
  for i,uid in enumerate(dev):
   seed_all(42+i);batch=strict_batch(dataset,i,device)
   with torch.no_grad():
    *_,geo,mask=prepare_batch(batch,512,device);features=model.geo_encoder(torch.nan_to_num(geo.float().clamp(0,1)));model._set_geo_feats_on_wrappers(features)
   for w in wrappers:w._adapter_scale=0.
   record=hand[uid];source=Path(record['gt_rgba_17'][record['target_view_mapping'][0]['raw_view_index']]);seed_all(42);start=time.time()
   with torch.no_grad():result=pipe(Image.open(source).convert('RGBA'),num_inference_steps=50,generator=torch.Generator(device=device).manual_seed(42),guidance_scale=2.,depth_image=None,output_type='pil')
   previous=OUT/'iteration003_native_base_diagnostic_rgba_attempt02/predictions/native_base_50'/f'{uid}.png';assert np.array_equal(np.asarray(result[0]),np.asarray(Image.open(previous)))
   path=run/f'zero_scale_{uid}.png';result[0].save(path);zero_rows.append({'uid':uid,'output_sha256':sha(path),'previous_sha256':sha(previous),'rgb_pixels_identical':True,'elapsed_seconds':time.time()-start})
   model._clear_geo_feats_on_wrappers()
   for w in wrappers:del w._adapter_scale
   del features,geo,mask,batch
  write(run/'ZERO_IDENTITY.json',zero_rows)
  train=dataset_for(config,RUN/'train_objects_1112.txt',Path(config.data.params.train.params.root_dir_list[0]));assert len(train)==1112
  payloads=[];cross_gpu=[]
  for i in range(2):
   uid=Path(train.paths[i]).name;seed_all(42+i);batch=strict_batch(train,i,device);source=source_for(train,i);verify_reference_target(batch,source);payload=capture_native_conditioning(pipe,source,device,42);payloads.append(payload)
   cached=RUN/'conditioning_cache'/f'{uid}.pt';assert cached.exists(),'GPU1 cache should supply first two inputs before identity gates finish'
   comparison=payload_hashes(torch.load(cached,map_location='cpu',weights_only=False));assert payload_hashes(payload)==comparison
   cross_gpu.append({'uid':uid,'source_sha256':sha(source),'payload_hashes':comparison,'gpu0_gpu1_payload_identical':True});del batch
  write(run/'CROSS_GPU_CONDITIONING_IDENTITY.json',cross_gpu)
  for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to('cpu')
  torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats(device)
  model.unet.requires_grad_(False);model.adapters.requires_grad_(True);model.geo_encoder.requires_grad_(True);model.adapters.train();model.geo_encoder.train()
  params=list(model.adapters.parameters())+list(model.geo_encoder.parameters());assert len({id(p) for p in params})==len(params);opt=torch.optim.AdamW(params,lr=1e-4);before={'adapters':state_hash(model.adapters),'encoder':state_hash(model.geo_encoder)};rows=[]
  for i,drop in enumerate([False,True]):
   uid=Path(train.paths[i]).name;seed_all(42+i);batch=strict_batch(train,i,device);source=source_for(train,i);error=verify_reference_target(batch,source);_,target,normal,depth,geo,mask=prepare_batch(batch,512,device);label='negative' if drop else 'positive';payload=payloads[i][label];prompt=payload['prompt'].to(device);ref=payload['reference'].to(device);added={k:v.to(device) for k,v in payload['added'].items()}
   t=torch.tensor([100 if i==0 else 700],device=device,dtype=torch.long);start=time.time();opt.zero_grad(set_to_none=True)
   with torch.no_grad():
    posterior=pipe.vae.encode(((target-.5)/.8).to(dtype=torch.float16)).latent_dist
    from metrics import scale_latents
    latent=scale_latents(posterior.sample()*pipe.vae.config.scaling_factor);noise=torch.randn_like(latent);noisy=model.train_scheduler.add_noise(latent,noise,t)
   features=model.geo_encoder(torch.nan_to_num(geo.float().clamp(0,1)));model._set_geo_feats_on_wrappers(features)
   pred=pipe.unet(noisy,t,encoder_hidden_states=prompt,cross_attention_kwargs={'cond_lat':ref},added_cond_kwargs=added,return_dict=False,is_training=True)[0]
   loss,components=model.compute_loss(pred,noise,target,mask,torch.float16,depth_imgs=depth,normal_imgs=normal)
   write(run/'LATEST_FORWARD_GATE.json',{'uid':uid,'drop_condition':drop,'loss':float(loss.detach()),'components':{k:float(v.detach()) for k,v in components.items()},'depth_zero_channel_values':sum(train.depth_zero_counts.values())})
   assert torch.isfinite(loss) and 'train/reg_loss' in components and components['train/reg_loss']>0
   loss.backward();an=grad_norm(model.adapters);en=grad_norm(model.geo_encoder);assert an>0 and en>0
   torch.nn.utils.clip_grad_norm_(params,1.);opt.step();model._clear_geo_feats_on_wrappers();assert all(torch.isfinite(p).all() for p in params)
   row={'uid':uid,'drop_condition':drop,'timestep':int(t[0]),'latent_shape':list(latent.shape),'target_reference_max_error':error,'source_sha256':sha(source),'loss':float(loss.detach()),'components':{k:float(v.detach()) for k,v in components.items()},'adapter_grad_norm':an,'encoder_grad_norm':en,'elapsed_seconds':time.time()-start,'allocated_peak_bytes':torch.cuda.max_memory_allocated(device),'reserved_peak_bytes':torch.cuda.max_memory_reserved(device)};rows.append(row);write(run/'BACKWARD_GATES.json',rows);print('Backward gate passed',uid,'drop',drop,'loss',row['loss'],flush=True)
   del batch,target,normal,depth,geo,mask,features,pred,loss,components,latent,noise,noisy,posterior
  after={'adapters':state_hash(model.adapters),'encoder':state_hash(model.geo_encoder)};assert all(before[k]!=after[k] for k in before)
  identity.update(status='PASS_NATIVE512_TRAINING_PREFLIGHT',zero_identity=zero_rows,cross_gpu=cross_gpu,backward_gates=rows,before_weights=before,after_weights=after,trainable_parameter_count=sum(p.numel() for p in params),smoke_weights_discarded=True);write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:
  identity.update(status='FAILED_NATIVE512_TRAINING_PREFLIGHT',error=f'{type(exc).__name__}: {exc}');write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
