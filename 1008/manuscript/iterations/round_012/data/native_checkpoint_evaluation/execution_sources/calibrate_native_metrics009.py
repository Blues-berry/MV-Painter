"""Calibrate native512 target/mask/metric identity before checkpoint output evaluation."""
import json
from native_training_protocol008 import *
from evaluate_fresh_c_native_egl import load_metric_implementations
R9=OUT/'iteration009_native_checkpoint_evaluation'
def main():
 assert not (R9/'predictions').exists();torch.set_num_threads(4);config=OmegaConf.load(RUN/'formal_ddp_training/native512_config.yaml');dataset=dataset_for(config,R9/'objects.txt',base.DATA_ROOT);frozen=json.loads((R9/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());rows=[]
 impl=load_metric_implementations();lp=impl['get_lpips_fn']('cpu');assert lp is not None
 for i,uid in enumerate(frozen['uids']):
  seed_all(42+i);batch=strict_batch(dataset,i,'cpu');source=source_for(dataset,i);err=verify_reference_target(batch,source);_,target,normal,depth,geo,mask=prepare_batch(batch,512,'cpu');assert tensor_hash(target)==frozen['rows'][i]['target_tensor_hash'];counts=[];self_metrics=[]
  for view in range(6):
   y,x=divmod(view,2);gt=target[:,:,y*512:(y+1)*512,x*512:(x+1)*512];m=(mask[:,:,y*512:(y+1)*512,x*512:(x+1)*512]>.5).float();counts.append(float(m.sum()));assert counts[-1]>0
   if i==0:
    rgb=gt[0].permute(1,2,0).numpy();values={'fg_psnr':impl['compute_psnr'](gt,gt,m),'fg_ssim':impl['compute_ssim'](gt,gt,m),'fg_lpips':impl['compute_lpips'](gt,gt,m,lpips_fn=lp,device='cpu'),'ciede2000':impl['masked_ciede2000'](rgb,rgb,m[0,0].numpy(),erosion_radius=1)};assert values['fg_psnr']==100. and abs(values['fg_ssim']-1.)<1e-6 and abs(values['fg_lpips'])<1e-8 and abs(values['ciede2000'])<1e-8;self_metrics.append(values)
  rows.append({'uid':uid,'reference_target_max_error':err,'foreground_pixel_counts':counts,'self_metrics_first_object':self_metrics})
 write(R9/'METRIC_CALIBRATION.json',{'status':'PASS_NATIVE512_TARGET_MASK_AND_SELF_METRICS','uids':len(rows),'rows':rows,'mask_rule':'binarize original GT alpha at >0.5 as existing EGL evaluation, shared by all predictions; no predicted mask','metric_sources':impl['source_hashes'],'source_sha256':sha(Path(__file__)),'cohort_freeze_sha256':sha(R9/'COHORT_AND_ANALYSIS_FREEZE.json'),'target_identity':'encoded raw RGBA composite, exact reference first tile; fixed 512 unique6 layout','scope':'metric/input contract, not rendered generated-camera or quality proof'});print('PASS GT self all four metrics and 50x6 positive masks')
if __name__=='__main__':main()
