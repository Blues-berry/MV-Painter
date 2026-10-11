"""Shared strict data and native-conditioning preparation for a new training protocol."""
import sys,random,hashlib
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path[:0]=['/4T/CXY/MV-Painter/MVPainter','/4T/CXY/MV-Painter/geotex','/4T/CXY/MV-Painter']
import torch
from PIL import Image
from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from data_utils import collate_batch,prepare_batch
from revision_expansion_common import OUT,sha,write
import run_fresh_c_glb_method_matrix as base
RUN=OUT/'iteration008_native_training_attempt02'
def tensor_hash(t):return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
def seed_all(seed):random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
def dataset_for(config,list_path,root):
 cfg=OmegaConf.create(OmegaConf.to_container(config.data.params.validation,resolve=True))
 cfg.params.object_list_file=str(list_path);cfg.params.root_dir_list=[str(root)];cfg.params.target_view_mode='unique6'
 dataset=instantiate_from_config(cfg);dataset.random_ratio_range=1.
 original_depth=dataset.load_img_depth
 dataset.depth_zero_counts={}
 def guarded_depth(path,color,ratio):
  image,alpha=original_depth(path,color,ratio)
  zero=image<=0;assert torch.isfinite(image).all()
  dataset.depth_zero_counts[str(path)]=int(zero.sum())
  # Zero cannot be inverted. Encoding it as1 excludes it from the existing
  # inverse-depth normalization; RGB, normal maps and masks remain unchanged.
  return torch.where(zero,torch.ones_like(image),image),alpha
 dataset.load_img_depth=guarded_depth
 expected=list_path.read_text().splitlines();assert [Path(x).name for x in dataset.paths]==expected
 return dataset
def strict_batch(dataset,index,device):
 # The legacy loader otherwise changes objects silently after an input failure.
 dataset.depth_zero_counts={}
 with patch('src.data.mvpainter_dataset.random.randint',side_effect=RuntimeError('Strict native training forbids fallback object replacement')):
  batch=collate_batch(dataset,index,device)
 return batch
def source_for(dataset,index):
 p=Path(dataset.paths[index])/'image'
 _,a=dataset.load_im(str(p/'000.png'),[1.,1.,1.],1.)
 _,b=dataset.load_im(str(p/'014.png'),[1.,1.,1.],1.)
 return p/('014.png' if (a==0).sum().item()>(b==0).sum().item() else '000.png')
class ConditioningCaptured(Exception):pass
def capture_native_conditioning(pipe,source,device,seed=42):
 captured={}
 def stop_before_unet(module,args,kw):
  prompt=kw['encoder_hidden_states'];ref=kw['cross_attention_kwargs']['cond_lat'];added=kw['added_cond_kwargs']
  assert prompt.shape[0]==ref.shape[0]==2
  for label,i in [('negative',0),('positive',1)]:
   captured[label]={'prompt':prompt[i:i+1].detach().cpu().clone(),'reference':ref[i:i+1].detach().cpu().clone(),'added':{k:v[i:i+1].detach().cpu().clone() for k,v in added.items()}}
  raise ConditioningCaptured()
 h=pipe.unet.register_forward_pre_hook(stop_before_unet,with_kwargs=True);seed_all(seed)
 try:
  with torch.no_grad():pipe(Image.open(source).convert('RGBA'),num_inference_steps=50,generator=torch.Generator(device=device).manual_seed(42),guidance_scale=2.,depth_image=None,output_type='pil')
 except ConditioningCaptured:pass
 finally:h.remove()
 assert set(captured)=={'negative','positive'}
 assert torch.count_nonzero(captured['negative']['prompt'])==0
 assert torch.count_nonzero(captured['negative']['added']['text_embeds'])==0
 return captured
def payload_hashes(payload):
 return {label:{'prompt':tensor_hash(p['prompt']),'reference':tensor_hash(p['reference']),'added':{k:tensor_hash(v) for k,v in p['added'].items()}} for label,p in payload.items()}
def verify_reference_target(batch,source):
 raw=np.asarray(Image.open(source).convert('RGBA'),dtype=np.float32)/255.
 rgb=raw[...,:3]*raw[...,3:]+1.-raw[...,3:]
 target=batch['target_imgs'][0,0].detach().cpu()
 assert target.shape==torch.Size([3,512,512])
 error=float((target-torch.from_numpy(rgb).permute(2,0,1)).abs().max());assert error<1e-6
 assert torch.isfinite(batch['depth_imgs']).all() and torch.isfinite(batch['real_depth_imgs']).all()
 return error
