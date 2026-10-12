"""Offline primary LPIPS checks from delivered view rows; no model or GPU."""
from pathlib import Path
import csv,json
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
    uids=json.loads((ROOT/'data/GSO100_UID_ORDER.json').read_text())
    rows=list(csv.DictReader((ROOT/'data/GSO100_VIEW_METRICS.csv').open()))
    cells={}
    for r in rows:
        key=r['uid'],int(r['seed']),r['condition']
        cells.setdefault(key,[]).append(r)
    assert len(rows)==14400 and len(cells)==2400
    values={}
    for key,vs in cells.items():
        assert sorted(int(v['view']) for v in vs)==list(range(6))
        values[key]=np.mean([float(v['fg_lpips']) for v in vs if int(v['view'])!=1])
    output=[]
    for stage in ['gso_mva_external_attempt01','gso_apg_closure_attempt01']:
        recorded=json.loads((ROOT/'data'/stage/'COMPARISONS.json').read_text())
        family=[]
        for t in recorded['comparisons']:
            if t['metric']!='fg_lpips':continue
            ds=np.array([np.mean([values[u,s,t['a']]-values[u,s,t['b']] for s in [42,2026,31415]]) for u in uids])
            rng=np.random.default_rng(20261011)
            ci=np.percentile(ds[rng.integers(0,100,(20000,100))].mean(1),[2.5,97.5])
            rng=np.random.default_rng(20261011);count=0;obs=abs(ds.mean())
            for _ in range(20):
                count+=int((abs((rng.choice([-1,1],(10000,100))*ds).mean(1))>=obs-1e-12).sum())
            p=(count+1)/200001
            assert abs(ds.mean()-t['mean_difference'])<1e-12
            assert np.allclose(ci,t['ci95_pointwise'],rtol=0,atol=1e-12)
            assert abs(p-t['p_raw'])<1e-12
            family.append({'a':t['a'],'b':t['b'],'mean_difference':float(ds.mean()),'ci95_pointwise':ci.tolist(),'p_raw':p,'recorded_holm':t['p_holm']})
        previous=0
        for i,t in enumerate(sorted(family,key=lambda t:t['p_raw'])):
            previous=max(previous,min(1,(len(family)-i)*t['p_raw']))
            assert abs(previous-t.pop('recorded_holm'))<1e-12
            t['p_holm']=previous
        output.append({'family':stage,'comparisons':family})
    path=ROOT/'data/EXTERNAL_PRIMARY_RECOMPUTATION.json'
    path.write_text(json.dumps({'status':'PASS_ALL15_PRIMARY_MEANS_CIS_P_VALUES_AND_HOLM','families':output},indent=2)+'\n')
    print('PASS: 15 primary differences, intervals, sign-flip p values and Holm adjustments.')

if __name__=='__main__':main()
