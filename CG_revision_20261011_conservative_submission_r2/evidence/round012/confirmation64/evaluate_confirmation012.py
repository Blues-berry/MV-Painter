"""Confirmation64 evaluation: collect frozen outputs, score, run preregistered primaries.

Collect mirrors collect_native_development012.py (identity ledger + symlinks),
scoring reuses the frozen score_native_checkpoint009.py unchanged, and the
primaries follow CONFIRMATION64_FREEZE.json: view_projection vs native on
source fg_psnr and source ciede2000, pooled over seeds with objects as the
resampling unit, two-sided paired sign-flip MonteCarlo (200000, seed 20261010,
plus-one) and paired object bootstrap CI (20000, seed 20261010), Holm2 across
the two primaries. Fresh C has historical exposure; no non-inferiority margin or cross-backbone confirmation.
"""
import json,hashlib,shutil,subprocess,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from revision_expansion_common import OUT,write,sha
R12=OUT/'iteration012_condition_interference';R9=OUT/'iteration009_native_checkpoint_evaluation'
FREEZE=R12/'CONFIRMATION64_FREEZE.json'
def pixels(path):return hashlib.sha256(np.asarray(Image_open(path).convert('RGB')).tobytes()).hexdigest()
def Image_open(p):
 from PIL import Image;return Image.open(p)
def collect():
 freeze=json.loads(FREEZE.read_text());uids=freeze['uids'];dest=R12/'confirmation64_evaluation';assert not dest.exists();ledger=[]
 # Verify every frozen cell before creating outputs; no partial-quality selection.
 for seed in freeze['seeds']:
  for mode in freeze['conditions']:
   found={}
   for rank in [0,1]:
    run=R12/f'confirmation64_{mode}_seed{seed}_rank{rank}';ident=json.loads((run/'RUN_IDENTITY.json').read_text());assert ident['status']=='COMPLETE_CONFIRMATION64_GENERATION',run
    protocol=json.loads((run/'PROTOCOL_FREEZE.json').read_text());assert protocol['seed']==seed and protocol['mode']==mode and protocol['cohort_freeze_sha256']==sha(FREEZE)
    for row in ident['outputs']:
     uid=row['uid'];assert uid not in found and uid in set(uids);path=run/f'{uid}.png';assert pixels(path)==row['pixel_sha256'];found[uid]={'path':path,'pixel_sha256':row['pixel_sha256']}
   assert set(found)==set(uids),(seed,mode,len(found))
   ledger.extend({'uid':uid,'condition':mode,'seed':seed,'source_path':str(found[uid]['path']),'source_sha256':sha(found[uid]['path']),'pixel_sha256':found[uid]['pixel_sha256']} for uid in uids)
 assert len(ledger)==len(uids)*len(freeze['seeds'])*len(freeze['conditions'])
 dest.mkdir()
 write(dest/'OUTPUT_REUSE_AND_IDENTITY_LEDGER.json',{'status':'PASS_COMPLETE64_OBJECT_CONDITION_SEED_CELLS','rows':ledger,'resampling_unit':'object; seed and views nested','scope':'Confirmation cohort outputs; preregistered primaries only'})
 for seed in freeze['seeds']:
  seedroot=dest/f'seed{seed}';seedroot.mkdir()
  original={'uids':uids,'rows':[{'uid':r['uid'],'target_tensor_hash':r['target_tensor_hash']} for r in freeze['targets']],'conditions':freeze['conditions'],'status':'SCORING_VIEW_OF_CONFIRMATION64','selection_freeze_sha256':sha(FREEZE),'seed':seed}
  assert [r['uid'] for r in original['rows']]==uids
  write(seedroot/'COHORT_AND_ANALYSIS_FREEZE.json',original);(seedroot/'objects.txt').write_text('\n'.join(uids)+'\n');shutil.copy(R9/'METRIC_CALIBRATION.json',seedroot);shutil.copy(FREEZE,seedroot/'STATISTICAL_PROTOCOL.json')
  for row in ledger:
   if row['seed']!=seed:continue
   target=seedroot/'predictions'/row['condition']/f"{row['uid']}.png";target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(Path(row['source_path']))
 return dest
def signflip(diffs):
 d=np.asarray(diffs,dtype=np.float64);n=len(d);rng=np.random.default_rng(20261010);obs=abs(float(d.mean()))
 flips=rng.choice([-1,1],size=(200000,n));means=np.abs((flips*d).mean(axis=1))
 return {'mean_difference':float(d.mean()),'test_statistic':obs,'p_value':(1+int((means>=obs-1e-12).sum()))/(200000+1),'montecarlo':200000,'plus_one':True}
