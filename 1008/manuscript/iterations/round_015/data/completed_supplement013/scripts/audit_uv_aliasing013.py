"""GT-only common-coverage resolution and discontinuous-sampling footprint audit."""
import argparse,json,sys
from pathlib import Path
import torch,torch.nn.functional as F
from revision_expansion_common import OUT,write
R=OUT/'iteration012_condition_interference';f=json.loads((R/'gso_mva_external_attempt01/targets/MATRIX_FREEZE.json').read_text());sys.path.insert(0,f['deployed_source_root'])
from mvadapter.utils.mesh_utils import CameraProjection,NVDiffRastContextWrapper,get_orthogonal_camera,load_mesh,render
from mvadapter.utils.mesh_utils.uv import uv_precompute,uv_render_geometry,uv_render_attr,uv_blend,SimpleUVValidityStrategy,ExponentialBlend
from mvadapter.utils.mesh_utils.utils import get_clip_space_position

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--device',required=True);a=ap.parse_args();assert not a.out.exists();a.out.mkdir();torch.set_num_threads(4);torch.cuda.set_device(a.device);ctx=NVDiffRastContextWrapper(a.device);proj=CameraProjection(pb_backend='torch-native',bg_remover=None,device=a.device)
 cams=get_orthogonal_camera(elevation_deg=[0,0,0,0,89.99,-89.99],azimuth_deg=[-90,0,90,180,90,90],distance=[1.8]*6,left=-.55,right=.55,bottom=-.55,top=.55,device=a.device);q=torch.linspace(.5/1024,1-.5/1024,1024,device=a.device);yy,xx=torch.meshgrid(q,q,indexing='ij');ramp=torch.stack([xx,yy,.25+xx*.25+yy*.25],-1);results=[]
 with torch.inference_mode():
  for obj in [f['objects'][0],next(x for x in f['objects'] if x['object_uid']=='Remington_TStudio_Hair_Dryer')]:
   mesh=load_mesh(obj['mesh_path'],rescale=True,default_uv_size=1024,device=a.device);pre=uv_precompute(ctx,mesh,1024,1024);outputs={}
   for res in [256,512,1024]:
    rv=render(ctx,mesh,cams,height=res,width=res,texture_override=ramp,attr_background=1.)
    back=proj(rv.attr,mesh,cams,masks=rv.mask.float(),uv_size=1024,from_scratch=True,poisson_blending=False,uv_padding=False,depth_grad_dilation=5,depth_grad_threshold=.1,uv_exp_blend_alpha=3,uv_exp_blend_view_weight=torch.ones(6,device=a.device),aoi_cos_valid_threshold=.2,return_dict=True)
    outputs[res]=(back.uv_proj,back.uv_proj_mask)
   common=outputs[256][1]&outputs[512][1]&outputs[1024][1];common[:3,:]=False;common[-3:,:]=False;common[:,:3]=False;common[:,-3:]=False
   item={'uid':obj['object_uid'],'common_pixels':int(common.sum()),'resolution_sensitivity':{}}
   for res,(im,mask) in outputs.items():
    error=(im[common]-ramp[common]).abs();item['resolution_sensitivity'][str(res)]={'mean':float(error.mean()),'q99':float(torch.quantile(error.flatten(),.99))}
   # Compute UV discontinuity at the actual 512-pixel bilinear footprint.
   geo=uv_render_geometry(ctx,mesh,cams,512,512,pre,compute_depth_grad=True,depth_grad_dilation=5)
   rast,_=ctx.rasterize(get_clip_space_position(mesh.v_pos,cams.mvp_mtx),mesh.t_pos_idx,(512,512))
   vu,_=ctx.interpolate(mesh.v_tex[None],rast,mesh.t_tex_idx)
   x=(geo.uv_pos_ndc[...,0]+1)*256-.5;y=(geo.uv_pos_ndc[...,1]+1)*256-.5;xi=x.floor().long();yi=y.floor().long();fx=x-xi;fy=y-yi
   footprints=[];weights=[];gv=[];indices=torch.arange(6,device=a.device)[:,None,None]
   for dx,dy,w in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
    vx=(xi+dx).clamp(0,511);vy=(yi+dy).clamp(0,511);footprints.append(vu[indices,vy,vx]);weights.append(w);gv.append(geo.view_mask[indices,vy,vx])
   # Flag a discontinuity in a positive-weight sample relative to its atlas texel;
   # 0.15 is the original raw-error bound, independent of candidate quality.
   reference=torch.stack([xx,yy],-1)[None];bad=torch.zeros_like(x,dtype=torch.bool)
   for uv,w,visible in zip(footprints,weights,gv):bad|=((uv-reference).abs().amax(-1)>.15)&(w>1e-6)&visible
   attrs=uv_render_attr(render(ctx,mesh,cams,height=512,width=512,texture_override=ramp,attr_background=1.).attr,geo,masks=geo.view_mask.float())
   valids=SimpleUVValidityStrategy(aoi_cos_thresh=.2,depth_grad_thresh=.1)(pre,geo,attrs);weighted=ExponentialBlend(alpha=3,view_weight=torch.ones(6,device=a.device))(pre,geo,attrs,valids)
   bad_used=(bad&valids&(weighted>1e-6)).any(0)&common
   high=(outputs[512][0]-ramp).abs().amax(-1)>.15
   item['footprint_discontinuity_fraction']=float(bad_used[common].float().mean());item['high_error_pixels']=int((high&common).sum());item['high_error_at_flagged_footprint_fraction']=float(bad_used[high&common].float().mean()) if (high&common).any() else None
   results.append(item);write(a.out/'REPORT.json',results);print(item,flush=True)
 write(a.out/'STATUS.json',{'status':'COMPLETE_GT_ONLY_ALIASING_DIAGNOSTIC','objects':len(results)})
if __name__=='__main__':main()
