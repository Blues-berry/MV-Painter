"""Score the frozen MV-Adapter development32 matrix against official GT targets.

Metrics and aggregation conventions mirror score_native_checkpoint009.py:
fg_psnr/fg_ssim/fg_lpips/ciede2000, all six native views pooled by arithmetic mean; camera-index summaries have
no reference/nonreference role labels, object as the
analysis unit. GT masks are the alpha channel of the official 512 RGBA targets
in MVA_MATRIX_FREEZE.json; every GT file and every prediction file is verified
against its recorded sha256 before scoring. Development evidence only: no
superiority claim, no winner selection.
"""
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from PIL import Image
from revision_expansion_common import OUT,sha,write
from evaluate_fresh_c_native_egl import load_metric_implementations
ROOT=OUT/'iteration012_condition_interference'
METRICS=['fg_psnr','fg_ssim','fg_lpips','ciede2000']

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--run-prefix',type=Path,required=True);ap.add_argument('--seeds',default='42,2026,31415');ap.add_argument('--device',default='cuda:0');ap.add_argument('--out',type=Path,default=ROOT/'mvadapter_development32_scoring');a=ap.parse_args()
 freeze=json.loads(a.freeze.read_text());objects=freeze['objects'];uids=[o['object_uid'] for o in objects]
 gt={o['object_uid']:[] for o in objects}
 for o in objects:
  for g in o['gt_images_official_order']:
   assert sha(g['path'])==g['sha256'],g['path'];gt[o['object_uid']].append(g['path'])
 impl=load_metric_implementations();device=torch.device(a.device);lp=impl['get_lpips_fn'](device);torch.set_num_threads(4)
 a.out.mkdir(parents=True,exist_ok=True)
 for seed in [int(s) for s in a.seeds.split(',')]:
  out=a.out/f'scores_mvadapter_seed{seed}.json';assert not out.exists(),out
  found={}
  for rank in [0,1]:
   run=Path(str(a.run_prefix)+f'_seed{seed}_rank{rank}')
   rows=json.loads((run/'ROWS.json').read_text())
   for row in rows:
    assert row['seed']==seed;key=(row['uid'],row['condition']);assert key not in found,key
    import hashlib
    h=hashlib.sha256(b''.join(np.asarray(Image.open(f).convert('RGB')).tobytes() for f in row['output_files'])).hexdigest()
    assert h==row['pixel_sha256'],key;found[key]=[str(f) for f in row['output_files']]
  conditions=sorted(set(k[1] for k in found));assert len(found)==len(uids)*len(conditions),(len(found),conditions)
  rows_out=[];started=time.time()
  for i,uid in enumerate(uids):
   gts=[]
   for p in gt[uid]:
    im=np.asarray(Image.open(p).convert('RGBA'),np.float32)/255.
    gts.append((im[...,:3],im[...,3:4]>.5))
   for condition in conditions:
    views=[]
    for v,p in enumerate(found[(uid,condition)]):
     rgb=np.asarray(Image.open(p).convert('RGB'),np.float32)/255.;assert rgb.shape==(512,512,3)
     gt_rgb,mask_np=gts[v];gt_img=torch.from_numpy(gt_rgb.transpose(2,0,1))[None].to(device);m=torch.from_numpy(mask_np.transpose(2,0,1).astype(np.float32))[None].to(device)
     pred=torch.from_numpy(rgb.transpose(2,0,1).copy())[None].to(device)
     values={'fg_psnr':float(impl['compute_psnr'](pred,gt_img,m)),'fg_ssim':float(impl['compute_ssim'](pred,gt_img,m)),'fg_lpips':float(impl['compute_lpips'](pred,gt_img,m,lpips_fn=lp,device=device)),'ciede2000':float(impl['masked_ciede2000'](rgb,gt_rgb,mask_np[...,0] if mask_np.ndim==3 else mask_np,erosion_radius=1))}
     assert all(np.isfinite(v) for v in values.values());views.append({'view':v,'role':'native_camera_view',**values})
    rows_out.append({'uid':uid,'condition':condition,'seed':seed,'views':views,'native_views1to5_mean':{k:float(np.mean([x[k] for x in views[1:]])) for k in METRICS},'all_six_mean':{k:float(np.mean([x[k] for x in views])) for k in METRICS},'native_view0':{k:views[0][k] for k in METRICS}})
   write(a.out/f'scores_mvadapter_seed{seed}_partial.json',rows_out);print('Scored',i+1,len(uids),uid,flush=True)
  write(out,{'status':'COMPLETE_MVADAPTER_DEVELOPMENT32_SCORING','seed':seed,'conditions':conditions,'rows':rows_out,
             'gt_source':'MVA_MATRIX_FREEZE.json gt_images_official_order (alpha channel as foreground mask)',
             'mva_matrix_freeze_sha256':sha(a.freeze),
             'rows_sources':{f'mvadapter_development32_seed{seed}_rank{r}':sha(Path(str(a.run_prefix)+f'_seed{seed}_rank{r}')/'ROWS.json') for r in [0,1]},
             'metric_sources':impl['source_hashes'],'source_sha256':sha(Path(__file__)),'elapsed_seconds':time.time()-started,
             'scope':'Development scoring on previously observed MVA50 subset; Fixed GSO cohort; six native camera embedded scanned-color appearance. Reference supplied from native view1. Geometry retained; not physical albedo, PBR or baked quality.'})
  print('WROTE',out)

if __name__=='__main__':main()
