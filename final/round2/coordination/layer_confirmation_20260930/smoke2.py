import sys, random, hashlib, torch
import numpy as np
from omegaconf import OmegaConf
sys.path.insert(0, '/4T/CXY/MV-Painter'); sys.path.insert(0, '/4T/CXY/MV-Painter/geotex'); sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')
import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from src.utils.train_util import instantiate_from_config

CONFIG = '/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml'
CKPT = '/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt'
device = torch.device('cuda:0'); dtype = torch.float16

def stage(p, e, m, l):
    return e if p < 1/3 else (m if p < 2/3 else l)
def layer_llh(p):
    return {"deep": stage(p,1.25,1.25,2.50), "middle": stage(p,1.25,1.25,2.50), "shallow": stage(p,0.50,0.50,0.75)}

model = ee.load_model(CONFIG, CKPT, device)
config = OmegaConf.load(CONFIG)
validation = config.data.params.validation
validation.params.target_view_mode = "unique6"
validation.params.object_list_file = "/4T/CXY/MV-Painter/final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
dataset = instantiate_from_config(validation)
lpips_fn = ee.get_lpips_fn(device)

results = []
for trial in range(2):
    object_seed = 42 + 0
    random.seed(object_seed); np.random.seed(object_seed); torch.manual_seed(object_seed)
    batch = collate_batch(dataset, 0, device)
    _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
    geo_clean = torch.nan_to_num(geo_input.float().clamp(0,1), nan=0.0, posinf=1.0, neginf=0.0)
    geo_feats = model.geo_encoder(geo_clean)
    edge = compute_edge_mask(real_depth.float(), threshold=0.1)
    torch.manual_seed(42)
    lh, lw = model.img_size*3//8, model.img_size*2//8
    init = torch.randn(1,4,lh,lw,device=device,dtype=dtype)
    torch.manual_seed(42)
    pred = exp.generate_with_schedule(model, batch, device, dtype, geo_feats, layer_llh, 50, init.clone(), {})
    m = ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)
    png_hash = hashlib.sha256(pred.cpu().numpy().tobytes()).hexdigest()[:16]
    results.append((png_hash, round(m['fg_lpips'],6), round(m['fg_psnr'],4)))
    print('trial%d: hash=%s fg_lpips=%.6f fg_psnr=%.4f' % (trial, *results[-1]), flush=True)
    del pred, batch, target, geo_feats
    torch.cuda.empty_cache()
print('DETERMINISM:', 'PASS' if results[0]==results[1] else 'FAIL')
