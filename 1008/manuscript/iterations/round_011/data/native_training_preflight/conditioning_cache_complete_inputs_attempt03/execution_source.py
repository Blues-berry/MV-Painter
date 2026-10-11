"""Prepare native positive/negative conditioning on GPU1, without denoising."""
import json,time,datetime,io,contextlib,shutil
from pathlib import Path
from native_training_protocol008 import *
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline

def main():
 run=RUN/'conditioning_cache_complete_inputs_attempt03';assert not run.exists();gpu=base.gpu_snapshot('cuda:1');sources=base.verify_sources();run.mkdir(parents=True)
 audit=json.loads((OUT/'iteration007_training_audit/TRAINING_AUDIT.json').read_text());missing={x['uid'] for x in audit['structural_input_missing']}
 train=(OUT/'iteration007_training_audit/train_objects_full_1118.txt').read_text().splitlines();uids=sorted(x for x in train if x not in missing);fresh=set((OUT/'iteration007_training_audit/fresh_c_objects.txt').read_text().splitlines());assert len(uids)==1112 and not set(uids)&fresh
 list_path=RUN/'train_objects_1112.txt';list_path.write_text('\n'.join(uids)+'\n')
 config=OmegaConf.load(base.load_launcher_helpers().CONFIG);config.model.params.img_size=512;OmegaConf.save(config,RUN/'native512_config.yaml')
 identity={'status':'FROZEN_CACHE_PREPARATION','uid_count':len(uids),'uid_sha256':sha(list_path),'source_sha256':sha(Path(__file__)),'helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py')),'gpu':gpu,'frozen_sources':sources,'seed':42,'random_resize_ratio':1.,'target_view_mode':'unique6','dropout_payloads':['positive','negative'],'native_denoiser_calls':0,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(run/'RUN_IDENTITY.json',identity)
 (run/'execution_source.py').write_bytes(Path(__file__).read_bytes());(run/'execution_helper.py').write_bytes(Path(__file__).with_name('native_training_protocol008.py').read_bytes())
 torch.set_num_threads(4);device=torch.device('cuda:1');dataset=dataset_for(config,list_path,Path(config.data.params.train.params.root_dir_list[0]))
 pipe=MVPainter_Pipeline.from_pretrained(str(base.load_launcher_helpers().BASE_MODEL),torch_dtype=torch.float16,use_safetensors=True).to(device);pipe.prepare();rows=[];failures=[]
 previous=RUN/'conditioning_cache';prior={x['uid']:x for x in json.loads((previous/'ROWS.json').read_text())}
 try:
  for i,uid in enumerate(uids):
   seed_all(42+i);diagnostic=io.StringIO()
   try:
    with contextlib.redirect_stdout(diagnostic):
     batch=strict_batch(dataset,i,torch.device('cpu'));source=source_for(dataset,i);error=verify_reference_target(batch,source)
   except Exception as exc:
    failures.append({'uid':uid,'stage':'input validation before native conditioning','error':f'{type(exc).__name__}: {exc}','loader_diagnostic':diagnostic.getvalue()});write(run/'INPUT_FAILURES.json',failures);continue
   start=time.time();path=run/f'{uid}.pt';reused=None
   if uid in prior:
    previous_file=previous/f'{uid}.pt';old=prior[uid];assert sha(source)==old['source_sha256'] and sha(previous_file)==old['cache_sha256']
    payload=torch.load(previous_file,map_location='cpu',weights_only=False);assert payload_hashes(payload)==old['payload_hashes'];shutil.copy2(previous_file,path);reused=str(previous_file)
   else:
    payload=capture_native_conditioning(pipe,source,device,42);torch.save(payload,path)
   row={'uid':uid,'source_path':str(source),'source_sha256':sha(source),'cache_sha256':sha(path),'payload_hashes':payload_hashes(payload),'target_reference_max_error':error,'depth_zero_channel_values':sum(dataset.depth_zero_counts.values()),'elapsed_seconds':time.time()-start,'reused_from':reused}
   rows.append(row);write(run/'ROWS.json',rows)
   if (i+1)%25==0 or i<2:print('Cached',i+1,'/',len(uids),uid,flush=True)
  (RUN/'train_objects_native_valid.txt').write_text('\n'.join(x['uid'] for x in rows)+'\n')
  identity.update(status='COMPLETE_NATIVE_CONDITIONING_CACHE_WITH_INPUT_LEDGER',rows=rows,input_failures=failures,eligible_uid_count=len(rows),eligible_uid_sha256=sha(RUN/'train_objects_native_valid.txt'),peak_allocated_bytes=torch.cuda.max_memory_allocated(device),peak_reserved_bytes=torch.cuda.max_memory_reserved(device));write(run/'RUN_IDENTITY.json',identity)
 except Exception as exc:
  identity.update(status='FAILED_NATIVE_CONDITIONING_CACHE',error=f'{type(exc).__name__}: {exc}',completed_rows=rows);write(run/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