def bootstrap_ci(diffs):
 d=np.asarray(diffs,dtype=np.float64);rng=np.random.default_rng(20261010);idx=rng.integers(0,len(d),size=(20000,len(d)));means=d[idx].mean(axis=1)
 return [float(np.percentile(means,2.5)),float(np.percentile(means,97.5))]
def main():
 dest=collect();freeze=json.loads(FREEZE.read_text());conds=','.join(freeze['conditions']);name=conds.replace(',','_');uids=freeze['uids'];seeds=freeze['seeds'];table={};score_sources={};rows=[]
 for seed in seeds:
  seedroot=dest/f'seed{seed}'
  result=subprocess.run([sys.executable,str(HERE/'score_native_checkpoint009.py'),'--evaluation-root',str(seedroot),'--training-root',str(OUT/'iteration010_same_v29_base'),'--conditions',conds,'--device','cuda:0'],cwd=HERE.parents[1],capture_output=True,text=True)
  assert result.returncode==0,f'seed {seed} scoring failed: {result.stderr[-2000:]}'
  scorepath=seedroot/f'scores_{name}.json';scores=json.loads(scorepath.read_text());assert scores['status']=='COMPLETE_NATIVE_SLOT_SCORING';score_sources[str(seed)]=sha(scorepath)
  assert len(scores['rows'])==len(uids)*len(freeze['conditions'])
  for row in scores['rows']:
   key=(seed,row['uid'],row['condition']);assert key not in table
   assert row['output_sha256']==sha(seedroot/'predictions'/row['condition']/f"{row['uid']}.png")
   row=dict(row,seed=seed);table[key]=row;rows.append(row)
 assert len(table)==len(uids)*len(seeds)*len(freeze['conditions'])
 scores={'status':'COMPLETE_NATIVE_SLOT_SCORING_ALL_FROZEN_SEEDS','rows':rows,'seed_scores_sha256':score_sources,'freeze_sha256':sha(FREEZE),'source_sha256':sha(Path(__file__))};write(dest/f'scores_{name}.json',scores)
 tests=[]
 for comp,base_c,domain,metric in freeze['primary_comparisons']:
  per_uid=[]
  for uid in uids:
   diffs=[table[(s,uid,comp)][domain][metric]-table[(s,uid,base_c)][domain][metric] for s in seeds]
   per_uid.append(float(np.mean(diffs)))
  t=signflip(per_uid);t.update({'comparison':f'{comp}_minus_{base_c}','domain':domain,'metric':metric,'ci95':bootstrap_ci(per_uid),'n_objects':len(uids),'seeds':seeds,'objects_better':int(sum(d>0 if metric in ['fg_psnr','fg_ssim'] else d<0 for d in per_uid)),'objects_worse':int(sum(d<0 if metric in ['fg_psnr','fg_ssim'] else d>0 for d in per_uid))})
  tests.append(t)
 ps=[t['p_value'] for t in tests];order=np.argsort(ps);m=len(tests);adj=[0.]*m;prev=0.
 for rank,idx in enumerate(order):
  prev=max(prev,min(1.0,(m-rank)*ps[idx]));adj[idx]=prev
 for idx,t in enumerate(tests):t['holm_adjusted_p']=float(adj[idx])
 out={'status':'COMPLETE_CONFIRMATION64_PREREGISTERED_PRIMARIES','freeze_sha256':sha(FREEZE),'scores_sha256':sha(dest/f'scores_{name}.json'),'targets_verified':'target_tensor_hash asserted by frozen scorer against CONFIRMATION64_FREEZE','primaries':tests,'scope':'Pre-generation specified primaries on new-to-development objects within historically exposed Fresh C; no non-inferiority margin or cross-backbone superiority claim.'}
 write(dest/'CONFIRMATION64_TEST.json',out)
 lines=['# Confirmation64 preregistered primaries','','Positive difference favors projection for psnr; for ciede2000 lower is better so positive = worse.','',
  '| comparison | domain | metric | mean diff | 95% CI | sign-flip p | Holm p | better/worse |','|---|---|---|---|---|---|---|---|']
 for t in tests:
  lines.append(f"| {t['comparison']} | {t['domain']} | {t['metric']} | {t['mean_difference']:+.4f} | [{t['ci95'][0]:+.4f}, {t['ci95'][1]:+.4f}] | {t['p_value']:.4f} | {t['holm_adjusted_p']:.4f} | {t['objects_better']}/{t['objects_worse']} |")
 (dest/'CONFIRMATION64_TEST.md').write_text('\n'.join(lines)+'\n')
 print('WROTE',dest/'CONFIRMATION64_TEST.json')
 for t in tests:print(f"  {t['comparison']} {t['metric']}: {t['mean_difference']:+.4f} CI{t['ci95']} p={t['p_value']:.4f} holm={t['holm_adjusted_p']:.4f}")
if __name__=='__main__':main()
