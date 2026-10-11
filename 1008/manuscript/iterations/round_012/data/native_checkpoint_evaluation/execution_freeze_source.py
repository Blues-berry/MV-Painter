"""Prospective native-protocol cohort selected by UID and input validity only."""
import json,datetime,io,contextlib
from native_training_protocol008 import *
from run_native_disabled_gate006 import UIDS
RUN009=OUT/'iteration009_native_checkpoint_evaluation'
CONDITIONS=['disabled','native_unset','native_gfl','native_gfh','budget_fixed_mean','native_gc3','budget_late16','gen_linear']
def main():
 assert not RUN009.exists();RUN009.mkdir();(RUN009/'execution_freeze_source.py').write_bytes(Path(__file__).read_bytes());(RUN009/'execution_input_helper.py').write_bytes(Path(__file__).with_name('native_training_protocol008.py').read_bytes())
 fresh=sorted((OUT/'iteration007_training_audit/fresh_c_objects.txt').read_text().splitlines());train=set((RUN/'train_objects_native_valid.txt').read_text().splitlines());assert len(fresh)==300 and not set(fresh)&train
 old=json.loads((OUT/'ITERATION002_BAKE_HANDOFF.json').read_text());excluded=set(UIDS)|{x['uid'] for x in old['objects']};candidates=[u for u in fresh if u not in excluded];list_path=RUN009/'candidate_objects.txt';list_path.write_text('\n'.join(candidates)+'\n')
 config=OmegaConf.load(RUN/'native512_config.yaml');dataset=dataset_for(config,list_path,base.DATA_ROOT);rows=[];failures=[];torch.set_num_threads(4)
 for i,uid in enumerate(candidates):
  diagnostic=io.StringIO();seed_all(42+i)
  try:
   with contextlib.redirect_stdout(diagnostic):batch=strict_batch(dataset,i,torch.device('cpu'));source=source_for(dataset,i);err=verify_reference_target(batch,source);_,target,normal,depth,geo,mask=prepare_batch(batch,512,'cpu')
   assert torch.isfinite(geo).all() and torch.isfinite(target).all() and torch.isfinite(mask).all();assert mask.sum()>0
  except Exception as exc:failures.append({'uid':uid,'error':f'{type(exc).__name__}: {exc}','loader_diagnostic':diagnostic.getvalue()});continue
  rows.append({'uid':uid,'source_path':str(source),'source_sha256':sha(source),'reference_target_max_error':err,'target_tensor_hash':tensor_hash(target),'geometry_tensor_hash':tensor_hash(geo),'mask_tensor_hash':tensor_hash(mask),'foreground_pixels':float(mask.sum()),'depth_zero_channel_values':sum(dataset.depth_zero_counts.values())})
  if len(rows)==50:break
 uids=[x['uid'] for x in rows];(RUN009/'objects.txt').write_text('\n'.join(uids)+'\n')
 identity={'status':'FROZEN_BEFORE_NEW_CHECKPOINT_OUTPUTS','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uids':uids,'uid_sha256':sha(RUN009/'objects.txt'),'rows':rows,'conditions':CONDITIONS,'excluded_seen_native_and_bake_uids':sorted(excluded),'input_failures':failures,'selection':'sorted Fresh C UID, exclude prior native development and prior10 baking, input criteria only, first50 valid','cohort_exposure':'Fresh C previously used for old protocol research; prospective new native-path cohort, not globally unseen study data','training_uid_overlap':0,'checkpoint':'formal_ddp_training/geotex_step2000.pt only; lower step outputs not consulted','geometry_target_resolution':512,'seed':42,'steps':50,'cfg':2.,'primary_comparison_family':[{'a':'native_unset','b':'disabled','metric':'fg_lpips','direction':'lower'},{'a':'budget_late16','b':'budget_fixed_mean','metric':'fg_lpips','direction':'lower'}],'primary_multiplicity':'Holm over two tests','secondary_family':'PSNR, SSIM, deltaE and all named C3 contrasts, Holm within declared complete family before analysis','resampling_unit':'object, not view','pipeline_identity':'native bare-base with GeoTex; official ControlNet absent, not full unmodified default','source_sha256':sha(Path(__file__)),'input_helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py'))};write(RUN009/'COHORT_AND_ANALYSIS_FREEZE.json',identity);print('Frozen',len(uids),'objects; input failures',len(failures))
if __name__=='__main__':main()
