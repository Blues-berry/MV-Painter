"""Build an identity-checked scoring view of frozen native development outputs."""
import argparse,json,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from revision_expansion_common import OUT,sha,write
ROOT=OUT/'iteration012_condition_interference';OLD=OUT/'iteration009_native_checkpoint_evaluation'
def pixels(path):return hashlib.sha256(np.asarray(Image.open(path).convert('RGB')).tobytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);ap.add_argument('--conditions',required=True);a=ap.parse_args();conditions=a.conditions.split(',');assert set(conditions)<={'native','grid_projection','view_projection','interaction_projection'};freeze=ROOT/'DEVELOPMENT32_BASELINE_FREEZE.json';plan=json.loads(freeze.read_text());uids=plan['uids'];assert a.seed in plan['seeds'];dest=ROOT/f"development32_seed{a.seed}_{'_'.join(conditions)}_evaluation";assert not dest.exists();ledger=[]
 for condition in conditions:
  found={}
  if condition=='native' and a.seed==42:
   for uid in uids:found[uid]={'path':OLD/'predictions/v29_full_controlnet'/f'{uid}.png','role':'Previously evaluated original native seed42 output, reuse explicitly recorded'}
  else:
   folders=[ROOT/f'development32_{condition}_seed{a.seed}_rank{rank}' for rank in [0,1]]
   if a.seed==42 and condition in ['grid_projection','view_projection']:folders+=[ROOT/f'{condition}_development_rank{rank}_attempt01' for rank in [0,1]]
   for folder in folders:
    identity=json.loads((folder/'RUN_IDENTITY.json').read_text());assert identity['status'].startswith('COMPLETE_'),folder
    protocol=json.loads((folder/'PROTOCOL_FREEZE.json').read_text());assert protocol['seed']==a.seed
    for row in identity['outputs']:
     uid=row['uid'];assert uid not in found and uid in uids;path=folder/f'{uid}.png';assert pixels(path)==row['pixel_sha256'];found[uid]={'path':path,'role':'R012 development output','source_pixel_sha256':row['pixel_sha256']}
  assert set(found)==set(uids),(condition,len(found));ledger.extend({'uid':uid,'condition':condition,'seed':a.seed,'source_path':str(found[uid]['path']),'source_sha256':sha(found[uid]['path']),'pixel_sha256':pixels(found[uid]['path']),'role':found[uid]['role']} for uid in uids)
 dest.mkdir();original=json.loads((OLD/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());original.update(uids=uids,rows=[r for r in original['rows'] if r['uid'] in set(uids)],conditions=conditions,status='SCORING_VIEW_OF_PREOUTPUT_FROZEN_DEVELOPMENT32',selection_freeze_sha256=sha(freeze),seed=a.seed);assert [r['uid'] for r in original['rows']]==uids;uidtext='\n'.join(uids)+'\n';original['uid_sha256']=hashlib.sha256(uidtext.encode()).hexdigest();write(dest/'COHORT_AND_ANALYSIS_FREEZE.json',original);(dest/'objects.txt').write_text(uidtext);shutil.copy(OLD/'METRIC_CALIBRATION.json',dest);shutil.copy(freeze,dest/'STATISTICAL_PROTOCOL.json');write(dest/'OUTPUT_REUSE_AND_IDENTITY_LEDGER.json',{'status':'PASS_COMPLETE32_OBJECT_CONDITION_CELLS','rows':ledger,'resampling_unit':'object; seed and views nested','scope':'Development outputs; no independent confirmation or novelty claim.'})
 for row in ledger:
  p=dest/'predictions'/row['condition']/f"{row['uid']}.png";p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(Path(row['source_path']))
 print(dest)
if __name__=='__main__':main()
