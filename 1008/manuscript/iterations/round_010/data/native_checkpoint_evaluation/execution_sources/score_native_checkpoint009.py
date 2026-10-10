"""Score exact native512 target slots with one object as analysis unit."""
import argparse,json,math,time
from native_training_protocol008 import *
from evaluate_fresh_c_native_egl import load_metric_implementations
R9=OUT/'iteration009_native_checkpoint_evaluation';METRICS=['fg_psnr','fg_ssim','fg_lpips','ciede2000']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--conditions',default='disabled,native_unset');ap.add_argument('--device',default='cuda:0');args=ap.parse_args();conditions=args.conditions.split(',');name='_'.join(conditions);out=R9/f'scores_{name}.json';assert not out.exists();cohort=json.loads((R9/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());assert json.loads((R9/'METRIC_CALIBRATION.json').read_text())['status']=='PASS_NATIVE512_TARGET_MASK_AND_SELF_METRICS';config=OmegaConf.load(RUN/'formal_ddp_training/native512_config.yaml');dataset=dataset_for(config,R9/'objects.txt',base.DATA_ROOT);torch.set_num_threads(4);device=torch.device(args.device);impl=load_metric_implementations();lp=impl['get_lpips_fn'](device);assert lp is not None;rows=[];started=time.time()
 for i,uid in enumerate(cohort['uids']):
  seed_all(42+i);batch=strict_batch(dataset,i,'cpu');_,target,normal,depth,geo,mask=prepare_batch(batch,512,'cpu');assert tensor_hash(target)==cohort['rows'][i]['target_tensor_hash']
  for condition in conditions:
   path=R9/'predictions'/condition/f'{uid}.png';assert path.exists();image=np.asarray(Image.open(path).convert('RGB'),np.float32)/255.;assert image.shape==(1536,1024,3);views=[]
   for view in range(6):
    y,x=divmod(view,2);pred_rgb=image[y*512:(y+1)*512,x*512:(x+1)*512];gt=target[:,:,y*512:(y+1)*512,x*512:(x+1)*512].to(device);m=(mask[:,:,y*512:(y+1)*512,x*512:(x+1)*512]>.5).float().to(device);pred=torch.from_numpy(pred_rgb.copy()).permute(2,0,1)[None].to(device);gt_rgb=gt[0].permute(1,2,0).cpu().numpy();values={'fg_psnr':float(impl['compute_psnr'](pred,gt,m)),'fg_ssim':float(impl['compute_ssim'](pred,gt,m)),'fg_lpips':float(impl['compute_lpips'](pred,gt,m,lpips_fn=lp,device=device)),'ciede2000':float(impl['masked_ciede2000'](pred_rgb,gt_rgb,m[0,0].cpu().numpy(),erosion_radius=1))};assert all(math.isfinite(v) for v in values.values());views.append({'view':view,'role':'source' if view==0 else 'nonreference',**values})
   rows.append({'uid':uid,'condition':condition,'output_sha256':sha(path),'views':views,'nonreference_mean':{k:float(np.mean([v[k] for v in views[1:]])) for k in METRICS},'all_six_mean':{k:float(np.mean([v[k] for v in views])) for k in METRICS},'source':{k:views[0][k] for k in METRICS}});write(R9/f'scores_{name}_partial.json',rows)
  print('Scored',i+1,len(cohort['uids']),uid,flush=True)
 write(out,{'status':'COMPLETE_NATIVE_SLOT_SCORING','conditions':conditions,'rows':rows,'cohort_sha256':sha(R9/'COHORT_AND_ANALYSIS_FREEZE.json'),'statistics_sha256':sha(R9/'STATISTICAL_PROTOCOL.json'),'metric_calibration_sha256':sha(R9/'METRIC_CALIBRATION.json'),'source_sha256':sha(Path(__file__)),'metric_sources':impl['source_hashes'],'elapsed_seconds':time.time()-started})
if __name__=='__main__':main()
