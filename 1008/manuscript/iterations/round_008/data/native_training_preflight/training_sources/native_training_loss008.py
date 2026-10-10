"""Retain native noise losses while computing residual regularization in float32."""
import torch
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

def training_loss(model,pred,noise,target,mask,depth,normal):
 weight=model.adapter_reg_weight;model.adapter_reg_weight=0.
 try:loss,components=model.compute_loss(pred,noise,target,mask,torch.float16,depth_imgs=depth,normal_imgs=normal)
 finally:model.adapter_reg_weight=weight
 corrections=[m._last_correction for m in model.unet.modules() if isinstance(m,GeoTexResnetWrapper)]
 assert len(corrections)==9 and all(c is not None for c in corrections)
 reg=torch.stack([c.float().square().mean() for c in corrections]).mean()
 assert torch.isfinite(reg)
 loss=loss+weight*reg;components['train/reg_loss']=reg;components['train/loss']=loss
 return loss,components
