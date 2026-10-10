"""Post hoc matched GT reference context; never changes the frozen primary."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 path=ROOT/'data/bake10_object_metrics.csv'
 with path.open() as f:rows=list(csv.DictReader(f))
 uids=sorted({r['object_uid'] for r in rows});assert len(uids)==10
 index={(r['object_uid'],r['method']):r for r in rows};assert len(index)==80
 gt=np.array([float(index[u,'gt']['fg_lpips']) for u in uids]);mean=np.array([float(index[u,'budget_fixed_mean']['fg_lpips']) for u in uids]);late=np.array([float(index[u,'budget_late16']['fg_lpips']) for u in uids])
 delta=late-mean;reference_gap=mean-gt
 rng=np.random.default_rng(20261010);draw=rng.integers(0,10,size=(50000,10))
 numerator=(mean-late)[draw].mean(axis=1);denominator=reference_gap[draw].mean(axis=1);assert np.all(denominator>0)
 ratio=numerator/denominator
 gt_means={m:float(np.mean([float(index[u,'gt'][m]) for u in uids])) for m in ['fg_psnr','fg_lpips','fg_ssim','edge_ssim','ciede2000']}
 result={'analysis_class':'post hoc descriptive context, not new confirmation','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n':10,'gt256_means':gt_means,'late_minus_mean_lpips':float(delta.mean()),'delta_ci95':np.quantile(delta[draw].mean(axis=1),[.025,.975]).tolist(),'reference_gap_ratio':float((mean-late).mean()/reference_gap.mean()),'reference_gap_ratio_ci95':np.quantile(ratio,[.025,.975]).tolist(),'ratio_definition':'mean(FixedMean-Late) / mean(FixedMean-GT256); empirical matched reference, not theoretical bound','leave_one_out_mean_range':[float(min(np.delete(delta,i).mean() for i in range(10))),float(max(np.delete(delta,i).mean() for i in range(10)))],'objects':[{'uid':u,'gt_lpips':float(g),'mean_lpips':float(m),'late_lpips':float(l),'delta':float(d)} for u,g,m,l,d in zip(uids,gt,mean,late,delta)]}
 (ROOT/'GT_REFERENCE_CONTEXT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='objects'},indent=2))
if __name__=='__main__':main()
