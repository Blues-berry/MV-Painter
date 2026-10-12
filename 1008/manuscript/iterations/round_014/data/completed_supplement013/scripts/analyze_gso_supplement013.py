"""Complete existing schedule/image/bake comparisons; object-level paired inference."""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.stats import spearmanr
from revision_expansion_common import OUT,write,sha
R=OUT/'iteration012_condition_interference'
SEEDS=[42,2026,31415];METRICS=['fg_psnr','fg_ssim','fg_lpips','ciede2000']
SCHEDULES=['native','fixed_low','fixed_mean','early_high','middle_high','late_high','generic_linear']

def paired(ds):
 ds=np.asarray(ds);rng=np.random.default_rng(20261011);ci=np.percentile(ds[rng.integers(0,len(ds),(20000,len(ds)))].mean(1),[2.5,97.5]);rng=np.random.default_rng(20261011);count=0;obs=abs(ds.mean())
 for _ in range(20):count+=int((abs((rng.choice([-1,1],(10000,len(ds)))*ds).mean(1))>=obs-1e-12).sum())
 return {'mean_difference':float(ds.mean()),'ci95_pointwise':ci.tolist(),'p_raw':(count+1)/200001,'n_objects':len(ds)}

def holm(family):
 previous=0
 for i,t in enumerate(sorted(family,key=lambda t:t['p_raw'])):previous=max(previous,min(1,(len(family)-i)*t['p_raw']));t['p_holm']=previous

def images(root):
 table={}
 for stage in [R/'gso_mva_external_attempt01',R/'gso_apg_closure_attempt01',root]:
  for seed in SEEDS:
   for row in json.loads((stage/f'scores_seed{seed}/scores_mvadapter_seed{seed}.json').read_text())['rows']:
    key=row['uid'],seed,row['condition'];assert key not in table;assert len(row['views'])==6;table[key]={'all':{m:float(np.mean([v[m] for v in row['views']])) for m in METRICS},'nonref':{m:float(np.mean([v[m] for v in row['views'] if v['view']!=1])) for m in METRICS}}
 return table

