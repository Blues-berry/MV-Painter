"""Recover recorded checkpoint training protocol without assuming exact replay."""
from pathlib import Path
import ast,csv,json,subprocess,hashlib,shutil,torch
from omegaconf import OmegaConf
from revision_expansion_common import OUT,sha,write
RUN=OUT/'iteration007_training_audit';ROOT=Path('/4T/CXY/MV-Painter');H=ROOT/'mvpoutput/reviewer1_main_rerun_20260928';COMMIT='f2f0019a008277213af0127fa7cb628cb5fa1eef'
def main():
 assert not RUN.exists();RUN.mkdir();(RUN/'execution_source.py').write_bytes(Path(__file__).read_bytes())
 text=(H/'training_manifest.json').read_text();manifest,end=json.JSONDecoder().raw_decode(text);suffix=text[end:];assert suffix.strip()=='\\n'
 records=['training_manifest.json','training_config_snapshot.yaml','training_command.txt','train_summary.json','train_metrics.csv','train_objects_full_1118.txt']
 for n in records:shutil.copy2(H/n,RUN/n)
 config=OmegaConf.load(H/'training_config_snapshot.yaml');train=(H/'train_objects_full_1118.txt').read_text().splitlines();fresh=(ROOT/'1006/data/fresh_c/fresh_c_objects.txt').read_text().splitlines()
 assert sha(H/'train_objects_full_1118.txt')==manifest['train_list_sha256'];checkpoint=H/manifest['checkpoint'];assert sha(checkpoint)==manifest['checkpoint_sha256']
 snap={}
 for rel in ['geotex/train.py','MVPainter/mvpainter/model_unet_geotex.py','MVPainter/src/data/mvpainter_dataset.py']:
  raw=subprocess.check_output(['git','show',COMMIT+':'+rel],cwd=ROOT);name=rel.replace('/','__');(RUN/name).write_bytes(raw)
  present=Path('/tmp/mv_main_rerun')/rel
  snap[rel]={'source_commit_sha256':hashlib.sha256(raw).hexdigest(),'surviving_tree_sha256':sha(present),'surviving_tree_equals_recorded_commit':raw==present.read_bytes()}
  if raw!=present.read_bytes():shutil.copy2(present,RUN/('surviving__'+name))
 code=(RUN/'geotex__train.py').read_text();tree=ast.parse(code)
 drop_reads=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and n.attr=='drop_cond_prob'];drop_values=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.keyword) and n.arg=='is_drop':drop_values.append(ast.literal_eval(n.value))
 assert not drop_reads and drop_values and all(x is False for x in drop_values)
 metrics=list(csv.DictReader((H/'train_metrics.csv').open()));assert [int(x['step']) for x in metrics]==list(range(1,2001))
 missing=[];root=Path(config.data.params.train.params.root_dir_list[0])
 for uid in train:
  absent=[f'{kind}/{i:03d}.png' for kind in ['image','normal','depth_png'] for i in [0,12,13,14,15,16] if not (root/uid/kind/f'{i:03d}.png').exists()]
  if absent:missing.append({'uid':uid,'missing':absent})
 state=torch.load(checkpoint,map_location='cpu',weights_only=False)
 result={'status':'COMPLETE_RECORDED_TRAINING_AUDIT_WITH_REPLAY_LIMITS','source_sha256':sha(Path(__file__)),'recorded_source_commit':COMMIT,'source_comparisons':snap,'recorded_artifact_hashes':{n:sha(RUN/n) for n in records},'manifest_trailing_literal_newline':repr(suffix),'checkpoint_sha256':sha(checkpoint),'checkpoint_keys':list(state),'checkpoint_has_embedded_step':any(k in state for k in ['step','global_step']),'train_uid_count':len(train),'fresh_uid_count':len(fresh),'train_fresh_overlap':sorted(set(train)&set(fresh)),'training_image_size':int(config.model.params.img_size),'configured_drop_cond_prob':float(config.model.params.drop_cond_prob),'actual_entry_reads_drop_cond_prob':False,'actual_entry_is_drop_values':drop_values,'actual_entry_has_unconditional_branch':False,'metric_steps_complete_1_to_2000':True,'recorded_final_loss':float(metrics[-1]['loss']),'structural_input_missing':missing,'structural_inputs_complete_count':len(train)-len(missing),'training_target_view_mode_explicit_in_snapshot':'target_view_mode' in config.data.params.train.params,'historical_dataset_target_lists':[[14,15,0,15,12,13],[0,15,12,15,13,14]],'replay_limits':['recorded runtime list override differs from YAML snapshot; transient wrapper is not preserved','training entry has no explicit seed setup; exact sampling order cannot be replayed from these artifacts','surviving dataset differs from source commit; executed dataset version is not fully authenticated','checkpoint has no embedded step; filename/manifest and complete step CSV are recorded lineage evidence','this main-adapter audit does not restore historical FAC training or explain failures causally'],'interpretation':'Recorded trainer uses conditional-only B1 training at256 and ignores configured conditioning dropout. Inserting geometry into the native unconditional CFG branch is not supported by this trainer. Duplicate-top targets and inference-size differences are additional compatibility concerns; causal attribution remains unproven.'}
 write(RUN/'TRAINING_AUDIT.json',result);print({k:result[k] for k in ['train_uid_count','train_fresh_overlap','structural_inputs_complete_count','actual_entry_reads_drop_cond_prob','checkpoint_keys']})
if __name__=='__main__':main()
