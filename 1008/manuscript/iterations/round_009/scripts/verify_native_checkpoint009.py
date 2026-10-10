"""Frozen paired analysis; require both primary conditions before inferential claims."""
import json,math,numpy as np
import hashlib
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+"\n")
from pathlib import Path
r=Path(__file__).resolve().parents[1]/'data/native_checkpoint_evaluation';protocol=json.loads((r/'STATISTICAL_PROTOCOL.json').read_text());uids=json.loads((r/'COHORT_AND_ANALYSIS_FREEZE.json').read_text())['uids'];rows={}
for p in r.glob('scores_*.json'):
 if p.name.endswith('_partial.json'):continue
 d=json.loads(p.read_text());assert d['status']=='COMPLETE_NATIVE_SLOT_SCORING'
 for x in d['rows']:
  key=(x['uid'],x['condition']);assert key not in rows;rows[key]=x
needed={a for a,b,m in protocol['primary_comparisons']}|{b for a,b,m in protocol['primary_comparisons']};assert all((u,c) in rows for u in uids for c in needed),'Both predeclared primary contrasts must be complete before inferential reporting'
def contrast(a,b,m):
 delta=np.array([rows[(u,a)]['nonreference_mean'][m]-rows[(u,b)]['nonreference_mean'][m] for u in uids]);assert np.isfinite(delta).all();rng=np.random.default_rng(20261010);boot=np.mean(delta[rng.integers(0,len(delta),(20000,len(delta)))],axis=1);observed=abs(float(delta.mean()));count=0;total=200000
 for start in range(0,total,4000):
  signs=rng.choice([-1.,1.],size=(min(4000,total-start),len(delta)));count+=int((np.abs(np.mean(signs*delta,axis=1))>=observed-1e-15).sum())
 return {'a':a,'b':b,'metric':m,'n_objects':len(delta),'difference_a_minus_b':float(delta.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'signflip_p':(count+1)/(total+1),'better_count':int((delta<0).sum()) if m in ['fg_lpips','ciede2000'] else int((delta>0).sum()),'zero_count':int((delta==0).sum()),'object_differences':dict(zip(uids,delta.tolist()))}
def holm(items):
 order=sorted(range(len(items)),key=lambda i:items[i]['signflip_p']);previous=0.
 for rank,i in enumerate(order):previous=max(previous,min(1.,(len(items)-rank)*items[i]['signflip_p']));items[i]['holm_p']=previous
primary=[contrast(*c) for c in protocol['primary_comparisons']];holm(primary);secondary=[];missing=[]
for c in protocol['secondary_comparisons']:
 a,b,m=c
 if all((u,a) in rows and (u,b) in rows for u in uids):secondary.append(contrast(*c))
 else:missing.append(c)
if not missing:holm(secondary)
result={'status':'COMPLETE_PRIMARY_FAMILY_SECONDARY_PENDING' if missing else 'COMPLETE_ALL_PREDECLARED_ANALYSIS','primary':primary,'secondary':secondary,'secondary_missing':missing,'secondary_inference':'No corrected significance claim until all18 tests complete' if missing else 'Holm18 complete','cohort_sha256':sha(r/'COHORT_AND_ANALYSIS_FREEZE.json'),'statistics_sha256':sha(r/'STATISTICAL_PROTOCOL.json'),'source_sha256':sha(Path(__file__)),'aggregation':'five nonreference views per object; paired object bootstrap and signflip','quality_failure_exclusion':'none'};stored=json.loads((r/'PAIRED_NATIVE_ANALYSIS.json').read_text());assert result['primary']==stored['primary'] and result['secondary']==stored['secondary'];print('PASS_ALL20_MAIN_CONTRASTS_REPRODUCE')

v29=json.loads((r/"V29_DEPLOYMENT_COMPARISON.json").read_text());items=[contrast(x["a"],x["b"],x["metric"]) for x in v29["tests"]];holm(items)
for actual,stored in zip(items,v29["tests"]):
 for k in ["difference_a_minus_b","ci95","signflip_p","holm_p","object_differences"]:assert actual[k]==stored[k],k
print("PASS_ALL4_V29_CONTRASTS_REPRODUCE")
