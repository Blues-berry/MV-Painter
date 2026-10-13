"""Fixed native-camera projection -> byte-preserved GLB ->11 unseen-view metrics."""
import argparse,io,json,sys
from pathlib import Path
import numpy as np,torch,trimesh
from PIL import Image
from revision_expansion_common import OUT,sha,write
from patch_glb_basecolor_texture import patch_basecolor_texture,read_glb,BIN_CHUNK
from evaluate_fresh_c_native_egl import load_metric_implementations
R=OUT/'iteration012_condition_interference';EXTERNAL=R/'gso_mva_external_attempt01'
def embedded_texture(path):
 doc,chunks=read_glb(path);pbr=doc['materials'][0]['pbrMetallicRoughness'];info=doc['images'][doc['textures'][pbr['baseColorTexture']['index']]['source']];view=doc['bufferViews'][info['bufferView']];blob=next(b for k,b in chunks if k==BIN_CHUNK);start=view.get('byteOffset',0);return np.asarray(Image.open(io.BytesIO(blob[start:start+view['byteLength']])).convert('RGB'),np.float32)/255

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--rank',type=int,choices=[0,1],required=True);ap.add_argument('--device',required=True);ap.add_argument('--gate-only',action='store_true');ap.add_argument('--additional-rows-prefix',type=Path);a=ap.parse_args();assert not a.out.exists();a.out.mkdir();plan=json.loads(a.plan.read_text());f=json.loads((EXTERNAL/'targets/MATRIX_FREEZE.json').read_text());objects=f['objects'][:20];assert [x['object_uid'] for x in objects]==plan['uids'];sys.path.insert(0,f['deployed_source_root']);from mvadapter.utils.mesh_utils import CameraProjection,NVDiffRastContextWrapper,get_orthogonal_camera,load_mesh,render;from mvadapter.utils.mesh_utils.uv import uv_precompute
 torch.set_num_threads(4);torch.cuda.set_device(a.device);ctx=NVDiffRastContextWrapper(a.device);proj=CameraProjection(pb_backend='torch-native',bg_remover=None,device=a.device)
 camkw=dict(distance=[1.8]*6,left=-.55,right=.55,bottom=-.55,top=.55,device=a.device)
 cameras=get_orthogonal_camera(elevation_deg=[0,0,0,0,89.99,-89.99],azimuth_deg=[-90,0,90,180,90,90],**camkw)
 unseen=get_orthogonal_camera(elevation_deg=plan['unseen_elevations'],azimuth_deg=plan['unseen_azimuths'],distance=[1.8]*11,left=-.55,right=.55,bottom=-.55,top=.55,device=a.device)
 metrics=load_metric_implementations();lp=None if a.gate_only else metrics['get_lpips_fn'](torch.device(a.device));assert a.gate_only or lp is not None
 rows=[];gates=[]
 def project(images,mesh,masks):
  result=proj(images,mesh,cameras,masks=masks,uv_size=1024,from_scratch=True,poisson_blending=False,uv_padding=False,depth_grad_dilation=5,depth_grad_threshold=.1,uv_exp_blend_alpha=3,uv_exp_blend_view_weight=torch.ones(6,device=a.device),aoi_cos_valid_threshold=.2,return_dict=True)
  assert result is not None and torch.isfinite(result.uv_proj).all() and result.uv_proj_mask.any();return result
 selected=objects[:3] if a.gate_only else [x for i,x in enumerate(objects) if i%2==a.rank]
 for obj in selected:
  uid=obj['object_uid'];source=Path(obj['mesh_path']);assert sha(source)==obj['mesh_sha256'];mesh=load_mesh(str(source),rescale=True,default_uv_size=1024,device=a.device);source_tex=embedded_texture(source);folder=a.out/uid;folder.mkdir()
  rgba=[]
  for g in obj['gt_images_official_order']:assert sha(g['path'])==g['sha256'];rgba.append(np.asarray(Image.open(g['path']).convert('RGBA'),np.float32)/255)
  masks=torch.as_tensor(np.stack([im[...,3] for im in rgba]),device=a.device);gt_images=torch.as_tensor(np.stack([im[...,:3] for im in rgba]),device=a.device)
  with torch.inference_mode():
   control=render(ctx,mesh,cameras,height=512,width=512,render_attr=False);assert torch.equal(control.mask,masks>.5),'Native target mask not aligned with bake cameras'
   const=project(torch.full_like(gt_images,.25),mesh,masks);constant_err=float((const.uv_proj[const.uv_proj_mask]-.25).abs().max());assert constant_err<1e-4,constant_err
   coord=torch.linspace(.5/1024,1-.5/1024,1024,device=a.device);yy,xx=torch.meshgrid(coord,coord,indexing='ij');ramp=torch.stack([xx,yy,.25+xx*.25+yy*.25],-1);ramp_views=render(ctx,mesh,cameras,height=512,width=512,texture_override=ramp,attr_background=1.).attr;back=project(ramp_views,mesh,masks);valid=back.uv_proj_mask.clone();valid[:3,:]=False;valid[-3:,:]=False;valid[:,:3]=False;valid[:,-3:]=False;error=(back.uv_proj[valid]-ramp[valid]).abs();assert error.numel()>0;meanerr=float(error.mean());q99=float(torch.quantile(error.flatten(),.99));assert meanerr<.03,(uid,meanerr,q99)
   position_views=render(ctx,mesh,cameras,height=512,width=512,render_attr=False).pos;colors=(position_views+.5).clamp(0,1);colors=torch.stack([colors[...,0],colors[...,1]**2,colors[...,2]**3],-1);colors[masks<=.5]=1;world_back=project(colors,mesh,masks);uvpos=uv_precompute(ctx,mesh,1024,1024).uv_pos;truth_colors=(uvpos+.5).clamp(0,1);truth_colors=torch.stack([truth_colors[...,0],truth_colors[...,1]**2,truth_colors[...,2]**3],-1);world_error=(world_back.uv_proj[world_back.uv_proj_mask]-truth_colors[world_back.uv_proj_mask]).abs();world_mean=float(world_error.mean());world_q99=float(torch.quantile(world_error.flatten(),.99));assert world_mean<.03 and world_q99<.15,(uid,world_mean,world_q99);assert torch.equal(world_back.uv_proj_mask,back.uv_proj_mask)
   assert (q99<.15) or uid in plan['calibration_addendum']['raw_uv_ramp_aliasing_objects'],(uid,'Unexpected raw UV diagnostic failure')
   gt_bake=project(gt_images,mesh,masks);coverage=gt_bake.uv_proj_mask.clone();assert torch.equal(coverage,const.uv_proj_mask) and torch.equal(coverage,back.uv_proj_mask),'Color changed UV coverage';gate={'uid':uid,'constant_max_abs_error':constant_err,'ramp_mean_abs_error':meanerr,'ramp_q99_abs_error':q99,'raw_uv_ramp_original_gate_pass':q99<.15,'continuous_world_mean_error':world_mean,'continuous_world_q99_error':world_q99,'uv_covered_pixels':int(coverage.sum()),'source_resolution':512,'texture_resolution':1024,'target_mask_identity':True};gates.append(gate);write(a.out/'CALIBRATION_GATES.json',gates)
   source_render=render(ctx,mesh,unseen,height=512,width=512,texture_override=torch.as_tensor(source_tex.copy(),device=a.device),attr_background=1.);truth=source_render.attr;eval_masks=source_render.mask;coverage_view=render(ctx,mesh,unseen,height=512,width=512,texture_override=coverage.float()[...,None].expand(-1,-1,3).contiguous(),attr_background=0.).attr[...,0];coverage_fractions=[float((coverage_view[v][eval_masks[v]]>=1-1e-6).float().mean()) for v in range(11)];gate['unseen_full_bilinear_footprint_coverage']=coverage_fractions;write(a.out/'CALIBRATION_GATES.json',gates)
   def render_and_score(texture,condition,seed):
    png=folder/f'{condition}_seed{seed}_texture.png';Image.fromarray(np.rint(np.clip(texture.cpu().numpy(),0,1)*255).astype(np.uint8)).save(png);glb=folder/f'{condition}_seed{seed}.glb';patch=patch_basecolor_texture(source,png,glb,expected_resolution=1024);assert patch['status']=='PASS';loaded=load_mesh(str(glb),rescale=True,default_uv_size=1024,device=a.device)
    for name in ['v_pos','t_pos_idx','v_tex','t_tex_idx']:assert torch.equal(getattr(mesh,name),getattr(loaded,name)),name
    reloaded_texture=embedded_texture(glb);assert np.array_equal(np.rint(reloaded_texture*255).astype(np.uint8),np.asarray(Image.open(png).convert('RGB')))
    output=render(ctx,loaded,unseen,height=512,width=512,texture_override=torch.as_tensor(reloaded_texture.copy(),device=a.device),attr_background=1.);assert torch.equal(output.mask,eval_masks);renderfolder=folder/f'{condition}_seed{seed}_unseen';renderfolder.mkdir();values=[]
    for v in range(11):
     pred=output.attr[v].permute(2,0,1)[None];gt=truth[v].permute(2,0,1)[None];mask=eval_masks[v][None,None].float();prgb=output.attr[v].cpu().numpy();grgb=truth[v].cpu().numpy();m=eval_masks[v].cpu().numpy();assert m.any();scores={'fg_psnr':float(metrics['compute_psnr'](pred,gt,mask)),'fg_ssim':float(metrics['compute_ssim'](pred,gt,mask)),'fg_lpips':float(metrics['compute_lpips'](pred,gt,mask,lpips_fn=lp,device=torch.device(a.device))),'ciede2000':float(metrics['masked_ciede2000'](prgb,grgb,m,erosion_radius=1))};assert all(np.isfinite(x) for x in scores.values());Image.fromarray(np.rint(np.clip(prgb,0,1)*255).astype(np.uint8)).save(renderfolder/f'view_{v:02d}.png');values.append({'view':v,**scores})
    rows.append({'uid':uid,'condition':condition,'seed':seed,'mean_unseen':{k:float(np.mean([x[k] for x in values])) for k in values[0] if k!='view'},'views':values,'glb_path':str(glb),'glb_sha256':sha(glb),'texture_sha256':sha(png),'uv_coverage_pixels':int(coverage.sum()),'unseen_full_bilinear_footprint_coverage':coverage_fractions,'byte_identity_patch_pass':True});write(a.out/'OBJECT_METRICS.json',rows);print('BAKE_EVAL_COMPLETE',uid,condition,seed,flush=True)
   if a.gate_only:
    png=folder/'calibration_gt_texture.png';Image.fromarray(np.rint(np.clip(gt_bake.uv_proj.cpu().numpy(),0,1)*255).astype(np.uint8)).save(png);patch=patch_basecolor_texture(source,png,folder/'calibration_gt.glb',expected_resolution=1024);assert patch['status']=='PASS';loaded=load_mesh(str(folder/'calibration_gt.glb'),rescale=True,default_uv_size=1024,device=a.device);assert torch.equal(mesh.v_pos,loaded.v_pos) and torch.equal(mesh.t_pos_idx,loaded.t_pos_idx);print('BAKE_GATE_PASS',uid,flush=True);continue
   truth_folder=folder/'source_unseen';truth_folder.mkdir()
   for v in range(11):Image.fromarray(np.rint(np.clip(truth[v].cpu().numpy(),0,1)*255).astype(np.uint8)).save(truth_folder/f'view_{v:02d}.png')
   render_and_score(gt_bake.uv_proj,'gt',0)
   for seed in plan['seeds']:
    index=next(i for i,o in enumerate(f['objects']) if o['object_uid']==uid);run=EXTERNAL/f'matrix_seed{seed}_rank{index%2}';original=json.loads((run/'ROWS.json').read_text());apg=R/'gso_apg_closure_attempt01'/f'matrix_seed{seed}_rank{index%2}';original+=json.loads((apg/'ROWS.json').read_text());
    if a.additional_rows_prefix:original+=json.loads((Path(str(a.additional_rows_prefix)+f'_seed{seed}_rank{index%2}')/'ROWS.json').read_text())
    bycond={x['condition']:x for x in original if x['uid']==uid};assert set(plan['conditions']).issubset(bycond)
    for condition in plan['conditions']:
     row=bycond[condition];import hashlib
     h=hashlib.sha256(b''.join(np.asarray(Image.open(x).convert('RGB')).tobytes() for x in row['output_files'])).hexdigest();assert h==row['pixel_sha256'];images=torch.as_tensor(np.stack([np.asarray(Image.open(x).convert('RGB'),np.float32)/255 for x in row['output_files']]),device=a.device);baked=project(images,mesh,masks);assert torch.equal(baked.uv_proj_mask,coverage),'Condition-dependent UV coverage';render_and_score(baked.uv_proj,condition,seed)
  print('BAKE_OBJECT_COMPLETE',uid,flush=True)
 write(a.out/'STATUS.json',{'status':'PASS_BAKE_GATE_ONLY' if a.gate_only else 'COMPLETE_BAKED_UNSEEN_EVALUATION','objects':len(selected),'metric_rows':len(rows),'rank':a.rank,'scope':'Native deterministic projection; original geometry and materials retained; scanned RGB appearance, no PBR/material truth claim.'})
if __name__=='__main__':main()
