"""Frozen native512 training: two GPU ranks, strict inputs and actual condition dropout."""
import os,json,time,argparse,datetime,csv
from native_training_protocol008 import *
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
import geotex.eval_exploration as ee
from metrics import scale_latents

class NativeStep(torch.nn.Module):
 def __init__(self,model):
  super().__init__();self.unet=model.unet;self.encoder=model.geo_encoder
  self.wrappers=[m for m in self.unet.modules() if isinstance(m,GeoTexResnetWrapper)]
 def forward(self,noisy,t,geo,prompt,ref,added):
  features=self.encoder(geo.float().clamp(0,1))
  for m in self.wrappers:m.set_geo_feats(features)
  pred=self.unet(noisy,t,encoder_hidden_states=prompt,cross_attention_kwargs={'cond_lat':ref},added_cond_kwargs=added,return_dict=False,is_training=True)[0]
  reg=torch.stack([m._last_correction.float().square().mean() for m in self.wrappers]).mean()
  return pred,reg

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--gate',action='store_true');ap.add_argument('--run-root',type=Path,default=RUN);ap.add_argument('--base-model',type=Path);ap.add_argument('--gate-directory',default='ddp_backward_gate');args=ap.parse_args()
 if args.base_model:
  asset_identity=json.loads((args.run_root/'BASE_OVERLAY_IDENTITY.json').read_text());assert asset_identity['status']=='PASS1680_V29_UNET_TENSORS_EXACT_FP32_EXPORT';assert args.base_model.resolve()==Path(asset_identity['export_path']).resolve();assert sha(args.base_model/'unet/diffusion_pytorch_model.safetensors')==asset_identity['export_unet_sha256']
  if not args.gate:assert json.loads((args.run_root/args.gate_directory/'RUN_IDENTITY.json').read_text())['status']=='PASS_DDP_BACKWARD_GATE'
 rank=int(os.environ['LOCAL_RANK']);torch.cuda.set_device(rank);device=torch.device('cuda',rank);dist.init_process_group('nccl');torch.set_num_threads(4)
 run=args.run_root/(args.gate_directory if args.gate else 'formal_ddp_training');cache=RUN/'conditioning_cache_complete_inputs_attempt03';meta=json.loads((cache/'RUN_IDENTITY.json').read_text());assert meta['status']=='COMPLETE_NATIVE_CONDITIONING_CACHE_WITH_INPUT_LEDGER'
 pre=json.loads((RUN/'preflight_fp32_regularization_attempt03/RUN_IDENTITY.json').read_text());assert pre['status']=='PASS_NATIVE512_TRAINING_PREFLIGHT'
 uids=(RUN/'train_objects_native_valid.txt').read_text().splitlines();assert len(uids)==meta['eligible_uid_count']==1090;assert sha(RUN/'train_objects_native_valid.txt')==meta['eligible_uid_sha256']
 steps=2 if args.gate else 2000
 if rank==0:
  assert not run.exists();run.mkdir();(run/'execution_source.py').write_bytes(Path(__file__).read_bytes());(run/'execution_helper.py').write_bytes(Path(__file__).with_name('native_training_protocol008.py').read_bytes())
  config=OmegaConf.load(RUN/'native512_config.yaml');
  if args.base_model:config.model.params.stable_diffusion_config.pretrained_model_name_or_path=str(args.base_model.resolve())
  config.data.params.train.params.object_list_file=str(RUN/'train_objects_native_valid.txt');config.data.params.train.params.target_view_mode='unique6';OmegaConf.save(config,run/'native512_config.yaml')
  identity={'status':'FROZEN_DDP_TRAINING','steps':steps,'successful_optimizer_steps':0,'global_batch_size':2,'per_gpu_batch_size':1,'world_size':2,'seed':42,'lr':1e-4,'adamw_weight_decay':.01,'gradient_clip':1.,'grad_scaler_init':1024.,'condition_drop_probability':.1,'forced_gate_branch_per_rank':args.gate,'eligible_uid_count':len(uids),'eligible_uid_sha256':sha(RUN/'train_objects_native_valid.txt'),'cache_identity_sha256':sha(cache/'RUN_IDENTITY.json'),'source_sha256':sha(Path(__file__)),'helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py')),'frozen_source_files':base.verify_sources(),'base_model_override':str(args.base_model.resolve()) if args.base_model else None,'base_overlay_identity':asset_identity if args.base_model else None,'geometry_target_resolution':512,'target_view_mode':'unique6','random_resize_ratio':1.,'regularization':'float32 before clear','final_checkpoint_rule':'step2000 regardless of quality; no best checkpoint selection','scope':'new main adapter training; not FAC or historical reproduction','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(run/'RUN_IDENTITY.json',identity)
 dist.barrier();seed_all(42);model=ee.load_model(str(run/'native512_config.yaml'),None,device);pipe=model.pipeline;pipe.prepare_init=True
 if args.base_model:
  from safetensors import safe_open
  actual={k.replace('.resnet.','.'):v for k,v in model.unet.unet.state_dict().items() if '.adapter.' not in k}
  with safe_open(args.base_model/'unet/diffusion_pytorch_model.safetensors',framework='pt',device='cpu') as f:
   assert set(actual)==set(f.keys()) and len(actual)==1680
   for k,v in actual.items():assert torch.equal(v.detach().cpu(),f.get_tensor(k).to(v.dtype)),k
  del actual
  if args.gate:
   for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to(device,dtype=torch.float16).eval()
   check_config=OmegaConf.load(run/'native512_config.yaml');check_dataset=dataset_for(check_config,RUN/'train_objects_native_valid.txt',Path(check_config.data.params.train.params.root_dir_list[0]));checked=[]
   for i in range(2):
    uid=uids[i];source=source_for(check_dataset,i);payload=capture_native_conditioning(pipe,source,device,42);cached=torch.load(cache/f'{uid}.pt',map_location='cpu',weights_only=False);assert payload_hashes(payload)==payload_hashes(cached);checked.append({'uid':uid,'payload_hashes':payload_hashes(payload)})
   write(run/f'BASE_AND_CONDITION_IDENTITY_rank{rank}.json',{'status':'PASS1680_BASE_TENSORS_AND_TWO_NATIVE_CONDITIONS','rank':rank,'inputs':checked})
   del check_dataset,payload,cached
 for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to('cpu')
 model.unet.eval().requires_grad_(False);model.adapters.requires_grad_(True).train();model.geo_encoder.requires_grad_(True).train()
 # up_only never consumes the projected x1 branch; retain its weights but freeze it.
 model.geo_encoder.proj_x1.requires_grad_(False)
 module=NativeStep(model).to(device);params=[p for p in module.parameters() if p.requires_grad];allowed={id(p) for p in model.adapters.parameters()}|{id(p) for p in model.geo_encoder.parameters()};assert all(id(p) in allowed for p in params)
 ddp=DDP(module,device_ids=[rank],find_unused_parameters=False);opt=torch.optim.AdamW(params,lr=1e-4,weight_decay=.01);scaler=torch.amp.GradScaler('cuda',init_scale=1024.,growth_interval=2000)
 config=OmegaConf.load(run/'native512_config.yaml');dataset=dataset_for(config,RUN/'train_objects_native_valid.txt',Path(config.data.params.train.params.root_dir_list[0]));rows={x['uid']:x for x in meta['rows']};validated=set();seed_all(42+rank);order_rng=np.random.default_rng(42);drop_rng=np.random.default_rng(4242+rank);order=order_rng.permutation(len(uids));epoch=0
 torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats(device);start=time.time();csv_path=run/f'train_rank{rank}.csv';columns=['step','rank','uid','drop_condition','timestep','loss','noise_loss','ssim_loss','reg_loss','gradient_norm','gradient_scale','elapsed_seconds','peak_allocated_bytes'];fh=csv_path.open('w');writer=csv.DictWriter(fh,fieldnames=columns);writer.writeheader()
 try:
  for step in range(1,steps+1):
   position=2*(step-1)+rank;new_epoch=position//len(uids)
   while epoch<new_epoch:order=order_rng.permutation(len(uids));epoch+=1
   index=int(order[position%len(uids)]);uid=uids[index];batch=strict_batch(dataset,index,device);source=source_for(dataset,index);verify_reference_target(batch,source);assert sha(source)==rows[uid]['source_sha256'];_,target,normal,depth,geo,mask=prepare_batch(batch,512,device)
   cachefile=cache/f'{uid}.pt';payload=torch.load(cachefile,map_location='cpu',weights_only=False)
   if uid not in validated:assert sha(cachefile)==rows[uid]['cache_sha256'] and payload_hashes(payload)==rows[uid]['payload_hashes'];validated.add(uid)
   drop=bool(rank==1) if args.gate else bool(drop_rng.random()<.1);condition=payload['negative' if drop else 'positive'];prompt=condition['prompt'].to(device);ref=condition['reference'].to(device);added={k:v.to(device) for k,v in condition['added'].items()};t=torch.randint(0,model.train_scheduler.config.num_train_timesteps,(1,),device=device)
   opt.zero_grad(set_to_none=True)
   with torch.no_grad():
    latent=scale_latents(pipe.vae.encode(((target-.5)/.8).half()).latent_dist.sample()*pipe.vae.config.scaling_factor);noise=torch.randn_like(latent);noisy=model.train_scheduler.add_noise(latent,noise,t)
   pred,reg=ddp(noisy,t,geo,prompt,ref,added);weight=model.adapter_reg_weight;model.adapter_reg_weight=0.
   try:loss,components=model.compute_loss(pred,noise,target,mask,torch.float16,depth_imgs=depth,normal_imgs=normal)
   finally:model.adapter_reg_weight=weight
   loss=loss+weight*reg;assert torch.isfinite(loss) and torch.isfinite(reg)
   scaler.scale(loss).backward();scaler.unscale_(opt)
   assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in params)
   assert all(p.grad is None for p in module.parameters() if not p.requires_grad)
   grad=torch.nn.utils.clip_grad_norm_(params,1.);assert torch.isfinite(grad) and grad>0
   oldscale=scaler.get_scale();scaler.step(opt);scaler.update();assert scaler.get_scale()>=oldscale,'Numerical skip forbids silently counting an optimizer step'
   model._clear_geo_feats_on_wrappers();assert all(torch.isfinite(p).all() for p in params)
   row={'step':step,'rank':rank,'uid':uid,'drop_condition':int(drop),'timestep':int(t.item()),'loss':float(loss.detach()),'noise_loss':float(components['train/noise_loss'].detach()),'ssim_loss':float(components['train/ssim_loss'].detach()),'reg_loss':float(reg.detach()),'gradient_norm':float(grad),'gradient_scale':scaler.get_scale(),'elapsed_seconds':time.time()-start,'peak_allocated_bytes':torch.cuda.max_memory_allocated(device)};writer.writerow(row);fh.flush()
   if step%25==0 or step<=2:print('rank',rank,'step',step,'loss',row['loss'],'drop',drop,flush=True)
   if step%500==0 or step==steps:
    rng={'torch':torch.get_rng_state(),'cuda':torch.cuda.get_rng_state(device),'numpy_order':order_rng.bit_generator.state,'numpy_drop':drop_rng.bit_generator.state,'python':random.getstate()};torch.save(rng,run/f'rng_step{step}_rank{rank}.pt');dist.barrier()
    if rank==0:
     path=run/f'geotex_step{step}.pt';torch.save({'adapters':model.adapters.state_dict(),'encoder':model.geo_encoder.state_dict(),'step':step,'optimizer':opt.state_dict(),'scaler':scaler.state_dict(),'protocol_identity':identity},path);identity.update(status='TRAINING_RUNNING',successful_optimizer_steps=step,latest_checkpoint=str(path),latest_checkpoint_sha256=sha(path),active_trainable_parameters=sum(p.numel() for p in params));write(run/'RUN_IDENTITY.json',identity)
    dist.barrier()
   del batch,target,normal,depth,geo,mask,latent,noise,noisy,pred,reg,loss,components
  if rank==0:identity.update(status='PASS_DDP_BACKWARD_GATE' if args.gate else 'COMPLETE_NATIVE512_DDP_TRAINING',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:
  write(run/f'FAILURE_rank{rank}.json',{'error':f'{type(exc).__name__}: {exc}','last_attempted_step':locals().get('step'),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});raise
 finally:fh.close();dist.destroy_process_group()
if __name__=='__main__':main()
