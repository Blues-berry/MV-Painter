"""Matched deployment timing; output identity gates and no model-loading/PNG IO timing."""
import argparse,json,time,hashlib,gc
from native_training_protocol008 import *
import geotex.eval_exploration as ee
from run_v29_native_probe009 import controls,MVPainter_Pipeline,ControlNetModel_Union
from safetensors import safe_open
R10=OUT/'iteration010_same_v29_base';R9=OUT/'iteration009_native_checkpoint_evaluation';R11=OUT/'iteration011_deployment_performance'
def pixelsha(im):return hashlib.sha256(np.asarray(im.convert('RGB')).tobytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--method',choices=['geometry','full_v29'],required=True);ap.add_argument('--device',required=True);ap.add_argument('--phase',type=int,choices=[0,1],required=True);ap.add_argument('--attempt',type=int,default=1);a=ap.parse_args();protocol=json.loads((R11/'PROTOCOL_FREEZE.json').read_text());run=R11/(f'phase{a.phase}_{a.method}_{a.device.replace(":","_")}' +(f'_attempt{a.attempt:02d}' if a.attempt!=1 else ''));assert not run.exists();run.mkdir();gpu=base.gpu_snapshot(a.device);device=torch.device(a.device);torch.cuda.set_device(device);torch.set_num_threads(4);seed_all(42);config=OmegaConf.load(R10/'formal_ddp_training/native512_config.yaml');dataset=dataset_for(config,R10/'evaluation/objects.txt',base.DATA_ROOT);uids=protocol['uids'];inputs=[]
 for i,uid in enumerate(uids):
  assert Path(dataset.paths[i]).name==uid;batch=strict_batch(dataset,i,'cpu');source=source_for(dataset,i);verify_reference_target(batch,source);_,target,normal,depth,geo,mask=prepare_batch(batch,512,'cpu');image=Image.open(source).convert('RGBA');n,d,m=controls(Path(dataset.paths[i]),source);expected=(R10/'evaluation/predictions/native_unset' if a.method=='geometry' else R9/'predictions/v29_full_controlnet')/f'{uid}.png';inputs.append({'uid':uid,'image':image,'geo':geo,'normal':n,'depth':d,'expected_pixel_sha256':pixelsha(Image.open(expected)),'source_sha256':sha(source)})
 if a.method=='geometry':
  identity=json.loads((R10/'formal_ddp_training/RUN_IDENTITY.json').read_text());checkpoint=R10/'formal_ddp_training/geotex_step2000.pt';assert sha(checkpoint)==identity['latest_checkpoint_sha256'];model=ee.load_model(str(R10/'formal_ddp_training/native512_config.yaml'),None,device);state=torch.load(checkpoint,map_location='cpu',weights_only=False);model.adapters.load_state_dict(state['adapters'],strict=True);model.geo_encoder.load_state_dict(state['encoder'],strict=True);del state;pipe=model.pipeline;pipe.prepare_init=True
  for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to(device,dtype=torch.float16).eval()
  params=list(model.unet.parameters())+list(model.geo_encoder.parameters())
 else:
  audit=json.loads((R9/'controlnet_asset_audit_attempt02/CONTROLNET_ASSET_AUDIT.json').read_text());assert sha(Path(audit['asset_path']))==audit['asset_sha256'];pipe=MVPainter_Pipeline.from_pretrained(str(base.load_launcher_helpers().BASE_MODEL),torch_dtype=torch.float16,use_safetensors=True);pipe.add_controlnet(ControlNetModel_Union.from_unet(pipe.unet).to(dtype=torch.float16),conditioning_scale=1.)
  with safe_open(audit['asset_path'],framework='pt',device='cpu') as f:
   state=pipe.unet.state_dict();assert set(state)==set(f.keys())
   with torch.no_grad():
    for k,t in state.items():x=f.get_tensor(k);assert t.shape==x.shape;t.copy_(x.to(t.dtype))
  del state,x;pipe.to(device);pipe.unet.eval();params=list(pipe.unet.parameters())
 pipe.unet.eval();gc.collect();torch.cuda.empty_cache();rows=[];identity={'status':'RUNNING_BENCHMARK','method':a.method,'device':a.device,'phase':a.phase,'gpu':gpu,'protocol_sha256':sha(R11/'PROTOCOL_FREEZE.json'),'source_sha256':sha(Path(__file__)),'denoiser_geometry_parameter_count':sum(p.numel() for p in {id(x):x for x in params}.values()),'time_scope':protocol['time_scope']};write(run/'RUN_IDENTITY.json',identity);(run/'execution_source.py').write_bytes(Path(__file__).read_bytes());del params
 def execute(item,warm,rep):
  seed_all(42);torch.cuda.synchronize(device);torch.cuda.reset_peak_memory_stats(device);baseline=torch.cuda.memory_allocated(device);started=time.perf_counter()
  with torch.no_grad():
   if a.method=='geometry':
    model._clear_geo_feats_on_wrappers();features=model.geo_encoder(item['geo'].to(device).float().clamp(0,1));model._set_geo_feats_on_wrappers(features);result=pipe(item['image'],num_inference_steps=50,guidance_scale=2.,depth_image=None,generator=torch.Generator(device=device).manual_seed(42),output_type='pil');model._clear_geo_feats_on_wrappers();del features
   else:result=pipe(item['image'],depth_image=item['normal'],depth_image_2=item['depth'],num_inference_steps=50,guidance_scale=2.,generator=torch.Generator(device=device).manual_seed(42),output_type='pil')
  torch.cuda.synchronize(device);elapsed=time.perf_counter()-started;actual=pixelsha(result[0]);assert actual==item['expected_pixel_sha256'],'Output pixels differ from frozen quality matrix; no performance claim';row={'uid':item['uid'],'warmup':warm,'repeat':rep,'seconds':elapsed,'baseline_allocated_bytes':baseline,'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),'peak_reserved_bytes':torch.cuda.max_memory_reserved(device),'pixel_sha256':actual,'expected_pixel_sha256':item['expected_pixel_sha256']};rows.append(row);write(run/'ROWS.json',rows)
  if not warm and rep==0:result[0].save(run/f"{item['uid']}.png")
  print(a.method,item['uid'],'warm' if warm else rep,elapsed,flush=True)
 try:
  for rep in range(2):execute(inputs[0],True,rep)
  for item in inputs:
   for rep in range(3):execute(item,False,rep)
  identity.update(status='COMPLETE_PIXEL_IDENTICAL_DEPLOYMENT_BENCHMARK',rows=rows);write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:identity.update(status='FAILED_BENCHMARK_NO_RETRY',error=f'{type(exc).__name__}: {exc}',rows=rows);write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
