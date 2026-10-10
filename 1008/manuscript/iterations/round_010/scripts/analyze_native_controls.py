"""Recompute all fifteen post hoc object-paired contrasts from delivered rows."""
from pathlib import Path
import csv,json,itertools,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def holm_adjust(pvalues):
    order=np.argsort(pvalues);adjusted=np.ones(len(pvalues));running=0.
    for rank,index in enumerate(order):
        running=max(running,min(1.,(len(pvalues)-rank)*pvalues[index]));adjusted[index]=running
    return adjusted.tolist()

def stats(delta):
    delta=np.asarray(delta,dtype=float)
    if not len(delta) or not np.isfinite(delta).all():raise ValueError('missing/nonfinite complete pairs')
    rng=np.random.default_rng(20261010)
    boot=np.concatenate([delta[rng.integers(0,len(delta),size=(5000,len(delta)))].mean(axis=1) for _ in range(10)])
    lo,hi=np.quantile(boot,[.025,.975])
    observed=abs(delta.mean())
    if len(delta)<=16:
        signs=np.array(list(itertools.product([-1,1],repeat=len(delta))),dtype=np.int8)
        p=float(np.mean(np.abs((signs*delta).mean(axis=1))>=observed-1e-12));test='exact paired sign flip'
    else:
        rng=np.random.default_rng(20261010);extreme=0
        for _ in range(20):
            signs=rng.integers(0,2,size=(5000,len(delta)),dtype=np.int8)*2-1
            extreme+=np.count_nonzero(np.abs((signs*delta).mean(axis=1))>=observed-1e-12)
        p=float((extreme+1)/100001);test='100000-draw paired Monte Carlo sign flip'
    return {'n':len(delta),'mean_difference':float(delta.mean()),'median_difference':float(np.median(delta)),
            'ci95':[float(lo),float(hi)],'p_raw':p,'test':test,'positive_objects':int((delta>0).sum()),
            'negative_objects':int((delta<0).sum())}
path=ROOT/'data/bake10_all_controls.csv'
with path.open() as f:rows=list(csv.DictReader(f))
uids=sorted({r['object_uid'] for r in rows});index={(r['object_uid'],r['method']):r for r in rows}
assert len(uids)==10 and len(index)==len(rows)==100
metrics=['fg_psnr','fg_lpips','fg_ssim','edge_ssim','ciede2000']
conditions=sorted({r['method'] for r in rows});assert len(conditions)==10
assert all((u,c) in index for u in uids for c in conditions)
contrasts=[]
for a in ['budget_late16','native_gc3','no_adapter']:
 for metric in metrics:
  contrasts.append({'a':a,'b':'native_unset','metric':metric,**stats([float(index[u,a][metric])-float(index[u,'native_unset'][metric]) for u in uids])})
for r,p in zip(contrasts,holm_adjust([r['p_raw'] for r in contrasts])):r['p_holm']=p
means={c:{m:float(np.mean([float(index[u,c][m]) for u in uids])) for m in metrics} for c in conditions}
reference=json.loads((ROOT/'data/ITERATION002_STATISTICS.json').read_text())
assert means==reference['means']
for a,b in zip(contrasts,reference['contrasts']):
 for key in ['a','b','metric','n','mean_difference','median_difference','ci95','p_raw','p_holm','positive_objects','negative_objects']:
  assert a[key]==b[key],(key,a,b)
result={'status':'PASS_ALL_MEANS_AND_15_CONTRASTS_REPRODUCED','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'means':means,'contrasts':contrasts,'analysis':'post hoc; no independent confirmation'}
(ROOT/'STATISTICS_REPRODUCED.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
