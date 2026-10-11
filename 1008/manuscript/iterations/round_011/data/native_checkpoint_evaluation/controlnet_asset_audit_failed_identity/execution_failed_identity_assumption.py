"""Read-only asset/layout check for the missing full native geometry baseline."""
import json,sys,torch,datetime
from pathlib import Path
from safetensors import safe_open
from revision_expansion_common import OUT,sha,write
from native_training_protocol008 import seed_all
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.controlnet import ControlNetModel_Union
r=OUT/'iteration009_native_checkpoint_evaluation/controlnet_asset_audit';assert not r.exists();r.mkdir();torch.set_num_threads(4);weights=Path('/4T/CXY/checkpoints/v29_25000.safetensors');base=Path('/4T/CXY/checkpoints/hf_repo');matches=[]
with safe_open(weights,framework='pt',device='cpu') as a,safe_open(base/'unet/diffusion_pytorch_model.safetensors',framework='pt',device='cpu') as b:
 keys=list(a.keys());native=list(b.keys());assert {k for k in keys if k.startswith('unet.unet.')}=={'unet.unet.'+k for k in native};control=[k for k in keys if k.startswith('controlnet.')];assert len(control)==863
 for key in native:
  x=a.get_tensor('unet.unet.'+key);y=b.get_tensor(key);assert torch.equal(x.to(y.dtype),y),key;matches.append(key)
seed_all(42);pipe=MVPainter_Pipeline.from_pretrained(str(base),torch_dtype=torch.float16,use_safetensors=True);controlnet=ControlNetModel_Union.from_unet(pipe.unet).to(dtype=torch.float16);pipe.add_controlnet(controlnet,conditioning_scale=1.0)
current=pipe.unet.state_dict();assert set(current)==set(keys),(len(current),len(keys));loaded=0;changed=0
with safe_open(weights,framework='pt',device='cpu') as a:
 with torch.no_grad():
  for key,tensor in current.items():
   source=a.get_tensor(key);assert source.shape==tensor.shape;source=source.to(tensor.dtype);changed+=int(not torch.equal(tensor,source));tensor.copy_(source);assert torch.equal(tensor,source);loaded+=1
params=sum(p.numel() for p in pipe.unet.controlnet.parameters());result={'status':'PASS_LOCAL_FULL_CONTROLNET_CHECKPOINT_CPU_STRICT_LAYOUT_AND_LOAD','asset_path':str(weights),'asset_sha256':sha(weights),'base_unet_path':str(base/'unet/diffusion_pytorch_model.safetensors'),'base_unet_sha256':sha(base/'unet/diffusion_pytorch_model.safetensors'),'base_unet_tensors_match':len(matches),'full_checkpoint_keys_strict_loaded':loaded,'loaded_tensors_different_from_constructed':changed,'controlnet_parameter_count':params,'controlnet_weight_keys':len(control),'official_source_sha256':sha(OUT/'iteration006_camera_protocol_audit/infer_multiview.py'),'cpu_only':True,'source_sha256':sha(Path(__file__)),'scope':'local convertedv29 asset; strict official architecture compatibility; no GPU inference or quality evidence, no canonical remote checkpoint bytehash verification','intended_evaluation':'paired50 steps/seed42/CFG2 with same source and geometry; official CLI defaults75 steps/seed12/rembg differ and must not be called full unmodified default'};write(r/'CONTROLNET_ASSET_AUDIT.json',result);(r/'execution_source.py').write_bytes(Path(__file__).read_bytes());print(result['status'],params,'controlnet parameters')