def contrasts(table,uids,conditions,scope):
 tests=[]
 for a,b in itertools.combinations(conditions,2):
  if {a,b}=={'middle_high','fixed_mean'}:a,b='middle_high','fixed_mean'
  for m in METRICS:
   ds=[np.mean([table[u,s,a][scope][m]-table[u,s,b][scope][m] for s in SEEDS]) for u in uids];tests.append({'a':a,'b':b,'metric':m,**paired(ds),'seed_means':[float(np.mean([table[u,s,a][scope][m]-table[u,s,b][scope][m] for u in uids])) for s in SEEDS]})
 return tests

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--temporal-root',type=Path,required=True);ap.add_argument('--bake-root',type=Path,required=True);ap.add_argument('--extra-bake-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=False)
 uids=json.loads((a.temporal_root/'PROTOCOL_FREEZE.json').read_text())['uids'];table=images(a.temporal_root);assert len(table)==3600
 tests=contrasts(table,uids,SCHEDULES,'all');primary=next(t for t in tests if (t['a'],t['b'],t['metric'])==('middle_high','fixed_mean','fg_psnr'));primary['p_primary']=primary['p_raw'];secondary=[t for t in tests if t is not primary];assert len(secondary)==83;holm(secondary)
 nonref=[t for t in contrasts(table,uids,SCHEDULES,'nonref') if t['metric']=='fg_lpips'];holm(nonref)
 means={c:{m:float(np.mean([table[u,s,c]['all'][m] for u in uids for s in SEEDS])) for m in METRICS} for c in SCHEDULES}
 write(a.out/'TEMPORAL100_COMPARISONS.json',{'primary':primary,'all_six_comparisons':tests,'nonreference_lpips_Holm21':nonref,'means':means,'scope':'Frozen new4 profiles on already-exposed canonicalGSO100; external sensitivity, not pristine confirmation. No algorithm/parameter search. No overallFWER across separate families.'})
 bake={};rows=[];old={}
 for root in [a.bake_root,a.extra_bake_root]:
  for rank in [0,1]:
   for row in json.loads((root/f'rank{rank}/OBJECT_METRICS.json').read_text()):
    key=row['uid'],row['seed'],row['condition'];assert sha(Path(row['glb_path']))==row['glb_sha256'] and row['byte_identity_patch_pass']
    if key in bake:
     assert row['condition']=='gt' and row['glb_sha256']==old[key]['glb_sha256'] and row['mean_unseen']==old[key]['mean_unseen'];continue
    old[key]=row;rows.append(row);bake[key]={'baked':row['mean_unseen']}
 buids=uids[:20];conditions=json.loads((a.bake_root/'PROTOCOL_FREEZE.json').read_text())['conditions']+['fixed_low','early_high','middle_high','generic_linear'];assert len(rows)==740 and len(bake)==740
 assert set(k for k in bake if k[2]!='gt')==set(itertools.product(buids,SEEDS,conditions))
 oldfamily=[]
 for x,y in json.loads((a.bake_root/'PROTOCOL_FREEZE.json').read_text())['comparison_family']:
  for m in METRICS:
   ds=[np.mean([bake[u,s,x]['baked'][m]-bake[u,s,y]['baked'][m] for s in SEEDS]) for u in buids];oldfamily.append({'a':x,'b':y,'metric':m,**paired(ds)})
 holm([t for t in oldfamily if t['metric']=='fg_lpips'])
 btests=contrasts(bake,buids,SCHEDULES,'baked');holm(btests)
 coverage={u:old[u,0,'gt']['unseen_full_bilinear_footprint_coverage'] for u in buids};gtmean={m:float(np.mean([bake[u,0,'gt']['baked'][m] for u in buids])) for m in METRICS}
 bmeans={c:{m:float(np.mean([bake[u,s,c]['baked'][m] for u in buids for s in SEEDS])) for m in METRICS} for c in conditions}
 ranks=[]
 for u in buids:
  gi=[float(np.mean([table[u,s,c]['nonref']['fg_lpips'] for s in SEEDS])) for c in conditions];bi=[float(np.mean([bake[u,s,c]['baked']['fg_lpips'] for s in SEEDS])) for c in conditions];rho=float(spearmanr(gi,bi).statistic);ranks.append({'uid':u,'rho':rho if np.isfinite(rho) else None,'conditions':conditions,'image_lpips':gi,'baked_lpips':bi})
 rr=np.array([x['rho'] for x in ranks if x['rho'] is not None]);rng=np.random.default_rng(20261011);rci=np.percentile(rr[rng.integers(0,len(rr),(20000,len(rr)))].mean(1),[2.5,97.5]).tolist()
 write(a.out/'BAKE20_COMPARISONS.json',{'original_Holm16_family':oldfamily,'schedule_all84_Holm_family':btests,'means':bmeans,'gt_self_bake_mean':gtmean,'coverage':coverage,'ranking_mean':float(rr.mean()),'ranking_object_ci95':rci,'ranking_rows':ranks,'rows':rows,'scope':'Full20 fixed inputs; revisedGT-only calibration after15 original outcomes; original rawUV diagnostic failures retained. All foreground main scores; coverage diagnostic, no GT error subtraction. Twelve methods,3seeds,11views nested within object.'})
 # Verify the original15 completed objects reproduce exactly, rather than silently changing the bake.
 oldrows=[]
 for rank in [0,1]:oldrows+=json.loads((R/f'gso_bake_closure_attempt01/rank{rank}/OBJECT_METRICS.json').read_text())
 for row in oldrows:
  new=old[row['uid'],row['seed'],row['condition']];assert row['glb_sha256']==new['glb_sha256'] and row['mean_unseen']==new['mean_unseen']
 write(a.out/'REPRODUCED_ORIGINAL15.json',{'status':'PASS_ALL375_EXISTING_GLB_HASHES_AND_METRICS_EXACT','cells':len(oldrows)})
 with (a.out/'BAKE_VIEW_METRICS.csv').open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=['uid','condition','seed','view',*METRICS]);writer.writeheader()
  for row in rows:
   for v in row['views']:writer.writerow({'uid':row['uid'],'condition':row['condition'],'seed':row['seed'],**v})
 visuals=a.out/'visuals';visuals.mkdir()
 for u in buids[:4]:
  canvas=Image.new('RGB',(4*256,4*282),'white');draw=ImageDraw.Draw(canvas)
  paths=[('source_gt',a.bake_root/f'rank{buids.index(u)%2}'/u/'source_unseen/view_00.png')]
  for c in conditions:paths.append((c,Path(old[u,42,c]['glb_path']).parent/f'{c}_seed42_unseen/view_00.png'))
  for i,(label,path) in enumerate(paths):x=(i%4)*256;y=(i//4)*282;canvas.paste(Image.open(path).convert('RGB').resize((256,256)),(x,y+26));draw.text((x+3,y+5),label,fill='black')
  canvas.save(visuals/f'{u}.png')
 lines=['# Existing-schedule supplementary validation complete','','No new algorithm. Same fixedGSO100 inputs and native interface; no profile search. New4 profiles frozen before outputs, after baseline exposure. Bake calibration addendum is post hoc and rawUV failure retained.','',f'Middle-high minusFixedMean primary all-six FG-PSNR: {primary}',f'GT self-bake mean: {gtmean}',f'Baked/image method-rank mean Spearman: {float(rr.mean()):.6f}, objectCI {rci}','Original375 baked records reproduce exactly. All740 finalbakes retained.','','| Bake condition | PSNR | LPIPS | SSIM | dE00 |','|---|---:|---:|---:|---:|']
 for c,m in bmeans.items():lines.append(f"| {c} | {m['fg_psnr']:.4f} | {m['fg_lpips']:.6f} | {m['fg_ssim']:.6f} | {m['ciede2000']:.4f} |")
 (a.out/'REPORT.md').write_text('\n'.join(lines)+'\n');write(a.out/'STATUS.json',{'status':'COMPLETE_SUPPLEMENTARY_SCHEDULE_IMAGE_AND_BAKE_ANALYSIS','generation_cells':3600,'new_generation_cells':1200,'bake_cells':740,'bake_view_rows':8140,'objects_image':100,'objects_bake':20,'reproduced_prior_cells':375})
if __name__=='__main__':main()
