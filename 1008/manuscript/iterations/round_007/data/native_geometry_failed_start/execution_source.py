"""Seen-case native-loop geometry matrix, frozen schedules and observed wrapper calls."""
import sys,json,time,random,datetime,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
from revision_expansion_common import OUT,sha,write
import run_fresh_c_glb_method_matrix as base
sys.path[:0]=['/4T/CXY/MV-Painter/MVPainter','/4T/CXY/MV-Painter/geotex','/4T/CXY/MV-Painter']
import torch
from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from data_utils import collate_batch,prepare_batch
import geotex.eval_exploration as ee
from mvpainter.model_unet_geotex import GeoTexResnetWrapper
from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet
from run_native_disabled_gate006 import tensor_hash,UIDS
RUN=OUT/'iteration006_native_geometry_matrix'
CONDITIONS=['disabled','native_unset','native_gfl','native_gfh','budget_fixed_mean','native_gc3','budget_late16','gen_linear']
def main():
 assert not RUN.exists(),'No overwrite'
 gate=json.loads((OUT/'iteration006_native_disabled_gate/RUN_IDENTITY.json').read_text());assert gate['disabled_pixels_identical_to_bare_native']
 gpu=base.gpu_snapshot('cuda:0');sources=base.verify_sources();RUN.mkdir()
 (RUN/'objects.txt').write_text('\n'.join(UIDS)+'\n')
 spec=importlib.util.spec_from_file_location('frozen_native_matrix_schedules',base.RUNNER_SOURCE);registry=importlib.util.module_from_spec(spec);spec.loader.exec_module(registry)
 schedules={n:registry.CONDITIONS[n]['fn'] for n in ['native_gfl','native_gfh','native_gc3','gen_linear']}
 schedules.update(budget_fixed_mean=lambda _:1.65,budget_late16=lambda p:2.5 if round(p*49)>=34 else 1.25)
 identity={'status':'FROZEN_NATIVE_GEOMETRY_MATRIX','objects':UIDS,'conditions':CONDITIONS,'source_sha256':sha(Path(__file__)),'schedule_registry_sha256':sha(base.RUNNER_SOURCE),'gpu_before':gpu,'frozen_asset_identity':sources,'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'two seen cases; native512 CFG2 EulerAncestral; fixed trained256 geometry encoding interpolated by wrappers; geometry broadcasts to both CFG branches; no GT inference','geometry_input_resolution':256,'geometry_cfg_branch_semantics':'same B1 geometry broadcasts to B2 hidden-state-dependent gates, both negative and positive branches; reference write skips corrections'}
 write(RUN/'RUN_IDENTITY.json',identity);(RUN/'execution_source.py').write_bytes(Path(__file__).read_bytes())
 config=OmegaConf.load(base.load_launcher_helpers().CONFIG);val=config.data.params.validation
 val.params.object_list_file=str(RUN/'objects.txt');val.params.target_view_mode='unique6';val.params.root_dir_list=[str(base.DATA_ROOT)];dataset=instantiate_from_config(val)
 device=torch.device('cuda:0');torch.set_num_threads(6)
 model=ee.load_model(str(base.load_launcher_helpers().CONFIG),str(base.load_launcher_helpers().CHECKPOINT),device);pipe=model.pipeline
 assert isinstance(pipe.unet,RefOnlyNoisedUNet);pipe.prepare_init=True
 for enc in [pipe.vision_encoder,pipe.vision_encoder_2]:enc.to(device,dtype=torch.float16).eval()
 wrappers=[m for m in pipe.unet.modules() if isinstance(m,GeoTexResnetWrapper)];assert len(wrappers)==9
 records={r['uid']:r for r in json.loads((OUT/'ITERATION002_BAKE_HANDOFF.json').read_text())['objects']};rows=[]
 try:
  for idx,uid in enumerate(UIDS):
   object_rows=[]
   for condition in CONDITIONS:
    random.seed(42+idx);np.random.seed(42+idx);torch.manual_seed(42+idx)
    batch=collate_batch(dataset,idx,device)
    with torch.no_grad():
     *_,geo_input,mask=prepare_batch(batch,model.img_size,device)
     geo_clean=torch.nan_to_num(geo_input.float().clamp(0,1),nan=0.,posinf=1.,neginf=0.);features=model.geo_encoder(geo_clean)
    model._clear_geo_feats_on_wrappers()
    for w in wrappers:
     if hasattr(w,'_adapter_scale'):del w._adapter_scale
    if condition!='disabled':model._set_geo_feats_on_wrappers(features)
    rec=records[uid];source=Path(rec['gt_rgba_17'][rec['target_view_mapping'][0]['raw_view_index']]);pil=Image.open(source).convert('RGBA')
    trace={'unet_calls':0,'initial_latent':None,'rng_states':[],'scales':[],'read_counts':[0]*9,'skip_counts':[0]*9,'correction_shapes':{}}
    original=pipe.prepare_latents
    def observe_prepare(*args,**kw):
     result=original(*args,**kw);trace['initial_latent']=tensor_hash(result);return result
    def before(module,args,kw):
     sample=args[0] if args else kw['sample'];assert sample.shape[0]==2
     step=trace['unet_calls'];assert step<50
     trace['rng_states'].append(tensor_hash(torch.cuda.get_rng_state(device)))
     requested=None if condition in ['disabled','native_unset'] else schedules[condition](step/49)
     trace['scales'].append(requested)
     if requested is not None:
      for w in wrappers:w._adapter_scale=requested.get(w.depth_group,1.) if isinstance(requested,dict) else requested
     trace['unet_calls']+=1
    def wrapper_after(i):
     def observe(module,args,output):
      if GeoTexResnetWrapper._skip_correction:trace['skip_counts'][i]+=1
      else:
       trace['read_counts'][i]+=1
       if condition!='disabled':
        corr=module._last_correction;assert corr is not None and corr.shape[0]==2 and torch.isfinite(corr).all();trace['correction_shapes'][str(i)]=list(corr.shape)
     return observe
    pipe.prepare_latents=observe_prepare;hooks=[pipe.unet.register_forward_pre_hook(before,with_kwargs=True)]+[w.register_forward_hook(wrapper_after(i)) for i,w in enumerate(wrappers)]
    torch.manual_seed(42);generator=torch.Generator(device=device).manual_seed(42);start=time.time()
    try:
     with torch.no_grad():result=pipe(pil,num_inference_steps=50,generator=generator,guidance_scale=2.,depth_image=None,output_type='pil')
    finally:
     for h in hooks:h.remove()
     pipe.prepare_latents=original;model._clear_geo_feats_on_wrappers()
    assert trace['unet_calls']==50 and trace['read_counts']==[50]*9 and trace['skip_counts']==[50]*9
    path=RUN/'predictions'/condition/f'{uid}.png';path.parent.mkdir(parents=True,exist_ok=True);result[0].save(path)
    assert result[0].size==(1024,1536)
    if condition=='disabled':
     old=OUT/'iteration006_native_disabled_gate/predictions/native_base_50'/f'{uid}.png';assert np.array_equal(np.asarray(result[0]),np.asarray(Image.open(old)))
    if object_rows:assert trace['initial_latent']==object_rows[0]['trace']['initial_latent'] and trace['rng_states']==object_rows[0]['trace']['rng_states']
    row={'uid':uid,'condition':condition,'output_path':str(path),'output_sha256':sha(path),'source_rgba_sha256':sha(source),'conditioning_tensor_hash':tensor_hash(batch['cond_imgs']),'geometry_input_hash':tensor_hash(geo_clean),'geometry_feature_hashes':{k:tensor_hash(v) for k,v in features.items()},'elapsed_seconds':time.time()-start,'trace':trace}
    rows.append(row);object_rows.append(row);write(RUN/'ROWS.json',rows);print('Saved',uid,condition,flush=True)
  identity.update(status='COMPLETE_NATIVE_GEOMETRY_MATRIX',rows=rows,disabled_identity_pass=True,within_object_latent_rng_match=True,all_wrapper_counts_pass=True);write(RUN/'RUN_IDENTITY.json',identity)
 except Exception as exc:
  identity.update(status='FAILED_NATIVE_GEOMETRY_MATRIX',error=f'{type(exc).__name__}: {exc}',completed_rows=rows);write(RUN/'RUN_IDENTITY.json',identity);raise
if __name__=='__main__':main()
