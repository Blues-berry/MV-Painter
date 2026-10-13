"""GT-only diagnostics; unchanged native projection, with analytic synthetic controls."""
import argparse,json,sys
from pathlib import Path
import numpy as np,torch
from PIL import Image
from revision_expansion_common import OUT,write,sha
R=OUT/'iteration012_condition_interference';EXT=R/'gso_mva_external_attempt01'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--device',required=True);ap.add_argument('--rank',type=int,default=0);a=ap.parse_args();assert not a.out.exists();a.out.mkdir();torch.set_num_threads(4);torch.cuda.set_device(a.device)
 f=json.loads((EXT/'targets/MATRIX_FREEZE.json').read_text());sys.path.insert(0,f['deployed_source_root'])
 from mvadapter.utils.mesh_utils import CameraProjection,NVDiffRastContextWrapper,get_orthogonal_camera,load_mesh,render
 from mvadapter.utils.mesh_utils.mesh import TexturedMesh
 from mvadapter.utils.mesh_utils.uv import uv_precompute
 ctx=NVDiffRastContextWrapper(a.device);proj=CameraProjection(pb_backend='torch-native',bg_remover=None,device=a.device);cams=get_orthogonal_camera(elevation_deg=[0,0,0,0,89.99,-89.99],azimuth_deg=[-90,0,90,180,90,90],distance=[1.8]*6,left=-.55,right=.55,bottom=-.55,top=.55,device=a.device)
 def project(images,mesh,masks,cameras=cams):
  return proj(images,mesh,cameras,masks=masks,uv_size=1024,from_scratch=True,poisson_blending=False,uv_padding=False,depth_grad_dilation=5,depth_grad_threshold=.1,uv_exp_blend_alpha=3,uv_exp_blend_view_weight=torch.ones(images.shape[0],device=a.device),aoi_cos_valid_threshold=.2,return_dict=True)
 def scores(pred,truth,mask):
  e=(pred[mask]-truth[mask]).abs();return {'mean':float(e.mean()),'q99':float(torch.quantile(e.flatten(),.99)),'max':float(e.max()),'pixels':int(mask.sum())}
 def nonlinear(pos):
  c=(pos+.5).clamp(0,1);return torch.stack([c[...,0],c[...,1]**2,c[...,2]**3],-1)
 coord=torch.linspace(.5/1024,1-.5/1024,1024,device=a.device);yy,xx=torch.meshgrid(coord,coord,indexing='ij');ramp=torch.stack([xx,yy,.25+xx*.25+yy*.25],-1)
 # Independent, explicitly synthetic fixture with two UV islands sharing a world edge.
 v=torch.tensor([[0,-.45,-.45],[0,0,-.45],[0,0,.45],[0,-.45,.45],[0,0,-.45],[0,.45,-.45],[0,.45,.45],[0,0,.45]],device=a.device)
 faces=torch.tensor([[0,1,2],[0,2,3],[4,5,6],[4,6,7]],device=a.device,dtype=torch.int32)
 uv=torch.tensor([[.55,.05],[.95,.05],[.95,.95],[.55,.95],[.05,.05],[.45,.05],[.45,.95],[.05,.95]],device=a.device)
 mesh=TexturedMesh(v,faces,v_tex=uv,t_tex_idx=faces,texture=ramp);mesh.set_vertex_normal(torch.tensor([[1.,0,0]],device=a.device).repeat(8,1));cam=get_orthogonal_camera(elevation_deg=[0],azimuth_deg=[0],distance=[1.8],left=-.55,right=.55,bottom=-.55,top=.55,device=a.device)
 with torch.inference_mode():
  pre=uv_precompute(ctx,mesh,1024,1024);m=pre.uv_mask
  target_y=torch.where(xx>.5,-.45+(xx-.55)*(.45/.4),(xx-.05)*(.45/.4));analytic=torch.stack([torch.full_like(xx,.5),target_y+.5,yy],-1)
  assert float((pre.uv_pos[m]+.5-analytic[m]).abs().max())<1e-5
  rv=render(ctx,mesh,cam,height=64,width=64,texture_override=ramp,attr_background=1.)
  raw=project(rv.attr,mesh,rv.mask.float(),cam);rawstats=scores(raw.uv_proj,ramp,raw.uv_proj_mask)
  world=nonlinear(rv.pos);world[~rv.mask]=1;back=project(world,mesh,rv.mask.float(),cam);worldstats=scores(back.uv_proj,nonlinear(pre.uv_pos),back.uv_proj_mask)
  wrong=project(world.flip(2),mesh,rv.mask.float(),cam);wrongstats=scores(wrong.uv_proj,nonlinear(pre.uv_pos),wrong.uv_proj_mask)
  assert rawstats['max']>.15 and worldstats['mean']<.03 and worldstats['q99']<.15 and wrongstats['mean']>.03
  write(a.out/'SYNTHETIC_CONTROL.json',{'analytic_atlas_max_error':float((pre.uv_pos[m]+.5-analytic[m]).abs().max()),'discontinuous_uv_ramp':rawstats,'continuous_nonlinear_world_color':worldstats,'deliberate_horizontal_flip_negative_control':wrongstats,'fixture':'Synthetic two-island planar mesh; independent affine atlas mapping;64pixel image ->1024 UV. Not experiment output.'})
  rows=[]
  for i,obj in enumerate(f['objects'][:20]):
   if i%2!=a.rank:continue
   mesh=load_mesh(obj['mesh_path'],rescale=True,default_uv_size=1024,device=a.device);pre=uv_precompute(ctx,mesh,1024,1024);rv=render(ctx,mesh,cams,height=512,width=512,texture_override=ramp,attr_background=1.)
   masks=torch.as_tensor(np.stack([np.asarray(Image.open(v['path']).convert('RGBA'))[...,3]/255 for v in obj['gt_images_official_order']]),device=a.device);assert torch.equal(rv.mask,masks>.5)
   raw=project(rv.attr,mesh,masks);valid=raw.uv_proj_mask.clone();valid[:3,:]=False;valid[-3:,:]=False;valid[:,:3]=False;valid[:,-3:]=False;rawstats=scores(raw.uv_proj,ramp,valid)
   world=nonlinear(rv.pos);world[~rv.mask]=1;wb=project(world,mesh,masks);worldstats=scores(wb.uv_proj,nonlinear(pre.uv_pos),wb.uv_proj_mask)
   constant=project(torch.full_like(world,.25),mesh,masks);ce=float((constant.uv_proj[constant.uv_proj_mask]-.25).abs().max());assert ce<1e-4
   assert torch.equal(raw.uv_proj_mask,wb.uv_proj_mask) and torch.equal(wb.uv_proj_mask,constant.uv_proj_mask)
   item={'uid':obj['object_uid'],'raw_uv_ramp':rawstats,'continuous_nonlinear_world_color':worldstats,'constant_error':ce,'target_mask_identity':True,'coverage_pixels':int(raw.uv_proj_mask.sum())};rows.append(item);write(a.out/'OBJECT_DIAGNOSTICS.json',rows)
   if obj['object_uid'] in [f['objects'][0]['object_uid'],'Remington_TStudio_Hair_Dryer']:
    folder=a.out/obj['object_uid'];folder.mkdir();err=(raw.uv_proj-ramp).abs().amax(-1);np.savez_compressed(folder/'raw_diagnostic.npz',error=err.cpu().numpy(),mask=valid.cpu().numpy(),world_error=(wb.uv_proj-nonlinear(pre.uv_pos)).abs().amax(-1).cpu().numpy());heat=(torch.stack([err.clamp(0,.5)*2,torch.zeros_like(err),1-err.clamp(0,.5)*2],-1)*valid[...,None]).cpu().numpy();Image.fromarray((heat*255).astype(np.uint8)).save(folder/'UV_RAMP_ERROR.png')
   print('DIAGNOSTIC',obj['object_uid'],rawstats,worldstats,flush=True)
  write(a.out/'STATUS.json',{'status':'COMPLETE_GT_ONLY_DIAGNOSTICS','objects':len(rows),'raw_uv_failures':[x['uid'] for x in rows if x['raw_uv_ramp']['mean']>=.03 or x['raw_uv_ramp']['q99']>=.15],'continuous_control_failures':[x['uid'] for x in rows if x['continuous_nonlinear_world_color']['mean']>=.03 or x['continuous_nonlinear_world_color']['q99']>=.15]})
if __name__=='__main__':main()
