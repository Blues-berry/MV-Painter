"""Seen-case probe of actual full v29 weights; controlled Fresh geometry, not CLI default."""
import argparse,json,time
from native_training_protocol008 import *
from safetensors import safe_open
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.controlnet import ControlNetModel_Union
from run_native_disabled_gate006 import UIDS
R9=OUT/'iteration009_native_checkpoint_evaluation'
def controls(root,source):
 ids=[0,15,12,16,13,14] if source.stem=='000' else [14,15,0,16,12,13];norms=[];depths=[]
 for i in ids:
  normal=Image.open(root/'normal'/f'{i:03d}.png').convert('RGB');depth=np.asarray(Image.open(root/'depth_png'/f'{i:03d}.png'));assert depth.dtype==np.uint16 and depth.shape==(512,512)
  if i in [15,16]:normal=normal.transpose(Image.Transpose.ROTATE_90);depth=np.rot90(depth)
  assert normal.size==(512,512);norms.append(np.asarray(normal));depths.append(depth)
 normal=np.concatenate([np.concatenate(norms[i:i+2],axis=1) for i in [0,2,4]],axis=0);depth=np.concatenate([np.concatenate(depths[i:i+2],axis=1) for i in [0,2,4]],axis=0);valid=(depth>0)&(depth<65535);assert valid.any();inverse=np.ones(depth.shape,dtype=np.float32);inverse[valid]=65535./depth[valid];low=float(inverse[valid].min());high=float(inverse[valid].max());assert high>low;inverse[valid]=(inverse[valid]-low)/(high-low);assert np.isfinite(inverse).all();depth_rgb=np.repeat((inverse*255).astype('uint8')[:,:,None],3,axis=2)
 return Image.fromarray(normal),Image.fromarray(depth_rgb),{'raw_indices':ids,'zero_depth_pixels':int((depth==0).sum()),'normal_policy':'raw RGB channels, alpha discarded as official cv2 RGB save, no white composite','depth_policy':'official inverse-depth normalization with noninvertible zeros excluded','pole_policy':'Fresh target poles rotatedCCW90 to match current target layout; projection/roll equivalence to official renderer not proven','normal_array_sha256':hashlib.sha256(normal.tobytes()).hexdigest(),'depth_array_sha256':hashlib.sha256(depth_rgb.tobytes()).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--device',default='cuda:1');ap.add_argument('--cohort',type=Path);ap.add_argument('--rank',type=int,choices=[0,1]);a=ap.parse_args();uids=a.cohort.read_text().splitlines() if a.cohort else UIDS;conditions=['v29_full_controlnet'] if a.cohort else ['v29_bare','v29_full_controlnet'];run=R9/f'v29_frozen_fresh50_rank{a.rank}' if a.cohort else R9/'v29_seen_case_probe';assert not run.exists();gpu=base.gpu_snapshot(a.device);audit=json.loads((R9/'controlnet_asset_audit_attempt02/CONTROLNET_ASSET_AUDIT.json').read_text());assert audit['status']=='PASS_LOCAL_FULL_CONTROLNET_CHECKPOINT_CPU_STRICT_LAYOUT_AND_LOAD';run.mkdir();(run/'objects.txt').write_text('\n'.join(uids)+'\n');config=OmegaConf.load(RUN/'formal_ddp_training/native512_config.yaml');dataset=dataset_for(config,run/'objects.txt',base.DATA_ROOT);torch.set_num_threads(4);seed_all(42);device=torch.device(a.device);torch.cuda.set_device(device)
 identity={'status':'RUNNING_V29_SEEN_CASE_PROBE','objects':uids,'conditions':conditions,'rank':a.rank,'seed':42,'steps':50,'cfg':2.,'control_scale':1.,'asset_sha256':audit['asset_sha256'],'source_sha256':sha(Path(__file__)),'gpu':gpu,'scope':'controlled50/42/no-rembg on declared inputs; not unmodified75/12/rembg CLI; same pre-frozen Fresh cohort when supplied, not globally unseen data'};write(run/'RUN_IDENTITY.json',identity);(run/'execution_source.py').write_bytes(Path(__file__).read_bytes())
 pipe=MVPainter_Pipeline.from_pretrained(str(base.load_launcher_helpers().BASE_MODEL),torch_dtype=torch.float16,use_safetensors=True);net=ControlNetModel_Union.from_unet(pipe.unet).to(dtype=torch.float16);pipe.add_controlnet(net,conditioning_scale=1.0);weights=Path(audit['asset_path']);assert sha(weights)==audit['asset_sha256'];state=pipe.unet.state_dict()
 with safe_open(weights,framework='pt',device='cpu') as f:
  assert set(state)==set(f.keys())
  with torch.no_grad():
   for key,t in state.items():x=f.get_tensor(key);assert t.shape==x.shape;t.copy_(x.to(t.dtype))
 pipe.to(device);pipe.unet.eval();full=pipe.unet;bare=full.unet;rows=[]
 try:
  for i,uid in enumerate(uids):
   if a.rank is not None and i%2!=a.rank:continue
   batch=strict_batch(dataset,i,'cpu');source=source_for(dataset,i);verify_reference_target(batch,source);normal,depth,metadata=controls(Path(dataset.paths[i]),source)
   for cond in conditions:
    pipe.unet=bare if cond=='v29_bare' else full;seed_all(42);torch.cuda.reset_peak_memory_stats(device);start=time.time()
    with torch.no_grad():result=pipe(Image.open(source).convert('RGBA'),depth_image=normal if cond=='v29_full_controlnet' else None,depth_image_2=depth if cond=='v29_full_controlnet' else None,num_inference_steps=50,guidance_scale=2.,generator=torch.Generator(device=device).manual_seed(42),output_type='pil')
    assert result[0].size==(1024,1536);path=(R9 if a.cohort else run)/'predictions'/cond/f'{uid}.png';path.parent.mkdir(parents=True,exist_ok=True);result[0].save(path);rows.append({'uid':uid,'condition':cond,'output_sha256':sha(path),'source_sha256':sha(source),'control_metadata':metadata,'elapsed_seconds':time.time()-start,'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),'output_path':str(path),'timing_scope':'instrumented development execution, not clean matched latency benchmark; both model branches remain resident'});write(run/'ROWS.json',rows);print('Saved',uid,cond,flush=True)
  identity.update(status='COMPLETE_V29_FROZEN_FIFTY_OBJECT_RANK' if a.cohort else 'COMPLETE_V29_SEEN_CASE_PROBE',rows=rows);write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:identity.update(status='FAILED_V29_SEEN_CASE_PROBE',error=f'{type(exc).__name__}: {exc}',rows=rows);write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
