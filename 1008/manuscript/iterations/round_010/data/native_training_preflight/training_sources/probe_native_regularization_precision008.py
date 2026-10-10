"""Observe correction precision before changing the training loss implementation."""
from native_training_protocol008 import *
import geotex.eval_exploration as ee
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

def main():
 device=torch.device('cuda:0');base.gpu_snapshot('cuda:0');seed_all(42);torch.set_num_threads(4);config=OmegaConf.load(RUN/'native512_config.yaml');model=ee.load_model(str(RUN/'native512_config.yaml'),None,device);model.unet.eval();model.geo_encoder.eval()
 dataset=dataset_for(config,RUN/'train_objects_1112.txt',Path(config.data.params.train.params.root_dir_list[0]));uid=Path(dataset.paths[0]).name;seed_all(42);batch=strict_batch(dataset,0,device);_,target,normal,depth,geo,mask=prepare_batch(batch,512,device)
 payload=torch.load(RUN/'conditioning_cache'/f'{uid}.pt',map_location=device,weights_only=False)['positive']
 with torch.no_grad():
  from metrics import scale_latents
  latent=scale_latents(model.pipeline.vae.encode(((target-.5)/.8).half()).latent_dist.sample()*model.pipeline.vae.config.scaling_factor);noise=torch.randn_like(latent);t=torch.tensor([100],device=device);noisy=model.train_scheduler.add_noise(latent,noise,t)
  features=model.geo_encoder(torch.nan_to_num(geo.float().clamp(0,1)));model._set_geo_feats_on_wrappers(features)
  pred=model.unet(noisy,t,encoder_hidden_states=payload['prompt'],cross_attention_kwargs={'cond_lat':payload['reference']},added_cond_kwargs=payload['added'],return_dict=False,is_training=True)[0]
  rows=[]
  for i,w in enumerate(m for m in model.unet.modules() if isinstance(m,GeoTexResnetWrapper)):
   c=w._last_correction;assert c is not None
   rows.append({'wrapper':i,'dtype':str(c.dtype),'correction_max_abs':float(c.abs().max()),'half_mean_square':float(c.square().mean()),'float_mean_square':float(c.float().square().mean()),'output_projection_weight_std':float(w.adapter.output_proj.weight.std())})
 result={'status':'MEASURED_REGULARIZATION_PRECISION','source_sha256':sha(Path(__file__)),'helper_sha256':sha(Path(__file__).with_name('native_training_protocol008.py')),'uid':uid,'rows':rows,'prediction_all_finite':bool(torch.isfinite(pred).all())};write(RUN/'REGULARIZATION_PRECISION_PROBE.json',result);print(result)
if __name__=='__main__':main()
